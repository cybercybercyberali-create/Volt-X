#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║              OMEGA BOT — Complete Project Setup              ║
║         Enterprise-Grade Telegram Bot (Free & Paid)          ║
║                                                              ║
║  Run: python setup.py                                        ║
║  Creates all project files automatically                     ║
╚══════════════════════════════════════════════════════════════╝
"""

FILES = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 1 — FOUNDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES["requirements.txt"] = """
aiogram==3.7.0
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy[asyncio]==2.0.31
aiosqlite==0.20.0
asyncpg==0.29.0
httpx==0.27.0
pydantic==2.7.4
pydantic-settings==2.3.4
structlog==24.2.0
python-dotenv==1.0.1
beautifulsoup4==4.12.3
lxml==5.2.2
reportlab==4.2.0
Pillow==10.3.0
aiofiles==23.2.1
diskcache==5.6.3
redis[hiredis]==5.0.7
yfinance==0.2.40
apscheduler==3.10.4
tenacity==8.4.1
cachetools==5.3.3
orjson==3.10.5
psutil==5.9.8
"""

FILES[".env.example"] = """
# ━━━ Required Keys (all free) ━━━
BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
DEEPSEEK_API_KEY=your_deepseek_key
CEREBRAS_API_KEY=your_cerebras_key
OPENROUTER_API_KEY=your_openrouter_key
COHERE_API_KEY=your_cohere_key
TMDB_API_KEY=your_tmdb_key
OPENWEATHER_API_KEY=your_openweather_key
FOOTBALL_DATA_KEY=your_football_data_key
METALS_API_KEY=your_metals_api_key
EXCHANGE_RATE_KEY=your_exchange_rate_key

# ━━━ Deployment ━━━
RENDER_PLAN=free
ADMIN_IDS=123456789
WEBHOOK_URL=https://your-app.onrender.com/webhook
PORT=10000

# ━━━ Optional Keys (improve quality) ━━━
OMDB_API_KEY=
DEEPL_API_KEY=
HUGGINGFACE_API_KEY=
TOGETHER_API_KEY=
MISTRAL_API_KEY=
NVIDIA_API_KEY=
SILICONFLOW_KEY=
GITHUB_TOKEN=
SAMBANOVA_API_KEY=
WEATHERAPI_KEY=
CURRENCY_API_KEY=
NEWSAPI_KEY=
GNEWS_API_KEY=
ALPHA_VANTAGE_KEY=
POLYGON_API_KEY=

# ━━━ Paid Plan Only ━━━
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://localhost:6379
"""

FILES["Procfile"] = """
web: uvicorn main:app --host 0.0.0.0 --port $PORT
"""

FILES["runtime.txt"] = """
python-3.11.9
"""

FILES["render.yaml"] = """
services:
  - type: web
    name: omega-bot
    runtime: python
    plan: free
    buildCommand: python setup.py && pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: RENDER_PLAN
        value: free
