import logging
from datetime import datetime, timezone
from typing import Any, Optional

from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)


class OmegaMemory:
    """Layer 4: Memory & Personalization — tracks user behavior and adapts."""

    async def update_user_context(self, user_id: int, query: str, service: str, response_quality: float) -> None:
        """Update user memory after each interaction."""
        try:
            async with get_session() as session:
                await CRUDManager.add_query_to_memory(session, user_id, query)

                user = await CRUDManager.get_user_by_telegram_id(session, user_id)
                if user and user.memory:
                    memory = user.memory
                    topics = dict(memory.common_topics or {})
                    topics[service] = topics.get(service, 0) + 1
                    await CRUDManager.update_memory(session, user.id, common_topics=topics)

                    hour = datetime.now(timezone.utc).hour
                    hours = dict(memory.active_hours or {})
                    hours[str(hour)] = hours.get(str(hour), 0) + 1
                    await CRUDManager.update_memory(session, user.id, active_hours=hours)

                    signals = dict(memory.satisfaction_signals or {})
                    if response_quality >= 0.7:
                        signals["positive"] = signals.get("positive", 0) + 1
                    else:
                        signals["negative"] = signals.get("negative", 0) + 1
                    await CRUDManager.update_memory(session, user.id, satisfaction_signals=signals)

        except Exception as exc:
            logger.error(f"Error updating memory for user {user_id}: {exc}", exc_info=True)

    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]:
        """Get user profile for personalization."""
        try:
            async with get_session() as session:
                user = await CRUDManager.get_user_by_telegram_id(session, telegram_id)
                if not user:
                    return {"exists": False}

                memory = user.memory
                return {
                    "exists": True,
                    "language": user.language_code,
                    "currency": user.preferred_currency,
                    "city": user.home_city,
                    "country": user.home_country,
                    "expertise": user.expertise_level,
                    "prefers_emojis": user.prefers_emojis,
                    "response_length": user.response_length_pref,
                    "common_topics": dict(memory.common_topics or {}) if memory else {},
                    "total_requests": user.total_requests,
                }
        except Exception as exc:
            logger.error(f"Error getting profile for user {telegram_id}: {exc}", exc_info=True)
            return {"exists": False}

    async def predict_next_query(self, telegram_id: int) -> Optional[str]:
        """Predict what the user might ask next based on patterns."""
        try:
            profile = await self.get_user_profile(telegram_id)
            if not profile.get("exists"):
                return None

            topics = profile.get("common_topics", {})
            if not topics:
                return None

            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            top_topic = sorted_topics[0][0] if sorted_topics else None
            return top_topic

        except Exception as exc:
            logger.error(f"Error predicting for user {telegram_id}: {exc}", exc_info=True)
            return None


omega_memory = OmegaMemory()
