import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL

# TMDB genre ID → name (covers movies + TV)
_GENRE_MAP: dict[int, str] = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
    53: "Thriller", 10752: "War", 37: "Western", 10759: "Action & Adventure",
    10762: "Kids", 10763: "News", 10764: "Reality", 10765: "Sci-Fi & Fantasy",
    10766: "Soap", 10767: "Talk", 10768: "War & Politics", 10770: "TV Movie",
}
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaMovies:
    """Movies & TV with TMDB (primary) + OMDb (IMDb/RT ratings) + Jikan (anime)."""

    def __init__(self):
        self._tmdb = BaseAPIClient("tmdb", "https://api.themoviedb.org/3")
        self._omdb = BaseAPIClient("omdb", "https://www.omdbapi.com")
        self._jikan = BaseAPIClient("jikan", "https://api.jikan.moe/v4")

    async def search(self, query: str, media_type: str = "multi", lang: str = "en") -> dict[str, Any]:
        """Search for movies/TV/anime."""
        cache_key = f"movie:search:{query}:{media_type}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        if media_type == "anime":
            result = await self._search_anime(query)
        else:
            result = await self._search_tmdb(query, media_type, lang)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])

        return result or {"results": [], "error": True}

    async def get_details(self, tmdb_id: int, media_type: str = "movie", lang: str = "en") -> dict[str, Any]:
        """Get detailed info for a movie/TV show."""
        cache_key = f"movie:detail:{tmdb_id}:{media_type}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = await self._fetch_tmdb_details(tmdb_id, media_type, lang)

        if result and not result.get("error"):
            if result.get("imdb_id") and settings.omdb_api_key:
                omdb_data = await self._fetch_omdb(result["imdb_id"])
                if omdb_data:
                    result["imdb_rating"] = omdb_data.get("imdb_rating")
                    result["rotten_tomatoes"] = omdb_data.get("rotten_tomatoes")
                    result["metacritic"] = omdb_data.get("metacritic")

            await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])

        return result or {"error": True, "message": "Details unavailable"}

    async def get_trending(self, media_type: str = "all", time_window: str = "week", lang: str = "en") -> dict[str, Any]:
        """Get trending movies/TV."""
        cache_key = f"movie:trending:{media_type}:{time_window}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._tmdb.get(
                f"/trending/{media_type}/{time_window}",
                params={"api_key": settings.tmdb_api_key, "language": lang},
            )
            if data and "results" in data:
                results = [{
                    "id": item["id"],
                    "title": item.get("title") or item.get("name", ""),
                    "media_type": item.get("media_type", media_type),
                    "overview": item.get("overview", ""),
                    "vote_average": item.get("vote_average", 0),
                    "poster": f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else "",
                    "release_date": item.get("release_date") or item.get("first_air_date", ""),
                    "genres": [_GENRE_MAP[g] for g in item.get("genre_ids", []) if g in _GENRE_MAP][:3],
                } for item in data["results"][:20]]

                result = {"results": results, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])
                return result
        except Exception as exc:
            logger.debug(f"TMDB trending error: {exc}")

        return {"results": [], "error": True}

    async def _search_tmdb(self, query: str, media_type: str, lang: str) -> Optional[dict]:
        """Search TMDB."""
        try:
            endpoint = f"/search/{media_type}" if media_type in ("movie", "tv") else "/search/multi"
            data = await self._tmdb.get(
                endpoint,
                params={"api_key": settings.tmdb_api_key, "query": query, "language": lang},
            )
            if data and "results" in data:
                results = [{
                    "id": item["id"],
                    "title": item.get("title") or item.get("name", ""),
                    "media_type": item.get("media_type", media_type),
                    "overview": item.get("overview", "")[:200],
                    "vote_average": item.get("vote_average", 0),
                    "poster": f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else "",
                    "release_date": item.get("release_date") or item.get("first_air_date", ""),
                    "genres": [_GENRE_MAP[g] for g in item.get("genre_ids", []) if g in _GENRE_MAP][:3],
                } for item in data["results"][:10]]
                return {"results": results, "error": False}
        except Exception as exc:
            logger.debug(f"TMDB search error: {exc}")
        return None

    async def _fetch_tmdb_details(self, tmdb_id: int, media_type: str, lang: str) -> Optional[dict]:
        """Fetch detailed info from TMDB."""
        try:
            data = await self._tmdb.get(
                f"/{media_type}/{tmdb_id}",
                params={"api_key": settings.tmdb_api_key, "language": lang, "append_to_response": "credits,videos"},
            )
            if data:
                result = {
                    "id": data["id"],
                    "title": data.get("title") or data.get("name", ""),
                    "overview": data.get("overview", ""),
                    "vote_average": data.get("vote_average", 0),
                    "vote_count": data.get("vote_count", 0),
                    "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else "",
                    "backdrop": f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}" if data.get("backdrop_path") else "",
                    "release_date": data.get("release_date") or data.get("first_air_date", ""),
                    "runtime": data.get("runtime") or data.get("episode_run_time", [0])[0] if data.get("episode_run_time") else 0,
                    "genres": [g["name"] for g in data.get("genres", [])],
                    "imdb_id": data.get("imdb_id", ""),
                    "budget": data.get("budget", 0),
                    "revenue": data.get("revenue", 0),
                    "status": data.get("status", ""),
                    "tagline": data.get("tagline", ""),
                    "media_type": media_type,
                    "error": False,
                }

                credits = data.get("credits", {})
                result["cast"] = [{"name": c["name"], "character": c.get("character", "")} for c in credits.get("cast", [])[:10]]
                result["director"] = next((c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"), "")

                videos = data.get("videos", {}).get("results", [])
                trailer = next((v for v in videos if v.get("type") == "Trailer" and v.get("site") == "YouTube"), None)
                result["trailer_url"] = f"https://youtube.com/watch?v={trailer['key']}" if trailer else ""

                return result
        except Exception as exc:
            logger.debug(f"TMDB details error: {exc}")
        return None

    async def _fetch_omdb(self, imdb_id: str) -> Optional[dict]:
        """Fetch ratings from OMDb (7-day cache)."""
        cache_key = f"omdb:{imdb_id}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._omdb.get(
                "/",
                params={"apikey": settings.omdb_api_key, "i": imdb_id},
            )
            if data and data.get("Response") == "True":
                result = {
                    "imdb_rating": data.get("imdbRating", "N/A"),
                    "metacritic": data.get("Metascore", "N/A"),
                }
                for rating in data.get("Ratings", []):
                    if "Rotten Tomatoes" in rating.get("Source", ""):
                        result["rotten_tomatoes"] = rating["Value"]
                        break
                else:
                    result["rotten_tomatoes"] = "N/A"

                await cache.set(cache_key, result, ttl=604800)
                return result
        except Exception as exc:
            logger.debug(f"OMDb error: {exc}")
        return None

    async def get_by_genre(self, genre_id: int, lang: str = "en") -> dict[str, Any]:
        """Get top movies by TMDB genre ID using discover endpoint."""
        cache_key = f"movie:genre:{genre_id}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached
        try:
            tmdb_lang = "ar" if lang == "ar" else "en-US"
            data = await self._tmdb.get(
                "/discover/movie",
                params={
                    "api_key": settings.tmdb_api_key,
                    "with_genres": genre_id,
                    "sort_by": "popularity.desc",
                    "language": tmdb_lang,
                    "vote_count.gte": 200,
                    "page": 1,
                },
            )
            if data and "results" in data:
                results = [
                    {
                        "id": item["id"],
                        "title": item.get("title") or item.get("name", ""),
                        "overview": (item.get("overview") or "")[:200],
                        "release_date": item.get("release_date") or item.get("first_air_date", ""),
                        "vote_average": round(item.get("vote_average", 0), 1),
                        "genres": [_GENRE_MAP[g] for g in item.get("genre_ids", []) if g in _GENRE_MAP][:3],
                        "media_type": "movie",
                    }
                    for item in data["results"][:10]
                    if item.get("vote_average", 0) >= 6.0
                ]
                result = {"results": results, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])
                return result
        except Exception as exc:
            logger.debug(f"get_by_genre error: {exc}")
        return {"results": [], "error": True}

    async def _search_anime(self, query: str) -> Optional[dict]:
        """Search anime using Jikan (MyAnimeList)."""
        try:
            data = await self._jikan.get("/anime", params={"q": query, "limit": 10})
            if data and "data" in data:
                results = [{
                    "id": item["mal_id"],
                    "title": item.get("title_english") or item.get("title", ""),
                    "title_japanese": item.get("title_japanese", ""),
                    "media_type": "anime",
                    "overview": item.get("synopsis", "")[:200],
                    "vote_average": item.get("score", 0),
                    "poster": item.get("images", {}).get("jpg", {}).get("image_url", ""),
                    "episodes": item.get("episodes"),
                    "status": item.get("status", ""),
                    "aired": item.get("aired", {}).get("string", ""),
                } for item in data["data"]]
                return {"results": results, "error": False}
        except Exception as exc:
            logger.debug(f"Jikan search error: {exc}")
        return None

    async def close(self) -> None:
        await self._tmdb.close()
        await self._omdb.close()
        await self._jikan.close()


omega_movies = OmegaMovies()
