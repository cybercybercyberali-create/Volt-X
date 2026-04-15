import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_crypto import omega_crypto
from services.cards import crypto_card
from config import t

logger = logging.getLogger(__name__)
router = Router(name="crypto")


@router.message(Command("crypto"))
async def cmd_crypto(message: Message, lang: str = "en") -> None:
    coin = message.text.replace("/crypto", "").strip().lower() if message.text else ""
    if not coin:
        # Show top 10 as a compact list card
        data = await omega_crypto.get_top_coins(10)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        sep = "━━━━━━━━━━━━━━"
        title = "₿ *أفضل 10 عملات رقمية*" if lang == "ar" else "₿ *Top 10 Crypto*"
        lines = [title, sep]
        for c in data["coins"]:
            emoji = "📈" if (c.get("change_24h") or 0) >= 0 else "📉"
            lines.append(f"*#{c['rank']}* {c['symbol']} — *${c['price']:,.2f}* {emoji} {c.get('change_24h', 0):+.1f}%")
        await message.answer("\n".join(lines), parse_mode="Markdown")
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_crypto.get_price(coin)
        if data.get("error"):
            await message.answer(t("not_found", lang))
            return
        await message.answer(crypto_card(data, lang), parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Crypto error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_crypto_handlers(dp) -> None:
    dp.include_router(router)