"""

FILES["config.py"] = r'''
import os
import sys
import psutil
import logging
from typing import Any, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

logger = logging.getLogger(__name__)


def _detect_plan() -> str:
    """Auto-detect Render plan based on available RAM."""
    explicit = os.getenv("RENDER_PLAN", "").strip().lower()
    if explicit in ("free", "paid"):
        return explicit
    try:
        ram_mb = psutil.virtual_memory().total / (1024 * 1024)
        plan = "paid" if ram_mb >= 1800 else "free"
        logger.info(f"Auto-detected plan: {plan} (RAM: {ram_mb:.0f}MB)")
        return plan
    except Exception:
        return "free"


RENDER_PLAN = _detect_plan()
IS_FREE = RENDER_PLAN == "free"
IS_PAID = RENDER_PLAN == "paid"
DATA_DIR = Path("/data") if Path("/data").exists() else Path("./data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Application settings with environment variable loading."""

    # ━━━ Bot ━━━
    bot_token: str = Field(default="", alias="BOT_TOKEN")
    admin_ids: str = Field(default="", alias="ADMIN_IDS")
    webhook_url: str = Field(default="", alias="WEBHOOK_URL")
    port: int = Field(default=10000, alias="PORT")
    render_plan: str = Field(default="free", alias="RENDER_PLAN")

    # ━━━ AI Keys ━━━
    groq_api_key: str = Field(default="", alias="GROQ_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    cerebras_api_key: str = Field(default="", alias="CEREBRAS_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    cohere_api_key: str = Field(default="", alias="COHERE_API_KEY")

    # ━━━ Service Keys ━━━
    tmdb_api_key: str = Field(default="", alias="TMDB_API_KEY")
    openweather_api_key: str = Field(default="", alias="OPENWEATHER_API_KEY")
    football_data_key: str = Field(default="", alias="FOOTBALL_DATA_KEY")
    metals_api_key: str = Field(default="", alias="METALS_API_KEY")
    goldapi_key: str = Field(default="", alias="GOLDAPI_KEY")
    exchange_rate_key: str = Field(default="", alias="EXCHANGE_RATE_KEY")

    # ━━━ Optional Keys ━━━
    omdb_api_key: str = Field(default="", alias="OMDB_API_KEY")
    deepl_api_key: str = Field(default="", alias="DEEPL_API_KEY")
    huggingface_api_key: str = Field(default="", alias="HUGGINGFACE_API_KEY")
    together_api_key: str = Field(default="", alias="TOGETHER_API_KEY")
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    nvidia_api_key: str = Field(default="", alias="NVIDIA_API_KEY")
    siliconflow_key: str = Field(default="", alias="SILICONFLOW_KEY")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    sambanova_api_key: str = Field(default="", alias="SAMBANOVA_API_KEY")
    weatherapi_key: str = Field(default="", alias="WEATHERAPI_KEY")
    currency_api_key: str = Field(default="", alias="CURRENCY_API_KEY")
    newsapi_key: str = Field(default="", alias="NEWSAPI_KEY")
    gnews_api_key: str = Field(default="", alias="GNEWS_API_KEY")
    alpha_vantage_key: str = Field(default="", alias="ALPHA_VANTAGE_KEY")
    polygon_api_key: str = Field(default="", alias="POLYGON_API_KEY")

    # ━━━ Database ━━━
    database_url: str = Field(default="", alias="DATABASE_URL")
    redis_url: str = Field(default="", alias="REDIS_URL")

    @property
    def admin_id_list(self) -> list[int]:
        """Parse admin IDs from comma-separated string."""
        if not self.admin_ids:
            return []
        try:
            return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]
        except ValueError:
            return []

    @property
    def db_url(self) -> str:
        """Get appropriate database URL based on plan."""
        if IS_PAID and self.database_url:
            return self.database_url
        return f"sqlite+aiosqlite:///{DATA_DIR}/omega.db"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite."""
        return "sqlite" in self.db_url

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI Models Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FREE_MODELS = [
    {"id": "groq/llama3-8b-8192", "provider": "groq", "model": "llama3-8b-8192", "tier": 1, "timeout": 10},
    {"id": "groq/llama3-3-70b", "provider": "groq", "model": "llama-3.3-70b-versatile", "tier": 1, "timeout": 10},
    {"id": "cerebras/llama3.1-70b", "provider": "cerebras", "model": "llama3.1-70b", "tier": 1, "timeout": 10},
    {"id": "gemini/gemini-2.0-flash", "provider": "gemini", "model": "gemini-2.0-flash", "tier": 1, "timeout": 12},
    {"id": "openrouter/llama-3.3-70b:free", "provider": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct:free", "tier": 2, "timeout": 15},
    {"id": "cohere/command-r", "provider": "cohere", "model": "command-r", "tier": 3, "timeout": 15},
    {"id": "pollinations/text", "provider": "pollinations", "model": "openai", "tier": 4, "timeout": 25},
]

PAID_MODELS = [
    # Tier 1 — Ultra Fast (2s timeout)
    {"id": "groq/llama3-8b-8192", "provider": "groq", "model": "llama3-8b-8192", "tier": 1, "timeout": 10},
    {"id": "groq/llama3-3-70b", "provider": "groq", "model": "llama-3.3-70b-versatile", "tier": 1, "timeout": 10},
    {"id": "groq/llama4-scout", "provider": "groq", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "tier": 1, "timeout": 10},
    {"id": "groq/mixtral-8x7b-32768", "provider": "groq", "model": "mixtral-8x7b-32768", "tier": 1, "timeout": 10},
    {"id": "groq/kimi-k2", "provider": "groq", "model": "moonshotai/kimi-k2-instruct", "tier": 1, "timeout": 2},
    {"id": "cerebras/llama3.1-70b", "provider": "cerebras", "model": "llama3.1-70b", "tier": 1, "timeout": 2},
    {"id": "cerebras/qwen3-235b", "provider": "cerebras", "model": "qwen3-235b", "tier": 1, "timeout": 2},
    {"id": "cerebras/gpt-oss-120b", "provider": "cerebras", "model": "gpt-oss-120b", "tier": 1, "timeout": 2},
    {"id": "gemini/gemini-2.5-flash", "provider": "gemini", "model": "gemini-2.0-flash", "tier": 1, "timeout": 3},
    {"id": "sambanova/llama3.3-70b", "provider": "sambanova", "model": "Meta-Llama-3.3-70B-Instruct", "tier": 1, "timeout": 2},
    # Tier 2 — Fast (4s timeout)
    {"id": "gemini/gemini-2.5-pro", "provider": "gemini", "model": "gemini-2.5-pro-preview-05-06", "tier": 2, "timeout": 4},
    {"id": "deepseek/deepseek-chat", "provider": "deepseek", "model": "deepseek-chat", "tier": 2, "timeout": 4},
    {"id": "deepseek/deepseek-reasoner", "provider": "deepseek", "model": "deepseek-reasoner", "tier": 2, "timeout": 4},
    {"id": "deepseek/deepseek-coder-v2", "provider": "deepseek", "model": "deepseek-coder", "tier": 2, "timeout": 4},
    {"id": "openrouter/llama-3-70b:free", "provider": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct:free", "tier": 2, "timeout": 4},
    {"id": "openrouter/qwen3-235b:free", "provider": "openrouter", "model": "qwen/qwen3-235b:free", "tier": 2, "timeout": 4},
    {"id": "openrouter/deepseek-r1:free", "provider": "openrouter", "model": "deepseek/deepseek-r1:free", "tier": 2, "timeout": 4},
    {"id": "openrouter/gemma-3-27b:free", "provider": "openrouter", "model": "google/gemma-3-27b-it:free", "tier": 2, "timeout": 4},
    {"id": "openrouter/phi-4:free", "provider": "openrouter", "model": "microsoft/phi-4:free", "tier": 2, "timeout": 4},
    {"id": "openrouter/mythomist-7b:free", "provider": "openrouter", "model": "gryphe/mythomist-7b:free", "tier": 2, "timeout": 4},
    # Tier 3 — Medium (6s timeout)
    {"id": "cohere/command-r-plus", "provider": "cohere", "model": "command-r-plus", "tier": 3, "timeout": 6},
    {"id": "cohere/command-r", "provider": "cohere", "model": "command-r", "tier": 3, "timeout": 6},
    {"id": "mistral/mistral-small-latest", "provider": "mistral", "model": "mistral-small-latest", "tier": 3, "timeout": 6},
    {"id": "nvidia/llama3.3-70b", "provider": "nvidia", "model": "meta/llama-3.3-70b-instruct", "tier": 3, "timeout": 6},
    {"id": "nvidia/mistral-large", "provider": "nvidia", "model": "mistralai/mistral-large-2-instruct", "tier": 3, "timeout": 6},
    {"id": "nvidia/qwen3-235b", "provider": "nvidia", "model": "qwen/qwen3-235b-instruct", "tier": 3, "timeout": 6},
    {"id": "siliconflow/qwen3-8b", "provider": "siliconflow", "model": "Qwen/Qwen3-8B", "tier": 3, "timeout": 6},
    {"id": "siliconflow/deepseek-r1-distill", "provider": "siliconflow", "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", "tier": 3, "timeout": 6},
    {"id": "cloudflare/llama3.3-70b", "provider": "cloudflare", "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "tier": 3, "timeout": 6},
    {"id": "cloudflare/qwq-32b", "provider": "cloudflare", "model": "@cf/qwen/qwq-32b", "tier": 3, "timeout": 6},
    {"id": "github/gpt-4o", "provider": "github", "model": "gpt-4o", "tier": 3, "timeout": 6},
    {"id": "github/llama-3.3-70b", "provider": "github", "model": "Meta-Llama-3.3-70B-Instruct", "tier": 3, "timeout": 6},
    {"id": "github/deepseek-r1", "provider": "github", "model": "DeepSeek-R1", "tier": 3, "timeout": 6},
    # Tier 4 — Slow but reliable (8s timeout)
    {"id": "huggingface/mixtral-8x7b", "provider": "huggingface", "model": "mistralai/Mixtral-8x7B-Instruct-v0.1", "tier": 4, "timeout": 8},
    {"id": "huggingface/qwen2.5-72b", "provider": "huggingface", "model": "Qwen/Qwen2.5-72B-Instruct", "tier": 4, "timeout": 8},
    {"id": "together/llama-3-70b", "provider": "together", "model": "meta-llama/Llama-3-70b-chat-hf", "tier": 4, "timeout": 8},
    {"id": "fireworks/llama-v3p3-70b", "provider": "fireworks", "model": "accounts/fireworks/models/llama-v3p3-70b-instruct", "tier": 4, "timeout": 8},
    {"id": "fireworks/deepseek-v3", "provider": "fireworks", "model": "accounts/fireworks/models/deepseek-v3", "tier": 4, "timeout": 8},
    {"id": "hyperbolic/deepseek-v3.1", "provider": "hyperbolic", "model": "deepseek-ai/DeepSeek-V3-0324", "tier": 4, "timeout": 8},
    {"id": "kluster/deepseek-r1", "provider": "kluster", "model": "deepseek-r1", "tier": 4, "timeout": 8},
    {"id": "llm7/deepseek-r1", "provider": "llm7", "model": "deepseek-r1", "tier": 4, "timeout": 8},
    {"id": "pollinations/text", "provider": "pollinations", "model": "openai", "tier": 4, "timeout": 8},
]

AI_MODELS = FREE_MODELS if IS_FREE else PAID_MODELS


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Provider API Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROVIDER_ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "cerebras": "https://api.cerebras.ai/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "cohere": "https://api.cohere.ai/v2/chat",
    "mistral": "https://api.mistral.ai/v1/chat/completions",
    "nvidia": "https://integrate.api.nvidia.com/v1/chat/completions",
    "siliconflow": "https://api.siliconflow.cn/v1/chat/completions",
    "cloudflare": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}",
    "github": "https://models.inference.ai.azure.com/chat/completions",
    "huggingface": "https://api-inference.huggingface.co/models/{model}/v1/chat/completions",
    "together": "https://api.together.xyz/v1/chat/completions",
    "fireworks": "https://api.fireworks.ai/inference/v1/chat/completions",
    "hyperbolic": "https://api.hyperbolic.xyz/v1/chat/completions",
    "kluster": "https://api.kluster.ai/v1/chat/completions",
    "llm7": "https://api.llm7.io/v1/chat/completions",
    "sambanova": "https://api.sambanova.ai/v1/chat/completions",
    "pollinations": "https://text.pollinations.ai/openai",
}

PROVIDER_KEY_MAP = {
    "groq": "groq_api_key",
    "cerebras": "cerebras_api_key",
    "gemini": "gemini_api_key",
    "deepseek": "deepseek_api_key",
    "openrouter": "openrouter_api_key",
    "cohere": "cohere_api_key",
    "mistral": "mistral_api_key",
    "nvidia": "nvidia_api_key",
    "siliconflow": "siliconflow_key",
    "github": "github_token",
    "huggingface": "huggingface_api_key",
    "together": "together_api_key",
    "fireworks": "together_api_key",
    "hyperbolic": "together_api_key",
    "kluster": "together_api_key",
    "llm7": "together_api_key",
    "sambanova": "sambanova_api_key",
    "pollinations": None,
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cache TTL Configuration (seconds)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CACHE_TTL = {
    "gold": 300,
    "currency": 600,
    "lbp_rate": 900,
    "weather_current": 1800,
    "weather_forecast": 3600,
    "football_static": 3600,
    "football_live": 60,
    "stocks": 300,
    "crypto": 120,
    "news": 1800,
    "movies": 86400,
    "fuel": 21600,
    "fuel_lebanon": 604800,
    "ai_factual": 3600,
    "ai_creative": 86400,
    "flights": 300,
    "quakes": 600,
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# i18n — 40 Languages
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANGUAGES = {
    "ar": {"name": "العربية", "flag": "🇸🇦", "rtl": True, "dir": "rtl"},
    "en": {"name": "English", "flag": "🇺🇸", "rtl": False, "dir": "ltr"},
    "fr": {"name": "Français", "flag": "🇫🇷", "rtl": False, "dir": "ltr"},
    "es": {"name": "Español", "flag": "🇪🇸", "rtl": False, "dir": "ltr"},
    "pt": {"name": "Português", "flag": "🇧🇷", "rtl": False, "dir": "ltr"},
    "de": {"name": "Deutsch", "flag": "🇩🇪", "rtl": False, "dir": "ltr"},
    "it": {"name": "Italiano", "flag": "🇮🇹", "rtl": False, "dir": "ltr"},
    "ru": {"name": "Русский", "flag": "🇷🇺", "rtl": False, "dir": "ltr"},
    "tr": {"name": "Türkçe", "flag": "🇹🇷", "rtl": False, "dir": "ltr"},
    "fa": {"name": "فارسی", "flag": "🇮🇷", "rtl": True, "dir": "rtl"},
    "ur": {"name": "اردو", "flag": "🇵🇰", "rtl": True, "dir": "rtl"},
    "hi": {"name": "हिन्दी", "flag": "🇮🇳", "rtl": False, "dir": "ltr"},
    "bn": {"name": "বাংলা", "flag": "🇧🇩", "rtl": False, "dir": "ltr"},
    "pa": {"name": "ਪੰਜਾਬੀ", "flag": "🇮🇳", "rtl": False, "dir": "ltr"},
    "id": {"name": "Indonesia", "flag": "🇮🇩", "rtl": False, "dir": "ltr"},
    "ms": {"name": "Melayu", "flag": "🇲🇾", "rtl": False, "dir": "ltr"},
    "zh-CN": {"name": "简体中文", "flag": "🇨🇳", "rtl": False, "dir": "ltr"},
    "zh-TW": {"name": "繁體中文", "flag": "🇹🇼", "rtl": False, "dir": "ltr"},
    "ja": {"name": "日本語", "flag": "🇯🇵", "rtl": False, "dir": "ltr"},
    "ko": {"name": "한국어", "flag": "🇰🇷", "rtl": False, "dir": "ltr"},
    "nl": {"name": "Nederlands", "flag": "🇳🇱", "rtl": False, "dir": "ltr"},
    "pl": {"name": "Polski", "flag": "🇵🇱", "rtl": False, "dir": "ltr"},
    "sv": {"name": "Svenska", "flag": "🇸🇪", "rtl": False, "dir": "ltr"},
    "no": {"name": "Norsk", "flag": "🇳🇴", "rtl": False, "dir": "ltr"},
    "da": {"name": "Dansk", "flag": "🇩🇰", "rtl": False, "dir": "ltr"},
    "fi": {"name": "Suomi", "flag": "🇫🇮", "rtl": False, "dir": "ltr"},
    "el": {"name": "Ελληνικά", "flag": "🇬🇷", "rtl": False, "dir": "ltr"},
    "he": {"name": "עברית", "flag": "🇮🇱", "rtl": True, "dir": "rtl"},
    "ro": {"name": "Română", "flag": "🇷🇴", "rtl": False, "dir": "ltr"},
    "hu": {"name": "Magyar", "flag": "🇭🇺", "rtl": False, "dir": "ltr"},
    "cs": {"name": "Čeština", "flag": "🇨🇿", "rtl": False, "dir": "ltr"},
    "sk": {"name": "Slovenčina", "flag": "🇸🇰", "rtl": False, "dir": "ltr"},
    "th": {"name": "ไทย", "flag": "🇹🇭", "rtl": False, "dir": "ltr"},
    "vi": {"name": "Tiếng Việt", "flag": "🇻🇳", "rtl": False, "dir": "ltr"},
    "sw": {"name": "Kiswahili", "flag": "🇰🇪", "rtl": False, "dir": "ltr"},
    "am": {"name": "አማርኛ", "flag": "🇪🇹", "rtl": False, "dir": "ltr"},
    "ha": {"name": "Hausa", "flag": "🇳🇬", "rtl": False, "dir": "ltr"},
    "yo": {"name": "Yorùbá", "flag": "🇳🇬", "rtl": False, "dir": "ltr"},
    "az": {"name": "Azərbaycan", "flag": "🇦🇿", "rtl": False, "dir": "ltr"},
    "uz": {"name": "Oʻzbek", "flag": "🇺🇿", "rtl": False, "dir": "ltr"},
    "kk": {"name": "Қазақ", "flag": "🇰🇿", "rtl": False, "dir": "ltr"},
}

ARABIC_DIALECTS = {
    "ar-gulf": {"name": "خليجي", "countries": ["SA", "AE", "KW", "QA", "BH", "OM"]},
    "ar-egypt": {"name": "مصري", "countries": ["EG"]},
    "ar-levant": {"name": "شامي", "countries": ["LB", "SY", "JO", "PS"]},
    "ar-maghreb": {"name": "مغاربي", "countries": ["MA", "DZ", "TN", "LY"]},
    "ar-iraq": {"name": "عراقي", "countries": ["IQ"]},
    "ar-yemen": {"name": "يمني", "countries": ["YE"]},
    "ar-sudan": {"name": "سوداني", "countries": ["SD"]},
}

RTL_LANGUAGES = {"ar", "he", "fa", "ur"}

# ━━━ Core Translations (expandable) ━━━
I18N = {
    "welcome": {
        "ar": "مرحباً {name}! 👋\nأنا أوميغا — أذكى بوت في تلغرام.\nاختر خدمة من القائمة أو اسألني أي شيء!",
        "en": "Welcome {name}! 👋\nI'm Omega — the smartest Telegram bot.\nPick a service or ask me anything!",
        "fr": "Bienvenue {name}! 👋\nJe suis Omega — le bot Telegram le plus intelligent.\nChoisissez un service ou posez-moi une question!",
        "es": "¡Bienvenido {name}! 👋\nSoy Omega — el bot de Telegram más inteligente.\n¡Elige un servicio o pregúntame lo que quieras!",
        "tr": "Hoş geldin {name}! 👋\nBen Omega — en akıllı Telegram botu.\nBir hizmet seç veya bana bir şey sor!",
        "ru": "Добро пожаловать {name}! 👋\nЯ Omega — самый умный бот Telegram.\nВыберите услугу или задайте мне вопрос!",
        "fa": "خوش آمدید {name}! 👋\nمن امگا هستم — باهوش‌ترین ربات تلگرام.\nیک سرویس انتخاب کنید یا هر چیزی بپرسید!",
        "de": "Willkommen {name}! 👋\nIch bin Omega — der smarteste Telegram-Bot.\nWähle einen Service oder frag mich was!",
        "hi": "स्वागत है {name}! 👋\nमैं ओमेगा हूँ — टेलीग्राम का सबसे स्मार्ट बॉट।\nकोई सेवा चुनें या मुझसे कुछ भी पूछें!",
        "zh-CN": "欢迎 {name}！👋\n我是 Omega — 最智能的 Telegram 机器人。\n选择服务或问我任何问题！",
    },
    "main_menu": {
        "ar": "📋 القائمة الرئيسية",
        "en": "📋 Main Menu",
        "fr": "📋 Menu Principal",
        "es": "📋 Menú Principal",
        "tr": "📋 Ana Menü",
        "ru": "📋 Главное Меню",
    },
    "loading": {
        "ar": "⏳ جاري التحميل...",
        "en": "⏳ Loading...",
        "fr": "⏳ Chargement...",
        "es": "⏳ Cargando...",
        "tr": "⏳ Yükleniyor...",
        "ru": "⏳ Загрузка...",
    },
    "error": {
        "ar": "❌ حدث خطأ. يرجى المحاولة لاحقاً.",
        "en": "❌ An error occurred. Please try again later.",
        "fr": "❌ Une erreur est survenue. Veuillez réessayer.",
        "es": "❌ Ocurrió un error. Inténtalo de nuevo.",
        "tr": "❌ Bir hata oluştu. Lütfen tekrar deneyin.",
        "ru": "❌ Произошла ошибка. Попробуйте позже.",
    },
    "gold_title": {
        "ar": "🪙 أسعار الذهب والمعادن",
        "en": "🪙 Gold & Metals Prices",
    },
    "currency_title": {
        "ar": "💱 أسعار العملات",
        "en": "💱 Currency Exchange Rates",
    },
    "fuel_title": {
        "ar": "⛽ أسعار المحروقات",
        "en": "⛽ Fuel Prices",
    },
    "weather_title": {
        "ar": "🌤 حالة الطقس",
        "en": "🌤 Weather",
    },
    "football_title": {
        "ar": "⚽ كرة القدم",
        "en": "⚽ Football",
    },
    "movies_title": {
        "ar": "🎬 أفلام ومسلسلات",
        "en": "🎬 Movies & TV Shows",
    },
    "cv_title": {
        "ar": "📄 إنشاء سيرة ذاتية",
        "en": "📄 CV Generator",
    },
    "logo_title": {
        "ar": "🎨 تصميم شعار",
        "en": "🎨 Logo Generator",
    },
    "ai_title": {
        "ar": "🤖 مساعد AI الذكي",
        "en": "🤖 AI Smart Assistant",
    },
    "stocks_title": {
        "ar": "📈 الأسهم والبورصة",
        "en": "📈 Stocks & Markets",
    },
    "crypto_title": {
        "ar": "₿ العملات الرقمية",
        "en": "₿ Cryptocurrency",
    },
    "news_title": {
        "ar": "📰 الأخبار",
        "en": "📰 News",
    },
    "flights_title": {
        "ar": "✈️ تتبع الرحلات",
        "en": "✈️ Flight Tracker",
    },
    "quakes_title": {
        "ar": "🌋 تنبيهات الزلازل",
        "en": "🌋 Earthquake Alerts",
    },
    "settings_title": {
        "ar": "⚙️ الإعدادات",
        "en": "⚙️ Settings",
    },
    # ━━━ Sub-keys: Gold ━━━
    "gold_price": {
        "ar": "🪙 **سعر الذهب**\n\n💰 الأونصة: ${price}",
        "en": "🪙 **Gold Price**\n\n💰 Ounce: ${price}",
        "fr": "🪙 **Prix de l'or**\n\n💰 Once: ${price}",
        "es": "🪙 **Precio del oro**\n\n💰 Onza: ${price}",
        "tr": "🪙 **Altın Fiyatı**\n\n💰 Ons: ${price}",
        "ru": "🪙 **Цена золота**\n\n💰 Унция: ${price}",
        "fa": "🪙 **قیمت طلا**\n\n💰 اونس: ${price}",
        "de": "🪙 **Goldpreis**\n\n💰 Unze: ${price}",
        "hi": "🪙 **सोने की कीमत**\n\n💰 औंस: ${price}",
        "zh-CN": "🪙 **黄金价格**\n\n💰 盎司: ${price}",
    },
    "gold_karats_btn": {
        "ar": "💍 أسعار العيارات", "en": "💍 Karat Prices", "fr": "💍 Prix des carats",
        "es": "💍 Precios por quilate", "tr": "💍 Ayar Fiyatları", "ru": "💍 Цены по каратам",
        "fa": "💍 قیمت عیارها", "de": "💍 Karatpreise", "hi": "💍 कैरट मूल्य", "zh-CN": "💍 克拉价格",
    },
    "gold_karats_title": {
        "ar": "💍 **أسعار عيارات الذهب (لكل غرام)**",
        "en": "💍 **Gold Karat Prices (per gram)**",
        "fr": "💍 **Prix des carats d'or (par gramme)**",
        "es": "💍 **Precios por quilate de oro (por gramo)**",
        "tr": "💍 **Altın Ayar Fiyatları (gram başına)**",
        "ru": "💍 **Цены по каратам золота (за грамм)**",
        "fa": "💍 **قیمت عیارهای طلا (هر گرم)**",
        "de": "💍 **Goldpreise nach Karat (pro Gramm)**",
        "hi": "💍 **सोने के कैरट मूल्य (प्रति ग्राम)**",
        "zh-CN": "💍 **黄金克拉价格（每克）**",
    },
    "btn_refresh": {
        "ar": "🔄 تحديث", "en": "🔄 Refresh", "fr": "🔄 Actualiser",
        "es": "🔄 Actualizar", "tr": "🔄 Yenile", "ru": "🔄 Обновить",
        "fa": "🔄 بروزرسانی", "de": "🔄 Aktualisieren", "hi": "🔄 ताज़ा करें", "zh-CN": "🔄 刷新",
    },
    "btn_silver": {
        "ar": "🥈 فضة", "en": "🥈 Silver", "fr": "🥈 Argent",
        "es": "🥈 Plata", "tr": "🥈 Gümüş", "ru": "🥈 Серебро",
        "fa": "🥈 نقره", "de": "🥈 Silber", "hi": "🥈 चाँदी", "zh-CN": "🥈 白银",
    },
    "btn_platinum": {
        "ar": "💎 بلاتينيوم", "en": "💎 Platinum", "fr": "💎 Platine",
        "es": "💎 Platino", "tr": "💎 Platin", "ru": "💎 Платина",
        "fa": "💎 پلاتین", "de": "💎 Platin", "hi": "💎 प्लैटिनम", "zh-CN": "💎 铂金",
    },
    # ━━━ Sub-keys: Currency ━━━
    "currency_rate": {
        "ar": "💱 **{base} → {target}**\n\n💰 السعر: {rate}",
        "en": "💱 **{base} → {target}**\n\n💰 Rate: {rate}",
        "fr": "💱 **{base} → {target}**\n\n💰 Taux: {rate}",
        "es": "💱 **{base} → {target}**\n\n💰 Tasa: {rate}",
        "tr": "💱 **{base} → {target}**\n\n💰 Kur: {rate}",
        "ru": "💱 **{base} → {target}**\n\n💰 Курс: {rate}",
    },
    "currency_parallel": {
        "ar": "⚠️ **السعر الموازي:** {rate}", "en": "⚠️ **Parallel rate:** {rate}",
        "fr": "⚠️ **Taux parallèle:** {rate}", "es": "⚠️ **Tasa paralela:** {rate}",
        "tr": "⚠️ **Paralel kur:** {rate}", "ru": "⚠️ **Параллельный курс:** {rate}",
    },
    # ━━━ Sub-keys: Weather ━━━
    "weather_result": {
        "ar": "🌤 **الطقس في {city}**\n\n🌡 الحرارة: {temp}°C\n🤔 الإحساس: {feels}°C\n💧 الرطوبة: {humidity}%\n💨 الرياح: {wind} km/h\n📝 {desc}",
        "en": "🌤 **Weather in {city}**\n\n🌡 Temp: {temp}°C\n🤔 Feels: {feels}°C\n💧 Humidity: {humidity}%\n💨 Wind: {wind} km/h\n📝 {desc}",
        "fr": "🌤 **Météo à {city}**\n\n🌡 Temp: {temp}°C\n💧 Humidité: {humidity}%\n💨 Vent: {wind} km/h\n📝 {desc}",
        "es": "🌤 **Clima en {city}**\n\n🌡 Temp: {temp}°C\n💧 Humedad: {humidity}%\n💨 Viento: {wind} km/h\n📝 {desc}",
        "tr": "🌤 **{city} Hava Durumu**\n\n🌡 Sıcaklık: {temp}°C\n💧 Nem: {humidity}%\n💨 Rüzgar: {wind} km/h\n📝 {desc}",
        "ru": "🌤 **Погода в {city}**\n\n🌡 Темп: {temp}°C\n💧 Влажность: {humidity}%\n💨 Ветер: {wind} км/ч\n📝 {desc}",
    },
    # ━━━ Sub-keys: Football ━━━
    "fb_choose_league": {
        "ar": "⚽ **اختر الدوري:**", "en": "⚽ **Choose league:**",
        "fr": "⚽ **Choisir la ligue:**", "es": "⚽ **Elige la liga:**",
        "tr": "⚽ **Lig seçin:**", "ru": "⚽ **Выберите лигу:**",
    },
    "fb_live_btn": {
        "ar": "🔴 مباشر", "en": "🔴 Live", "fr": "🔴 En direct",
        "es": "🔴 En vivo", "tr": "🔴 Canlı", "ru": "🔴 Живой",
    },
    "fb_no_live": {
        "ar": "⚽ لا توجد مباريات مباشرة حالياً", "en": "⚽ No live matches right now",
        "fr": "⚽ Aucun match en direct", "es": "⚽ No hay partidos en vivo",
        "tr": "⚽ Şu anda canlı maç yok", "ru": "⚽ Нет матчей в прямом эфире",
    },
    # ━━━ Sub-keys: Stocks ━━━
    "stock_result": {
        "ar": "📊 **{name} ({symbol})**\n\n💰 السعر: ${price}\n{emoji} التغير: {change} ({pct}%)\n📊 الحجم: {volume}",
        "en": "📊 **{name} ({symbol})**\n\n💰 Price: ${price}\n{emoji} Change: {change} ({pct}%)\n📊 Volume: {volume}",
    },
    # ━━━ Sub-keys: Crypto ━━━
    "crypto_result": {
        "ar": "₿ **{name} ({symbol})**\n\n💰 السعر: ${price}\n{emoji} 24h: {change}%\n🏆 الترتيب: #{rank}\n📊 القيمة السوقية: ${mcap}",
        "en": "₿ **{name} ({symbol})**\n\n💰 Price: ${price}\n{emoji} 24h: {change}%\n🏆 Rank: #{rank}\n📊 Market Cap: ${mcap}",
    },
    # ━━━ Sub-keys: Common ━━━
    "fetching": {
        "ar": "⏳ جاري جلب البيانات...", "en": "⏳ Fetching data...",
        "fr": "⏳ Chargement...", "es": "⏳ Cargando datos...",
        "tr": "⏳ Veriler yükleniyor...", "ru": "⏳ Загрузка данных...",
        "fa": "⏳ در حال بارگذاری...", "de": "⏳ Daten laden...",
        "hi": "⏳ डेटा लोड हो रहा है...", "zh-CN": "⏳ 正在加载...",
    },
    "not_found": {
        "ar": "❌ لم نجد نتائج", "en": "❌ No results found",
        "fr": "❌ Aucun résultat", "es": "❌ Sin resultados",
        "tr": "❌ Sonuç bulunamadı", "ru": "❌ Ничего не найдено",
    },
    "send_city": {
        "ar": "🌤 أرسل اسم المدينة:", "en": "🌤 Send city name:",
        "fr": "🌤 Envoyez le nom de la ville:", "es": "🌤 Envía el nombre de la ciudad:",
        "tr": "🌤 Şehir adını gönderin:", "ru": "🌤 Отправьте название города:",
    },
    # ━━━ Sub-keys: Start & Help ━━━
    "help_text": {
        "ar": "🤖 **Omega Bot**\n\nالأوامر:\n/gold — ذهب\n/currency USD EUR — عملات\n/fuel LB — محروقات\n/weather London — طقس\n/football PL — كرة قدم\n/movie Inception — أفلام\n/cv — سيرة ذاتية\n/logo — شعار\n/stock AAPL — أسهم\n/crypto bitcoin — كريبتو\n/news — أخبار\n/flight LH400 — رحلات\n/quakes — زلازل\n/settings — إعدادات\n\nأو أرسل أي سؤال مباشرة!",
        "en": "🤖 **Omega Bot**\n\nCommands:\n/gold — Gold prices\n/currency USD EUR — Exchange\n/fuel LB — Fuel prices\n/weather London — Weather\n/football PL — Football\n/movie Inception — Movies\n/cv — Generate CV\n/logo — Logo design\n/stock AAPL — Stocks\n/crypto bitcoin — Crypto\n/news — Headlines\n/flight LH400 — Flights\n/quakes — Earthquakes\n/settings — Settings\n\nOr just type any question!",
        "fr": "🤖 **Omega Bot**\n\nCommandes:\n/gold — Or\n/currency — Devises\n/weather — Météo\n/news — Actualités\n/settings — Paramètres\n\nOu posez une question!",
        "tr": "🤖 **Omega Bot**\n\nKomutlar:\n/gold — Altın\n/currency — Döviz\n/weather — Hava\n/news — Haberler\n/settings — Ayarlar\n\nVeya bir soru yazın!",
        "ru": "🤖 **Omega Bot**\n\nКоманды:\n/gold — Золото\n/currency — Валюты\n/weather — Погода\n/news — Новости\n/settings — Настройки\n\nИли задайте вопрос!",
    },
    "admin_only": {
        "ar": "⛔ هذا الأمر للمشرفين فقط", "en": "⛔ Admin only",
        "fr": "⛔ Réservé aux admins", "tr": "⛔ Sadece yöneticiler", "ru": "⛔ Только для админов",
    },
    # ━━━ Sub-keys: Currency detail ━━━
    "currency_rates_title": {
        "ar": "💱 **أسعار {base}**", "en": "💱 **{base} Rates**",
        "fr": "💱 **Taux {base}**", "tr": "💱 **{base} Kurları**", "ru": "💱 **Курсы {base}**",
    },
    # ━━━ Sub-keys: Fuel ━━━
    "fuel_title_country": {
        "ar": "⛽ **أسعار المحروقات — {country}**", "en": "⛽ **Fuel Prices — {country}**",
        "fr": "⛽ **Prix carburant — {country}**", "tr": "⛽ **Yakıt — {country}**", "ru": "⛽ **Топливо — {country}**",
    },
    # ━━━ Sub-keys: Movies ━━━
    "trending_title": {
        "ar": "🎬 **الأفلام الرائجة:**", "en": "🎬 **Trending Movies:**",
        "fr": "🎬 **Films tendance:**", "tr": "🎬 **Trend Filmler:**", "ru": "🎬 **Популярные фильмы:**",
    },
    "search_hint": {
        "ar": "🔍 للبحث: /movie اسم الفيلم", "en": "🔍 Search: /movie name",
        "fr": "🔍 Chercher: /movie nom", "tr": "🔍 Ara: /movie isim", "ru": "🔍 Поиск: /movie название",
    },
    "btn_details": {
        "ar": "📋 تفاصيل", "en": "📋 Details", "fr": "📋 Détails",
        "tr": "📋 Detaylar", "ru": "📋 Детали",
    },
    "btn_favorite": {
        "ar": "➕ المفضلة", "en": "➕ Favorite", "fr": "➕ Favoris",
        "tr": "➕ Favori", "ru": "➕ Избранное",
    },
    # ━━━ Sub-keys: News ━━━
    "news_headline": {
        "ar": "📰 **آخر الأخبار:**", "en": "📰 **Latest News:**",
        "fr": "📰 **Dernières nouvelles:**", "tr": "📰 **Son Haberler:**", "ru": "📰 **Последние новости:**",
    },
    "read_more": {
        "ar": "🔗 اقرأ المزيد", "en": "🔗 Read more", "fr": "🔗 Lire la suite",
        "tr": "🔗 Devamını oku", "ru": "🔗 Читать далее",
    },
    # ━━━ Sub-keys: Crypto ━━━
    "crypto_top_title": {
        "ar": "₿ **العملات الرقمية:**", "en": "₿ **Cryptocurrencies:**",
        "fr": "₿ **Cryptomonnaies:**", "tr": "₿ **Kripto Paralar:**", "ru": "₿ **Криптовалюты:**",
    },
    "crypto_detail_hint": {
        "ar": "🔍 للتفاصيل: /crypto bitcoin", "en": "🔍 Details: /crypto bitcoin",
        "fr": "🔍 Détails: /crypto bitcoin", "tr": "🔍 Detay: /crypto bitcoin",
    },
    # ━━━ Sub-keys: Stocks ━━━
    "stock_send_symbol": {
        "ar": "📈 أرسل رمز السهم: /stock AAPL", "en": "📈 Send symbol: /stock AAPL",
        "fr": "📈 Envoyez le symbole: /stock AAPL", "tr": "📈 Sembol gönderin: /stock AAPL",
    },
    # ━━━ Sub-keys: Flights ━━━
    "flight_send": {
        "ar": "✈️ أرسل رقم الرحلة أو رمز المطار:\n/flight LH400\n/flight EGLL",
        "en": "✈️ Send flight number or airport code:\n/flight LH400\n/flight EGLL",
        "fr": "✈️ Envoyez le numéro de vol:\n/flight LH400\n/flight EGLL",
        "tr": "✈️ Uçuş numarası gönderin:\n/flight LH400\n/flight EGLL",
    },
    # ━━━ Sub-keys: AI ━━━
    "ai_intro": {
        "ar": "🤖 **مساعد AI الذكي**\n\nاكتب سؤالك بعد /ai\nأو أرسل أي رسالة مباشرة!",
        "en": "🤖 **AI Smart Assistant**\n\nType your question after /ai\nOr just send any message!",
        "fr": "🤖 **Assistant IA**\n\nÉcrivez après /ai\nOu envoyez un message!",
        "tr": "🤖 **AI Asistan**\n\n/ai sonrası sorunuzu yazın\nVeya direkt mesaj gönderin!",
    },
    # ━━━ Sub-keys: CV ━━━
    "cv_intro": {
        "ar": "📄 **إنشاء سيرة ذاتية احترافية**\n\nسأطلب منك 9 معلومات.",
        "en": "📄 **Professional CV Generator**\n\nI will ask you 9 questions.",
        "fr": "📄 **Générateur de CV**\n\n9 questions à remplir.",
        "tr": "📄 **Profesyonel CV Oluşturucu**\n\n9 soru soracağım.",
    },
    "cv_step": {
        "ar": "{n}️⃣ **الخطوة {n}/9:** {q}", "en": "{n}️⃣ **Step {n}/9:** {q}",
        "fr": "{n}️⃣ **Étape {n}/9:** {q}", "tr": "{n}️⃣ **Adım {n}/9:** {q}",
    },
    "cv_q_name": {"ar": "ما اسمك الكامل؟", "en": "What is your full name?", "fr": "Votre nom complet?", "tr": "Tam adınız?"},
    "cv_q_email": {"ar": "ما بريدك الإلكتروني؟", "en": "Your email?", "fr": "Votre email?", "tr": "E-posta adresiniz?"},
    "cv_q_phone": {"ar": "ما رقم هاتفك؟", "en": "Your phone number?", "fr": "Votre téléphone?", "tr": "Telefon numaranız?"},
    "cv_q_summary": {"ar": "اكتب ملخصاً عن نفسك:", "en": "Write a short bio:", "fr": "Résumé personnel:", "tr": "Kendinizi tanıtın:"},
    "cv_q_experience": {"ar": "خبراتك العملية:", "en": "Work experience:", "fr": "Expérience:", "tr": "İş deneyimi:"},
    "cv_q_education": {"ar": "شهاداتك:", "en": "Education:", "fr": "Formation:", "tr": "Eğitim:"},
    "cv_q_skills": {"ar": "مهاراتك:", "en": "Skills:", "fr": "Compétences:", "tr": "Yetenekler:"},
    "cv_q_languages": {"ar": "اللغات التي تتحدثها:", "en": "Languages you speak:", "fr": "Langues parlées:", "tr": "Bildiğiniz diller:"},
    "cv_q_template": {"ar": "اختر قالب (1-5):", "en": "Choose template (1-5):", "fr": "Choisir modèle (1-5):", "tr": "Şablon seçin (1-5):"},
    "cv_generating": {"ar": "⏳ جاري إنشاء السيرة الذاتية...", "en": "⏳ Generating CV...", "fr": "⏳ Génération du CV...", "tr": "⏳ CV oluşturuluyor..."},
    "cv_done": {"ar": "✅ سيرتك الذاتية جاهزة!", "en": "✅ Your CV is ready!", "fr": "✅ Votre CV est prêt!", "tr": "✅ CV'niz hazır!"},
    # ━━━ Sub-keys: Logo ━━━
    "logo_intro": {
        "ar": "🎨 **مولّد الشعارات**\n\nأرسل اسم المشروع:\n/logo اسم المشروع",
        "en": "🎨 **Logo Generator**\n\nSend project name:\n/logo ProjectName",
        "fr": "🎨 **Générateur de logo**\n\nEnvoyez le nom:\n/logo NomProjet",
        "tr": "🎨 **Logo Oluşturucu**\n\nProje adı gönderin:\n/logo ProjeAdı",
    },
    "logo_generating": {"ar": "⏳ جاري تصميم الشعار...", "en": "⏳ Designing logo...", "fr": "⏳ Création du logo...", "tr": "⏳ Logo tasarlanıyor..."},
    # ━━━ Sub-keys: Settings ━━━
    "btn_language": {"ar": "🌐 اللغة", "en": "🌐 Language", "fr": "🌐 Langue", "tr": "🌐 Dil", "ru": "🌐 Язык"},
    "btn_currency_pref": {"ar": "💱 العملة", "en": "💱 Currency", "fr": "💱 Devise", "tr": "💱 Para Birimi", "ru": "💱 Валюта"},
    "btn_city": {"ar": "🏠 المدينة", "en": "🏠 City", "fr": "🏠 Ville", "tr": "🏠 Şehir", "ru": "🏠 Город"},
    "btn_length": {"ar": "📏 طول الردود", "en": "📏 Response length", "fr": "📏 Longueur", "tr": "📏 Yanıt uzunluğu"},
    "choose_lang": {"ar": "🌐 اختر لغتك:", "en": "🌐 Choose language:", "fr": "🌐 Choisir la langue:", "tr": "🌐 Dil seçin:"},
    "lang_changed": {"ar": "✅ تم تغيير اللغة إلى {lang}", "en": "✅ Language changed to {lang}", "fr": "✅ Langue changée: {lang}", "tr": "✅ Dil değiştirildi: {lang}"},
    "label_ounce": {"ar": "💰 الأونصة", "en": "💰 Ounce", "fr": "💰 Once", "tr": "💰 Ons", "ru": "💰 Унция"},
    "label_temp": {"ar": "🌡 الحرارة", "en": "🌡 Temp", "fr": "🌡 Temp", "tr": "🌡 Sıcaklık", "ru": "🌡 Темп"},
    "label_humidity": {"ar": "💧 الرطوبة", "en": "💧 Humidity", "fr": "💧 Humidité", "tr": "💧 Nem", "ru": "💧 Влажность"},
    "label_wind": {"ar": "💨 الرياح", "en": "💨 Wind", "fr": "💨 Vent", "tr": "💨 Rüzgar", "ru": "💨 Ветер"},
    "label_feels": {"ar": "🤔 الإحساس", "en": "🤔 Feels like", "fr": "🤔 Ressenti", "tr": "🤔 Hissedilen", "ru": "🤔 Ощущается"},
    "label_price": {"ar": "💰 السعر", "en": "💰 Price", "fr": "💰 Prix", "tr": "💰 Fiyat", "ru": "💰 Цена"},
    "label_change": {"ar": "التغير", "en": "Change", "fr": "Variation", "tr": "Değişim", "ru": "Изменение"},
    "label_volume": {"ar": "📊 الحجم", "en": "📊 Volume", "fr": "📊 Volume", "tr": "📊 Hacim", "ru": "📊 Объём"},
    "label_mcap": {"ar": "🏢 القيمة السوقية", "en": "🏢 Market Cap", "fr": "🏢 Cap. boursière", "tr": "🏢 Piyasa Değeri", "ru": "🏢 Капитализация"},
    "label_rank": {"ar": "🏆 الترتيب", "en": "🏆 Rank", "fr": "🏆 Rang", "tr": "🏆 Sıra", "ru": "🏆 Ранг"},
    "label_rating": {"ar": "⭐ التقييم", "en": "⭐ Rating", "fr": "⭐ Note", "tr": "⭐ Puan", "ru": "⭐ Рейтинг"},
    "label_director": {"ar": "🎬 المخرج", "en": "🎬 Director", "fr": "🎬 Réalisateur", "tr": "🎬 Yönetmen", "ru": "🎬 Режиссёр"},
    "label_cast": {"ar": "🌟 الممثلون", "en": "🌟 Cast", "fr": "🌟 Acteurs", "tr": "🌟 Oyuncular", "ru": "🌟 В ролях"},
    "label_note": {"ar": "📝 ملاحظة", "en": "📝 Note", "fr": "📝 Note", "tr": "📝 Not", "ru": "📝 Примечание"},
    "label_parallel": {"ar": "⚠️ السعر الموازي", "en": "⚠️ Parallel rate", "fr": "⚠️ Taux parallèle", "tr": "⚠️ Paralel kur", "ru": "⚠️ Параллельный курс"},
    "fb_live_title": {
        "ar": "🔴 **مباريات مباشرة:**", "en": "🔴 **Live Matches:**",
        "fr": "🔴 **Matchs en direct:**", "tr": "🔴 **Canli Maclar:**",
        "es": "🔴 **Partidos en vivo:**", "ru": "🔴 **Живые матчи:**",
    },
    "label_departures": {
        "ar": "🛫 المغادرات", "en": "🛫 Departures", "fr": "🛫 Departs",
        "tr": "🛫 Kalkislar", "es": "🛫 Salidas", "ru": "🛫 Вылеты",
    },
    "label_arrivals": {
        "ar": "🛬 الوصول", "en": "🛬 Arrivals", "fr": "🛬 Arrivees",
        "tr": "🛬 Varislar", "es": "🛬 Llegadas", "ru": "🛬 Прилёты",
    },
    "label_altitude": {
        "ar": "⬆️ الارتفاع", "en": "⬆️ Altitude", "fr": "⬆️ Altitude",
        "tr": "⬆️ Yukseklik", "es": "⬆️ Altitud", "ru": "⬆️ Высота",
    },
    "label_speed": {
        "ar": "💨 السرعة", "en": "💨 Speed", "fr": "💨 Vitesse",
        "tr": "💨 Hiz", "es": "💨 Velocidad", "ru": "💨 Скорость",
    },
    "label_heading": {
        "ar": "🧭 الاتجاه", "en": "🧭 Heading", "fr": "🧭 Cap",
        "tr": "🧭 Yon", "es": "🧭 Rumbo", "ru": "🧭 Курс",
    },
    "stats_title": {
        "ar": "📊 **إحصائيات Omega Bot**", "en": "📊 **Omega Bot Stats**",
        "fr": "📊 **Stats Omega Bot**", "tr": "📊 **Omega Bot Istatistikler**",
    },
    "stats_system": {
        "ar": "📋 النظام", "en": "📋 System", "fr": "📋 Systeme", "tr": "📋 Sistem",
    },
    "stats_plan": {
        "ar": "الخطة", "en": "Plan", "fr": "Plan", "tr": "Plan",
    },
    "stats_models": {
        "ar": "النماذج", "en": "Models", "fr": "Modeles", "tr": "Modeller",
    },
    "stats_users_title": {
        "ar": "👥 المستخدمون", "en": "👥 Users", "fr": "👥 Utilisateurs", "tr": "👥 Kullanicilar",
    },
    "stats_total": {
        "ar": "الإجمالي", "en": "Total", "fr": "Total", "tr": "Toplam",
    },
    "stats_active": {
        "ar": "نشط (24h)", "en": "Active (24h)", "fr": "Actifs (24h)", "tr": "Aktif (24h)",
    },
    "stats_perf": {
        "ar": "🔄 الأداء", "en": "🔄 Performance", "fr": "🔄 Performance", "tr": "🔄 Performans",
    },
    "stats_searches": {
        "ar": "عمليات البحث", "en": "Searches", "fr": "Recherches", "tr": "Aramalar",
    },
    "stats_fusions": {
        "ar": "عمليات الدمج", "en": "Fusions", "fr": "Fusions", "tr": "Birlesimler",
    },
    "stats_avg_time": {
        "ar": "متوسط الوقت", "en": "Avg time", "fr": "Temps moyen", "tr": "Ort. sure",
    },
    "stats_circuits": {
        "ar": "دوائر مفتوحة", "en": "Open circuits", "fr": "Circuits ouverts", "tr": "Acik devreler",
    },
    "stats_quotas": {
        "ar": "📦 حصص APIs", "en": "📦 API Quotas", "fr": "📦 Quotas API", "tr": "📦 API Kotalari",
    },
    "rate_limited": {
        "ar": "⏳ انتظر قليلاً ثم حاول مجدداً", "en": "⏳ Please wait a moment and try again",
        "fr": "⏳ Veuillez patienter un instant", "es": "⏳ Espera un momento e inténtalo de nuevo",
        "tr": "⏳ Lütfen bir dakika bekleyin", "ru": "⏳ Подождите немного",
    },
}


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    """Get translated string with fallback chain: lang -> en -> key."""
    translations = I18N.get(key, {})
    text = translations.get(lang, translations.get("en", key))
    try:
        return text.format(**kwargs) if kwargs else text
    except (KeyError, IndexError):
        return text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Service Menu Buttons
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MENU_LABELS = {
    "gold": {"ar": "🪙 ذهب", "en": "🪙 Gold", "fr": "🪙 Or", "tr": "🪙 Altin", "ru": "🪙 Золото", "es": "🪙 Oro"},
    "currency": {"ar": "💱 عملات", "en": "💱 Currency", "fr": "💱 Devises", "tr": "💱 Doviz", "ru": "💱 Валюты", "es": "💱 Divisas"},
    "fuel": {"ar": "⛽ محروقات", "en": "⛽ Fuel", "fr": "⛽ Carburant", "tr": "⛽ Yakit", "ru": "⛽ Топливо", "es": "⛽ Combustible"},
    "weather": {"ar": "🌤 طقس", "en": "🌤 Weather", "fr": "🌤 Meteo", "tr": "🌤 Hava", "ru": "🌤 Погода", "es": "🌤 Clima"},
    "football": {"ar": "⚽ كرة قدم", "en": "⚽ Football", "fr": "⚽ Foot", "tr": "⚽ Futbol", "ru": "⚽ Футбол", "es": "⚽ Futbol"},
    "movies": {"ar": "🎬 افلام", "en": "🎬 Movies", "fr": "🎬 Films", "tr": "🎬 Film", "ru": "🎬 Кино", "es": "🎬 Cine"},
    "cv": {"ar": "📄 سيرة", "en": "📄 CV", "fr": "📄 CV", "tr": "📄 CV", "ru": "📄 Резюме", "es": "📄 CV"},
    "logo": {"ar": "🎨 شعار", "en": "🎨 Logo", "fr": "🎨 Logo", "tr": "🎨 Logo", "ru": "🎨 Лого", "es": "🎨 Logo"},
    "ai_chat": {"ar": "🤖 ذكاء", "en": "🤖 AI", "fr": "🤖 IA", "tr": "🤖 AI", "ru": "🤖 ИИ", "es": "🤖 IA"},
    "stocks": {"ar": "📈 اسهم", "en": "📈 Stocks", "fr": "📈 Bourse", "tr": "📈 Borsa", "ru": "📈 Акции", "es": "📈 Bolsa"},
    "crypto": {"ar": "₿ كريبتو", "en": "₿ Crypto", "fr": "₿ Crypto", "tr": "₿ Kripto", "ru": "₿ Крипто", "es": "₿ Cripto"},
    "news": {"ar": "📰 اخبار", "en": "📰 News", "fr": "📰 Infos", "tr": "📰 Haber", "ru": "📰 Новости", "es": "📰 Noticias"},
    "flights": {"ar": "✈️ رحلات", "en": "✈️ Flights", "fr": "✈️ Vols", "tr": "✈️ Ucus", "ru": "✈️ Рейсы", "es": "✈️ Vuelos"},
    "quakes": {"ar": "🌋 زلازل", "en": "🌋 Quakes", "fr": "🌋 Seismes", "tr": "🌋 Deprem", "ru": "🌋 Землетр.", "es": "🌋 Sismos"},
    "settings": {"ar": "⚙️ اعدادات", "en": "⚙️ Settings", "fr": "⚙️ Reglages", "tr": "⚙️ Ayarlar", "ru": "⚙️ Настройки", "es": "⚙️ Ajustes"},
}

MENU_LAYOUT = [
    ["gold", "currency", "fuel"],
    ["weather", "football", "movies"],
    ["cv", "logo", "ai_chat"],
    ["stocks", "crypto", "news"],
    ["flights", "quakes", "settings"],
]


def get_menu_label(key: str, lang: str = "en") -> str:
    labels = MENU_LABELS.get(key, {})
    return labels.get(lang, labels.get("en", key))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Parallel Countries & Currencies Config
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARALLEL_RATE_COUNTRIES = {
    "LB": {"currency": "LBP", "source": "lirarate.org", "name_ar": "لبنان", "name_en": "Lebanon"},
    "SY": {"currency": "SYP", "source": "lirarate.net", "name_ar": "سوريا", "name_en": "Syria"},
    "DZ": {"currency": "DZD", "source": "cours-dz.com", "name_ar": "الجزائر", "name_en": "Algeria"},
    "AR": {"currency": "ARS", "source": "dolarito.ar", "name_ar": "الأرجنتين", "name_en": "Argentina"},
    "IR": {"currency": "IRR", "source": "bonbast.com", "name_ar": "إيران", "name_en": "Iran"},
    "VE": {"currency": "VES", "source": "monitordolarvenezuela.com", "name_ar": "فنزويلا", "name_en": "Venezuela"},
    "YE": {"currency": "YER", "source": "ye.exchange", "name_ar": "اليمن", "name_en": "Yemen"},
}

GOLD_KARATS = {
    "24K": 1.0,
    "22K": 0.9167,
    "21K": 0.875,
    "18K": 0.75,
    "14K": 0.5833,
    "10K": 0.4167,
    "9K": 0.375,
}

SUPPORTED_METALS = ["XAU", "XAG", "XPT", "XPD", "XCU"]
METAL_NAMES = {
    "XAU": {"en": "Gold", "ar": "ذهب"},
    "XAG": {"en": "Silver", "ar": "فضة"},
    "XPT": {"en": "Platinum", "ar": "بلاتينيوم"},
    "XPD": {"en": "Palladium", "ar": "بالاديوم"},
    "XCU": {"en": "Copper", "ar": "نحاس"},
}

DISPLAY_CURRENCIES = [
    "USD", "EUR", "GBP", "SAR", "AED", "KWD", "QAR",
    "BHD", "OMR", "EGP", "MAD", "DZD", "TND", "LBP",
]

logger.info(f"Config loaded: plan={RENDER_PLAN}, models={len(AI_MODELS)}, db={'SQLite' if IS_FREE else 'PostgreSQL'}")
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 2 — DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES["database/__init__.py"] = """
from database.connection import get_engine, get_session, init_db, close_db
from database.models import Base, User, UserPreference, UserMemory, SearchHistory, Watchlist, CVData
from database.models import AIFusionLog, APICallLog, FavoriteTeam, TrackedCoin, AIConversation, ProactiveNotification
from database.crud import CRUDManager

