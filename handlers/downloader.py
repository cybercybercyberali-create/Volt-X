import logging
import os
import asyncio
import tempfile
import time
import shutil
from pathlib import Path
from typing import Optional

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile,
)
from aiogram.filters import Command

from config import t

logger = logging.getLogger(__name__)
router = Router(name="downloader")

MAX_BYTES = 50 * 1024 * 1024  # 50 MB Telegram bot limit

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
            [InlineKeyboardButton(text="🎵 صوت MP3", callback_data="dl:mp3")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📹 High Quality", callback_data="dl:high"),
            InlineKeyboardButton(text="📱 Low Quality", callback_data="dl:low"),
        ],
        [InlineKeyboardButton(text="🎵 Audio MP3", callback_data="dl:mp3")],
    ])


def _build_ydl_opts(fmt: str, tmp_dir: str) -> dict:
    base = {
        "outtmpl": f"{tmp_dir}/%(title).80s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": MAX_BYTES,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }
    if fmt == "mp3":
        base.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    elif fmt == "low":
        base["format"] = "bestvideo[height<=480]+bestaudio/best[height<=480]/worst[ext=mp4]/worst"
    else:
        base["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best[ext=mp4]/best"
    return base


def _find_output(tmp_dir: str) -> Optional[str]:
    """Return the largest file in tmp_dir — yt-dlp may change the extension."""
    candidates = sorted(Path(tmp_dir).iterdir(), key=lambda p: p.stat().st_size, reverse=True)
    return str(candidates[0]) if candidates else None


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
    prompt = "🎬 اختر صيغة التحميل:" if lang == "ar" else "🎬 Choose download format:"
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
        "⏳ جارٍ التحميل..." if lang == "ar" else "⏳ Downloading..."
    )
    tmp_dir = tempfile.mkdtemp(prefix="vx_dl_")

    try:
        import yt_dlp

        ydl_opts = _build_ydl_opts(fmt, tmp_dir)
        loop = asyncio.get_event_loop()
        last_update = [time.monotonic()]

        def _progress_hook(d: dict) -> None:
            if d.get("status") != "downloading":
                return
            now = time.monotonic()
            if now - last_update[0] < 4:
                return
            last_update[0] = now
            pct = d.get("_percent_str", "?%").strip()
            spd = d.get("_speed_str", "").strip()
            text = (
                f"⏳ جارٍ التحميل: {pct}  {spd}"
                if lang == "ar"
                else f"⏳ Downloading: {pct}  {spd}"
            )
            asyncio.run_coroutine_threadsafe(
                status_msg.edit_text(text), loop
            )

        ydl_opts["progress_hooks"] = [_progress_hook]

        def _do_download() -> None:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, _do_download)

        found = _find_output(tmp_dir)
        if not found:
            raise FileNotFoundError("yt-dlp produced no output file")

        size = os.path.getsize(found)
        if size > MAX_BYTES:
            mb = size // (1024 * 1024)
            over = (
                f"⚠️ حجم الملف {mb}MB يتجاوز الحد (50MB). جرّب صيغة MP3."
                if lang == "ar"
                else f"⚠️ File is {mb}MB — exceeds the 50MB limit. Try Audio MP3."
            )
            await status_msg.edit_text(over)
            return

        await status_msg.edit_text("📤 جارٍ الإرسال..." if lang == "ar" else "📤 Sending...")
        file_obj = FSInputFile(found)
        if fmt == "mp3":
            await callback.message.answer_audio(file_obj)
        else:
            try:
                await callback.message.answer_video(file_obj)
            except Exception:
                await callback.message.answer_document(file_obj)

        await status_msg.delete()
        _pending_urls.pop(user_id, None)

    except Exception as exc:
        logger.error(f"Download error for {url!r}: {exc}", exc_info=True)
        err = (
            f"❌ فشل التحميل: {type(exc).__name__}"
            if lang == "ar"
            else f"❌ Download failed: {type(exc).__name__}"
        )
        try:
            await status_msg.edit_text(err)
        except Exception:
            pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def register_downloader_handlers(dp) -> None:
    dp.include_router(router)
