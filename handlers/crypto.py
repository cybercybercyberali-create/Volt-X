import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_crypto import omega_crypto
from config import t

logger = logging.getLogger(__name__)
router = Router(name="crypto")


@router.message(Command("crypto"))
async def cmd_crypto(message: Message, lang: str = "en") -> None:
    coin = message.text.replace("/crypto", "").strip().lower() if message.text else ""
    if not coin:
        data = await omega_crypto.get_top_coins(10)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        text = t("crypto_top_title", lang) + "\n\n"
        for c in data["coins"]:
            emoji = "📈" if (c.get("change_24h") or 0) >= 0 else "📉"
            text += f"{c['rank']}. **{c['symbol']}** — ${c['price']:,.2f} {emoji} {c.get('change_24h', 0):+.1f}%\n"
        text += "\n" + t("crypto_detail_hint", lang)
        await message.answer(text, parse_mode="Markdown")
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_crypto.get_price(coin)
        if data.get("error"):
            await message.answer(t("not_found", lang))
            return
        emoji = "📈" if (data.get("change_24h") or 0) >= 0 else "📉"
        text = f"₿ **{data['name']} ({data['symbol']})**\n\n"
        text += f"{t('label_price', lang)}: ${data['price']:,.2f}\n"
        text += f"{emoji} 24h: {data.get('change_24h', 0):+.2f}%\n"
        if data.get("change_7d"):
            text += f"📊 7d: {data['change_7d']:+.2f}%\n"
        text += f"{t('label_rank', lang)}: #{data.get('rank', 'N/A')}\n"
        text += f"{t('label_mcap', lang)}: ${data.get('market_cap', 0):,.0f}\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Crypto error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_crypto_handlers(dp) -> None:
    dp.include_router(router)
