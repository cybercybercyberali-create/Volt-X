import logging
import statistics
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL, PARALLEL_RATE_COUNTRIES
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


# Static fallback rates — used when ALL live APIs are down.
# Updated manually to reflect approximate real-world rates (April 2026 basis).
_STATIC_FALLBACK: dict[tuple, float] = {
    ("USD", "EUR"): 0.880,  ("USD", "GBP"): 0.760,  ("USD", "JPY"): 145.0,
    ("USD", "CHF"): 0.905,  ("USD", "CAD"): 1.390,  ("USD", "AUD"): 1.570,
    ("USD", "LBP"): 89500.0,("USD", "SAR"): 3.750,  ("USD", "AED"): 3.672,
    ("USD", "EGP"): 51.0,   ("USD", "TRY"): 39.0,   ("USD", "JOD"): 0.709,
    ("USD", "KWD"): 0.307,  ("USD", "QAR"): 3.640,  ("USD", "BHD"): 0.376,
    ("USD", "OMR"): 0.385,  ("USD", "IQD"): 1310.0, ("USD", "SYP"): 13000.0,
    ("USD", "MAD"): 9.85,   ("USD", "DZD"): 136.0,  ("USD", "TND"): 3.18,
    ("EUR", "USD"): 1.136,  ("EUR", "GBP"): 0.864,  ("EUR", "LBP"): 101700.0,
    ("GBP", "USD"): 1.316,  ("GBP", "EUR"): 1.158,  ("GBP", "LBP"): 117700.0,
}

def _static_fallback(base: str, target: str) -> float | None:
    """Look up a static fallback rate, trying direct and reverse."""
    direct = _STATIC_FALLBACK.get((base, target))
    if direct is not None:
        return direct
    rev = _STATIC_FALLBACK.get((target, base))
    if rev:
        return round(1.0 / rev, 6)
    return None


