import logging
import os
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.filters import Command, CommandStart

from config import t, settings
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)
router = Router(name="start")

# ── Reply Keyboard layout ─────────────────────────────────────────────────────
# Bilingual button labels. The text sent to the bot is the Arabic or English label.
_KB_AR = [
    ["⛽ محروقات",  "🌤 طقس",      "🥇 ذهب"],
    ["💱 عملة",     "₿ كريبتو",   "📈 أسهم"],
    ["📰 أخبار",   "⚽ كرة قدم",  "🎬 أفلام"],
    ["🤖 ذكاء اصطناعي", "✈️ رحلات", "🌍 زلازل"],
    ["⚙️ إعدادات"],
]
_KB_EN = [
    ["⛽ Fuel",     "🌤 Weather",  "🥇 Gold"],
    ["💱 Currency", "₿ Crypto",   "📈 Stocks"],
    ["📰 News",     "⚽ Football", "🎬 Movies"],
    ["🤖 AI Chat",  "✈️ Flights",  "🌍 Quakes"],
    ["⚙️ Settings"],
]

# Flat lookup: button text → internal key (for routing)
_BTN_MAP: dict[str, str] = {}
for _row in _KB_AR:
    for _lbl in _row:
        _key = _lbl.split()[-1].lower()  # last word as key
        _BTN_MAP[_lbl] = _key
for _row in _KB_EN:
    for _lbl in _row:
        _key = _lbl.split()[-1].lower()
        _BTN_MAP[_lbl] = _key

# Extra exact mappings for ambiguous labels
_BTN_MAP.update({
    "⛽ محروقات": "fuel",    "⛽ Fuel": "fuel",
    "🌤 طقس": "weather",     "🌤 Weather": "weather",
    "🥇 ذهب": "gold",        "🥇 Gold": "gold",
    "💱 عملة": "currency",   "💱 Currency": "currency",
    "₿ كريبتو": "crypto",    "₿ Crypto": "crypto",
    "📈 أسهم": "stocks",     "📈 Stocks": "stocks",
    "📰 أخبار": "news",      "📰 News": "news",
    "⚽ كرة قدم": "football","⚽ Football": "football",
    "🎬 أفلام": "movies",    "🎬 Movies": "movies",
    "🤖 ذكاء اصطناعي": "ai","🤖 AI Chat": "ai",
    "✈️ رحلات": "flights",  "✈️ Flights": "flights",
    "🌍 زلازل": "quakes",   "🌍 Quakes": "quakes",
    "⚙️ إعدادات": "settings","⚙️ Settings": "settings",
})


def _build_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    layout = _KB_AR if lang == "ar" else _KB_EN
    rows = [[KeyboardButton(text=lbl) for lbl in row] for row in layout]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="اكتب رسالتك..." if lang == "ar" else "Type a message...",
    )


async def _dispatch_key(message: Message, key: str, lang: str) -> None:
    """Route a menu key to the correct handler."""
    try:
        if key == "fuel":
            from handlers.fuel import cmd_fuel
            await cmd_fuel(message, lang=lang)
        elif key == "weather":
            hint = "🌤 أرسل اسم المدينة — مثال: بيروت" if lang == "ar" else "🌤 Send a city name — e.g. Beirut"
            await message.answer(hint)
        elif key == "gold":
            from handlers.gold import cmd_gold
            await cmd_gold(message, lang=lang)
        elif key == "currency":
            from handlers.currency import cmd_currency
            await cmd_currency(message, lang=lang)
        elif key == "crypto":
            from handlers.crypto import cmd_crypto
            await cmd_crypto(message, lang=lang)
        elif key == "stocks":
            hint = "📈 أرسل رمز السهم — مثال: AAPL" if lang == "ar" else "📈 Send a stock symbol — e.g. AAPL"
            await message.answer(hint)
        elif key == "news":
            from handlers.news import cmd_news
            await cmd_news(message, lang=lang)
        elif key == "football":
            from handlers.football import cmd_football
            await cmd_football(message, lang=lang)
        elif key == "movies":
            from handlers.movies import cmd_movie
            await cmd_movie(message, lang=lang)
        elif key == "ai":
            hint = "🤖 اكتب سؤالك مباشرةً!" if lang == "ar" else "🤖 Just type your question!"
            await message.answer(hint)
        elif key == "flights":
            hint = "✈️ أرسل رمز المطار — مثال: BEY" if lang == "ar" else "✈️ Send airport code — e.g. BEY"
            await message.answer(hint)
        elif key == "quakes":
            from api_clients.omega_quakes import omega_quakes
            await message.answer("🌍 ..." if lang != "ar" else "🌍 جارٍ الجلب...")
            result = await omega_quakes.get_recent(min_magnitude=4.0, limit=8)
            if result.get("error") or not result.get("quakes"):
                await message.answer(t("error", lang))
                return
            lines = ["🌍 *زلازل حديثة (M4+)*\n" if lang == "ar" else "🌍 *Recent Earthquakes (M4+)*\n"]
            for q in result["quakes"][:8]:
                mag = q.get("magnitude", 0)
                place = q.get("place", "Unknown")
                e = "🟥" if mag >= 6 else ("🟧" if mag >= 5 else "🟨")
                lines.append(f"{e} M{mag:.1f} — {place}")
            await message.answer("\n".join(lines), parse_mode="Markdown")
        elif key == "settings":
            from handlers.settings import cmd_settings
            await cmd_settings(message, lang=lang)
    except Exception as exc:
        logger.error(f"Menu dispatch error for key={key!r}: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str = "en") -> None:
    try:
        name = message.from_user.first_name or "User"
        welcome = t("welcome", lang, name=name)
        await message.answer(welcome, reply_markup=_build_reply_keyboard(lang))
    except Exception as exc:
        logger.error(f"Start error: {exc}", exc_info=True)
        await message.answer(t("error", "en"))


@router.message(Command("menu"))
async def cmd_menu(message: Message, lang: str = "en") -> None:
    label = "اختر خدمة:" if lang == "ar" else "Choose a service:"
    await message.answer(label, reply_markup=_build_reply_keyboard(lang))


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "en") -> None:
    await message.answer(t("help_text", lang), parse_mode="Markdown")


@router.message(F.text.func(lambda t: t in _BTN_MAP))
async def handle_menu_button(message: Message, lang: str = "en") -> None:
    """Intercept reply-keyboard button taps before the AI catch-all."""
    key = _BTN_MAP[message.text]
    await _dispatch_key(message, key, lang)


def register_start_handlers(dp) -> None:
    dp.include_router(router)