__all__ = [
    "get_engine", "get_session", "init_db", "close_db",
    "Base", "User", "UserPreference", "UserMemory", "SearchHistory",
    "Watchlist", "CVData", "AIFusionLog", "APICallLog",
    "FavoriteTeam", "TrackedCoin", "AIConversation", "ProactiveNotification",
    "CRUDManager",
]
"""

FILES["database/connection.py"] = r'''
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from config import settings, IS_FREE, DATA_DIR

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    global _engine
    if _engine is not None:
        return _engine

    db_url = settings.db_url
    is_sqlite = "sqlite" in db_url

    if is_sqlite:
        _engine = create_async_engine(
            db_url,
            poolclass=NullPool,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        # Enable WAL mode for concurrent read/write support
        from sqlalchemy import event as sa_event
        @sa_event.listens_for(_engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        logger.info(f"SQLite engine created with WAL mode: {DATA_DIR}/omega.db")
    else:
        _engine = create_async_engine(
            db_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=5 if IS_FREE else 20,
            max_overflow=10 if IS_FREE else 40,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False,
        )
        logger.info("PostgreSQL engine created")

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is not None:
        return _session_factory

    engine = get_engine()
    _session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception as exc:
        await session.rollback()
        logger.error(f"Database session error: {exc}", exc_info=True)
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Initialize database and create all tables."""
    from database.models import Base

    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}", exc_info=True)
        raise


