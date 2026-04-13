import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_currency import omega_currency
from config import t

logger = logging.getLogger(__name__)
router = Router(name="currency")


@router.message(Command("currency"))
async def cmd_currency(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    base = args[0].upper() if len(args) >= 1 else "USD"
    target = args[1].upper() if len(args) >= 2 else None

    await message.answer(t("fetching", lang))
    try:
        if target:
            data = await omega_currency.get_rate(base, target)
            if data.get("error"):
                await message.answer(t("error", lang))
                return
            text = f"💱 **{base} → {target}**\n\n"
            text += f"{t('label_price', lang)}: {data['rate']:,.6f}\n"

            if data.get("has_parallel"):
                text += f"\n{t('label_parallel', lang)}: {data['parallel_rate']:,.2f}\n"

        else:
            data = await omega_currency.get_multiple_rates(base)
            text = t("currency_rates_title", lang, base=base) + "\n\n"
            for currency, info in data.items():
                if not info.get("error"):
                    text += f"  {currency}: {info['rate']:,.4f}"
                    if info.get("has_parallel"):
                        text += f" ({t('label_parallel', lang)}: {info['parallel_rate']:,.2f})"
                    text += "\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Currency error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_currency_handlers(dp) -> None:
    dp.include_router(router)
