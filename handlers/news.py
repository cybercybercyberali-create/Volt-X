import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_news import omega_news
from config import t

logger = logging.getLogger(__name__)
router = Router(name="news")


def _time_ago(ts: str) -> str:
    if not ts:
        return ""
    fmts = [
        "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
    ]
    dt = None
    for fmt in fmts:
        try:
            dt = datetime.strptime(ts, fmt)
            break
        except ValueError:
            continue
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    mins = int(delta.total_seconds() / 60)
    if mins < 60:
        return f"{mins}m"
    hours = mins // 60
    if hours < 24:
        return f"{hours}h"
    return f"{hours // 24}d"


def _card(article: dict, lang: str) -> str:
    rtl = "\u200f" if lang == "ar" else ""
    title = article.get("title", "").strip()
    desc = (article.get("description", "") or "").strip()
    source = (article.get("source", "") or "").strip() or "—"
    url = article.get("url", "")
    ago = _time_ago(article.get("published_at", ""))
    desc_short = desc[:200] + ("..." if len(desc) > 200 else "")
    read_lbl = "📖 اقرأ المزيد" if lang == "ar" else "📖 Read more"
    parts = [f"{rtl}📰 *{title}*", ""]
    if desc_short:
        parts.append(f"{rtl}{desc_short}")
        parts.append("")
    meta = f"{rtl}📍 {source}"
    if ago:
        meta += f"  |  🕐 {ago}"
    parts.append(meta)
    if url:
        parts.append(f"{rtl}[{read_lbl}]({url})")
    return "\n".join(parts)


@router.message(Command("news"))
async def cmd_news(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/news", "", 1).strip() if message.text else ""
    try:
        if query:
            data = await omega_news.search_news(query, lang=lang)
        else:
            data = await omega_news.get_headlines(lang=lang)

        if data.get("error") or not data.get("articles"):
            await message.answer(t("not_found", lang))
            return

        for article in data["articles"][:5]:
            card = _card(article, lang)
            if not card.strip():
                continue
            try:
                await message.answer(card, parse_mode="Markdown", disable_web_page_preview=False)
            except Exception as exc:
                logger.warning(f"News card send error: {exc}")

    except Exception as exc:
        logger.error(f"News error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_news_handlers(dp) -> None:
    dp.include_router(router)
