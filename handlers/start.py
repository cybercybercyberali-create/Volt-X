import logging
import os
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.filters import Command, CommandStart

from config import t, MENU_LABELS, MENU_LAYOUT, get_menu_label, settings
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)
router = Router(name="start")

# TWA URL ─ resolves to Render external URL + /static/menu.html
_BASE_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
TWA_MENU_URL = f"{_BASE_URL}/static/menu.html" if _BASE_URL else ""


def _build_main_menu(lang: str = "en") -> InlineKeyboardMarkup:
    from config import MENU_LAYOUT, get_menu_label
    buttons = []
    for row in MENU_LAYOUT:
        btn_row = [InlineKeyboardButton(text=get_menu_label(key, lang), callback_data=f"menu:{key}") for key in row]
        buttons.append(btn_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _build_twa_button(lang: str = "en") -> InlineKeyboardMarkup:
    """Return a keyboard with one button that opens the TWA menu."""
    label = "📋 القائمة" if lang == "ar" else "📋 Menu"
    if TWA_MENU_URL:
        btn = InlineKeyboardButton(text=label, web_app=WebAppInfo(url=TWA_MENU_URL))
    else:
        # Fallback: inline menu if TWA URL not set
        btn = InlineKeyboardButton(text=label, callback_data="menu:home")
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str = "en") -> None:
    try:
        name = message.from_user.first_name or "User"
        welcome = t("welcome", lang, name=name)
        # Show TWA menu button first, then inline grid below
        markup = _build_twa_button(lang)
        await message.answer(welcome, reply_markup=markup)
    except Exception as exc:
        logger.error(f"Start error: {exc}", exc_info=True)
        await message.answer(t("error", "en"))


@router.message(Command("menu"))
async def cmd_menu(message: Message, lang: str = "en") -> None:
    await message.answer(t("main_menu", "en"), reply_markup=_build_twa_button(lang))


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "en") -> None:
    await message.answer(t("help_text", lang), parse_mode="Markdown")


@router.callback_query(F.data.startswith("menu:"))
async def handle_menu_callback(callback: CallbackQuery, lang: str = "en") -> None:
    action = callback.data.split(":")[1]
    action_map = {
        "gold": "/gold", "currency": "/currency", "fuel": "/fuel",
        "weather": "/weather", "football": "/football", "movies": "/movie",
        "cv": "/cv", "logo": "/logo", "ai_chat": "/ai",
        "stocks": "/stock", "crypto": "/crypto", "news": "/news",
        "flights": "/flight", "quakes": "/quakes", "settings": "/settings",
    }
    cmd = action_map.get(action, "/help")
    await callback.answer()
    await callback.message.answer(f"Use {cmd} command or just type your request!")


# ── TWA data_sent handler ─────────────────────────────────────────────────────

@router.message(F.web_app_data)
async def handle_menu_selection(message: Message, lang: str = "en") -> None:
    """Handle button selections sent from the Telegram Web App menu."""
    data = (message.web_app_data.data or "").strip().lower()
    logger.info(f"TWA menu selection: {data!r} from user {message.from_user.id}")

    try:
        if data == "gold":
            from handlers.gold import cmd_gold
            await cmd_gold(message, lang=lang)

        elif data == "currency":
            from handlers.currency import cmd_currency
            await cmd_currency(message, lang=lang)

        elif data == "fuel":
            from handlers.fuel import cmd_fuel
            await cmd_fuel(message, lang=lang)

        elif data == "weather":
            if lang == "ar":
                await message.answer("🌤 أرسل اسم المدينة للحصول على الطقس.\nمثال: بيروت")
            else:
                await message.answer("🌤 Send a city name to get the weather.\nExample: Beirut")

        elif data == "football":
            from handlers.football import cmd_football
            await cmd_football(message, lang=lang)

        elif data == "movies":
            from handlers.movies import cmd_movie
            await cmd_movie(message, lang=lang)

        elif data == "cv":
            from handlers.cv_generator import cmd_cv
            await cmd_cv(message, lang=lang)

        elif data == "logo":
            from handlers.logo_generator import cmd_logo
            await cmd_logo(message, lang=lang)

        elif data == "ai":
            if lang == "ar":
                await message.answer("🤖 اكتب سؤالك وسأجيب عليك فوراً!")
            else:
                await message.answer("🤖 Ask me anything and I'll answer right away!")

        elif data == "stocks":
            if lang == "ar":
                await message.answer("📈 أرسل رمز السهم (مثال: AAPL, TSLA)")
            else:
                await message.answer("📈 Send a stock symbol (e.g. AAPL, TSLA)")

        elif data == "crypto":
            from handlers.crypto import cmd_crypto
            await cmd_crypto(message, lang=lang)

        elif data == "news":
            from handlers.news import cmd_news
            await cmd_news(message, lang=lang)

        elif data == "flights":
            if lang == "ar":
                await message.answer("✈️ أرسل رمز المطار أو اسم المدينة (مثال: BEY)")
            else:
                await message.answer("✈️ Send an airport code or city (e.g. BEY)")

        elif data == "quakes":
            # Try dedicated quakes handler first, fall back to inline fetch
            try:
                from handlers.quakes import cmd_quakes
                await cmd_quakes(message, lang=lang)
            except ImportError:
                if lang == "ar":
                    await message.answer("🌍 جارٍ جلب بيانات الزلازل...")
                else:
                    await message.answer("🌍 Fetching earthquake data...")
                from api_clients.omega_quakes import omega_quakes
                result = await omega_quakes.get_recent(min_magnitude=4.0, limit=10)
                if result.get("error") or not result.get("quakes"):
                    await message.answer(t("error", lang))
                    return
                quakes = result["quakes"][:10]
                lines = ["🌍 *Recent Earthquakes (M4+)*\n"]
                for q in quakes:
                    mag = q.get("magnitude", 0)
                    place = q.get("place", "Unknown")
                    mag_emoji = "🟥" if mag >= 6 else ("🟧" if mag >= 5 else "🟨")
                    lines.append(f"{mag_emoji} M{mag:.1f} — {place}")
                await message.answer("\n".join(lines), parse_mode="Markdown")

        elif data == "settings":
            from handlers.settings import cmd_settings
            await cmd_settings(message, lang=lang)

        else:
            logger.warning(f"Unknown TWA menu selection: {data!r}")
            await message.answer(t("error", lang))

    except Exception as exc:
        logger.error(f"TWA menu handler error for {data!r}: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_start_handlers(dp) -> None:
    dp.include_router(router)
