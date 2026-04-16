import logging
import re
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_currency import omega_currency
from config import t

logger = logging.getLogger(__name__)
router = Router(name="currency")

# ─────────────────────────── NLP currency name map ───────────────────────────
# Sorted longest-first so multi-word names match before single words.
_CURRENCY_NAMES: dict[str, str] = {
    # Arabic multi-word first
    "دولار امريكي": "USD",  "دولار أمريكي": "USD",
    "ليرة لبنانية": "LBP",  "ليرة سورية": "SYP",  "ليرة تركية": "TRY",
    "جنيه إسترليني": "GBP", "جنيه استرليني": "GBP",
    "جنيه مصري": "EGP",
    "ريال سعودي": "SAR",    "ريال قطري": "QAR",   "ريال عماني": "OMR",
    "درهم إماراتي": "AED",  "درهم اماراتي": "AED", "درهم مغربي": "MAD",
    "دينار أردني": "JOD",   "دينار اردني": "JOD",
    "دينار كويتي": "KWD",
    "دينار بحريني": "BHD",
    "دينار عراقي": "IQD",
    "فرنك سويسري": "CHF",
    "دولار كندي": "CAD",    "دولار أسترالي": "AUD", "دولار استرالي": "AUD",
    "فرنك سويسري": "CHF",
    # Arabic single-word
    "دولار": "USD",  "الدولار": "USD",
    "يورو": "EUR",   "اليورو": "EUR",
    "جنيه": "GBP",   "الجنيه": "GBP",
    "ين": "JPY",     "الين": "JPY",
    "ليرة": "LBP",   "اللبنانية": "LBP",  "ليرات": "LBP",
    "ريال": "SAR",   "السعودي": "SAR",
    "درهم": "AED",   "الاماراتي": "AED",   "الإماراتي": "AED",
    "مصري": "EGP",
    "تركي": "TRY",
    "أردني": "JOD",  "اردني": "JOD",
    "كويتي": "KWD",
    "قطري": "QAR",
    "بحريني": "BHD",
    "عماني": "OMR",
    "عراقي": "IQD",
    "سوري": "SYP",
    "مغربي": "MAD",
    "فرنك": "CHF",
    "كندي": "CAD",
    "أسترالي": "AUD", "استرالي": "AUD",
    # English names
    "dollar": "USD", "dollars": "USD",
    "euro": "EUR",   "euros": "EUR",
    "pound": "GBP",  "pounds": "GBP",
    "yen": "JPY",
    "lira": "LBP",   "lebanese": "LBP",
    "riyal": "SAR",  "saudi": "SAR",
    "dirham": "AED", "emirati": "AED",
    "franc": "CHF",  "swiss": "CHF",
    "canadian": "CAD",
    "australian": "AUD",
}

_ISO_CODES = {
    "USD","EUR","GBP","JPY","CHF","CAD","AUD",
    "LBP","SAR","AED","EGP","TRY","JOD","KWD",
    "QAR","BHD","OMR","IQD","SYP","MAD",
}


def _parse_conversion(text: str) -> dict | None:
    """
    Parse NL currency query into {base, target, amount}.
    Handles Arabic colloquial:
      "حول 100 يورو لليرة"      → EUR 100 → LBP
      "كم تساوي الليرة بالدرهم" → LBP → AED  (amount=1)
      "دولار على ليرة"          → USD → LBP
      "EUR LBP"                  → USD=EUR, target=LBP
    """
    # Extract numeric amount (Arabic & Western digits)
    ar_num = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    amount_match = re.search(r"[\d,\.]+", ar_num)
    amount = float(amount_match.group().replace(",", "")) if amount_match else 1.0

    found: list[tuple[int, str]] = []

    # Check raw ISO codes first
    for iso in _ISO_CODES:
        m = re.search(r"\b" + iso + r"\b", text, re.IGNORECASE)
        if m:
            found.append((m.start(), iso))

    # Check name map (longest names first to avoid partial matches)
    names_sorted = sorted(_CURRENCY_NAMES.keys(), key=len, reverse=True)
    for name in names_sorted:
        pattern = re.sub(r"\s+", r"\\s*", re.escape(name))
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            code = _CURRENCY_NAMES[name]
            # Skip if position already covered by a longer match
            already = any(abs(pos - m.start()) < 3 for pos, _ in found)
            if not already:
                found.append((m.start(), code))

    # Sort by position in text, deduplicate consecutive same code
    found.sort(key=lambda x: x[0])
    seen: list[tuple[int, str]] = []
    for pos, code in found:
        if not seen or seen[-1][1] != code:
            seen.append((pos, code))

    if len(seen) >= 2:
        return {"base": seen[0][1], "target": seen[1][1], "amount": amount}
    if len(seen) == 1:
        # Single currency — context decides direction
        # "ما سعر الدولار" → USD vs multi
        code = seen[0][1]
        if code == "USD":
            return None  # default multi-rate view
        return {"base": "USD", "target": code, "amount": amount}
    return None


