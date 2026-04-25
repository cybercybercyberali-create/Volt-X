import html
import os
import re
import logging
import asyncio
import tempfile
from typing import Optional

import httpx
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile,
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
_YT_ID_RE = re.compile(r'(?:v=|youtu\.be/|/shorts/|embed/)([A-Za-z0-9_-]{11})')

_MAX_TG_BYTES = 50 * 1024 * 1024  # 50 MB Telegram upload limit
_YTDLP_TIMEOUT = 45.0  # seconds for yt-dlp extraction

# user_id → URL awaiting format selection
_pending_urls: dict[int, str] = {}


def _is_media_url(text: str) -> bool:
    text = (text or "").strip().lower()
    return text.startswith("http") and any(d in text for d in _SUPPORTED_DOMAINS)


def _is_youtube(url: str) -> bool:
    return any(d in url.lower() for d in _YT_DOMAINS)


def _is_tiktok(url: str) -> bool:
    return any(d in url.lower() for d in _TT_DOMAINS)


def _extract_yt_id(url: str) -> Optional[str]:
    m = _YT_ID_RE.search(url)
    return m.group(1) if m else None


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


async def _safe_edit(msg, text: str, **kwargs) -> None:
    """Edit a message safely — ignore errors if the message was already deleted."""
    try:
        await msg.edit_text(text, **kwargs)
    except Exception:
        pass


# ─── Cobalt API ────────────────────────────────────────────────────────────────

async def _cobalt_get_link(url: str, fmt: str) -> Optional[dict]:
    """POST to cobalt.tools v10, return {url, filename} or None."""
    body = {
        "url": url,
        "videoQuality": "720" if fmt != "mp3" else "480",
        "downloadMode": "audio" if fmt == "mp3" else "auto",
        "audioFormat": "mp3",
        "filenameStyle": "nerdy",
        "alwaysProxy": True,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.cobalt.tools/",
                json=body,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
    except Exception as exc:
        logger.warning(f"Cobalt request error: {exc}")
        return None

    if resp.status_code >= 400:
        logger.warning(f"Cobalt HTTP {resp.status_code}: {resp.text[:200]}")
        return None

    try:
        data = resp.json()
    except Exception as exc:
        logger.warning(f"Cobalt JSON parse error: {exc}")
        return None

    status = data.get("status")
    if status in ("stream", "tunnel", "redirect", "local-processing"):
        dl_url = data.get("url")
        if not dl_url:
            return None
        return {"url": dl_url, "filename": data.get("filename") or "media"}
    if status == "picker":
        items = data.get("picker") or []
        if items:
            item_url = items[0].get("url")
            return {"url": item_url, "filename": "media"} if item_url else None
    if status == "error":
        err = (data.get("error") or {}).get("code", "unknown")
        logger.warning(f"Cobalt error for {url!r}: {err}")
    return None


# ─── Stream download to /tmp ───────────────────────────────────────────────────

async def _stream_to_tmp(dl_url: str) -> Optional[str]:
    """Download URL to a /tmp file, abort if > 50 MB. Returns path or None."""
    fd, path = tempfile.mkstemp(prefix="voltx_dl_", dir="/tmp")
    os.close(fd)
    written = 0
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(120.0, connect=15.0),
            follow_redirects=True,
        ) as client:
            async with client.stream(
                "GET", dl_url,
                headers={"User-Agent": "Mozilla/5.0"},
            ) as resp:
                if resp.status_code >= 400:
                    os.unlink(path)
                    return None
                # Check Content-Length header early to skip huge files fast
                cl = resp.headers.get("content-length")
                try:
                    if cl and int(cl) > _MAX_TG_BYTES:
                        os.unlink(path)
                        return None
                except (ValueError, TypeError):
                    pass
                with open(path, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=65536):
                        written += len(chunk)
                        if written > _MAX_TG_BYTES:
                            f.close()
                            os.unlink(path)
                            return None
                        f.write(chunk)
        return path
    except Exception as exc:
        logger.warning(f"Stream download error: {exc}")
        try:
            os.unlink(path)
        except OSError:
            pass
        return None


# ─── Send downloaded file via Telegram ────────────────────────────────────────

async def _send_media_file(message: Message, path: str, filename: str, fmt: str) -> None:
    fs = FSInputFile(path, filename=filename)
    if fmt == "mp3":
        await message.answer_audio(audio=fs, title=filename[:64])
    else:
        await message.answer_video(video=fs, supports_streaming=True)


# ─── URL-mode fallbacks ────────────────────────────────────────────────────────

