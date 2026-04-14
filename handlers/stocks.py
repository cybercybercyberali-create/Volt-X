import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_stocks import omega_stocks
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

        change_emoji = "📈" if (data.get("change", 0) or 0) >= 0 else "📉"
        text = f"📊 **{data.get('name', symbol)} ({data['symbol']})**\n\n"
        text += f"{t('label_price', lang)}: ${data.get('price', 0):,.2f}\n"
        text += f"{change_emoji} {t('label_change', lang)}: {data.get('change', 0):+,.2f} ({data.get('change_percent', 0):+.2f}%)\n"
        text += f"{t('label_volume', lang)}: {data.get('volume', 0):,}\n"
        if data.get("market_cap"):
            text += f"{t('label_mcap', lang)}: ${data['market_cap']:,.0f}\n"
        if data.get("pe_ratio"):
            text += f"📐 P/E: {data['pe_ratio']:.2f}\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Stock error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_stocks_handlers(dp) -> None:
    dp.include_router(router)
