import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from services.rate_limiter import check_user_rate

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Rate limit incoming messages per user."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            if not check_user_rate(user_id, "message"):
                logger.warning(f"Rate limited user {user_id}")
                await event.answer("⏳ Too many messages. Please wait a moment.")
                return None

        return await handler(event, data)
