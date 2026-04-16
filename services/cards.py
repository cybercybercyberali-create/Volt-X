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

    def _fmt_llp(val_str: str) -> str:
        """Return clean LBP string from raw value like '2,460,000 ل.ل.'"""
        v = _parse_llp(val_str)
        if v:
            return f"{v:,.0f} ل.ل."
        return str(val_str)

    def _usd_20l(llp_price: float) -> str:
        if rate and rate > 0:
            usd = llp_price / rate
            return f"≈ ${usd:.2f} / 20L"
        return ""

    def _usd_10kg(llp_price: float) -> str:
        if rate and rate > 0:
            usd = llp_price / rate
            return f"≈ ${usd:.2f}"
        return ""

    def _fuel_line(emoji: str, label_ar: str, label_en: str,
                   key_ar: str, key_en: str, is_20l: bool) -> str:
        """Build one fuel price line, always showing LBP value."""
        # Try canonical Arabic key first, then any key containing the hint
        val_str = (prices_llp.get(key_ar)
                   or next((v for k, v in prices_llp.items()
                            if key_en.lower() in k.lower() or key_ar in k), None))
        if val_str:
            v = _parse_llp(str(val_str))
            llp_display = _fmt_llp(str(val_str))
            usd_display = (_usd_20l(v) if is_20l else _usd_10kg(v)) if v else ""
            return f"• {emoji} {label_en if lang != 'ar' else label_ar}:  {llp_display}  {usd_display}".rstrip()
        return f"• {emoji} {label_en if lang != 'ar' else label_ar}:  {'غير متاح' if lang == 'ar' else 'N/A'}"

    today = datetime.now().strftime("%Y-%m-%d")

    if lang == "ar":
        title = "⛽ *أسعار المحروقات — لبنان* 🇱🇧"
        date_line = f"📅 {today}"
        rate_line = f"💱 سعر الصرف: 1$ = {rate:,.0f} ل.ل." if rate else "💱 سعر الصرف: غير متاح"
        footer = f"🔄 منذ {ago} | {source}"
        lines = [title, date_line, ""]
        lines.append(_fuel_line("🔵", "بنزين 98", "Benzin 98", "بنزين 98", "98", True))
        lines.append(_fuel_line("🔵", "بنزين 95", "Benzin 95", "بنزين 95", "95", True))
        lines.append(_fuel_line("⚫", "ديزل",     "Diesel",    "ديزل",     "diesel", True))
        lines.append(_fuel_line("🟠", "غاز (10kg)", "Gas (10kg)", "غاز 10kg", "gas", False))
        lines.extend(["", rate_line, footer])
    else:
        title = "⛽ *Lebanon Fuel Prices* 🇱🇧"
        date_line = f"📅 {today}"
        rate_line = f"💱 Exchange Rate: 1$ = {rate:,.0f} LBP" if rate else "💱 Exchange Rate: unavailable"
        footer = f"🔄 {ago} ago | {source}"
        lines = [title, date_line, ""]
        lines.append(_fuel_line("🔵", "بنزين 98", "Benzin 98", "بنزين 98", "98", True))
        lines.append(_fuel_line("🔵", "بنزين 95", "Benzin 95", "بنزين 95", "95", True))
        lines.append(_fuel_line("⚫", "ديزل",     "Diesel",    "ديزل",     "diesel", True))
        lines.append(_fuel_line("🟠", "غاز (10kg)", "Gas (10kg)", "غاز 10kg", "gas", False))
        lines.extend(["", rate_line, footer])

    return "\n".join(lines)


# ── weather card ─────────────────────────────────────────────────────────────

def weather_card(data: dict, lang: str) -> str:
    """Format weather data into a visual card."""
    from datetime import datetime as _dt
    city        = data.get("city", "")
    country     = data.get("country", "")
    temp        = data.get("temperature", "N/A")
    feels       = data.get("feels_like", "N/A")
    humidity    = data.get("humidity", "N/A")
    wind        = data.get("wind_speed", "N/A")
    wind_dir    = data.get("wind_direction", "")
    precip      = data.get("precipitation")
    sunrise     = data.get("sunrise", "")
    sunset      = data.get("sunset", "")
    description = data.get("description", "")
    observed_at = data.get("observed_at", "")
    is_stale    = data.get("stale", False)

    # Format observation timestamp → "HH:MM"
    obs_str = ""
    if observed_at:
        try:
            obs_str = _dt.fromisoformat(observed_at.replace("Z", "+00:00")).strftime("%H:%M")
        except Exception:
            obs_str = observed_at[:16] if len(observed_at) >= 16 else observed_at

    sep      = _sep()
    location = f"{city}, {country}" if country else city

    # Wind direction: convert degrees to compass label
    def _compass(deg) -> str:
        try:
            d = float(deg)
            dirs = ["N","NE","E","SE","S","SW","W","NW"]
            return dirs[int((d + 22.5) / 45) % 8]
        except Exception:
            return str(deg) if deg else ""

    wind_label = _compass(wind_dir) if wind_dir else ""

    if lang == "ar":
        lines = [
            f"{description or '🌤'} *{location}*",
            sep,
            f"🌡 *{temp}°C*  •  يُحسّ كـ {feels}°C",
            f"💧 الرطوبة: {humidity}%   💨 الرياح: {wind} كم/س {wind_label}",
        ]
        if precip is not None and float(precip) > 0:
            lines.append(f"🌧 هطول: {precip} مم")
        if sunrise and sunset:
            lines.append(f"🌅 {sunrise}  |  🌇 {sunset}")
        stale_note = " _(بيانات قديمة)_" if is_stale else ""
        ts_line = f"🕐 آخر تحديث: {obs_str}{stale_note}" if obs_str else ("⚠️ _(بيانات قديمة)_" if is_stale else "")
        if ts_line:
            lines.append(ts_line)
    else:
        lines = [
            f"{description or '🌤'} *{location}*",
            sep,
            f"🌡 *{temp}°C*  •  feels like {feels}°C",
            f"💧 Humidity: {humidity}%   💨 Wind: {wind} km/h {wind_label}",
        ]
        if precip is not None and float(precip) > 0:
            lines.append(f"🌧 Precipitation: {precip} mm")
        if sunrise and sunset:
            lines.append(f"🌅 {sunrise}  |  🌇 {sunset}")
        stale_note = " _(stale)_" if is_stale else ""
        ts_line = f"🕐 Updated: {obs_str}{stale_note}" if obs_str else ("⚠️ _(stale data)_" if is_stale else "")
        if ts_line:
            lines.append(ts_line)

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
