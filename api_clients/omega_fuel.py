import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)

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
        else:
            result["prices"] = {"note": "Data temporarily unavailable"}

        return result

    async def _scrape_lebanon_fuel(self) -> Optional[dict]:
        """Scrape Lebanon fuel prices from multiple sources."""
        import re

        # Source 1: Lebanese Ministry of Energy (try multiple pages)
        for url in ["https://www.mol.gov.lb/", "https://www.mol.gov.lb/tabid/272/Default.aspx"]:
            try:
                html = await self._scraper.fetch_html(url)
                if html:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "lxml")
                    prices = {}
                    for table in soup.find_all("table"):
                        for row in table.find_all("tr"):
                            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                            if len(cells) < 2 or not cells[0] or len(cells[0]) < 2:
                                continue
                            name = cells[0]
                            for cell_text in cells[1:]:
                                nums = re.findall(r'[\d]+', cell_text.replace(",", "").replace(".", ""))
                                for n in nums:
                                    val = int(n)
                                    if val >= 1000:  # LBP prices are large integers
                                        prices[name] = f"{val:,} LBP"
                                        break
                    if len(prices) >= 2:
                        return prices
            except Exception as exc:
                logger.debug(f"mol.gov.lb scrape error ({url}): {exc}")

        # Source 2: GlobalPetrolPrices Lebanon page
        try:
            html = await self._scraper.fetch_html("https://www.globalpetrolprices.com/Lebanon/")
            if html:
                from bs4 import BeautifulSoup
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
        """Get fuel prices from GlobalPetrolPrices.com."""
        try:
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
            country_name = country_map.get(country_code, country_code)
            url = f"https://www.globalpetrolprices.com/{country_name}/gasoline_prices/"
            html = await self._scraper.fetch_html(url)

            if html:
                import re as _re
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "lxml")
                prices = {}
                for row in soup.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        fuel_name = cells[0].get_text(strip=True)
                        if not fuel_name or len(fuel_name) < 2:
                            continue
                        for cell in cells[1:]:
                            text = cell.get_text(strip=True)
                            m = _re.match(r'^(\d+[\.,]\d+)$', text.strip())
                            if m:
                                val_str = m.group(1).replace(",", ".")
                                try:
                                    val = float(val_str)
                                    if 0.05 < val < 20.0:
                                        prices[fuel_name] = f"{val:.3f} USD/L"
                                        break
                                except ValueError:
                                    continue

                return {
                    "country_code": country_code,
                    "prices": prices if prices else {"note": "Prices not available"},
                    "source": "GlobalPetrolPrices",
                    "error": not bool(prices),
                }
        except Exception as exc:
            logger.debug(f"Global fuel prices error for {country_code}: {exc}")

        return {"country_code": country_code, "prices": {}, "error": True, "message": "Data unavailable"}

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
