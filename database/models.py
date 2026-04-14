import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint, JSON,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    preferred_currency: Mapped[str] = mapped_column(String(10), default="USD")
    home_city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    home_country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    home_timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expertise_level: Mapped[str] = mapped_column(String(20), default="normal")
    prefers_emojis: Mapped[bool] = mapped_column(Boolean, default=True)
    response_length_pref: Mapped[str] = mapped_column(String(20), default="medium")

    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    memory = relationship("UserMemory", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    cv_data = relationship("CVData", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    favorite_teams = relationship("FavoriteTeam", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    tracked_coins = relationship("TrackedCoin", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    notifications = relationship("ProactiveNotification", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        Index("ix_users_last_active", "last_active"),
        Index("ix_users_country", "home_country"),
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pref_key: Mapped[str] = mapped_column(String(100), nullable=False)
    pref_value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="preferences")

    __table_args__ = (
        UniqueConstraint("user_id", "pref_key", name="uq_user_pref"),
        Index("ix_user_pref_key", "user_id", "pref_key"),
    )


class UserMemory(Base):
    __tablename__ = "user_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    common_topics: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    active_hours: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    satisfaction_signals: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    last_10_queries: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    language_fluency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    predictive_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="memory")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    service: Mapped[str] = mapped_column(String(50), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    result_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_models_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    fusion_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    user_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="search_history")

    __table_args__ = (
        Index("ix_search_user_service", "user_id", "service"),
        Index("ix_search_created", "created_at"),
    )


class Watchlist(Base):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    poster_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="plan_to_watch")
    personal_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    watched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="watchlist")

    __table_args__ = (
        UniqueConstraint("user_id", "tmdb_id", "media_type", name="uq_user_watchlist"),
    )


class CVData(Base):
    __tablename__ = "cv_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    data_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    template: Mapped[str] = mapped_column(String(50), default="modern")
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="cv_data")


class AIFusionLog(Base):
    __tablename__ = "ai_fusion_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    models_called: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    models_responded: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    fusion_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    judge_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_fusion_task", "task_type"),
        Index("ix_fusion_created", "created_at"),
    )


class APICallLog(Base):
    __tablename__ = "api_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    is_outlier_removed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_apicall_name", "api_name"),
        Index("ix_apicall_created", "created_at"),
    )


class FavoriteTeam(Base):
    __tablename__ = "favorite_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[str] = mapped_column(String(50), nullable=False)
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    league_code: Mapped[str] = mapped_column(String(20), nullable=False)
    notify_goals: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="favorite_teams")

    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_user_team"),
    )


class TrackedCoin(Base):
    __tablename__ = "tracked_coins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id: Mapped[str] = mapped_column(String(100), nullable=False)
    coin_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_price_above: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    alert_price_below: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="tracked_coins")

    __table_args__ = (
        UniqueConstraint("user_id", "coin_id", name="uq_user_coin"),
    )


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    models_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    fusion_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="conversations")

    __table_args__ = (
        Index("ix_convo_user", "user_id", "created_at"),
    )


class ProactiveNotification(Base):
    __tablename__ = "proactive_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    triggered_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("ix_notif_user", "user_id"),
        Index("ix_notif_type", "type"),
    )
