import base64
import io
import logging
import re
import time
import urllib.parse
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict

import httpx

# ── Download-intent detection ───────────────────────────────────
_DL_KW = {"download", "تحميل", "نزل", "حمل", "حمّل", "تنزيل", "دانلود"}
_DL_DOMAINS = (
    "youtube.com", "youtu.be", "tiktok.com", "vm.tiktok.com",
    "instagram.com", "instagr.am", "twitter.com", "x.com",
    "facebook.com", "fb.watch", "vimeo.com", "reddit.com", "v.redd.it",
)

def _extract_media_url(text: str) -> Optional[str]:
    """Return first supported-platform URL found anywhere in text, or None."""
    m = re.search(r'https?://\S+', text or "")
    if not m:
        return None
    url = m.group(0).rstrip(".,;)")
    return url if any(d in url.lower() for d in _DL_DOMAINS) else None
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from services.omega_router import omega_router
from services.omega_query_engine import query_engine
from services.omega_fusion import omega_fusion
from services.omega_judge import omega_judge
from services.omega_memory import omega_memory
from services.rate_limiter import check_user_rate
from services.web_search import web_search, needs_web_search
from config import settings, t
from database.connection import get_session
from database.crud import CRUDManager

# ── Smart routing keywords ──────────────────────────────────────
_GOLD_KW    = {"ذهب", "gold", "فضة", "silver", "بلاتين", "platinum", "معادن", "metals",
               "غرام ذهب", "كيلو ذهب", "سعر ذهب", "gold price"}
_WEATHER_KW = {"طقس", "weather", "درجة حرار", "temperature", "مطر", "rain", "جو", "حرارة",
               "الطقس", "الجو", "حالة الجو", "كيف الطقس", "شو الطقس"}
_CURRENCY_KW= {"عملة", "currency", "دولار", "dollar", "يورو", "euro", "صرف", "exchange",
               "ليرة", "lira", "ريال", "riyal", "درهم", "dirham", "pound", "جنيه",
               "سعر صرف", "exchange rate", "سعر اليوم", "سعر الدولار", "سعر العملة",
               "سعر الصرف", "يعر صرف", "صرف اليوم", "الدولار اليوم", "usd", "eur",
               "كم الدولار", "كم سعر", "حول", "تحويل", "يساوي", "convert",
               "فرنك", "ين", "دينار", "فلس", "جنيه مصري"}
_FOOTBALL_KW= {"كرة قدم", "football", "مباراة", "مباريات", "دوري", "league", "هدف", "goals",
               "نتيجة", "score", "فريق", "team", "برشلونة", "ريال مدريد", "مانشستر",
               "ليفربول", "تشيلسي", "بايرن", "يوفنتوس", "دوري أبطال", "champions",
               "فيفا", "fifa", "الدوري الإنجليزي", "premier league", "laliga", "سيريا"}
_FUEL_KW    = {"بنزين", "benzin", "fuel", "محروقات", "وقود", "diesel", "ديزل", "petrol",
               "سعر البنزين", "محروقات", "بنزين 95", "بنزين 98"}
_STOCK_KW   = {"سهم", "اسهم", "stock", "stocks", "بورصة", "nasdaq", "سوق مال", "أسهم"}
_CRYPTO_KW  = {"بيتكوين", "bitcoin", "كريبتو", "crypto", "ethereum", "ايثريوم", "btc", "eth",
               "عملات رقمية", "بيتكوين"}
_NEWS_KW    = {"اخبار", "خبر", "news", "أخبار", "اخر الاخبار", "latest news"}
_MOVIE_KW   = {"فيلم", "أفلام", "افلام", "سينما", "مسلسل", "أنيمي", "أنمي",
               "movie", "movies", "film", "cinema", "series", "anime", "cartoon",
               "trending movies", "what to watch"}

