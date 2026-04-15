"""Visual card formatters for all Omega Bot services.

Each function returns a Markdown-formatted string with emojis and bold prices.
All functions accept a `lang` parameter ("ar" | "en").
"""
from datetime import datetime
from typing import Optional


# ── helpers ──────────────────────────────────────────────────────────────────

def _sep() -> str:
    return "━━━━━━━━━━━━━━"


def _dir(lang: str) -> str:
    """Return RLM prefix for Arabic text in Telegram."""
    return "\u200F" if lang == "ar" else ""


# ── fuel card ────────────────────────────────────────────────────────────────

def fuel_card(
    prices_llp: dict,
    rate: float,
    lang: str,
    source: str,
    ago: str,
) -> str:
    """Format Lebanon fuel prices card.

    prices_llp: dict keyed by Arabic fuel name → "XXX,XXX ل.ل." strings.
    rate: LBP per 1 USD (e.g. 89700).
    lang: "ar" or "en".
    source: source label string.
    ago: human-readable age string like "5 دقائق" or "5 minutes".
    """
    import re

    def _parse_llp(val: str) -> Optional[float]:
        """Extract numeric LBP value from string."""
        m = re.search(r"([\d,]+)", str(val))
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                pass
        return None

    def _usd_20l(llp_price: float) -> str:
        if rate and rate > 0:
            usd = llp_price / rate
            usd_l = usd / 20
            return f"{usd:.2f}$ / 20L  →  {usd_l:.2f}$ / L"
        return "N/A"

    def _usd_10kg(llp_price: float) -> str:
        if rate and rate > 0:
            usd = llp_price / rate
            return f"{usd:.2f}$"
        return "N/A"

    today = datetime.now().strftime("%Y-%m-%d")

    if lang == "ar":
        title = "⛽ *أسعار المحروقات — لبنان* 🇱🇧"
        date_line = f"📅 {today}"
        rate_line = f"💱 سعر الصرف: 1$ = {rate:,.0f} ل.ل." if rate else "💱 سعر الصرف: غير متاح"
        footer = f"🔄 منذ {ago} | {source}"

        lines = [title, date_line, ""]

        # Benzin 98
        key98 = next((k for k in prices_llp if "98" in k), None)
        val98 = _parse_llp(prices_llp[key98]) if key98 else None
        lines.append(f"• 🔵 بنزين 98:  {_usd_20l(val98) if val98 else 'غير متاح'}")

        # Benzin 95
        key95 = next((k for k in prices_llp if "95" in k), None)
        val95 = _parse_llp(prices_llp[key95]) if key95 else None
        lines.append(f"• 🔵 بنزين 95:  {_usd_20l(val95) if val95 else 'غير متاح'}")

        # Diesel
        keyd = next((k for k in prices_llp if "ديزل" in k or "diesel" in k.lower() or "مازوت" in k), None)
        vald = _parse_llp(prices_llp[keyd]) if keyd else None
        lines.append(f"• ⚫ ديزل:      {_usd_20l(vald) if vald else 'غير متاح'}")

        # Gas 10kg
        keyg = next((k for k in prices_llp if "غاز" in k or "gas" in k.lower()), None)
        valg = _parse_llp(prices_llp[keyg]) if keyg else None
        lines.append(f"• 🟠 غاز (10kg): {_usd_10kg(valg) if valg else 'غير متاح'}")

        lines.extend(["", rate_line, footer])
    else:
        title = "⛽ *Lebanon Fuel Prices* 🇱🇧"
        date_line = f"📅 {today}"
        rate_line = f"💱 Exchange Rate: 1$ = {rate:,.0f} LBP" if rate else "💱 Exchange Rate: unavailable"
        footer = f"🔄 {ago} ago | {source}"

        lines = [title, date_line, ""]

        key98 = next((k for k in prices_llp if "98" in k), None)
        val98 = _parse_llp(prices_llp[key98]) if key98 else None
        lines.append(f"• 🔵 Benzin 98:  {_usd_20l(val98) if val98 else 'N/A'}")

        key95 = next((k for k in prices_llp if "95" in k), None)
        val95 = _parse_llp(prices_llp[key95]) if key95 else None
        lines.append(f"• 🔵 Benzin 95:  {_usd_20l(val95) if val95 else 'N/A'}")

        keyd = next((k for k in prices_llp if "ديزل" in k or "diesel" in k.lower() or "مازوت" in k), None)
        vald = _parse_llp(prices_llp[keyd]) if keyd else None
        lines.append(f"• ⚫ Diesel:      {_usd_20l(vald) if vald else 'N/A'}")

        keyg = next((k for k in prices_llp if "غاز" in k or "gas" in k.lower()), None)
        valg = _parse_llp(prices_llp[keyg]) if keyg else None
        lines.append(f"• 🟠 Gas (10kg):  {_usd_10kg(valg) if valg else 'N/A'}")

        lines.extend(["", rate_line, footer])

    return "\n".join(lines)


