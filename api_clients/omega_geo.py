import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaGeo:
    """Geocoding and location services."""

    def __init__(self):
        self._nominatim = BaseAPIClient("nominatim", "https://nominatim.openstreetmap.org")

    async def geocode(self, query: str) -> Optional[dict[str, Any]]:
        """Geocode a location name to coordinates."""
        cache_key = f"geo:{query.lower()}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._nominatim.get(
                "/search",
                params={"q": query, "format": "json", "limit": 1, "accept-language": "en"},
                headers={"User-Agent": "OmegaBot/1.0"},
            )
            if data and isinstance(data, list) and data:
                result = {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "name": data[0].get("display_name", query),
                    "type": data[0].get("type", ""),
                }
                await cache.set(cache_key, result, ttl=86400)
                return result
        except Exception as exc:
            logger.debug(f"Geocode error: {exc}")
        return None

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[dict[str, Any]]:
        """Reverse geocode coordinates to location name."""
        try:
            data = await self._nominatim.get(
                "/reverse",
                params={"lat": lat, "lon": lon, "format": "json", "accept-language": "en"},
                headers={"User-Agent": "OmegaBot/1.0"},
            )
            if data and "address" in data:
                return {
                    "city": data["address"].get("city") or data["address"].get("town", ""),
                    "country": data["address"].get("country", ""),
                    "country_code": data["address"].get("country_code", "").upper(),
                    "display_name": data.get("display_name", ""),
                }
        except Exception as exc:
            logger.debug(f"Reverse geocode error: {exc}")
        return None

    async def close(self) -> None:
        await self._nominatim.close()


omega_geo = OmegaGeo()
