import logging
import asyncio
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

IMAGE_SOURCES = [
    {"name": "unsplash", "url": "https://source.unsplash.com/featured/?{query}", "type": "redirect"},
    {"name": "picsum", "url": "https://picsum.photos/800/600", "type": "redirect"},
    {"name": "lorem_flickr", "url": "https://loremflickr.com/800/600/{query}", "type": "redirect"},
    {"name": "pollinations_image", "url": "https://image.pollinations.ai/prompt/{query}?width=800&height=600", "type": "direct"},
]


class OmegaImage:
    """Image generation service using multiple free sources."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(15.0),
                follow_redirects=True,
                limits=httpx.Limits(max_connections=10),
            )
        return self._client

    async def generate_image(self, prompt: str, style: str = "modern") -> Optional[str]:
        """Generate image URL from prompt."""
        client = await self._get_client()
        query = prompt.replace(" ", "+")

        for source in IMAGE_SOURCES:
            try:
                url = source["url"].format(query=query)

                if source["type"] == "direct":
                    return url

                response = await client.head(url, timeout=5.0)
                if response.status_code in (200, 301, 302):
                    final_url = str(response.headers.get("location", url))
                    return final_url if final_url.startswith("http") else url

            except Exception as exc:
                logger.debug(f"Image source {source['name']} failed: {exc}")
                continue

        return f"https://image.pollinations.ai/prompt/{query}?width=800&height=600"

    async def search_logos(self, company_name: str, style: str = "minimalist") -> list[str]:
        """Search for logo inspiration images."""
        prompt = f"{company_name} {style} logo design"
        urls = []

        for i in range(3):
            url = await self.generate_image(f"{prompt} variation {i+1}", style)
            if url:
                urls.append(url)

        return urls

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


omega_image = OmegaImage()
