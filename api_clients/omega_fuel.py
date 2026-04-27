import logging
from datetime import datetime, timezone
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)

_COUNTRY_NAMES: dict[str, tuple[str, str]] = {
    "US": ("الولايات المتحدة", "USA"),
    "DE": ("ألمانيا",          "Germany"),
    "FR": ("فرنسا",            "France"),
    "GB": ("المملكة المتحدة",  "UK"),
    "JP": ("اليابان",          "Japan"),
    "CN": ("الصين",            "China"),
    "IN": ("الهند",            "India"),
    "BR": ("البرازيل",         "Brazil"),
    "RU": ("روسيا",            "Russia"),
    "TR": ("تركيا",            "Turkey"),
}

# Static pump prices (USD/L) — April 2026; used when live scraping fails.
# NOTE: Global prices spiked significantly due to Iran-Israel conflict (Feb-Apr 2026).
_STATIC_FUEL_PRICES: dict[str, dict] = {
    # Gulf — government-set quarterly prices (Q2 April 2026 — Aramco/ADNOC/QatarEnergy)
    "SA": {"بنزين 91": "0.581 USD/L", "بنزين 95": "0.621 USD/L", "ديزل": "0.477 USD/L"},
    "AE": {"بنزين 91 (E-Plus)": "0.831 USD/L", "بنزين 95 (Special)": "0.894 USD/L", "بنزين 98 (Super)": "0.924 USD/L", "ديزل": "1.278 USD/L"},
    "KW": {"بنزين 91 (Premium)": "0.277 USD/L", "بنزين 95 (Special)": "0.342 USD/L", "ديزل": "0.375 USD/L"},
    "QA": {"بنزين 91 (Premium)": "0.508 USD/L", "بنزين 95 (Super)": "0.563 USD/L", "ديزل": "0.500 USD/L"},
    "BH": {"بنزين 91": "0.370 USD/L", "بنزين 95": "0.400 USD/L", "ديزل": "0.320 USD/L"},
    "OM": {"بنزين 91": "0.530 USD/L", "بنزين 95": "0.560 USD/L", "ديزل": "0.500 USD/L"},
    # Levant & North Africa
    "EG": {"بنزين 92": "0.436 USD/L", "بنزين 95": "0.471 USD/L", "ديزل": "0.230 USD/L"},
    "JO": {"بنزين 90": "1.130 USD/L", "بنزين 95": "1.350 USD/L", "ديزل": "1.270 USD/L"},
    "IQ": {"بنزين": "0.307 USD/L", "ديزل": "0.230 USD/L"},
    "SY": {"بنزين": "0.230 USD/L", "ديزل": "0.180 USD/L"},
    "PS": {"بنزين 95": "1.550 USD/L", "ديزل": "1.500 USD/L"},
    "DZ": {"بنزين": "0.277 USD/L", "ديزل": "0.166 USD/L"},
    "MA": {"بنزين 95": "1.566 USD/L", "ديزل": "1.667 USD/L"},
    "TN": {"بنزين 91": "0.900 USD/L", "بنزين 95": "0.980 USD/L", "ديزل": "0.780 USD/L"},
    "LY": {"بنزين": "0.031 USD/L", "ديزل": "0.021 USD/L"},
    "SD": {"بنزين": "0.640 USD/L", "ديزل": "0.550 USD/L"},
    "YE": {"بنزين": "0.530 USD/L", "ديزل": "0.470 USD/L"},
    # Europe & Global
    "TR": {"بنزين 95": "1.592 USD/L", "ديزل": "1.744 USD/L"},
    "US": {"Gasoline (Regular)": "1.070 USD/L", "Diesel": "1.427 USD/L"},
    "DE": {"Super E10 (95)": "2.393 USD/L", "Diesel": "2.424 USD/L"},
    "FR": {"SP95-E10": "2.298 USD/L", "Diesel": "2.483 USD/L"},
    "GB": {"Petrol E10": "2.082 USD/L", "Diesel": "2.515 USD/L"},
    "JP": {"Regular": "1.154 USD/L", "Diesel": "1.228 USD/L"},
    "IN": {"Petrol": "1.141 USD/L", "Diesel": "1.057 USD/L"},
    "BR": {"Gasoline": "1.158 USD/L", "Diesel": "1.191 USD/L"},
    "RU": {"AI-95": "0.809 USD/L", "Diesel": "0.905 USD/L"},
    "CN": {"No. 92": "1.182 USD/L", "Diesel": "1.137 USD/L"},
}

