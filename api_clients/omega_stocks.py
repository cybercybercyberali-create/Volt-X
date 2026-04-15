import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)

# Common company name → ticker (Arabic + English)
_NAME_MAP: dict[str, str] = {
    "apple": "AAPL", "ابل": "AAPL", "آبل": "AAPL",
    "microsoft": "MSFT", "مايكروسوفت": "MSFT", "ميكروسوفت": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "جوجل": "GOOGL",
    "amazon": "AMZN", "امازون": "AMZN", "أمازون": "AMZN",
    "tesla": "TSLA", "تسلا": "TSLA",
    "meta": "META", "facebook": "META", "ميتا": "META", "فيسبوك": "META",
    "nvidia": "NVDA", "انفيديا": "NVDA", "نفيديا": "NVDA",
    "samsung": "005930.KS", "سامسونج": "005930.KS",
    "saudi aramco": "2222.SR", "أرامكو": "2222.SR", "ارامكو": "2222.SR",
    "stc": "7010.SR", "اتصالات السعودية": "7010.SR",
    "sabic": "2010.SR", "سابك": "2010.SR",
    "netflix": "NFLX", "نتفليكس": "NFLX",
    "disney": "DIS", "ديزني": "DIS",
    "snapchat": "SNAP", "snap": "SNAP", "سناب": "SNAP",
    "twitter": "X", "تويتر": "X",
    "uber": "UBER", "اوبر": "UBER",
    "paypal": "PYPL", "بيبال": "PYPL",
    "intel": "INTC", "انتل": "INTC",
    "amd": "AMD",
    "qualcomm": "QCOM", "كوالكوم": "QCOM",
    "alibaba": "BABA", "علي بابا": "BABA",
    "berkshire": "BRK-B",
    "johnson": "JNJ", "jpmorgan": "JPM", "goldman": "GS",
}


def _resolve_name(query: str) -> Optional[str]:
    """Try to resolve company name to ticker symbol."""
    q = query.strip().lower()
    # Direct map lookup
    if q in _NAME_MAP:
        return _NAME_MAP[q]
    # Partial match
    for name, ticker in _NAME_MAP.items():
        if name in q or q in name:
            return ticker
    return None


class OmegaStocks:

    def __init__(self):
        self._alpha = BaseAPIClient("alpha_vantage", "https://www.alphavantage.co")

    async def resolve_symbol(self, query: str) -> str:
        """Turn company name / Arabic name into a ticker symbol."""
        q = query.strip()
        # Already looks like a ticker (short, uppercase-able, no spaces)
        if len(q) <= 6 and q.replace(".", "").replace("-", "").isalnum():
            return q.upper()
        # Static map
        mapped = _resolve_name(q)
        if mapped:
            return mapped
        # yfinance Search fallback
        try:
            import yfinance as yf
            def _search():
                results = yf.Search(q, max_results=5).quotes
                for r in results:
                    sym = r.get("symbol", "")
                    qt  = r.get("quoteType", "")
                    if sym and qt in ("EQUITY", "ETF"):
                        return sym
                return None
            loop = asyncio.get_event_loop()
            sym = await asyncio.wait_for(loop.run_in_executor(None, _search), timeout=10.0)
            if sym:
                return sym
        except Exception as exc:
            logger.debug(f"yfinance search error: {exc}")
        return q.upper()

    async def get_quote(self, query: str) -> dict[str, Any]:
        symbol = await self.resolve_symbol(query)
        cache_key = f"stock:{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = await self._fetch_yfinance(symbol)
        if (not result or result.get("error")) and quota.has_quota("alpha_vantage"):
            result = await self._fetch_alpha_vantage(symbol)
            if result and not result.get("error"):
                quota.use_quota("alpha_vantage")

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["stocks"])
            return result

        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            r = stale["data"]
            r["stale"] = True
            return r

        return {"error": True, "symbol": symbol, "message": "البيانات غير متوفرة حالياً من المصادر الحية"}

    async def _fetch_yfinance(self, symbol: str) -> Optional[dict]:
        try:
            import yfinance as yf

            def _sync():
                t = yf.Ticker(symbol)
                fi = t.fast_info
                price = fi.last_price
                if not price or price <= 0:
                    hist = t.history(period="2d")
                    if hist.empty:
                        return None
                    price = float(hist["Close"].iloc[-1])
                prev  = getattr(fi, "previous_close", None) or price
                chg   = price - prev
                chg_p = (chg / prev * 100) if prev else 0
                mcap  = getattr(fi, "market_cap", 0) or 0
                exch  = getattr(fi, "exchange", "") or ""
                info  = {}
                try:
                    info = t.info or {}
                except Exception:
                    pass
                name = info.get("shortName") or info.get("longName") or symbol.upper()
                now  = datetime.now(timezone.utc).strftime("%H:%M UTC")
                return {
                    "symbol":         symbol.upper(),
                    "name":           name,
                    "price":          float(price),
                    "change":         float(chg),
                    "change_percent": float(chg_p),
                    "market_cap":     float(mcap),
                    "exchange":       exch,
                    "last_updated":   now,
                    "source":         "yfinance",
                    "error":          False,
                }

            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(loop.run_in_executor(None, _sync), timeout=25.0)
        except Exception as exc:
            logger.debug(f"yfinance {symbol}: {exc}")
        return None

    async def _fetch_alpha_vantage(self, symbol: str) -> Optional[dict]:
        from config import settings
        if not settings.alpha_vantage_key:
            return None
        try:
            data = await self._alpha.get(
                "/query",
                params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": settings.alpha_vantage_key},
            )
            if data and "Global Quote" in data:
                q = data["Global Quote"]
                now = datetime.now(timezone.utc).strftime("%H:%M UTC")
                return {
                    "symbol":         q.get("01. symbol", symbol),
                    "name":           q.get("01. symbol", symbol),
                    "price":          float(q.get("05. price", 0)),
                    "change":         float(q.get("09. change", 0)),
                    "change_percent": float(q.get("10. change percent", "0").replace("%", "")),
                    "volume":         int(q.get("06. volume", 0)),
                    "last_updated":   now,
                    "source":         "Alpha Vantage",
                    "error":          False,
                }
        except Exception as exc:
            logger.debug(f"AlphaVantage {symbol}: {exc}")
        return None

    async def close(self) -> None:
        await self._alpha.close()


omega_stocks = OmegaStocks()
