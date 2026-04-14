import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from database.models import (
    User, UserPreference, UserMemory, SearchHistory, Watchlist, CVData,
    AIFusionLog, APICallLog, FavoriteTeam, TrackedCoin, AIConversation,
    ProactiveNotification,
)

logger = logging.getLogger(__name__)


class CRUDManager:
    """Centralized CRUD operations for all database models."""

    # ━━━ User Operations ━━━

    @staticmethod
    async def get_or_create_user(session: AsyncSession, telegram_id: int, **kwargs: Any) -> User:
        """Get existing user or create new one."""
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is not None:
                user.last_active = datetime.now(timezone.utc)
                user.total_requests = (user.total_requests or 0) + 1
                for key, value in kwargs.items():
                    if hasattr(user, key) and value is not None:
                        current = getattr(user, key)
                        if current is None or current == "":
                            setattr(user, key, value)
                await session.flush()
                return user

            user = User(
                telegram_id=telegram_id,
                username=kwargs.get("username"),
                first_name=kwargs.get("first_name"),
                last_name=kwargs.get("last_name"),
                language_code=kwargs.get("language_code", "en"),
                total_requests=1,
            )
            session.add(user)
            await session.flush()

            memory = UserMemory(user_id=user.id)
            session.add(memory)
            await session.flush()

            logger.info(f"New user created: {telegram_id} ({kwargs.get('first_name', 'Unknown')})")
            return user

        except Exception as exc:
            logger.error(f"Error in get_or_create_user({telegram_id}): {exc}", exc_info=True)
            raise

    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Fetch user by Telegram ID."""
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error(f"Error fetching user {telegram_id}: {exc}", exc_info=True)
            return None

    @staticmethod
    async def update_user(session: AsyncSession, telegram_id: int, **kwargs: Any) -> bool:
        """Update user fields."""
        try:
            await session.execute(
                update(User).where(User.telegram_id == telegram_id).values(**kwargs)
            )
            return True
        except Exception as exc:
            logger.error(f"Error updating user {telegram_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_user_count(session: AsyncSession) -> int:
        """Get total user count."""
        try:
            result = await session.execute(select(func.count(User.id)))
            return result.scalar_one() or 0
        except Exception as exc:
            logger.error(f"Error counting users: {exc}", exc_info=True)
            return 0

    @staticmethod
    async def get_active_users(session: AsyncSession, hours: int = 24) -> int:
        """Count users active in last N hours."""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            result = await session.execute(
                select(func.count(User.id)).where(User.last_active >= cutoff)
            )
            return result.scalar_one() or 0
        except Exception as exc:
            logger.error(f"Error counting active users: {exc}", exc_info=True)
            return 0

    # ━━━ Preference Operations ━━━

    @staticmethod
    async def set_preference(session: AsyncSession, user_id: int, key: str, value: str) -> bool:
        """Set a user preference (upsert)."""
        try:
            existing = await session.execute(
                select(UserPreference).where(
                    and_(UserPreference.user_id == user_id, UserPreference.pref_key == key)
                )
            )
            pref = existing.scalar_one_or_none()
            if pref:
                pref.pref_value = value
                pref.updated_at = datetime.now(timezone.utc)
            else:
                pref = UserPreference(user_id=user_id, pref_key=key, pref_value=value)
                session.add(pref)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error setting preference {key} for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_preference(session: AsyncSession, user_id: int, key: str) -> Optional[str]:
        """Get a user preference value."""
        try:
            result = await session.execute(
                select(UserPreference.pref_value).where(
                    and_(UserPreference.user_id == user_id, UserPreference.pref_key == key)
                )
            )
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error(f"Error getting preference {key} for user {user_id}: {exc}", exc_info=True)
            return None

    # ━━━ Memory Operations ━━━

    @staticmethod
    async def update_memory(session: AsyncSession, user_id: int, **kwargs: Any) -> bool:
        """Update user memory fields."""
        try:
            result = await session.execute(
                select(UserMemory).where(UserMemory.user_id == user_id)
            )
            memory = result.scalar_one_or_none()
            if memory is None:
                memory = UserMemory(user_id=user_id, **kwargs)
                session.add(memory)
            else:
                for key, value in kwargs.items():
                    if hasattr(memory, key):
                        setattr(memory, key, value)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error updating memory for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def add_query_to_memory(session: AsyncSession, user_id: int, query: str) -> bool:
        """Add a query to user's last_10_queries."""
        try:
            result = await session.execute(
                select(UserMemory).where(UserMemory.user_id == user_id)
            )
            memory = result.scalar_one_or_none()
            if memory is None:
                memory = UserMemory(user_id=user_id, last_10_queries=[query])
                session.add(memory)
            else:
                queries = list(memory.last_10_queries or [])
                queries.append(query)
                memory.last_10_queries = queries[-10:]
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error adding query to memory for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ Search History ━━━

    @staticmethod
    async def log_search(session: AsyncSession, user_id: int, service: str, query: str, **kwargs: Any) -> bool:
        """Log a search query."""
        try:
            entry = SearchHistory(
                user_id=user_id,
                service=service,
                query=query,
                result_summary=kwargs.get("result_summary"),
                response_time_ms=kwargs.get("response_time_ms"),
                ai_models_used=kwargs.get("ai_models_used"),
                fusion_score=kwargs.get("fusion_score"),
            )
            session.add(entry)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error logging search for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ Watchlist ━━━

    @staticmethod
    async def add_to_watchlist(session: AsyncSession, user_id: int, tmdb_id: int, media_type: str, title: str, **kwargs: Any) -> bool:
        """Add item to watchlist."""
        try:
            existing = await session.execute(
                select(Watchlist).where(
                    and_(Watchlist.user_id == user_id, Watchlist.tmdb_id == tmdb_id, Watchlist.media_type == media_type)
                )
            )
            if existing.scalar_one_or_none():
                return False
            item = Watchlist(
                user_id=user_id, tmdb_id=tmdb_id, media_type=media_type,
                title=title, poster_path=kwargs.get("poster_path"),
                status=kwargs.get("status", "plan_to_watch"),
            )
            session.add(item)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error adding to watchlist for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_watchlist(session: AsyncSession, user_id: int, status: Optional[str] = None) -> list[Watchlist]:
        """Get user's watchlist."""
        try:
            query = select(Watchlist).where(Watchlist.user_id == user_id)
            if status:
                query = query.where(Watchlist.status == status)
            query = query.order_by(Watchlist.added_at.desc())
            result = await session.execute(query)
            return list(result.scalars().all())
        except Exception as exc:
            logger.error(f"Error fetching watchlist for user {user_id}: {exc}", exc_info=True)
            return []

    # ━━━ AI Fusion Logs ━━━

    @staticmethod
    async def log_fusion(session: AsyncSession, task_type: str, models_called: list, models_responded: list, fusion_time_ms: int, **kwargs: Any) -> bool:
        """Log AI fusion result."""
        try:
            entry = AIFusionLog(
                task_type=task_type,
                models_called=models_called,
                models_responded=models_responded,
                fusion_time_ms=fusion_time_ms,
                judge_score=kwargs.get("judge_score"),
                final_confidence=kwargs.get("final_confidence"),
            )
            session.add(entry)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error logging fusion: {exc}", exc_info=True)
            return False

    # ━━━ API Call Logs ━━━

    @staticmethod
    async def log_api_call(session: AsyncSession, api_name: str, endpoint: str, status_code: int, response_time_ms: int, **kwargs: Any) -> bool:
        """Log external API call."""
        try:
            entry = APICallLog(
                api_name=api_name,
                endpoint=endpoint,
                status_code=status_code,
                response_time_ms=response_time_ms,
                is_fallback=kwargs.get("is_fallback", False),
                is_outlier_removed=kwargs.get("is_outlier_removed", False),
            )
            session.add(entry)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error logging API call: {exc}", exc_info=True)
            return False

    # ━━━ Favorite Teams ━━━

    @staticmethod
    async def add_favorite_team(session: AsyncSession, user_id: int, team_id: str, team_name: str, league_code: str) -> bool:
        """Add a favorite football team."""
        try:
            existing = await session.execute(
                select(FavoriteTeam).where(
                    and_(FavoriteTeam.user_id == user_id, FavoriteTeam.team_id == team_id)
                )
            )
            if existing.scalar_one_or_none():
                return False
            team = FavoriteTeam(user_id=user_id, team_id=team_id, team_name=team_name, league_code=league_code)
            session.add(team)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error adding favorite team for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ Tracked Coins ━━━

    @staticmethod
    async def track_coin(session: AsyncSession, user_id: int, coin_id: str, coin_symbol: str, **kwargs: Any) -> bool:
        """Track a cryptocurrency."""
        try:
            existing = await session.execute(
                select(TrackedCoin).where(
                    and_(TrackedCoin.user_id == user_id, TrackedCoin.coin_id == coin_id)
                )
            )
            if existing.scalar_one_or_none():
                return False
            coin = TrackedCoin(
                user_id=user_id, coin_id=coin_id, coin_symbol=coin_symbol,
                alert_price_above=kwargs.get("alert_price_above"),
                alert_price_below=kwargs.get("alert_price_below"),
            )
            session.add(coin)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error tracking coin for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ AI Conversations ━━━

    @staticmethod
    async def save_conversation(session: AsyncSession, user_id: int, role: str, content: str, **kwargs: Any) -> bool:
        """Save a conversation message."""
        try:
            msg = AIConversation(
                user_id=user_id, role=role, content=content,
                models_used=kwargs.get("models_used"),
                fusion_score=kwargs.get("fusion_score"),
            )
            session.add(msg)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error saving conversation for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_conversation_history(session: AsyncSession, user_id: int, limit: int = 20) -> list[AIConversation]:
        """Get recent conversation history."""
        try:
            result = await session.execute(
                select(AIConversation)
                .where(AIConversation.user_id == user_id)
                .order_by(AIConversation.created_at.desc())
                .limit(limit)
            )
            messages = list(result.scalars().all())
            messages.reverse()
            return messages
        except Exception as exc:
            logger.error(f"Error fetching conversation for user {user_id}: {exc}", exc_info=True)
            return []

    # ━━━ Stats ━━━

    @staticmethod
    async def get_stats(session: AsyncSession) -> dict[str, Any]:
        """Get system-wide statistics."""
        try:
            total_users = await session.execute(select(func.count(User.id)))
            active_24h = await session.execute(
                select(func.count(User.id)).where(
                    User.last_active >= datetime.now(timezone.utc) - timedelta(hours=24)
                )
            )
            total_searches = await session.execute(select(func.count(SearchHistory.id)))
            total_fusions = await session.execute(select(func.count(AIFusionLog.id)))
            avg_fusion_time = await session.execute(select(func.avg(AIFusionLog.fusion_time_ms)))

            return {
                "total_users": total_users.scalar_one() or 0,
                "active_24h": active_24h.scalar_one() or 0,
                "total_searches": total_searches.scalar_one() or 0,
                "total_fusions": total_fusions.scalar_one() or 0,
                "avg_fusion_time_ms": round(avg_fusion_time.scalar_one() or 0, 1),
            }
        except Exception as exc:
            logger.error(f"Error getting stats: {exc}", exc_info=True)
            return {"total_users": 0, "active_24h": 0, "total_searches": 0, "total_fusions": 0, "avg_fusion_time_ms": 0}
