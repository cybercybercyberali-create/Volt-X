import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_flights import omega_flights
from config import t

logger = logging.getLogger(__name__)
router = Router(name="flights")


@router.message(Command("flight"))
async def cmd_flight(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/flight", "").strip().upper() if message.text else ""
    if not query:
        await message.answer(t("flight_send", lang))
        return

    await message.answer(t("fetching", lang))
    try:
        if len(query) == 4 and query.isalpha():
            data = await omega_flights.get_flights_by_airport(query)
            if data.get("error"):
                await message.answer(t("not_found", lang))
                return
            text = f"✈️ *{query}*\n\n"
            text += f"{t('label_departures', lang)} ({len(data['departures'])}):\n"
            for f in data["departures"][:5]:
                text += f"  {f['callsign']} → {f['arrival']}\n"
            text += f"\n{t('label_arrivals', lang)} ({len(data['arrivals'])}):\n"
            for f in data["arrivals"][:5]:
                text += f"  {f['callsign']} ← {f['departure']}\n"
        else:
            data = await omega_flights.track_flight(query)
            if data.get("error"):
                await message.answer(t("not_found", lang))
                return
            text = f"✈️ *{data['callsign']}*\n\n"
            text += f"🌍 {data.get('origin_country', 'N/A')}\n"
            text += f"📍 {data.get('latitude', 0):.2f}, {data.get('longitude', 0):.2f}\n"
            text += f"{t('label_altitude', lang)}: {data.get('altitude', 0):,.0f}m\n"
            text += f"{t('label_speed', lang)}: {data.get('velocity', 0):,.0f}m/s\n"
            text += f"{t('label_heading', lang)}: {data.get('heading', 0):.0f}°\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Flight error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_flights_handlers(dp) -> None:
    dp.include_router(router)
