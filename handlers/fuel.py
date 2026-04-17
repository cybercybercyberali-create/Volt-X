import logging
import httpx
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_fuel import omega_fuel
from config import t, settings
from services.cards import fuel_card

logger = logging.getLogger(__name__)
router = Router(name="fuel")

# BDL official rate fixed at 89,500 LBP/USD since Feb 2023.
# Valid range check: if scraped value is outside 80,000–150,000 it's rejected.
_FALLBACK_RATE = 89500.0  # LBP per 1 USD — BDL official (Feb 2023 onwards)

# Canonical Arabic names for the 4 fuel types shown on the card
_FUEL_KEYS = {
    "98":                                              "بنزين 98",
    "95":                                              "بنزين 95",
    "diesel|ديزل|مازوت|mazout|gasoil|gas oil":         "ديزل",
    "gas|غاز|lpg|butane|gaz":                          "غاز 10kg",
}


_CANONICAL_LB_KEYS = {"بنزين 98", "بنزين 95", "ديزل", "غاز 10kg"}


def _has_canonical_prices(d: dict) -> bool:
    """Return True only when at least 2 canonical Lebanon fuel keys are present."""
    return sum(1 for k in d if k in _CANONICAL_LB_KEYS) >= 2


def _normalize_fuel_keys(prices: dict) -> dict:
    """Map any scraped key names to standard Arabic canonical names."""
    out: dict = {}
    for raw_key, val in prices.items():
        kl = raw_key.lower()
        matched = False
        for patterns_str, canonical in _FUEL_KEYS.items():
            if canonical in out:          # already set by a better match
                continue
            for p in patterns_str.split("|"):
                if p in kl or p in raw_key:
                    out[canonical] = val
                    matched = True
                    break
            if matched:
                break
        if not matched:
            out[raw_key] = val            # keep as-is if no mapping found
    return out


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


# ── Country selector ──────────────────────────────────────────────────────────
_FUEL_COUNTRIES = [
    ("🇱🇧 لبنان",      "LB"), ("🇸🇦 السعودية",  "SA"), ("🇦🇪 الإمارات",  "AE"),
    ("🇪🇬 مصر",        "EG"), ("🇰🇼 الكويت",    "KW"), ("🇶🇦 قطر",       "QA"),
    ("🇯🇴 الأردن",     "JO"), ("🇮🇶 العراق",    "IQ"), ("🇩🇿 الجزائر",   "DZ"),
    ("🇲🇦 المغرب",     "MA"), ("🇹🇳 تونس",      "TN"), ("🇹🇷 تركيا",     "TR"),
    ("🇺🇸 USA",        "US"), ("🇩🇪 Germany",   "DE"), ("🇫🇷 France",    "FR"),
    ("🇬🇧 UK",         "GB"), ("🇯🇵 Japan",     "JP"), ("🇮🇳 India",     "IN"),
    ("🇧🇷 Brazil",     "BR"), ("🇷🇺 Russia",    "RU"), ("🇨🇳 China",     "CN"),
]


