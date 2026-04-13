import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaQuakes:
    """Earthquake data from USGS (free, no key)."""

    def __init__(self):
        self._usgs = BaseAPIClient("usgs", "https://earthquake.usgs.gov/fdsnws/event/1")

    async def get_recent(self, min_magnitude: float = 4.0, limit: int = 20) -> dict[str, Any]:
        """Get recent earthquakes."""
        cache_key = f"quakes:recent:{min_magnitude}:{limit}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._usgs.get(
                "/query",
                params={
                    "format": "geojson",
                    "minmagnitude": min_magnitude,
                    "orderby": "time",
                    "limit": limit,
                },
            )

            if data and "features" in data:
                quakes = []
                for feature in data["features"]:
                    props = feature["properties"]
                    coords = feature["geometry"]["coordinates"]
                    quakes.append({
                        "title": props.get("title", ""),
                        "magnitude": props.get("mag", 0),
                        "place": props.get("place", ""),
                        "time": props.get("time"),
                        "longitude": coords[0],
                        "latitude": coords[1],
                        "depth_km": coords[2],
                        "tsunami": props.get("tsunami", 0),
                        "alert": props.get("alert"),
                        "url": props.get("url", ""),
                    })

                result = {"quakes": quakes, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["quakes"])
                return result
        except Exception as exc:
            logger.debug(f"USGS error: {exc}")

        return {"quakes": [], "error": True}

    async def get_by_region(self, lat: float, lon: float, radius_km: float = 500, min_mag: float = 3.0) -> dict[str, Any]:
        """Get earthquakes near a location."""
        try:
            data = await self._usgs.get(
                "/query",
                params={
                    "format": "geojson",
                    "latitude": lat,
                    "longitude": lon,
                    "maxradiuskm": radius_km,
                    "minmagnitude": min_mag,
                    "orderby": "time",
                    "limit": 20,
                },
            )
            if data and "features" in data:
                quakes = [{
                    "title": f["properties"].get("title", ""),
                    "magnitude": f["properties"].get("mag", 0),
                    "place": f["properties"].get("place", ""),
                    "time": f["properties"].get("time"),
                    "depth_km": f["geometry"]["coordinates"][2],
                } for f in data["features"]]
                return {"quakes": quakes, "error": False}
        except Exception as exc:
            logger.debug(f"USGS region error: {exc}")
        return {"quakes": [], "error": True}

    async def close(self) -> None:
        await self._usgs.close()


omega_quakes = OmegaQuakes()
