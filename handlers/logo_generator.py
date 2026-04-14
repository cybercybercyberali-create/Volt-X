import logging
import asyncio
import urllib.parse
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import t

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
        # Use Pollinations.ai for real AI image generation (free, no auth needed)
        styles = [
            f"professional minimalist logo for {query}, flat design, vector style, white background",
            f"modern creative logo {query}, gradient colors, clean typography, transparent background",
            f"corporate logo design {query}, geometric shapes, blue and gold, professional",
        ]

        sent = False
        for style_prompt in styles:
            try:
                encoded = urllib.parse.quote(style_prompt)
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true"
                caption = f"🎨 **{query}**\n\n_AI-generated logo concept_"
                await message.answer_photo(img_url, caption=caption, parse_mode="Markdown")
                sent = True
                break
            except Exception:
                continue

        if not sent:
            # Fallback: send link
            encoded = urllib.parse.quote(f"professional logo {query} white background flat design")
            img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512"
            await message.answer(
                f"🎨 **{query}**\n\n[View AI logo]({img_url})",
                parse_mode="Markdown"
            )
    except Exception as exc:
        logger.error(f"Logo error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_logo_handlers(dp) -> None:
    dp.include_router(router)
