import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import settings, RENDER_PLAN, IS_FREE, AI_MODELS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher(storage=MemoryStorage())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info(f"🚀 Omega Bot starting — Plan: {RENDER_PLAN}, Models: {len(AI_MODELS)}")

    from database.connection import init_db
    await init_db()
    logger.info("✅ Database initialized")

    from handlers import register_all_handlers
    register_all_handlers(dp)
    logger.info("✅ Handlers registered")

    from middlewares import LoggingMiddleware, RateLimitMiddleware, UserTrackerMiddleware, SecurityMiddleware
    # Message middlewares
    dp.message.middleware(SecurityMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(UserTrackerMiddleware())
    dp.message.middleware(LoggingMiddleware())
    # Callback middlewares (so buttons get lang too)
    dp.callback_query.middleware(UserTrackerMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    logger.info("✅ Middlewares registered")

    from handlers.ai_chat import process_ai_query
    @dp.message(lambda m: m.text is not None and not m.text.startswith("/"))
    async def catch_all_messages(message, lang: str = "en"):
        await process_ai_query(message, message.text, lang=lang)

    # Resolve webhook URL: prefer explicit setting, fallback to Render's auto URL
    _webhook_url = settings.webhook_url or (
        os.environ.get("RENDER_EXTERNAL_URL", "") + "/webhook"
        if os.environ.get("RENDER_EXTERNAL_URL") else ""
    )
    if _webhook_url:
        await bot.set_webhook(
            url=_webhook_url,
            drop_pending_updates=True,
        )
        logger.info(f"✅ Webhook set: {_webhook_url}")

    if IS_FREE:
        asyncio.create_task(_self_ping())
        logger.info("✅ Self-ping task started (free plan)")

    from workers.notification_worker import notification_worker
    await notification_worker.start(bot)

    from services.cache_service import AdminAlert
    AdminAlert.set_bot(bot)

    logger.info("🟢 Omega Bot is LIVE!")

    yield

    logger.info("Shutting down...")
    from workers.notification_worker import notification_worker
    await notification_worker.stop()

    from services.omega_query_engine import query_engine
    await query_engine.close()

    from services.cache_service import cache
    await cache.close()

    from database.connection import close_db
    await close_db()

    await bot.session.close()
    logger.info("🔴 Omega Bot stopped")


app = FastAPI(title="Omega Bot", lifespan=lifespan)


@app.post("/webhook")
async def webhook_handler(request: Request) -> Response:
    """Handle incoming Telegram webhook updates."""
    try:
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot=bot, update=update)
        return Response(status_code=200)
    except Exception as exc:
        logger.error(f"Webhook error: {exc}", exc_info=True)
        return Response(status_code=200)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import psutil
    ram = psutil.virtual_memory()
    return {
        "status": "healthy",
        "plan": RENDER_PLAN,
        "models": len(AI_MODELS),
        "ram_percent": ram.percent,
        "db": "sqlite" if IS_FREE else "postgresql",
    }


@app.get("/")
async def root():
    return {"message": "Omega Bot is running!", "plan": RENDER_PLAN}


async def _self_ping():
    """Ping the external URL every 4 minutes to prevent Render free tier from sleeping."""
    import httpx
    await asyncio.sleep(30)  # wait for server to fully start first
    while True:
        try:
            # Use external URL so Render counts it as real traffic
            external_url = os.environ.get("RENDER_EXTERNAL_URL", "")
            if external_url:
                ping_url = f"{external_url}/health"
            else:
                ping_url = f"http://127.0.0.1:{settings.port}/health"
            async with httpx.AsyncClient(timeout=10) as client:
                await client.get(ping_url)
                logger.debug(f"Self-ping OK: {ping_url}")
        except Exception:
            pass
        await asyncio.sleep(240)  # every 4 minutes
