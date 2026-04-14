import asyncio
import logging
import time
from typing import Any, Optional

import httpx

from config import settings, AI_MODELS, PROVIDER_ENDPOINTS, PROVIDER_KEY_MAP
from services.circuit_breaker import circuit_breaker
from services.rate_limiter import check_api_rate

logger = logging.getLogger(__name__)


class OmegaQueryEngine:
    """Layer 1: Parallel query engine — calls multiple AI models simultaneously."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(15.0, connect=5.0),
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
                follow_redirects=True,
            )
        return self._client

    async def query_all(self, prompt: str, system_prompt: str = "", analysis: Optional[dict] = None) -> list[dict[str, Any]]:
        """Query all available models in parallel."""
        models = AI_MODELS
        if analysis and analysis.get("recommended_models"):
            model_ids = analysis["recommended_models"]
            model_map = {m["id"]: m for m in AI_MODELS}
            models = [model_map[mid] for mid in model_ids if mid in model_map]
            if not models:
                models = AI_MODELS

        tasks = []
        for model in models:
            if not circuit_breaker.is_available(model["id"]):
                logger.debug(f"Skipping {model['id']} — circuit open")
                continue
            tasks.append(self._query_single(model, prompt, system_prompt))

        if not tasks:
            logger.warning("No models available, using fallback")
            fallback = next((m for m in AI_MODELS if m["provider"] == "pollinations"), AI_MODELS[-1])
            tasks = [self._query_single(fallback, prompt, system_prompt)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        responses = []
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                responses.append(result)
            elif isinstance(result, Exception):
                logger.debug(f"Model query exception: {result}")

        logger.info(f"Query complete: {len(responses)}/{len(tasks)} models responded")
        return responses

    async def _query_single(self, model: dict, prompt: str, system_prompt: str) -> dict[str, Any]:
        """Query a single AI model."""
        model_id = model["id"]
        provider = model["provider"]
        model_name = model["model"]
        timeout = model.get("timeout", 5)
        start_time = time.monotonic()

        try:
            key_attr = PROVIDER_KEY_MAP.get(provider)
            api_key = getattr(settings, key_attr, "") if key_attr else ""

            if key_attr and not api_key:
                return {"success": False, "model_id": model_id, "error": "no_api_key"}

            if provider == "gemini":
                response_text = await self._call_gemini(model_name, prompt, system_prompt, api_key, timeout)
            elif provider == "cohere":
                response_text = await self._call_cohere(model_name, prompt, system_prompt, api_key, timeout)
            elif provider == "pollinations":
                response_text = await self._call_pollinations(prompt, system_prompt, timeout)
            else:
                endpoint = PROVIDER_ENDPOINTS.get(provider, "")
                response_text = await self._call_openai_compat(
                    endpoint, model_name, prompt, system_prompt, api_key, timeout, provider
                )

            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            circuit_breaker.record_success(model_id)

            return {
                "success": True,
                "model_id": model_id,
                "provider": provider,
                "text": response_text,
                "elapsed_ms": elapsed_ms,
                "tier": model.get("tier", 4),
            }

        except httpx.TimeoutException:
            circuit_breaker.record_failure(model_id)
            return {"success": False, "model_id": model_id, "error": "timeout"}
        except Exception as exc:
            circuit_breaker.record_failure(model_id)
            logger.debug(f"Error querying {model_id}: {exc}")
            return {"success": False, "model_id": model_id, "error": str(exc)}

    async def _call_openai_compat(self, endpoint: str, model: str, prompt: str, system_prompt: str, api_key: str, timeout: int, provider: str) -> str:
        """Call OpenAI-compatible API endpoint."""
        client = await self._get_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://omega-bot.onrender.com"
            headers["X-Title"] = "Omega Bot"

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
        }

        response = await client.post(endpoint, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_gemini(self, model: str, prompt: str, system_prompt: str, api_key: str, timeout: int) -> str:
        """Call Google Gemini API."""
        client = await self._get_client()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        parts = []
        if system_prompt:
            parts.append({"text": f"System: {system_prompt}\n\n{prompt}"})
        else:
            parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.7},
        }

        response = await client.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_cohere(self, model: str, prompt: str, system_prompt: str, api_key: str, timeout: int) -> str:
        """Call Cohere API."""
        client = await self._get_client()
        url = "https://api.cohere.ai/v2/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": model, "messages": messages, "max_tokens": 2048}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        response = await client.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"][0]["text"]

    async def _call_pollinations(self, prompt: str, system_prompt: str, timeout: int) -> str:
        """Call Pollinations API (no key needed)."""
        client = await self._get_client()
        url = "https://text.pollinations.ai/openai"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": "openai", "messages": messages, "max_tokens": 2048}

        response = await client.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


query_engine = OmegaQueryEngine()