def _fuel_country_kb(lang: str = "ar") -> InlineKeyboardMarkup:
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    btns = [
        InlineKeyboardButton(text=name, callback_data=f"fuel_c:{code}")
        for name, code in _FUEL_COUNTRIES
    ]
    rows = [btns[i:i+3] for i in range(0, len(btns), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_fuel(send_to: Message, country: str, lang: str) -> None:
    """Core fuel display — shared by command and callback."""
    await send_to.answer(t("fetching", lang))
    try:
        data = await omega_fuel.get_prices(country)

        # ── Lebanon: rich visual card ─────────────────────────────────────────
        if country == "LB":
            from datetime import date as _date
            prices_raw = data.get("prices", {}) if not data.get("error") else {}
            rate = await _fetch_exchange_rate()
            source_label = "IPT Group"
            ago = "—"

            # Published date from scraper (e.g. "17 أبريل 2026") or scraped_at timestamp
            published_date = data.get("published_date", "")
            scraped_at     = data.get("scraped_at", "")
            if published_date:
                ago = f"تحديث: {published_date}"
            elif scraped_at:
                try:
                    from datetime import datetime as _dt, timezone as _tz
                    dt = _dt.fromisoformat(scraped_at)
                    _MONTHS_AR = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                                  "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
                    ago = f"تحديث: {dt.day} {_MONTHS_AR[dt.month-1]} {dt.year}"
                except Exception:
                    pass

            lbp_prices = {
                k: v for k, v in prices_raw.items()
                if k != "note"
                and any(c.isdigit() for c in str(v))
                and any(m in str(v) for m in ("ل.ل", "LL", "LBP", "لل"))
            }
            prices_real = _normalize_fuel_keys(lbp_prices)

            if not _has_canonical_prices(prices_real):
                gpp_prices = {k: v for k, v in prices_raw.items()
                              if k != "note" and "USD" in str(v)
                              and any(c.isdigit() for c in str(v))}
                if gpp_prices and rate:
                    import re as _re
                    raw_converted = {}
                    for fuel_name, usd_str in gpp_prices.items():
                        m = _re.search(r"([\d.]+)", usd_str)
                        if m:
                            usd_per_l = float(m.group(1))
                            llp_20l = int(usd_per_l * rate * 20)
                            raw_converted[fuel_name] = f"{llp_20l:,} ل.ل."
                    converted = _normalize_fuel_keys(raw_converted)
                    if _has_canonical_prices(converted):
                        prices_real = converted
                        source_label = "GlobalPetrolPrices"

            if not _has_canonical_prices(prices_real):
                # Static fallback — compute last Saturday (IPT updates Saturdays)
                today = _date.today()
                days_since_sat = (today.weekday() - 5) % 7
                last_sat = today.replace(day=today.day - days_since_sat) if days_since_sat else today
                _MONTHS_AR = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                              "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
                last_sat_ar = f"{last_sat.day} {_MONTHS_AR[last_sat.month-1]} {last_sat.year}"
                prices_real = {
                    "بنزين 98": "2,427,000 ل.ل.",
                    "بنزين 95": "2,386,000 ل.ل.",
                    "ديزل":     "2,495,000 ل.ل.",
                    "غاز 10kg": "1,751,000 ل.ل.",
                }
                source_label = "IPT Group"
                ago = f"آخر معروف: {last_sat_ar} ⚠️"

            card_text = fuel_card(
                prices_llp=prices_real,
                rate=rate,
                lang=lang,
                source=source_label,
                ago=ago,
            )
            await send_to.answer(card_text, parse_mode="Markdown")
            return

        # ── Other countries: simple display ──────────────────────────────────
        if data.get("error"):
            await send_to.answer(t("error", lang))
            return

        name = data.get("country_name_ar", data.get("country_name_en", country))
        text = t("fuel_title_country", lang, country=name) + "\n\n"
        prices = data.get("prices", {})
        if isinstance(prices, dict):
            for fuel_type, price in prices.items():
                if fuel_type != "note":
                    text += f"  🔹 {fuel_type}: {price}\n"
        if data.get("stale"):
            text += (
                "\n⚠️ _آخر بيانات معروفة — أبريل 2026_"
                if lang == "ar"
                else "\n⚠️ _Last known data — April 2026_"
            )
        if data.get("note"):
            text += f"\n{t('label_note', lang)}: {data['note']}"
        await send_to.answer(text, parse_mode="Markdown")

    except Exception as exc:
        logger.error(f"Fuel error for {country}: {exc}", exc_info=True)
        await send_to.answer(t("error", lang))


@router.message(Command("fuel"))
async def cmd_fuel(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    country = None
    if args:
        candidate = args[0].upper()
        if len(candidate) == 2 and candidate.isalpha():
            country = candidate

    if not country:
        prompt = "⛽ *اختر الدولة:*" if lang == "ar" else "⛽ *Select a country:*"
        await message.answer(prompt, parse_mode="Markdown", reply_markup=_fuel_country_kb(lang))
        return

    await _show_fuel(message, country, lang)


@router.callback_query(lambda c: c.data and c.data.startswith("fuel_c:"))
async def handle_fuel_country_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    country = callback.data.split(":", 1)[1].upper()
    await _show_fuel(callback.message, country, lang)


def register_fuel_handlers(dp) -> None:
    dp.include_router(router)
