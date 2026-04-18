import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import t

from config import settings, RENDER_PLAN, IS_FREE, AI_MODELS
from database.connection import get_session
from database.crud import CRUDManager
from services.circuit_breaker import circuit_breaker
from services.rate_limiter import quota

logger = logging.getLogger(__name__)
router = Router(name="stats")


@router.message(Command("stats"))
async def cmd_stats(message: Message, lang: str = "en") -> None:
    if message.from_user.id not in settings.admin_id_list:
        await message.answer(t("admin_only", lang))
        return

    try:
        async with get_session() as session:
            stats = await CRUDManager.get_stats(session)

        circuits = circuit_breaker.get_all_statuses()
        open_circuits = sum(1 for c in circuits.values() if c["state"] == "open")

        import psutil
        ram = psutil.virtual_memory()

        text = t("stats_title", lang) + "\n\n"
        text += f"{t('stats_system', lang)}:\n"
        text += f"  {t('stats_plan', lang)}: {RENDER_PLAN.upper()}\n"
        text += f"  {t('stats_models', lang)}: {len(AI_MODELS)}\n"
        text += f"  RAM: {ram.percent}%\n"
        text += f"  DB: {'SQLite' if IS_FREE else 'PostgreSQL'}\n\n"
        text += f"{t('stats_users_title', lang)}:\n"
        text += f"  {t('stats_total', lang)}: {stats['total_users']}\n"
        text += f"  {t('stats_active', lang)}: {stats['active_24h']}\n\n"
        text += f"{t('stats_perf', lang)}:\n"
        text += f"  {t('stats_searches', lang)}: {stats['total_searches']}\n"
        text += f"  {t('stats_fusions', lang)}: {stats['total_fusions']}\n"
        text += f"  {t('stats_avg_time', lang)}: {stats['avg_fusion_time_ms']}ms\n"
        text += f"  {t('stats_circuits', lang)}: {open_circuits}/{len(circuits)}\n"

        # Quota status
        text += f"\n{t('stats_quotas', lang)}:\n"
        for qs in quota.get_all_statuses():
            icon = "✅" if qs.get("remaining", 0) > 0 else "🔴"
            text += f"  {icon} {qs['name']}: {qs.get('remaining',0)}/{qs.get('limit',0)} ({qs['period']})\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Stats error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.message(Command("flushteams"))
async def cmd_flushteams(message: Message, lang: str = "en") -> None:
    if message.from_user.id not in settings.admin_id_list:
        await message.answer(t("admin_only", lang))
        return

    from services.cache_service import _get_redis, _get_disk_cache

    redis = await _get_redis()
    if redis:
        backend = f"Redis @ {settings.redis_url[:30]}..."
    else:
        backend = "diskcache (local filesystem)"
    logger.info(f"[flushteams] Cache backend: {backend}")

    keys = [
        "sfsc:league_teams:PD",  "sfsc:league_teams:PL",
        "sfsc:league_teams:SA",  "sfsc:league_teams:BL1",
        "sfsc:league_teams:FL1", "sfsc:league_teams:CL",
        "sfsc:league_teams:SPL", "sfsc:league_teams:ELC",
    ]

    deleted = []
    skipped = []
    if redis:
        for k in keys:
            existed = await redis.delete(k)
            (deleted if existed else skipped).append(k)
            await redis.delete(f"backup:{k}")
    else:
        dc = _get_disk_cache()
        for k in keys:
            existed = k in dc
            dc.delete(k)
            dc.delete(f"backup:{k}")
            (deleted if existed else skipped).append(k)

    report = (
        f"✅ *Cache flush complete*\n"
        f"Backend: `{backend}`\n"
        f"Deleted ({len(deleted)}): `{'`, `'.join(k.split(':')[-1] for k in deleted) or 'none'}`\n"
        f"Not found ({len(skipped)}): `{'`, `'.join(k.split(':')[-1] for k in skipped) or 'none'}`"
    )
    logger.info(f"[flushteams] Deleted={deleted} Skipped={skipped}")
    await message.answer(report, parse_mode="Markdown")


def register_stats_handlers(dp) -> None:
    dp.include_router(router)
