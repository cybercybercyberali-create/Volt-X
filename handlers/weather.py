import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_weather import omega_weather
from config import t

logger = logging.getLogger(__name__)
router = Router(name="weather")


@router.message(Command("weather"))
async def cmd_weather(message: Message, lang: str = "en") -> None:
    city = message.text.replace("/weather", "").strip() if message.text else ""
    if not city:
        city = "Beirut"  # default to Beirut if no city given

    await message.answer(t("fetching", lang))
    try:
        data = await omega_weather.get_weather(city, lang)
        if data.get("error"):
            await message.answer(t("error", lang))
            return

        text = f"🌤 **{data.get('city', city)}**\n\n"
        text += f"🌡 {t('label_temp', lang)}: {data['temperature']}°C\n"
        text += f"🤔 {t('label_feels', lang)}: {data.get('feels_like', 'N/A')}°C\n"
        text += f"💧 {t('label_humidity', lang)}: {data.get('humidity', 'N/A')}%\n"
        text += f"💨 {t('label_wind', lang)}: {data.get('wind_speed', 'N/A')} km/h\n"
        if data.get("description"):
            text += f"📝 {data['description']}\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Weather error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_weather_handlers(dp) -> None:
    dp.include_router(router)
