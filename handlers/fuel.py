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

# BDL official rate fixed at 89,500 LBP/USD since Feb 2023.
# Valid range check: if scraped value is outside 80,000–150,000 it's rejected.
_FALLBACK_RATE = 89500.0  # LBP per 1 USD — BDL official (Feb 2023 onwards)


async def _fetch_exchange_rate() -> float:
    """Fetch live USD→LBP rate. Tries 3 sources in order, falls back to BDL official."""
    import re as _re

    # Source 1: ExchangeRate-API (uses EXCHANGE_RATE_KEY)
    key = getattr(settings, "exchange_rate_key", "") or ""
    if key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                url = f"https://v6.exchangerate-api.com/v6/{key}/pair/USD/LBP"
                resp = await client.get(url)
                resp.raise_for_status()
                js = resp.json()
                rate = float(js.get("conversion_rate", 0))
                if 80000 < rate < 150000:
                    logger.debug(f"LBP rate from exchangerate-api: {rate}")
                    return rate
        except Exception as exc:
            logger.debug(f"ExchangeRate-API failed: {exc}")

    # Source 2: lirarate.org (live Lebanese market rate, no key needed)
    try:
        async with httpx.AsyncClient(
            timeout=8.0,
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
        ) as client:
            resp = await client.get("https://lirarate.org/")
            resp.raise_for_status()
            # Look for large numbers like 89,500 or 89500 in the page text
            nums = _re.findall(r'\b(8[0-9][,\s]?\d{3})\b', resp.text)
            for n in nums:
                try:
                    r = float(n.replace(",", "").replace(" ", ""))
                    if 80000 < r < 150000:
                        logger.debug(f"LBP rate from lirarate.org: {r}")
                        return r
                except ValueError:
                    pass
    except Exception as exc:
        logger.debug(f"lirarate.org failed: {exc}")

    # Source 3: Open-source free API (no key)
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get("https://open.er-api.com/v6/latest/USD")
            resp.raise_for_status()
            js = resp.json()
            rate = float(js.get("rates", {}).get("LBP", 0))
            if 80000 < rate < 150000:
                logger.debug(f"LBP rate from open.er-api: {rate}")
                return rate
    except Exception as exc:
        logger.debug(f"open.er-api failed: {exc}")

    logger.info(f"Using BDL fallback rate: {_FALLBACK_RATE}")
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
            # Filter out non-price meta keys like "note"
            prices_real = {k: v for k, v in prices_raw.items()
                           if k != "note" and any(c.isdigit() for c in str(v))}

            # Fetch LBP/USD rate
            rate = await _fetch_exchange_rate()

            source_label = "IPT Group"
            ago = "—"
            if not prices_real:
                # Fallback: last verified IPT Group weekly prices
                prices_real = {
                    "بنزين 98": "2,460,000 ل.ل.",
                    "بنزين 95": "2,376,000 ل.ل.",
                    "ديزل":     "2,442,000 ل.ل.",
                    "غاز 10kg": "980,000 ل.ل.",
                }
                source_label = "IPT Group (آخر بيانات)"
                ago = "غير محدد"

            card_text = fuel_card(
                prices_llp=prices_real,
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
