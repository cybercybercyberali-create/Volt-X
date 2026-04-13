import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from config import settings, IS_FREE, DATA_DIR

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    global _engine
    if _engine is not None:
        return _engine

    db_url = settings.db_url
    is_sqlite = "sqlite" in db_url

    if is_sqlite:
        _engine = create_async_engine(
            db_url,
            poolclass=NullPool,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        # Enable WAL mode for concurrent read/write support
        from sqlalchemy import event as sa_event
        @sa_event.listens_for(_engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        logger.info(f"SQLite engine created with WAL mode: {DATA_DIR}/omega.db")
    else:
        _engine = create_async_engine(
            db_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=5 if IS_FREE else 20,
            max_overflow=10 if IS_FREE else 40,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False,
        )
        logger.info("PostgreSQL engine created")

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is not None:
        return _session_factory

    engine = get_engine()
    _session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception as exc:
        await session.rollback()
        logger.error(f"Database session error: {exc}", exc_info=True)
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Initialize database and create all tables."""
    from database.models import Base

    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}", exc_info=True)
        raise


async def close_db() -> None:
    """Close database engine and cleanup connections."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")
