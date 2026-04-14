import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)

MAJOR_LEAGUES = {
    "PL": {"name": "Premier League", "name_ar": "الدوري الإنجليزي", "country": "England"},
    "PD": {"name": "La Liga", "name_ar": "الدوري الإسباني", "country": "Spain"},
    "SA": {"name": "Serie A", "name_ar": "الدوري الإيطالي", "country": "Italy"},
    "BL1": {"name": "Bundesliga", "name_ar": "الدوري الألماني", "country": "Germany"},
    "FL1": {"name": "Ligue 1", "name_ar": "الدوري الفرنسي", "country": "France"},
    "CL": {"name": "Champions League", "name_ar": "دوري أبطال أوروبا", "country": "Europe"},
    "SPL": {"name": "Saudi Pro League", "name_ar": "دوري روشن", "country": "Saudi Arabia"},
    "ELC": {"name": "Championship", "name_ar": "الدوري الإنجليزي الدرجة الأولى", "country": "England"},
}


class OmegaFootball:
    """Football data with multi-source fusion (football-data.org + ESPN + TheSportsDB)."""

    def __init__(self):
        self._football_data = BaseAPIClient("football_data", "https://api.football-data.org/v4")
        self._espn = BaseAPIClient("espn_football", "https://site.api.espn.com/apis/site/v2/sports/soccer")
        self._sportsdb = BaseAPIClient("thesportsdb", "https://www.thesportsdb.com/api/v1/json")

    async def get_standings(self, league: str = "PL") -> dict[str, Any]:
        """Get league standings with multi-source fusion."""
        cache_key = f"football:standings:{league}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # Limited API first (auto-restores when quota renews)
        if quota.has_quota("football_data"):
            result = await self._fetch_fd_standings(league)
            if result and not result.get("error"):
                quota.use_quota("football_data")

        # Unlimited ESPN fallback (when football-data exhausted)
        if not result or result.get("error"):
            result = await self._fetch_espn_standings(league)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["football_static"])

        if not result or result.get("error"):
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                return result
        return result or {"error": True, "message": "Standings unavailable"}

    async def get_matches(self, league: str = "PL", status: str = "SCHEDULED") -> dict[str, Any]:
        """Get matches for a league."""
        cache_key = f"football:matches:{league}:{status}"
        ttl = CACHE_TTL["football_live"] if status == "LIVE" else CACHE_TTL["football_static"]
        cached = await cache.get(cache_key)
        if cached:
            return cached

        if quota.has_quota("football_data"):
            result = await self._fetch_fd_matches(league, status)
            if result and not result.get("error"):
                quota.use_quota("football_data")

        if not result or result.get("error"):
            result = await self._fetch_espn_scores(league)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=ttl)

        return result or {"error": True, "message": "Matches unavailable"}

    async def get_live_scores(self) -> dict[str, Any]:
        """Get all live scores across leagues."""
        cache_key = "football:live"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        scores = await self._fetch_espn_live()
        if scores:
            await cache.set(cache_key, scores, ttl=CACHE_TTL["football_live"])
            return scores

        return {"matches": [], "error": False, "message": "No live matches"}

    async def _fetch_fd_standings(self, league: str) -> Optional[dict]:
        """Fetch standings from football-data.org."""
        if not settings.football_data_key:
            return None
        try:
            data = await self._football_data.get(
                f"/competitions/{league}/standings",
                headers={"X-Auth-Token": settings.football_data_key},
            )
            if data and "standings" in data:
                standings = []
                for table in data["standings"]:
                    if table.get("type") == "TOTAL":
                        for entry in table.get("table", []):
                            standings.append({
                                "position": entry["position"],
                                "team": entry["team"]["name"],
                                "team_crest": entry["team"].get("crest", ""),
                                "played": entry["playedGames"],
                                "won": entry["won"],
                                "draw": entry["draw"],
                                "lost": entry["lost"],
                                "goals_for": entry["goalsFor"],
                                "goals_against": entry["goalsAgainst"],
                                "goal_diff": entry["goalDifference"],
                                "points": entry["points"],
                            })
                league_info = MAJOR_LEAGUES.get(league, {})
                return {
                    "league": league,
                    "league_name": league_info.get("name", league),
                    "league_name_ar": league_info.get("name_ar", league),
                    "standings": standings,
                    "source": "football-data.org",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"football-data standings error: {exc}")
        return None

    async def _fetch_fd_matches(self, league: str, status: str) -> Optional[dict]:
        """Fetch matches from football-data.org."""
        if not settings.football_data_key:
            return None
        try:
            params = {"status": status} if status != "ALL" else {}
            data = await self._football_data.get(
                f"/competitions/{league}/matches",
                params=params,
                headers={"X-Auth-Token": settings.football_data_key},
            )
            if data and "matches" in data:
                matches = []
                for m in data["matches"][:20]:
                    matches.append({
                        "home": m["homeTeam"]["name"],
                        "away": m["awayTeam"]["name"],
                        "score_home": m.get("score", {}).get("fullTime", {}).get("home"),
                        "score_away": m.get("score", {}).get("fullTime", {}).get("away"),
                        "status": m["status"],
                        "date": m.get("utcDate", ""),
                        "matchday": m.get("matchday"),
                    })
                return {"league": league, "matches": matches, "source": "football-data.org", "error": False}
        except Exception as exc:
            logger.debug(f"football-data matches error: {exc}")
        return None

    async def _fetch_espn_standings(self, league: str) -> Optional[dict]:
        """Fetch standings from ESPN (free, no key)."""
        espn_league_map = {"PL": "eng.1", "PD": "esp.1", "SA": "ita.1", "BL1": "ger.1", "FL1": "fra.1"}
        espn_league = espn_league_map.get(league)
        if not espn_league:
            return None
        try:
            data = await self._espn.get(f"/{espn_league}/standings")
            if data and "children" in data:
                standings = []
                for group in data.get("children", []):
                    for entry in group.get("standings", {}).get("entries", []):
                        team_info = entry.get("team", {})
                        stats = {s["name"]: s["value"] for s in entry.get("stats", [])}
                        standings.append({
                            "position": int(stats.get("rank", 0)),
                            "team": team_info.get("displayName", ""),
                            "team_crest": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else "",
                            "played": int(stats.get("gamesPlayed", 0)),
                            "won": int(stats.get("wins", 0)),
                            "draw": int(stats.get("ties", 0)),
                            "lost": int(stats.get("losses", 0)),
                            "points": int(stats.get("points", 0)),
                            "goal_diff": int(stats.get("pointDifferential", 0)),
                        })
                league_info = MAJOR_LEAGUES.get(league, {})
                return {
                    "league": league,
                    "league_name": league_info.get("name", league),
                    "standings": sorted(standings, key=lambda x: x["position"]),
                    "source": "ESPN",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"ESPN standings error: {exc}")
        return None

    async def _fetch_espn_scores(self, league: str) -> Optional[dict]:
        """Fetch scores from ESPN."""
        espn_map = {"PL": "eng.1", "PD": "esp.1", "SA": "ita.1", "BL1": "ger.1", "FL1": "fra.1"}
        espn_league = espn_map.get(league)
        if not espn_league:
            return None
        try:
            data = await self._espn.get(f"/{espn_league}/scoreboard")
            if data and "events" in data:
                matches = []
                for event in data["events"]:
                    comps = event.get("competitions", [{}])
                    if comps:
                        comp = comps[0]
                        teams = comp.get("competitors", [])
                        if len(teams) >= 2:
                            home = next((t for t in teams if t.get("homeAway") == "home"), teams[0])
                            away = next((t for t in teams if t.get("homeAway") == "away"), teams[1])
                            matches.append({
                                "home": home.get("team", {}).get("displayName", ""),
                                "away": away.get("team", {}).get("displayName", ""),
                                "score_home": home.get("score"),
                                "score_away": away.get("score"),
                                "status": event.get("status", {}).get("type", {}).get("name", ""),
                                "date": event.get("date", ""),
                            })
                return {"league": league, "matches": matches, "source": "ESPN", "error": False}
        except Exception as exc:
            logger.debug(f"ESPN scores error: {exc}")
        return None

    async def _fetch_espn_live(self) -> Optional[dict]:
        """Fetch all live scores from ESPN."""
        all_matches = []
        for espn_league in ["eng.1", "esp.1", "ita.1", "ger.1", "fra.1"]:
            try:
                data = await self._espn.get(f"/{espn_league}/scoreboard")
                if data and "events" in data:
                    for event in data["events"]:
                        status = event.get("status", {}).get("type", {}).get("state", "")
                        if status == "in":
                            comps = event.get("competitions", [{}])
                            if comps:
                                comp = comps[0]
                                teams = comp.get("competitors", [])
                                if len(teams) >= 2:
                                    home = next((t for t in teams if t.get("homeAway") == "home"), teams[0])
                                    away = next((t for t in teams if t.get("homeAway") == "away"), teams[1])
                                    all_matches.append({
                                        "league": espn_league,
                                        "home": home.get("team", {}).get("displayName", ""),
                                        "away": away.get("team", {}).get("displayName", ""),
                                        "score_home": home.get("score"),
                                        "score_away": away.get("score"),
                                        "clock": event.get("status", {}).get("displayClock", ""),
                                        "period": event.get("status", {}).get("period", 0),
                                    })
            except Exception as exc:
                logger.debug(f"ESPN live error for {espn_league}: {exc}")

        return {"matches": all_matches, "error": False}

    async def close(self) -> None:
        await self._football_data.close()
        await self._espn.close()
        await self._sportsdb.close()


omega_football = OmegaFootball()
