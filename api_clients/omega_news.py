import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


class OmegaNews:
    """News aggregation from NewsAPI + GNews + RSS feeds."""

    def __init__(self):
        self._newsapi = BaseAPIClient("newsapi", "https://newsapi.org/v2")
        self._gnews = BaseAPIClient("gnews", "https://gnews.io/api/v4")
        self._rss = BaseAPIClient("rss_news")

    async def get_headlines(self, category: str = "general", country: str = "us", lang: str = "en") -> dict[str, Any]:
        """Get top headlines."""
        cache_key = f"news:headlines:{category}:{country}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = None  # initialise before conditional branches
        # Limited APIs first (auto-restore when quota renews)
        if quota.has_quota("newsapi"):
            result = await self._fetch_newsapi(category, country)
            if result and not result.get("error"):
                quota.use_quota("newsapi")
        if (not result or result.get("error")) and quota.has_quota("gnews"):
            result = await self._fetch_gnews(category, lang)
            if result and not result.get("error"):
                quota.use_quota("gnews")
        # Unlimited RSS fallback (when all limited exhausted)
        if not result or result.get("error"):
            result = await self._fetch_rss(lang)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["news"])

        return result or {"articles": [], "error": True}

    async def search_news(self, query: str, lang: str = "en") -> dict[str, Any]:
        """Search news by keyword."""
        cache_key = f"news:search:{query}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            if settings.newsapi_key:
                data = await self._newsapi.get(
                    "/everything",
                    params={"apiKey": settings.newsapi_key, "q": query, "language": lang, "pageSize": 10, "sortBy": "publishedAt"},
                )
                if data and data.get("status") == "ok":
                    articles = self._parse_newsapi_articles(data.get("articles", []))
                    result = {"articles": articles, "query": query, "error": False}
                    await cache.set(cache_key, result, ttl=CACHE_TTL["news"])
                    return result
        except Exception as exc:
            logger.debug(f"NewsAPI search error: {exc}")

        return {"articles": [], "error": True}

    async def _fetch_newsapi(self, category: str, country: str) -> Optional[dict]:
        """Fetch from NewsAPI."""
        if not settings.newsapi_key:
            return None
        try:
            data = await self._newsapi.get(
                "/top-headlines",
                params={"apiKey": settings.newsapi_key, "category": category, "country": country, "pageSize": 20},
            )
            if data and data.get("status") == "ok":
                articles = self._parse_newsapi_articles(data.get("articles", []))
                return {"articles": articles, "source": "NewsAPI", "error": False}
        except Exception as exc:
            logger.debug(f"NewsAPI error: {exc}")
        return None

    async def _fetch_gnews(self, category: str, lang: str) -> Optional[dict]:
        """Fetch from GNews."""
        if not settings.gnews_api_key:
            return None
        try:
            data = await self._gnews.get(
                "/top-headlines",
                params={"token": settings.gnews_api_key, "topic": category, "lang": lang, "max": 10},
            )
            if data and "articles" in data:
                articles = [{
                    "title": a.get("title", ""),
                    "description": a.get("description", ""),
                    "url": a.get("url", ""),
                    "source": a.get("source", {}).get("name", ""),
                    "published_at": a.get("publishedAt", ""),
                    "image": a.get("image", ""),
                } for a in data["articles"]]
                return {"articles": articles, "source": "GNews", "error": False}
        except Exception as exc:
            logger.debug(f"GNews error: {exc}")
        return None

    async def _fetch_rss(self, lang: str) -> Optional[dict]:
        """Fetch from RSS feeds as fallback. Uses xml.etree for correct XML parsing."""
        import xml.etree.ElementTree as ET
        import html as html_mod

        feeds = {
            "en": [
                "https://feeds.bbci.co.uk/news/rss.xml",
                "https://feeds.reuters.com/reuters/topNews",
                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            ],
            "ar": [
                "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9",
                "https://www.bbc.com/arabic/rss.xml",
                "https://arabic.rt.com/rss/",
            ],
        }

        rss_urls = feeds.get(lang, feeds["en"])
        articles = []

        for url in rss_urls:
            try:
                raw = await self._rss.fetch_html(url)
                if not raw or len(raw) < 200:
                    continue

                # Strip any BOM or XML declaration that may confuse ET
                raw_clean = raw.strip()
                if raw_clean.startswith('\ufeff'):
                    raw_clean = raw_clean[1:]

                # Parse as proper XML
                root = ET.fromstring(raw_clean)
                # RSS items can be at channel/item or directly at item
                items = root.findall('.//item')[:10]
                for item in items:
                    def _text(tag):
                        el = item.find(tag)
                        if el is None:
                            return ""
                        txt = (el.text or "").strip()
                        # Unwrap CDATA if present
                        return html_mod.unescape(txt)

                    title = _text("title")
                    if not title:
                        continue
                    link = _text("link")
                    # link may be in a different namespace or as text after <link/>
                    if not link:
                        link_el = item.find("link")
                        if link_el is not None:
                            link = (link_el.tail or "").strip()
                    articles.append({
                        "title": title[:120],
                        "description": _text("description")[:200],
                        "url": link,
                        "source": "RSS",
                        "published_at": _text("pubDate"),
                    })
                if articles:
                    break  # got enough from first working feed
            except Exception as exc:
                logger.debug(f"RSS error for {url}: {exc}")

        if articles:
            return {"articles": articles[:10], "source": "RSS", "error": False}
        return None

    def _parse_newsapi_articles(self, articles: list) -> list[dict]:
        """Parse NewsAPI articles into standard format."""
        return [{
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", ""),
            "published_at": a.get("publishedAt", ""),
            "image": a.get("urlToImage", ""),
        } for a in articles if a.get("title")]

    async def close(self) -> None:
        await self._newsapi.close()
        await self._gnews.close()
        await self._rss.close()


omega_news = OmegaNews()