async def close_db() -> None:
    """Close database engine and cleanup connections."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")
'''

FILES["database/models.py"] = r'''
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint, JSON,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    preferred_currency: Mapped[str] = mapped_column(String(10), default="USD")
    home_city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    home_country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    home_timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expertise_level: Mapped[str] = mapped_column(String(20), default="normal")
    prefers_emojis: Mapped[bool] = mapped_column(Boolean, default=True)
    response_length_pref: Mapped[str] = mapped_column(String(20), default="medium")

    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    memory = relationship("UserMemory", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    cv_data = relationship("CVData", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    favorite_teams = relationship("FavoriteTeam", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    tracked_coins = relationship("TrackedCoin", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    notifications = relationship("ProactiveNotification", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        Index("ix_users_last_active", "last_active"),
        Index("ix_users_country", "home_country"),
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pref_key: Mapped[str] = mapped_column(String(100), nullable=False)
    pref_value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="preferences")

    __table_args__ = (
        UniqueConstraint("user_id", "pref_key", name="uq_user_pref"),
        Index("ix_user_pref_key", "user_id", "pref_key"),
    )


class UserMemory(Base):
    __tablename__ = "user_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    common_topics: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    active_hours: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    satisfaction_signals: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    last_10_queries: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    language_fluency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    predictive_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="memory")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    service: Mapped[str] = mapped_column(String(50), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    result_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_models_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    fusion_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    user_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="search_history")

    __table_args__ = (
        Index("ix_search_user_service", "user_id", "service"),
        Index("ix_search_created", "created_at"),
    )


class Watchlist(Base):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    poster_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="plan_to_watch")
    personal_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    watched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="watchlist")

    __table_args__ = (
        UniqueConstraint("user_id", "tmdb_id", "media_type", name="uq_user_watchlist"),
    )


class CVData(Base):
    __tablename__ = "cv_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    data_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    template: Mapped[str] = mapped_column(String(50), default="modern")
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="cv_data")


class AIFusionLog(Base):
    __tablename__ = "ai_fusion_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    models_called: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    models_responded: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    fusion_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    judge_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_fusion_task", "task_type"),
        Index("ix_fusion_created", "created_at"),
    )


class APICallLog(Base):
    __tablename__ = "api_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    is_outlier_removed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_apicall_name", "api_name"),
        Index("ix_apicall_created", "created_at"),
    )


class FavoriteTeam(Base):
    __tablename__ = "favorite_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[str] = mapped_column(String(50), nullable=False)
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    league_code: Mapped[str] = mapped_column(String(20), nullable=False)
    notify_goals: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="favorite_teams")

    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_user_team"),
    )


class TrackedCoin(Base):
    __tablename__ = "tracked_coins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id: Mapped[str] = mapped_column(String(100), nullable=False)
    coin_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_price_above: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    alert_price_below: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="tracked_coins")

    __table_args__ = (
        UniqueConstraint("user_id", "coin_id", name="uq_user_coin"),
    )


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    models_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    fusion_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="conversations")

    __table_args__ = (
        Index("ix_convo_user", "user_id", "created_at"),
    )


class ProactiveNotification(Base):
    __tablename__ = "proactive_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    triggered_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("ix_notif_user", "user_id"),
        Index("ix_notif_type", "type"),
    )
'''

FILES["database/crud.py"] = r'''
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from database.models import (
    User, UserPreference, UserMemory, SearchHistory, Watchlist, CVData,
    AIFusionLog, APICallLog, FavoriteTeam, TrackedCoin, AIConversation,
    ProactiveNotification,
)

logger = logging.getLogger(__name__)


class CRUDManager:
    """Centralized CRUD operations for all database models."""

    # ━━━ User Operations ━━━

    @staticmethod
    async def get_or_create_user(session: AsyncSession, telegram_id: int, **kwargs: Any) -> User:
        """Get existing user or create new one."""
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is not None:
                user.last_active = datetime.now(timezone.utc)
                user.total_requests = (user.total_requests or 0) + 1
                for key, value in kwargs.items():
                    if hasattr(user, key) and value is not None:
                        current = getattr(user, key)
                        if current is None or current == "":
                            setattr(user, key, value)
                await session.flush()
                return user

            user = User(
                telegram_id=telegram_id,
                username=kwargs.get("username"),
                first_name=kwargs.get("first_name"),
                last_name=kwargs.get("last_name"),
                language_code=kwargs.get("language_code", "en"),
                total_requests=1,
            )
            session.add(user)
            await session.flush()

            memory = UserMemory(user_id=user.id)
            session.add(memory)
            await session.flush()

            logger.info(f"New user created: {telegram_id} ({kwargs.get('first_name', 'Unknown')})")
            return user

        except Exception as exc:
            logger.error(f"Error in get_or_create_user({telegram_id}): {exc}", exc_info=True)
            raise

    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Fetch user by Telegram ID."""
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error(f"Error fetching user {telegram_id}: {exc}", exc_info=True)
            return None

    @staticmethod
    async def update_user(session: AsyncSession, telegram_id: int, **kwargs: Any) -> bool:
        """Update user fields."""
        try:
            await session.execute(
                update(User).where(User.telegram_id == telegram_id).values(**kwargs)
            )
            return True
        except Exception as exc:
            logger.error(f"Error updating user {telegram_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_user_count(session: AsyncSession) -> int:
        """Get total user count."""
        try:
            result = await session.execute(select(func.count(User.id)))
            return result.scalar_one() or 0
        except Exception as exc:
            logger.error(f"Error counting users: {exc}", exc_info=True)
            return 0

    @staticmethod
    async def get_active_users(session: AsyncSession, hours: int = 24) -> int:
        """Count users active in last N hours."""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            result = await session.execute(
                select(func.count(User.id)).where(User.last_active >= cutoff)
            )
            return result.scalar_one() or 0
        except Exception as exc:
            logger.error(f"Error counting active users: {exc}", exc_info=True)
            return 0

    # ━━━ Preference Operations ━━━

    @staticmethod
    async def set_preference(session: AsyncSession, user_id: int, key: str, value: str) -> bool:
        """Set a user preference (upsert)."""
        try:
            existing = await session.execute(
                select(UserPreference).where(
                    and_(UserPreference.user_id == user_id, UserPreference.pref_key == key)
                )
            )
            pref = existing.scalar_one_or_none()
            if pref:
                pref.pref_value = value
                pref.updated_at = datetime.now(timezone.utc)
            else:
                pref = UserPreference(user_id=user_id, pref_key=key, pref_value=value)
                session.add(pref)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error setting preference {key} for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_preference(session: AsyncSession, user_id: int, key: str) -> Optional[str]:
        """Get a user preference value."""
        try:
            result = await session.execute(
                select(UserPreference.pref_value).where(
                    and_(UserPreference.user_id == user_id, UserPreference.pref_key == key)
                )
            )
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error(f"Error getting preference {key} for user {user_id}: {exc}", exc_info=True)
            return None

    # ━━━ Memory Operations ━━━

    @staticmethod
    async def update_memory(session: AsyncSession, user_id: int, **kwargs: Any) -> bool:
        """Update user memory fields."""
        try:
            result = await session.execute(
                select(UserMemory).where(UserMemory.user_id == user_id)
            )
            memory = result.scalar_one_or_none()
            if memory is None:
                memory = UserMemory(user_id=user_id, **kwargs)
                session.add(memory)
            else:
                for key, value in kwargs.items():
                    if hasattr(memory, key):
                        setattr(memory, key, value)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error updating memory for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def add_query_to_memory(session: AsyncSession, user_id: int, query: str) -> bool:
        """Add a query to user's last_10_queries."""
        try:
            result = await session.execute(
                select(UserMemory).where(UserMemory.user_id == user_id)
            )
            memory = result.scalar_one_or_none()
            if memory is None:
                memory = UserMemory(user_id=user_id, last_10_queries=[query])
                session.add(memory)
            else:
                queries = list(memory.last_10_queries or [])
                queries.append(query)
                memory.last_10_queries = queries[-10:]
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error adding query to memory for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ Search History ━━━

    @staticmethod
    async def log_search(session: AsyncSession, user_id: int, service: str, query: str, **kwargs: Any) -> bool:
        """Log a search query."""
        try:
            entry = SearchHistory(
                user_id=user_id,
                service=service,
                query=query,
                result_summary=kwargs.get("result_summary"),
                response_time_ms=kwargs.get("response_time_ms"),
                ai_models_used=kwargs.get("ai_models_used"),
                fusion_score=kwargs.get("fusion_score"),
            )
            session.add(entry)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error logging search for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ Watchlist ━━━

    @staticmethod
    async def add_to_watchlist(session: AsyncSession, user_id: int, tmdb_id: int, media_type: str, title: str, **kwargs: Any) -> bool:
        """Add item to watchlist."""
        try:
            existing = await session.execute(
                select(Watchlist).where(
                    and_(Watchlist.user_id == user_id, Watchlist.tmdb_id == tmdb_id, Watchlist.media_type == media_type)
                )
            )
            if existing.scalar_one_or_none():
                return False
            item = Watchlist(
                user_id=user_id, tmdb_id=tmdb_id, media_type=media_type,
                title=title, poster_path=kwargs.get("poster_path"),
                status=kwargs.get("status", "plan_to_watch"),
            )
            session.add(item)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error adding to watchlist for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_watchlist(session: AsyncSession, user_id: int, status: Optional[str] = None) -> list[Watchlist]:
        """Get user's watchlist."""
        try:
            query = select(Watchlist).where(Watchlist.user_id == user_id)
            if status:
                query = query.where(Watchlist.status == status)
            query = query.order_by(Watchlist.added_at.desc())
            result = await session.execute(query)
            return list(result.scalars().all())
        except Exception as exc:
            logger.error(f"Error fetching watchlist for user {user_id}: {exc}", exc_info=True)
            return []

    # ━━━ AI Fusion Logs ━━━

    @staticmethod
    async def log_fusion(session: AsyncSession, task_type: str, models_called: list, models_responded: list, fusion_time_ms: int, **kwargs: Any) -> bool:
        """Log AI fusion result."""
        try:
            entry = AIFusionLog(
                task_type=task_type,
                models_called=models_called,
                models_responded=models_responded,
                fusion_time_ms=fusion_time_ms,
                judge_score=kwargs.get("judge_score"),
                final_confidence=kwargs.get("final_confidence"),
            )
            session.add(entry)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error logging fusion: {exc}", exc_info=True)
            return False

    # ━━━ API Call Logs ━━━

    @staticmethod
    async def log_api_call(session: AsyncSession, api_name: str, endpoint: str, status_code: int, response_time_ms: int, **kwargs: Any) -> bool:
        """Log external API call."""
        try:
            entry = APICallLog(
                api_name=api_name,
                endpoint=endpoint,
                status_code=status_code,
                response_time_ms=response_time_ms,
                is_fallback=kwargs.get("is_fallback", False),
                is_outlier_removed=kwargs.get("is_outlier_removed", False),
            )
            session.add(entry)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error logging API call: {exc}", exc_info=True)
            return False

    # ━━━ Favorite Teams ━━━

    @staticmethod
    async def add_favorite_team(session: AsyncSession, user_id: int, team_id: str, team_name: str, league_code: str) -> bool:
        """Add a favorite football team."""
        try:
            existing = await session.execute(
                select(FavoriteTeam).where(
                    and_(FavoriteTeam.user_id == user_id, FavoriteTeam.team_id == team_id)
                )
            )
            if existing.scalar_one_or_none():
                return False
            team = FavoriteTeam(user_id=user_id, team_id=team_id, team_name=team_name, league_code=league_code)
            session.add(team)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error adding favorite team for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ Tracked Coins ━━━

    @staticmethod
    async def track_coin(session: AsyncSession, user_id: int, coin_id: str, coin_symbol: str, **kwargs: Any) -> bool:
        """Track a cryptocurrency."""
        try:
            existing = await session.execute(
                select(TrackedCoin).where(
                    and_(TrackedCoin.user_id == user_id, TrackedCoin.coin_id == coin_id)
                )
            )
            if existing.scalar_one_or_none():
                return False
            coin = TrackedCoin(
                user_id=user_id, coin_id=coin_id, coin_symbol=coin_symbol,
                alert_price_above=kwargs.get("alert_price_above"),
                alert_price_below=kwargs.get("alert_price_below"),
            )
            session.add(coin)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error tracking coin for user {user_id}: {exc}", exc_info=True)
            return False

    # ━━━ AI Conversations ━━━

    @staticmethod
    async def save_conversation(session: AsyncSession, user_id: int, role: str, content: str, **kwargs: Any) -> bool:
        """Save a conversation message."""
        try:
            msg = AIConversation(
                user_id=user_id, role=role, content=content,
                models_used=kwargs.get("models_used"),
                fusion_score=kwargs.get("fusion_score"),
            )
            session.add(msg)
            await session.flush()
            return True
        except Exception as exc:
            logger.error(f"Error saving conversation for user {user_id}: {exc}", exc_info=True)
            return False

    @staticmethod
    async def get_conversation_history(session: AsyncSession, user_id: int, limit: int = 20) -> list[AIConversation]:
        """Get recent conversation history."""
        try:
            result = await session.execute(
                select(AIConversation)
                .where(AIConversation.user_id == user_id)
                .order_by(AIConversation.created_at.desc())
                .limit(limit)
            )
            messages = list(result.scalars().all())
            messages.reverse()
            return messages
        except Exception as exc:
            logger.error(f"Error fetching conversation for user {user_id}: {exc}", exc_info=True)
            return []

    # ━━━ Stats ━━━

    @staticmethod
    async def get_stats(session: AsyncSession) -> dict[str, Any]:
        """Get system-wide statistics."""
        try:
            total_users = await session.execute(select(func.count(User.id)))
            active_24h = await session.execute(
                select(func.count(User.id)).where(
                    User.last_active >= datetime.now(timezone.utc) - timedelta(hours=24)
                )
            )
            total_searches = await session.execute(select(func.count(SearchHistory.id)))
            total_fusions = await session.execute(select(func.count(AIFusionLog.id)))
            avg_fusion_time = await session.execute(select(func.avg(AIFusionLog.fusion_time_ms)))

            return {
                "total_users": total_users.scalar_one() or 0,
                "active_24h": active_24h.scalar_one() or 0,
                "total_searches": total_searches.scalar_one() or 0,
                "total_fusions": total_fusions.scalar_one() or 0,
                "avg_fusion_time_ms": round(avg_fusion_time.scalar_one() or 0, 1),
            }
        except Exception as exc:
            logger.error(f"Error getting stats: {exc}", exc_info=True)
            return {"total_users": 0, "active_24h": 0, "total_searches": 0, "total_fusions": 0, "avg_fusion_time_ms": 0}
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3 — AI ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES["services/__init__.py"] = """
from services.cache_service import CacheService, cache
from services.rate_limiter import RateLimiter
from services.circuit_breaker import CircuitBreaker

__all__ = ["CacheService", "cache", "RateLimiter", "CircuitBreaker"]
"""

FILES["services/cache_service.py"] = r'''
import logging
import time
import hashlib
import json
from typing import Any, Optional
from pathlib import Path

from config import IS_FREE, IS_PAID, DATA_DIR, CACHE_TTL, settings

logger = logging.getLogger(__name__)

_disk_cache = None
_redis_client = None


def _get_disk_cache():
    """Initialize diskcache for free plan."""
    global _disk_cache
    if _disk_cache is None:
        import diskcache
        cache_dir = DATA_DIR / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        _disk_cache = diskcache.Cache(
            str(cache_dir),
            size_limit=500 * 1024 * 1024,
            eviction_policy="least-recently-used",
        )
        logger.info(f"DiskCache initialized at {cache_dir}")
    return _disk_cache


async def _get_redis():
    """Initialize Redis for paid plan."""
    global _redis_client
    if _redis_client is None and IS_PAID and settings.redis_url:
        try:
            import redis.asyncio as aioredis
            _redis_client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
            await _redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as exc:
            logger.warning(f"Redis connection failed, falling back to diskcache: {exc}")
            _redis_client = None
    return _redis_client


def _make_key(prefix: str, *args: Any) -> str:
    """Generate a cache key from prefix and arguments."""
    raw = f"{prefix}:" + ":".join(str(a) for a in args)
    if len(raw) > 200:
        hashed = hashlib.md5(raw.encode()).hexdigest()
        return f"{prefix}:{hashed}"
    return raw


class CacheService:
    """Unified caching with stale fallback — never returns empty to users."""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get a cached value."""
        try:
            redis = await _get_redis()
            if redis is not None:
                val = await redis.get(key)
                if val is not None:
                    return json.loads(val)
                return None
            else:
                dc = _get_disk_cache()
                return dc.get(key, default=None)
        except Exception as exc:
            logger.warning(f"Cache get error for {key}: {exc}")
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value + save permanent backup for stale fallback."""
        try:
            redis = await _get_redis()
            if redis is not None:
                serialized = json.dumps(value, ensure_ascii=False, default=str)
                if ttl:
                    await redis.setex(key, ttl, serialized)
                else:
                    await redis.set(key, serialized)
                backup = json.dumps({"data": value, "saved_at": time.time()}, ensure_ascii=False, default=str)
                await redis.set(f"backup:{key}", backup)
                return True
            else:
                dc = _get_disk_cache()
                dc.set(key, value, expire=ttl)
                dc.set(f"backup:{key}", {"data": value, "saved_at": time.time()})
                return True
        except Exception as exc:
            logger.warning(f"Cache set error for {key}: {exc}")
            return False

    @staticmethod
    async def get_stale(key: str) -> Optional[dict]:
        """Get stale backup data when all APIs fail. Returns {data, saved_at, stale: True}."""
        try:
            redis = await _get_redis()
            if redis is not None:
                val = await redis.get(f"backup:{key}")
                if val is not None:
                    backup = json.loads(val)
                    backup["stale"] = True
                    backup["age_minutes"] = int((time.time() - backup.get("saved_at", 0)) / 60)
                    return backup
            else:
                dc = _get_disk_cache()
                backup = dc.get(f"backup:{key}", default=None)
                if backup is not None:
                    backup["stale"] = True
                    backup["age_minutes"] = int((time.time() - backup.get("saved_at", 0)) / 60)
                    return backup
        except Exception as exc:
            logger.warning(f"Stale cache error for {key}: {exc}")
        return None

    @staticmethod
    async def delete(key: str) -> bool:
        """Delete a cached value."""
        try:
            redis = await _get_redis()
            if redis is not None:
                await redis.delete(key)
            else:
                dc = _get_disk_cache()
                dc.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"Cache delete error for {key}: {exc}")
            return False

    @staticmethod
    async def get_or_set(key: str, factory, ttl: Optional[int] = None) -> Any:
        """Get cached value or compute and cache it."""
        cached = await CacheService.get(key)
        if cached is not None:
            return cached
        value = await factory() if callable(factory) else factory
        await CacheService.set(key, value, ttl=ttl)
        return value

    @staticmethod
    async def clear_prefix(prefix: str) -> int:
        """Clear all keys with a given prefix."""
        count = 0
        try:
            redis = await _get_redis()
            if redis is not None:
                async for key in redis.scan_iter(f"{prefix}*"):
                    await redis.delete(key)
                    count += 1
            else:
                dc = _get_disk_cache()
                for key in list(dc):
                    if isinstance(key, str) and key.startswith(prefix):
                        dc.delete(key)
                        count += 1
        except Exception as exc:
            logger.warning(f"Cache clear_prefix error for {prefix}: {exc}")
        return count

    @staticmethod
    async def close() -> None:
        """Close cache connections."""
        global _redis_client, _disk_cache
        try:
            if _redis_client is not None:
                await _redis_client.close()
                _redis_client = None
            if _disk_cache is not None:
                _disk_cache.close()
                _disk_cache = None
            logger.info("Cache connections closed")
        except Exception as exc:
            logger.warning(f"Error closing cache: {exc}")


cache = CacheService()


class AdminAlert:
    """Layer 3: Send alerts to admin when APIs fail repeatedly."""

    _failed_sources: dict = {}
    _alerted: set = set()
    _bot = None

    @classmethod
    def set_bot(cls, bot) -> None:
        cls._bot = bot

    @classmethod
    async def report_failure(cls, source_name: str) -> None:
        """Report an API failure. Alerts admin after 3 consecutive failures."""
        from config import settings
        count = cls._failed_sources.get(source_name, 0) + 1
        cls._failed_sources[source_name] = count

        if count >= 3 and source_name not in cls._alerted:
            cls._alerted.add(source_name)
            logger.warning(f"[ALERT] {source_name} failed {count} times consecutively")
            if cls._bot and settings.admin_id_list:
                try:
                    for admin_id in settings.admin_id_list:
                        await cls._bot.send_message(
                            admin_id,
                            f"⚠️ **{source_name}** failed {count} times\nFallbacks active — users not affected"
                        )
                except Exception as exc:
                    logger.debug(f"Admin alert send error: {exc}")

    @classmethod
    async def report_success(cls, source_name: str) -> None:
        """Report API recovery. Alerts admin that service is back."""
        from config import settings
        if source_name in cls._alerted:
            cls._alerted.discard(source_name)
            cls._failed_sources.pop(source_name, None)
            logger.info(f"[RECOVERED] {source_name} is back online")
            if cls._bot and settings.admin_id_list:
                try:
                    for admin_id in settings.admin_id_list:
                        await cls._bot.send_message(admin_id, f"✅ **{source_name}** recovered")
                except Exception as exc:
                    logger.debug(f"Admin recovery alert error: {exc}")
        else:
            cls._failed_sources.pop(source_name, None)

    @classmethod
    def get_status(cls) -> dict:
        return {"failed": dict(cls._failed_sources), "alerted": list(cls._alerted)}


admin_alert = AdminAlert
'''

FILES["services/rate_limiter.py"] = r'''
import logging
import time
import json
from collections import defaultdict
from typing import Optional
from pathlib import Path
from datetime import datetime, timezone

from config import DATA_DIR

logger = logging.getLogger(__name__)

QUOTA_FILE = DATA_DIR / "api_quotas.json"


class RateLimiter:
    def __init__(self):
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        self._buckets[key] = [t for t in self._buckets[key] if t > cutoff]
        if len(self._buckets[key]) >= max_requests:
            return False
        self._buckets[key].append(now)
        return True

    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        now = time.monotonic()
        cutoff = now - window_seconds
        active = [t for t in self._buckets[key] if t > cutoff]
        return max(0, max_requests - len(active))

    def reset(self, key: str) -> None:
        self._buckets.pop(key, None)


class QuotaTracker:
    """Tracks daily/monthly API quotas with automatic reset.
    
    - has_quota() = True  -> use the limited API (better data)
    - quota exhausted     -> has_quota() = False -> skip to unlimited
    - new day/month       -> auto-reset -> has_quota() = True again
    """

    QUOTAS = {
        "metals_api":     {"limit": 45, "period": "month", "name": "Metals API"},
        "omdb":           {"limit": 950, "period": "day", "name": "OMDb"},
        "newsapi":        {"limit": 95, "period": "day", "name": "NewsAPI"},
        "gnews":          {"limit": 95, "period": "day", "name": "GNews"},
        "football_data":  {"limit": 950, "period": "day", "name": "Football-Data"},
        "exchange_rate":  {"limit": 1400, "period": "month", "name": "ExchangeRate-API"},
        "alpha_vantage":  {"limit": 23, "period": "day", "name": "Alpha Vantage"},
        "openweather":    {"limit": 950, "period": "day", "name": "OpenWeatherMap"},
    }

    def __init__(self):
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        try:
            if QUOTA_FILE.exists():
                with open(QUOTA_FILE, "r") as f:
                    self._data = json.load(f)
        except Exception as exc:
            logger.warning(f"Quota load failed: {exc}")
            self._data = {}

    def _save(self) -> None:
        try:
            QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(QUOTA_FILE, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception as exc:
            logger.warning(f"Quota save failed: {exc}")

    def _period_key(self, period: str) -> str:
        now = datetime.now(timezone.utc)
        if period == "day":
            return now.strftime("%Y-%m-%d")
        elif period == "month":
            return now.strftime("%Y-%m")
        return now.strftime("%Y-%m-%d")

    def has_quota(self, api_name: str) -> bool:
        """Check if API has remaining quota. Auto-resets on new period."""
        config = self.QUOTAS.get(api_name)
        if config is None:
            return True
        period_key = self._period_key(config["period"])
        entry = self._data.get(api_name, {})
        if entry.get("period_key") != period_key:
            self._data[api_name] = {"period_key": period_key, "used": 0, "limit": config["limit"], "exhausted_at": None}
            self._save()
            logger.info(f"[Quota] {config['name']}: RESET - new {config['period']}, quota restored ({config['limit']})")
            return True
        remaining = config["limit"] - entry.get("used", 0)
        return remaining > 0

    def use_quota(self, api_name: str) -> None:
        """Record one API call. Logs when exhausted."""
        config = self.QUOTAS.get(api_name)
        if config is None:
            return
        period_key = self._period_key(config["period"])
        entry = self._data.get(api_name, {})
        if entry.get("period_key") != period_key:
            entry = {"period_key": period_key, "used": 0, "limit": config["limit"], "exhausted_at": None}
        entry["used"] = entry.get("used", 0) + 1
        remaining = config["limit"] - entry["used"]
        if remaining <= 0 and entry.get("exhausted_at") is None:
            entry["exhausted_at"] = datetime.now(timezone.utc).isoformat()
            logger.warning(f"[Quota] {config['name']}: EXHAUSTED - switching to unlimited until {config['period']} resets")
        self._data[api_name] = entry
        self._save()

    def get_status(self, api_name: str) -> dict:
        config = self.QUOTAS.get(api_name)
        if config is None:
            return {"api": api_name, "tracked": False}
        period_key = self._period_key(config["period"])
        entry = self._data.get(api_name, {})
        if entry.get("period_key") != period_key:
            return {"api": api_name, "name": config["name"], "used": 0, "limit": config["limit"],
                    "remaining": config["limit"], "period": config["period"], "exhausted": False}
        used = entry.get("used", 0)
        remaining = max(0, config["limit"] - used)
        return {"api": api_name, "name": config["name"], "used": used, "limit": config["limit"],
                "remaining": remaining, "period": config["period"], "exhausted": remaining <= 0,
                "exhausted_at": entry.get("exhausted_at")}

    def get_all_statuses(self) -> list[dict]:
        return [self.get_status(name) for name in self.QUOTAS]


user_limiter = RateLimiter()
api_limiter = RateLimiter()
quota = QuotaTracker()

USER_RATE_LIMITS = {
    "message": {"max": 30, "window": 60},
    "ai_chat": {"max": 10, "window": 60},
    "search": {"max": 20, "window": 60},
    "cv_generate": {"max": 3, "window": 300},
    "logo_generate": {"max": 5, "window": 300},
}

API_RATE_LIMITS = {
    "football_data": {"max": 10, "window": 60},
    "metals_api": {"max": 1, "window": 600},
    "omdb": {"max": 40, "window": 3600},
    "newsapi": {"max": 4, "window": 3600},
    "openweather": {"max": 55, "window": 60},
    "exchange_rate": {"max": 50, "window": 3600},
}


def check_user_rate(user_id: int, action: str) -> bool:
    config = USER_RATE_LIMITS.get(action, {"max": 30, "window": 60})
    key = f"user:{user_id}:{action}"
    return user_limiter.is_allowed(key, config["max"], config["window"])


def check_api_rate(api_name: str) -> bool:
    config = API_RATE_LIMITS.get(api_name, {"max": 100, "window": 60})
    key = f"api:{api_name}"
    return api_limiter.is_allowed(key, config["max"], config["window"])
'''

FILES["services/circuit_breaker.py"] = r'''
import logging
import time
from enum import Enum
from typing import Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitStats:
    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    total_calls: int = 0


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        self._circuits: dict[str, CircuitStats] = {}

    def _get_circuit(self, name: str) -> CircuitStats:
        """Get or create circuit stats."""
        if name not in self._circuits:
            self._circuits[name] = CircuitStats()
        return self._circuits[name]

    def is_available(self, name: str) -> bool:
        """Check if a service is available (circuit not open)."""
        circuit = self._get_circuit(name)
        now = time.monotonic()

        if circuit.state == CircuitState.CLOSED:
            return True

        if circuit.state == CircuitState.OPEN:
            if now - circuit.last_failure_time >= self._recovery_timeout:
                circuit.state = CircuitState.HALF_OPEN
                circuit.consecutive_failures = 0
                logger.info(f"Circuit {name} transitioning to HALF_OPEN")
                return True
            return False

        if circuit.state == CircuitState.HALF_OPEN:
            return circuit.successes < self._half_open_max_calls

        return True

    def record_success(self, name: str) -> None:
        """Record a successful call."""
        circuit = self._get_circuit(name)
        circuit.successes += 1
        circuit.total_calls += 1
        circuit.consecutive_failures = 0
        circuit.last_success_time = time.monotonic()

        if circuit.state == CircuitState.HALF_OPEN:
            if circuit.successes >= self._half_open_max_calls:
                circuit.state = CircuitState.CLOSED
                circuit.failures = 0
                circuit.successes = 0
                logger.info(f"Circuit {name} CLOSED (recovered)")

    def record_failure(self, name: str) -> None:
        """Record a failed call."""
        circuit = self._get_circuit(name)
        circuit.failures += 1
        circuit.total_calls += 1
        circuit.consecutive_failures += 1
        circuit.last_failure_time = time.monotonic()

        if circuit.state == CircuitState.HALF_OPEN:
            circuit.state = CircuitState.OPEN
            logger.warning(f"Circuit {name} OPEN (failed during half-open)")
            return

        if circuit.consecutive_failures >= self._failure_threshold:
            circuit.state = CircuitState.OPEN
            logger.warning(f"Circuit {name} OPEN (threshold {self._failure_threshold} reached)")

    def get_status(self, name: str) -> dict[str, Any]:
        """Get circuit status."""
        circuit = self._get_circuit(name)
        return {
            "name": name,
            "state": circuit.state.value,
            "failures": circuit.failures,
            "successes": circuit.successes,
            "consecutive_failures": circuit.consecutive_failures,
            "total_calls": circuit.total_calls,
        }

    def get_all_statuses(self) -> dict[str, dict[str, Any]]:
        """Get all circuit statuses."""
        return {name: self.get_status(name) for name in self._circuits}

    def reset(self, name: str) -> None:
        """Manually reset a circuit."""
        if name in self._circuits:
            self._circuits[name] = CircuitStats()
            logger.info(f"Circuit {name} manually reset")


# Global circuit breaker instance
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
'''

FILES["services/omega_router.py"] = r'''
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

TASK_PATTERNS = {
    "code": [r"\bcode\b", r"\bprogram\b", r"\bscript\b", r"\bfunction\b", r"\bclass\b", r"\bapi\b", r"\bdebug\b", r"\bكود\b", r"\bبرمج\b"],
    "math": [r"\bcalculate\b", r"\bsolve\b", r"\bequation\b", r"\bmath\b", r"\bاحسب\b", r"\bحل\b", r"\bمعادلة\b"],
    "creative": [r"\bwrite\b.*\b(story|poem|essay)\b", r"\bcreative\b", r"\bimagine\b", r"\bاكتب\b", r"\bقصة\b", r"\bقصيدة\b"],
    "analysis": [r"\banalyze\b", r"\bcompare\b", r"\bevaluate\b", r"\bحلل\b", r"\bقارن\b"],
    "translation": [r"\btranslat\b", r"\bترجم\b"],
    "factual": [r"\bwhat is\b", r"\bwho is\b", r"\bwhen did\b", r"\bما هو\b", r"\bمن هو\b", r"\bمتى\b"],
    "chat": [r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bmerhaba\b", r"\bمرحبا\b", r"\bأهلا\b", r"\bسلام\b"],
    "summarize": [r"\bsummar\b", r"\btl;?dr\b", r"\bلخص\b", r"\bملخص\b"],
    "explain": [r"\bexplain\b", r"\bteach\b", r"\bhow does\b", r"\bاشرح\b", r"\bكيف\b"],
}

COMPLEXITY_INDICATORS = {
    "high": [r"\bdetail\b", r"\bcomplex\b", r"\badvanced\b", r"\bin-depth\b", r"\bتفصيل\b", r"\bمعقد\b", r"\bمتقدم\b"],
    "low": [r"\bsimple\b", r"\bquick\b", r"\bbrief\b", r"\bبسيط\b", r"\bسريع\b", r"\bمختصر\b"],
}

LANGUAGE_PATTERNS = {
    "ar": r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+",
    "fa": r"[\u0600-\u06FF]+",
    "he": r"[\u0590-\u05FF]+",
    "zh": r"[\u4E00-\u9FFF]+",
    "ja": r"[\u3040-\u309F\u30A0-\u30FF]+",
    "ko": r"[\uAC00-\uD7AF]+",
    "ru": r"[\u0400-\u04FF]+",
    "hi": r"[\u0900-\u097F]+",
    "th": r"[\u0E00-\u0E7F]+",
}


class OmegaRouter:
    """Layer 0: Extracts 'DNA' of a question — task type, complexity, urgency, language."""

    def analyze(self, text: str) -> dict[str, Any]:
        """Analyze a user query and return its DNA."""
        text_lower = text.lower().strip()

        result = {
            "task_type": self._detect_task_type(text_lower),
            "complexity": self._detect_complexity(text_lower),
            "language": self._detect_language(text),
            "urgency": self._detect_urgency(text_lower),
            "word_count": len(text.split()),
            "has_question_mark": "?" in text or "؟" in text,
            "recommended_models": [],
            "recommended_timeout": 4,
            "needs_reasoning": False,
        }

        result["needs_reasoning"] = result["task_type"] in ("code", "math", "analysis")
        result["recommended_timeout"] = self._recommend_timeout(result)
        result["recommended_models"] = self._recommend_models(result)

        logger.debug(f"Router analysis: task={result['task_type']}, complexity={result['complexity']}, lang={result['language']}")
        return result

    def _detect_task_type(self, text: str) -> str:
        """Detect the primary task type."""
        scores: dict[str, int] = {}
        for task, patterns in TASK_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
            if score > 0:
                scores[task] = score

        if not scores:
            return "general"
        return max(scores, key=scores.get)

    def _detect_complexity(self, text: str) -> str:
        """Detect query complexity: low, medium, high."""
        for level, patterns in COMPLEXITY_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level

        word_count = len(text.split())
        if word_count > 50:
            return "high"
        elif word_count > 15:
            return "medium"
        return "low"

    def _detect_language(self, text: str) -> str:
        """Detect the primary language of the text."""
        for lang, pattern in LANGUAGE_PATTERNS.items():
            matches = re.findall(pattern, text)
            if len(matches) >= 2 or (len(matches) == 1 and len(matches[0]) > 3):
                return lang
        return "en"

    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level."""
        urgent_words = [r"\burgent\b", r"\basap\b", r"\bnow\b", r"\bquick\b", r"\bعاجل\b", r"\bفوراً\b", r"\bسريع\b"]
        for pattern in urgent_words:
            if re.search(pattern, text, re.IGNORECASE):
                return "high"
        return "normal"

    def _recommend_timeout(self, analysis: dict[str, Any]) -> int:
        """Recommend total timeout based on analysis."""
        base = 4
        if analysis["complexity"] == "high":
            base = 8
        elif analysis["complexity"] == "low":
            base = 2
        if analysis["urgency"] == "high":
            base = max(2, base - 2)
        if analysis["needs_reasoning"]:
            base += 2
        return min(base, 12)

    def _recommend_models(self, analysis: dict[str, Any]) -> list[str]:
        """Recommend model IDs based on analysis."""
        from config import AI_MODELS

        task = analysis["task_type"]
        complexity = analysis["complexity"]

        if complexity == "low" or analysis["urgency"] == "high":
            return [m["id"] for m in AI_MODELS if m["tier"] <= 2]

        if task in ("code", "math"):
            preferred = ["deepseek", "gemini", "groq"]
            recommended = [m["id"] for m in AI_MODELS if m["provider"] in preferred]
            others = [m["id"] for m in AI_MODELS if m["provider"] not in preferred]
            return recommended + others

        if task == "creative":
            preferred = ["cohere", "openrouter", "gemini"]
            recommended = [m["id"] for m in AI_MODELS if m["provider"] in preferred]
            others = [m["id"] for m in AI_MODELS if m["provider"] not in preferred]
            return recommended + others

        return [m["id"] for m in AI_MODELS]


omega_router = OmegaRouter()
'''

FILES["services/omega_query_engine.py"] = r'''
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
'''

FILES["services/omega_fusion.py"] = r'''
import logging
import re
from collections import Counter
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OmegaFusion:
    """Layer 2: Fusion Engine — merges multiple AI responses into one optimal answer."""

    TIER_WEIGHTS = {1: 1.0, 2: 0.9, 3: 0.8, 4: 0.6}

    def fuse(self, responses: list[dict[str, Any]], analysis: Optional[dict] = None) -> dict[str, Any]:
        """Fuse multiple AI responses into the best answer."""
        if not responses:
            return {"text": "", "confidence": 0.0, "models_used": [], "method": "none"}

        if len(responses) == 1:
            return {
                "text": responses[0]["text"],
                "confidence": 0.7,
                "models_used": [responses[0]["model_id"]],
                "method": "single",
            }

        task_type = (analysis or {}).get("task_type", "general")

        if task_type in ("code", "math"):
            return self._fuse_precision(responses)
        elif task_type == "creative":
            return self._fuse_creative(responses)
        elif task_type == "factual":
            return self._fuse_factual(responses)
        else:
            return self._fuse_general(responses)

    def _fuse_general(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """General fusion: weighted scoring."""
        scored = []
        for resp in responses:
            weight = self.TIER_WEIGHTS.get(resp.get("tier", 4), 0.6)
            text = resp["text"]
            length_score = min(len(text) / 500, 1.0)
            structure_score = self._score_structure(text)
            speed_bonus = 0.1 if resp.get("elapsed_ms", 5000) < 2000 else 0.0

            total_score = (weight * 0.4) + (length_score * 0.2) + (structure_score * 0.3) + speed_bonus
            scored.append((resp, total_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        best = scored[0][0]

        return {
            "text": best["text"],
            "confidence": min(scored[0][1], 1.0),
            "models_used": [r["model_id"] for r, _ in scored[:3]],
            "method": "weighted_general",
        }

    def _fuse_precision(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Precision fusion for code/math: prefer responses with code blocks."""
        code_responses = []
        for resp in responses:
            text = resp["text"]
            has_code = bool(re.search(r"```[\s\S]+?```", text))
            weight = self.TIER_WEIGHTS.get(resp.get("tier", 4), 0.6)
            score = weight + (0.3 if has_code else 0.0)
            code_responses.append((resp, score))

        code_responses.sort(key=lambda x: x[1], reverse=True)
        best = code_responses[0][0]

        return {
            "text": best["text"],
            "confidence": min(code_responses[0][1], 1.0),
            "models_used": [r["model_id"] for r, _ in code_responses[:3]],
            "method": "precision",
        }

    def _fuse_creative(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Creative fusion: pick the longest, most expressive response."""
        creative_scored = []
        for resp in responses:
            text = resp["text"]
            uniqueness = len(set(text.split())) / max(len(text.split()), 1)
            length_score = min(len(text) / 1000, 1.0)
            score = (uniqueness * 0.5) + (length_score * 0.5)
            creative_scored.append((resp, score))

        creative_scored.sort(key=lambda x: x[1], reverse=True)
        best = creative_scored[0][0]

        return {
            "text": best["text"],
            "confidence": min(creative_scored[0][1], 1.0),
            "models_used": [r["model_id"] for r, _ in creative_scored[:3]],
            "method": "creative",
        }

    def _fuse_factual(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Factual fusion: voting + consensus."""
        texts = [r["text"] for r in responses]
        key_facts = []
        for text in texts:
            numbers = re.findall(r"\b\d[\d,.]+\b", text)
            key_facts.extend(numbers)

        fact_counts = Counter(key_facts)
        consensus_facts = {fact for fact, count in fact_counts.items() if count >= 2}

        best_resp = None
        best_score = -1
        for resp in responses:
            text = resp["text"]
            match_count = sum(1 for fact in consensus_facts if fact in text)
            weight = self.TIER_WEIGHTS.get(resp.get("tier", 4), 0.6)
            score = (match_count * 0.5) + (weight * 0.3) + (self._score_structure(text) * 0.2)
            if score > best_score:
                best_score = score
                best_resp = resp

        if best_resp is None:
            best_resp = responses[0]

        return {
            "text": best_resp["text"],
            "confidence": min(best_score, 1.0) if best_score > 0 else 0.5,
            "models_used": [r["model_id"] for r in responses[:3]],
            "method": "factual_consensus",
        }

    def _score_structure(self, text: str) -> float:
        """Score text structure quality."""
        score = 0.0
        if len(text) > 100:
            score += 0.2
        if "\n" in text:
            score += 0.2
        if any(marker in text for marker in ["1.", "•", "-", "*", "①"]):
            score += 0.2
        if re.search(r"```[\s\S]+?```", text):
            score += 0.2
        if text.strip().endswith((".", "!", "؟", "?")):
            score += 0.2
        return min(score, 1.0)


omega_fusion = OmegaFusion()
'''

FILES["services/omega_judge.py"] = r'''
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OmegaJudge:
    """Layer 3: Judge System — evaluates and improves the fused response."""

    def evaluate(self, fused: dict[str, Any], original_query: str, analysis: Optional[dict] = None) -> dict[str, Any]:
        """Evaluate fused response with 3 judges."""
        text = fused.get("text", "")
        if not text:
            return {**fused, "judge_score": 0.0, "issues": ["empty_response"]}

        accuracy_score = self._judge_accuracy(text, original_query, analysis)
        completeness_score = self._judge_completeness(text, original_query, analysis)
        user_fit_score = self._judge_user_fit(text, original_query, analysis)

        overall = (accuracy_score * 0.4) + (completeness_score * 0.35) + (user_fit_score * 0.25)
        issues = []

        if accuracy_score < 0.5:
            issues.append("low_accuracy")
        if completeness_score < 0.5:
            issues.append("incomplete")
        if user_fit_score < 0.5:
            issues.append("poor_user_fit")

        result = {
            **fused,
            "judge_score": round(overall, 3),
            "accuracy_score": round(accuracy_score, 3),
            "completeness_score": round(completeness_score, 3),
            "user_fit_score": round(user_fit_score, 3),
            "issues": issues,
        }

        if overall < 0.4:
            result["text"] = self._add_disclaimer(text, issues)

        logger.debug(f"Judge scores: accuracy={accuracy_score:.2f}, complete={completeness_score:.2f}, fit={user_fit_score:.2f}, overall={overall:.2f}")
        return result

    def _judge_accuracy(self, text: str, query: str, analysis: Optional[dict]) -> float:
        """Judge 1: Accuracy — does the response answer the question?"""
        score = 0.5

        query_words = set(query.lower().split())
        text_lower = text.lower()
        matched = sum(1 for w in query_words if w in text_lower and len(w) > 3)
        relevance = min(matched / max(len(query_words), 1), 1.0)
        score += relevance * 0.3

        hedging = len(re.findall(r"\b(maybe|perhaps|might|possibly|ربما|قد|يمكن)\b", text_lower))
        if hedging > 3:
            score -= 0.1

        if re.search(r"\b(error|mistake|incorrect|خطأ)\b", text_lower):
            score -= 0.15

        has_numbers = bool(re.search(r"\b\d+\.?\d*\b", text))
        if analysis and analysis.get("task_type") in ("math", "factual") and has_numbers:
            score += 0.1

        return max(0.0, min(score, 1.0))

    def _judge_completeness(self, text: str, query: str, analysis: Optional[dict]) -> float:
        """Judge 2: Completeness — is the response thorough enough?"""
        score = 0.3

        word_count = len(text.split())
        complexity = (analysis or {}).get("complexity", "medium")

        if complexity == "high":
            target = 200
        elif complexity == "low":
            target = 30
        else:
            target = 80

        length_ratio = min(word_count / target, 1.5)
        score += min(length_ratio * 0.3, 0.4)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) >= 2:
            score += 0.1

        if any(marker in text for marker in ["1.", "2.", "•", "-", "①", "②"]):
            score += 0.1

        has_intro = len(paragraphs) > 0 and len(paragraphs[0].split()) >= 10
        has_conclusion = len(paragraphs) > 1 and len(paragraphs[-1].split()) >= 5
        if has_intro:
            score += 0.05
        if has_conclusion:
            score += 0.05

        return max(0.0, min(score, 1.0))

    def _judge_user_fit(self, text: str, query: str, analysis: Optional[dict]) -> float:
        """Judge 3: User Fit — is the response appropriate for the user?"""
        score = 0.5

        query_lang = (analysis or {}).get("language", "en")
        if query_lang == "ar":
            arabic_ratio = len(re.findall(r"[\u0600-\u06FF]+", text)) / max(len(text.split()), 1)
            if arabic_ratio > 0.3:
                score += 0.3
            else:
                score -= 0.2
        elif query_lang == "en":
            english_ratio = len(re.findall(r"[a-zA-Z]+", text)) / max(len(text.split()), 1)
            if english_ratio > 0.5:
                score += 0.2

        if "?" in query or "؟" in query:
            if text.strip().startswith(("Yes", "No", "نعم", "لا", "The", "It", "هو", "هي")):
                score += 0.1

        return max(0.0, min(score, 1.0))

    def _add_disclaimer(self, text: str, issues: list[str]) -> str:
        """Add disclaimer for low-quality responses."""
        disclaimer = "\n\n⚠️ *Note: This response may not be fully accurate. Please verify important information.*"
        return text + disclaimer


omega_judge = OmegaJudge()
'''

FILES["services/omega_memory.py"] = r'''
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)


class OmegaMemory:
    """Layer 4: Memory & Personalization — tracks user behavior and adapts."""

    async def update_user_context(self, user_id: int, query: str, service: str, response_quality: float) -> None:
        """Update user memory after each interaction."""
        try:
            async with get_session() as session:
                await CRUDManager.add_query_to_memory(session, user_id, query)

                user = await CRUDManager.get_user_by_telegram_id(session, user_id)
                if user and user.memory:
                    memory = user.memory
                    topics = dict(memory.common_topics or {})
                    topics[service] = topics.get(service, 0) + 1
                    await CRUDManager.update_memory(session, user.id, common_topics=topics)

                    hour = datetime.now(timezone.utc).hour
                    hours = dict(memory.active_hours or {})
                    hours[str(hour)] = hours.get(str(hour), 0) + 1
                    await CRUDManager.update_memory(session, user.id, active_hours=hours)

                    signals = dict(memory.satisfaction_signals or {})
                    if response_quality >= 0.7:
                        signals["positive"] = signals.get("positive", 0) + 1
                    else:
                        signals["negative"] = signals.get("negative", 0) + 1
                    await CRUDManager.update_memory(session, user.id, satisfaction_signals=signals)

        except Exception as exc:
            logger.error(f"Error updating memory for user {user_id}: {exc}", exc_info=True)

    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]:
        """Get user profile for personalization."""
        try:
            async with get_session() as session:
                user = await CRUDManager.get_user_by_telegram_id(session, telegram_id)
                if not user:
                    return {"exists": False}

                memory = user.memory
                return {
                    "exists": True,
                    "language": user.language_code,
                    "currency": user.preferred_currency,
                    "city": user.home_city,
                    "country": user.home_country,
                    "expertise": user.expertise_level,
                    "prefers_emojis": user.prefers_emojis,
                    "response_length": user.response_length_pref,
                    "common_topics": dict(memory.common_topics or {}) if memory else {},
                    "total_requests": user.total_requests,
                }
        except Exception as exc:
            logger.error(f"Error getting profile for user {telegram_id}: {exc}", exc_info=True)
            return {"exists": False}

    async def predict_next_query(self, telegram_id: int) -> Optional[str]:
        """Predict what the user might ask next based on patterns."""
        try:
            profile = await self.get_user_profile(telegram_id)
            if not profile.get("exists"):
                return None

            topics = profile.get("common_topics", {})
            if not topics:
                return None

            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            top_topic = sorted_topics[0][0] if sorted_topics else None
            return top_topic

        except Exception as exc:
            logger.error(f"Error predicting for user {telegram_id}: {exc}", exc_info=True)
            return None


omega_memory = OmegaMemory()
'''

FILES["services/omega_learning.py"] = r'''
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class OmegaLearning:
    """Layer 5: Real-time Data Fusion — replaces AI-generated data with real API data."""

    def inject_real_data(self, ai_text: str, real_data: Optional[dict[str, Any]] = None) -> str:
        """Replace any AI-generated numbers/data with real API data."""
        if not real_data:
            return ai_text

        result = ai_text

        for key, value in real_data.items():
            if isinstance(value, (int, float)):
                placeholder_patterns = [
                    f"{{{key}}}",
                    f"[{key}]",
                ]
                for pattern in placeholder_patterns:
                    result = result.replace(pattern, str(value))

        return result

    def build_fact_prompt(self, real_data: dict[str, Any]) -> str:
        """Build a fact-injection prompt section with real data."""
        if not real_data:
            return ""

        lines = ["IMPORTANT: Use these EXACT real-time values in your response:"]
        for key, value in real_data.items():
            lines.append(f"  - {key}: {value}")
        lines.append("Do NOT make up any numbers. Only use the values above.")

        return "\n".join(lines)

    def validate_response_data(self, text: str, real_data: dict[str, Any], tolerance: float = 0.02) -> dict[str, Any]:
        """Validate that the AI response uses correct real data."""
        import re

        issues = []
        valid = True

        for key, expected in real_data.items():
            if not isinstance(expected, (int, float)):
                continue

            numbers_in_text = re.findall(r"[\d,]+\.?\d*", text)
            found = False
            for num_str in numbers_in_text:
                try:
                    num = float(num_str.replace(",", ""))
                    if abs(num - expected) / max(abs(expected), 0.01) <= tolerance:
                        found = True
                        break
                except ValueError:
                    continue

            if not found:
                issues.append(f"Missing or incorrect value for {key}: expected {expected}")
                valid = False

        return {"valid": valid, "issues": issues}


omega_learning = OmegaLearning()
'''

FILES["services/omega_image.py"] = r'''
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
'''

FILES["services/translation_service.py"] = r'''
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
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 4 — API CLIENTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES["api_clients/__init__.py"] = """
from api_clients.base_client import BaseAPIClient

__all__ = ["BaseAPIClient"]
"""

FILES["api_clients/base_client.py"] = r'''
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
'''

FILES["api_clients/omega_metals.py"] = r'''
import asyncio
import logging
import statistics
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL, GOLD_KARATS, SUPPORTED_METALS, DISPLAY_CURRENCIES
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


class OmegaMetals:
    """Gold & metals prices with multi-source fusion and outlier removal."""

    def __init__(self):
        self._metals_api = BaseAPIClient("metals_api", "https://metals-api.com/api")
        self._goldapi = BaseAPIClient("goldapi", "https://www.goldapi.io/api")
        self._fallback = BaseAPIClient("metals_fallback")

    async def get_prices(self, metal: str = "XAU", currency: str = "USD") -> dict[str, Any]:
        """Get metal price with multi-source fusion."""
        cache_key = f"metals:{metal}:{currency}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        prices = []

        # Limited API first (if quota available, auto-restores when renewed)
        if quota.has_quota("metals_api"):
            price1 = await self._fetch_metals_api(metal, currency)
            if price1 is not None:
                quota.use_quota("metals_api")
                prices.append({"source": "metals-api", "price": price1})

        price2 = await self._fetch_goldapi(metal, currency)
        if price2 is not None:
            prices.append({"source": "goldapi", "price": price2})

        price3 = await self._fetch_metals_live(metal)
        if price3 is not None:
            prices.append({"source": "metals.live", "price": price3})

        if not prices:
            price4 = await self._fetch_yfinance(metal)
            if price4 is not None:
                prices.append({"source": "yfinance", "price": price4})

        if not prices:
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                result["age_minutes"] = stale.get("age_minutes", 0)
                return result
            return {"error": True, "message": "No price data available"}

        fused_price = self._fuse_prices(prices)

        result = {
            "metal": metal,
            "currency": currency,
            "price_per_ounce": round(fused_price, 2),
            "price_per_gram": round(fused_price / 31.1035, 2),
            "price_per_kilo": round(fused_price / 31.1035 * 1000, 2),
            "sources_count": len(prices),
            "karats": {},
            "error": False,
        }

        if metal == "XAU":
            for karat, purity in GOLD_KARATS.items():
                result["karats"][karat] = {
                    "per_gram": round((fused_price / 31.1035) * purity, 2),
                    "per_ounce": round(fused_price * purity, 2),
                }

        await cache.set(cache_key, result, ttl=CACHE_TTL["gold"])
        return result

    async def _fetch_metals_api(self, metal: str, currency: str) -> Optional[float]:
        """Fetch from metals-api.com (50 requests/month)."""
        if not settings.metals_api_key:
            return None
        try:
            data = await self._metals_api.get(
                f"/latest?access_key={settings.metals_api_key}&base={currency}&symbols={metal}"
            )
            if data and data.get("success") and "rates" in data:
                rate = data["rates"].get(metal)
                if rate and rate > 0:
                    return 1.0 / rate
        except Exception as exc:
            logger.debug(f"metals-api error: {exc}")
        return None

    async def _fetch_goldapi(self, metal: str, currency: str) -> Optional[float]:
        """Fetch from goldapi.io."""
        api_key = settings.goldapi_key or "goldapi-demo"
        try:
            data = await self._fallback.get(
                f"https://www.goldapi.io/api/{metal}/{currency}",
                headers={"x-access-token": api_key},
            )
            if data and "price" in data:
                return data["price"]
        except Exception as exc:
            logger.debug(f"goldapi error: {exc}")
        return None

    async def _fetch_metals_live(self, metal: str) -> Optional[float]:
        """Fetch from metals.live (free, no key)."""
        try:
            data = await self._fallback.get("https://api.metals.live/v1/spot")
            if data and isinstance(data, list):
                metal_map = {"XAU": "gold", "XAG": "silver", "XPT": "platinum", "XPD": "palladium"}
                metal_name = metal_map.get(metal, "gold")
                for item in data:
                    if item.get("metal", "").lower() == metal_name:
                        return item.get("price")
        except Exception as exc:
            logger.debug(f"metals.live error: {exc}")
        return None

    async def _fetch_yfinance(self, metal: str) -> Optional[float]:
        """Fetch from Yahoo Finance via yfinance (free, no key, most reliable)."""
        metal_ticker_map = {"XAU": "GC=F", "XAG": "SI=F", "XPT": "PL=F", "XPD": "PA=F"}
        ticker_symbol = metal_ticker_map.get(metal, "GC=F")
        try:
            loop = asyncio.get_event_loop()
            def _sync_fetch():
                import yfinance as yf
                t = yf.Ticker(ticker_symbol)
                price = t.fast_info.last_price
                return price
            price = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_fetch), timeout=15.0
            )
            if price and price > 0:
                logger.debug(f"yfinance {ticker_symbol}: {price}")
                return float(price)
        except Exception as exc:
            logger.debug(f"yfinance error: {exc}")
        return None

    def _fuse_prices(self, prices: list[dict]) -> float:
        """Fuse prices with outlier removal."""
        values = [p["price"] for p in prices]
        if len(values) == 1:
            return values[0]

        median = statistics.median(values)
        filtered = [v for v in values if abs(v - median) / max(median, 0.01) <= 0.02]

        if not filtered:
            filtered = values

        return statistics.mean(filtered)

    async def get_all_metals(self, currency: str = "USD") -> dict[str, Any]:
        """Get prices for all supported metals."""
        results = {}
        for metal in SUPPORTED_METALS:
            results[metal] = await self.get_prices(metal, currency)
        return results

    async def close(self) -> None:
        await self._metals_api.close()
        await self._goldapi.close()
        await self._fallback.close()