def _stale_note(lang: str) -> str:
    return "\n\n⚠️ _البيانات الحية غير متاحة — يُعرض آخر سعر معروف_" if lang == "ar" \
        else "\n\n⚠️ _Live data unavailable — showing last known rate_"


def _fmt_rate(rate: float) -> str:
    if rate >= 1000:
        return f"{rate:,.0f}"
    if rate >= 1:
        return f"{rate:,.4f}"
    return f"{rate:,.6f}"


async def _send_pair(message: Message, base: str, target: str,
                     amount: float, lang: str) -> None:
    """Fetch and send a single currency pair card."""
    data = await omega_currency.get_rate(base, target)
    if data.get("error"):
        err = "البيانات غير متوفرة حالياً" if lang == "ar" else "Rate unavailable"
        await message.answer(f"⚠️ {err}")
        return

    rate = data["rate"]
    converted = rate * amount
    rate_str   = _fmt_rate(rate)
    conv_str   = _fmt_rate(converted)

    header = f"💱 *{base} → {target}*"
    body   = f"\n\n  1 {base} = `{rate_str}` {target}"
    if amount != 1.0:
        body += f"\n  {amount:g} {base} = `{conv_str}` {target}"

    if data.get("has_parallel") and data.get("parallel_rate"):
        par = data["parallel_rate"]
        body += f"\n\n  📊 _السوق الموازي:_ `{par:,.0f}` {target}"

    stale = _stale_note(lang) if data.get("stale") else ""
    await message.answer(header + body + stale, parse_mode="Markdown")


_QUICK_PAIRS = [
    ("USD", "LBP"), ("USD", "EUR"), ("USD", "GBP"),
    ("USD", "TRY"), ("USD", "EGP"), ("EUR", "USD"),
    ("USD", "SAR"), ("USD", "AED"),
]


def _currency_quick_kb() -> InlineKeyboardMarkup:
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    btns = [
        InlineKeyboardButton(text=f"{b}→{t}", callback_data=f"cur_q:{b}:{t}")
        for b, t in _QUICK_PAIRS
    ]
    rows = [btns[i:i+4] for i in range(0, len(btns), 4)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("currency"))
async def cmd_currency(message: Message, lang: str = "en") -> None:
    raw = message.text or ""

    # ── /currency command with explicit args ──────────────────────────────────
    if raw.strip().startswith("/currency"):
        parts = raw.split()[1:]
        base   = parts[0].upper() if len(parts) >= 1 else "USD"
        target = parts[1].upper() if len(parts) >= 2 else None
        amount = 1.0
        try:
            amount = float(parts[2]) if len(parts) >= 3 else 1.0
        except ValueError:
            pass
        if target:
            await _send_pair(message, base, target, amount, lang)
        else:
            await _send_multi(message, base, lang)
        return

    # ── Natural language ──────────────────────────────────────────────────────
    parsed = _parse_conversion(raw)
    if parsed:
        await _send_pair(message, parsed["base"], parsed["target"],
                         parsed["amount"], lang)
    else:
        # Button tap with no specific pair — show prompt + quick-select keyboard
        hint = (
            "💱 *تحويل العملات*\n\n"
            "اكتب مثال:\n"
            "  `100 دولار بيورو`\n"
            "  `USD EUR`\n"
            "  `كم يساوي الدولار بالليرة`\n\n"
            "أو اختر زوجاً سريعاً:"
            if lang == "ar"
            else
            "💱 *Currency Converter*\n\n"
            "Type e.g.:\n"
            "  `100 USD to EUR`\n"
            "  `euro to lira`\n\n"
            "Or pick a quick pair:"
        )
        await message.answer(hint, parse_mode="Markdown", reply_markup=_currency_quick_kb())


async def _send_multi(message: Message, base: str, lang: str) -> None:
    """Send multi-rate overview for a base currency."""
    data = await omega_currency.get_multiple_rates(base)
    lines: list[str] = []
    any_stale = False

    for cur, info in data.items():
        if info.get("error"):
            continue
        rate = info["rate"]
        rate_fmt   = _fmt_rate(rate)
        stale_mark = " ⚠️" if info.get("stale") else ""
        parallel   = ""
        if info.get("has_parallel") and info.get("parallel_rate"):
            parallel = f" _(موازي: {info['parallel_rate']:,.0f})_"
        lines.append(f"  `{cur}` {rate_fmt}{stale_mark}{parallel}")
        if info.get("stale"):
            any_stale = True

    if not lines:
        await message.answer(t("error", lang))
        return

    header = f"💱 *أسعار الصرف — أساس: {base}*\n\n" if lang == "ar" \
        else f"💱 *Exchange Rates — Base: {base}*\n\n"
    text = header + "\n".join(lines)
    if any_stale:
        text += _stale_note(lang)
    await message.answer(text, parse_mode="Markdown")


@router.callback_query(lambda c: c.data and c.data.startswith("cur_q:"))
async def handle_cur_quick_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    base, target = parts[1], parts[2]
    await _send_pair(callback.message, base, target, 1.0, lang)


def register_currency_handlers(dp) -> None:
    dp.include_router(router)
