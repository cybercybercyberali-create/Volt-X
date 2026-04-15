import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_football import omega_football, MAJOR_LEAGUES
from config import t

logger = logging.getLogger(__name__)
router = Router(name="football")

_BEIRUT = ZoneInfo("Asia/Beirut")


def _fmt_local(date_utc: str) -> str:
    try:
        dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00"))
        return dt.astimezone(_BEIRUT).strftime("%H:%M")
    except Exception:
        return "—"


def _score_display(f: dict) -> str:
    if f["status"] == "NS":
        return "🆚"
    h = f.get("home_score")
    a = f.get("away_score")
    return f"‹ {h if h is not None else '?'} - {a if a is not None else '?'} ›"


def _status_line(f: dict) -> str:
    s = f.get("status", "NS")
    el = f.get("status_elapsed")
    if s == "NS":   return "🗓️ موعد"
    if s in ("1H", "2H"): return f"🔴 مباشر '{el}"
    if s == "HT":   return "⏸️ استراحة"
    if s == "FT":   return "🏁 انتهت"
    if s == "ET":   return "⚡ وقت إضافي"
    if s == "PEN":  return "🎯 ضربات ترجيح"
    return s


def _card(f: dict) -> str:
    return (
        f"⚽ {f['league_ar']}\n\n"
        f"{f['home']}\n"
        f"{_score_display(f)}\n"
        f"{f['away']}\n\n"
        f"{_status_line(f)}\n"
        f"🏟️ {f.get('venue') or '—'}\n"
        f"🕙 {_fmt_local(f.get('date_utc', ''))} (بيروت)"
    )


def _league_kb() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text=info["name_ar"], callback_data=f"fb:{code}")
        for code, info in MAJOR_LEAGUES.items()
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton(text="🔴 نتائج مباشرة", callback_data="fb:live")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _today(fixtures: list) -> list:
    today = datetime.now(timezone.utc).date().isoformat()
    return [f for f in fixtures if f.get("date_utc", "").startswith(today)]


def _nearest(fixtures: list) -> list:
    upcoming = sorted([f for f in fixtures if f.get("status") == "NS"], key=lambda f: f.get("date_utc",""))
    if upcoming:
        return upcoming[:8]
    return sorted([f for f in fixtures if f.get("status") == "FT"], key=lambda f: f.get("date_utc",""), reverse=True)[:8]


async def _send_fixtures(target, league_code: str, lang: str) -> None:
    send = target.answer if isinstance(target, Message) else target.message.answer
    data = await omega_football.get_fixtures(league_code)
    if isinstance(data, dict) and data.get("error"):
        await send(t("error", lang))
        return
    selection = _today(data) or _nearest(data)
    if not selection:
        await send(t("fb_no_live", lang))
        return
    for f in selection[:8]:
        await send(_card(f), parse_mode="Markdown")


async def _send_live(target, lang: str) -> None:
    send = target.answer if isinstance(target, Message) else target.message.answer
    data = await omega_football.get_live()
    if isinstance(data, dict) and data.get("error"):
        await send(t("fb_no_live", lang))
        return
    if not data:
        await send(t("fb_no_live", lang))
        return
    for f in data[:8]:
        await send(_card(f), parse_mode="Markdown")


@router.message(Command("football"))
async def cmd_football(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(t("fb_choose_league", lang), parse_mode="Markdown", reply_markup=_league_kb())
        return
    arg = args[0].upper()
    if arg == "LIVE":
        await _send_live(message, lang)
    elif arg in MAJOR_LEAGUES:
        await _send_fixtures(message, arg, lang)
    else:
        await message.answer(t("not_found", lang))


@router.callback_query(lambda c: c.data and c.data.startswith("fb:"))
async def handle_fb_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    parts = callback.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    if action == "live":
        await _send_live(callback, lang)
    elif action.upper() in MAJOR_LEAGUES:
        await _send_fixtures(callback, action.upper(), lang)


def register_football_handlers(dp) -> None:
    dp.include_router(router)