omega_metals = OmegaMetals()
'''

FILES["api_clients/omega_currency.py"] = r'''
import logging
import statistics
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL, PARALLEL_RATE_COUNTRIES
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


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
'''

FILES["api_clients/omega_fuel.py"] = r'''
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
'''

FILES["api_clients/omega_weather.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaWeather:
    """Weather service with Open-Meteo (primary) and OpenWeatherMap (fallback)."""

    def __init__(self):
        self._open_meteo = BaseAPIClient("open_meteo", "https://api.open-meteo.com/v1")
        self._owm = BaseAPIClient("openweathermap", "https://api.openweathermap.org/data/2.5")
        self._geocode = BaseAPIClient("geocode", "https://geocoding-api.open-meteo.com/v1")

    async def get_weather(self, city: str, lang: str = "en") -> dict[str, Any]:
        """Get current weather for a city."""
        cache_key = f"weather:current:{city}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        coords = await self._geocode_city(city)
        if not coords:
            return {"error": True, "message": f"City not found: {city}"}

        result = await self._fetch_open_meteo(coords["lat"], coords["lon"], coords["name"], lang)

        if not result or result.get("error"):
            result = await self._fetch_owm(city, lang)

        if result and not result.get("error"):
            result["city"] = coords.get("name", city)
            result["country"] = coords.get("country", "")
            await cache.set(cache_key, result, ttl=CACHE_TTL["weather_current"])

        if not result or result.get("error"):
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                result["age_minutes"] = stale.get("age_minutes", 0)
                return result
        return result or {"error": True, "message": "Weather data unavailable"}

    async def get_forecast(self, city: str, days: int = 7, lang: str = "en") -> dict[str, Any]:
        """Get weather forecast."""
        cache_key = f"weather:forecast:{city}:{days}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        coords = await self._geocode_city(city)
        if not coords:
            return {"error": True, "message": f"City not found: {city}"}

        try:
            data = await self._open_meteo.get(
                "/forecast",
                params={
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
                    "timezone": "auto",
                    "forecast_days": min(days, 16),
                },
            )

            if data and "daily" in data:
                daily = data["daily"]
                forecast = []
                for i in range(len(daily.get("time", []))):
                    forecast.append({
                        "date": daily["time"][i],
                        "temp_max": daily["temperature_2m_max"][i],
                        "temp_min": daily["temperature_2m_min"][i],
                        "precipitation": daily["precipitation_sum"][i],
                        "weather_code": daily["weathercode"][i],
                        "wind_max": daily["windspeed_10m_max"][i],
                        "description": self._weather_code_to_text(daily["weathercode"][i], lang),
                    })

                result = {
                    "city": coords.get("name", city),
                    "country": coords.get("country", ""),
                    "forecast": forecast,
                    "error": False,
                }
                await cache.set(cache_key, result, ttl=CACHE_TTL["weather_forecast"])
                return result
        except Exception as exc:
            logger.debug(f"Forecast error: {exc}")

        return {"error": True, "message": "Forecast unavailable"}

    async def _geocode_city(self, city: str) -> Optional[dict]:
        """Geocode a city name to coordinates."""
        # Translate common Arabic city names to English for reliable geocoding
        _AR_CITIES = {
            "بيروت": "Beirut", "دمشق": "Damascus", "عمّان": "Amman", "عمان": "Amman",
            "القاهرة": "Cairo", "الرياض": "Riyadh", "رياض": "Riyadh",
            "دبي": "Dubai", "أبوظبي": "Abu Dhabi", "ابوظبي": "Abu Dhabi",
            "الكويت": "Kuwait City", "المنامة": "Manama", "الدوحة": "Doha",
            "مسقط": "Muscat", "صنعاء": "Sanaa", "بغداد": "Baghdad",
            "الجزائر": "Algiers", "الدار البيضاء": "Casablanca", "تونس": "Tunis",
            "طرابلس": "Tripoli", "الخرطوم": "Khartoum", "مقديشو": "Mogadishu",
            "اسطنبول": "Istanbul", "أنقرة": "Ankara", "انقرة": "Ankara",
            "لندن": "London", "باريس": "Paris", "برلين": "Berlin",
            "نيويورك": "New York", "لوس انجلوس": "Los Angeles",
            "طوكيو": "Tokyo", "بكين": "Beijing", "موسكو": "Moscow",
            "مدريد": "Madrid", "روما": "Rome", "أمستردام": "Amsterdam",
            "جنيف": "Geneva", "زيوريخ": "Zurich", "فيينا": "Vienna",
            "صيدا": "Sidon", "طرابلس لبنان": "Tripoli Lebanon", "زحلة": "Zahle",
            "حلب": "Aleppo", "حمص": "Homs", "اللاذقية": "Latakia",
            "الاسكندرية": "Alexandria", "اسكندرية": "Alexandria",
            "جدة": "Jeddah", "مكة": "Mecca", "المدينة": "Medina",
            "شارجة": "Sharjah", "عجمان": "Ajman", "الفجيرة": "Fujairah",
        }
        city_en = _AR_CITIES.get(city.strip(), city)

        cache_key = f"geocode:{city_en.lower()}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._geocode.get("/search", params={"name": city_en, "count": 5, "language": "en"})
            if data and data.get("results"):
                result = data["results"][0]
                coords = {
                    "lat": result["latitude"],
                    "lon": result["longitude"],
                    "name": result.get("name", city_en),
                    "country": result.get("country_code", ""),
                }
                await cache.set(cache_key, coords, ttl=86400)
                return coords
        except Exception as exc:
            logger.debug(f"Geocode error for {city_en}: {exc}")
        return None

    async def _fetch_open_meteo(self, lat: float, lon: float, city_name: str, lang: str = "en") -> Optional[dict]:
        """Fetch current weather from Open-Meteo."""
        try:
            data = await self._open_meteo.get(
                "/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weathercode,windspeed_10m,winddirection_10m",
                    "timezone": "auto",
                },
            )
            if data and "current" in data:
                current = data["current"]
                return {
                    "temperature": current["temperature_2m"],
                    "feels_like": current["apparent_temperature"],
                    "humidity": current["relative_humidity_2m"],
                    "precipitation": current["precipitation"],
                    "wind_speed": current["windspeed_10m"],
                    "wind_direction": current["winddirection_10m"],
                    "weather_code": current["weathercode"],
                    "description": self._weather_code_to_text(current["weathercode"], lang),
                    "source": "Open-Meteo",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"Open-Meteo error: {exc}")
        return None

    async def _fetch_owm(self, city: str, lang: str) -> Optional[dict]:
        """Fetch from OpenWeatherMap (fallback)."""
        if not settings.openweather_api_key:
            return None
        try:
            data = await self._owm.get(
                "/weather",
                params={"q": city, "appid": settings.openweather_api_key, "units": "metric", "lang": lang},
            )
            if data and "main" in data:
                return {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data.get("wind", {}).get("speed", 0),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                    "icon": data.get("weather", [{}])[0].get("icon", ""),
                    "source": "OpenWeatherMap",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"OWM error: {exc}")
        return None

    def _weather_code_to_text(self, code: int, lang: str = "en") -> str:
        """Convert WMO weather code to localized text."""
        codes = {
            "en": {0: "☀️ Clear", 1: "🌤 Mainly clear", 2: "⛅ Partly cloudy", 3: "☁️ Overcast",
                   45: "🌫 Foggy", 48: "🌫 Rime fog", 51: "🌧 Light drizzle", 53: "🌧 Drizzle",
                   55: "🌧 Dense drizzle", 61: "🌧 Light rain", 63: "🌧 Rain", 65: "🌧 Heavy rain",
                   71: "🌨 Light snow", 73: "🌨 Snow", 75: "🌨 Heavy snow", 80: "🌧 Rain showers",
                   81: "🌧 Heavy showers", 82: "⛈ Violent rain", 85: "🌨 Snow showers",
                   95: "⛈ Thunderstorm", 96: "⛈ Thunderstorm + hail", 99: "⛈ Heavy thunderstorm"},
            "ar": {0: "☀️ صافي", 1: "🌤 صافي غالباً", 2: "⛅ غائم جزئياً", 3: "☁️ غائم",
                   45: "🌫 ضبابي", 48: "🌫 ضباب كثيف", 51: "🌧 رذاذ خفيف", 53: "🌧 رذاذ",
                   55: "🌧 رذاذ كثيف", 61: "🌧 مطر خفيف", 63: "🌧 مطر", 65: "🌧 مطر غزير",
                   71: "🌨 ثلج خفيف", 73: "🌨 ثلج", 75: "🌨 ثلج كثيف", 80: "🌧 زخات مطر",
                   81: "🌧 زخات قوية", 82: "⛈ أمطار عنيفة", 85: "🌨 زخات ثلج",
                   95: "⛈ عاصفة رعدية", 96: "⛈ رعدية مع بَرَد", 99: "⛈ عاصفة رعدية قوية"},
            "fr": {0: "☀️ Dégagé", 1: "🌤 Ciel clair", 2: "⛅ Partiellement nuageux", 3: "☁️ Couvert",
                   45: "🌫 Brouillard", 61: "🌧 Pluie légère", 63: "🌧 Pluie", 65: "🌧 Forte pluie",
                   71: "🌨 Neige légère", 73: "🌨 Neige", 95: "⛈ Orage"},
            "tr": {0: "☀️ Açık", 1: "🌤 Az bulutlu", 2: "⛅ Parçalı bulutlu", 3: "☁️ Kapalı",
                   45: "🌫 Sisli", 61: "🌧 Hafif yağmur", 63: "🌧 Yağmur", 65: "🌧 Şiddetli yağmur",
                   71: "🌨 Hafif kar", 73: "🌨 Kar", 95: "⛈ Fırtına"},
            "es": {0: "☀️ Despejado", 1: "🌤 Mayormente despejado", 2: "⛅ Parcialmente nublado", 3: "☁️ Nublado",
                   61: "🌧 Lluvia ligera", 63: "🌧 Lluvia", 65: "🌧 Lluvia fuerte", 95: "⛈ Tormenta"},
            "ru": {0: "☀️ Ясно", 1: "🌤 Малооблачно", 2: "⛅ Переменная облачность", 3: "☁️ Пасмурно",
                   61: "🌧 Небольшой дождь", 63: "🌧 Дождь", 65: "🌧 Сильный дождь", 71: "🌨 Снег", 95: "⛈ Гроза"},
            "fa": {0: "☀️ صاف", 1: "🌤 عمدتاً صاف", 2: "⛅ نیمه ابری", 3: "☁️ ابری",
                   61: "🌧 باران خفیف", 63: "🌧 باران", 65: "🌧 باران شدید", 95: "⛈ طوفان"},
            "de": {0: "☀️ Klar", 1: "🌤 Heiter", 2: "⛅ Teilweise bewölkt", 3: "☁️ Bedeckt",
                   61: "🌧 Leichter Regen", 63: "🌧 Regen", 65: "🌧 Starker Regen", 95: "⛈ Gewitter"},
        }
        lang_codes = codes.get(lang, codes["en"])
        return lang_codes.get(code, codes["en"].get(code, f"Code {code}"))

    async def close(self) -> None:
        await self._open_meteo.close()
        await self._owm.close()
        await self._geocode.close()


omega_weather = OmegaWeather()
'''