ARAB_FUEL_SOURCES = {
    "LB": {"name_ar": "لبنان", "name_en": "Lebanon", "types": ["benzin95", "benzin98", "diesel", "gas10kg", "gas12kg", "gas50kg"]},
    "SA": {"name_ar": "السعودية", "name_en": "Saudi Arabia", "types": ["benzin91", "benzin95", "diesel"]},
    "AE": {"name_ar": "الإمارات", "name_en": "UAE", "types": ["super98", "special95", "eplus91", "diesel"]},
    "EG": {"name_ar": "مصر", "name_en": "Egypt", "types": ["benzin80", "benzin92", "benzin95", "diesel", "gas12.5kg"]},
    "KW": {"name_ar": "الكويت", "name_en": "Kuwait", "types": ["super", "premium", "ultra", "diesel"]},
    "QA": {"name_ar": "قطر", "name_en": "Qatar", "types": ["super", "premium", "diesel"]},
    "BH": {"name_ar": "البحرين", "name_en": "Bahrain", "types": ["super", "premium", "diesel"]},
    "OM": {"name_ar": "عمان", "name_en": "Oman", "types": ["m91", "m95", "diesel"]},
    "JO": {"name_ar": "الأردن", "name_en": "Jordan", "types": ["benzin90", "benzin95", "diesel", "gas"]},
    "IQ": {"name_ar": "العراق", "name_en": "Iraq", "types": ["benzin", "diesel"], "note": "أسعار تختلف بين بغداد وكردستان"},
    "SY": {"name_ar": "سوريا", "name_en": "Syria", "types": ["benzin", "diesel", "gas"], "note": "سعر رسمي + سوق"},
    "DZ": {"name_ar": "الجزائر", "name_en": "Algeria", "types": ["super", "normal", "diesel", "gpl", "butane13kg"]},
    "MA": {"name_ar": "المغرب", "name_en": "Morocco", "types": ["super", "diesel50", "diesel"]},
    "TN": {"name_ar": "تونس", "name_en": "Tunisia", "types": ["super", "diesel", "gpl"]},
    "LY": {"name_ar": "ليبيا", "name_en": "Libya", "types": ["benzin", "diesel"]},
    "YE": {"name_ar": "اليمن", "name_en": "Yemen", "types": ["benzin", "diesel", "gas"], "note": "أسعار عدن تختلف عن صنعاء"},
    "PS": {"name_ar": "فلسطين", "name_en": "Palestine", "types": ["benzin95", "diesel"]},
    "SD": {"name_ar": "السودان", "name_en": "Sudan", "types": ["benzin", "diesel", "gas"]},
}

_GPP_COUNTRY_SLUGS: dict[str, str] = {
    "SA": "Saudi-Arabia",        "AE": "United-Arab-Emirates", "KW": "Kuwait",
    "QA": "Qatar",               "BH": "Bahrain",              "OM": "Oman",
    "EG": "Egypt",               "JO": "Jordan",               "IQ": "Iraq",
    "MA": "Morocco",             "DZ": "Algeria",              "TN": "Tunisia",
    "LY": "Libya",               "TR": "Turkey",               "DE": "Germany",
    "GB": "United-Kingdom",      "JP": "Japan",                "IN": "India",
    "BR": "Brazil",              "RU": "Russia",               "CN": "China",
}

_GPP_NAME_TO_CODE: dict[str, str] = {
    "Saudi Arabia": "SA", "United Arab Emirates": "AE", "Egypt": "EG",
    "Kuwait": "KW", "Qatar": "QA", "Bahrain": "BH", "Oman": "OM",
    "Jordan": "JO", "Iraq": "IQ", "Algeria": "DZ", "Morocco": "MA",
    "Tunisia": "TN", "Libya": "LY", "Yemen": "YE", "Syria": "SY",
    "Turkey": "TR", "United States": "US", "Germany": "DE", "France": "FR",
    "United Kingdom": "GB", "Japan": "JP", "India": "IN", "Brazil": "BR",
    "Russia": "RU", "China": "CN", "Pakistan": "PK",
}

