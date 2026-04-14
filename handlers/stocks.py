import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_stocks import omega_stocks
from services.cards import stock_card
from config import t

logger = logging.getLogger(__name__)
router = Router(name="stocks")


@router.message(Command("stock"))
async def cmd_stock(message: Message, lang: str = "en") -> None:
    symbol = message.text.replace("/stock", "").strip().upper() if message.text else ""
    if not symbol:
        await message.answer(t("stock_send_symbol", lang))
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_stocks.get_quote(symbol)
        if data.get("error"):
            await message.answer(t("not_found", lang))
            return
        await message.answer(stock_card(data, lang), parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Stock error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_stocks_handlers(dp) -> None:
    dp.include_router(router)
