import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import settings
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseMiddleware):
    """Security checks: banned users, admin commands."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            try:
                async with get_session() as session:
                    user = await CRUDManager.get_user_by_telegram_id(session, event.from_user.id)
                    if user and user.is_banned:
                        logger.warning(f"Banned user {event.from_user.id} attempted access")
                        await event.answer("⛔")
                        return None
            except Exception as exc:
                logger.debug(f"Security check error: {exc}")

        return await handler(event, data)