_GPP_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class OmegaFuel:
    """Fuel prices with per-country sources and scraping."""

    def __init__(self):
        self._scraper = BaseAPIClient("fuel_scraper")
        self._global = BaseAPIClient("globalpetrolprices", "https://www.globalpetrolprices.com")

    async def get_prices(self, country_code: str, force: bool = False) -> dict[str, Any]:
        """Get fuel prices for a country. force=True bypasses cache."""
        country_code = country_code.upper()
        cache_key = f"fuel:{country_code}"

        if not force:
            cached = await cache.get(cache_key)
            if cached:
                # For Lebanon: force-refresh if cached data is older than 48 hours
                if country_code == "LB":
                    scraped_at = cached.get("scraped_at", "")
                    if scraped_at:
                        try:
                            age_h = (datetime.now(timezone.utc) -
                                     datetime.fromisoformat(scraped_at)).total_seconds() / 3600
                            if age_h > 48:
                                logger.info("LB fuel cache older than 48 h — forcing refresh")
                                force = True
                        except Exception:
                            pass
                if not force:
                    return cached

        if country_code in ARAB_FUEL_SOURCES:
            result = await self._get_arab_country_prices(country_code)
        else:
            result = await self._get_global_prices(country_code)

        if result and not result.get("error"):
            ttl = CACHE_TTL["fuel_lebanon"] if country_code == "LB" else CACHE_TTL["fuel"]
            await cache.set(cache_key, result, ttl=ttl)

        return result

    async def _get_arab_country_prices(self, country_code: str) -> dict[str, Any]:
        """Get fuel prices for Arab countries with specific sources."""
        config = ARAB_FUEL_SOURCES[country_code]
        result = {
            "country_code": country_code,
            "country_name_ar": config["name_ar"],
            "country_name_en": config["name_en"],
            "fuel_types": config["types"],
            "prices": {},
            "note": config.get("note", ""),
            "error": False,
        }

        if country_code == "LB":
            prices = await self._scrape_lebanon_fuel()
            if prices:
                result["scraped_at"]      = prices.pop("__scraped_at__", "")
                result["published_date"]  = prices.pop("__published_date__", "")
                result["prices"] = prices
                return result
            # Scraping failed — hardcoded fallback (IPT prices, updated weekly on Thu)
            from datetime import date as _d, timedelta as _td
            _today = _d.today()
            _last_thu = _today - _td(days=(_today.weekday() - 3) % 7)
            result["prices"] = {
                "بنزين 98": "2,418,000 ل.ل.",
                "بنزين 95": "2,378,000 ل.ل.",
                "ديزل":     "2,407,000 ل.ل.",
                "غاز 10kg": "1,706,000 ل.ل.",
            }
            result["published_date"] = f"{_last_thu.day}/{_last_thu.month}/{_last_thu.year}"
            result["scraped_at"]     = datetime.now(timezone.utc).isoformat()
            result["stale"]          = True
            return result

        try:
            global_prices = await self._get_global_prices(country_code)
        except Exception as exc:
            logger.warning(f"_get_global_prices raised for {country_code}: {exc}")
            global_prices = None
        if global_prices and not global_prices.get("error"):
            result["prices"] = global_prices.get("prices", {})
            result["stale"]  = global_prices.get("stale", False)
        else:
            static = _STATIC_FUEL_PRICES.get(country_code)
            if static:
                result["prices"] = static
                result["stale"]  = True
            else:
                result["error"] = True

        return result

    async def _scrape_lebanon_fuel(self) -> Optional[dict]:
        """Scrape Lebanon fuel prices — returns dict with prices + scraped_at + published_date."""
        import re
        from bs4 import BeautifulSoup

        _NOW_ISO = datetime.now(timezone.utc).isoformat()

        # Helper: extract a date string from IPT page (looks for patterns like "17 April 2026")
        _AR_MONTHS = {"january":"يناير","february":"فبراير","march":"مارس","april":"أبريل",
                      "may":"مايو","june":"يونيو","july":"يوليو","august":"أغسطس",
                      "september":"سبتمبر","october":"أكتوبر","november":"نوفمبر","december":"ديسمبر"}
        def _extract_date(text: str) -> str:
            m = re.search(
                r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|'
                r'september|october|november|december)\s+(\d{4})',
                text, re.IGNORECASE)
            if m:
                day, month_en, year = m.group(1), m.group(2).lower(), m.group(3)
                month_ar = _AR_MONTHS.get(month_en, month_en)
                return f"{day} {month_ar} {year}"
            # ISO date 2026-04-17 or 17/04/2026
            m2 = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
            if m2:
                from datetime import date as _date
                try:
                    d = _date(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
                    month_ar = _AR_MONTHS.get(d.strftime("%B").lower(), d.strftime("%B"))
                    return f"{d.day} {month_ar} {d.year}"
                except Exception:
                    pass
            return ""

        # Helper: extract LBP price numbers >100,000 from HTML text
        def _extract_llp_prices(html_text: str) -> dict:
            prices = {}
            patterns = [
                (r'UNL\s*95[\s\S]{0,40}?([\d,]{7,})\s*(?:L\.?L\.?|ل\.?ل\.?|LBP|LL)', 'بنزين 95'),
                (r'UNL\s*98[\s\S]{0,40}?([\d,]{7,})\s*(?:L\.?L\.?|ل\.?ل\.?|LBP|LL)', 'بنزين 98'),
                (r'Diesel[\s\S]{0,40}?([\d,]{7,})\s*(?:L\.?L\.?|ل\.?ل\.?|LBP|LL)', 'ديزل'),
                (r'Gas\s*(?:Oil|\(LPG\)|LPG)?[\s\S]{0,40}?([\d,]{7,})\s*(?:L\.?L\.?|ل\.?ل\.?|LBP|LL)', 'غاز 10kg'),
                (r'Kerosene[\s\S]{0,40}?([\d,]{7,})\s*(?:L\.?L\.?|ل\.?ل\.?|LBP|LL)', 'كيروسين'),
                (r'(?:بنزين|Benzine)\s*95[\s\S]{0,40}?([\d,]{7,})', 'بنزين 95'),
                (r'(?:بنزين|Benzine)\s*98[\s\S]{0,40}?([\d,]{7,})', 'بنزين 98'),
                (r'(?:ديزل|مازوت|Mazout)[\s\S]{0,40}?([\d,]{7,})', 'ديزل'),
            ]
            for pattern, label in patterns:
                if label in prices:
                    continue
                m = re.search(pattern, html_text, re.IGNORECASE)
                if m:
                    val_str = m.group(1).replace(",", "")
                    try:
                        val = int(val_str)
                        if val > 100_000:
                            prices[label] = f"{val:,} ل.ل."
                    except ValueError:
                        pass
            return prices

        # Full browser-like headers to bypass Cloudflare / CDN blocks
        _BROWSER = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
        }

        # Source 0a: ScraperAPI — JS-rendered fetch (IPT is a React SPA)
        _skey = getattr(settings, "scraper_api_key", "") or ""
        if _skey:
            import httpx as _httpx
            _ipt_url = "https://www.iptgroup.com.lb/ipt/en/our-stations/fuel-prices"
            # Try JS-rendered first (5 credits), then plain HTML (1 credit) as fallback
            for _render in ("true", "false"):
                try:
                    async with _httpx.AsyncClient(timeout=35.0) as _cl:
                        _r = await _cl.get(
                            "https://api.scraperapi.com/",
                            params={
                                "api_key": _skey,
                                "url": _ipt_url,
                                "render": _render,
                                "wait": "3000" if _render == "true" else "0",
                                "country_code": "lb",
                            },
                        )
                        if _r.status_code != 200 or len(_r.text) < 500:
                            continue
                        _plain = re.sub(r'<[^>]+>', ' ', _r.text)
                        _prices = _extract_llp_prices(_plain)
                        if not _prices:
                            _prices = _extract_llp_prices(_r.text)
                        if len(_prices) >= 2:
                            _pub = _extract_date(_plain)
                            _prices["__scraped_at__"] = _NOW_ISO
                            _prices["__published_date__"] = _pub
                            logger.info(f"ScraperAPI IPT prices (render={_render}): {_prices}")
                            return _prices
                        logger.debug(f"ScraperAPI render={_render}: found {len(_prices)} prices, retrying")
                except Exception as _exc:
                    logger.debug(f"ScraperAPI error (render={_render}): {_exc}")

        # Source 0: IPT Group — correct URL + fallbacks
        ipt_urls = [
            "https://www.iptgroup.com.lb/ipt/en/our-stations/fuel-prices",
            "https://iptgroup.com.lb/ipt/en/our-stations/fuel-prices",
            "https://www.iptgroup.com.lb/ipt/ar/our-stations/fuel-prices",
            "https://www.iptgroup.com.lb/",
        ]
        for url in ipt_urls:
            try:
                html = await self._scraper.fetch_html(url, headers=_BROWSER)
                if not html or len(html) < 500:
                    continue

                # Next.js embeds server-side props in <script id="__NEXT_DATA__">
                json_match = re.search(
                    r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>\s*(\{.+?)\s*</script>',
                    html, re.DOTALL
                ) or re.search(
                    r'(?:__NUXT__|window\.__data__|initialState)\s*[=:]\s*(\{.{20,})',
                    html, re.DOTALL
                )
                if json_match:
                    import json as _json
                    raw_json = json_match.group(1)
                    # Find end of JSON object (balanced braces)
                    depth, end = 0, 0
                    for i, ch in enumerate(raw_json[:50000]):
                        if ch == '{': depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                end = i + 1
                                break
                    try:
                        obj = _json.loads(raw_json[:end])
                        obj_str = str(obj)
                        prices = _extract_llp_prices(obj_str)
                        if len(prices) >= 2:
                            logger.info(f"IPT JSON embed prices from {url}: {prices}")
                            return prices
                    except Exception:
                        pass

                # Strip HTML tags for regex matching
                plain = re.sub(r'<[^>]+>', ' ', html)
                prices = _extract_llp_prices(plain)
                if len(prices) >= 2:
                    logger.info(f"IPT fuel prices from {url}: {prices}")
                    pub = _extract_date(plain)
                    prices["__scraped_at__"] = _NOW_ISO
                    prices["__published_date__"] = pub
                    return prices
                # Also try raw HTML in case values are in attributes
                prices = _extract_llp_prices(html)
                if len(prices) >= 2:
                    pub = _extract_date(re.sub(r'<[^>]+>', ' ', html))
                    prices["__scraped_at__"] = _NOW_ISO
                    prices["__published_date__"] = pub
                    return prices
            except Exception as exc:
                logger.debug(f"iptgroup {url} error: {exc}")

        # Source 1: Lebanese Ministry of Energy
        for url in ["https://www.mol.gov.lb/tabid/272/Default.aspx", "https://www.mol.gov.lb/"]:
            try:
                html = await self._scraper.fetch_html(url)
                if html and len(html) > 500:
                    soup = BeautifulSoup(html, "lxml")
                    plain = soup.get_text(" ")
                    prices = _extract_llp_prices(plain)
                    if len(prices) >= 2:
                        pub = _extract_date(plain)
                        prices["__scraped_at__"] = _NOW_ISO
                        prices["__published_date__"] = pub
                        return prices
                    # Try table parsing
                    prices_tbl = {}
                    for table in soup.find_all("table"):
                        for row in table.find_all("tr"):
                            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                            if len(cells) < 2:
                                continue
                            name = cells[0]
                            for cell_text in cells[1:]:
                                nums = re.findall(r'\d[\d,]{5,}', cell_text)
                                for n in nums:
                                    val = int(n.replace(",", ""))
                                    if val > 100_000:
                                        prices_tbl[name] = f"{val:,} ل.ل."
                                        break
                    if len(prices_tbl) >= 2:
                        prices_tbl["__scraped_at__"] = _NOW_ISO
                        prices_tbl["__published_date__"] = _extract_date(plain)
                        return prices_tbl
            except Exception as exc:
                logger.debug(f"mol.gov.lb error ({url}): {exc}")

        # Source 2: GlobalPetrolPrices Lebanon (shows USD/L)
        try:
            html = await self._scraper.fetch_html("https://www.globalpetrolprices.com/Lebanon/gasoline_prices/")
            if html:
                soup = BeautifulSoup(html, "lxml")
                prices = {}
                for row in soup.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        fuel_name = cells[0].get_text(strip=True)
                        if not fuel_name or len(fuel_name) < 2:
                            continue
                        for cell in cells[1:]:
                            m = re.search(r'(\d+\.\d+)', cell.get_text(strip=True))
                            if m:
                                val = float(m.group(1))
                                if 0.05 < val < 20.0:
                                    prices[fuel_name] = f"{val:.3f} USD/L"
                                    break
                if prices:
                    return prices
        except Exception as exc:
            logger.debug(f"globalpetrolprices LB error: {exc}")

        return None

    async def _fetch_gpp_all(self) -> dict[str, dict]:
        """
        Scrape GlobalPetrolPrices for all countries.
        Uses ScraperAPI as PRIMARY when key is set (bypasses IP blocks / Cloudflare).
        Direct fetch is last-resort only (will be blocked on Render).
        Cached 12 hours.
        """
        cache_key = "gpp:listing"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        import re as _re
        import httpx as _httpx
        from bs4 import BeautifulSoup
        from config import settings as _cfg

        _skey = getattr(_cfg, "scraper_api_key", "") or ""
        result: dict[str, dict] = {}

        async def _parse_gpp_html(html: str, fuel_key: str) -> None:
            soup = BeautifulSoup(html, "lxml")
            for row in soup.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue
                country_text = cells[0].get_text(strip=True)
                code = _GPP_NAME_TO_CODE.get(country_text)
                if not code:
                    continue
                for cell in cells[1:5]:
                    txt = cell.get_text(strip=True).replace(",", ".")
                    m = _re.search(r'\b(\d+\.\d{2,4})\b', txt)
                    if m:
                        val = float(m.group(1))
                        if 0.01 < val < 10.0:
                            result.setdefault(code, {})
                            label = "Gasoline" if fuel_key == "gasoline" else "Diesel"
                            result[code][label] = f"{val:.3f} USD/L"
                            break

        async def _fetch_via_scraperapi(url: str, render: str) -> str | None:
            try:
                async with _httpx.AsyncClient(timeout=30.0) as cl:
                    r = await cl.get(
                        "https://api.scraperapi.com/",
                        params={"api_key": _skey, "url": url, "render": render},
                    )
                    if r.status_code == 200 and len(r.text) > 2000:
                        logger.info(f"GPP ScraperAPI render={render} OK: {len(r.text)} bytes ({url})")
                        return r.text
                    logger.debug(f"GPP ScraperAPI render={render} short/bad: status={r.status_code} len={len(r.text)}")
            except Exception as exc:
                logger.debug(f"GPP ScraperAPI render={render} error: {exc}")
            return None

        async def _fetch_direct(url: str) -> str | None:
            try:
                html = await self._scraper.fetch_html(url, headers=_GPP_BROWSER_HEADERS)
                if html and len(html) > 2000:
                    logger.info(f"GPP direct OK: {len(html)} bytes ({url})")
                    return html
            except Exception as exc:
                logger.debug(f"GPP direct fetch error: {exc}")
            return None

        for fuel_key, url_path in [("gasoline", "gasoline_prices"), ("diesel", "diesel_prices")]:
            gpp_url = f"https://www.globalpetrolprices.com/{url_path}/"
            html = None

            if _skey:
                # ScraperAPI PRIMARY: plain HTML first (1 credit), JS-rendered fallback (5 credits)
                html = await _fetch_via_scraperapi(gpp_url, "false")
                if not html:
                    html = await _fetch_via_scraperapi(gpp_url, "true")

            if not html:
                # Last resort: Render's own IP — likely blocked, but try anyway
                html = await _fetch_direct(gpp_url)

            if html:
                try:
                    await _parse_gpp_html(html, fuel_key)
                except Exception as exc:
                    logger.debug(f"GPP parse error ({fuel_key}): {exc}")

        if result:
            await cache.set(cache_key, result, ttl=3600 * 12)
            logger.info(f"GPP listing cached: {len(result)} countries")
        return result

    async def _fetch_us_eia(self) -> dict | None:
        """Official EIA weekly retail fuel prices for USA — routed via ScraperAPI to bypass Render IP block."""
        import httpx as _httpx, urllib.parse as _up
        from config import settings as _cfg
        eia_key = getattr(_cfg, "eia_api_key", "") or "DEMO_KEY"
        scraper_key = getattr(_cfg, "scraper_api_key", "") or ""
        results: dict[str, str] = {}
        try:
            async with _httpx.AsyncClient(timeout=20.0) as cl:
                for product, label in [("EPM0", "Gasoline (Regular)"), ("EPD2D", "Diesel")]:
                    eia_params = {
                        "api_key": eia_key,
                        "frequency": "weekly",
                        "data[0]": "value",
                        "facets[duoarea][]": "USA",
                        "facets[product][]": product,
                        "sort[0][column]": "period",
                        "sort[0][direction]": "desc",
                        "length": "1",
                    }
                    # Build full EIA URL so ScraperAPI can proxy it
                    eia_url = "https://api.eia.gov/v2/petroleum/pri/gnd/data/?" + _up.urlencode(eia_params)
                    # Try ScraperAPI proxy first — bypasses Render's blocked IP
                    r = None
                    if scraper_key:
                        try:
                            r = await cl.get(
                                "https://api.scraperapi.com/",
                                params={"api_key": scraper_key, "url": eia_url, "render": "false"},
                                timeout=20.0,
                            )
                        except Exception:
                            r = None
                    # Direct fallback (works if EIA doesn't block this IP)
                    if r is None or r.status_code != 200:
                        try:
                            r = await cl.get(
                                "https://api.eia.gov/v2/petroleum/pri/gnd/data/",
                                params=eia_params,
                                timeout=12.0,
                            )
                        except Exception:
                            continue
                    if r and r.status_code == 200:
                        try:
                            rows = r.json().get("response", {}).get("data", [])
                            if rows and rows[0].get("value"):
                                liter = round(float(rows[0]["value"]) / 3.785, 3)
                                results[label] = f"{liter:.3f} USD/L"
                        except Exception:
                            pass
            if results:
                logger.info(f"EIA USA prices: {results}")
        except Exception as exc:
            logger.debug(f"EIA error: {exc}")
        return results or None

    async def _fetch_france_open(self) -> dict | None:
        """Official French weekly average fuel prices — open data, no key needed."""
        import httpx as _httpx
        try:
            async with _httpx.AsyncClient(timeout=12.0, follow_redirects=True) as cl:
                r = await cl.get(
                    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
                    "prix-moyens-hebdomadaires-des-carburants-en-france/records",
                    params={"limit": 1, "order_by": "date_debut desc"},
                )
                if r.status_code != 200:
                    return None
                records = r.json().get("results", [])
                if not records:
                    return None
                rec = records[0]
                prices: dict[str, str] = {}
                for field, label in [
                    ("prix_sp95", "SP95"), ("prix_sp98", "SP98"),
                    ("prix_gazole", "Diesel"), ("prix_e10", "SP95-E10"),
                    ("prix_gplc", "GPL"),
                ]:
                    v = rec.get(field)
                    if v:
                        try:
                            prices[label] = f"{float(v):.3f} EUR/L"
                        except (ValueError, TypeError):
                            pass
                if prices:
                    logger.info(f"France official prices: {list(prices.keys())}")
                return prices or None
        except Exception as exc:
            logger.debug(f"France open data error: {exc}")
        return None

    async def _fetch_country_gpp_page(self, country_code: str) -> dict | None:
        """Fetch per-country GPP page via ScraperAPI — extracts price from embedded JS chart data."""
        import httpx as _httpx, re as _re
        from bs4 import BeautifulSoup
        from config import settings as _cfg
        _skey = getattr(_cfg, "scraper_api_key", "") or ""
        slug = _GPP_COUNTRY_SLUGS.get(country_code)
        if not slug or not _skey:
            return None
        results: dict[str, str] = {}
        for label, path in [("Gasoline", "gasoline_prices"), ("Diesel", "diesel_prices")]:
            url = f"https://www.globalpetrolprices.com/{slug}/{path}/"
            try:
                async with _httpx.AsyncClient(timeout=25.0) as cl:
                    r = await cl.get(
                        "https://api.scraperapi.com/",
                        params={"api_key": _skey, "url": url, "render": "false"},
                    )
                if r.status_code != 200 or len(r.text) < 500:
                    continue
                html = r.text
                # GPP embeds price history in a JS array: [["YYYY-MM-DD", usd_val, local_val], ...]
                # The last entry is the most recent price in USD/L
                m = _re.search(r'var\s+(?:chart|data|chartData|prices)\s*=\s*(\[\[.*?\]\])', html, _re.DOTALL)
                if m:
                    try:
                        import json as _json
                        rows = _json.loads(m.group(1))
                        for row in reversed(rows):
                            if len(row) >= 2 and row[1] is not None:
                                val = float(row[1])
                                if 0.01 < val < 10.0:
                                    results[label] = f"{val:.3f} USD/L"
                                    break
                        if label in results:
                            continue
                    except Exception:
                        pass
                # Fallback: scan <script> tags for date+price pattern
                soup = BeautifulSoup(html, "lxml")
                for script in soup.find_all("script"):
                    txt = script.string or ""
                    hits = _re.findall(r'\["20\d\d-\d\d-\d\d",\s*([\d.]+)', txt)
                    if hits:
                        try:
                            val = float(hits[-1])
                            if 0.01 < val < 10.0:
                                results[label] = f"{val:.3f} USD/L"
                                break
                        except Exception:
                            pass
                if label in results:
                    continue
                # Last resort: any price-like number in table cells
                for el in soup.select("table td"):
                    txt = el.get_text(strip=True).replace(",", ".")
                    m2 = _re.search(r'(?<!\d)(\d+\.\d{2,4})(?!\d)', txt)
                    if m2:
                        val = float(m2.group(1))
                        if 0.01 < val < 10.0:
                            results[label] = f"{val:.3f} USD/L"
                            break
            except Exception as exc:
                logger.debug(f"GPP country page {country_code}/{label}: {exc}")
        return results or None

    async def _get_global_prices(self, country_code: str) -> dict[str, Any]:
        """Get fuel prices with tiered sources: dedicated API → per-country GPP → bulk GPP → static."""
        if country_code in ARAB_FUEL_SOURCES:
            name_ar = ARAB_FUEL_SOURCES[country_code]["name_ar"]
            name_en = ARAB_FUEL_SOURCES[country_code]["name_en"]
        else:
            name_ar, name_en = _COUNTRY_NAMES.get(country_code, (country_code, country_code))

        def _ok(prices: dict | None, source: str, stale: bool = False) -> dict[str, Any]:
            return {
                "country_code":    country_code,
                "country_name_ar": name_ar,
                "country_name_en": name_en,
                "prices":          prices or {},
                "source":          source,
                "stale":           stale,
                "fetched_at":      datetime.now(timezone.utc).isoformat(),
                "error":           False,
            }

        # Tier 1 — Dedicated free APIs (no scraping, most reliable)
        try:
            if country_code == "US":
                prices = await self._fetch_us_eia()
                if prices:
                    return _ok(prices, "EIA (official)")
            elif country_code == "FR":
                prices = await self._fetch_france_open()
                if prices:
                    return _ok(prices, "prix-carburants.gouv.fr")
        except Exception as exc:
            logger.debug(f"Tier-1 fetcher failed for {country_code}: {exc}")

        # Tier 2 — Per-country GPP page via ScraperAPI
        try:
            prices = await self._fetch_country_gpp_page(country_code)
            if prices:
                return _ok(prices, "GlobalPetrolPrices")
        except Exception as exc:
            logger.debug(f"Tier-2 GPP page failed for {country_code}: {exc}")

        # Tier 3 — Bulk GPP listing (shared cache across all countries)
        try:
            all_prices = await self._fetch_gpp_all()
            if country_code in all_prices:
                return _ok(all_prices[country_code], "GlobalPetrolPrices")
        except Exception as exc:
            logger.warning(f"Tier-3 GPP bulk failed for {country_code}: {exc}")

        # Tier 4 — Static reference prices
        static = _STATIC_FUEL_PRICES.get(country_code)
        if static:
            return _ok(static, "static reference", stale=True)

        return {
            "country_code":    country_code,
            "country_name_ar": name_ar,
            "country_name_en": name_en,
            "prices":          {},
            "error":           True,
        }

    async def get_arab_summary(self) -> dict[str, Any]:
        """Get summary of fuel prices for all Arab countries."""
        results = {}
        for code in ARAB_FUEL_SOURCES:
            results[code] = await self.get_prices(code)
        return results

    async def close(self) -> None:
        await self._scraper.close()
        await self._global.close()


omega_fuel = OmegaFuel()
