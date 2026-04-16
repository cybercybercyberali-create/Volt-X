import logging
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

# Static pump prices (USD/L) — April 2026 reference; shown when live scraping fails.
_STATIC_FUEL_PRICES: dict[str, dict] = {
    "SA": {"بنزين 91": "0.175 USD/L", "بنزين 95": "0.209 USD/L", "ديزل": "0.209 USD/L"},
    "AE": {"بنزين 95": "0.645 USD/L", "بنزين 98": "0.704 USD/L", "ديزل": "0.640 USD/L"},
    "EG": {"بنزين 80": "0.270 USD/L", "بنزين 92": "0.350 USD/L", "بنزين 95": "0.440 USD/L", "ديزل": "0.250 USD/L"},
    "KW": {"بنزين 91": "0.272 USD/L", "بنزين 95": "0.300 USD/L", "ديزل": "0.280 USD/L"},
    "QA": {"بنزين 91": "0.449 USD/L", "بنزين 95": "0.461 USD/L", "ديزل": "0.449 USD/L"},
    "JO": {"بنزين 90": "1.110 USD/L", "بنزين 95": "1.230 USD/L", "ديزل": "1.050 USD/L"},
    "IQ": {"بنزين":    "0.530 USD/L", "ديزل":     "0.550 USD/L"},
    "DZ": {"بنزين":    "0.323 USD/L", "ديزل":     "0.207 USD/L"},
    "MA": {"بنزين 95": "1.230 USD/L", "ديزل":     "1.010 USD/L"},
    "TN": {"بنزين 91": "0.820 USD/L", "بنزين 95": "0.900 USD/L", "ديزل": "0.690 USD/L"},
    "TR": {"بنزين 95": "1.450 USD/L", "ديزل":     "1.400 USD/L"},
    "US": {"Gasoline (Regular)": "0.900 USD/L", "Diesel": "0.970 USD/L"},
    "DE": {"Super 95":           "1.740 USD/L", "Diesel": "1.620 USD/L"},
    "FR": {"SP95":               "1.700 USD/L", "Diesel": "1.570 USD/L"},
    "GB": {"Petrol E10":         "1.640 USD/L", "Diesel": "1.660 USD/L"},
    "JP": {"Regular":            "1.200 USD/L", "Diesel": "1.100 USD/L"},
    "IN": {"Petrol":             "1.150 USD/L", "Diesel": "0.990 USD/L"},
    "BR": {"Gasoline":           "1.310 USD/L", "Diesel": "1.100 USD/L"},
    "RU": {"AI-95":              "0.570 USD/L", "Diesel": "0.540 USD/L"},
    "CN": {"No. 92":             "1.050 USD/L", "Diesel": "0.990 USD/L"},
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


class OmegaFuel:
    """Fuel prices with per-country sources and scraping."""

    def __init__(self):
        self._scraper = BaseAPIClient("fuel_scraper")
        self._global = BaseAPIClient("globalpetrolprices", "https://www.globalpetrolprices.com")

    async def get_prices(self, country_code: str) -> dict[str, Any]:
        """Get fuel prices for a country."""
        cache_key = f"fuel:{country_code}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        country_code = country_code.upper()

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
                result["prices"] = prices
                return result

        global_prices = await self._get_global_prices(country_code)
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
        """Scrape Lebanon fuel prices from multiple sources."""
        import re
        from bs4 import BeautifulSoup

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

                # Many React/Next.js sites embed initial state in <script> tags
                # Look for JSON data like {"fuelPrices":[...]} or window.__NEXT_DATA__
                json_match = re.search(
                    r'(?:__NEXT_DATA__|__NUXT__|window\.__data__|initialState)\s*[=:]\s*(\{.{20,})',
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
                    return prices
                # Also try raw HTML in case values are in attributes
                prices = _extract_llp_prices(html)
                if len(prices) >= 2:
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

    async def _get_global_prices(self, country_code: str) -> dict[str, Any]:
        """Get fuel prices from GlobalPetrolPrices.com, falling back to static data."""
        import re as _re

        if country_code in ARAB_FUEL_SOURCES:
            name_ar = ARAB_FUEL_SOURCES[country_code]["name_ar"]
            name_en = ARAB_FUEL_SOURCES[country_code]["name_en"]
        else:
            name_ar, name_en = _COUNTRY_NAMES.get(country_code, (country_code, country_code))

        country_map = {
            "US": "USA", "GB": "United-Kingdom", "DE": "Germany",
            "FR": "France", "JP": "Japan", "CN": "China",
            "IN": "India", "BR": "Brazil", "RU": "Russia",
            "LB": "Lebanon", "SA": "Saudi-Arabia", "AE": "United-Arab-Emirates",
            "EG": "Egypt", "KW": "Kuwait", "QA": "Qatar", "BH": "Bahrain",
            "OM": "Oman", "JO": "Jordan", "IQ": "Iraq", "SY": "Syria",
            "DZ": "Algeria", "MA": "Morocco", "TN": "Tunisia",
            "LY": "Libya", "YE": "Yemen", "SD": "Sudan",
            "TR": "Turkey", "PK": "Pakistan", "NG": "Nigeria",
        }
        _SKIP_ROWS = {
            "correlation", "flexibility", "index", "tax", "vat", "subsidy",
            "margin", "volatility", "trend", "rank", "rate", "change", "percent",
        }
        prices: dict[str, str] = {}
        country_name = country_map.get(country_code, country_code)

        for fuel_path in ("gasoline_prices", "diesel_prices"):
            url = f"https://www.globalpetrolprices.com/{country_name}/{fuel_path}/"
            try:
                html = await self._scraper.fetch_html(url)
                if not html:
                    continue
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "lxml")
                for row in soup.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) < 2:
                        continue
                    fuel_name = cells[0].get_text(strip=True)
                    if not fuel_name or len(fuel_name) < 2:
                        continue
                    if any(skip in fuel_name.lower() for skip in _SKIP_ROWS):
                        continue
                    # Try first few cells for a price-like value
                    for cell in cells[1:4]:
                        cell_text = cell.get_text(strip=True).replace(",", ".")
                        m = _re.search(r'\b(\d+\.\d{2,4})\b', cell_text)
                        if m:
                            try:
                                val = float(m.group(1))
                                if 0.05 < val < 10.0:
                                    prices[fuel_name] = f"{val:.3f} USD/L"
                                    break
                            except ValueError:
                                pass
                # Also try finding price in plain text (some pages render JS)
                if not prices:
                    plain = soup.get_text(" ")
                    for m in _re.finditer(r'(\d+\.\d{3})\s*USD', plain):
                        val = float(m.group(1))
                        if 0.05 < val < 10.0:
                            label = "Gasoline" if fuel_path == "gasoline_prices" else "Diesel"
                            prices[label] = f"{val:.3f} USD/L"
                            break
            except Exception as exc:
                logger.debug(f"GPP {fuel_path} error for {country_code}: {exc}")

        if prices:
            return {
                "country_code": country_code,
                "country_name_ar": name_ar,
                "country_name_en": name_en,
                "prices": prices,
                "source": "GlobalPetrolPrices",
                "error": False,
            }

        # Static fallback
        static = _STATIC_FUEL_PRICES.get(country_code)
        if static:
            return {
                "country_code": country_code,
                "country_name_ar": name_ar,
                "country_name_en": name_en,
                "prices": static,
                "source": "static",
                "stale": True,
                "error": False,
            }

        return {
            "country_code": country_code,
            "country_name_ar": name_ar,
            "country_name_en": name_en,
            "prices": {},
            "error": True,
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
