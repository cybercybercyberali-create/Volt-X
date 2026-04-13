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
        """Fetch from yfinance."""
        try:
            import yfinance as yf
            import asyncio
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)

            if info and info.get("regularMarketPrice"):
                return {
                    "symbol": symbol.upper(),
                    "name": info.get("shortName", symbol),
                    "price": info.get("regularMarketPrice", 0),
                    "change": info.get("regularMarketChange", 0),
                    "change_percent": info.get("regularMarketChangePercent", 0),
                    "high": info.get("dayHigh", 0),
                    "low": info.get("dayLow", 0),
                    "volume": info.get("volume", 0),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE"),
                    "52w_high": info.get("fiftyTwoWeekHigh", 0),
                    "52w_low": info.get("fiftyTwoWeekLow", 0),
                    "currency": info.get("currency", "USD"),
                    "exchange": info.get("exchange", ""),
                    "source": "yfinance",
                    "error": False,
                }
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
