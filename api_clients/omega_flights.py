import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaFlights:
    """Flight tracking using OpenSky Network (free, no key)."""

    def __init__(self):
        self._opensky = BaseAPIClient("opensky", "https://opensky-network.org/api")

    async def get_flights_by_airport(self, airport_icao: str) -> dict[str, Any]:
        """Get departures/arrivals for an airport."""
        cache_key = f"flights:{airport_icao}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        import time
        end_time = int(time.time())
        begin_time = end_time - 7200

        try:
            departures = await self._opensky.get(
                "/flights/departure",
                params={"airport": airport_icao, "begin": begin_time, "end": end_time},
            )
            arrivals = await self._opensky.get(
                "/flights/arrival",
                params={"airport": airport_icao, "begin": begin_time, "end": end_time},
            )

            result = {
                "airport": airport_icao,
                "departures": self._parse_flights(departures) if isinstance(departures, list) else [],
                "arrivals": self._parse_flights(arrivals) if isinstance(arrivals, list) else [],
                "error": False,
            }
            await cache.set(cache_key, result, ttl=CACHE_TTL["flights"])
            return result
        except Exception as exc:
            logger.debug(f"OpenSky error: {exc}")

        return {"airport": airport_icao, "departures": [], "arrivals": [], "error": True}

    async def track_flight(self, callsign: str) -> dict[str, Any]:
        """Track a specific flight by callsign."""
        try:
            data = await self._opensky.get("/states/all", params={"callsign": callsign.strip()})
            if data and data.get("states"):
                state = data["states"][0]
                return {
                    "callsign": state[1].strip() if state[1] else callsign,
                    "origin_country": state[2],
                    "longitude": state[5],
                    "latitude": state[6],
                    "altitude": state[7],
                    "velocity": state[9],
                    "heading": state[10],
                    "on_ground": state[8],
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"Flight track error: {exc}")

        return {"callsign": callsign, "error": True, "message": "Flight not found"}

    def _parse_flights(self, flights: list) -> list[dict]:
        """Parse flight data."""
        result = []
        for f in flights[:20]:
            result.append({
                "callsign": f.get("callsign", "").strip(),
                "departure": f.get("estDepartureAirport", ""),
                "arrival": f.get("estArrivalAirport", ""),
                "first_seen": f.get("firstSeen"),
                "last_seen": f.get("lastSeen"),
            })
        return result

    async def close(self) -> None:
        await self._opensky.close()


omega_flights = OmegaFlights()
