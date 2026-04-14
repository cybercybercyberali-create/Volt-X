import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_weather import omega_weather
from services.cards import weather_card
from config import t

logger = logging.getLogger(__name__)
router = Router(name="weather")


@router.message(Command("weather"))
async def cmd_weather(message: Message, lang: str = "en") -> None:
    city = message.text.replace("/weather", "").strip() if message.text else ""
    if not city:
        city = "Beirut"

    await message.answer(t("fetching", lang))
    try:
        data = await omega_weather.get_weather(city, lang)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        await message.answer(weather_card(data, lang), parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Weather error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_weather_handlers(dp) -> None:
    dp.include_router(router)