# Arabic stop words to strip when extracting city from weather query
_WEATHER_STOP = {
    "طقس", "الطقس", "جو", "الجو", "حرارة", "الحرارة", "درجة", "درجات", "مطر", "المطر",
    "الطقس", "حالة", "شو", "كيف", "ما", "هو", "هي", "ايش", "في", "على", "عن", "من",
    "الى", "إلى", "هل", "اليوم", "هلق", "الآن", "الان", "الان", "بكرا", "الغد", "هناك",
    "weather", "temperature", "temp", "rain", "raining", "how", "what", "is", "the",
    "in", "at", "now", "today", "forecast", "هناك", "عندي", "عندنا",
}

def _has_kw(text: str, keywords: set) -> bool:
    t_low = text.lower()
    return any(kw in t_low for kw in keywords)

# Arabic/common name → CoinGecko ID
_CRYPTO_MAP = {
    "بيتكوين": "bitcoin", "بتكوين": "bitcoin", "bitcoin": "bitcoin", "btc": "bitcoin",
    "ايثيريوم": "ethereum", "ايثريوم": "ethereum", "اثيريوم": "ethereum",
    "ethereum": "ethereum", "eth": "ethereum",
    "ريبل": "ripple", "ripple": "ripple", "xrp": "ripple",
    "دوجكوين": "dogecoin", "دوج": "dogecoin", "doge": "dogecoin", "dogecoin": "dogecoin",
    "سولانا": "solana", "solana": "solana", "sol": "solana",
    "بينانس": "binancecoin", "bnb": "binancecoin",
    "كاردانو": "cardano", "cardano": "cardano", "ada": "cardano",
    "تيثر": "tether", "usdt": "tether", "tether": "tether",
    "دوت": "polkadot", "polkadot": "polkadot", "dot": "polkadot",
    "شيبا": "shiba-inu", "shib": "shiba-inu",
    "ليتكوين": "litecoin", "litecoin": "litecoin", "ltc": "litecoin",
    "اڤالانش": "avalanche-2", "avax": "avalanche-2",
    "بوليجون": "matic-network", "matic": "matic-network", "polygon": "matic-network",
    "ترون": "tron", "trx": "tron",
    "لينك": "chainlink", "chainlink": "chainlink", "link": "chainlink",
}

# Arabic/common name → stock ticker
_STOCK_MAP = {
    "ابل": "AAPL", "آبل": "AAPL", "apple": "AAPL",
    "مايكروسوفت": "MSFT", "مايكروسوفت": "MSFT", "microsoft": "MSFT",
    "جوجل": "GOOGL", "google": "GOOGL", "alphabet": "GOOGL",
    "امازون": "AMZN", "amazon": "AMZN",
    "تسلا": "TSLA", "tesla": "TSLA",
    "ميتا": "META", "فيسبوك": "META", "meta": "META", "facebook": "META",
    "نفليكس": "NFLX", "netflix": "NFLX",
    "نفيديا": "NVDA", "nvidia": "NVDA",
    "اوبر": "UBER", "uber": "UBER",
    "سامسونج": "005930.KS", "samsung": "005930.KS",
    "سناب": "SNAP", "snapchat": "SNAP",
    "تويتر": "X", "اكس": "X",
    "بالانتير": "PLTR", "palantir": "PLTR",
    "سبوتيفاي": "SPOT", "spotify": "SPOT",
    "ايرباص": "AIR.PA", "airbus": "AIR.PA",
    "ارامكو": "2222.SR", "aramco": "2222.SR",
}

def _extract_crypto(query: str) -> str:
    """Extract CoinGecko coin ID from natural language query."""
    q = query.lower().strip()
    for name, coin_id in _CRYPTO_MAP.items():
        if name.lower() in q:
            return coin_id
    return "bitcoin"

def _extract_stock(query: str) -> Optional[str]:
    """Extract stock ticker from natural language query."""
    q = query.lower().strip()
    for name, ticker in _STOCK_MAP.items():
        if name.lower() in q:
            return ticker
    # Fallback: look for standalone 2-5 uppercase letters in original query
    for word in query.split():
        clean = word.strip(".,!?/")
        if 2 <= len(clean) <= 5 and clean.isalpha() and clean == clean.upper() and clean.isascii():
            skip = {"USD", "EUR", "GBP", "SAR", "AED", "LBP", "THE", "AND", "FOR"}
            if clean not in skip:
                return clean
    return None