async def _tikwm_get_url(url: str, fmt: str) -> Optional[str]:
    """TikWM API — tikwm.com-hosted URLs, never IP-bound TikTok CDN."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://www.tikwm.com/api/",
                params={"url": url, "hd": "1"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if resp.status_code >= 400:
                return None
            data = resp.json()
    except Exception as exc:
        logger.warning(f"TikWM request error: {exc}")
        return None

    if not isinstance(data, dict) or data.get("code") != 0:
        return None
    d = data.get("data") or {}
    if fmt == "mp3":
        return d.get("music") or None
    if fmt == "low":
        return d.get("play") or None
    return d.get("hdplay") or d.get("play") or None


async def _piped_get_url(url: str, fmt: str) -> Optional[str]:
    """Piped API — YouTube streams proxied, not IP-bound."""
    vid_id = _extract_yt_id(url)
    if not vid_id:
        return None

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://pipedapi.kavin.rocks/streams/{vid_id}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if resp.status_code >= 400:
                return None
            data = resp.json()
    except Exception as exc:
        logger.warning(f"Piped request error: {exc}")
        return None

    if fmt == "mp3":
        streams = sorted(
            data.get("audioStreams") or [],
            key=lambda x: x.get("bitrate", 0), reverse=True,
        )
        return streams[0].get("url") if streams else None

    all_streams = data.get("videoStreams") or []
    streams = [s for s in all_streams if not s.get("videoOnly")] or all_streams

    def _res(s: dict) -> int:
        try:
            return int(str(s.get("quality", "0")).rstrip("p"))
        except (ValueError, AttributeError):
            return 0

    streams.sort(key=_res, reverse=(fmt != "low"))
    return streams[0].get("url") if streams else None


def _extract_direct_url(url: str, fmt: str) -> dict:
    """yt-dlp info extraction (no download) — last-resort fallback."""
    import yt_dlp

    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 15,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }
    if fmt == "mp3":
        opts["format"] = "bestaudio/best"
    elif fmt == "low":
        opts["format"] = "bestvideo[height<=480]+bestaudio/best[height<=480]/worst"
    else:
        opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        return {"title": "", "duration": 0, "direct_url": ""}

    direct = info.get("url", "")
    if not direct:
        fmts = info.get("formats") or []
        if fmts:
            direct = fmts[-1].get("url", "")

    return {
        "title": info.get("title", ""),
        "duration": info.get("duration", 0),
        "direct_url": direct or "",
    }


def _build_link_reply(title: str, dur: str, direct: str, lang: str) -> str:
    safe_title = html.escape(title or "")
    safe_link = html.escape(direct or "")
    title_line = f"🎬 <b>{safe_title}</b>\n" if safe_title else ""
    dur_line = f"⏱ {dur}\n" if dur else ""
    head = title_line + dur_line
    if head:
        head += "\n"
    if lang == "ar":
        return (
            f"{head}"
            f'🔗 <a href="{safe_link}">افتح / حمّل الرابط المباشر</a>\n\n'
            f"<i>⚠️ الرابط مؤقت — افتحه في المتصفح للتحميل</i>"
        )
    return (
        f"{head}"
        f'🔗 <a href="{safe_link}">Open / Download Direct Link</a>\n\n'
        f"<i>⚠️ Link is temporary — open in browser to save</i>"
    )


# ─── Handlers ─────────────────────────────────────────────────────────────────

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
        "⏳ جارٍ معالجة الرابط..." if lang == "ar" else "⏳ Processing your link..."
    )
    _pending_urls.pop(user_id, None)

    tmp_path: Optional[str] = None
    try:
        # ── 1. TikWM (for TikTok) or Cobalt → download → send file ───────────
        cobalt_link = None
        if _is_tiktok(url):
            try:
                tik_url = await _tikwm_get_url(url, fmt)
                if tik_url:
                    cobalt_link = {"url": tik_url, "filename": "tiktok_media"}
            except Exception as exc:
                logger.warning(f"TikWM failed: {exc}")

        if not cobalt_link:
            try:
                cobalt_link = await _cobalt_get_link(url, fmt)
            except Exception as exc:
                logger.warning(f"Cobalt failed: {exc}")

        if cobalt_link and cobalt_link.get("url"):
            dl_url = cobalt_link["url"]
            filename = cobalt_link.get("filename") or "media"

            await _safe_edit(status_msg, "⬇️ جارٍ تحميل الملف..." if lang == "ar" else "⬇️ Downloading file...")
            tmp_path = await _stream_to_tmp(dl_url)

            if tmp_path:
                await _safe_edit(status_msg, "📤 جارٍ الإرسال..." if lang == "ar" else "📤 Sending...")
                await _send_media_file(callback.message, tmp_path, filename, fmt)
                try:
                    await status_msg.delete()
                except Exception:
                    pass
                return
            else:
                # File > 50 MB — send direct link instead
                text = _build_link_reply("", "", dl_url, lang)
                await _safe_edit(status_msg, text, parse_mode="HTML")
                return

        # ── 2. YouTube → Piped URL fallback ──────────────────────────────────
        if _is_youtube(url):
            try:
                piped_url = await _piped_get_url(url, fmt)
                if piped_url:
                    text = _build_link_reply("", "", piped_url, lang)
                    await _safe_edit(status_msg, text, parse_mode="HTML")
                    return
            except Exception as exc:
                logger.warning(f"Piped failed: {exc}")

        # ── 3. yt-dlp last-resort URL extraction (with hard timeout) ─────────
        try:
            loop = asyncio.get_event_loop()
            data = await asyncio.wait_for(
                loop.run_in_executor(None, _extract_direct_url, url, fmt),
                timeout=_YTDLP_TIMEOUT,
            )
            direct = data.get("direct_url", "")
            if direct:
                title = data.get("title") or ""
                dur = _fmt_duration(data.get("duration") or 0)
                text = _build_link_reply(title, dur, direct, lang)
                await _safe_edit(status_msg, text, parse_mode="HTML")
                return
        except asyncio.TimeoutError:
            logger.warning(f"yt-dlp timed out for {url!r}")
        except Exception as exc:
            logger.warning(f"yt-dlp failed: {exc}")

        # ── 4. All methods failed ─────────────────────────────────────────────
        await _safe_edit(
            status_msg,
            "⚠️ تعذّر معالجة الرابط حالياً. جرّب لاحقاً."
            if lang == "ar"
            else "⚠️ Unable to process this link at the moment. Please try again later.",
        )

    except Exception as exc:
        logger.error(f"Downloader error for {url!r}: {exc}", exc_info=True)
        await _safe_edit(
            status_msg,
            "⚠️ حدث خطأ غير متوقع. جرّب لاحقاً."
            if lang == "ar"
            else "⚠️ An unexpected error occurred. Please try again later.",
        )
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def register_downloader_handlers(dp) -> None:
    dp.include_router(router)
