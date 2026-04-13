import logging
from typing import Optional

import httpx

from config import settings, LANGUAGES

logger = logging.getLogger(__name__)


class TranslationService:
    """Translation service with multiple fallback providers."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                limits=httpx.Limits(max_connections=10),
            )
        return self._client

    async def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> str:
        """Translate text with fallback chain."""
        if not text or not text.strip():
            return text

        if source_lang == target_lang:
            return text

        if settings.deepl_api_key:
            try:
                result = await self._translate_deepl(text, target_lang, source_lang)
                if result:
                    return result
            except Exception as exc:
                logger.debug(f"DeepL translation failed: {exc}")

        try:
            result = await self._translate_mymemory(text, target_lang, source_lang)
            if result:
                return result
        except Exception as exc:
            logger.debug(f"MyMemory translation failed: {exc}")

        try:
            result = await self._translate_lingva(text, target_lang, source_lang)
            if result:
                return result
        except Exception as exc:
            logger.debug(f"Lingva translation failed: {exc}")

        return text

    async def _translate_deepl(self, text: str, target: str, source: str) -> Optional[str]:
        """Translate using DeepL API."""
        client = await self._get_client()
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": settings.deepl_api_key,
            "text": text,
            "target_lang": target.upper()[:2],
        }
        if source and source != "auto":
            params["source_lang"] = source.upper()[:2]

        response = await client.post(url, data=params)
        response.raise_for_status()
        data = response.json()
        return data["translations"][0]["text"]

    async def _translate_mymemory(self, text: str, target: str, source: str) -> Optional[str]:
        """Translate using MyMemory free API."""
        client = await self._get_client()
        src = source if source != "auto" else "en"
        url = f"https://api.mymemory.translated.net/get?q={text[:500]}&langpair={src}|{target[:2]}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        translated = data.get("responseData", {}).get("translatedText", "")
        return translated if translated and translated != text else None

    async def _translate_lingva(self, text: str, target: str, source: str) -> Optional[str]:
        """Translate using Lingva (free, no key)."""
        client = await self._get_client()
        src = source if source != "auto" else "auto"
        url = f"https://lingva.ml/api/v1/{src}/{target[:2]}/{text[:500]}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("translation")

    async def detect_language(self, text: str) -> str:
        """Detect language of text."""
        import re
        from config import LANGUAGES

        arabic_pattern = re.compile(r"[\u0600-\u06FF\u0750-\u077F]+")
        if arabic_pattern.search(text) and len(arabic_pattern.findall(text)) >= 2:
            return "ar"

        persian_extra = re.compile(r"[\u06CC\u06AF\u067E\u0686]")
        if persian_extra.search(text):
            return "fa"

        hebrew_pattern = re.compile(r"[\u0590-\u05FF]+")
        if hebrew_pattern.search(text):
            return "he"

        cjk_pattern = re.compile(r"[\u4E00-\u9FFF]+")
        if cjk_pattern.search(text):
            return "zh-CN"

        japanese_pattern = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]+")
        if japanese_pattern.search(text):
            return "ja"

        korean_pattern = re.compile(r"[\uAC00-\uD7AF]+")
        if korean_pattern.search(text):
            return "ko"

        russian_pattern = re.compile(r"[\u0400-\u04FF]+")
        if russian_pattern.search(text):
            return "ru"

        return "en"

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


translation_service = TranslationService()