def _extract_city(query: str, default: str = "Beirut") -> str:
    """Extract city name from a natural language weather query."""
    words = re.split(r'[\s،,؟?!.]+', query)
    city_words = []
    for w in words:
        clean = w.strip("؟?!.,:؛\"'")
        if not clean:
            continue
        if clean.lower() in _WEATHER_STOP:
            continue
        # Skip pure Arabic particles: ال، في، من، على، عن (2 chars or less)
        if len(clean) <= 2 and re.search(r'[\u0600-\u06FF]', clean):
            continue
        city_words.append(clean)
    city = " ".join(city_words).strip()
    return city if len(city) > 1 else default

logger = logging.getLogger(__name__)
router = Router(name="ai_chat")

SYSTEM_PROMPT = """You are Omega, a powerful AI assistant on Telegram. You are friendly, direct, and fast.

🔴 ABSOLUTE RULE — LANGUAGE:
- You MUST reply in the EXACT same language the user wrote in. No exceptions.
- Arabic message → Arabic reply (use their dialect: Lebanese, Egyptian, Gulf, etc.)
- English message → English reply
- French message → French reply
- Mixed message → use the dominant language
- NEVER reply in English if the user wrote in Arabic or any other language
- Match their tone exactly: casual stays casual, formal stays formal

🔴 ABSOLUTE RULE — DATE / YEAR:
- The current date is provided below under [CURRENT_DATE]. Treat it as the real "today".
- NEVER say your knowledge was last updated in 2023 or any prior year.
- If asked about your update/version date, say you receive continuous updates and reference [CURRENT_DATE] as today.
- If asked for info about the current year, answer from the perspective of someone living in [CURRENT_DATE]; do not say "I can only speculate" just because of a training cutoff.
- Never mention "training data", "knowledge cutoff", "I was trained on…", or similar phrases.

Keep answers short and clear. Use emojis naturally. Be the smartest assistant they've ever used."""


def _current_date_block() -> str:
    """Inject today's date into the system prompt so models don't fall back to 2023."""
    now = datetime.now(timezone.utc)
    return (
        f"[CURRENT_DATE: {now.strftime('%A, %B %d, %Y')} "
        f"(ISO {now.date().isoformat()}, year {now.year})]"
    )

# ── Per-user conversation memory (in-process, max 10 messages, 30-min TTL) ──
_USER_HISTORY: dict = defaultdict(list)
_MAX_HIST = 10
_HISTORY_TTL = 1800  # 30 minutes in seconds

def _history_prune(uid: int) -> None:
    """Drop entries older than 30 min; remove the key entirely when empty."""
    cutoff = time.time() - _HISTORY_TTL
    pruned = [m for m in _USER_HISTORY.get(uid, []) if m.get("ts", 0) > cutoff]
    if pruned:
        _USER_HISTORY[uid] = pruned
    else:
        _USER_HISTORY.pop(uid, None)

def _history_add(uid: int, role: str, text: str) -> None:
    _USER_HISTORY[uid].append({"role": role, "content": text[:400], "ts": time.time()})
    if len(_USER_HISTORY[uid]) > _MAX_HIST:
        _USER_HISTORY[uid] = _USER_HISTORY[uid][-_MAX_HIST:]

def _history_get(uid: int) -> str:
    _history_prune(uid)
    msgs = _USER_HISTORY.get(uid, [])
    if not msgs:
        return ""
    lines = []
    for m in msgs:
        prefix = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{prefix}: {m['content']}")
    return "\n".join(lines)


