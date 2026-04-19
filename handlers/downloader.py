import logging
import asyncio
import re
from typing import Optional

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command

from config import t

logger = logging.getLogger(__name__)
router = Router(name="downloader")

_SUPPORTED_DOMAINS = (
    "youtube.com", "youtu.be",
    "tiktok.com", "vm.tiktok.com",
    "instagram.com", "instagr.am",
    "twitter.com", "x.com",
    "facebook.com", "fb.watch",
    "vimeo.com",
    "reddit.com", "v.redd.it",
)

# user_id → URL awaiting format selection
_pending_urls: dict[int, str] = {}


def _is_media_url(text: str) -> bool:
    text = (text or "").strip().lower()
    return text.startswith("http") and any(d in text for d in _SUPPORTED_DOMAINS)


def _format_kb(lang: str) -> InlineKeyboardMarkup:
    if lang == "ar":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📹 جودة عالية", callback_data="dl:high"),
                InlineKeyboardButton(text="📱 جودة منخفضة", callback_data="dl:low"),
            ],
            [InlineKeyboardButton(text="🎵 صوت فقط", callback_data="dl:mp3")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📹 High Quality", callback_data="dl:high"),
            InlineKeyboardButton(text="📱 Low Quality", callback_data="dl:low"),
        ],
        [InlineKeyboardButton(text="🎵 Audio Only", callback_data="dl:mp3")],
    ])


def _fmt_duration(secs: int) -> str:
    if not secs:
        return ""
    m, s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _extract_direct_url(url: str, fmt: str) -> dict:
    """Use yt-dlp info extraction (no download) to get the direct CDN stream URL."""
    import yt_dlp

    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }
    if fmt == "mp3":
        opts["format"] = "bestaudio/best"
    elif fmt == "low":
        opts["format"] = "bestvideo[height<=480]+bestaudio/best[height<=480]/worst"
    else:
        opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # Merged formats (video+audio) are re-muxed; direct URL lives on the format entry
    direct = info.get("url", "")
    if not direct:
        fmts = info.get("formats") or []
        if fmts:
            direct = fmts[-1].get("url", "")

    return {
        "title": info.get("title", ""),
        "duration": info.get("duration", 0),
        "direct_url": direct,
        "ext": info.get("ext", "mp4"),
        "is_youtube": "youtube" in url or "youtu.be" in url,
    }


@router.message(Command("download"))
async def cmd_download(message: Message, lang: str = "en") -> None:
    hint = (
        "📥 أرسل رابطاً من يوتيوب أو تيك توك أو إنستغرام..."
        if lang == "ar"
        else "📥 Send a YouTube, TikTok, or Instagram link to download it."
    )
    await message.answer(hint)


@router.message(F.text.func(_is_media_url))
async def handle_media_url(message: Message, lang: str = "en") -> None:
    url = (message.text or "").strip()
    _pending_urls[message.from_user.id] = url
    prompt = "🎬 اختر الجودة:" if lang == "ar" else "🎬 Choose quality:"
    await message.answer(prompt, reply_markup=_format_kb(lang))


@router.callback_query(lambda c: c.data and c.data.startswith("dl:"))
async def handle_dl_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    user_id = callback.from_user.id
    url = _pending_urls.get(user_id)
    if not url:
        no_url = (
            "❌ لم يُعثر على رابط. أرسل الرابط مجدداً."
            if lang == "ar"
            else "❌ No URL found. Please send the link again."
        )
        await callback.message.answer(no_url)
        return

    fmt = callback.data.split(":")[1]  # high / low / mp3
    status_msg = await callback.message.answer(
        "⏳ جارٍ استخراج الرابط..." if lang == "ar" else "⏳ Extracting link..."
    )

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _extract_direct_url, url, fmt)

        direct = data["direct_url"]
        title = data["title"] or "—"
        dur = _fmt_duration(data["duration"])
        is_yt = data["is_youtube"]

        if direct:
            dur_line = f"\n⏱ {dur}" if dur else ""
            if lang == "ar":
                text = (
                    f"🎬 *{title}*{dur_line}\n\n"
                    f"🔗 [افتح / حمّل الرابط المباشر]({direct})\n\n"
                    f"_⚠️ الرابط مؤقت — افتحه في المتصفح للتحميل_"
                )
            else:
                text = (
                    f"🎬 *{title}*{dur_line}\n\n"
                    f"🔗 [Open / Download Direct Link]({direct})\n\n"
                    f"_⚠️ Link is temporary — open in browser to save_"
                )
        else:
            # Extraction succeeded but no direct URL (common for YouTube merged formats)
            # Fall back to the original URL
            if lang == "ar":
                text = (
                    f"🎬 *{title}*\n\n"
                    f"⚠️ تعذّر استخراج رابط مباشر.\n"
                    f"افتح الرابط الأصلي في متصفحك:\n{url}"
                )
            else:
                text = (
                    f"🎬 *{title}*\n\n"
                    f"⚠️ Could not extract a direct link.\n"
                    f"Open the original link in your browser:\n{url}"
                )

        await status_msg.edit_text(text, parse_mode="Markdown")
        _pending_urls.pop(user_id, None)

    except Exception as exc:
        logger.error(f"URL extraction error for {url!r}: {exc}", exc_info=True)
        # Final fallback: just return the original URL
        if lang == "ar":
            fallback = (
                f"⚠️ تعذّر معالجة الرابط تلقائياً.\n"
                f"يمكنك استخدام الرابط الأصلي مع أداة تحميل خارجية:\n{url}"
            )
        else:
            fallback = (
                f"⚠️ Could not process this link automatically.\n"
                f"Use the original link with an external downloader:\n{url}"
            )
        try:
            await status_msg.edit_text(fallback)
        except Exception:
            pass


def register_downloader_handlers(dp) -> None:
    dp.include_router(router)
