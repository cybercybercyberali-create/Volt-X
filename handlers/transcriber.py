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
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.0-flash:generateContent"
)
_SUMMARY_THRESHOLD = 500  # chars


async def _transcribe(audio_path: str) -> str:
    """Send audio file to Groq Whisper; return transcript text."""
    async with httpx.AsyncClient(timeout=120) as client:
        with open(audio_path, "rb") as fh:
            resp = await client.post(
                _GROQ_STT_URL,
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                files={"file": (os.path.basename(audio_path), fh, "audio/ogg")},
                data={"model": _GROQ_MODEL, "response_format": "text"},
            )
        resp.raise_for_status()
        # response_format=text returns plain text, not JSON
        return resp.text.strip()


async def _summarize(text: str, lang: str) -> Optional[str]:
    """Ask Gemini for a 3-point summary. Returns None if key missing or call fails."""
    if not settings.gemini_api_key:
        return None
    prompt = (
        f"لخّص النص التالي في 3 نقاط رئيسية موجزة:\n\n{text}"
        if lang == "ar"
        else f"Summarize the following text in exactly 3 concise bullet points:\n\n{text}"
    )
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{_GEMINI_URL}?key={settings.gemini_api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            resp.raise_for_status()
            data = resp.json()
            parts = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])
            )
            return (parts[0].get("text") or "").strip() or None
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
        return result.returncode == 0 and os.path.exists(output_path)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        logger.warning(f"ffmpeg unavailable: {exc}")
        return False


async def _process(message: Message, file_id: str, ext: str, lang: str) -> None:
    """Download, transcribe, optionally summarize, then clean up."""
    wait_msg = await message.answer(
        "🎙️ جارٍ النسخ..." if lang == "ar" else "🎙️ Transcribing..."
    )
    tmp_dir = tempfile.mkdtemp(prefix="vx_tr_")
    try:
        if not settings.groq_api_key:
            await wait_msg.edit_text(
                "❌ مفتاح Groq غير مُهيَّأ." if lang == "ar"
                else "❌ Groq API key is not configured."
            )
            return

        # ── Download from Telegram ─────────────────────────────────────────
        audio_path = os.path.join(tmp_dir, f"input.{ext}")
        await message.bot.download(file_id, destination=audio_path)

        # ── Extract audio for video types ─────────────────────────────────
        if ext in ("mp4", "webm", "avi", "mov", "mkv"):
            extracted = os.path.join(tmp_dir, "audio.mp3")
            ok = await asyncio.get_event_loop().run_in_executor(
                None, _extract_audio, audio_path, extracted
            )
            if ok:
                audio_path = extracted
            else:
                await wait_msg.edit_text(
                    "⚠️ تعذّر استخراج الصوت. أرسل ملف صوت مباشرةً."
                    if lang == "ar"
                    else "⚠️ Could not extract audio. Please send an audio file directly."
                )
                return

        # ── Transcribe ─────────────────────────────────────────────────────
        text = await _transcribe(audio_path)
        if not text:
            await wait_msg.edit_text(
                "❌ لم يُتعرَّف على أي كلام." if lang == "ar"
                else "❌ No speech detected in the file."
            )
            return

        header = "🎙️ *النص المستخرج:*\n\n" if lang == "ar" else "🎙️ *Transcription:*\n\n"
        # Telegram message limit is 4096 chars; truncate gracefully
        body = text if len(text) <= 3800 else text[:3800] + "…"
        await wait_msg.edit_text(header + body, parse_mode="Markdown")

        # ── Summarize long texts ───────────────────────────────────────────
        if len(text) > _SUMMARY_THRESHOLD:
            await message.answer("⏳ جارٍ التلخيص..." if lang == "ar" else "⏳ Summarizing...")
            summary = await _summarize(text, lang)
            if summary:
                sum_header = "📝 *الملخص:*\n\n" if lang == "ar" else "📝 *Summary:*\n\n"
                await message.answer(sum_header + summary, parse_mode="Markdown")

    except Exception as exc:
        logger.error(f"Transcription error: {exc}", exc_info=True)
        err = (
            f"❌ فشل النسخ: {type(exc).__name__}"
            if lang == "ar"
            else f"❌ Transcription failed: {type(exc).__name__}"
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
        "🎙️ أرسل رسالة صوتية أو مقطع فيديو لتحويله إلى نص."
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
        ext = message.audio.file_name.rsplit(".", 1)[-1].lower() or "mp3"
    await _process(message, message.audio.file_id, ext, lang)


def register_transcriber_handlers(dp) -> None:
    dp.include_router(router)
