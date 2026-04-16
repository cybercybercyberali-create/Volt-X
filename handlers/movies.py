import logging
import re

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_movies import omega_movies
from config import t

logger = logging.getLogger(__name__)
router = Router(name="movies")

_YEAR_RE = re.compile(r"\b(19[0-9]{2}|20[0-9]{2})\b")


def _extract_year(text: str) -> tuple:
    m = _YEAR_RE.search(text)
    if m:
        return _YEAR_RE.sub("", text).strip(), int(m.group(1))
    return text, None


def _item_year(item: dict) -> int | None:
    rd = item.get("release_date", "")
    try:
        return int(rd[:4]) if rd else None
    except ValueError:
        return None


def _caption(item: dict) -> str:
    title = item.get("title", "")
    rd = item.get("release_date", "")
    year = rd[:4] if rd else "?"
    vote = item.get("vote_average", 0)
    genres = item.get("genres", [])
    genres_str = ", ".join(genres) if isinstance(genres, list) and genres else "—"
    overview = item.get("overview", "")
    preview = overview[:180] + ("..." if len(overview) > 180 else "")
    return (
        f"🎬 *{title}* ({year})\n"
        f"⭐ {vote}/10  |  🎭 {genres_str}\n"
        f"📅 {rd}\n"
        f"📝 {preview}"
    )


async def _send_card(msg: Message, item: dict, lang: str) -> None:
    poster = item.get("poster", "")
    cap = _caption(item)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("btn_details", lang),
            callback_data=f"mv:detail:{item['id']}:{item.get('media_type','movie')}",
        )
    ]])
    try:
        if poster:
            await msg.answer_photo(photo=poster, caption=cap, parse_mode="Markdown", reply_markup=kb)
            return
    except Exception:
        pass
    await msg.answer(cap, parse_mode="Markdown", reply_markup=kb)


@router.message(Command("movie"))
async def cmd_movie(message: Message, lang: str = "en") -> None:
    raw = message.text or ""
    for prefix in ("/movie", "🎬 أفلام", "🎬 Movies", "🎬"):
        if raw.lower().startswith(prefix.lower()):
            raw = raw[len(prefix):].strip()
            break

    if not raw:
        hint = (
            "🎬 *أرسل اسم الفيلم للبحث*\n\nمثال: `باتمان` أو `Inception 2010`\n\n🔥 *الأكثر مشاهدة الآن:*"
            if lang == "ar"
            else "🎬 *Send a movie name to search*\n\nExample: `Batman` or `Inception 2010`\n\n🔥 *Trending Now:*"
        )
        await message.answer(hint, parse_mode="Markdown")
        data = await omega_movies.get_trending()
        if data.get("error") or not data.get("results"):
            await message.answer(t("error", lang))
            return
        for item in data["results"][:3]:
            await _send_card(message, item, lang)
        return

    query, requested_year = _extract_year(raw)
    if not query:
        query = raw

    try:
        data = await omega_movies.search(query)
        if data.get("error") or not data.get("results"):
            await message.answer(t("not_found", lang))
            return

        results = data["results"]
        if requested_year is not None:
            filtered = [r for r in results if _item_year(r) == requested_year]
            if not filtered:
                await message.answer(
                    f"❌ لا توجد أفلام موثّقة في {requested_year}\n"
                    f"No verified {requested_year} movies found."
                )
                return
            results = filtered

        for item in results[:3]:
            await _send_card(message, item, lang)

    except Exception as exc:
        logger.error(f"Movie error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data and c.data.startswith("mv:"))
async def handle_mv_cb(callback: CallbackQuery, lang: str = "en") -> None:
    parts = callback.data.split(":")
    await callback.answer()
    if parts[1] != "detail" or len(parts) < 4:
        return
    try:
        tmdb_id, media_type = int(parts[2]), parts[3]
    except (ValueError, IndexError):
        return

    data = await omega_movies.get_details(tmdb_id, media_type)
    if data.get("error"):
        await callback.message.answer(t("error", lang))
        return

    title = data.get("title", "")
    rd = data.get("release_date", "")
    year = rd[:4] if rd else "?"
    vote = data.get("vote_average", 0)
    genres = ", ".join(data.get("genres", []))
    overview = data.get("overview", "")[:180]

    text = (
        f"🎬 *{title}* ({year})\n"
        f"⭐ {vote}/10  |  🎭 {genres}\n"
        f"📅 {rd}"
    )
    if data.get("runtime"):
        text += f"  |  ⏱ {data['runtime']} min"
    if data.get("tagline"):
        text += f"\n\n_{data['tagline']}_"
    if data.get("director"):
        text += f"\n\n🎬 {t('label_director', lang)}: {data['director']}"
    if data.get("cast"):
        names = ", ".join(c["name"] for c in data["cast"][:5])
        text += f"\n🌟 {t('label_cast', lang)}: {names}"
    text += f"\n\n📝 {overview}"
    if data.get("trailer_url"):
        text += f"\n\n🎥 [Trailer]({data['trailer_url']})"

    await callback.message.answer(text, parse_mode="Markdown")


def register_movies_handlers(dp) -> None:
    dp.include_router(router)
