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

# Sofascore tournament IDs (free, no API key)
_SF_TOURNAMENT_IDS: dict[str, int] = {
    "PL":  17,
    "PD":  8,
    "SA":  23,
    "BL1": 35,
    "FL1": 37,
    "CL":  7,
    "SPL": 679,
    "ELC": 44,
}

_SF_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
}

# Hardcoded team lists (2024-25 seasons) — last-resort fallback when every
# live source (Sofascore standings + day scan) fails or returns empty.
_FALLBACK_TEAMS: dict[str, list[str]] = {
    "PL": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town",
        "Leicester City", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham",
        "West Ham", "Wolverhampton",
    ],
    "PD": [
        "Alavés", "Athletic Club", "Atlético Madrid", "Barcelona", "Real Betis",
        "Celta Vigo", "Espanyol", "Getafe", "Girona", "Las Palmas",
        "Leganés", "Mallorca", "Osasuna", "Rayo Vallecano", "Real Madrid",
        "Real Sociedad", "Sevilla", "Valencia", "Valladolid", "Villarreal",
    ],
    "SA": [
        "Atalanta", "Bologna", "Cagliari", "Como", "Empoli",
        "Fiorentina", "Genoa", "Hellas Verona", "Inter", "Juventus",
        "Lazio", "Lecce", "Milan", "Monza", "Napoli",
        "Parma", "Roma", "Torino", "Udinese", "Venezia",
    ],
    "BL1": [
        "Augsburg", "Bayer Leverkusen", "Bayern München", "Bochum", "Borussia Dortmund",
        "Borussia Mönchengladbach", "Eintracht Frankfurt", "FC St. Pauli", "Freiburg",
        "Heidenheim", "Hoffenheim", "Holstein Kiel", "Mainz 05", "RB Leipzig",
        "Stuttgart", "Union Berlin", "Werder Bremen", "Wolfsburg",
    ],
    "FL1": [
        "Angers", "Auxerre", "Brest", "Le Havre", "Lens",
        "Lille", "Lyon", "Marseille", "Monaco", "Montpellier",
        "Nantes", "Nice", "Paris Saint-Germain", "Reims", "Rennes",
        "Saint-Étienne", "Strasbourg", "Toulouse",
    ],
    "SPL": [
        "Al-Ahli", "Al-Ettifaq", "Al-Fateh", "Al-Fayha", "Al-Hilal",
        "Al-Ittihad", "Al-Kholood", "Al-Nassr", "Al-Okhdood", "Al-Orobah",
        "Al-Qadsiah", "Al-Raed", "Al-Riyadh", "Al-Shabab", "Al-Taawoun",
        "Al-Wehda", "Damac", "Al-Khaleej",
    ],
    "ELC": [
        "Blackburn", "Bristol City", "Burnley", "Cardiff City", "Coventry City",
        "Derby County", "Hull City", "Leeds United", "Luton Town", "Middlesbrough",
        "Millwall", "Norwich City", "Oxford United", "Plymouth Argyle",
        "Portsmouth", "Preston North End", "Queens Park Rangers", "Sheffield United",
        "Sheffield Wednesday", "Stoke City", "Sunderland", "Swansea City",
        "Watford", "West Bromwich Albion",
    ],
    "CL": [
        "Real Madrid", "Manchester City", "Bayern München", "Paris Saint-Germain",
        "Liverpool", "Arsenal", "Barcelona", "Inter", "Borussia Dortmund",
        "Atlético Madrid", "RB Leipzig", "Bayer Leverkusen", "Milan", "Juventus",
        "Celtic", "Feyenoord", "PSV Eindhoven", "Benfica", "Sporting CP",
        "Atalanta", "Aston Villa", "Monaco", "Brest", "Lille",
        "Club Brugge", "Young Boys", "Shakhtar Donetsk", "Dinamo Zagreb",
        "Red Star Belgrade", "Sparta Prague", "Slovan Bratislava", "Sturm Graz",
        "Girona", "Salzburg", "Bologna", "Stuttgart",
    ],
}


def _headers() -> dict:
    return {
        "X-RapidAPI-Key": settings.api_football_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }


