import logging
import time
from typing import Any, Optional

import httpx

from services.circuit_breaker import circuit_breaker
from services.cache_service import cache, AdminAlert

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base class for all API clients with retry, circuit breaker, and caching."""

    def __init__(self, name: str, base_url: str = "", timeout: float = 10.0):
        self.name = name
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout, connect=5.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                follow_redirects=True,
            )
        return self._client

    async def get(self, url: str, params: Optional[dict] = None, headers: Optional[dict] = None, cache_key: Optional[str] = None, cache_ttl: Optional[int] = None) -> Optional[dict]:
        """HTTP GET with caching and circuit breaker."""
        if cache_key:
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached

        if not circuit_breaker.is_available(self.name):
            logger.warning(f"{self.name}: circuit open, skipping request")
            return None

        start = time.monotonic()
        try:
            client = await self._get_client()
            full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
            response = await client.get(full_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            circuit_breaker.record_success(self.name)
            await AdminAlert.report_success(self.name)
            elapsed = int((time.monotonic() - start) * 1000)
            logger.debug(f"{self.name} GET {url}: {response.status_code} in {elapsed}ms")

            if cache_key and cache_ttl:
                await cache.set(cache_key, data, ttl=cache_ttl)

            return data

        except httpx.HTTPStatusError as exc:
            circuit_breaker.record_failure(self.name)
            await AdminAlert.report_failure(self.name)
            logger.warning(f"{self.name} HTTP error: {exc.response.status_code}")
            return None
        except Exception as exc:
            circuit_breaker.record_failure(self.name)
            await AdminAlert.report_failure(self.name)
            logger.warning(f"{self.name} request error: {exc}")
            return None

    async def post(self, url: str, json_data: Optional[dict] = None, headers: Optional[dict] = None) -> Optional[dict]:
        """HTTP POST request."""
        if not circuit_breaker.is_available(self.name):
            return None

        try:
            client = await self._get_client()
            full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
            response = await client.post(full_url, json=json_data, headers=headers)
            response.raise_for_status()
            circuit_breaker.record_success(self.name)
            return response.json()
        except Exception as exc:
            circuit_breaker.record_failure(self.name)
            logger.warning(f"{self.name} POST error: {exc}")
            return None

    async def fetch_html(self, url: str, headers: Optional[dict] = None) -> Optional[str]:
        """Fetch raw HTML for scraping."""
        try:
            client = await self._get_client()
            default_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            if headers:
                default_headers.update(headers)
            response = await client.get(url, headers=default_headers)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            logger.warning(f"{self.name} HTML fetch error for {url}: {exc}")
            return None

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