# ── weather card ─────────────────────────────────────────────────────────────

def weather_card(data: dict, lang: str) -> str:
    """Format weather data into a visual card."""
    city = data.get("city", "")
    country = data.get("country", "")
    temp = data.get("temperature", "N/A")
    feels = data.get("feels_like", "N/A")
    humidity = data.get("humidity", "N/A")
    wind = data.get("wind_speed", "N/A")
    wind_dir = data.get("wind_direction", "")
    sunrise = data.get("sunrise", "")
    sunset = data.get("sunset", "")
    description = data.get("description", "")

    sep = _sep()

    if lang == "ar":
        location = f"{city}, {country}" if country else city
        lines = [
            f"🌤 *{location}*",
            sep,
            f"🌡 درجة الحرارة: *{temp}°C* (يُحسّ كـ {feels}°C)",
            f"💧 الرطوبة: *{humidity}%*",
            f"💨 الرياح: *{wind} كم/س* {wind_dir}",
        ]
        if sunrise and sunset:
            lines.append(f"🌅 الشروق: {sunrise} | الغروب: {sunset}")
        if description:
            lines.append(f"📊 الحالة: {description}")
    else:
        location = f"{city}, {country}" if country else city
        lines = [
            f"🌤 *{location}*",
            sep,
            f"🌡 Temperature: *{temp}°C* (feels like {feels}°C)",
            f"💧 Humidity: *{humidity}%*",
            f"💨 Wind: *{wind} km/h* {wind_dir}",
        ]
        if sunrise and sunset:
            lines.append(f"🌅 Sunrise: {sunrise} | Sunset: {sunset}")
        if description:
            lines.append(f"📊 Condition: {description}")

    return "\n".join(lines)


# ── gold card ─────────────────────────────────────────────────────────────────

def gold_card(data: dict, lang: str) -> str:
    """Format precious metals prices into a visual card."""
    sep = _sep()
    xau = data.get("price_per_ounce", 0)
    xag = data.get("silver_per_ounce", 0)
    xpt = data.get("platinum_per_ounce", 0)
    gram = xau / 31.1035 if xau else 0
    change = data.get("change_24h_pct", None)
    change_str = f"{change:+.2f}%" if change is not None else "N/A"
    change_emoji = "📈" if (change or 0) >= 0 else "📉"

    if lang == "ar":
        lines = [
            "🥇 *أسعار الذهب والمعادن*",
            sep,
            f"💛 ذهب 24K: *${xau:,.2f}* / أونصة",
            f"   *${gram:,.2f}* / غرام",
        ]
        if xag:
            lines.append(f"🥈 فضة:    *${xag:,.2f}* / أونصة")
        if xpt:
            lines.append(f"🔘 بلاتين: *${xpt:,.2f}* / أونصة")
        lines.append(f"{change_emoji} تغيير 24س: *{change_str}*")
    else:
        lines = [
            "🥇 *Gold & Precious Metals*",
            sep,
            f"💛 Gold 24K: *${xau:,.2f}* / oz",
            f"   *${gram:,.2f}* / gram",
        ]
        if xag:
            lines.append(f"🥈 Silver:   *${xag:,.2f}* / oz")
        if xpt:
            lines.append(f"🔘 Platinum: *${xpt:,.2f}* / oz")
        lines.append(f"{change_emoji} 24h Change: *{change_str}*")

    return "\n".join(lines)


# ── crypto card ───────────────────────────────────────────────────────────────

def crypto_card(data: dict, lang: str) -> str:
    """Format cryptocurrency data into a visual card."""
    sep = _sep()
    name = data.get("name", "")
    symbol = data.get("symbol", "")
    price = data.get("price", 0)
    change_24h = data.get("change_24h", 0) or 0
    change_7d = data.get("change_7d", None)
    rank = data.get("rank", "N/A")
    mcap = data.get("market_cap", 0) or 0
    emoji = "📈" if change_24h >= 0 else "📉"

    if lang == "ar":
        lines = [
            f"₿ *{name} ({symbol})*",
            sep,
            f"💰 السعر: *${price:,.2f}*",
            f"{emoji} 24س: *{change_24h:+.2f}%*",
        ]
        if change_7d is not None:
            lines.append(f"📊 7 أيام: *{change_7d:+.2f}%*")
        lines.append(f"🏆 الترتيب: *#{rank}*")
        if mcap:
            lines.append(f"💎 القيمة السوقية: *${mcap:,.0f}*")
    else:
        lines = [
            f"₿ *{name} ({symbol})*",
            sep,
            f"💰 Price: *${price:,.2f}*",
            f"{emoji} 24h: *{change_24h:+.2f}%*",
        ]
        if change_7d is not None:
            lines.append(f"📊 7d: *{change_7d:+.2f}%*")
        lines.append(f"🏆 Rank: *#{rank}*")
        if mcap:
            lines.append(f"💎 Market Cap: *${mcap:,.0f}*")

    return "\n".join(lines)


