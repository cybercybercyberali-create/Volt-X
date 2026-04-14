import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


class OmegaStocks:
    """Stock market data using yfinance + Alpha Vantage."""

    def __init__(self):
        self._alpha = BaseAPIClient("alpha_vantage", "https://www.alphavantage.co")

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Get stock quote."""
        cache_key = f"stock:{symbol.upper()}"
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

        if not result or result.get("error"):
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                return result
        return result or {"error": True, "symbol": symbol, "message": "Quote unavailable"}

    async def _fetch_yfinance(self, symbol: str) -> Optional[dict]:
        """Fetch stock data using yfinance fast_info (reliable, no key needed)."""
        try:
            import yfinance as yf
            import asyncio

            def _sync_fetch():
                ticker = yf.Ticker(symbol)
                fi = ticker.fast_info
                price = fi.last_price
                # fallback to recent history if fast_info fails
                if not price or price <= 0:
                    hist = ticker.history(period="2d")
                    if not hist.empty:
                        price = float(hist["Close"].iloc[-1])
                    else:
                        return None
                prev = getattr(fi, "previous_close", None) or price
                change = price - prev
                change_pct = (change / prev * 100) if prev else 0
                mcap = getattr(fi, "market_cap", 0) or 0
                return {
                    "symbol": symbol.upper(),
                    "name": symbol.upper(),
                    "price": float(price),
                    "change": float(change),
                    "change_percent": float(change_pct),
                    "market_cap": float(mcap),
                    "source": "yfinance",
                    "error": False,
                }

            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_fetch), timeout=25.0
            )
            return result
        except Exception as exc:
            logger.debug(f"yfinance error for {symbol}: {exc}")
        return None

    async def _fetch_alpha_vantage(self, symbol: str) -> Optional[dict]:
        """Fetch from Alpha Vantage."""
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
                return {
                    "symbol": q.get("01. symbol", symbol),
                    "price": float(q.get("05. price", 0)),
                    "change": float(q.get("09. change", 0)),
                    "change_percent": q.get("10. change percent", "0%"),
                    "volume": int(q.get("06. volume", 0)),
                    "source": "Alpha Vantage",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"Alpha Vantage error: {exc}")
        return None

    async def close(self) -> None:
        await self._alpha.close()


omega_stocks = OmegaStocks()
