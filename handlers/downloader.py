import logging
import asyncio
from typing import Optional

import httpx
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
_YT_DOMAINS = ("youtube.com", "youtu.be")
_TT_DOMAINS = ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com")

# user_id → URL awaiting format selection
_pending_urls: dict[int, str] = {}


def _is_media_url(text: str) -> bool:
    text = (text or "").strip().lower()
    return text.startswith("http") and any(d in text for d in _SUPPORTED_DOMAINS)


def _is_youtube(url: str) -> bool:
    return any(d in url.lower() for d in _YT_DOMAINS)


def _is_tiktok(url: str) -> bool:
    return any(d in url.lower() for d in _TT_DOMAINS)


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


async def _tikwm_get_url(url: str, fmt: str) -> Optional[str]:
    """TikWM API — returns tikwm.com-hosted URLs, not IP-bound TikTok CDN."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://www.tikwm.com/api/",
            params={"url": url, "hd": "1"},
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if resp.status_code >= 400:
            logger.warning(f"TikWM HTTP {resp.status_code}")
            return None
        data = resp.json()

    if data.get("code") != 0:
        logger.warning(f"TikWM error: {data.get('msg')}")
        return None

    d = data.get("data", {})
    if fmt == "mp3":
        return d.get("music")
    if fmt == "low":
        return d.get("play")
    return d.get("hdplay") or d.get("play")


async def _cobalt_get_url(url: str, fmt: str) -> Optional[str]:
    """Get direct download link from cobalt.tools."""
    body = {
        "url": url,
        "videoQuality": "1080" if fmt == "high" else "480",
        "downloadMode": "audio" if fmt == "mp3" else "auto",
        "audioFormat": "mp3",
        "alwaysProxy": True,
        "filenameStyle": "basic",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://api.cobalt.tools/",
            json=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        if resp.status_code >= 400:
            logger.warning(f"Cobalt HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        data = resp.json()

    status = data.get("status")
    if status in ("redirect", "tunnel", "stream", "local-processing"):
        return data.get("url")
    if status == "picker":
        items = data.get("picker") or []
        return items[0].get("url") if items else None
    if status == "error":
        err = (data.get("error") or {}).get("code", "unknown")
        logger.warning(f"Cobalt error for {url!r}: {err}")
    return None


def _extract_direct_url(url: str, fmt: str) -> dict:
    """yt-dlp info extraction (no download) — fallback."""
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

    direct = info.get("url", "")
    if not direct:
        fmts = info.get("formats") or []
        if fmts:
            direct = fmts[-1].get("url", "")

    return {
        "title": info.get("title", ""),
        "duration": info.get("duration", 0),
        "direct_url": direct,
    }


def _build_link_reply(title: str, dur: str, direct: str, lang: str) -> str:
    title_line = f"🎬 *{title}*\n" if title else ""
    dur_line = f"⏱ {dur}\n" if dur else ""
    head = title_line + dur_line
    if head:
        head += "\n"
    if lang == "ar":
        return (
            f"{head}"
            f"🔗 [افتح / حمّل الرابط المباشر]({direct})\n\n"
            f"_⚠️ الرابط مؤقت — افتحه في المتصفح للتحميل_"
        )
    return (
        f"{head}"
        f"🔗 [Open / Download Direct Link]({direct})\n\n"
        f"_⚠️ Link is temporary — open in browser to save_"
    )


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
        await callback.message.answer(
            "❌ لم يُعثر على رابط. أرسل الرابط مجدداً."
            if lang == "ar"
            else "❌ No URL found. Please send the link again."
        )
        return

    fmt = callback.data.split(":")[1]  # high / low / mp3
    status_msg = await callback.message.answer(
        "⏳ جارٍ استخراج الرابط..." if lang == "ar" else "⏳ Extracting link..."
    )

    try:
        direct = None
        title = ""
        dur = ""

        # ── 1. TikTok → TikWM (returns tikwm.com URLs, never IP-bound) ─────
        if _is_tiktok(url):
            try:
                direct = await _tikwm_get_url(url, fmt)
            except Exception as exc:
                logger.warning(f"TikWM failed for {url!r}: {exc}")

        # ── 2. cobalt.tools for YouTube / Instagram / others ─────────────
        if not direct:
            try:
                direct = await _cobalt_get_url(url, fmt)
            except Exception as exc:
                logger.warning(f"Cobalt failed for {url!r}: {exc}")

        if direct:
            text = _build_link_reply("", "", direct, lang)
        else:
            # ── 3. Fallback: yt-dlp ───────────────────────────────────────
            try:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, _extract_direct_url, url, fmt)
                direct = data["direct_url"]
                title = data["title"] or "—"
                dur = _fmt_duration(data["duration"])
            except Exception as exc:
                logger.warning(f"yt-dlp failed for {url!r}: {exc}")
                direct = None

            if direct:
                text = _build_link_reply(title, dur, direct, lang)
            else:
                # ── 4. All failed ─────────────────────────────────────────
                text = (
                    "⚠️ تعذّر معالجة الرابط تلقائياً.\n"
                    "جرّب: @SaveVideo_Bot أو savefrom.net"
                    if lang == "ar"
                    else
                    "⚠️ Could not process this link automatically.\n"
                    "Try: @SaveVideo_Bot or savefrom.net"
                )

        await status_msg.edit_text(text, parse_mode="Markdown")
        _pending_urls.pop(user_id, None)

    except Exception as exc:
        logger.error(f"Downloader error for {url!r}: {exc}", exc_info=True)
        fallback = (
            f"⚠️ تعذّر معالجة الرابط.\nجرّب: @SaveVideo_Bot أو savefrom.net\n{url}"
            if lang == "ar"
            else f"⚠️ Could not process this link.\nTry: @SaveVideo_Bot or savefrom.net\n{url}"
        )
        try:
            await status_msg.edit_text(fallback)
        except Exception:
            pass


def register_downloader_handlers(dp) -> None:
    dp.include_router(router)
