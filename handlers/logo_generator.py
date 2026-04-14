import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import t

from services.omega_image import omega_image

logger = logging.getLogger(__name__)
router = Router(name="logo")


@router.message(Command("logo"))
async def cmd_logo(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/logo", "").strip() if message.text else ""
    if not query:
        await message.answer(
            t("logo_intro", lang),
            parse_mode="Markdown"
        )
        return

    await message.answer(t("logo_generating", lang))
    try:
        from services.omega_query_engine import query_engine

        lang_instruction = f"Respond in {lang} language." if lang != "en" else ""
        prompt = f"Create a professional logo concept description for a company called '{query}'. Describe the visual elements, colors, and style. {lang_instruction}"
        responses = await query_engine.query_all(prompt, system_prompt="You are a professional graphic designer.")
        description = responses[0]["text"] if responses else f"Modern logo for {query}"

        urls = await omega_image.search_logos(query)
        text = f"🎨 **{query}**\n\n"
        text += f"📝 {description[:400]}\n\n"
        for i, url in enumerate(urls, 1):
            text += f"{i}. [#{i}]({url})\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Logo error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_logo_handlers(dp) -> None:
    dp.include_router(router)
