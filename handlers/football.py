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

_MONTHS_AR = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]


# ── date helpers ───────────────────────────────────────────────────────────────

def _fmt_local(date_utc: str) -> str:
    try:
        dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00"))
        return dt.astimezone(_BEIRUT).strftime("%H:%M")
    except Exception:
        return "—"


def _fmt_full(date_utc: str, lang: str = "ar") -> str:
    try:
        dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00")).astimezone(_BEIRUT)
        if lang == "ar":
            return f"{dt.day} {_MONTHS_AR[dt.month - 1]}  {dt.strftime('%H:%M')}"
        return dt.strftime("%d %b  %H:%M")
    except Exception:
        return "—"


def _fmt_short_date(date_utc: str) -> str:
    try:
        dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00")).astimezone(_BEIRUT)
        return f"{dt.day:02d}/{dt.month:02d}"
    except Exception:
        return "—"


# ── match card helpers ─────────────────────────────────────────────────────────

def _score_display(f: dict) -> str:
    if f["status"] == "NS":
        return "🆚"
    h = f.get("home_score")
    a = f.get("away_score")
    return f"‹ {h if h is not None else '?'} - {a if a is not None else '?'} ›"


def _status_line(f: dict, lang: str = "ar") -> str:
    s = f.get("status", "NS")
    el = f.get("status_elapsed")
    if lang == "ar":
        if s == "NS":              return "🗓️ موعد"
        if s in ("1H", "2H"):     return f"🔴 مباشر '{el}"
        if s == "HT":             return "⏸️ استراحة"
        if s == "FT":             return "🏁 انتهت"
        if s == "ET":             return "⚡ وقت إضافي"
        if s == "PEN":            return "🎯 ضربات ترجيح"
    else:
        if s == "NS":              return "🗓️ Scheduled"
        if s in ("1H", "2H"):     return f"🔴 Live '{el}"
        if s == "HT":             return "⏸️ Half Time"
        if s == "FT":             return "🏁 Finished"
        if s == "ET":             return "⚡ Extra Time"
        if s == "PEN":            return "🎯 Penalties"
    return s


def _card(f: dict, lang: str = "ar") -> str:
    return (
        f"⚽ {f['league_ar']}\n\n"
        f"{f['home']}\n"
        f"{_score_display(f)}\n"
        f"{f['away']}\n\n"
        f"{_status_line(f, lang)}\n"
        f"🏟️ {f.get('venue') or '—'}\n"
        f"🕙 {_fmt_local(f.get('date_utc', ''))} (Beirut)"
    )


def _card_kb(f: dict) -> InlineKeyboardMarkup | None:
    fid = f.get("fixture_id")
    if fid and f.get("status") not in ("NS", "TBD"):
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📋 أحداث | Events", callback_data=f"fb_ev:{fid}")
        ]])
    return None


def _fmt_events(events: list) -> str:
    if not events:
        return "لا توجد أحداث | No events recorded"
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
            icon = "🔙" if "Own Goal" in detail else ("🎯" if "Penalty" in detail else "⚽")
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

    return "📋 *Match Events*\n\n" + "\n".join(lines)


# ── keyboards ──────────────────────────────────────────────────────────────────

