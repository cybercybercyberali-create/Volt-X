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
    query = message.text.replace("/stock", "", 1).strip() if message.text else ""
    if not query:
        hint = "📈 أرسل اسم الشركة أو رمز السهم\nمثال: /stock ابل  أو  /stock AAPL" if lang == "ar" \
            else "📈 Send a company name or ticker\nExample: /stock Apple  or  /stock AAPL"
        await message.answer(hint)
        return

    try:
        data = await omega_stocks.get_quote(query)
        if data.get("error"):
            msg = f"❌ البيانات غير متوفرة حالياً من المصادر الحية\nالرمز: `{query}`" if lang == "ar" \
                else f"❌ No live data available for `{query}`"
            await message.answer(msg, parse_mode="Markdown")
            return
        await message.answer(stock_card(data, lang), parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Stock error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_stocks_handlers(dp) -> None:
    dp.include_router(router)
