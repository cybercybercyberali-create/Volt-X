import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_fuel import omega_fuel
from config import t

logger = logging.getLogger(__name__)
router = Router(name="fuel")


@router.message(Command("fuel"))
async def cmd_fuel(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    # Only accept a valid 2-letter country code; ignore natural language words
    country = "LB"
    if args:
        candidate = args[0].upper()
        if len(candidate) == 2 and candidate.isalpha():
            country = candidate

    await message.answer(t("fetching", lang))
    try:
        data = await omega_fuel.get_prices(country)
        if data.get("error"):
            await message.answer(t("error", lang))
            return

        name = data.get("country_name_ar", data.get("country_name_en", country))
        text = t("fuel_title_country", lang, country=name) + "\n\n"

        prices = data.get("prices", {})
        if isinstance(prices, dict):
            for fuel_type, price in prices.items():
                if fuel_type != "note":
                    text += f"  🔹 {fuel_type}: {price}\n"

        if data.get("note"):
            text += f"\n{t('label_note', lang)}: {data['note']}"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Fuel error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_fuel_handlers(dp) -> None:
    dp.include_router(router)