def _league_kb(lang: str = "ar") -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text=info["name_ar"], callback_data=f"fb:{code}")
        for code, info in MAJOR_LEAGUES.items()
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    live_lbl = "🔴 نتائج مباشرة" if lang == "ar" else "🔴 Live Now"
    rows.append([InlineKeyboardButton(text=live_lbl, callback_data="fb:live")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _team_kb(teams: list, league_code: str, lang: str = "ar") -> InlineKeyboardMarkup:
    """Use index (0-based) as callback data — stays within 64-byte limit."""
    btns = [
        InlineKeyboardButton(
            text=tm["name"],
            callback_data=f"fb_t:{i}:{league_code}",
        )
        for i, tm in enumerate(teams[:24])
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    back_lbl = "🔙 الدوريات" if lang == "ar" else "🔙 Leagues"
    rows.append([InlineKeyboardButton(text=back_lbl, callback_data="fb:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── team schedule card ─────────────────────────────────────────────────────────

def _result_emoji(f: dict, team_name: str) -> str:
    if f.get("status") != "FT":
        return "⬜"
    h, a = f.get("home_score"), f.get("away_score")
    if h is None or a is None:
        return "⬜"
    is_home = f.get("home", "") == team_name
    my_g = h if is_home else a
    op_g = a if is_home else h
    if my_g > op_g:   return "🟢"
    if my_g == op_g:  return "🟡"
    return "🔴"


def _team_schedule_card(sched: dict, team_name: str, league_ar: str, lang: str = "ar") -> str:
    SEP = "━━━━━━━━━━━━"
    lines = [f"⚽ *{league_ar}*", f"🏆 *{team_name}*", SEP]

    if sched.get("live"):
        lbl = "🔴 *مباشر الآن*" if lang == "ar" else "🔴 *Live Now*"
        lines.append(lbl)
        for f in sched["live"]:
            el = f.get("status_elapsed", "")
            el_str = f"  `{el}'`" if el else ""
            h_s = f.get("home_score", 0)
            a_s = f.get("away_score", 0)
            lines.append(f"  *{f['home']}*  {h_s} — {a_s}  *{f['away']}*{el_str}")
        lines.append(SEP)

    if sched.get("past"):
        lbl = "📅 *الأخيرة*" if lang == "ar" else "📅 *Recent*"
        lines.append(lbl)
        for f in sched["past"]:
            res = _result_emoji(f, team_name)
            h_s = f.get("home_score", "?")
            a_s = f.get("away_score", "?")
            d   = _fmt_short_date(f.get("date_utc", ""))
            lines.append(f"{res}  `{d}`  {f['home']}  {h_s}–{a_s}  {f['away']}")
        lines.append(SEP)

    if sched.get("upcoming"):
        lbl = "📆 *القادمة*" if lang == "ar" else "📆 *Upcoming*"
        lines.append(lbl)
        for f in sched["upcoming"]:
            dt = _fmt_full(f.get("date_utc", ""), lang)
            lines.append(f"⬜  {f['home']}  🆚  {f['away']}")
            lines.append(f"     `{dt}`")

    if not any(sched.get(k) for k in ("past", "live", "upcoming")):
        no_data = "لا توجد بيانات متاحة" if lang == "ar" else "No data available"
        lines.append(no_data)

    return "\n".join(lines)


# ── internal send helpers ──────────────────────────────────────────────────────

def _today(fixtures: list) -> list:
    today = datetime.now(timezone.utc).date().isoformat()
    return [f for f in fixtures if f.get("date_utc", "").startswith(today)]


def _nearest(fixtures: list) -> list:
    upcoming = sorted(
        [f for f in fixtures if f.get("status") == "NS"],
        key=lambda f: f.get("date_utc", ""),
    )
    if upcoming:
        return upcoming[:8]
    return sorted(
        [f for f in fixtures if f.get("status") == "FT"],
        key=lambda f: f.get("date_utc", ""),
        reverse=True,
    )[:8]


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
        await send(_card(f, lang), parse_mode="Markdown", reply_markup=kb)


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
        await send(_card(f, lang), parse_mode="Markdown", reply_markup=kb)


# ── command handler ────────────────────────────────────────────────────────────

@router.message(Command("football"))
async def cmd_football(message: Message, lang: str = "en") -> None:
    raw = (message.text or "").strip()
    for prefix in ("/football", "⚽ كرة قدم", "⚽ Football", "⚽"):
        if raw.upper().startswith(prefix.upper()):
            raw = raw[len(prefix):].strip()
            break
    arg = raw.upper()

    if not arg:
        await message.answer(
            t("fb_choose_league", lang), parse_mode="Markdown",
            reply_markup=_league_kb(lang),
        )
        return
    if arg == "LIVE":
        await _send_live(message, lang)
    elif arg in MAJOR_LEAGUES:
        await _send_fixtures(message, arg, lang)
    else:
        await message.answer(
            t("fb_choose_league", lang), parse_mode="Markdown",
            reply_markup=_league_kb(lang),
        )


# ── callback: league / live / back ────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb:"))
async def handle_fb_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    parts  = callback.data.split(":")
    action = parts[1] if len(parts) > 1 else ""

    if action == "live":
        await _send_live(callback, lang)
        return

    if action == "menu":
        try:
            await callback.message.edit_text(
                t("fb_choose_league", lang),
                parse_mode="Markdown",
                reply_markup=_league_kb(lang),
            )
        except Exception:
            await callback.message.answer(
                t("fb_choose_league", lang),
                parse_mode="Markdown",
                reply_markup=_league_kb(lang),
            )
        return

    league_code = action.upper()
    if league_code not in MAJOR_LEAGUES:
        return

    league_ar = MAJOR_LEAGUES[league_code]["name_ar"]
    teams = await omega_football.get_league_teams(league_code)

    if teams:
        choose_lbl = "🏟️ اختر الفريق:" if lang == "ar" else "🏟️ Choose a team:"
        text = f"⚽ *{league_ar}*\n\n{choose_lbl}"
        try:
            await callback.message.edit_text(
                text, parse_mode="Markdown",
                reply_markup=_team_kb(teams, league_code, lang),
            )
        except Exception:
            await callback.message.answer(
                text, parse_mode="Markdown",
                reply_markup=_team_kb(teams, league_code, lang),
            )
    else:
        await _send_fixtures(callback, league_code, lang)


# ── callback: team schedule ───────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb_t:"))
async def handle_fb_team_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    try:
        team_idx    = int(parts[1])
        league_code = parts[2].upper()
    except (ValueError, IndexError):
        return

    league_ar = MAJOR_LEAGUES.get(league_code, {}).get("name_ar", league_code)

    teams = await omega_football.get_league_teams(league_code)
    if team_idx >= len(teams):
        await callback.message.answer(t("error", lang))
        return
    team_name = teams[team_idx]["name"]

    sched = await omega_football.get_team_schedule_by_name(team_name, league_code)
    card  = _team_schedule_card(sched, team_name, league_ar, lang)

    back_lbl   = "🔙 الفرق"  if lang == "ar" else "🔙 Teams"
    reload_lbl = "🔄 تحديث"  if lang == "ar" else "🔄 Refresh"
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=back_lbl,   callback_data=f"fb:{league_code.lower()}"),
        InlineKeyboardButton(text=reload_lbl, callback_data=f"fb_t:{team_idx}:{league_code}"),
    ]])
    await callback.message.answer(card, parse_mode="Markdown", reply_markup=back_kb)


# ── callback: match events ─────────────────────────────────────────────────────

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