FILES["api_clients/omega_football.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)

MAJOR_LEAGUES = {
    "PL": {"name": "Premier League", "name_ar": "الدوري الإنجليزي", "country": "England"},
    "PD": {"name": "La Liga", "name_ar": "الدوري الإسباني", "country": "Spain"},
    "SA": {"name": "Serie A", "name_ar": "الدوري الإيطالي", "country": "Italy"},
    "BL1": {"name": "Bundesliga", "name_ar": "الدوري الألماني", "country": "Germany"},
    "FL1": {"name": "Ligue 1", "name_ar": "الدوري الفرنسي", "country": "France"},
    "CL": {"name": "Champions League", "name_ar": "دوري أبطال أوروبا", "country": "Europe"},
    "SPL": {"name": "Saudi Pro League", "name_ar": "دوري روشن", "country": "Saudi Arabia"},
    "ELC": {"name": "Championship", "name_ar": "الدوري الإنجليزي الدرجة الأولى", "country": "England"},
}


class OmegaFootball:
    """Football data with multi-source fusion (football-data.org + ESPN + TheSportsDB)."""

    def __init__(self):
        self._football_data = BaseAPIClient("football_data", "https://api.football-data.org/v4")
        self._espn = BaseAPIClient("espn_football", "https://site.api.espn.com/apis/site/v2/sports/soccer")
        self._sportsdb = BaseAPIClient("thesportsdb", "https://www.thesportsdb.com/api/v1/json")

    async def get_standings(self, league: str = "PL") -> dict[str, Any]:
        """Get league standings with multi-source fusion."""
        cache_key = f"football:standings:{league}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # Limited API first (auto-restores when quota renews)
        if quota.has_quota("football_data"):
            result = await self._fetch_fd_standings(league)
            if result and not result.get("error"):
                quota.use_quota("football_data")

        # Unlimited ESPN fallback (when football-data exhausted)
        if not result or result.get("error"):
            result = await self._fetch_espn_standings(league)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["football_static"])

        if not result or result.get("error"):
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                return result
        return result or {"error": True, "message": "Standings unavailable"}

    async def get_matches(self, league: str = "PL", status: str = "SCHEDULED") -> dict[str, Any]:
        """Get matches for a league."""
        cache_key = f"football:matches:{league}:{status}"
        ttl = CACHE_TTL["football_live"] if status == "LIVE" else CACHE_TTL["football_static"]
        cached = await cache.get(cache_key)
        if cached:
            return cached

        if quota.has_quota("football_data"):
            result = await self._fetch_fd_matches(league, status)
            if result and not result.get("error"):
                quota.use_quota("football_data")

        if not result or result.get("error"):
            result = await self._fetch_espn_scores(league)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=ttl)

        return result or {"error": True, "message": "Matches unavailable"}

    async def get_live_scores(self) -> dict[str, Any]:
        """Get all live scores across leagues."""
        cache_key = "football:live"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        scores = await self._fetch_espn_live()
        if scores:
            await cache.set(cache_key, scores, ttl=CACHE_TTL["football_live"])
            return scores

        return {"matches": [], "error": False, "message": "No live matches"}

    async def _fetch_fd_standings(self, league: str) -> Optional[dict]:
        """Fetch standings from football-data.org."""
        if not settings.football_data_key:
            return None
        try:
            data = await self._football_data.get(
                f"/competitions/{league}/standings",
                headers={"X-Auth-Token": settings.football_data_key},
            )
            if data and "standings" in data:
                standings = []
                for table in data["standings"]:
                    if table.get("type") == "TOTAL":
                        for entry in table.get("table", []):
                            standings.append({
                                "position": entry["position"],
                                "team": entry["team"]["name"],
                                "team_crest": entry["team"].get("crest", ""),
                                "played": entry["playedGames"],
                                "won": entry["won"],
                                "draw": entry["draw"],
                                "lost": entry["lost"],
                                "goals_for": entry["goalsFor"],
                                "goals_against": entry["goalsAgainst"],
                                "goal_diff": entry["goalDifference"],
                                "points": entry["points"],
                            })
                league_info = MAJOR_LEAGUES.get(league, {})
                return {
                    "league": league,
                    "league_name": league_info.get("name", league),
                    "league_name_ar": league_info.get("name_ar", league),
                    "standings": standings,
                    "source": "football-data.org",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"football-data standings error: {exc}")
        return None

    async def _fetch_fd_matches(self, league: str, status: str) -> Optional[dict]:
        """Fetch matches from football-data.org."""
        if not settings.football_data_key:
            return None
        try:
            params = {"status": status} if status != "ALL" else {}
            data = await self._football_data.get(
                f"/competitions/{league}/matches",
                params=params,
                headers={"X-Auth-Token": settings.football_data_key},
            )
            if data and "matches" in data:
                matches = []
                for m in data["matches"][:20]:
                    matches.append({
                        "home": m["homeTeam"]["name"],
                        "away": m["awayTeam"]["name"],
                        "score_home": m.get("score", {}).get("fullTime", {}).get("home"),
                        "score_away": m.get("score", {}).get("fullTime", {}).get("away"),
                        "status": m["status"],
                        "date": m.get("utcDate", ""),
                        "matchday": m.get("matchday"),
                    })
                return {"league": league, "matches": matches, "source": "football-data.org", "error": False}
        except Exception as exc:
            logger.debug(f"football-data matches error: {exc}")
        return None

    async def _fetch_espn_standings(self, league: str) -> Optional[dict]:
        """Fetch standings from ESPN (free, no key)."""
        espn_league_map = {"PL": "eng.1", "PD": "esp.1", "SA": "ita.1", "BL1": "ger.1", "FL1": "fra.1"}
        espn_league = espn_league_map.get(league)
        if not espn_league:
            return None
        try:
            data = await self._espn.get(f"/{espn_league}/standings")
            if data and "children" in data:
                standings = []
                for group in data.get("children", []):
                    for entry in group.get("standings", {}).get("entries", []):
                        team_info = entry.get("team", {})
                        stats = {s["name"]: s["value"] for s in entry.get("stats", [])}
                        standings.append({
                            "position": int(stats.get("rank", 0)),
                            "team": team_info.get("displayName", ""),
                            "team_crest": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else "",
                            "played": int(stats.get("gamesPlayed", 0)),
                            "won": int(stats.get("wins", 0)),
                            "draw": int(stats.get("ties", 0)),
                            "lost": int(stats.get("losses", 0)),
                            "points": int(stats.get("points", 0)),
                            "goal_diff": int(stats.get("pointDifferential", 0)),
                        })
                league_info = MAJOR_LEAGUES.get(league, {})
                return {
                    "league": league,
                    "league_name": league_info.get("name", league),
                    "standings": sorted(standings, key=lambda x: x["position"]),
                    "source": "ESPN",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"ESPN standings error: {exc}")
        return None

    async def _fetch_espn_scores(self, league: str) -> Optional[dict]:
        """Fetch scores from ESPN."""
        espn_map = {"PL": "eng.1", "PD": "esp.1", "SA": "ita.1", "BL1": "ger.1", "FL1": "fra.1"}
        espn_league = espn_map.get(league)
        if not espn_league:
            return None
        try:
            data = await self._espn.get(f"/{espn_league}/scoreboard")
            if data and "events" in data:
                matches = []
                for event in data["events"]:
                    comps = event.get("competitions", [{}])
                    if comps:
                        comp = comps[0]
                        teams = comp.get("competitors", [])
                        if len(teams) >= 2:
                            home = next((t for t in teams if t.get("homeAway") == "home"), teams[0])
                            away = next((t for t in teams if t.get("homeAway") == "away"), teams[1])
                            matches.append({
                                "home": home.get("team", {}).get("displayName", ""),
                                "away": away.get("team", {}).get("displayName", ""),
                                "score_home": home.get("score"),
                                "score_away": away.get("score"),
                                "status": event.get("status", {}).get("type", {}).get("name", ""),
                                "date": event.get("date", ""),
                            })
                return {"league": league, "matches": matches, "source": "ESPN", "error": False}
        except Exception as exc:
            logger.debug(f"ESPN scores error: {exc}")
        return None

    async def _fetch_espn_live(self) -> Optional[dict]:
        """Fetch all live scores from ESPN."""
        all_matches = []
        for espn_league in ["eng.1", "esp.1", "ita.1", "ger.1", "fra.1"]:
            try:
                data = await self._espn.get(f"/{espn_league}/scoreboard")
                if data and "events" in data:
                    for event in data["events"]:
                        status = event.get("status", {}).get("type", {}).get("state", "")
                        if status == "in":
                            comps = event.get("competitions", [{}])
                            if comps:
                                comp = comps[0]
                                teams = comp.get("competitors", [])
                                if len(teams) >= 2:
                                    home = next((t for t in teams if t.get("homeAway") == "home"), teams[0])
                                    away = next((t for t in teams if t.get("homeAway") == "away"), teams[1])
                                    all_matches.append({
                                        "league": espn_league,
                                        "home": home.get("team", {}).get("displayName", ""),
                                        "away": away.get("team", {}).get("displayName", ""),
                                        "score_home": home.get("score"),
                                        "score_away": away.get("score"),
                                        "clock": event.get("status", {}).get("displayClock", ""),
                                        "period": event.get("status", {}).get("period", 0),
                                    })
            except Exception as exc:
                logger.debug(f"ESPN live error for {espn_league}: {exc}")

        return {"matches": all_matches, "error": False}

    async def close(self) -> None:
        await self._football_data.close()
        await self._espn.close()
        await self._sportsdb.close()


omega_football = OmegaFootball()
'''

FILES["api_clients/omega_movies.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaMovies:
    """Movies & TV with TMDB (primary) + OMDb (IMDb/RT ratings) + Jikan (anime)."""

    def __init__(self):
        self._tmdb = BaseAPIClient("tmdb", "https://api.themoviedb.org/3")
        self._omdb = BaseAPIClient("omdb", "https://www.omdbapi.com")
        self._jikan = BaseAPIClient("jikan", "https://api.jikan.moe/v4")

    async def search(self, query: str, media_type: str = "multi", lang: str = "en") -> dict[str, Any]:
        """Search for movies/TV/anime."""
        cache_key = f"movie:search:{query}:{media_type}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        if media_type == "anime":
            result = await self._search_anime(query)
        else:
            result = await self._search_tmdb(query, media_type, lang)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])

        return result or {"results": [], "error": True}

    async def get_details(self, tmdb_id: int, media_type: str = "movie", lang: str = "en") -> dict[str, Any]:
        """Get detailed info for a movie/TV show."""
        cache_key = f"movie:detail:{tmdb_id}:{media_type}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = await self._fetch_tmdb_details(tmdb_id, media_type, lang)

        if result and not result.get("error"):
            if result.get("imdb_id") and settings.omdb_api_key:
                omdb_data = await self._fetch_omdb(result["imdb_id"])
                if omdb_data:
                    result["imdb_rating"] = omdb_data.get("imdb_rating")
                    result["rotten_tomatoes"] = omdb_data.get("rotten_tomatoes")
                    result["metacritic"] = omdb_data.get("metacritic")

            await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])

        return result or {"error": True, "message": "Details unavailable"}

    async def get_trending(self, media_type: str = "all", time_window: str = "week", lang: str = "en") -> dict[str, Any]:
        """Get trending movies/TV."""
        cache_key = f"movie:trending:{media_type}:{time_window}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._tmdb.get(
                f"/trending/{media_type}/{time_window}",
                params={"api_key": settings.tmdb_api_key, "language": lang},
            )
            if data and "results" in data:
                results = [{
                    "id": item["id"],
                    "title": item.get("title") or item.get("name", ""),
                    "media_type": item.get("media_type", media_type),
                    "overview": item.get("overview", ""),
                    "vote_average": item.get("vote_average", 0),
                    "poster": f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else "",
                    "release_date": item.get("release_date") or item.get("first_air_date", ""),
                } for item in data["results"][:20]]

                result = {"results": results, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])
                return result
        except Exception as exc:
            logger.debug(f"TMDB trending error: {exc}")

        return {"results": [], "error": True}

    async def _search_tmdb(self, query: str, media_type: str, lang: str) -> Optional[dict]:
        """Search TMDB."""
        try:
            endpoint = f"/search/{media_type}" if media_type in ("movie", "tv") else "/search/multi"
            data = await self._tmdb.get(
                endpoint,
                params={"api_key": settings.tmdb_api_key, "query": query, "language": lang},
            )
            if data and "results" in data:
                results = [{
                    "id": item["id"],
                    "title": item.get("title") or item.get("name", ""),
                    "media_type": item.get("media_type", media_type),
                    "overview": item.get("overview", "")[:200],
                    "vote_average": item.get("vote_average", 0),
                    "poster": f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else "",
                    "release_date": item.get("release_date") or item.get("first_air_date", ""),
                } for item in data["results"][:10]]
                return {"results": results, "error": False}
        except Exception as exc:
            logger.debug(f"TMDB search error: {exc}")
        return None

    async def _fetch_tmdb_details(self, tmdb_id: int, media_type: str, lang: str) -> Optional[dict]:
        """Fetch detailed info from TMDB."""
        try:
            data = await self._tmdb.get(
                f"/{media_type}/{tmdb_id}",
                params={"api_key": settings.tmdb_api_key, "language": lang, "append_to_response": "credits,videos"},
            )
            if data:
                result = {
                    "id": data["id"],
                    "title": data.get("title") or data.get("name", ""),
                    "overview": data.get("overview", ""),
                    "vote_average": data.get("vote_average", 0),
                    "vote_count": data.get("vote_count", 0),
                    "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else "",
                    "backdrop": f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}" if data.get("backdrop_path") else "",
                    "release_date": data.get("release_date") or data.get("first_air_date", ""),
                    "runtime": data.get("runtime") or data.get("episode_run_time", [0])[0] if data.get("episode_run_time") else 0,
                    "genres": [g["name"] for g in data.get("genres", [])],
                    "imdb_id": data.get("imdb_id", ""),
                    "budget": data.get("budget", 0),
                    "revenue": data.get("revenue", 0),
                    "status": data.get("status", ""),
                    "tagline": data.get("tagline", ""),
                    "media_type": media_type,
                    "error": False,
                }

                credits = data.get("credits", {})
                result["cast"] = [{"name": c["name"], "character": c.get("character", "")} for c in credits.get("cast", [])[:10]]
                result["director"] = next((c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"), "")

                videos = data.get("videos", {}).get("results", [])
                trailer = next((v for v in videos if v.get("type") == "Trailer" and v.get("site") == "YouTube"), None)
                result["trailer_url"] = f"https://youtube.com/watch?v={trailer['key']}" if trailer else ""

                return result
        except Exception as exc:
            logger.debug(f"TMDB details error: {exc}")
        return None

    async def _fetch_omdb(self, imdb_id: str) -> Optional[dict]:
        """Fetch ratings from OMDb (7-day cache)."""
        cache_key = f"omdb:{imdb_id}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._omdb.get(
                "/",
                params={"apikey": settings.omdb_api_key, "i": imdb_id},
            )
            if data and data.get("Response") == "True":
                result = {
                    "imdb_rating": data.get("imdbRating", "N/A"),
                    "metacritic": data.get("Metascore", "N/A"),
                }
                for rating in data.get("Ratings", []):
                    if "Rotten Tomatoes" in rating.get("Source", ""):
                        result["rotten_tomatoes"] = rating["Value"]
                        break
                else:
                    result["rotten_tomatoes"] = "N/A"

                await cache.set(cache_key, result, ttl=604800)
                return result
        except Exception as exc:
            logger.debug(f"OMDb error: {exc}")
        return None

    async def _search_anime(self, query: str) -> Optional[dict]:
        """Search anime using Jikan (MyAnimeList)."""
        try:
            data = await self._jikan.get("/anime", params={"q": query, "limit": 10})
            if data and "data" in data:
                results = [{
                    "id": item["mal_id"],
                    "title": item.get("title_english") or item.get("title", ""),
                    "title_japanese": item.get("title_japanese", ""),
                    "media_type": "anime",
                    "overview": item.get("synopsis", "")[:200],
                    "vote_average": item.get("score", 0),
                    "poster": item.get("images", {}).get("jpg", {}).get("image_url", ""),
                    "episodes": item.get("episodes"),
                    "status": item.get("status", ""),
                    "aired": item.get("aired", {}).get("string", ""),
                } for item in data["data"]]
                return {"results": results, "error": False}
        except Exception as exc:
            logger.debug(f"Jikan search error: {exc}")
        return None

    async def close(self) -> None:
        await self._tmdb.close()
        await self._omdb.close()
        await self._jikan.close()


omega_movies = OmegaMovies()
'''

