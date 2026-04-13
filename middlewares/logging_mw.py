import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log all incoming messages and callbacks with timing."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        start = time.monotonic()
        user_id = None
        event_type = type(event).__name__

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            text_preview = (event.text or "")[:50]
            logger.info(f"[MSG] user={user_id} text='{text_preview}'")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            logger.info(f"[CB] user={user_id} data='{event.data}'")

        try:
            result = await handler(event, data)
            elapsed = int((time.monotonic() - start) * 1000)
            logger.info(f"[{event_type}] user={user_id} processed in {elapsed}ms")
            return result
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.error(f"[{event_type}] user={user_id} FAILED in {elapsed}ms: {exc}", exc_info=True)
            raise
