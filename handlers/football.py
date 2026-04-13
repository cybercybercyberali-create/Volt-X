import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_football import omega_football, MAJOR_LEAGUES
from config import t

logger = logging.getLogger(__name__)
router = Router(name="football")


@router.message(Command("football"))
async def cmd_football(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    if not args:
        buttons = []
        for code, info in list(MAJOR_LEAGUES.items())[:8]:
            name = info.get("name_ar") if lang == "ar" else info.get("name", code)
            buttons.append(InlineKeyboardButton(text=name, callback_data=f"fb:standings:{code}"))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=t("fb_live_btn", lang), callback_data="fb:live")])
        await message.answer(t("fb_choose_league", lang), parse_mode="Markdown", reply_markup=keyboard)
        return

    league = args[0].upper()
    await message.answer(t("fetching", lang))
    try:
        data = await omega_football.get_standings(league)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        lname = data.get("league_name_ar") if lang == "ar" else data.get("league_name", league)
        text = f"⚽ **{lname}**\n\n"
        for entry in data.get("standings", [])[:10]:
            text += f"{entry['position']}. {entry['team']} — {entry['points']} pts\n"
        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Football error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data.startswith("fb:"))
async def handle_football_cb(callback: CallbackQuery, lang: str = "en") -> None:
    parts = callback.data.split(":")
    action = parts[1]
    await callback.answer()

    if action == "live":
        data = await omega_football.get_live_scores()
        if not data.get("matches"):
            await callback.message.answer(t("fb_no_live", lang))
            return
        text = t("fb_live_title", lang) + "\n\n"
        for m in data["matches"][:10]:
            text += f"  {m['home']} {m.get('score_home', '?')} - {m.get('score_away', '?')} {m['away']} ({m.get('clock', '')})\n"
        await callback.message.answer(text, parse_mode="Markdown")

    elif action == "standings" and len(parts) >= 3:
        league = parts[2]
        data = await omega_football.get_standings(league)
        if data.get("error"):
            await callback.message.answer(t("error", lang))
            return
        text = f"⚽ **{data.get('league_name_ar', league)}**\n\n"
        for entry in data.get("standings", [])[:10]:
            text += f"{entry['position']}. {entry['team']} — {entry['points']} pts\n"
        await callback.message.answer(text, parse_mode="Markdown")


def register_football_handlers(dp) -> None:
    dp.include_router(router)
