import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from config import LANGUAGES
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)

SUPPORTED_LANG_CODES = set(LANGUAGES.keys())


def _resolve_lang(telegram_lang: str) -> str:
    """Map Telegram device language to our supported language."""
    if not telegram_lang:
        return "en"
    code = telegram_lang.lower().strip()
    if code in SUPPORTED_LANG_CODES:
        return code
    short = code.split("-")[0].split("_")[0]
    if short in SUPPORTED_LANG_CODES:
        return short
    if short == "zh":
        return "zh-CN"
    return "en"


class UserTrackerMiddleware(BaseMiddleware):
    """Auto-detect device language + track user + inject lang into handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_obj = None
        if isinstance(event, Message) and event.from_user:
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_obj = event.from_user

        if user_obj:
            device_lang = _resolve_lang(user_obj.language_code)
            data["lang"] = device_lang

            try:
                async with get_session() as session:
                    user = await CRUDManager.get_or_create_user(
                        session,
                        telegram_id=user_obj.id,
                        username=user_obj.username,
                        first_name=user_obj.first_name,
                        last_name=user_obj.last_name,
                        language_code=device_lang,
                    )
                    if user.language_code != device_lang:
                        user.language_code = device_lang
                        await session.flush()
                    data["db_user"] = user
                    data["lang"] = user.language_code
            except Exception as exc:
                logger.debug(f"User tracker error: {exc}")
                data["lang"] = device_lang

            # Auto-detect Arabic text: if message contains Arabic chars, override lang to "ar"
            import re
            msg_text = ""
            if isinstance(event, Message) and event.text:
                msg_text = event.text
            elif isinstance(event, Message) and event.caption:
                msg_text = event.caption
            if msg_text and re.search(r'[\u0600-\u06FF]', msg_text):
                data["lang"] = "ar"
        else:
            data["lang"] = "en"

        return await handler(event, data)
