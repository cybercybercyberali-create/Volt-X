import logging
import os
import asyncio
import tempfile
import shutil
import subprocess
from typing import Optional

import httpx
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import t, settings

logger = logging.getLogger(__name__)
router = Router(name="transcriber")

_GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
_GROQ_MODEL = "whisper-large-v3"
_AUDIO_MIME: dict[str, str] = {
    "ogg": "audio/ogg", "oga": "audio/ogg", "opus": "audio/ogg",
    "mp3": "audio/mpeg", "mpga": "audio/mpeg",
    "m4a": "audio/mp4", "mp4": "audio/mp4",
    "wav": "audio/wav", "flac": "audio/flac",
    "webm": "audio/webm", "aac": "audio/aac",
}
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.0-flash:generateContent"
)
_SUMMARY_THRESHOLD = 500  # chars


async def _transcribe(audio_path: str, api_key: str) -> str:
    """Send audio file to Groq Whisper; return transcript text."""
    ext_lower = os.path.splitext(audio_path)[1].lstrip(".").lower()
    mime = _AUDIO_MIME.get(ext_lower, "audio/mpeg")
    async with httpx.AsyncClient(timeout=120) as client:
        with open(audio_path, "rb") as fh:
            resp = await client.post(
                _GROQ_STT_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": (os.path.basename(audio_path), fh, mime)},
                data={"model": _GROQ_MODEL, "response_format": "text"},
            )
    # Groq returns 200 with plain text for success, 4xx for errors
    if resp.status_code >= 400:
        err_msg = ""
        try:
            err_msg = resp.json().get("error", {}).get("message", "")
        except Exception:
            err_msg = resp.text[:200]
        raise RuntimeError(f"Groq API error {resp.status_code}: {err_msg}")
    return resp.text.strip()


