import logging
import xml.etree.ElementTree as ET
import html as html_mod
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)

# Browser-like headers — prevents 403 from news CDNs
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

# RSS feeds that reliably serve cloud/datacenter IPs
_RSS_FEEDS = {
    "en": [
        "https://news.google.com/rss?hl=en&gl=US&ceid=US:en",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.skynews.com/feeds/rss/world.xml",
        "https://www.theguardian.com/world/rss",
        "https://feeds.reuters.com/reuters/topNews",
    ],
    "ar": [
        "https://news.google.com/rss?hl=ar&gl=SA&ceid=SA:ar",
        "https://news.google.com/rss?hl=ar&gl=LB&ceid=LB:ar",
        "https://www.aljazeera.net/xml/rss/all.xml",
        "https://www.bbc.com/arabic/rss.xml",
        "https://www.skynewsarabia.com/rss.xml",
        "https://arabic.rt.com/rss/",
    ],
}


def _parse_rss_xml(raw: str) -> list[dict]:
    """Parse RSS/Atom XML into article dicts."""
    articles: list[dict] = []
    try:
        raw_clean = raw.strip().lstrip("\ufeff")
        # Strip XML declaration if malformed
        raw_clean = re.sub(r"^<\?xml[^?]*\?>", "", raw_clean).strip()
        root = ET.fromstring(raw_clean)
        items = root.findall(".//item")[:10]
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")[:10]
        for item in items:
            def _t(tag: str, ns: str = "") -> str:
                el = item.find(f"{{{ns}}}{tag}" if ns else tag)
                if el is None:
                    return ""
                txt = (el.text or el.get("href", "")).strip()
                return html_mod.unescape(txt)
            title = _t("title")
            if not title or title.lower() in ("", "[removed]"):
                continue
            link = _t("link")
            if not link:
                link_el = item.find("link")
                if link_el is not None:
                    link = (link_el.tail or "").strip() or link_el.get("href", "")
            desc = _t("description") or _t("summary", "http://www.w3.org/2005/Atom")
            # Remove HTML tags from description
            desc = re.sub(r"<[^>]+>", "", desc)[:300]
            articles.append({
                "title":        title[:150],
                "description":  desc,
                "url":          link,
                "source":       _t("source") or "RSS",
                "published_at": _t("pubDate") or _t("updated", "http://www.w3.org/2005/Atom"),
            })
    except Exception as exc:
        logger.debug(f"RSS parse error: {exc}")
    return articles


class OmegaNews:
    """News aggregation: NewsAPI → GNews → Google News RSS → fallback RSS."""

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

        result = None
        # Tier 1 — keyed APIs
        if quota.has_quota("newsapi"):
            result = await self._fetch_newsapi(category, country)
            if result and not result.get("error"):
                quota.use_quota("newsapi")
        if (not result or result.get("error")) and quota.has_quota("gnews"):
            result = await self._fetch_gnews(category, lang)
            if result and not result.get("error"):
                quota.use_quota("gnews")
        # Tier 2 — Google News RSS (free, no key, cloud-friendly)
        if not result or result.get("error"):
            result = await self._fetch_google_news_rss(lang)
        # Tier 3 — fallback RSS feeds
        if not result or result.get("error"):
            result = await self._fetch_rss(lang)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["news"])

        return result or {"articles": [], "error": True}

    async def search_news(self, query: str, lang: str = "en") -> dict[str, Any]:
        """Search news by keyword — prefers last 24h, falls back to 72h."""
        cache_key = f"news:search:{query}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)

        if settings.newsapi_key:
            # Try 24h window first, widen to 72h if empty
            for hours in (24, 72):
                from_dt = (now - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
                try:
                    data = await self._newsapi.get(
                        "/everything",
                        params={
                            "apiKey": settings.newsapi_key,
                            "q": query,
                            "language": lang,
                            "pageSize": 10,
                            "sortBy": "publishedAt",
                            "from": from_dt,
                        },
                    )
                    if data and data.get("status") == "ok":
                        articles = self._parse_newsapi_articles(data.get("articles", []))
                        if articles or hours == 72:
                            result = {"articles": articles, "query": query,
                                      "error": False, "window_hours": hours}
                            await cache.set(cache_key, result, ttl=CACHE_TTL["news"])
                            return result
                except Exception as exc:
                    logger.debug(f"NewsAPI search error ({hours}h): {exc}")
                    break

        # Google News RSS search (no API key needed)
        gn_lang = "ar" if lang == "ar" else "en"
        gn_region = "SA" if lang == "ar" else "US"
        gn_ceid = f"{gn_region}:{gn_lang}"
        gn_url = f"https://news.google.com/rss/search?q={query}&hl={gn_lang}&gl={gn_region}&ceid={gn_ceid}"
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=_HEADERS) as client:
                r = await client.get(gn_url)
                if r.status_code == 200:
                    articles = _parse_rss_xml(r.text)
                    if articles:
                        result = {"articles": articles[:10], "query": query,
                                  "error": False, "window_hours": 72, "source": "Google News"}
                        await cache.set(cache_key, result, ttl=CACHE_TTL["news"])
                        return result
        except Exception as exc:
            logger.debug(f"Google News search error: {exc}")

        return {"articles": [], "error": True}

    async def _fetch_newsapi(self, category: str, country: str) -> Optional[dict]:
        """Fetch from NewsAPI — top headlines within the last 24 h."""
        if not settings.newsapi_key:
            return None
        from datetime import datetime, timedelta, timezone
        from_dt = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            data = await self._newsapi.get(
                "/top-headlines",
                params={
                    "apiKey": settings.newsapi_key,
                    "category": category,
                    "country": country,
                    "pageSize": 20,
                    "from": from_dt,
                },
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

    async def _fetch_google_news_rss(self, lang: str) -> Optional[dict]:
        """Google News RSS — free, no key, works from cloud IPs."""
        gn_lang = "ar" if lang == "ar" else "en"
        region  = "SA" if lang == "ar" else "US"
        url = f"https://news.google.com/rss?hl={gn_lang}&gl={region}&ceid={region}:{gn_lang}"
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=_HEADERS) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    articles = _parse_rss_xml(r.text)
                    if articles:
                        logger.info(f"Google News RSS OK → {len(articles)} articles")
                        return {"articles": articles[:10], "source": "Google News", "error": False}
        except Exception as exc:
            logger.debug(f"Google News RSS error: {exc}")
        return None

    async def _fetch_rss(self, lang: str) -> Optional[dict]:
        """Fetch from RSS feeds using browser-like headers to bypass CDN blocks."""
        urls = _RSS_FEEDS.get(lang, _RSS_FEEDS["en"])
        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True,
            headers=_HEADERS,
        ) as client:
            for url in urls:
                try:
                    r = await client.get(url)
                    if r.status_code != 200 or len(r.text) < 300:
                        logger.debug(f"RSS {url} → HTTP {r.status_code}")
                        continue
                    articles = _parse_rss_xml(r.text)
                    if articles:
                        logger.info(f"RSS OK: {url} → {len(articles)} articles")
                        return {"articles": articles[:10], "source": "RSS", "error": False}
                except Exception as exc:
                    logger.debug(f"RSS error {url}: {exc}")
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
