import asyncio
import logging
import statistics
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL, GOLD_KARATS, SUPPORTED_METALS, DISPLAY_CURRENCIES
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


class OmegaMetals:
    """Gold & metals prices with multi-source fusion and outlier removal."""

    def __init__(self):
        self._metals_api = BaseAPIClient("metals_api", "https://metals-api.com/api")
        self._goldapi = BaseAPIClient("goldapi", "https://www.goldapi.io/api")
        self._fallback = BaseAPIClient("metals_fallback")

    async def get_prices(self, metal: str = "XAU", currency: str = "USD") -> dict[str, Any]:
        """Get metal price with multi-source fusion."""
        cache_key = f"metals:{metal}:{currency}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        prices = []

        # Limited API first (if quota available, auto-restores when renewed)
        if quota.has_quota("metals_api"):
            price1 = await self._fetch_metals_api(metal, currency)
            if price1 is not None:
                quota.use_quota("metals_api")
                prices.append({"source": "metals-api", "price": price1})

        price2 = await self._fetch_goldapi(metal, currency)
        if price2 is not None:
            prices.append({"source": "goldapi", "price": price2})

        price3 = await self._fetch_metals_live(metal)
        if price3 is not None:
            prices.append({"source": "metals.live", "price": price3})

        if not prices:
            price4 = await self._fetch_yfinance(metal)
            if price4 is not None:
                prices.append({"source": "yfinance", "price": price4})

        if not prices:
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                result["age_minutes"] = stale.get("age_minutes", 0)
                return result
            return {"error": True, "message": "No price data available"}

        fused_price = self._fuse_prices(prices)

        result = {
            "metal": metal,
            "currency": currency,
            "price_per_ounce": round(fused_price, 2),
            "price_per_gram": round(fused_price / 31.1035, 2),
            "price_per_kilo": round(fused_price / 31.1035 * 1000, 2),
            "sources_count": len(prices),
            "karats": {},
            "error": False,
        }

        if metal == "XAU":
            for karat, purity in GOLD_KARATS.items():
                result["karats"][karat] = {
                    "per_gram": round((fused_price / 31.1035) * purity, 2),
                    "per_ounce": round(fused_price * purity, 2),
                }

        await cache.set(cache_key, result, ttl=CACHE_TTL["gold"])
        return result

    async def _fetch_metals_api(self, metal: str, currency: str) -> Optional[float]:
        """Fetch from metals-api.com (50 requests/month)."""
        if not settings.metals_api_key:
            return None
        try:
            data = await self._metals_api.get(
                f"/latest?access_key={settings.metals_api_key}&base={currency}&symbols={metal}"
            )
            if data and data.get("success") and "rates" in data:
                rate = data["rates"].get(metal)
                if rate and rate > 0:
                    return 1.0 / rate
        except Exception as exc:
            logger.debug(f"metals-api error: {exc}")
        return None

    async def _fetch_goldapi(self, metal: str, currency: str) -> Optional[float]:
        """Fetch from goldapi.io."""
        api_key = settings.goldapi_key or "goldapi-demo"
        try:
            data = await self._fallback.get(
                f"https://www.goldapi.io/api/{metal}/{currency}",
                headers={"x-access-token": api_key},
            )
            if data and "price" in data:
                return data["price"]
        except Exception as exc:
            logger.debug(f"goldapi error: {exc}")
        return None

    async def _fetch_metals_live(self, metal: str) -> Optional[float]:
        """Fetch from metals.live (free, no key)."""
        try:
            data = await self._fallback.get("https://api.metals.live/v1/spot")
            if data and isinstance(data, list):
                metal_map = {"XAU": "gold", "XAG": "silver", "XPT": "platinum", "XPD": "palladium"}
                metal_name = metal_map.get(metal, "gold")
                for item in data:
                    if item.get("metal", "").lower() == metal_name:
                        return item.get("price")
        except Exception as exc:
            logger.debug(f"metals.live error: {exc}")
        return None

    async def _fetch_yfinance(self, metal: str) -> Optional[float]:
        """Fetch from Yahoo Finance via yfinance (free, no key, most reliable)."""
        metal_ticker_map = {"XAU": "GC=F", "XAG": "SI=F", "XPT": "PL=F", "XPD": "PA=F"}
        ticker_symbol = metal_ticker_map.get(metal, "GC=F")
        try:
            loop = asyncio.get_event_loop()
            def _sync_fetch():
                import yfinance as yf
                t = yf.Ticker(ticker_symbol)
                price = t.fast_info.last_price
                return price
            price = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_fetch), timeout=15.0
            )
            if price and price > 0:
                logger.debug(f"yfinance {ticker_symbol}: {price}")
                return float(price)
        except Exception as exc:
            logger.debug(f"yfinance error: {exc}")
        return None

    def _fuse_prices(self, prices: list[dict]) -> float:
        """Fuse prices with outlier removal."""
        values = [p["price"] for p in prices]
        if len(values) == 1:
            return values[0]

        median = statistics.median(values)
        filtered = [v for v in values if abs(v - median) / max(median, 0.01) <= 0.02]

        if not filtered:
            filtered = values

        return statistics.mean(filtered)

    async def get_all_metals(self, currency: str = "USD") -> dict[str, Any]:
        """Get prices for all supported metals."""
        results = {}
        for metal in SUPPORTED_METALS:
            results[metal] = await self.get_prices(metal, currency)
        return results

    async def close(self) -> None:
        await self._metals_api.close()
        await self._goldapi.close()
        await self._fallback.close()


omega_metals = OmegaMetals()
