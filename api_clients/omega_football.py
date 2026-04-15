import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from config import settings, CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)

BASE = "https://api-football-v1.p.rapidapi.com/v3"
CURRENT_SEASON = 2024

MAJOR_LEAGUES = {
    "PL":  {"id": 39,  "name": "Premier League",        "name_ar": "الدوري الإنجليزي",       "country": "England"},
    "PD":  {"id": 140, "name": "La Liga",               "name_ar": "الدوري الإسباني",        "country": "Spain"},
    "SA":  {"id": 135, "name": "Serie A",               "name_ar": "الدوري الإيطالي",        "country": "Italy"},
    "BL1": {"id": 78,  "name": "Bundesliga",            "name_ar": "الدوري الألماني",        "country": "Germany"},
    "FL1": {"id": 61,  "name": "Ligue 1",               "name_ar": "الدوري الفرنسي",         "country": "France"},
    "CL":  {"id": 2,   "name": "Champions League",      "name_ar": "دوري أبطال أوروبا",      "country": "Europe"},
    "SPL": {"id": 307, "name": "Saudi Pro League",      "name_ar": "دوري روشن",              "country": "Saudi Arabia"},
    "ELC": {"id": 40,  "name": "Championship",          "name_ar": "دوري الدرجة الأولى",     "country": "England"},
}


def _headers() -> dict:
    return {
        "X-RapidAPI-Key": settings.api_football_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }


def _normalize_fixture(fixture: dict, league_code: str) -> dict:
    f = fixture.get("fixture", {})
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    status = f.get("status", {})
    venue = f.get("venue", {})
    league_info = MAJOR_LEAGUES.get(league_code, {})
    return {
        "fixture_id": f.get("id"),
        "league": league_info.get("name", league_code),
        "league_ar": league_info.get("name_ar", league_code),
        "home": teams.get("home", {}).get("name", ""),
        "away": teams.get("away", {}).get("name", ""),
        "home_score": goals.get("home"),
        "away_score": goals.get("away"),
        "status": status.get("short", "NS"),
        "status_elapsed": status.get("elapsed"),
        "venue": venue.get("name", ""),
        "date_utc": f.get("date", ""),
    }


class OmegaFootball:

    async def _get(self, path: str, params: dict) -> Optional[dict]:
        if not settings.api_football_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{BASE}{path}", params=params, headers=_headers())
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning(f"api-football error: {exc}")
            return None

    async def get_fixtures(self, league_code: str, status: str = "all") -> list | dict:
        league_info = MAJOR_LEAGUES.get(league_code.upper())
        if not league_info:
            return {"error": True, "message": "Unknown league"}
        league_id = league_info["id"]
        cache_key = f"apifb:fixtures:{league_code}:{status}"
        ttl = CACHE_TTL.get("football_live", 60) if status.upper() == "LIVE" else CACHE_TTL.get("football_static", 3600)
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        from datetime import date, timedelta
        today = date.today()
        params: dict[str, Any] = {"league": league_id, "season": CURRENT_SEASON}
        if status.upper() == "LIVE":
            params["live"] = "all"
        elif status.upper() not in ("ALL", ""):
            params["status"] = status.upper()
        else:
            # "all" — fetch a 7-day window (3 days back, 3 days forward) to keep results relevant
            params["from"] = (today - timedelta(days=3)).isoformat()
            params["to"]   = (today + timedelta(days=4)).isoformat()
        data = await self._get("/fixtures", params)
        if data and "response" in data:
            fixtures = [_normalize_fixture(f, league_code.upper()) for f in data["response"]]
            await cache.set(cache_key, fixtures, ttl=ttl)
            return fixtures
        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def get_standings(self, league_code: str) -> dict:
        league_info = MAJOR_LEAGUES.get(league_code.upper())
        if not league_info:
            return {"error": True}
        league_id = league_info["id"]
        cache_key = f"apifb:standings:{league_code}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._get("/standings", {"league": league_id, "season": CURRENT_SEASON})
        if data and "response" in data:
            try:
                raw = data["response"][0]["league"]["standings"][0]
                standings = []
                for entry in raw:
                    team = entry.get("team", {})
                    all_s = entry.get("all", {})
                    goals = all_s.get("goals", {})
                    standings.append({
                        "position": entry.get("rank"),
                        "team": team.get("name", ""),
                        "played": all_s.get("played", 0),
                        "won": all_s.get("win", 0),
                        "draw": all_s.get("draw", 0),
                        "lost": all_s.get("lose", 0),
                        "goals_for": goals.get("for", 0),
                        "goals_against": goals.get("against", 0),
                        "goal_diff": entry.get("goalsDiff", 0),
                        "points": entry.get("points", 0),
                    })
                result = {
                    "league": league_code.upper(),
                    "league_name": league_info["name"],
                    "league_name_ar": league_info["name_ar"],
                    "standings": standings,
                    "error": False,
                }
                await cache.set(cache_key, result, ttl=CACHE_TTL.get("football_static", 3600))
                return result
            except (IndexError, KeyError) as exc:
                logger.warning(f"standings parse: {exc}")
        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def get_live(self) -> list | dict:
        cache_key = "apifb:live"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        league_ids = "-".join(str(v["id"]) for v in MAJOR_LEAGUES.values())
        data = await self._get("/fixtures", {"live": league_ids})
        if data and "response" in data:
            fixtures = []
            for raw in data["response"]:
                lid = raw.get("league", {}).get("id")
                code = next((k for k, v in MAJOR_LEAGUES.items() if v["id"] == lid), "")
                fixtures.append(_normalize_fixture(raw, code))
            await cache.set(cache_key, fixtures, ttl=CACHE_TTL.get("football_live", 60))
            return fixtures
        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def get_events(self, fixture_id: int) -> list | dict:
        """Fetch match events: goals, cards, substitutions."""
        cache_key = f"apifb:events:{fixture_id}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._get("/fixtures/events", {"fixture": fixture_id})
        if data and "response" in data:
            events = []
            for ev in data["response"]:
                ev_time = ev.get("time", {})
                events.append({
                    "team":    ev.get("team",   {}).get("name", ""),
                    "player":  ev.get("player", {}).get("name", ""),
                    "assist":  ev.get("assist", {}).get("name", ""),
                    "type":    ev.get("type",   ""),
                    "detail":  ev.get("detail", ""),
                    "elapsed": ev_time.get("elapsed", ""),
                    "extra":   ev_time.get("extra"),
                })
            await cache.set(cache_key, events, ttl=CACHE_TTL.get("football_live", 60))
            return events
        return {"error": True}


omega_football = OmegaFootball()
