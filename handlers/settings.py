import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import t

from config import LANGUAGES
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)
router = Router(name="settings")


@router.message(Command("settings"))
async def cmd_settings(message: Message, lang: str = "en") -> None:
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_language", lang), callback_data="set:lang"),
         InlineKeyboardButton(text=t("btn_currency_pref", lang), callback_data="set:currency")],
        [InlineKeyboardButton(text=t("btn_city", lang), callback_data="set:city"),
         InlineKeyboardButton(text=t("btn_length", lang), callback_data="set:length")],
    ])
    await message.answer(t("settings_title", lang), parse_mode="Markdown", reply_markup=buttons)


@router.callback_query(lambda c: c.data.startswith("set:"))
async def handle_settings(callback: CallbackQuery, lang: str = "en") -> None:
    action = callback.data.split(":")[1]
    await callback.answer()

    if action == "lang":
        buttons = []
        popular_langs = ["ar", "en", "fr", "es", "tr", "ru", "fa", "de", "hi", "zh-CN"]
        for lang_code in popular_langs:
            info = LANGUAGES.get(lang_code, {})
            buttons.append(InlineKeyboardButton(
                text=f"{info.get('flag', '')} {info.get('name', lang_code)}",
                callback_data=f"lang:{lang_code}"
            ))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
        await callback.message.answer(t("choose_lang", lang), reply_markup=keyboard)

    elif action == "currency":
        await callback.message.answer(t("btn_currency_pref", lang) + ": USD, EUR, SAR")

    elif action == "city":
        await callback.message.answer(t("btn_city", lang) + "?")


@router.callback_query(lambda c: c.data.startswith("lang:"))
async def handle_lang_change(callback: CallbackQuery, lang: str = "en") -> None:
    lang = callback.data.split(":")[1]
    await callback.answer(f"✅ {lang}")
    try:
        async with get_session() as session:
            await CRUDManager.update_user(session, callback.from_user.id, language_code=lang)
        lang_name = LANGUAGES.get(lang, {}).get("name", lang)
        await callback.message.answer(f"✅ {lang_name}")
    except Exception as exc:
        logger.error(f"Settings error: {exc}", exc_info=True)


def register_settings_handlers(dp) -> None:
    dp.include_router(router)
