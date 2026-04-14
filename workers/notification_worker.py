import logging
import asyncio
from typing import Optional

from config import IS_PAID

logger = logging.getLogger(__name__)


class NotificationWorker:
    """Background worker for proactive notifications (paid plan only)."""

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self, bot) -> None:
        """Start the notification worker."""
        if not IS_PAID:
            logger.info("Notification worker skipped (free plan)")
            return

        self._running = True
        self._task = asyncio.create_task(self._run(bot))
        logger.info("Notification worker started")

    async def stop(self) -> None:
        """Stop the notification worker."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Notification worker stopped")

    async def _run(self, bot) -> None:
        """Main worker loop."""
        while self._running:
            try:
                await self._check_price_alerts(bot)
                await self._check_match_notifications(bot)
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Notification worker error: {exc}", exc_info=True)
                await asyncio.sleep(30)

    async def _check_price_alerts(self, bot) -> None:
        """Check crypto/stock price alerts."""
        try:
            from database.connection import get_session
            from sqlalchemy import select
            from database.models import TrackedCoin
            from api_clients.omega_crypto import omega_crypto

            async with get_session() as session:
                result = await session.execute(select(TrackedCoin))
                tracked = result.scalars().all()

                for coin in tracked:
                    if coin.alert_price_above or coin.alert_price_below:
                        data = await omega_crypto.get_price(coin.coin_id)
                        if data.get("error"):
                            continue
                        price = data.get("price", 0)
                        if coin.alert_price_above and price >= coin.alert_price_above:
                            await bot.send_message(
                                coin.user_id,
                                f"🚨 {coin.coin_symbol} reached ${price:,.2f} (above ${coin.alert_price_above:,.2f})"
                            )
                        if coin.alert_price_below and price <= coin.alert_price_below:
                            await bot.send_message(
                                coin.user_id,
                                f"🚨 {coin.coin_symbol} dropped to ${price:,.2f} (below ${coin.alert_price_below:,.2f})"
                            )
        except Exception as exc:
            logger.debug(f"Price alert check error: {exc}")

    async def _check_match_notifications(self, bot) -> None:
        """Check football match notifications."""
        pass


notification_worker = NotificationWorker()