async def _summarize(text: str, lang: str) -> Optional[str]:
    """Ask Gemini for a 3-point summary. Returns None if key missing or call fails."""
    if not settings.gemini_api_key:
        return None
    prompt = (
        f"لخّص النص التالي في 3 نقاط رئيسية موجزة:\n\n{text[:4000]}"
        if lang == "ar"
        else f"Summarize the following text in exactly 3 concise bullet points:\n\n{text[:4000]}"
    )
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{_GEMINI_URL}?key={settings.gemini_api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates") or []
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts") or []
            if not parts:
                return None
            result = (parts[0].get("text") or "").strip()
            return result or None
    except Exception as exc:
        logger.warning(f"Gemini summary failed: {exc}")
        return None


def _extract_audio(input_path: str, output_path: str) -> bool:
    """Extract audio from video using ffmpeg. Returns True on success."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", input_path,
                "-vn", "-ar", "16000", "-ac", "1", "-ab", "128k",
                "-f", "mp3", output_path, "-y",
            ],
            capture_output=True,
            timeout=120,
        )
        # Verify the output file exists and has non-zero size
        return (
            result.returncode == 0
            and os.path.exists(output_path)
            and os.path.getsize(output_path) > 0
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        logger.warning(f"ffmpeg unavailable: {exc}")
        return False


async def _process(message: Message, file_id: str, ext: str, lang: str) -> None:
    """Download, transcribe, optionally summarize, then clean up."""
    # Check API key before doing anything expensive
    if not settings.groq_api_key:
        await message.answer(
            "❌ خدمة النسخ غير مفعّلة حالياً." if lang == "ar"
            else "❌ Transcription service is not configured."
        )
        return

    wait_msg = await message.answer(
        "🎙️ جارٍ تحميل الملف..." if lang == "ar" else "🎙️ Downloading file..."
    )
    tmp_dir = tempfile.mkdtemp(prefix="vx_tr_")
    try:
        # ── Download from Telegram ─────────────────────────────────────────
        audio_path = os.path.join(tmp_dir, f"input.{ext}")
        await message.bot.download(file_id, destination=audio_path)

        # Verify download succeeded
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            await wait_msg.edit_text(
                "❌ فشل تحميل الملف." if lang == "ar"
                else "❌ Failed to download the file."
            )
            return

        # ── Extract audio for video types ─────────────────────────────────
        if ext in ("mp4", "webm", "avi", "mov", "mkv"):
            await wait_msg.edit_text(
                "🔄 جارٍ استخراج الصوت..." if lang == "ar"
                else "🔄 Extracting audio..."
            )
            extracted = os.path.join(tmp_dir, "audio.mp3")
            ok = await asyncio.get_event_loop().run_in_executor(
                None, _extract_audio, audio_path, extracted
            )
            if ok:
                audio_path = extracted
            else:
                await wait_msg.edit_text(
                    "⚠️ تعذّر استخراج الصوت. تأكد أن الفيديو يحتوي على مسار صوتي."
                    if lang == "ar"
                    else "⚠️ Could not extract audio. Make sure the video has an audio track."
                )
                return

        # ── Transcribe ─────────────────────────────────────────────────────
        await wait_msg.edit_text(
            "🎙️ جارٍ النسخ..." if lang == "ar" else "🎙️ Transcribing..."
        )
        text = await _transcribe(audio_path, settings.groq_api_key)

        if not text.strip():
            await wait_msg.edit_text(
                "❌ لم يُتعرَّف على أي كلام في الملف." if lang == "ar"
                else "❌ No speech detected in the file."
            )
            return

        header = "🎙️ *النص المستخرج:*\n\n" if lang == "ar" else "🎙️ *Transcription:*\n\n"
        # Telegram message limit is 4096 chars; truncate at a safe boundary
        body = text if len(text) <= 3800 else text[:3797] + "…"

        try:
            await wait_msg.edit_text(header + body, parse_mode="Markdown")
        except Exception:
            # Fallback: send as plain text if transcript contains Markdown chars
            await wait_msg.edit_text("🎙️ Transcription:\n\n" + body)

        # ── Summarize long texts ───────────────────────────────────────────
        if len(text) > _SUMMARY_THRESHOLD:
            sum_status = await message.answer(
                "⏳ جارٍ التلخيص..." if lang == "ar" else "⏳ Summarizing..."
            )
            summary = await _summarize(text, lang)
            if summary:
                sum_header = "📝 *الملخص:*\n\n" if lang == "ar" else "📝 *Summary:*\n\n"
                try:
                    await sum_status.edit_text(sum_header + summary, parse_mode="Markdown")
                except Exception:
                    await sum_status.edit_text("📝 Summary:\n\n" + summary)
            else:
                try:
                    await sum_status.delete()
                except Exception:
                    pass

    except Exception as exc:
        logger.error(f"Transcription error: {exc}", exc_info=True)
        err = (
            "❌ فشل النسخ. تأكد من أن الملف يحتوي على صوت واضح وحاول مجدداً."
            if lang == "ar"
            else "❌ Transcription failed. Make sure the file has clear audio and try again."
        )
        try:
            await wait_msg.edit_text(err)
        except Exception:
            pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── Command handler ────────────────────────────────────────────────────────────

@router.message(Command("transcribe"))
async def cmd_transcribe(message: Message, lang: str = "en") -> None:
    hint = (
        "🎙️ أرسل رسالة صوتية أو مقطع فيديو أو ملف صوتي لتحويله إلى نص."
        if lang == "ar"
        else "🎙️ Send a voice message, video, or audio file to transcribe it."
    )
    await message.answer(hint)


# ── Media type handlers ────────────────────────────────────────────────────────

@router.message(F.voice)
async def handle_voice(message: Message, lang: str = "en") -> None:
    await _process(message, message.voice.file_id, "ogg", lang)


@router.message(F.video_note)
async def handle_video_note(message: Message, lang: str = "en") -> None:
    await _process(message, message.video_note.file_id, "mp4", lang)


@router.message(F.video)
async def handle_video(message: Message, lang: str = "en") -> None:
    await _process(message, message.video.file_id, "mp4", lang)


@router.message(F.audio)
async def handle_audio_file(message: Message, lang: str = "en") -> None:
    ext = "mp3"
    if message.audio.file_name:
        parts = message.audio.file_name.rsplit(".", 1)
        if len(parts) == 2 and parts[1]:
            ext = parts[1].lower()
    await _process(message, message.audio.file_id, ext, lang)


def register_transcriber_handlers(dp) -> None:
    dp.include_router(router)