@router.message(Command("ai"))
async def cmd_ai(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/ai", "").strip() if message.text else ""
    if not query:
        await message.answer(t("ai_intro", lang), parse_mode="Markdown")
        return
    await process_ai_query(message, query, lang=lang)


async def _route_to_service(message: Message, query: str, lang: str) -> bool:
    """Try to route natural language query to a specific service. Returns True if handled."""
    # ── Download intent ──────────────────────────────────────────────────────
    url = _extract_media_url(query)
    if url or _has_kw(query, _DL_KW):
        if url:
            # Keyword + URL, or bare URL with keyword context — show format picker
            from handlers.downloader import _pending_urls, _format_kb
            _pending_urls[message.from_user.id] = url
            prompt = "🎬 اختر صيغة التحميل:" if lang == "ar" else "🎬 Choose download format:"
            await message.answer(prompt, reply_markup=_format_kb(lang))
        else:
            # Keyword present but no URL — ask for the link
            hint = (
                "📥 أرسل الرابط الذي تريد تحميله"
                if lang == "ar"
                else "📥 Send the link you want to download"
            )
            await message.answer(hint)
        return True

    # Each block has its own try/except so one failing service doesn't hide others
    # Gold & metals
    if _has_kw(query, _GOLD_KW):
        try:
            from handlers.gold import cmd_gold
            await cmd_gold(message, lang=lang)
            return True
        except Exception as exc:
            logger.debug(f"Gold routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # Weather — extract city from query
    if _has_kw(query, _WEATHER_KW):
        try:
            city = _extract_city(query, default="Beirut")
            from api_clients.omega_weather import omega_weather
            await message.answer(t("fetching", lang))
            data = await omega_weather.get_weather(city, lang)
            if data and not data.get("error"):
                text = f"🌤 *{data.get('city', city)}*\n\n"
                text += f"🌡 {t('label_temp', lang)}: {data.get('temperature', 'N/A')}°C\n"
                text += f"🤔 {t('label_feels', lang)}: {data.get('feels_like', 'N/A')}°C\n"
                text += f"💧 {t('label_humidity', lang)}: {data.get('humidity', 'N/A')}%\n"
                text += f"💨 {t('label_wind', lang)}: {data.get('wind_speed', 'N/A')} km/h\n"
                if data.get("description"):
                    text += f"📝 {data['description']}\n"
                try:
                    await message.answer(text, parse_mode="Markdown")
                except Exception:
                    await message.answer(text)
            else:
                await message.answer(t("error", lang))
            return True
        except Exception as exc:
            logger.debug(f"Weather routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # Currency & exchange rates
    if _has_kw(query, _CURRENCY_KW):
        try:
            from handlers.currency import cmd_currency
            await cmd_currency(message, lang=lang)
            return True
        except Exception as exc:
            logger.debug(f"Currency routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # Fuel prices
    if _has_kw(query, _FUEL_KW):
        try:
            from handlers.fuel import cmd_fuel
            await cmd_fuel(message, lang=lang)
            return True
        except Exception as exc:
            logger.debug(f"Fuel routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # Stocks — extract ticker from natural language
    if _has_kw(query, _STOCK_KW):
        try:
            symbol = _extract_stock(query)
            if symbol:
                from api_clients.omega_stocks import omega_stocks
                await message.answer(t("fetching", lang))
                data = await omega_stocks.get_quote(symbol)
                if not data.get("error"):
                    change_emoji = "📈" if (data.get("change", 0) or 0) >= 0 else "📉"
                    text = f"📊 *{data.get('name', symbol)} ({data.get('symbol', symbol)})*\n\n"
                    text += f"{t('label_price', lang)}: ${data.get('price', 0):,.2f}\n"
                    text += f"{change_emoji} {t('label_change', lang)}: {data.get('change', 0):+,.2f} ({data.get('change_percent', 0):+.2f}%)\n"
                    if data.get("market_cap"):
                        text += f"{t('label_mcap', lang)}: ${data['market_cap']:,.0f}\n"
                    await message.answer(text, parse_mode="Markdown")
                else:
                    await message.answer(t("error", lang))
            else:
                await message.answer(t("fetching", lang))
                from handlers.stocks import cmd_stock
                await cmd_stock(message, lang=lang)
            return True
        except Exception as exc:
            logger.debug(f"Stocks routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # Crypto — extract coin from natural language
    if _has_kw(query, _CRYPTO_KW):
        try:
            coin = _extract_crypto(query)
            from api_clients.omega_crypto import omega_crypto
            await message.answer(t("fetching", lang))
            data = await omega_crypto.get_price(coin)
            if not data.get("error"):
                emoji = "📈" if (data.get("change_24h") or 0) >= 0 else "📉"
                text = f"₿ *{data.get('name', coin)} ({data.get('symbol', coin).upper()})*\n\n"
                text += f"{t('label_price', lang)}: ${data.get('price', 0):,.2f}\n"
                text += f"{emoji} 24h: {data.get('change_24h', 0):+.2f}%\n"
                if data.get("market_cap"):
                    text += f"{t('label_mcap', lang)}: ${data['market_cap']:,.0f}\n"
                await message.answer(text, parse_mode="Markdown")
            else:
                await message.answer(t("error", lang))
            return True
        except Exception as exc:
            logger.debug(f"Crypto routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # News
    if _has_kw(query, _NEWS_KW):
        try:
            from handlers.news import cmd_news
            await cmd_news(message, lang=lang)
            return True
        except Exception as exc:
            logger.debug(f"News routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # Football
    if _has_kw(query, _FOOTBALL_KW):
        try:
            from handlers.football import cmd_football
            await cmd_football(message, lang=lang)
            return True
        except Exception as exc:
            logger.debug(f"Football routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    # Movies & TV
    if _has_kw(query, _MOVIE_KW):
        try:
            from handlers.movies import cmd_movie
            await cmd_movie(message, lang=lang)
            return True
        except Exception as exc:
            logger.debug(f"Movies routing error: {exc}")
            await message.answer(t("error", lang))
            return True

    return False


async def process_ai_query(message: Message, query: str, lang: str = "en") -> None:
    """Process an AI query through the full Omega pipeline."""
    user_id = message.from_user.id

    if not check_user_rate(user_id, "ai_chat"):
        await message.answer(t("rate_limited", lang))
        return

    # Try smart service routing first (no AI needed)
    if await _route_to_service(message, query, lang):
        return

    await message.answer(t("fetching", lang))
    start_time = time.monotonic()

    try:
        analysis = omega_router.analyze(query)
        lang_names = {"ar": "Arabic", "en": "English", "fr": "French", "tr": "Turkish", "ru": "Russian", "es": "Spanish"}
        lang_name = lang_names.get(lang, lang)
        enhanced_prompt = (
            SYSTEM_PROMPT
            + f"\n\n{_current_date_block()}"
            + f"\n\n[SYSTEM: User is writing in {lang_name}. You MUST respond in {lang_name}. Do not use any other language.]"
        )

        # ── Optional: pull fresh web results for time-sensitive queries ─────
        search_block = ""
        if needs_web_search(query):
            try:
                results = await web_search(query, max_results=5)
                if results:
                    search_block = (
                        "\n\n[WEB_SEARCH_RESULTS — use these as the source of truth "
                        "for any current-events / time-sensitive claim; do NOT say "
                        "you lack up-to-date info if results are present]\n"
                        f"{results}\n[/WEB_SEARCH_RESULTS]"
                    )
            except Exception as exc:
                logger.debug(f"Web search failed: {exc}")

        # Build query with conversation history for context
        history_text = _history_get(user_id)
        base = f"{history_text}\nUser: {query}" if history_text else query
        query_with_ctx = f"{base}{search_block}"

        responses = await query_engine.query_all(query_with_ctx, system_prompt=enhanced_prompt, analysis=analysis)

        if not responses:
            await message.answer(t("error", lang))
            return

        fused = omega_fusion.fuse(responses, analysis)
        judged = omega_judge.evaluate(fused, query, analysis)

        elapsed = int((time.monotonic() - start_time) * 1000)
        text = judged["text"]

        if len(text) > 4000:
            text = text[:4000] + "..."

        try:
            await message.answer(text, parse_mode="Markdown")
        except Exception:
            # Fallback: send plain if AI output contains invalid Markdown
            await message.answer(text)

        # Save to in-memory conversation history
        _history_add(user_id, "user", query)
        _history_add(user_id, "assistant", text[:300])

        try:
            async with get_session() as session:
                user = await CRUDManager.get_user_by_telegram_id(session, user_id)
                if user:
                    await CRUDManager.save_conversation(session, user.id, "user", query)
                    await CRUDManager.save_conversation(session, user.id, "assistant", text[:500], models_used=judged.get("models_used"), fusion_score=judged.get("judge_score"))
                    await CRUDManager.log_search(session, user.id, "ai_chat", query, response_time_ms=elapsed, fusion_score=judged.get("judge_score"))
        except Exception as db_exc:
            logger.debug(f"DB logging error: {db_exc}")

        await omega_memory.update_user_context(user_id, query, "ai_chat", judged.get("judge_score", 0.5))

    except Exception as exc:
        logger.error(f"AI chat error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


_VISION_PROVIDERS = [
    {"provider": "gemini",     "model": "gemini-2.5-flash"},
    {"provider": "gemini",     "model": "gemini-2.0-flash"},
    {"provider": "openrouter", "model": "google/gemini-2.0-flash-exp:free"},
    {"provider": "openrouter", "model": "qwen/qwen2.5-vl-72b-instruct:free"},
    {"provider": "openrouter", "model": "meta-llama/llama-3.2-11b-vision-instruct:free"},
]


async def _analyze_image(img_b64: str, caption: str, system_text: str) -> str:
    """Try vision-capable providers in order until one succeeds."""
    for vp in _VISION_PROVIDERS:
        provider, model = vp["provider"], vp["model"]
        try:
            if provider == "gemini":
                key = settings.gemini_api_key
                if not key:
                    continue
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model}:generateContent?key={key}"
                )
                payload = {
                    "contents": [{"parts": [
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
                        {"text": f"System: {system_text}\n\nUser: {caption}"},
                    ]}],
                    "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7},
                }
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    candidates = data.get("candidates") or []
                    if not candidates:
                        continue
                    text = (
                        candidates[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )
                    if text:
                        return text
                    continue

            elif provider == "openrouter":
                key = settings.openrouter_api_key
                if not key:
                    continue
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": [
                        {"type": "text", "text": f"System: {system_text}\n\nUser: {caption}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    ]}],
                    "max_tokens": 1024,
                }
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        json=payload,
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    )
                    resp.raise_for_status()
                    choices = resp.json().get("choices") or []
                    if not choices:
                        continue
                    text = choices[0].get("message", {}).get("content", "")
                    if text:
                        return text
                    continue

        except Exception as exc:
            logger.debug(f"Vision {provider}/{model} failed: {exc}")
            continue

    raise RuntimeError("All vision providers failed")


@router.message(F.photo)
async def handle_photo_message(message: Message, lang: str = "en") -> None:
    """Analyze image using best available vision provider."""
    caption = (message.caption or "").strip()
    if not caption:
        caption = (
            "صف ما تراه في هذه الصورة بالتفصيل"
            if lang == "ar"
            else "Describe what you see in this image in detail."
        )

    if not check_user_rate(message.from_user.id, "ai_chat"):
        await message.answer(t("rate_limited", lang))
        return

    if not (settings.gemini_api_key or settings.openrouter_api_key):
        await message.answer(
            "❌ تحليل الصور غير مفعّل حالياً."
            if lang == "ar"
            else "❌ Image analysis is not available right now."
        )
        return

    status = await message.answer(
        "🔍 جارٍ تحليل الصورة..." if lang == "ar" else "🔍 Analyzing image..."
    )

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        bio = io.BytesIO()
        await message.bot.download_file(file.file_path, destination=bio)
        bio.seek(0)
        img_b64 = base64.b64encode(bio.read()).decode()

        system_text = SYSTEM_PROMPT + f"\n\n{_current_date_block()}"
        text = await _analyze_image(img_b64, caption, system_text)

        if len(text) > 4000:
            text = text[:4000] + "..."

        await status.delete()
        try:
            await message.answer(text, parse_mode="Markdown")
        except Exception:
            await message.answer(text)

        uid = message.from_user.id
        _history_add(uid, "user", f"[image] {caption}")
        _history_add(uid, "assistant", text[:300])

    except Exception as exc:
        logger.error(f"Vision error: {exc}", exc_info=True)
        try:
            await status.edit_text(
                "⚠️ تعذّر تحليل الصورة، حاول لاحقاً."
                if lang == "ar"
                else "⚠️ Could not analyze the image. Please try again."
            )
        except Exception:
            pass


def register_ai_handlers(dp) -> None:
    dp.include_router(router)
