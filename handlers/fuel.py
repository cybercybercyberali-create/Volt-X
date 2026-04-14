import logging
import httpx
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_fuel import omega_fuel
from config import t, settings
from services.cards import fuel_card

logger = logging.getLogger(__name__)
router = Router(name="fuel")

_FALLBACK_RATE = 89700.0  # LBP per 1 USD fallback


async def _fetch_exchange_rate() -> float:
    """Fetch USD→LBP rate from exchangerate-api.com. Returns fallback on failure."""
    key = getattr(settings, "exchange_rate_key", "") or ""
    if key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                url = f"https://v6.exchangerate-api.com/v6/{key}/pair/USD/LBP"
                resp = await client.get(url)
                resp.raise_for_status()
                js = resp.json()
                rate = float(js.get("conversion_rate", 0))
                if rate > 10000:
                    return rate
        except Exception as exc:
            logger.debug(f"Exchange rate fetch failed: {exc}")
    return _FALLBACK_RATE


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

        # ── Lebanon: render the rich visual card ──────────────────────────────
        if country == "LB":
            prices_raw = data.get("prices", {}) if not data.get("error") else {}

            # Fetch LBP/USD rate
            rate = await _fetch_exchange_rate()

            # Determine data age / source
            source_label = "IPT Group"
            ago = "—"
            if data.get("error") or not prices_raw:
                # Use hard-coded fallback prices so we always show a card
                prices_raw = {
                    "بنزين 98": "504,000 ل.ل.",
                    "بنزين 95": "490,000 ل.ل.",
                    "ديزل":     "459,000 ل.ل.",
                    "غاز 10kg": "370,000 ل.ل.",
                }
                ago = "N/A"

            card_text = fuel_card(
                prices_llp=prices_raw,
                rate=rate,
                lang=lang,
                source=source_label,
                ago=ago,
            )
            await message.answer(card_text, parse_mode="Markdown")
            return

        # ── Other countries: simple plain display ─────────────────────────────
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
