import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart

from config import t, MENU_LABELS, MENU_LAYOUT, get_menu_label, settings
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)
router = Router(name="start")


def _build_main_menu(lang: str = "en") -> InlineKeyboardMarkup:
    from config import MENU_LAYOUT, get_menu_label
    buttons = []
    for row in MENU_LAYOUT:
        btn_row = [InlineKeyboardButton(text=get_menu_label(key, lang), callback_data=f"menu:{key}") for key in row]
        buttons.append(btn_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str = "en") -> None:
    try:
        name = message.from_user.first_name or "User"
        welcome = t("welcome", lang, name=name)
        await message.answer(welcome, reply_markup=_build_main_menu(lang))
    except Exception as exc:
        logger.error(f"Start error: {exc}", exc_info=True)
        await message.answer(t("error", "en"))


@router.message(Command("menu"))
async def cmd_menu(message: Message, lang: str = "en") -> None:
    await message.answer(t("main_menu", "en"), reply_markup=_build_main_menu())


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


def register_start_handlers(dp) -> None:
    dp.include_router(router)
