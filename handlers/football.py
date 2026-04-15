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


def _card_kb(f: dict) -> InlineKeyboardMarkup | None:
    """Show events button only for started/finished matches."""
    fid = f.get("fixture_id")
    if fid and f.get("status") not in ("NS", "TBD"):
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📋 أحداث المباراة", callback_data=f"fb_ev:{fid}")
        ]])
    return None


def _fmt_events(events: list) -> str:
    """Format match events into a readable card."""
    if not events:
        return "لا توجد أحداث مسجلة بعد"
    lines: list[str] = []
    for ev in events:
        ev_type = ev.get("type", "")
        detail  = ev.get("detail", "")
        elapsed = ev.get("elapsed", "?")
        extra   = ev.get("extra")
        player  = ev.get("player", "")
        team    = ev.get("team", "")
        time_str = f"`{elapsed}+{extra}'`" if extra else f"`{elapsed}'`"

        if ev_type == "Goal":
            if "Own Goal" in detail:
                icon = "🔙"
            elif "Penalty" in detail:
                icon = "🎯"
            else:
                icon = "⚽"
        elif ev_type == "Card":
            icon = "🟥" if "Red" in detail else "🟨"
        elif ev_type in ("subst", "Subst"):
            icon = "🔄"
        else:
            icon = "📌"

        line = f"  {icon} {time_str} *{player}*"
        if team:
            line += f"  _{team}_"
        lines.append(line)

    return "📋 *أحداث المباراة*\n\n" + "\n".join(lines)


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
        kb = _card_kb(f)
        await send(_card(f), parse_mode="Markdown", reply_markup=kb)


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
        kb = _card_kb(f)
        await send(_card(f), parse_mode="Markdown", reply_markup=kb)


@router.message(Command("football"))
async def cmd_football(message: Message, lang: str = "en") -> None:
    # Strip /football prefix or any button label text, keep only the arg
    raw = (message.text or "").strip()
    # Remove /football command prefix or keyboard button text
    for prefix in ("/football", "⚽ كرة قدم", "⚽ Football", "⚽"):
        if raw.upper().startswith(prefix.upper()):
            raw = raw[len(prefix):].strip()
            break
    arg = raw.upper()

    if not arg:
        # Show league selector
        await message.answer(t("fb_choose_league", lang), parse_mode="Markdown", reply_markup=_league_kb())
        return
    if arg == "LIVE":
        await _send_live(message, lang)
    elif arg in MAJOR_LEAGUES:
        await _send_fixtures(message, arg, lang)
    else:
        # Unknown arg — show selector instead of "not found"
        await message.answer(t("fb_choose_league", lang), parse_mode="Markdown", reply_markup=_league_kb())


@router.callback_query(lambda c: c.data and c.data.startswith("fb:"))
async def handle_fb_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    parts = callback.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    if action == "live":
        await _send_live(callback, lang)
    elif action.upper() in MAJOR_LEAGUES:
        await _send_fixtures(callback, action.upper(), lang)


@router.callback_query(lambda c: c.data and c.data.startswith("fb_ev:"))
async def handle_fb_events_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    try:
        fixture_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        return
    events = await omega_football.get_events(fixture_id)
    if isinstance(events, dict) and events.get("error"):
        await callback.message.answer(t("error", lang))
        return
    text = _fmt_events(events if isinstance(events, list) else [])
    await callback.message.answer(text, parse_mode="Markdown")


def register_football_handlers(dp) -> None:
    dp.include_router(router)
