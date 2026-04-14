import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaCrypto:
    """Cryptocurrency data from CoinGecko + CoinCap + Binance."""

    def __init__(self):
        self._coingecko = BaseAPIClient("coingecko", "https://api.coingecko.com/api/v3")
        self._coincap = BaseAPIClient("coincap", "https://api.coincap.io/v2")

    async def get_price(self, coin_id: str = "bitcoin", currency: str = "usd") -> dict[str, Any]:
        """Get cryptocurrency price."""
        cache_key = f"crypto:{coin_id}:{currency}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = await self._fetch_coingecko(coin_id, currency)
        if not result or result.get("error"):
            result = await self._fetch_coincap(coin_id)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["crypto"])

        if not result or result.get("error"):
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                return result
        return result or {"error": True, "message": "Price unavailable"}

    async def get_top_coins(self, limit: int = 20, currency: str = "usd") -> dict[str, Any]:
        """Get top cryptocurrencies by market cap."""
        cache_key = f"crypto:top:{limit}:{currency}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._coingecko.get(
                "/coins/markets",
                params={"vs_currency": currency, "order": "market_cap_desc", "per_page": limit, "page": 1, "sparkline": "false"},
            )
            if data and isinstance(data, list):
                coins = [{
                    "id": c["id"],
                    "symbol": c["symbol"].upper(),
                    "name": c["name"],
                    "price": c["current_price"],
                    "change_24h": c.get("price_change_percentage_24h", 0),
                    "market_cap": c.get("market_cap", 0),
                    "volume_24h": c.get("total_volume", 0),
                    "rank": c.get("market_cap_rank", 0),
                    "image": c.get("image", ""),
                } for c in data]

                result = {"coins": coins, "currency": currency, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["crypto"])
                return result
        except Exception as exc:
            logger.debug(f"CoinGecko top coins error: {exc}")

        return {"coins": [], "error": True}

    async def _fetch_coingecko(self, coin_id: str, currency: str) -> Optional[dict]:
        """Fetch from CoinGecko."""
        try:
            data = await self._coingecko.get(
                f"/coins/{coin_id}",
                params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
            )
            if data and "market_data" in data:
                md = data["market_data"]
                return {
                    "id": data["id"],
                    "symbol": data["symbol"].upper(),
                    "name": data["name"],
                    "price": md["current_price"].get(currency, 0),
                    "change_24h": md.get("price_change_percentage_24h", 0),
                    "change_7d": md.get("price_change_percentage_7d", 0),
                    "market_cap": md.get("market_cap", {}).get(currency, 0),
                    "volume_24h": md.get("total_volume", {}).get(currency, 0),
                    "ath": md.get("ath", {}).get(currency, 0),
                    "atl": md.get("atl", {}).get(currency, 0),
                    "rank": data.get("market_cap_rank", 0),
                    "image": data.get("image", {}).get("small", ""),
                    "source": "CoinGecko",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"CoinGecko error: {exc}")
        return None

    async def _fetch_coincap(self, coin_id: str) -> Optional[dict]:
        """Fetch from CoinCap (fallback)."""
        try:
            data = await self._coincap.get(f"/assets/{coin_id}")
            if data and "data" in data:
                d = data["data"]
                return {
                    "id": d["id"],
                    "symbol": d["symbol"],
                    "name": d["name"],
                    "price": float(d.get("priceUsd", 0)),
                    "change_24h": float(d.get("changePercent24Hr", 0)),
                    "market_cap": float(d.get("marketCapUsd", 0)),
                    "volume_24h": float(d.get("volumeUsd24Hr", 0)),
                    "rank": int(d.get("rank", 0)),
                    "source": "CoinCap",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"CoinCap error: {exc}")
        return None

    async def close(self) -> None:
        await self._coingecko.close()
        await self._coincap.close()


omega_crypto = OmegaCrypto()
