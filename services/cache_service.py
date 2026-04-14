import logging
import time
import hashlib
import json
from typing import Any, Optional
from pathlib import Path

from config import IS_FREE, IS_PAID, DATA_DIR, CACHE_TTL, settings

logger = logging.getLogger(__name__)

_disk_cache = None
_redis_client = None


def _get_disk_cache():
    """Initialize diskcache for free plan."""
    global _disk_cache
    if _disk_cache is None:
        import diskcache
        cache_dir = DATA_DIR / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        _disk_cache = diskcache.Cache(
            str(cache_dir),
            size_limit=500 * 1024 * 1024,
            eviction_policy="least-recently-used",
        )
        logger.info(f"DiskCache initialized at {cache_dir}")
    return _disk_cache


async def _get_redis():
    """Initialize Redis for paid plan."""
    global _redis_client
    if _redis_client is None and IS_PAID and settings.redis_url:
        try:
            import redis.asyncio as aioredis
            _redis_client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
            await _redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as exc:
            logger.warning(f"Redis connection failed, falling back to diskcache: {exc}")
            _redis_client = None
    return _redis_client


def _make_key(prefix: str, *args: Any) -> str:
    """Generate a cache key from prefix and arguments."""
    raw = f"{prefix}:" + ":".join(str(a) for a in args)
    if len(raw) > 200:
        hashed = hashlib.md5(raw.encode()).hexdigest()
        return f"{prefix}:{hashed}"
    return raw


class CacheService:
    """Unified caching with stale fallback — never returns empty to users."""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get a cached value."""
        try:
            redis = await _get_redis()
            if redis is not None:
                val = await redis.get(key)
                if val is not None:
                    return json.loads(val)
                return None
            else:
                dc = _get_disk_cache()
                return dc.get(key, default=None)
        except Exception as exc:
            logger.warning(f"Cache get error for {key}: {exc}")
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value + save permanent backup for stale fallback."""
        try:
            redis = await _get_redis()
            if redis is not None:
                serialized = json.dumps(value, ensure_ascii=False, default=str)
                if ttl:
                    await redis.setex(key, ttl, serialized)
                else:
                    await redis.set(key, serialized)
                backup = json.dumps({"data": value, "saved_at": time.time()}, ensure_ascii=False, default=str)
                await redis.set(f"backup:{key}", backup)
                return True
            else:
                dc = _get_disk_cache()
                dc.set(key, value, expire=ttl)
                dc.set(f"backup:{key}", {"data": value, "saved_at": time.time()})
                return True
        except Exception as exc:
            logger.warning(f"Cache set error for {key}: {exc}")
            return False

    @staticmethod
    async def get_stale(key: str) -> Optional[dict]:
        """Get stale backup data when all APIs fail. Returns {data, saved_at, stale: True}."""
        try:
            redis = await _get_redis()
            if redis is not None:
                val = await redis.get(f"backup:{key}")
                if val is not None:
                    backup = json.loads(val)
                    backup["stale"] = True
                    backup["age_minutes"] = int((time.time() - backup.get("saved_at", 0)) / 60)
                    return backup
            else:
                dc = _get_disk_cache()
                backup = dc.get(f"backup:{key}", default=None)
                if backup is not None:
                    backup["stale"] = True
                    backup["age_minutes"] = int((time.time() - backup.get("saved_at", 0)) / 60)
                    return backup
        except Exception as exc:
            logger.warning(f"Stale cache error for {key}: {exc}")
        return None

    @staticmethod
    async def delete(key: str) -> bool:
        """Delete a cached value."""
        try:
            redis = await _get_redis()
            if redis is not None:
                await redis.delete(key)
            else:
                dc = _get_disk_cache()
                dc.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"Cache delete error for {key}: {exc}")
            return False

    @staticmethod
    async def get_or_set(key: str, factory, ttl: Optional[int] = None) -> Any:
        """Get cached value or compute and cache it."""
        cached = await CacheService.get(key)
        if cached is not None:
            return cached
        value = await factory() if callable(factory) else factory
        await CacheService.set(key, value, ttl=ttl)
        return value

    @staticmethod
    async def clear_prefix(prefix: str) -> int:
        """Clear all keys with a given prefix."""
        count = 0
        try:
            redis = await _get_redis()
            if redis is not None:
                async for key in redis.scan_iter(f"{prefix}*"):
                    await redis.delete(key)
                    count += 1
            else:
                dc = _get_disk_cache()
                for key in list(dc):
                    if isinstance(key, str) and key.startswith(prefix):
                        dc.delete(key)
                        count += 1
        except Exception as exc:
            logger.warning(f"Cache clear_prefix error for {prefix}: {exc}")
        return count

    @staticmethod
    async def close() -> None:
        """Close cache connections."""
        global _redis_client, _disk_cache
        try:
            if _redis_client is not None:
                await _redis_client.close()
                _redis_client = None
            if _disk_cache is not None:
                _disk_cache.close()
                _disk_cache = None
            logger.info("Cache connections closed")
        except Exception as exc:
            logger.warning(f"Error closing cache: {exc}")


cache = CacheService()


class AdminAlert:
    """Layer 3: Send alerts to admin when APIs fail repeatedly."""

    _failed_sources: dict = {}
    _alerted: set = set()
    _bot = None

    @classmethod
    def set_bot(cls, bot) -> None:
        cls._bot = bot

    @classmethod
    async def report_failure(cls, source_name: str) -> None:
        """Report an API failure. Alerts admin after 3 consecutive failures."""
        from config import settings
        count = cls._failed_sources.get(source_name, 0) + 1
        cls._failed_sources[source_name] = count

        if count >= 3 and source_name not in cls._alerted:
            cls._alerted.add(source_name)
            logger.warning(f"[ALERT] {source_name} failed {count} times consecutively")
            if cls._bot and settings.admin_id_list:
                try:
                    for admin_id in settings.admin_id_list:
                        await cls._bot.send_message(
                            admin_id,
                            f"⚠️ **{source_name}** failed {count} times\nFallbacks active — users not affected"
                        )
                except Exception as exc:
                    logger.debug(f"Admin alert send error: {exc}")

    @classmethod
    async def report_success(cls, source_name: str) -> None:
        """Report API recovery. Alerts admin that service is back."""
        from config import settings
        if source_name in cls._alerted:
            cls._alerted.discard(source_name)
            cls._failed_sources.pop(source_name, None)
            logger.info(f"[RECOVERED] {source_name} is back online")
            if cls._bot and settings.admin_id_list:
                try:
                    for admin_id in settings.admin_id_list:
                        await cls._bot.send_message(admin_id, f"✅ **{source_name}** recovered")
                except Exception as exc:
                    logger.debug(f"Admin recovery alert error: {exc}")
        else:
            cls._failed_sources.pop(source_name, None)

    @classmethod
    def get_status(cls) -> dict:
        return {"failed": dict(cls._failed_sources), "alerted": list(cls._alerted)}


admin_alert = AdminAlert
