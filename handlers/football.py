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


def _league_name(code: str, lang: str) -> str:
    """Return the league display name in the user's language."""
    info = MAJOR_LEAGUES.get(code.upper(), {})
    if lang == "ar":
        return info.get("name_ar") or info.get("name") or code
    return info.get("name") or info.get("name_ar") or code


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


# ── match overview card (all matches in one message) ──────────────────────────

def _matchday_card(fixtures: list, league_name: str, lang: str = "ar") -> str:
    """Format all matches as a single matchday overview — like football sites."""
    SEP  = "──────────────"
    live = [f for f in fixtures if f.get("status") in ("1H", "2H", "HT", "ET", "PEN")]
    done = [f for f in fixtures if f.get("status") == "FT"]
    ns   = [f for f in fixtures if f.get("status") == "NS"]

    lines = [f"⚽ *{league_name}*", SEP]

    if live:
        lbl = "🔴 *مباشر*" if lang == "ar" else "🔴 *Live*"
        lines.append(lbl)
        for f in live:
            el   = f.get("status_elapsed", "")
            tag  = f"  `{el}'`" if el else ""
            h, a = f.get("home_score", 0), f.get("away_score", 0)
            lines.append(f"  {f['home']}  `{h} – {a}`  {f['away']}{tag}")
        lines.append(SEP)

    if done:
        lbl = "🏁 *انتهت*" if lang == "ar" else "🏁 *Finished*"
        lines.append(lbl)
        for f in done:
            h, a = f.get("home_score", "?"), f.get("away_score", "?")
            lines.append(f"  {f['home']}  `{h} – {a}`  {f['away']}")
        lines.append(SEP)

    if ns:
        lbl = "🗓️ *المواعيد*" if lang == "ar" else "🗓️ *Scheduled*"
        lines.append(lbl)
        for f in ns:
            time_s = _fmt_local(f.get("date_utc", ""))
            date_s = _fmt_short_date(f.get("date_utc", ""))
            lines.append(f"  `{date_s}  {time_s}`  {f['home']}  🆚  {f['away']}")

    if not (live or done or ns):
        lines.append("لا توجد مباريات متاحة" if lang == "ar" else "No matches available")

    return "\n".join(lines)


def _matchday_kb(league_code: str, lang: str = "ar") -> InlineKeyboardMarkup:
    lc          = league_code.lower()
    team_lbl    = "🔍 اختر فريقاً" if lang == "ar" else "🔍 Choose Team"
    live_lbl    = "🔴 مباشر"       if lang == "ar" else "🔴 Live Now"
    refresh_lbl = "🔄 تحديث"       if lang == "ar" else "🔄 Refresh"
    back_lbl    = "🔙 الدوريات"    if lang == "ar" else "🔙 Leagues"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=team_lbl,    callback_data=f"fb_teams:{lc}")],
        [InlineKeyboardButton(text=live_lbl,    callback_data="fb:live"),
         InlineKeyboardButton(text=refresh_lbl, callback_data=f"fb:{lc}")],
        [InlineKeyboardButton(text=back_lbl,    callback_data="fb:menu")],
    ])


# ── team list keyboard ─────────────────────────────────────────────────────────