class OmegaCurrency:
    """Currency exchange with multi-source fusion and parallel market rates."""

    def __init__(self):
        self._frankfurter = BaseAPIClient("frankfurter", "https://api.frankfurter.app")
        self._exchangerate = BaseAPIClient("exchangerate")
        self._fxrates = BaseAPIClient("fxrates", "https://api.fxratesapi.com")
        self._scraper = BaseAPIClient("currency_scraper")

    async def get_rate(self, base: str = "USD", target: str = "EUR") -> dict[str, Any]:
        """Get exchange rate with multi-source fusion."""
        cache_key = f"currency:{base}:{target}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        rates = []

        rate1 = await self._fetch_frankfurter(base, target)
        if rate1 is not None:
            rates.append({"source": "ECB/Frankfurter", "rate": rate1})

        # Limited API (if quota available, auto-restores when renewed)
        if quota.has_quota("exchange_rate"):
            rate2 = await self._fetch_exchangerate_api(base, target)
            if rate2 is not None:
                quota.use_quota("exchange_rate")
                rates.append({"source": "ExchangeRate-API", "rate": rate2})

        rate3 = await self._fetch_fxrates(base, target)
        if rate3 is not None:
            rates.append({"source": "FXRatesAPI", "rate": rate3})

        if not rates:
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                result["age_minutes"] = stale.get("age_minutes", 0)
                return result
            # Static offline fallback — better than a hard error
            fb = _static_fallback(base, target)
            if fb is not None:
                logger.info(f"Using static fallback for {base}/{target}: {fb}")
                return {
                    "base": base, "target": target, "rate": fb,
                    "sources_count": 0, "error": False,
                    "stale": True, "stale_note": "offline_fallback",
                }
            return {"error": True, "message": "No rate data available"}

        values = [r["rate"] for r in rates]
        fused_rate = statistics.median(values) if len(values) >= 2 else values[0]

        result = {
            "base": base,
            "target": target,
            "rate": round(fused_rate, 6),
            "sources_count": len(rates),
            "error": False,
        }

        target_country = None
        for code, info in PARALLEL_RATE_COUNTRIES.items():
            if info["currency"] == target:
                target_country = code
                break

        if target_country:
            parallel = await self._fetch_parallel_rate(target_country, base)
            if parallel:
                result["parallel_rate"] = parallel["rate"]
                result["parallel_source"] = parallel["source"]
                result["has_parallel"] = True
            else:
                result["has_parallel"] = False
        else:
            result["has_parallel"] = False

        await cache.set(cache_key, result, ttl=CACHE_TTL["currency"])
        return result

    async def get_multiple_rates(self, base: str = "USD", targets: Optional[list[str]] = None) -> dict[str, Any]:
        """Get rates for multiple target currencies."""
        if targets is None:
            targets = ["EUR", "GBP", "SAR", "AED", "EGP", "TRY", "LBP"]

        results = {}
        for target in targets:
            results[target] = await self.get_rate(base, target)
        return results

    async def _fetch_frankfurter(self, base: str, target: str) -> Optional[float]:
        """Fetch from Frankfurter (ECB, free, no key)."""
        try:
            data = await self._frankfurter.get(f"/latest?from={base}&to={target}")
            if data and "rates" in data:
                return data["rates"].get(target)
        except Exception as exc:
            logger.debug(f"Frankfurter error: {exc}")
        return None

    async def _fetch_exchangerate_api(self, base: str, target: str) -> Optional[float]:
        """Fetch from ExchangeRate-API."""
        if not settings.exchange_rate_key:
            return None
        try:
            data = await self._exchangerate.get(
                f"https://v6.exchangerate-api.com/v6/{settings.exchange_rate_key}/pair/{base}/{target}"
            )
            if data and data.get("result") == "success":
                return data.get("conversion_rate")
        except Exception as exc:
            logger.debug(f"ExchangeRate-API error: {exc}")
        return None

    async def _fetch_fxrates(self, base: str, target: str) -> Optional[float]:
        """Fetch from FXRatesAPI (free)."""
        try:
            data = await self._fxrates.get(f"/latest?base={base}&currencies={target}")
            if data and data.get("success") and "rates" in data:
                return data["rates"].get(target)
        except Exception as exc:
            logger.debug(f"FXRatesAPI error: {exc}")
        return None

    async def _fetch_parallel_rate(self, country_code: str, base: str = "USD") -> Optional[dict]:
        """Fetch parallel/black market rate for special countries."""
        config = PARALLEL_RATE_COUNTRIES.get(country_code)
        if not config:
            return None

        source_domain = config["source"]
        try:
            if country_code == "LB":
                return await self._scrape_lirarate_lb(base)
            elif country_code == "SY":
                return await self._scrape_lirarate_sy(base)
            elif country_code == "DZ":
                return await self._scrape_cours_dz(base)
            else:
                return None
        except Exception as exc:
            logger.debug(f"Parallel rate error for {country_code}: {exc}")
            return None

    async def _scrape_lirarate_lb(self, base: str) -> Optional[dict]:
        """Scrape Lebanon parallel rate from lirarate.org."""
        try:
            html = await self._scraper.fetch_html("https://lirarate.org/")
            if html:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "lxml")
                rate_elements = soup.select(".rate-value, .exchange-rate, [class*='rate']")
                for el in rate_elements:
                    text = el.get_text(strip=True).replace(",", "")
                    try:
                        rate = float(text)
                        if 80000 < rate < 200000:
                            return {"rate": rate, "source": "lirarate.org"}
                    except ValueError:
                        continue
        except Exception as exc:
            logger.debug(f"Lebanon scrape error: {exc}")
        return None

    async def _scrape_lirarate_sy(self, base: str) -> Optional[dict]:
        """Scrape Syria parallel rate."""
        try:
            html = await self._scraper.fetch_html("https://lirarate.net/")
            if html:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "lxml")
                rate_elements = soup.select(".rate-value, [class*='rate'], [class*='price']")
                for el in rate_elements:
                    text = el.get_text(strip=True).replace(",", "")
                    try:
                        rate = float(text)
                        if 10000 < rate < 50000:
                            return {"rate": rate, "source": "lirarate.net"}
                    except ValueError:
                        continue
        except Exception as exc:
            logger.debug(f"Syria scrape error: {exc}")
        return None

    async def _scrape_cours_dz(self, base: str) -> Optional[dict]:
        """Scrape Algeria parallel rate."""
        try:
            html = await self._scraper.fetch_html("https://cours-dz.com/")
            if html:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "lxml")
                rate_elements = soup.select("td, .rate, [class*='price']")
                for el in rate_elements:
                    text = el.get_text(strip=True).replace(",", ".")
                    try:
                        rate = float(text)
                        if 200 < rate < 300:
                            return {"rate": rate, "source": "cours-dz.com"}
                    except ValueError:
                        continue
        except Exception as exc:
            logger.debug(f"Algeria scrape error: {exc}")
        return None

    async def close(self) -> None:
        await self._frankfurter.close()
        await self._exchangerate.close()
        await self._fxrates.close()
        await self._scraper.close()


omega_currency = OmegaCurrency()
