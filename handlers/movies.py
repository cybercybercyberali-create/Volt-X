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

# Genre list: (tmdb_id, ar_label, en_label)
_GENRES = [
    (28,    "🎬 أكشن",       "🎬 Action"),
    (35,    "😂 كوميدي",     "😂 Comedy"),
    (18,    "🎭 دراما",      "🎭 Drama"),
    (27,    "👻 رعب",        "👻 Horror"),
    (10749, "❤️ رومانسي",   "❤️ Romance"),
    (878,   "🚀 خيال علمي",  "🚀 Sci-Fi"),
    (53,    "🔍 إثارة",      "🔍 Thriller"),
    (16,    "🎨 أنيمي",      "🎨 Animation"),
    (80,    "🔫 جريمة",      "🔫 Crime"),
    (12,    "🌍 مغامرة",     "🌍 Adventure"),
]


def _genre_kb(lang: str) -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(
            text=(ar if lang == "ar" else en),
            callback_data=f"mv_g:{gid}",
        )
        for gid, ar, en in _GENRES
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
    """Clean text-only card — no poster."""
    title = item.get("title", "")
    rd = item.get("release_date", "")
    year = rd[:4] if rd else "?"
    vote = item.get("vote_average", 0)
    genres = item.get("genres", [])
    genres_str = " · ".join(genres[:2]) if genres else "—"
    overview = (item.get("overview") or "")
    preview = overview[:180] + ("..." if len(overview) > 180 else "")
    return (
        f"🎬 *{title}* `({year})`\n"
        f"⭐ `{vote}/10`  ·  🎭 {genres_str}\n"
        f"📝 {preview}"
    )


async def _send_card(msg: Message, item: dict, lang: str) -> None:
    cap = _caption(item)
    await msg.answer(cap, parse_mode="Markdown")


@router.message(Command("movie"))
async def cmd_movie(message: Message, lang: str = "en") -> None:
    raw = message.text or ""
    for prefix in ("/movie", "🎬 أفلام", "🎬 Movies", "🎬"):
        if raw.lower().startswith(prefix.lower()):
            raw = raw[len(prefix):].strip()
            break

    # No query → show genre selector
    if not raw:
        prompt = "🎬 *اختر النوع أو ابحث باسم الفيلم:*" if lang == "ar" \
            else "🎬 *Pick a genre or search by name:*"
        await message.answer(prompt, parse_mode="Markdown", reply_markup=_genre_kb(lang))
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
                no_result = (
                    f"❌ لا توجد نتائج في {requested_year}"
                    if lang == "ar"
                    else f"❌ No results found for {requested_year}"
                )
                await message.answer(no_result)
                return
            results = filtered

        for item in results[:3]:
            await _send_card(message, item, lang)

    except Exception as exc:
        logger.error(f"Movie error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.message(Command("trending"))
async def cmd_trending(message: Message, lang: str = "en") -> None:
    wait = await message.answer(
        "⏳ جارٍ تحميل الأكثر مشاهدةً..." if lang == "ar"
        else "⏳ Loading trending movies..."
    )
    try:
        tmdb_lang = "ar" if lang == "ar" else "en-US"
        data = await omega_movies.get_trending(lang=tmdb_lang)
        if data.get("error") or not data.get("results"):
            await wait.edit_text(t("not_found", lang))
            return
        await wait.delete()
        for item in data["results"][:5]:
            await _send_card(message, item, lang)
    except Exception as exc:
        logger.error(f"Trending error: {exc}", exc_info=True)
        try:
            await wait.edit_text(t("error", lang))
        except Exception:
            pass


@router.callback_query(lambda c: c.data and c.data.startswith("mv_g:"))
async def handle_genre_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    try:
        genre_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        return

    try:
        data = await omega_movies.get_by_genre(genre_id, lang=lang)
        if data.get("error") or not data.get("results"):
            await callback.message.answer(t("not_found", lang))
            return
        for item in data["results"][:5]:
            await _send_card(callback.message, item, lang)
    except Exception as exc:
        logger.error(f"Genre movies error: {exc}", exc_info=True)
        await callback.message.answer(t("error", lang))


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

    try:
        data = await omega_movies.get_details(tmdb_id, media_type)
        if data.get("error"):
            await callback.message.answer(t("error", lang))
            return

        title = data.get("title", "")
        rd = data.get("release_date", "")
        year = rd[:4] if rd else "?"
        vote = data.get("vote_average", 0)
        genres = " · ".join(data.get("genres", [])[:3])
        overview = (data.get("overview") or "")[:200]

        text = (
            f"🎬 *{title}* `({year})`\n"
            f"⭐ `{vote}/10`  ·  🎭 {genres}\n"
            f"📅 {rd}"
        )
        if data.get("runtime"):
            text += f"  ·  ⏱ {data['runtime']} min"
        if data.get("tagline"):
            text += f"\n\n_{data['tagline']}_"
        if data.get("director"):
            text += f"\n\n🎬 {t('label_director', lang)}: {data['director']}"
        cast = data.get("cast", [])
        if cast:
            names = ", ".join(c.get("name", "") for c in cast[:4] if c.get("name"))
            if names:
                text += f"\n🌟 {t('label_cast', lang)}: {names}"
        if overview:
            text += f"\n\n📝 {overview}"
        if data.get("trailer_url"):
            text += f"\n\n🎥 [Trailer]({data['trailer_url']})"

        await callback.message.answer(text, parse_mode="Markdown")

    except Exception as exc:
        logger.error(f"Movie detail error: {exc}", exc_info=True)
        await callback.message.answer(t("error", lang))


def register_movies_handlers(dp) -> None:
    dp.include_router(router)

