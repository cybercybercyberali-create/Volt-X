"""Web search via Tavily (primary) with Brave Search as fallback.

Used by the AI chat handler to ground model answers on current information
when the query references a specific year, "today", "latest", news, etc.
"""
import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

# Keywords that flag a query as time-sensitive → needs web search
_SEARCH_TRIGGERS = {
    # Arabic — temporal
    "اليوم", "الآن", "الان", "حالياً", "حاليا", "آخر", "اخر", "أحدث", "احدث",
    "هلق", "هاليومين", "هالأيام", "هالايام", "الأسبوع", "الشهر", "السنة",
    "مؤخراً", "مؤخرا", "جديد", "الجديد",
    # Arabic — current-events / news
    "خبر", "أخبار", "اخبار", "حدث", "صار", "جرى", "وقع",
    # English — temporal
    "today", "now", "latest", "current", "recent", "currently", "nowadays",
    "this week", "this month", "this year",
    # English — current-events / news
    "news", "happened", "breaking",
    # Years → anything past training cutoff
    "2024", "2025", "2026", "2027",
    "٢٠٢٤", "٢٠٢٥", "٢٠٢٦", "٢٠٢٧",
}


def needs_web_search(query: str) -> bool:
    """Return True if the query references recent/current information."""
    q = (query or "").lower()
    return any(kw in q for kw in _SEARCH_TRIGGERS)


async def tavily_search(query: str, max_results: int = 5) -> Optional[str]:
    """Call Tavily Search API. Returns formatted plain-text results, or None."""
    key = settings.tavily_api_key
    if not key:
        return None

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": max_results,
                    "include_answer": True,
                    "include_raw_content": False,
                },
            )
            if resp.status_code >= 400:
                logger.warning(f"Tavily HTTP {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
        except Exception as exc:
            logger.warning(f"Tavily error: {exc}")
            return None

    return _format_tavily(data)


def _format_tavily(data: dict) -> Optional[str]:
    lines: list[str] = []
    answer = (data.get("answer") or "").strip()
    if answer:
        lines.append(f"Summary: {answer}")
    for r in data.get("results") or []:
        title = (r.get("title") or "").strip()
        content = (r.get("content") or "").strip()[:250]
        if title or content:
            lines.append(f"- {title}: {content}")
    return "\n".join(lines) if lines else None


async def brave_search(query: str, max_results: int = 5) -> Optional[str]:
    """Fallback: Brave Search API."""
    key = settings.brave_search_key
    if not key:
        return None

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": max_results},
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": key,
                },
            )
            if resp.status_code >= 400:
                logger.warning(f"Brave HTTP {resp.status_code}")
                return None
            data = resp.json()
        except Exception as exc:
            logger.warning(f"Brave error: {exc}")
            return None

    results = (data.get("web") or {}).get("results") or []
    if not results:
        return None
    lines = []
    for r in results[:max_results]:
        title = (r.get("title") or "").strip()
        desc = (r.get("description") or "").strip()[:250]
        lines.append(f"- {title}: {desc}")
    return "\n".join(lines) if lines else None


async def web_search(query: str, max_results: int = 5) -> Optional[str]:
    """Primary entry: try Tavily first, fall back to Brave, then None."""
    result = await tavily_search(query, max_results)
    if result:
        return result
    result = await brave_search(query, max_results)
    return result
