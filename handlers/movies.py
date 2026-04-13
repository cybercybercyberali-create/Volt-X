import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_movies import omega_movies
from config import t

logger = logging.getLogger(__name__)
router = Router(name="movies")


@router.message(Command("movie"))
async def cmd_movie(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/movie", "").strip() if message.text else ""
    if not query:
        data = await omega_movies.get_trending()
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        text = t("trending_title", lang) + "\n\n"
        for i, item in enumerate(data["results"][:10], 1):
            stars = "⭐" * min(int(item.get("vote_average", 0) / 2), 5)
            text += f"{i}. **{item['title']}** {stars}\n"
            text += f"   📅 {item.get('release_date', 'N/A')} | 🎭 {item.get('media_type', '')}\n\n"
        text += t("search_hint", lang)
        await message.answer(text, parse_mode="Markdown")
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_movies.search(query)
        if data.get("error") or not data.get("results"):
            await message.answer(t("error", lang))
            return

        for item in data["results"][:3]:
            text = f"🎬 **{item['title']}**\n"
            text += f"{t('label_rating', lang)}: {item.get('vote_average', 'N/A')}/10\n"
            text += f"📅 {item.get('release_date', 'N/A')}\n"
            text += f"📝 {item.get('overview', '')[:200]}\n"

            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_details", lang), callback_data=f"mv:detail:{item['id']}:{item.get('media_type', 'movie')}"),
                 InlineKeyboardButton(text=t("btn_favorite", lang), callback_data=f"mv:watch:{item['id']}:{item.get('media_type', 'movie')}")],
            ])
            await message.answer(text, parse_mode="Markdown", reply_markup=buttons)
    except Exception as exc:
        logger.error(f"Movie error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data.startswith("mv:"))
async def handle_movie_cb(callback: CallbackQuery, lang: str = "en") -> None:
    parts = callback.data.split(":")
    action = parts[1]
    await callback.answer()

    if action == "detail" and len(parts) >= 4:
        tmdb_id = int(parts[2])
        media_type = parts[3]
        data = await omega_movies.get_details(tmdb_id, media_type)
        if data.get("error"):
            await callback.message.answer(t("error", lang))
            return
        text = f"🎬 **{data['title']}**\n"
        if data.get("tagline"):
            text += f"_\"{data['tagline']}\"_\n"
        text += f"\n⭐ TMDB: {data.get('vote_average', 'N/A')}/10"
        if data.get("imdb_rating") and data["imdb_rating"] != "N/A":
            text += f" | IMDb: {data['imdb_rating']}"
        if data.get("rotten_tomatoes") and data["rotten_tomatoes"] != "N/A":
            text += f" | 🍅 {data['rotten_tomatoes']}"
        text += f"\n📅 {data.get('release_date', 'N/A')}"
        if data.get("runtime"):
            text += f" | ⏱ {data['runtime']} min"
        text += f"\n🎭 {', '.join(data.get('genres', []))}\n"
        if data.get("director"):
            text += f"{t('label_director', lang)}: {data['director']}\n"
        if data.get("cast"):
            cast_names = [c['name'] for c in data['cast'][:5]]
            text += f"{t('label_cast', lang)}: {', '.join(cast_names)}\n"
        text += f"\n📝 {data.get('overview', '')[:300]}"
        if data.get("trailer_url"):
            text += f"\n\n🎥 [Trailer]({data['trailer_url']})"
        await callback.message.answer(text, parse_mode="Markdown")


def register_movies_handlers(dp) -> None:
    dp.include_router(router)