# ── stock card ────────────────────────────────────────────────────────────────

def stock_card(data: dict, lang: str) -> str:
    """Format stock quote data into a visual card."""
    sep = _sep()
    name        = data.get("name", "") or data.get("symbol", "")
    symbol      = data.get("symbol", "")
    price       = data.get("price", 0) or 0
    change      = data.get("change", 0) or 0
    change_pct  = data.get("change_percent", 0) or 0
    try:
        change_pct = float(str(change_pct).replace("%",""))
    except Exception:
        change_pct = 0.0
    volume      = data.get("volume", 0) or 0
    mcap        = data.get("market_cap", 0) or 0
    pe          = data.get("pe_ratio", None)
    exchange    = data.get("exchange", "") or ""
    updated     = data.get("last_updated", "") or ""
    stale       = data.get("stale", False)
    emoji       = "📈" if change >= 0 else "📉"

    if lang == "ar":
        lines = [
            f"📊 *{name}*",
            f"🏷️ `{symbol}`" + (f"  |  🏦 {exchange}" if exchange else ""),
            sep,
            f"💰 السعر: *${price:,.2f}*",
            f"{emoji} التغيير: *{change:+,.2f}  ({change_pct:+.2f}%)*",
        ]
        if volume:
            lines.append(f"📦 الحجم: {volume:,}")
        if mcap:
            lines.append(f"💎 القيمة السوقية: ${mcap:,.0f}")
        if pe:
            lines.append(f"📐 P/E: {pe:.2f}")
        lines.append(sep)
        note = "⚠️ آخر سعر معروف" if stale else "🟢 بيانات حية"
        lines.append(f"🕐 {updated}  {note}" if updated else note)
    else:
        lines = [
            f"📊 *{name}*",
            f"🏷️ `{symbol}`" + (f"  |  🏦 {exchange}" if exchange else ""),
            sep,
            f"💰 Price: *${price:,.2f}*",
            f"{emoji} Change: *{change:+,.2f}  ({change_pct:+.2f}%)*",
        ]
        if volume:
            lines.append(f"📦 Volume: {volume:,}")
        if mcap:
            lines.append(f"💎 Market Cap: ${mcap:,.0f}")
        if pe:
            lines.append(f"📐 P/E: {pe:.2f}")
        lines.append(sep)
        note = "⚠️ Last known price" if stale else "🟢 Live"
        lines.append(f"🕐 {updated}  {note}" if updated else note)

    return "\n".join(lines)


# ── currency card ─────────────────────────────────────────────────────────────

def currency_card(data: dict, base: str, lang: str) -> str:
    """Format currency exchange rates into a visual card."""
    sep = _sep()
    rates = data.get("rates", {})
    updated = data.get("updated", "")

    DISPLAY_CURRENCIES = [
        ("USD", "🇺🇸", "دولار", "Dollar"),
        ("EUR", "🇪🇺", "يورو", "Euro"),
        ("GBP", "🇬🇧", "جنيه", "Pound"),
        ("AED", "🇦🇪", "درهم", "Dirham"),
        ("SAR", "🇸🇦", "ريال سعودي", "SAR"),
        ("TRY", "🇹🇷", "ليرة تركية", "TRY"),
        ("LBP", "🇱🇧", "ل.ل.", "LBP"),
        ("EGP", "🇪🇬", "جنيه مصري", "EGP"),
    ]

    if lang == "ar":
        lines = [f"💱 *أسعار العملات — أساس: {base}*", sep]
        for code, flag, name_ar, _ in DISPLAY_CURRENCIES:
            if code == base:
                continue
            rate = rates.get(code)
            if rate is not None:
                lines.append(f"{flag} {name_ar}: *{rate:,.4f}*")
    else:
        lines = [f"💱 *Currency Rates — Base: {base}*", sep]
        for code, flag, _, name_en in DISPLAY_CURRENCIES:
            if code == base:
                continue
            rate = rates.get(code)
            if rate is not None:
                lines.append(f"{flag} {name_en}: *{rate:,.4f}*")

    if updated:
        lines.append(f"\n🕐 Updated: {updated}")

    return "\n".join(lines)
