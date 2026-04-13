import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_news import omega_news
from config import t

logger = logging.getLogger(__name__)
router = Router(name="news")


@router.message(Command("news"))
async def cmd_news(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/news", "").strip() if message.text else ""

    await message.answer(t("fetching", lang))
    try:
        if query:
            data = await omega_news.search_news(query)
        else:
            data = await omega_news.get_headlines()

        if data.get("error") or not data.get("articles"):
            await message.answer(t("error", lang))
            return

        text = t("news_headline", lang) + "\n\n"
        for i, article in enumerate(data["articles"][:8], 1):
            text += f"{i}. **{article['title'][:80]}**\n"
            if article.get("source"):
                text += f"   📍 {article['source']}\n"
            if article.get("url"):
                read_label = t("read_more", lang)
                text += f"   🔗 [{read_label}]({article['url']})\n"
            text += "\n"

        await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as exc:
        logger.error(f"News error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_news_handlers(dp) -> None:
    dp.include_router(router)