def _team_kb(teams: list, league_code: str, lang: str = "ar") -> InlineKeyboardMarkup:
    """Index-based callback — stays within 64-byte limit."""
    btns = [
        InlineKeyboardButton(
            text=tm["name"],
            callback_data=f"fb_t:{i}:{league_code}",
        )
        for i, tm in enumerate(teams[:24])
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    back_lbl = "🔙 المباريات" if lang == "ar" else "🔙 Matches"
    rows.append([InlineKeyboardButton(text=back_lbl, callback_data=f"fb:{league_code.lower()}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── league selector keyboard ───────────────────────────────────────────────────

def _league_kb(lang: str = "ar") -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text=_league_name(code, lang), callback_data=f"fb:{code}")
        for code in MAJOR_LEAGUES
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    live_lbl = "🔴 نتائج مباشرة" if lang == "ar" else "🔴 Live Now"
    rows.append([InlineKeyboardButton(text=live_lbl, callback_data="fb:live")])
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


def _team_schedule_card(sched: dict, team_name: str, league_name: str, lang: str = "ar") -> str:
    SEP = "━━━━━━━━━━━━"
    lines = [f"⚽ *{league_name}*", f"🏆 *{team_name}*", SEP]

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


# ── events card ────────────────────────────────────────────────────────────────

def _fmt_events(events: list, lang: str = "ar") -> str:
    if not events:
        return "لا توجد أحداث" if lang == "ar" else "No events recorded"
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
            line += f"  ({team})"
        lines.append(line)

    header = "📋 *أحداث المباراة*" if lang == "ar" else "📋 *Match Events*"
    return header + "\n\n" + "\n".join(lines)


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
        return upcoming[:10]
    return sorted(
        [f for f in fixtures if f.get("status") == "FT"],
        key=lambda f: f.get("date_utc", ""),
        reverse=True,
    )[:10]


async def _send_fixtures(target, league_code: str, lang: str) -> None:
    send = target.answer if isinstance(target, Message) else target.message.answer
    try:
        data = await omega_football.get_fixtures(league_code)
    except Exception as exc:
        logger.error(f"get_fixtures error {league_code}: {exc}", exc_info=True)
        data = {"error": True}
    if isinstance(data, dict) and data.get("error"):
        no_data = "لا تتوفر بيانات حالياً — اضغط تحديث" if lang == "ar" else "No data available right now — press Refresh"
        try:
            await send(no_data, reply_markup=_matchday_kb(league_code.upper(), lang))
        except Exception:
            await send(no_data)
        return
    selection = _today(data) or _nearest(data)
    if not selection:
        try:
            await send(t("fb_no_live", lang), reply_markup=_matchday_kb(league_code.upper(), lang))
        except Exception:
            await send(t("fb_no_live", lang))
        return
    league_name = _league_name(league_code, lang)
    card = _matchday_card(selection[:12], league_name, lang)
    kb   = _matchday_kb(league_code.upper(), lang)
    try:
        await send(card, parse_mode="Markdown", reply_markup=kb)
    except Exception:
        await send(card, reply_markup=kb)


async def _send_live(target, lang: str) -> None:
    send = target.answer if isinstance(target, Message) else target.message.answer
    try:
        data = await omega_football.get_live()
    except Exception as exc:
        logger.error(f"get_live error: {exc}", exc_info=True)
        await send(t("fb_no_live", lang))
        return
    if isinstance(data, dict) and data.get("error"):
        await send(t("fb_no_live", lang))
        return
    if not data:
        await send(t("fb_no_live", lang))
        return
    by_league: dict[str, list] = {}
    for f in data[:20]:
        if lang == "ar":
            key = f.get("league_ar") or f.get("league", "Football")
        else:
            key = f.get("league") or f.get("league_ar", "Football")
        by_league.setdefault(key, []).append(f)
    for league_name, matches in by_league.items():
        card = _matchday_card(matches, league_name, lang)
        try:
            await send(card, parse_mode="Markdown")
        except Exception:
            await send(card)


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

    # Always show match overview first; team list is via the "Choose Team" button
    await _send_fixtures(callback, league_code, lang)


# ── callback: team list (from matchday keyboard) ───────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb_teams:"))
async def handle_fb_teams_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    league_code = callback.data.split(":", 1)[1].upper()
    league_name = _league_name(league_code, lang)
    teams = await omega_football.get_league_teams(league_code)
    if not teams:
        no_teams = "لا توجد فرق متاحة حالياً" if lang == "ar" else "No teams available right now"
        await callback.answer(no_teams, show_alert=True)
        return
    choose_lbl = "🏟️ اختر الفريق:" if lang == "ar" else "🏟️ Choose a team:"
    text = f"⚽ *{league_name}*\n\n{choose_lbl}"
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

    league_name = _league_name(league_code, lang)

    teams = await omega_football.get_league_teams(league_code)
    if team_idx >= len(teams):
        await callback.message.answer(t("error", lang))
        return
    team_name = teams[team_idx]["name"]

    try:
        sched = await omega_football.get_team_schedule_by_name(team_name, league_code)
    except Exception as exc:
        logger.error(f"get_team_schedule_by_name error: {exc}", exc_info=True)
        await callback.message.answer(t("error", lang))
        return
    card  = _team_schedule_card(sched, team_name, league_name, lang)

    back_lbl   = "🔙 الفرق"  if lang == "ar" else "🔙 Teams"
    reload_lbl = "🔄 تحديث"  if lang == "ar" else "🔄 Refresh"
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=back_lbl,   callback_data=f"fb_teams:{league_code.lower()}"),
        InlineKeyboardButton(text=reload_lbl, callback_data=f"fb_t:{team_idx}:{league_code}"),
    ]])
    try:
        await callback.message.answer(card, parse_mode="Markdown", reply_markup=back_kb)
    except Exception:
        await callback.message.answer(card, reply_markup=back_kb)


# ── callback: match events ─────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb_ev:"))
async def handle_fb_events_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    try:
        fixture_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        return
    try:
        events = await omega_football.get_events(fixture_id)
    except Exception as exc:
        logger.error(f"get_events error: {exc}", exc_info=True)
        await callback.message.answer(t("error", lang))
        return
    if isinstance(events, dict) and events.get("error"):
        await callback.message.answer(t("error", lang))
        return
    text = _fmt_events(events if isinstance(events, list) else [], lang)
    try:
        await callback.message.answer(text, parse_mode="Markdown")
    except Exception:
        await callback.message.answer(text)


def register_football_handlers(dp) -> None:
    dp.include_router(router)