FILES["api_clients/omega_stocks.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


class OmegaStocks:
    """Stock market data using yfinance + Alpha Vantage."""

    def __init__(self):
        self._alpha = BaseAPIClient("alpha_vantage", "https://www.alphavantage.co")

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Get stock quote."""
        cache_key = f"stock:{symbol.upper()}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = await self._fetch_yfinance(symbol)
        if (not result or result.get("error")) and quota.has_quota("alpha_vantage"):
            result = await self._fetch_alpha_vantage(symbol)
            if result and not result.get("error"):
                quota.use_quota("alpha_vantage")

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["stocks"])

        if not result or result.get("error"):
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                return result
        return result or {"error": True, "symbol": symbol, "message": "Quote unavailable"}

    async def _fetch_yfinance(self, symbol: str) -> Optional[dict]:
        """Fetch from yfinance."""
        try:
            import yfinance as yf
            import asyncio
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)

            if info and info.get("regularMarketPrice"):
                return {
                    "symbol": symbol.upper(),
                    "name": info.get("shortName", symbol),
                    "price": info.get("regularMarketPrice", 0),
                    "change": info.get("regularMarketChange", 0),
                    "change_percent": info.get("regularMarketChangePercent", 0),
                    "high": info.get("dayHigh", 0),
                    "low": info.get("dayLow", 0),
                    "volume": info.get("volume", 0),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE"),
                    "52w_high": info.get("fiftyTwoWeekHigh", 0),
                    "52w_low": info.get("fiftyTwoWeekLow", 0),
                    "currency": info.get("currency", "USD"),
                    "exchange": info.get("exchange", ""),
                    "source": "yfinance",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"yfinance error for {symbol}: {exc}")
        return None

    async def _fetch_alpha_vantage(self, symbol: str) -> Optional[dict]:
        """Fetch from Alpha Vantage."""
        from config import settings
        if not settings.alpha_vantage_key:
            return None
        try:
            data = await self._alpha.get(
                "/query",
                params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": settings.alpha_vantage_key},
            )
            if data and "Global Quote" in data:
                q = data["Global Quote"]
                return {
                    "symbol": q.get("01. symbol", symbol),
                    "price": float(q.get("05. price", 0)),
                    "change": float(q.get("09. change", 0)),
                    "change_percent": q.get("10. change percent", "0%"),
                    "volume": int(q.get("06. volume", 0)),
                    "source": "Alpha Vantage",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"Alpha Vantage error: {exc}")
        return None

    async def close(self) -> None:
        await self._alpha.close()


omega_stocks = OmegaStocks()
'''

FILES["api_clients/omega_crypto.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaCrypto:
    """Cryptocurrency data from CoinGecko + CoinCap + Binance."""

    def __init__(self):
        self._coingecko = BaseAPIClient("coingecko", "https://api.coingecko.com/api/v3")
        self._coincap = BaseAPIClient("coincap", "https://api.coincap.io/v2")

    async def get_price(self, coin_id: str = "bitcoin", currency: str = "usd") -> dict[str, Any]:
        """Get cryptocurrency price."""
        cache_key = f"crypto:{coin_id}:{currency}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        result = await self._fetch_coingecko(coin_id, currency)
        if not result or result.get("error"):
            result = await self._fetch_coincap(coin_id)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["crypto"])

        if not result or result.get("error"):
            stale = await cache.get_stale(cache_key)
            if stale and stale.get("data"):
                result = stale["data"]
                result["stale"] = True
                return result
        return result or {"error": True, "message": "Price unavailable"}

    async def get_top_coins(self, limit: int = 20, currency: str = "usd") -> dict[str, Any]:
        """Get top cryptocurrencies by market cap."""
        cache_key = f"crypto:top:{limit}:{currency}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._coingecko.get(
                "/coins/markets",
                params={"vs_currency": currency, "order": "market_cap_desc", "per_page": limit, "page": 1, "sparkline": "false"},
            )
            if data and isinstance(data, list):
                coins = [{
                    "id": c["id"],
                    "symbol": c["symbol"].upper(),
                    "name": c["name"],
                    "price": c["current_price"],
                    "change_24h": c.get("price_change_percentage_24h", 0),
                    "market_cap": c.get("market_cap", 0),
                    "volume_24h": c.get("total_volume", 0),
                    "rank": c.get("market_cap_rank", 0),
                    "image": c.get("image", ""),
                } for c in data]

                result = {"coins": coins, "currency": currency, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["crypto"])
                return result
        except Exception as exc:
            logger.debug(f"CoinGecko top coins error: {exc}")

        return {"coins": [], "error": True}

    async def _fetch_coingecko(self, coin_id: str, currency: str) -> Optional[dict]:
        """Fetch from CoinGecko."""
        try:
            data = await self._coingecko.get(
                f"/coins/{coin_id}",
                params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
            )
            if data and "market_data" in data:
                md = data["market_data"]
                return {
                    "id": data["id"],
                    "symbol": data["symbol"].upper(),
                    "name": data["name"],
                    "price": md["current_price"].get(currency, 0),
                    "change_24h": md.get("price_change_percentage_24h", 0),
                    "change_7d": md.get("price_change_percentage_7d", 0),
                    "market_cap": md.get("market_cap", {}).get(currency, 0),
                    "volume_24h": md.get("total_volume", {}).get(currency, 0),
                    "ath": md.get("ath", {}).get(currency, 0),
                    "atl": md.get("atl", {}).get(currency, 0),
                    "rank": data.get("market_cap_rank", 0),
                    "image": data.get("image", {}).get("small", ""),
                    "source": "CoinGecko",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"CoinGecko error: {exc}")
        return None

    async def _fetch_coincap(self, coin_id: str) -> Optional[dict]:
        """Fetch from CoinCap (fallback)."""
        try:
            data = await self._coincap.get(f"/assets/{coin_id}")
            if data and "data" in data:
                d = data["data"]
                return {
                    "id": d["id"],
                    "symbol": d["symbol"],
                    "name": d["name"],
                    "price": float(d.get("priceUsd", 0)),
                    "change_24h": float(d.get("changePercent24Hr", 0)),
                    "market_cap": float(d.get("marketCapUsd", 0)),
                    "volume_24h": float(d.get("volumeUsd24Hr", 0)),
                    "rank": int(d.get("rank", 0)),
                    "source": "CoinCap",
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"CoinCap error: {exc}")
        return None

    async def close(self) -> None:
        await self._coingecko.close()
        await self._coincap.close()


omega_crypto = OmegaCrypto()
'''

FILES["api_clients/omega_news.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)


class OmegaNews:
    """News aggregation from NewsAPI + GNews + RSS feeds."""

    def __init__(self):
        self._newsapi = BaseAPIClient("newsapi", "https://newsapi.org/v2")
        self._gnews = BaseAPIClient("gnews", "https://gnews.io/api/v4")
        self._rss = BaseAPIClient("rss_news")

    async def get_headlines(self, category: str = "general", country: str = "us", lang: str = "en") -> dict[str, Any]:
        """Get top headlines."""
        cache_key = f"news:headlines:{category}:{country}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # Limited APIs first (auto-restore when quota renews)
        if quota.has_quota("newsapi"):
            result = await self._fetch_newsapi(category, country)
            if result and not result.get("error"):
                quota.use_quota("newsapi")
        if (not result or result.get("error")) and quota.has_quota("gnews"):
            result = await self._fetch_gnews(category, lang)
            if result and not result.get("error"):
                quota.use_quota("gnews")
        # Unlimited RSS fallback (when all limited exhausted)
        if not result or result.get("error"):
            result = await self._fetch_rss(lang)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["news"])

        return result or {"articles": [], "error": True}

    async def search_news(self, query: str, lang: str = "en") -> dict[str, Any]:
        """Search news by keyword."""
        cache_key = f"news:search:{query}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            if settings.newsapi_key:
                data = await self._newsapi.get(
                    "/everything",
                    params={"apiKey": settings.newsapi_key, "q": query, "language": lang, "pageSize": 10, "sortBy": "publishedAt"},
                )
                if data and data.get("status") == "ok":
                    articles = self._parse_newsapi_articles(data.get("articles", []))
                    result = {"articles": articles, "query": query, "error": False}
                    await cache.set(cache_key, result, ttl=CACHE_TTL["news"])
                    return result
        except Exception as exc:
            logger.debug(f"NewsAPI search error: {exc}")

        return {"articles": [], "error": True}

    async def _fetch_newsapi(self, category: str, country: str) -> Optional[dict]:
        """Fetch from NewsAPI."""
        if not settings.newsapi_key:
            return None
        try:
            data = await self._newsapi.get(
                "/top-headlines",
                params={"apiKey": settings.newsapi_key, "category": category, "country": country, "pageSize": 20},
            )
            if data and data.get("status") == "ok":
                articles = self._parse_newsapi_articles(data.get("articles", []))
                return {"articles": articles, "source": "NewsAPI", "error": False}
        except Exception as exc:
            logger.debug(f"NewsAPI error: {exc}")
        return None

    async def _fetch_gnews(self, category: str, lang: str) -> Optional[dict]:
        """Fetch from GNews."""
        if not settings.gnews_api_key:
            return None
        try:
            data = await self._gnews.get(
                "/top-headlines",
                params={"token": settings.gnews_api_key, "topic": category, "lang": lang, "max": 10},
            )
            if data and "articles" in data:
                articles = [{
                    "title": a.get("title", ""),
                    "description": a.get("description", ""),
                    "url": a.get("url", ""),
                    "source": a.get("source", {}).get("name", ""),
                    "published_at": a.get("publishedAt", ""),
                    "image": a.get("image", ""),
                } for a in data["articles"]]
                return {"articles": articles, "source": "GNews", "error": False}
        except Exception as exc:
            logger.debug(f"GNews error: {exc}")
        return None

    async def _fetch_rss(self, lang: str) -> Optional[dict]:
        """Fetch from RSS feeds as fallback."""
        feeds = {
            "en": [
                "https://feeds.bbci.co.uk/news/rss.xml",
                "http://feeds.reuters.com/reuters/topNews",
            ],
            "ar": [
                "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9",
                "https://www.bbc.com/arabic/rss.xml",
            ],
        }

        rss_urls = feeds.get(lang, feeds["en"])
        articles = []

        for url in rss_urls:
            try:
                html = await self._rss.fetch_html(url)
                if html:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "lxml")
                    items = soup.find_all("item")[:10]
                    for item in items:
                        articles.append({
                            "title": item.find("title").get_text(strip=True) if item.find("title") else "",
                            "description": item.find("description").get_text(strip=True)[:200] if item.find("description") else "",
                            "url": item.find("link").get_text(strip=True) if item.find("link") else "",
                            "source": "RSS",
                            "published_at": item.find("pubDate").get_text(strip=True) if item.find("pubDate") else "",
                        })
            except Exception as exc:
                logger.debug(f"RSS error for {url}: {exc}")

        if articles:
            return {"articles": articles[:10], "source": "RSS", "error": False}
        return None

    def _parse_newsapi_articles(self, articles: list) -> list[dict]:
        """Parse NewsAPI articles into standard format."""
        return [{
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", ""),
            "published_at": a.get("publishedAt", ""),
            "image": a.get("urlToImage", ""),
        } for a in articles if a.get("title")]

    async def close(self) -> None:
        await self._newsapi.close()
        await self._gnews.close()
        await self._rss.close()


omega_news = OmegaNews()
'''

FILES["api_clients/omega_flights.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaFlights:
    """Flight tracking using OpenSky Network (free, no key)."""

    def __init__(self):
        self._opensky = BaseAPIClient("opensky", "https://opensky-network.org/api")

    async def get_flights_by_airport(self, airport_icao: str) -> dict[str, Any]:
        """Get departures/arrivals for an airport."""
        cache_key = f"flights:{airport_icao}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        import time
        end_time = int(time.time())
        begin_time = end_time - 7200

        try:
            departures = await self._opensky.get(
                "/flights/departure",
                params={"airport": airport_icao, "begin": begin_time, "end": end_time},
            )
            arrivals = await self._opensky.get(
                "/flights/arrival",
                params={"airport": airport_icao, "begin": begin_time, "end": end_time},
            )

            result = {
                "airport": airport_icao,
                "departures": self._parse_flights(departures) if isinstance(departures, list) else [],
                "arrivals": self._parse_flights(arrivals) if isinstance(arrivals, list) else [],
                "error": False,
            }
            await cache.set(cache_key, result, ttl=CACHE_TTL["flights"])
            return result
        except Exception as exc:
            logger.debug(f"OpenSky error: {exc}")

        return {"airport": airport_icao, "departures": [], "arrivals": [], "error": True}

    async def track_flight(self, callsign: str) -> dict[str, Any]:
        """Track a specific flight by callsign."""
        try:
            data = await self._opensky.get("/states/all", params={"callsign": callsign.strip()})
            if data and data.get("states"):
                state = data["states"][0]
                return {
                    "callsign": state[1].strip() if state[1] else callsign,
                    "origin_country": state[2],
                    "longitude": state[5],
                    "latitude": state[6],
                    "altitude": state[7],
                    "velocity": state[9],
                    "heading": state[10],
                    "on_ground": state[8],
                    "error": False,
                }
        except Exception as exc:
            logger.debug(f"Flight track error: {exc}")

        return {"callsign": callsign, "error": True, "message": "Flight not found"}

    def _parse_flights(self, flights: list) -> list[dict]:
        """Parse flight data."""
        result = []
        for f in flights[:20]:
            result.append({
                "callsign": f.get("callsign", "").strip(),
                "departure": f.get("estDepartureAirport", ""),
                "arrival": f.get("estArrivalAirport", ""),
                "first_seen": f.get("firstSeen"),
                "last_seen": f.get("lastSeen"),
            })
        return result

    async def close(self) -> None:
        await self._opensky.close()


omega_flights = OmegaFlights()
'''

FILES["api_clients/omega_geo.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaGeo:
    """Geocoding and location services."""

    def __init__(self):
        self._nominatim = BaseAPIClient("nominatim", "https://nominatim.openstreetmap.org")

    async def geocode(self, query: str) -> Optional[dict[str, Any]]:
        """Geocode a location name to coordinates."""
        cache_key = f"geo:{query.lower()}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._nominatim.get(
                "/search",
                params={"q": query, "format": "json", "limit": 1, "accept-language": "en"},
                headers={"User-Agent": "OmegaBot/1.0"},
            )
            if data and isinstance(data, list) and data:
                result = {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "name": data[0].get("display_name", query),
                    "type": data[0].get("type", ""),
                }
                await cache.set(cache_key, result, ttl=86400)
                return result
        except Exception as exc:
            logger.debug(f"Geocode error: {exc}")
        return None

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[dict[str, Any]]:
        """Reverse geocode coordinates to location name."""
        try:
            data = await self._nominatim.get(
                "/reverse",
                params={"lat": lat, "lon": lon, "format": "json", "accept-language": "en"},
                headers={"User-Agent": "OmegaBot/1.0"},
            )
            if data and "address" in data:
                return {
                    "city": data["address"].get("city") or data["address"].get("town", ""),
                    "country": data["address"].get("country", ""),
                    "country_code": data["address"].get("country_code", "").upper(),
                    "display_name": data.get("display_name", ""),
                }
        except Exception as exc:
            logger.debug(f"Reverse geocode error: {exc}")
        return None

    async def close(self) -> None:
        await self._nominatim.close()


omega_geo = OmegaGeo()
'''

FILES["api_clients/omega_quakes.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)


class OmegaQuakes:
    """Earthquake data from USGS (free, no key)."""

    def __init__(self):
        self._usgs = BaseAPIClient("usgs", "https://earthquake.usgs.gov/fdsnws/event/1")

    async def get_recent(self, min_magnitude: float = 4.0, limit: int = 20) -> dict[str, Any]:
        """Get recent earthquakes."""
        cache_key = f"quakes:recent:{min_magnitude}:{limit}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            data = await self._usgs.get(
                "/query",
                params={
                    "format": "geojson",
                    "minmagnitude": min_magnitude,
                    "orderby": "time",
                    "limit": limit,
                },
            )

            if data and "features" in data:
                quakes = []
                for feature in data["features"]:
                    props = feature["properties"]
                    coords = feature["geometry"]["coordinates"]
                    quakes.append({
                        "title": props.get("title", ""),
                        "magnitude": props.get("mag", 0),
                        "place": props.get("place", ""),
                        "time": props.get("time"),
                        "longitude": coords[0],
                        "latitude": coords[1],
                        "depth_km": coords[2],
                        "tsunami": props.get("tsunami", 0),
                        "alert": props.get("alert"),
                        "url": props.get("url", ""),
                    })

                result = {"quakes": quakes, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["quakes"])
                return result
        except Exception as exc:
            logger.debug(f"USGS error: {exc}")

        return {"quakes": [], "error": True}

    async def get_by_region(self, lat: float, lon: float, radius_km: float = 500, min_mag: float = 3.0) -> dict[str, Any]:
        """Get earthquakes near a location."""
        try:
            data = await self._usgs.get(
                "/query",
                params={
                    "format": "geojson",
                    "latitude": lat,
                    "longitude": lon,
                    "maxradiuskm": radius_km,
                    "minmagnitude": min_mag,
                    "orderby": "time",
                    "limit": 20,
                },
            )
            if data and "features" in data:
                quakes = [{
                    "title": f["properties"].get("title", ""),
                    "magnitude": f["properties"].get("mag", 0),
                    "place": f["properties"].get("place", ""),
                    "time": f["properties"].get("time"),
                    "depth_km": f["geometry"]["coordinates"][2],
                } for f in data["features"]]
                return {"quakes": quakes, "error": False}
        except Exception as exc:
            logger.debug(f"USGS region error: {exc}")
        return {"quakes": [], "error": True}

    async def close(self) -> None:
        await self._usgs.close()


omega_quakes = OmegaQuakes()
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 5 — HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES["handlers/__init__.py"] = """
from handlers.start import register_start_handlers
from handlers.gold import register_gold_handlers
from handlers.currency import register_currency_handlers
from handlers.fuel import register_fuel_handlers
from handlers.weather import register_weather_handlers
from handlers.football import register_football_handlers
from handlers.movies import register_movies_handlers
from handlers.cv_generator import register_cv_handlers
from handlers.logo_generator import register_logo_handlers
from handlers.ai_chat import register_ai_handlers
from handlers.stocks import register_stocks_handlers
from handlers.crypto import register_crypto_handlers
from handlers.news import register_news_handlers
from handlers.flights import register_flights_handlers
from handlers.settings import register_settings_handlers
from handlers.stats import register_stats_handlers


def register_all_handlers(dp):
    register_start_handlers(dp)
    register_gold_handlers(dp)
    register_currency_handlers(dp)
    register_fuel_handlers(dp)
    register_weather_handlers(dp)
    register_football_handlers(dp)
    register_movies_handlers(dp)
    register_cv_handlers(dp)
    register_logo_handlers(dp)
    register_ai_handlers(dp)
    register_stocks_handlers(dp)
    register_crypto_handlers(dp)
    register_news_handlers(dp)
    register_flights_handlers(dp)
    register_settings_handlers(dp)
    register_stats_handlers(dp)
"""

FILES["handlers/start.py"] = r'''
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart

from config import t, MENU_LABELS, MENU_LAYOUT, get_menu_label, settings
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)
router = Router(name="start")


def _build_main_menu(lang: str = "en") -> InlineKeyboardMarkup:
    from config import MENU_LAYOUT, get_menu_label
    buttons = []
    for row in MENU_LAYOUT:
        btn_row = [InlineKeyboardButton(text=get_menu_label(key, lang), callback_data=f"menu:{key}") for key in row]
        buttons.append(btn_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str = "en") -> None:
    try:
        name = message.from_user.first_name or "User"
        welcome = t("welcome", lang, name=name)
        await message.answer(welcome, reply_markup=_build_main_menu(lang))
    except Exception as exc:
        logger.error(f"Start error: {exc}", exc_info=True)
        await message.answer(t("error", "en"))


@router.message(Command("menu"))
async def cmd_menu(message: Message, lang: str = "en") -> None:
    await message.answer(t("main_menu", "en"), reply_markup=_build_main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "en") -> None:
    await message.answer(t("help_text", lang), parse_mode="Markdown")


@router.callback_query(F.data.startswith("menu:"))
async def handle_menu_callback(callback: CallbackQuery, lang: str = "en") -> None:
    action = callback.data.split(":")[1]
    action_map = {
        "gold": "/gold", "currency": "/currency", "fuel": "/fuel",
        "weather": "/weather", "football": "/football", "movies": "/movie",
        "cv": "/cv", "logo": "/logo", "ai_chat": "/ai",
        "stocks": "/stock", "crypto": "/crypto", "news": "/news",
        "flights": "/flight", "quakes": "/quakes", "settings": "/settings",
    }
    cmd = action_map.get(action, "/help")
    await callback.answer()
    await callback.message.answer(f"Use {cmd} command or just type your request!")


def register_start_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/gold.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_metals import omega_metals
from config import GOLD_KARATS, METAL_NAMES, t

logger = logging.getLogger(__name__)
router = Router(name="gold")


@router.message(Command("gold"))
async def cmd_gold(message: Message, lang: str = "en") -> None:
    await message.answer(t("fetching", lang))
    try:
        data = await omega_metals.get_prices("XAU", "USD")
        if data.get("error"):
            await message.answer(t("error", lang))
            return

        price = f"{data['price_per_ounce']:,.2f}"
        text = t("gold_price", lang).replace("{price}", price)
        if data.get("stale"):
            text += f"\n\n⏰ {data.get('age_minutes', 0)} min ago"

        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("gold_karats_btn", lang), callback_data="gold:karats"),
             InlineKeyboardButton(text=t("btn_refresh", lang), callback_data="gold:refresh")],
            [InlineKeyboardButton(text=t("btn_silver", lang), callback_data="metal:XAG"),
             InlineKeyboardButton(text=t("btn_platinum", lang), callback_data="metal:XPT")],
        ])
        await message.answer(text, parse_mode="Markdown", reply_markup=buttons)
    except Exception as exc:
        logger.error(f"Gold error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data.startswith("metal:"))
async def handle_metal(callback: CallbackQuery, lang: str = "en") -> None:
    metal = callback.data.split(":")[1]
    await callback.answer(t("fetching", lang))
    try:
        data = await omega_metals.get_prices(metal, "USD")
        if data.get("error"):
            await callback.message.answer(t("error", lang))
            return
        name = METAL_NAMES.get(metal, {}).get(lang, METAL_NAMES.get(metal, {}).get("en", metal))
        text = f"🪙 **{name}**\n\n💰 ${data['price_per_ounce']:,.2f}"
        await callback.message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Metal callback error: {exc}", exc_info=True)


@router.callback_query(lambda c: c.data == "gold:karats")
async def handle_gold_karats(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    try:
        data = await omega_metals.get_prices("XAU", "USD")
        if data.get("error") or not data.get("karats"):
            await callback.message.answer(t("error", lang))
            return
        text = t("gold_karats_title", lang) + "\n\n"
        for karat in ["24K", "22K", "21K", "18K", "14K", "10K", "9K"]:
            if karat in data["karats"]:
                text += f"  {karat}: ${data['karats'][karat]['per_gram']:,.2f}\n"
        await callback.message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Karats error: {exc}", exc_info=True)


@router.callback_query(lambda c: c.data == "gold:refresh")
async def handle_gold_refresh(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer(t("fetching", lang))
    from services.cache_service import cache
    await cache.delete("metals:XAU:USD")
    await cmd_gold(callback.message, lang=lang)


def register_gold_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/currency.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_currency import omega_currency
from config import t

logger = logging.getLogger(__name__)
router = Router(name="currency")


@router.message(Command("currency"))
async def cmd_currency(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    base = args[0].upper() if len(args) >= 1 else "USD"
    target = args[1].upper() if len(args) >= 2 else None

    await message.answer(t("fetching", lang))
    try:
        if target:
            data = await omega_currency.get_rate(base, target)
            if data.get("error"):
                await message.answer(t("error", lang))
                return
            text = f"💱 **{base} → {target}**\n\n"
            text += f"{t('label_price', lang)}: {data['rate']:,.6f}\n"

            if data.get("has_parallel"):
                text += f"\n{t('label_parallel', lang)}: {data['parallel_rate']:,.2f}\n"

        else:
            data = await omega_currency.get_multiple_rates(base)
            text = t("currency_rates_title", lang, base=base) + "\n\n"
            for currency, info in data.items():
                if not info.get("error"):
                    text += f"  {currency}: {info['rate']:,.4f}"
                    if info.get("has_parallel"):
                        text += f" ({t('label_parallel', lang)}: {info['parallel_rate']:,.2f})"
                    text += "\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Currency error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_currency_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/fuel.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_fuel import omega_fuel
from config import t

logger = logging.getLogger(__name__)
router = Router(name="fuel")


@router.message(Command("fuel"))
async def cmd_fuel(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    # Only accept a valid 2-letter country code; ignore natural language words
    country = "LB"
    if args:
        candidate = args[0].upper()
        if len(candidate) == 2 and candidate.isalpha():
            country = candidate

    await message.answer(t("fetching", lang))
    try:
        data = await omega_fuel.get_prices(country)
        if data.get("error"):
            await message.answer(t("error", lang))
            return

        name = data.get("country_name_ar", data.get("country_name_en", country))
        text = t("fuel_title_country", lang, country=name) + "\n\n"

        prices = data.get("prices", {})
        if isinstance(prices, dict):
            for fuel_type, price in prices.items():
                if fuel_type != "note":
                    text += f"  🔹 {fuel_type}: {price}\n"

        if data.get("note"):
            text += f"\n{t('label_note', lang)}: {data['note']}"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Fuel error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_fuel_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/weather.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_weather import omega_weather
from config import t

logger = logging.getLogger(__name__)
router = Router(name="weather")


@router.message(Command("weather"))
async def cmd_weather(message: Message, lang: str = "en") -> None:
    city = message.text.replace("/weather", "").strip() if message.text else ""
    if not city:
        city = "Beirut"  # default to Beirut if no city given

    await message.answer(t("fetching", lang))
    try:
        data = await omega_weather.get_weather(city, lang)
        if data.get("error"):
            await message.answer(t("error", lang))
            return

        text = f"🌤 **{data.get('city', city)}**\n\n"
        text += f"🌡 {t('label_temp', lang)}: {data['temperature']}°C\n"
        text += f"🤔 {t('label_feels', lang)}: {data.get('feels_like', 'N/A')}°C\n"
        text += f"💧 {t('label_humidity', lang)}: {data.get('humidity', 'N/A')}%\n"
        text += f"💨 {t('label_wind', lang)}: {data.get('wind_speed', 'N/A')} km/h\n"
        if data.get("description"):
            text += f"📝 {data['description']}\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Weather error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_weather_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/football.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_football import omega_football, MAJOR_LEAGUES
from config import t

logger = logging.getLogger(__name__)
router = Router(name="football")


@router.message(Command("football"))
async def cmd_football(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    if not args:
        buttons = []
        for code, info in list(MAJOR_LEAGUES.items())[:8]:
            name = info.get("name_ar") if lang == "ar" else info.get("name", code)
            buttons.append(InlineKeyboardButton(text=name, callback_data=f"fb:standings:{code}"))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=t("fb_live_btn", lang), callback_data="fb:live")])
        await message.answer(t("fb_choose_league", lang), parse_mode="Markdown", reply_markup=keyboard)
        return

    league = args[0].upper()
    await message.answer(t("fetching", lang))
    try:
        data = await omega_football.get_standings(league)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        lname = data.get("league_name_ar") if lang == "ar" else data.get("league_name", league)
        text = f"⚽ **{lname}**\n\n"
        for entry in data.get("standings", [])[:10]:
            text += f"{entry['position']}. {entry['team']} — {entry['points']} pts\n"
        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Football error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data.startswith("fb:"))
async def handle_football_cb(callback: CallbackQuery, lang: str = "en") -> None:
    parts = callback.data.split(":")
    action = parts[1]
    await callback.answer()

    if action == "live":
        data = await omega_football.get_live_scores()
        if not data.get("matches"):
            await callback.message.answer(t("fb_no_live", lang))
            return
        text = t("fb_live_title", lang) + "\n\n"
        for m in data["matches"][:10]:
            text += f"  {m['home']} {m.get('score_home', '?')} - {m.get('score_away', '?')} {m['away']} ({m.get('clock', '')})\n"
        await callback.message.answer(text, parse_mode="Markdown")

    elif action == "standings" and len(parts) >= 3:
        league = parts[2]
        data = await omega_football.get_standings(league)
        if data.get("error"):
            await callback.message.answer(t("error", lang))
            return
        text = f"⚽ **{data.get('league_name_ar', league)}**\n\n"
        for entry in data.get("standings", [])[:10]:
            text += f"{entry['position']}. {entry['team']} — {entry['points']} pts\n"
        await callback.message.answer(text, parse_mode="Markdown")


def register_football_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/movies.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_movies import omega_movies
from config import t

logger = logging.getLogger(__name__)
router = Router(name="movies")


@router.message(Command("movie"))
async def cmd_movie(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/movie", "").strip() if message.text else ""
    if not query:
        data = await omega_movies.get_trending()
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        text = t("trending_title", lang) + "\n\n"
        for i, item in enumerate(data["results"][:10], 1):
            stars = "⭐" * min(int(item.get("vote_average", 0) / 2), 5)
            text += f"{i}. **{item['title']}** {stars}\n"
            text += f"   📅 {item.get('release_date', 'N/A')} | 🎭 {item.get('media_type', '')}\n\n"
        text += t("search_hint", lang)
        await message.answer(text, parse_mode="Markdown")
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_movies.search(query)
        if data.get("error") or not data.get("results"):
            await message.answer(t("error", lang))
            return

        for item in data["results"][:3]:
            text = f"🎬 **{item['title']}**\n"
            text += f"{t('label_rating', lang)}: {item.get('vote_average', 'N/A')}/10\n"
            text += f"📅 {item.get('release_date', 'N/A')}\n"
            text += f"📝 {item.get('overview', '')[:200]}\n"

            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_details", lang), callback_data=f"mv:detail:{item['id']}:{item.get('media_type', 'movie')}"),
                 InlineKeyboardButton(text=t("btn_favorite", lang), callback_data=f"mv:watch:{item['id']}:{item.get('media_type', 'movie')}")],
            ])
            await message.answer(text, parse_mode="Markdown", reply_markup=buttons)
    except Exception as exc:
        logger.error(f"Movie error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data.startswith("mv:"))
async def handle_movie_cb(callback: CallbackQuery, lang: str = "en") -> None:
    parts = callback.data.split(":")
    action = parts[1]
    await callback.answer()

    if action == "detail" and len(parts) >= 4:
        tmdb_id = int(parts[2])
        media_type = parts[3]
        data = await omega_movies.get_details(tmdb_id, media_type)
        if data.get("error"):
            await callback.message.answer(t("error", lang))
            return
        text = f"🎬 **{data['title']}**\n"
        if data.get("tagline"):
            text += f"_\"{data['tagline']}\"_\n"
        text += f"\n⭐ TMDB: {data.get('vote_average', 'N/A')}/10"
        if data.get("imdb_rating") and data["imdb_rating"] != "N/A":
            text += f" | IMDb: {data['imdb_rating']}"
        if data.get("rotten_tomatoes") and data["rotten_tomatoes"] != "N/A":
            text += f" | 🍅 {data['rotten_tomatoes']}"
        text += f"\n📅 {data.get('release_date', 'N/A')}"
        if data.get("runtime"):
            text += f" | ⏱ {data['runtime']} min"
        text += f"\n🎭 {', '.join(data.get('genres', []))}\n"
        if data.get("director"):
            text += f"{t('label_director', lang)}: {data['director']}\n"
        if data.get("cast"):
            cast_names = [c['name'] for c in data['cast'][:5]]
            text += f"{t('label_cast', lang)}: {', '.join(cast_names)}\n"
        text += f"\n📝 {data.get('overview', '')[:300]}"
        if data.get("trailer_url"):
            text += f"\n\n🎥 [Trailer]({data['trailer_url']})"
        await callback.message.answer(text, parse_mode="Markdown")


def register_movies_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/cv_generator.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import t
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)
router = Router(name="cv")


class CVStates(StatesGroup):
    full_name = State()
    email = State()
    phone = State()
    summary = State()
    experience = State()
    education = State()
    skills = State()
    languages = State()
    template = State()


@router.message(Command("cv"))
async def cmd_cv(message: Message, state: FSMContext, lang: str = "en") -> None:
    await state.update_data(lang=lang)
    await state.set_state(CVStates.full_name)
    await message.answer(
        t("cv_intro", lang) + "\n\n" + t("cv_step", lang, n="1", q=t("cv_q_name", lang)),
        parse_mode="Markdown"
    )


@router.message(CVStates.full_name)
async def process_name(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(full_name=message.text)
    await state.set_state(CVStates.email)
    await message.answer(t("cv_step", lang, n="2", q=t("cv_q_email", lang)), parse_mode="Markdown")


@router.message(CVStates.email)
async def process_email(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(email=message.text)
    await state.set_state(CVStates.phone)
    await message.answer(t("cv_step", lang, n="3", q=t("cv_q_phone", lang)), parse_mode="Markdown")


@router.message(CVStates.phone)
async def process_phone(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(phone=message.text)
    await state.set_state(CVStates.summary)
    await message.answer(t("cv_step", lang, n="4", q=t("cv_q_summary", lang)), parse_mode="Markdown")


@router.message(CVStates.summary)
async def process_summary(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(summary=message.text)
    await state.set_state(CVStates.experience)
    await message.answer(t("cv_step", lang, n="5", q=t("cv_q_experience", lang)), parse_mode="Markdown")


@router.message(CVStates.experience)
async def process_experience(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(experience=message.text)
    await state.set_state(CVStates.education)
    await message.answer(t("cv_step", lang, n="6", q=t("cv_q_education", lang)), parse_mode="Markdown")


@router.message(CVStates.education)
async def process_education(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(education=message.text)
    await state.set_state(CVStates.skills)
    await message.answer(t("cv_step", lang, n="7", q=t("cv_q_skills", lang)), parse_mode="Markdown")


@router.message(CVStates.skills)
async def process_skills(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(skills=message.text)
    await state.set_state(CVStates.languages)
    await message.answer(t("cv_step", lang, n="8", q=t("cv_q_languages", lang)), parse_mode="Markdown")


@router.message(CVStates.languages)
async def process_languages(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    await state.update_data(languages=message.text)
    await state.set_state(CVStates.template)
    await message.answer(
        t("cv_step", lang, n="9", q=t("cv_q_template", lang)) + "\n1. Modern\n2. Classic\n3. Creative\n4. Minimal\n5. Professional",
        parse_mode="Markdown"
    )


@router.message(CVStates.template)
async def process_template(message: Message, state: FSMContext, lang: str = "en") -> None:
    state_data = await state.get_data()
    lang = state_data.get("lang", lang)
    templates = {"1": "modern", "2": "classic", "3": "creative", "4": "minimal", "5": "professional"}
    template = templates.get(message.text.strip(), "modern")
    state_data["template"] = template
    data = state_data
    await state.clear()

    await message.answer(t("cv_generating", lang))

    try:
        from services.omega_query_engine import query_engine

        prompt = f"""Improve this CV professionally:
Name: {data.get('full_name', '')}
Summary: {data.get('summary', '')}
Experience: {data.get('experience', '')}
Education: {data.get('education', '')}
Skills: {data.get('skills', '')}
Languages: {data.get('languages', '')}

Return improved bullet points for each section. Be concise and professional."""

        lang_instruction = f"Respond in the same language as the CV data." 
        responses = await query_engine.query_all(prompt, system_prompt=f"You are a professional CV writer. {lang_instruction}")
        improved_text = responses[0]["text"] if responses else data.get("summary", "")

        await message.answer(
            t("cv_done", lang) + f"\n\n"
            f"📄 {template}\n"
            f"👤 {data.get('full_name', '')}\n\n"
            f"{improved_text[:500]}",
            parse_mode="Markdown"
        )

    except Exception as exc:
        logger.error(f"CV generation error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_cv_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/logo_generator.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import t

from services.omega_image import omega_image

logger = logging.getLogger(__name__)
router = Router(name="logo")


@router.message(Command("logo"))
async def cmd_logo(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/logo", "").strip() if message.text else ""
    if not query:
        await message.answer(
            t("logo_intro", lang),
            parse_mode="Markdown"
        )
        return

    await message.answer(t("logo_generating", lang))
    try:
        from services.omega_query_engine import query_engine

        lang_instruction = f"Respond in {lang} language." if lang != "en" else ""
        prompt = f"Create a professional logo concept description for a company called '{query}'. Describe the visual elements, colors, and style. {lang_instruction}"
        responses = await query_engine.query_all(prompt, system_prompt="You are a professional graphic designer.")
        description = responses[0]["text"] if responses else f"Modern logo for {query}"

        urls = await omega_image.search_logos(query)
        text = f"🎨 **{query}**\n\n"
        text += f"📝 {description[:400]}\n\n"
        for i, url in enumerate(urls, 1):
            text += f"{i}. [#{i}]({url})\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Logo error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_logo_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/ai_chat.py"] = r'''
import logging
import re
import time
from typing import Optional
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from services.omega_router import omega_router
from services.omega_query_engine import query_engine
from services.omega_fusion import omega_fusion
from services.omega_judge import omega_judge
from services.omega_memory import omega_memory
from services.rate_limiter import check_user_rate
from config import t
from database.connection import get_session
from database.crud import CRUDManager

# ── Smart routing keywords ──────────────────────────────────────
_GOLD_KW    = {"ذهب", "gold", "فضة", "silver", "بلاتين", "platinum", "معادن", "metals",
               "غرام ذهب", "كيلو ذهب", "سعر ذهب", "gold price"}
_WEATHER_KW = {"طقس", "weather", "درجة حرار", "temperature", "مطر", "rain", "جو", "حرارة",
               "الطقس", "الجو", "حالة الجو", "كيف الطقس", "شو الطقس"}
_CURRENCY_KW= {"عملة", "currency", "دولار", "dollar", "يورو", "euro", "صرف", "exchange",
               "ليرة", "lira", "ريال", "riyal", "درهم", "dirham", "pound", "جنيه",
               "سعر صرف", "exchange rate"}
_FUEL_KW    = {"بنزين", "benzin", "fuel", "محروقات", "وقود", "diesel", "ديزل", "petrol",
               "سعر البنزين", "محروقات", "بنزين 95", "بنزين 98"}
_STOCK_KW   = {"سهم", "اسهم", "stock", "stocks", "بورصة", "nasdaq", "سوق مال", "أسهم"}
_CRYPTO_KW  = {"بيتكوين", "bitcoin", "كريبتو", "crypto", "ethereum", "ايثريوم", "btc", "eth",
               "عملات رقمية", "بيتكوين"}
_NEWS_KW    = {"اخبار", "خبر", "news", "أخبار", "اخر الاخبار", "latest news"}

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

Keep answers short and clear. Use emojis naturally. Be the smartest assistant they've ever used."""


@router.message(Command("ai"))
async def cmd_ai(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/ai", "").strip() if message.text else ""
    if not query:
        await message.answer(t("ai_intro", lang), parse_mode="Markdown")
        return
    await process_ai_query(message, query, lang=lang)


async def _route_to_service(message: Message, query: str, lang: str) -> bool:
    """Try to route natural language query to a specific service. Returns True if handled."""
    try:
        # Gold & metals
        if _has_kw(query, _GOLD_KW):
            from handlers.gold import cmd_gold
            await cmd_gold(message, lang=lang)
            return True

        # Weather — extract city from query
        if _has_kw(query, _WEATHER_KW):
            city = _extract_city(query, default="Beirut")
            from api_clients.omega_weather import omega_weather
            await message.answer(t("fetching", lang))
            data = await omega_weather.get_weather(city, lang)
            if not data.get("error"):
                text = f"🌤 **{data.get('city', city)}**\n\n"
                text += f"🌡 {t('label_temp', lang)}: {data['temperature']}°C\n"
                text += f"🤔 {t('label_feels', lang)}: {data.get('feels_like', 'N/A')}°C\n"
                text += f"💧 {t('label_humidity', lang)}: {data.get('humidity', 'N/A')}%\n"
                text += f"💨 {t('label_wind', lang)}: {data.get('wind_speed', 'N/A')} km/h\n"
                if data.get("description"):
                    text += f"📝 {data['description']}\n"
                await message.answer(text, parse_mode="Markdown")
            else:
                await message.answer(t("error", lang))
            return True

        # Currency & exchange rates
        if _has_kw(query, _CURRENCY_KW):
            from handlers.currency import cmd_currency
            await cmd_currency(message, lang=lang)
            return True

        # Fuel prices
        if _has_kw(query, _FUEL_KW):
            from handlers.fuel import cmd_fuel
            await cmd_fuel(message, lang=lang)
            return True

        # Stocks — extract ticker from natural language
        if _has_kw(query, _STOCK_KW):
            symbol = _extract_stock(query)
            if symbol:
                from api_clients.omega_stocks import omega_stocks
                await message.answer(t("fetching", lang))
                data = await omega_stocks.get_quote(symbol)
                if not data.get("error"):
                    change_emoji = "📈" if (data.get("change", 0) or 0) >= 0 else "📉"
                    text = f"📊 **{data.get('name', symbol)} ({data.get('symbol', symbol)})**\n\n"
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

        # Crypto — extract coin from natural language
        if _has_kw(query, _CRYPTO_KW):
            coin = _extract_crypto(query)
            from api_clients.omega_crypto import omega_crypto
            await message.answer(t("fetching", lang))
            data = await omega_crypto.get_price(coin)
            if not data.get("error"):
                emoji = "📈" if (data.get("change_24h") or 0) >= 0 else "📉"
                text = f"₿ **{data.get('name', coin)} ({data.get('symbol', coin).upper()})**\n\n"
                text += f"{t('label_price', lang)}: ${data.get('price', 0):,.2f}\n"
                text += f"{emoji} 24h: {data.get('change_24h', 0):+.2f}%\n"
                if data.get("market_cap"):
                    text += f"{t('label_mcap', lang)}: ${data['market_cap']:,.0f}\n"
                await message.answer(text, parse_mode="Markdown")
            else:
                await message.answer(t("error", lang))
            return True

        # News
        if _has_kw(query, _NEWS_KW):
            from handlers.news import cmd_news
            await cmd_news(message, lang=lang)
            return True

    except Exception as exc:
        logger.debug(f"Service routing failed: {exc}")

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
        enhanced_prompt = SYSTEM_PROMPT + f"\n\n[SYSTEM: User is writing in {lang_name}. You MUST respond in {lang_name}. Do not use any other language.]"
        responses = await query_engine.query_all(query, system_prompt=enhanced_prompt, analysis=analysis)

        if not responses:
            await message.answer(t("error", lang))
            return

        fused = omega_fusion.fuse(responses, analysis)
        judged = omega_judge.evaluate(fused, query, analysis)

        elapsed = int((time.monotonic() - start_time) * 1000)
        text = judged["text"]

        if len(text) > 4000:
            text = text[:4000] + "..."

        await message.answer(text, parse_mode="Markdown")

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


def register_ai_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/stocks.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_stocks import omega_stocks
from config import t

logger = logging.getLogger(__name__)
router = Router(name="stocks")


@router.message(Command("stock"))
async def cmd_stock(message: Message, lang: str = "en") -> None:
    symbol = message.text.replace("/stock", "").strip().upper() if message.text else ""
    if not symbol:
        await message.answer(t("stock_send_symbol", lang))
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_stocks.get_quote(symbol)
        if data.get("error"):
            await message.answer(t("not_found", lang))
            return

        change_emoji = "📈" if (data.get("change", 0) or 0) >= 0 else "📉"
        text = f"📊 **{data.get('name', symbol)} ({data['symbol']})**\n\n"
        text += f"{t('label_price', lang)}: ${data.get('price', 0):,.2f}\n"
        text += f"{change_emoji} {t('label_change', lang)}: {data.get('change', 0):+,.2f} ({data.get('change_percent', 0):+.2f}%)\n"
        text += f"{t('label_volume', lang)}: {data.get('volume', 0):,}\n"
        if data.get("market_cap"):
            text += f"{t('label_mcap', lang)}: ${data['market_cap']:,.0f}\n"
        if data.get("pe_ratio"):
            text += f"📐 P/E: {data['pe_ratio']:.2f}\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Stock error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_stocks_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/crypto.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_crypto import omega_crypto
from config import t

logger = logging.getLogger(__name__)
router = Router(name="crypto")


@router.message(Command("crypto"))
async def cmd_crypto(message: Message, lang: str = "en") -> None:
    coin = message.text.replace("/crypto", "").strip().lower() if message.text else ""
    if not coin:
        data = await omega_crypto.get_top_coins(10)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        text = t("crypto_top_title", lang) + "\n\n"
        for c in data["coins"]:
            emoji = "📈" if (c.get("change_24h") or 0) >= 0 else "📉"
            text += f"{c['rank']}. **{c['symbol']}** — ${c['price']:,.2f} {emoji} {c.get('change_24h', 0):+.1f}%\n"
        text += "\n" + t("crypto_detail_hint", lang)
        await message.answer(text, parse_mode="Markdown")
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_crypto.get_price(coin)
        if data.get("error"):
            await message.answer(t("not_found", lang))
            return
        emoji = "📈" if (data.get("change_24h") or 0) >= 0 else "📉"
        text = f"₿ **{data['name']} ({data['symbol']})**\n\n"
        text += f"{t('label_price', lang)}: ${data['price']:,.2f}\n"
        text += f"{emoji} 24h: {data.get('change_24h', 0):+.2f}%\n"
        if data.get("change_7d"):
            text += f"📊 7d: {data['change_7d']:+.2f}%\n"
        text += f"{t('label_rank', lang)}: #{data.get('rank', 'N/A')}\n"
        text += f"{t('label_mcap', lang)}: ${data.get('market_cap', 0):,.0f}\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Crypto error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_crypto_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/news.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_news import omega_news
from config import t

logger = logging.getLogger(__name__)
router = Router(name="news")


@router.message(Command("news"))
async def cmd_news(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/news", "").strip() if message.text else ""

    await message.answer(t("fetching", lang))
    try:
        if query:
            data = await omega_news.search_news(query)
        else:
            data = await omega_news.get_headlines()

        if data.get("error") or not data.get("articles"):
            await message.answer(t("error", lang))
            return

        text = t("news_headline", lang) + "\n\n"
        for i, article in enumerate(data["articles"][:8], 1):
            text += f"{i}. **{article['title'][:80]}**\n"
            if article.get("source"):
                text += f"   📍 {article['source']}\n"
            if article.get("url"):
                read_label = t("read_more", lang)
                text += f"   🔗 [{read_label}]({article['url']})\n"
            text += "\n"

        await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as exc:
        logger.error(f"News error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_news_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/flights.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_flights import omega_flights
from config import t

logger = logging.getLogger(__name__)
router = Router(name="flights")


@router.message(Command("flight"))
async def cmd_flight(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/flight", "").strip().upper() if message.text else ""
    if not query:
        await message.answer(t("flight_send", lang))
        return

    await message.answer(t("fetching", lang))
    try:
        if len(query) == 4 and query.isalpha():
            data = await omega_flights.get_flights_by_airport(query)
            if data.get("error"):
                await message.answer(t("not_found", lang))
                return
            text = f"✈️ **{query}**\n\n"
            text += f"{t('label_departures', lang)} ({len(data['departures'])}):\n"
            for f in data["departures"][:5]:
                text += f"  {f['callsign']} → {f['arrival']}\n"
            text += f"\n{t('label_arrivals', lang)} ({len(data['arrivals'])}):\n"
            for f in data["arrivals"][:5]:
                text += f"  {f['callsign']} ← {f['departure']}\n"
        else:
            data = await omega_flights.track_flight(query)
            if data.get("error"):
                await message.answer(t("not_found", lang))
                return
            text = f"✈️ **{data['callsign']}**\n\n"
            text += f"🌍 {data.get('origin_country', 'N/A')}\n"
            text += f"📍 {data.get('latitude', 0):.2f}, {data.get('longitude', 0):.2f}\n"
            text += f"{t('label_altitude', lang)}: {data.get('altitude', 0):,.0f}m\n"
            text += f"{t('label_speed', lang)}: {data.get('velocity', 0):,.0f}m/s\n"
            text += f"{t('label_heading', lang)}: {data.get('heading', 0):.0f}°\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Flight error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_flights_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/settings.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import t

from config import LANGUAGES
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)
router = Router(name="settings")


@router.message(Command("settings"))
async def cmd_settings(message: Message, lang: str = "en") -> None:
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_language", lang), callback_data="set:lang"),
         InlineKeyboardButton(text=t("btn_currency_pref", lang), callback_data="set:currency")],
        [InlineKeyboardButton(text=t("btn_city", lang), callback_data="set:city"),
         InlineKeyboardButton(text=t("btn_length", lang), callback_data="set:length")],
    ])
    await message.answer(t("settings_title", lang), parse_mode="Markdown", reply_markup=buttons)


@router.callback_query(lambda c: c.data.startswith("set:"))
async def handle_settings(callback: CallbackQuery, lang: str = "en") -> None:
    action = callback.data.split(":")[1]
    await callback.answer()

    if action == "lang":
        buttons = []
        popular_langs = ["ar", "en", "fr", "es", "tr", "ru", "fa", "de", "hi", "zh-CN"]
        for lang_code in popular_langs:
            info = LANGUAGES.get(lang_code, {})
            buttons.append(InlineKeyboardButton(
                text=f"{info.get('flag', '')} {info.get('name', lang_code)}",
                callback_data=f"lang:{lang_code}"
            ))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
        await callback.message.answer(t("choose_lang", lang), reply_markup=keyboard)

    elif action == "currency":
        await callback.message.answer(t("btn_currency_pref", lang) + ": USD, EUR, SAR")

    elif action == "city":
        await callback.message.answer(t("btn_city", lang) + "?")


@router.callback_query(lambda c: c.data.startswith("lang:"))
async def handle_lang_change(callback: CallbackQuery, lang: str = "en") -> None:
    lang = callback.data.split(":")[1]
    await callback.answer(f"✅ {lang}")
    try:
        async with get_session() as session:
            await CRUDManager.update_user(session, callback.from_user.id, language_code=lang)
        lang_name = LANGUAGES.get(lang, {}).get("name", lang)
        await callback.message.answer(f"✅ {lang_name}")
    except Exception as exc:
        logger.error(f"Settings error: {exc}", exc_info=True)


def register_settings_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/stats.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import t

from config import settings, RENDER_PLAN, IS_FREE, AI_MODELS
from database.connection import get_session
from database.crud import CRUDManager
from services.circuit_breaker import circuit_breaker
from services.rate_limiter import quota

logger = logging.getLogger(__name__)
router = Router(name="stats")


@router.message(Command("stats"))
async def cmd_stats(message: Message, lang: str = "en") -> None:
    if message.from_user.id not in settings.admin_id_list:
        await message.answer(t("admin_only", lang))
        return

    try:
        async with get_session() as session:
            stats = await CRUDManager.get_stats(session)

        circuits = circuit_breaker.get_all_statuses()
        open_circuits = sum(1 for c in circuits.values() if c["state"] == "open")

        import psutil
        ram = psutil.virtual_memory()

        text = t("stats_title", lang) + "\n\n"
        text += f"{t('stats_system', lang)}:\n"
        text += f"  {t('stats_plan', lang)}: {RENDER_PLAN.upper()}\n"
        text += f"  {t('stats_models', lang)}: {len(AI_MODELS)}\n"
        text += f"  RAM: {ram.percent}%\n"
        text += f"  DB: {'SQLite' if IS_FREE else 'PostgreSQL'}\n\n"
        text += f"{t('stats_users_title', lang)}:\n"
        text += f"  {t('stats_total', lang)}: {stats['total_users']}\n"
        text += f"  {t('stats_active', lang)}: {stats['active_24h']}\n\n"
        text += f"{t('stats_perf', lang)}:\n"
        text += f"  {t('stats_searches', lang)}: {stats['total_searches']}\n"
        text += f"  {t('stats_fusions', lang)}: {stats['total_fusions']}\n"
        text += f"  {t('stats_avg_time', lang)}: {stats['avg_fusion_time_ms']}ms\n"
        text += f"  {t('stats_circuits', lang)}: {open_circuits}/{len(circuits)}\n"

        # Quota status
        text += f"\n{t('stats_quotas', lang)}:\n"
        for qs in quota.get_all_statuses():
            icon = "✅" if qs.get("remaining", 0) > 0 else "🔴"
            text += f"  {icon} {qs['name']}: {qs.get('remaining',0)}/{qs.get('limit',0)} ({qs['period']})\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Stats error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_stats_handlers(dp) -> None:
    dp.include_router(router)
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 6 — MIDDLEWARE + WORKERS + MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES["middlewares/__init__.py"] = """
from middlewares.logging_mw import LoggingMiddleware
from middlewares.rate_limit_mw import RateLimitMiddleware
from middlewares.user_tracker_mw import UserTrackerMiddleware
from middlewares.security_mw import SecurityMiddleware

__all__ = ["LoggingMiddleware", "RateLimitMiddleware", "UserTrackerMiddleware", "SecurityMiddleware"]
"""

FILES["middlewares/logging_mw.py"] = r'''
import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log all incoming messages and callbacks with timing."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        start = time.monotonic()
        user_id = None
        event_type = type(event).__name__

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            text_preview = (event.text or "")[:50]
            logger.info(f"[MSG] user={user_id} text='{text_preview}'")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            logger.info(f"[CB] user={user_id} data='{event.data}'")

        try:
            result = await handler(event, data)
            elapsed = int((time.monotonic() - start) * 1000)
            logger.info(f"[{event_type}] user={user_id} processed in {elapsed}ms")
            return result
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.error(f"[{event_type}] user={user_id} FAILED in {elapsed}ms: {exc}", exc_info=True)
            raise
'''

FILES["middlewares/rate_limit_mw.py"] = r'''
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from services.rate_limiter import check_user_rate

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Rate limit incoming messages per user."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            if not check_user_rate(user_id, "message"):
                logger.warning(f"Rate limited user {user_id}")
                await event.answer("⏳ Too many messages. Please wait a moment.")
                return None

        return await handler(event, data)
'''

FILES["middlewares/user_tracker_mw.py"] = r'''
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from config import LANGUAGES
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)

SUPPORTED_LANG_CODES = set(LANGUAGES.keys())


def _resolve_lang(telegram_lang: str) -> str:
    """Map Telegram device language to our supported language."""
    if not telegram_lang:
        return "en"
    code = telegram_lang.lower().strip()
    if code in SUPPORTED_LANG_CODES:
        return code
    short = code.split("-")[0].split("_")[0]
    if short in SUPPORTED_LANG_CODES:
        return short
    if short == "zh":
        return "zh-CN"
    return "en"


class UserTrackerMiddleware(BaseMiddleware):
    """Auto-detect device language + track user + inject lang into handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_obj = None
        if isinstance(event, Message) and event.from_user:
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_obj = event.from_user

        if user_obj:
            device_lang = _resolve_lang(user_obj.language_code)
            data["lang"] = device_lang

            try:
                async with get_session() as session:
                    user = await CRUDManager.get_or_create_user(
                        session,
                        telegram_id=user_obj.id,
                        username=user_obj.username,
                        first_name=user_obj.first_name,
                        last_name=user_obj.last_name,
                        language_code=device_lang,
                    )
                    if user.language_code != device_lang:
                        user.language_code = device_lang
                        await session.flush()
                    data["db_user"] = user
                    data["lang"] = user.language_code
            except Exception as exc:
                logger.debug(f"User tracker error: {exc}")
                data["lang"] = device_lang

            # Auto-detect Arabic text: if message contains Arabic chars, override lang to "ar"
            import re
            msg_text = ""
            if isinstance(event, Message) and event.text:
                msg_text = event.text
            elif isinstance(event, Message) and event.caption:
                msg_text = event.caption
            if msg_text and re.search(r'[\u0600-\u06FF]', msg_text):
                data["lang"] = "ar"
        else:
            data["lang"] = "en"

        return await handler(event, data)
'''

FILES["middlewares/security_mw.py"] = r'''
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import settings
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseMiddleware):
    """Security checks: banned users, admin commands."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            try:
                async with get_session() as session:
                    user = await CRUDManager.get_user_by_telegram_id(session, event.from_user.id)
                    if user and user.is_banned:
                        logger.warning(f"Banned user {event.from_user.id} attempted access")
                        await event.answer("⛔")
                        return None
            except Exception as exc:
                logger.debug(f"Security check error: {exc}")

        return await handler(event, data)
'''

FILES["workers/notification_worker.py"] = r'''
import logging
import asyncio
from typing import Optional

from config import IS_PAID

logger = logging.getLogger(__name__)


class NotificationWorker:
    """Background worker for proactive notifications (paid plan only)."""

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self, bot) -> None:
        """Start the notification worker."""
        if not IS_PAID:
            logger.info("Notification worker skipped (free plan)")
            return

        self._running = True
        self._task = asyncio.create_task(self._run(bot))
        logger.info("Notification worker started")

    async def stop(self) -> None:
        """Stop the notification worker."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Notification worker stopped")

    async def _run(self, bot) -> None:
        """Main worker loop."""
        while self._running:
            try:
                await self._check_price_alerts(bot)
                await self._check_match_notifications(bot)
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Notification worker error: {exc}", exc_info=True)
                await asyncio.sleep(30)

    async def _check_price_alerts(self, bot) -> None:
        """Check crypto/stock price alerts."""
        try:
            from database.connection import get_session
            from sqlalchemy import select
            from database.models import TrackedCoin
            from api_clients.omega_crypto import omega_crypto

            async with get_session() as session:
                result = await session.execute(select(TrackedCoin))
                tracked = result.scalars().all()

                for coin in tracked:
                    if coin.alert_price_above or coin.alert_price_below:
                        data = await omega_crypto.get_price(coin.coin_id)
                        if data.get("error"):
                            continue
                        price = data.get("price", 0)
                        if coin.alert_price_above and price >= coin.alert_price_above:
                            await bot.send_message(
                                coin.user_id,
                                f"🚨 {coin.coin_symbol} reached ${price:,.2f} (above ${coin.alert_price_above:,.2f})"
                            )
                        if coin.alert_price_below and price <= coin.alert_price_below:
                            await bot.send_message(
                                coin.user_id,
                                f"🚨 {coin.coin_symbol} dropped to ${price:,.2f} (below ${coin.alert_price_below:,.2f})"
                            )
        except Exception as exc:
            logger.debug(f"Price alert check error: {exc}")

    async def _check_match_notifications(self, bot) -> None:
        """Check football match notifications."""
        pass


notification_worker = NotificationWorker()
'''

FILES["main.py"] = r'''
import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import settings, RENDER_PLAN, IS_FREE, AI_MODELS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher(storage=MemoryStorage())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info(f"🚀 Omega Bot starting — Plan: {RENDER_PLAN}, Models: {len(AI_MODELS)}")

    from database.connection import init_db
    await init_db()
    logger.info("✅ Database initialized")

    from handlers import register_all_handlers
    register_all_handlers(dp)
    logger.info("✅ Handlers registered")

    from middlewares import LoggingMiddleware, RateLimitMiddleware, UserTrackerMiddleware, SecurityMiddleware
    # Message middlewares
    dp.message.middleware(SecurityMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(UserTrackerMiddleware())
    dp.message.middleware(LoggingMiddleware())
    # Callback middlewares (so buttons get lang too)
    dp.callback_query.middleware(UserTrackerMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    logger.info("✅ Middlewares registered")

    from handlers.ai_chat import process_ai_query
    @dp.message(lambda m: m.text is not None and not m.text.startswith("/"))
    async def catch_all_messages(message, lang: str = "en"):
        await process_ai_query(message, message.text, lang=lang)

    # Resolve webhook URL: prefer explicit setting, fallback to Render's auto URL
    _webhook_url = settings.webhook_url or (
        os.environ.get("RENDER_EXTERNAL_URL", "") + "/webhook"
        if os.environ.get("RENDER_EXTERNAL_URL") else ""
    )
    if _webhook_url:
        await bot.set_webhook(
            url=_webhook_url,
            drop_pending_updates=True,
        )
        logger.info(f"✅ Webhook set: {_webhook_url}")

    if IS_FREE:
        asyncio.create_task(_self_ping())
        logger.info("✅ Self-ping task started (free plan)")

    from workers.notification_worker import notification_worker
    await notification_worker.start(bot)

    from services.cache_service import AdminAlert
    AdminAlert.set_bot(bot)

    logger.info("🟢 Omega Bot is LIVE!")

    yield

    logger.info("Shutting down...")
    from workers.notification_worker import notification_worker
    await notification_worker.stop()

    from services.omega_query_engine import query_engine
    await query_engine.close()

    from services.cache_service import cache
    await cache.close()

    from database.connection import close_db
    await close_db()

    await bot.session.close()
    logger.info("🔴 Omega Bot stopped")


app = FastAPI(title="Omega Bot", lifespan=lifespan)


@app.post("/webhook")
async def webhook_handler(request: Request) -> Response:
    """Handle incoming Telegram webhook updates."""
    try:
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot=bot, update=update)
        return Response(status_code=200)
    except Exception as exc:
        logger.error(f"Webhook error: {exc}", exc_info=True)
        return Response(status_code=200)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import psutil
    ram = psutil.virtual_memory()
    return {
        "status": "healthy",
        "plan": RENDER_PLAN,
        "models": len(AI_MODELS),
        "ram_percent": ram.percent,
        "db": "sqlite" if IS_FREE else "postgresql",
    }


@app.get("/")
async def root():
    return {"message": "Omega Bot is running!", "plan": RENDER_PLAN}


async def _self_ping():
    """Ping the external URL every 4 minutes to prevent Render free tier from sleeping."""
    import httpx
    await asyncio.sleep(30)  # wait for server to fully start first
    while True:
        try:
            # Use external URL so Render counts it as real traffic
            external_url = os.environ.get("RENDER_EXTERNAL_URL", "")
            if external_url:
                ping_url = f"{external_url}/health"
            else:
                ping_url = f"http://127.0.0.1:{settings.port}/health"
            async with httpx.AsyncClient(timeout=10) as client:
                await client.get(ping_url)
                logger.debug(f"Self-ping OK: {ping_url}")
        except Exception:
            pass
        await asyncio.sleep(240)  # every 4 minutes
'''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SETUP RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os

def setup():
    """Create all project files from the FILES dictionary."""
    print("=" * 60)
    print("  OMEGA BOT — Project Setup")
    print("=" * 60)
    total = len(FILES)
    created = 0
    for path, content in FILES.items():
        try:
            d = os.path.dirname(path)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.strip() + '\n')
            created += 1
            print(f"  ✅ {path}")
        except Exception as e:
            print(f"  ❌ {path}: {e}")
    print("=" * 60)
    print(f"  Created: {created}/{total} files")
    print(f"  Plan: Check RENDER_PLAN in .env")
    print("=" * 60)
    print("  Next steps:")
    print("  1. Copy .env.example to .env")
    print("  2. Fill in your API keys")
    print("  3. pip install -r requirements.txt")
    print("  4. uvicorn main:app --host 0.0.0.0 --port 10000")
    print("=" * 60)
    print("  🚀 Setup complete!")

if __name__ == "__main__":
    setup()