def _normalize_sofascore(event: dict) -> dict | None:
    """Normalize a Sofascore event into the standard fixture dict."""
    try:
        home = event.get("homeTeam", {}).get("name", "")
        away = event.get("awayTeam", {}).get("name", "")
        if not home or not away:
            return None
        status_obj  = event.get("status", {})
        status_type = status_obj.get("type", "notstarted")
        elapsed     = status_obj.get("description", "")
        _STATUS_MAP = {
            "notstarted": "NS", "inprogress": "1H",
            "finished": "FT",  "halftime": "HT",
            "postponed": "PST","cancelled": "CANC",
        }
        status = _STATUS_MAP.get(status_type, status_type.upper()[:3])
        scores = event.get("homeScore", {}), event.get("awayScore", {})
        h_score = scores[0].get("current") if status not in ("NS",) else None
        a_score = scores[1].get("current") if status not in ("NS",) else None
        tournament = event.get("tournament", {})
        league_name = tournament.get("name", "")
        import datetime as _dt
        start_ts = event.get("startTimestamp", 0)
        date_utc = ""
        if start_ts:
            date_utc = _dt.datetime.fromtimestamp(
                start_ts, tz=_dt.timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        return {
            "fixture_id":     event.get("id"),
            "league":         league_name,
            "league_ar":      league_name,  # Sofascore doesn't have Arabic names
            "home":           home,
            "away":           away,
            "home_score":     h_score,
            "away_score":     a_score,
            "status":         status,
            "status_elapsed": elapsed,
            "venue":          event.get("venue", {}).get("name", ""),
            "date_utc":       date_utc,
            "source":         "sofascore",
        }
    except Exception:
        return None


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
        league_id   = league_info["id"]
        league_code_up = league_code.upper()
        cache_key = f"apifb:fixtures:{league_code_up}:{status}"
        ttl = CACHE_TTL.get("football_live", 60) if status.upper() == "LIVE" else CACHE_TTL.get("football_static", 3600)
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        from datetime import date, timedelta
        today = date.today()

        # Source 1 — API-Football (RapidAPI)
        if settings.api_football_key:
            params: dict[str, Any] = {"league": league_id, "season": CURRENT_SEASON}
            if status.upper() == "LIVE":
                params["live"] = "all"
            elif status.upper() not in ("ALL", ""):
                params["status"] = status.upper()
            else:
                params["from"] = (today - timedelta(days=3)).isoformat()
                params["to"]   = (today + timedelta(days=4)).isoformat()
            data = await self._get("/fixtures", params)
            if data and "response" in data:
                fixtures = [_normalize_fixture(f, league_code_up) for f in data["response"]]
                await cache.set(cache_key, fixtures, ttl=ttl)
                return fixtures

        # Source 2 — football-data.org (free key)
        if settings.football_data_key:
            fd_fixtures = await self._fetch_football_data(league_code_up, today, timedelta)
            if fd_fixtures:
                await cache.set(cache_key, fd_fixtures, ttl=ttl)
                return fd_fixtures

        # Source 3 — Sofascore (no key, always free) — filter strictly by this league
        sf_id    = _SF_TOURNAMENT_IDS.get(league_code_up)
        league_ar_name = MAJOR_LEAGUES.get(league_code_up, {}).get("name_ar", "")
        all_fixtures: list[dict] = []
        if sf_id:
            for delta in (0, -1, 1, -2, 2, 3):
                d = (today + timedelta(days=delta)).strftime("%Y-%m-%d")
                events = await self._sofascore_raw_day(d)
                for ev in events:
                    if ev.get("tournament", {}).get("id") != sf_id:
                        continue
                    n = _normalize_sofascore(ev)
                    if n:
                        if league_ar_name:
                            n["league_ar"] = league_ar_name
                        all_fixtures.append(n)
        if all_fixtures:
            await cache.set(cache_key, all_fixtures, ttl=ttl)
            return all_fixtures

        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def _fetch_football_data(self, league_code: str, today, timedelta) -> list:
        """Fetch from football-data.org v4 (free key)."""
        # football-data.org uses competition codes directly
        _FD_CODES = {
            "PL": "PL", "PD": "PD", "SA": "SA",
            "BL1": "BL1", "FL1": "FL1", "CL": "CL",
        }
        fd_code = _FD_CODES.get(league_code)
        if not fd_code:
            return []
        date_from = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        date_to   = (today + timedelta(days=4)).strftime("%Y-%m-%d")
        url = f"https://api.football-data.org/v4/competitions/{fd_code}/matches"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    url,
                    params={"dateFrom": date_from, "dateTo": date_to},
                    headers={"X-Auth-Token": settings.football_data_key},
                )
                if r.status_code != 200:
                    logger.debug(f"football-data.org {r.status_code}")
                    return []
                matches = r.json().get("matches", [])
                fixtures = []
                for m in matches:
                    home = m.get("homeTeam", {}).get("name", "")
                    away = m.get("awayTeam", {}).get("name", "")
                    if not home:
                        continue
                    score = m.get("score", {})
                    ft    = score.get("fullTime", {})
                    status_raw = m.get("status", "SCHEDULED")
                    _ST = {
                        "SCHEDULED": "NS", "TIMED": "NS", "IN_PLAY": "1H",
                        "PAUSED": "HT", "FINISHED": "FT",
                        "POSTPONED": "PST", "CANCELLED": "CANC",
                    }
                    league_info = MAJOR_LEAGUES.get(league_code, {})
                    fixtures.append({
                        "fixture_id":     m.get("id"),
                        "league":         league_info.get("name", fd_code),
                        "league_ar":      league_info.get("name_ar", fd_code),
                        "home":           home,
                        "away":           away,
                        "home_score":     ft.get("home"),
                        "away_score":     ft.get("away"),
                        "status":         _ST.get(status_raw, status_raw[:3]),
                        "status_elapsed": m.get("minute"),
                        "venue":          m.get("venue", ""),
                        "date_utc":       m.get("utcDate", ""),
                        "source":         "football-data.org",
                    })
                return fixtures
        except Exception as exc:
            logger.warning(f"football-data.org error: {exc}")
            return []

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
        # Try API-Football first
        if settings.api_football_key:
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
        # Sofascore fallback — free, no key
        return await self._sofascore_live()

    async def _sofascore_live(self) -> list | dict:
        """Fetch live matches from Sofascore (no API key needed)."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                r = await client.get(
                    "https://api.sofascore.com/api/v1/sport/football/events/live",
                    headers=_SF_HEADERS,
                )
                if r.status_code == 200:
                    events = r.json().get("events", [])
                    fixtures = [_normalize_sofascore(e) for e in events[:20]]
                    fixtures = [f for f in fixtures if f]
                    await cache.set("apifb:live", fixtures, ttl=CACHE_TTL.get("football_live", 60))
                    return fixtures if fixtures else {"error": True, "message": "No live matches"}
        except Exception as exc:
            logger.warning(f"Sofascore live error: {exc}")
        stale = await cache.get_stale("apifb:live")
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def _sofascore_raw_day(self, date_str: str) -> list:
        """Fetch and cache raw Sofascore events for one day (un-normalized, includes tournament ID)."""
        cache_key = f"sfsc:raw:{date_str}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
                r = await client.get(
                    f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}",
                    headers=_SF_HEADERS,
                )
                if r.status_code == 200:
                    events = r.json().get("events", [])
                    await cache.set(cache_key, events, ttl=3600 * 6)
                    return events
        except Exception as exc:
            logger.warning(f"Sofascore raw day {date_str}: {exc}")
        return []

    async def _sofascore_scheduled(self, date_str: str) -> list | dict:
        """Fetch scheduled/recent matches from Sofascore for a date (normalized)."""
        cache_key = f"sofascore:sched:{date_str}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        events = await self._sofascore_raw_day(date_str)
        if events:
            _SF_LEAGUE_IDS = set(_SF_TOURNAMENT_IDS.values())
            filtered = [e for e in events if e.get("tournament", {}).get("id") in _SF_LEAGUE_IDS]
            if not filtered:
                return {"error": True}
            fixtures = [_normalize_sofascore(e) for e in filtered[:20]]
            fixtures = [f for f in fixtures if f]
            if fixtures:
                await cache.set(cache_key, fixtures, ttl=CACHE_TTL.get("football_static", 3600))
                return fixtures
        return {"error": True}

    async def get_league_teams(self, league_code: str) -> list[dict]:
        """Return sorted [{id, name}] for a league via standings, fallback to day-scan."""
        sf_id = _SF_TOURNAMENT_IDS.get(league_code.upper())
        if not sf_id:
            return []
        cache_key = f"sfsc:league_teams:{league_code.upper()}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        teams: list[dict] = []
        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
                # Step 1: get latest season ID
                r = await client.get(
                    f"https://api.sofascore.com/api/v1/unique-tournament/{sf_id}/seasons",
                    headers=_SF_HEADERS,
                )
                if r.status_code == 200:
                    seasons = r.json().get("seasons", [])
                    if seasons:
                        season_id = seasons[0]["id"]
                        # Step 2: standings → full team list
                        r2 = await client.get(
                            f"https://api.sofascore.com/api/v1/unique-tournament/{sf_id}/season/{season_id}/standings/total",
                            headers=_SF_HEADERS,
                        )
                        if r2.status_code == 200:
                            for group in r2.json().get("standings", []):
                                for row in group.get("rows", []):
                                    team = row.get("team", {})
                                    tid, tname = team.get("id"), team.get("name", "")
                                    if tid and tname:
                                        teams.append({"id": tid, "name": tname})
        except Exception as exc:
            logger.warning(f"Sofascore standings for {league_code}: {exc}")

        # Fallback: scan ±21 days of fixtures
        if not teams:
            from datetime import date, timedelta
            today = date.today()
            team_dict: dict[int, str] = {}
            for delta in range(-14, 22):
                day = (today + timedelta(days=delta)).strftime("%Y-%m-%d")
                events = await self._sofascore_raw_day(day)
                for ev in events:
                    if ev.get("tournament", {}).get("id") != sf_id:
                        continue
                    for side in ("homeTeam", "awayTeam"):
                        t = ev.get(side, {})
                        tid, tname = t.get("id"), t.get("name", "")
                        if tid and tname:
                            team_dict[tid] = tname
            teams = sorted([{"id": k, "name": v} for k, v in team_dict.items()], key=lambda x: x["name"])

        # Last resort: hardcoded team list (offline / blocked scenarios)
        if not teams:
            fb = _FALLBACK_TEAMS.get(league_code.upper())
            if fb:
                teams = [{"id": i, "name": n} for i, n in enumerate(sorted(fb))]

        if teams:
            await cache.set(cache_key, teams, ttl=3600 * 24)
        return teams

    async def get_team_schedule(self, team_id: int) -> dict:
        """Fetch last-5 + next-5 matches for a team from Sofascore."""
        cache_key = f"sfsc:team_sched:{team_id}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        past: list[dict] = []
        upcoming_raw: list[dict] = []

        for path, dest in (("events/last/0", past), ("events/next/0", upcoming_raw)):
            try:
                async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                    r = await client.get(
                        f"https://api.sofascore.com/api/v1/team/{team_id}/{path}",
                        headers=_SF_HEADERS,
                    )
                    if r.status_code == 200:
                        for ev in r.json().get("events", []):
                            n = _normalize_sofascore(ev)
                            if n:
                                dest.append(n)
            except Exception as exc:
                logger.warning(f"Sofascore team {path}: {exc}")

        # most recent first; cap at 5
        past = past[:5]   # events/last/0 returns most-recent first
        live     = [f for f in upcoming_raw if f["status"] not in ("NS", "TBD", "PST", "CANC")]
        upcoming = [f for f in upcoming_raw if f["status"] in ("NS", "TBD")][:5]

        has_data = bool(past or live or upcoming)
        result = {"past": past, "live": live, "upcoming": upcoming, "error": not has_data}
        await cache.set(cache_key, result, ttl=60 if live else 300)
        return result

    async def get_team_schedule_by_name(self, team_name: str, league_code: str = "") -> dict:
        """Scan Sofascore daily events to build team schedule — no Sofascore team ID needed."""
        cache_key = f"sfsc:tsched_name:{league_code}:{team_name}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        from datetime import date, timedelta
        today = date.today()
        sf_id = _SF_TOURNAMENT_IDS.get(league_code.upper()) if league_code else None
        team_lower = team_name.lower()

        past: list[dict] = []
        upcoming: list[dict] = []
        live: list[dict] = []

        for delta in range(-20, 10):
            day = (today + timedelta(days=delta)).strftime("%Y-%m-%d")
            events = await self._sofascore_raw_day(day)
            for ev in events:
                if sf_id and ev.get("tournament", {}).get("id") != sf_id:
                    continue
                home = ev.get("homeTeam", {}).get("name", "")
                away = ev.get("awayTeam", {}).get("name", "")
                if team_lower not in (home.lower(), away.lower()):
                    continue
                n = _normalize_sofascore(ev)
                if not n:
                    continue
                status = n.get("status", "NS")
                if status in ("1H", "2H", "HT", "ET", "PEN"):
                    live.append(n)
                elif status == "FT":
                    past.append(n)
                else:
                    upcoming.append(n)

        past.sort(key=lambda x: x.get("date_utc", ""), reverse=True)
        upcoming.sort(key=lambda x: x.get("date_utc", ""))

        has_data = bool(past or live or upcoming)
        result = {
            "past": past[:5],
            "live": live,
            "upcoming": upcoming[:5],
            "error": not has_data,
        }
        if has_data:
            await cache.set(cache_key, result, ttl=60 if live else 300)
        return result

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
