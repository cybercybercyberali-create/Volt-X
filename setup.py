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
feedparser==6.0.11
diskcache==5.6.3
redis[hiredis]==5.0.7
yfinance==0.2.40
apscheduler==3.10.4
tenacity==8.4.1
cachetools==5.3.3
orjson==3.10.5
psutil==5.9.8
yt-dlp>=2024.1.1
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
API_FOOTBALL_KEY=your_rapidapi_key_for_api-football
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
    api_football_key: str = Field(default="", alias="API_FOOTBALL_KEY")
    metals_api_key: str = Field(default="", alias="METALS_API_KEY")
    goldapi_key: str = Field(default="", alias="GOLDAPI_KEY")
    exchange_rate_key: str = Field(default="", alias="EXCHANGE_RATE_KEY")
    scraper_api_key: str = Field(default="", alias="SCRAPER_API_KEY")

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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore", "populate_by_name": True}


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
    "llm7": None,              # llm7.io — free, no key needed
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
    "weather_current": 600,
    "weather_forecast": 3600,
    "football_static": 3600,
    "football_live": 60,
    "stocks": 300,
    "crypto": 120,
    "news": 1800,
    "movies": 86400,
    "fuel": 21600,
    "fuel_lebanon": 86400,
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
        "ar": "🪙 *سعر الذهب*\n\n💰 الأونصة: ${price}",
        "en": "🪙 *Gold Price*\n\n💰 Ounce: ${price}",
        "fr": "🪙 *Prix de l'or*\n\n💰 Once: ${price}",
        "es": "🪙 *Precio del oro*\n\n💰 Onza: ${price}",
        "tr": "🪙 *Altın Fiyatı*\n\n💰 Ons: ${price}",
        "ru": "🪙 *Цена золота*\n\n💰 Унция: ${price}",
        "fa": "🪙 *قیمت طلا*\n\n💰 اونس: ${price}",
        "de": "🪙 *Goldpreis*\n\n💰 Unze: ${price}",
        "hi": "🪙 *सोने की कीमत*\n\n💰 औंस: ${price}",
        "zh-CN": "🪙 *黄金价格*\n\n💰 盎司: ${price}",
    },
    "gold_karats_btn": {
        "ar": "💍 أسعار العيارات", "en": "💍 Karat Prices", "fr": "💍 Prix des carats",
        "es": "💍 Precios por quilate", "tr": "💍 Ayar Fiyatları", "ru": "💍 Цены по каратам",
        "fa": "💍 قیمت عیارها", "de": "💍 Karatpreise", "hi": "💍 कैरट मूल्य", "zh-CN": "💍 克拉价格",
    },
    "gold_karats_title": {
        "ar": "💍 *أسعار عيارات الذهب (لكل غرام)*",
        "en": "💍 *Gold Karat Prices (per gram)*",
        "fr": "💍 *Prix des carats d'or (par gramme)*",
        "es": "💍 *Precios por quilate de oro (por gramo)*",
        "tr": "💍 *Altın Ayar Fiyatları (gram başına)*",
        "ru": "💍 *Цены по каратам золота (за грамм)*",
        "fa": "💍 *قیمت عیارهای طلا (هر گرم)*",
        "de": "💍 *Goldpreise nach Karat (pro Gramm)*",
        "hi": "💍 *सोने के कैरट मूल्य (प्रति ग्राम)*",
        "zh-CN": "💍 *黄金克拉价格（每克）*",
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
        "ar": "💱 *{base} → {target}*\n\n💰 السعر: {rate}",
        "en": "💱 *{base} → {target}*\n\n💰 Rate: {rate}",
        "fr": "💱 *{base} → {target}*\n\n💰 Taux: {rate}",
        "es": "💱 *{base} → {target}*\n\n💰 Tasa: {rate}",
        "tr": "💱 *{base} → {target}*\n\n💰 Kur: {rate}",
        "ru": "💱 *{base} → {target}*\n\n💰 Курс: {rate}",
    },
    "currency_parallel": {
        "ar": "⚠️ *السعر الموازي:* {rate}", "en": "⚠️ *Parallel rate:* {rate}",
        "fr": "⚠️ *Taux parallèle:* {rate}", "es": "⚠️ *Tasa paralela:* {rate}",
        "tr": "⚠️ *Paralel kur:* {rate}", "ru": "⚠️ *Параллельный курс:* {rate}",
    },
    # ━━━ Sub-keys: Weather ━━━
    "weather_result": {
        "ar": "🌤 *الطقس في {city}*\n\n🌡 الحرارة: {temp}°C\n🤔 الإحساس: {feels}°C\n💧 الرطوبة: {humidity}%\n💨 الرياح: {wind} km/h\n📝 {desc}",
        "en": "🌤 *Weather in {city}*\n\n🌡 Temp: {temp}°C\n🤔 Feels: {feels}°C\n💧 Humidity: {humidity}%\n💨 Wind: {wind} km/h\n📝 {desc}",
        "fr": "🌤 *Météo à {city}*\n\n🌡 Temp: {temp}°C\n💧 Humidité: {humidity}%\n💨 Vent: {wind} km/h\n📝 {desc}",
        "es": "🌤 *Clima en {city}*\n\n🌡 Temp: {temp}°C\n💧 Humedad: {humidity}%\n💨 Viento: {wind} km/h\n📝 {desc}",
        "tr": "🌤 *{city} Hava Durumu*\n\n🌡 Sıcaklık: {temp}°C\n💧 Nem: {humidity}%\n💨 Rüzgar: {wind} km/h\n📝 {desc}",
        "ru": "🌤 *Погода в {city}*\n\n🌡 Темп: {temp}°C\n💧 Влажность: {humidity}%\n💨 Ветер: {wind} км/ч\n📝 {desc}",
    },
    # ━━━ Sub-keys: Football ━━━
    "fb_choose_league": {
        "ar": "⚽ *اختر الدوري:*", "en": "⚽ *Choose league:*",
        "fr": "⚽ *Choisir la ligue:*", "es": "⚽ *Elige la liga:*",
        "tr": "⚽ *Lig seçin:*", "ru": "⚽ *Выберите лигу:*",
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
        "ar": "📊 *{name} ({symbol})*\n\n💰 السعر: ${price}\n{emoji} التغير: {change} ({pct}%)\n📊 الحجم: {volume}",
        "en": "📊 *{name} ({symbol})*\n\n💰 Price: ${price}\n{emoji} Change: {change} ({pct}%)\n📊 Volume: {volume}",
    },
    # ━━━ Sub-keys: Crypto ━━━
    "crypto_result": {
        "ar": "₿ *{name} ({symbol})*\n\n💰 السعر: ${price}\n{emoji} 24h: {change}%\n🏆 الترتيب: #{rank}\n📊 القيمة السوقية: ${mcap}",
        "en": "₿ *{name} ({symbol})*\n\n💰 Price: ${price}\n{emoji} 24h: {change}%\n🏆 Rank: #{rank}\n📊 Market Cap: ${mcap}",
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
        "ar": "🤖 *Omega Bot*\n\nالأوامر:\n/gold — ذهب\n/currency USD EUR — عملات\n/fuel LB — محروقات\n/weather London — طقس\n/football PL — كرة قدم\n/movie Inception — أفلام\n/cv — سيرة ذاتية\n/logo — شعار\n/stock AAPL — أسهم\n/crypto bitcoin — كريبتو\n/news — أخبار\n/flight LH400 — رحلات\n/quakes — زلازل\n/settings — إعدادات\n\nأو أرسل أي سؤال مباشرة!",
        "en": "🤖 *Omega Bot*\n\nCommands:\n/gold — Gold prices\n/currency USD EUR — Exchange\n/fuel LB — Fuel prices\n/weather London — Weather\n/football PL — Football\n/movie Inception — Movies\n/cv — Generate CV\n/logo — Logo design\n/stock AAPL — Stocks\n/crypto bitcoin — Crypto\n/news — Headlines\n/flight LH400 — Flights\n/quakes — Earthquakes\n/settings — Settings\n\nOr just type any question!",
        "fr": "🤖 *Omega Bot*\n\nCommandes:\n/gold — Or\n/currency — Devises\n/weather — Météo\n/news — Actualités\n/settings — Paramètres\n\nOu posez une question!",
        "tr": "🤖 *Omega Bot*\n\nKomutlar:\n/gold — Altın\n/currency — Döviz\n/weather — Hava\n/news — Haberler\n/settings — Ayarlar\n\nVeya bir soru yazın!",
        "ru": "🤖 *Omega Bot*\n\nКоманды:\n/gold — Золото\n/currency — Валюты\n/weather — Погода\n/news — Новости\n/settings — Настройки\n\nИли задайте вопрос!",
    },
    "admin_only": {
        "ar": "⛔ هذا الأمر للمشرفين فقط", "en": "⛔ Admin only",
        "fr": "⛔ Réservé aux admins", "tr": "⛔ Sadece yöneticiler", "ru": "⛔ Только для админов",
    },
    # ━━━ Sub-keys: Currency detail ━━━
    "currency_rates_title": {
        "ar": "💱 *أسعار {base}*", "en": "💱 *{base} Rates*",
        "fr": "💱 *Taux {base}*", "tr": "💱 *{base} Kurları*", "ru": "💱 *Курсы {base}*",
    },
    # ━━━ Sub-keys: Fuel ━━━
    "fuel_title_country": {
        "ar": "⛽ *أسعار المحروقات — {country}*", "en": "⛽ *Fuel Prices — {country}*",
        "fr": "⛽ *Prix carburant — {country}*", "tr": "⛽ *Yakıt — {country}*", "ru": "⛽ *Топливо — {country}*",
    },
    # ━━━ Sub-keys: Movies ━━━
    "trending_title": {
        "ar": "🎬 *الأفلام الرائجة:*", "en": "🎬 *Trending Movies:*",
        "fr": "🎬 *Films tendance:*", "tr": "🎬 *Trend Filmler:*", "ru": "🎬 *Популярные фильмы:*",
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
        "ar": "📰 *آخر الأخبار:*", "en": "📰 *Latest News:*",
        "fr": "📰 *Dernières nouvelles:*", "tr": "📰 *Son Haberler:*", "ru": "📰 *Последние новости:*",
    },
    "read_more": {
        "ar": "🔗 اقرأ المزيد", "en": "🔗 Read more", "fr": "🔗 Lire la suite",
        "tr": "🔗 Devamını oku", "ru": "🔗 Читать далее",
    },
    # ━━━ Sub-keys: Crypto ━━━
    "crypto_top_title": {
        "ar": "₿ *العملات الرقمية:*", "en": "₿ *Cryptocurrencies:*",
        "fr": "₿ *Cryptomonnaies:*", "tr": "₿ *Kripto Paralar:*", "ru": "₿ *Криптовалюты:*",
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
        "ar": "🤖 *مساعد AI الذكي*\n\nاكتب سؤالك بعد /ai\nأو أرسل أي رسالة مباشرة!",
        "en": "🤖 *AI Smart Assistant*\n\nType your question after /ai\nOr just send any message!",
        "fr": "🤖 *Assistant IA*\n\nÉcrivez après /ai\nOu envoyez un message!",
        "tr": "🤖 *AI Asistan*\n\n/ai sonrası sorunuzu yazın\nVeya direkt mesaj gönderin!",
    },
    # ━━━ Sub-keys: CV ━━━
    "cv_intro": {
        "ar": "📄 *إنشاء سيرة ذاتية احترافية*\n\nسأطلب منك 9 معلومات.",
        "en": "📄 *Professional CV Generator*\n\nI will ask you 9 questions.",
        "fr": "📄 *Générateur de CV*\n\n9 questions à remplir.",
        "tr": "📄 *Profesyonel CV Oluşturucu*\n\n9 soru soracağım.",
    },
    "cv_step": {
        "ar": "{n}️⃣ *الخطوة {n}/9:* {q}", "en": "{n}️⃣ *Step {n}/9:* {q}",
        "fr": "{n}️⃣ *Étape {n}/9:* {q}", "tr": "{n}️⃣ *Adım {n}/9:* {q}",
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
        "ar": "🎨 *مولّد الشعارات*\n\nأرسل اسم المشروع:\n/logo اسم المشروع",
        "en": "🎨 *Logo Generator*\n\nSend project name:\n/logo ProjectName",
        "fr": "🎨 *Générateur de logo*\n\nEnvoyez le nom:\n/logo NomProjet",
        "tr": "🎨 *Logo Oluşturucu*\n\nProje adı gönderin:\n/logo ProjeAdı",
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
        "ar": "🔴 *مباريات مباشرة:*", "en": "🔴 *Live Matches:*",
        "fr": "🔴 *Matchs en direct:*", "tr": "🔴 *Canli Maclar:*",
        "es": "🔴 *Partidos en vivo:*", "ru": "🔴 *Живые матчи:*",
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
        "ar": "📊 *إحصائيات Omega Bot*", "en": "📊 *Omega Bot Stats*",
        "fr": "📊 *Stats Omega Bot*", "tr": "📊 *Omega Bot Istatistikler*",
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
    # ── Downloader ────────────────────────────────────────────────────────────
    "dl_hint": {
        "ar": "📥 أرسل رابطاً من يوتيوب أو تيك توك أو إنستغرام...",
        "en": "📥 Send a YouTube, TikTok, or Instagram link to download it.",
        "fr": "📥 Envoyez un lien YouTube, TikTok ou Instagram.",
        "tr": "📥 YouTube, TikTok veya Instagram bağlantısı gönderin.",
    },
    "dl_choose_format": {
        "ar": "🎬 اختر صيغة التحميل:", "en": "🎬 Choose download format:",
        "fr": "🎬 Choisissez le format:", "tr": "🎬 Format seçin:",
    },
    "dl_downloading": {
        "ar": "⏳ جارٍ التحميل...", "en": "⏳ Downloading...",
        "fr": "⏳ Téléchargement...", "tr": "⏳ İndiriliyor...",
    },
    "dl_sending": {
        "ar": "📤 جارٍ الإرسال...", "en": "📤 Sending...",
        "fr": "📤 Envoi en cours...", "tr": "📤 Gönderiliyor...",
    },
    "dl_too_large": {
        "ar": "⚠️ الملف أكبر من 50MB. جرّب صيغة MP3.",
        "en": "⚠️ File exceeds 50MB limit. Try Audio MP3 instead.",
        "fr": "⚠️ Fichier > 50MB. Essayez le format MP3.",
        "tr": "⚠️ Dosya 50MB'ı aşıyor. MP3 formatını deneyin.",
    },
    "dl_no_url": {
        "ar": "❌ لم يُعثر على رابط. أرسل الرابط مجدداً.",
        "en": "❌ No URL found. Please send the link again.",
        "fr": "❌ Aucun lien trouvé. Renvoyez le lien.",
        "tr": "❌ URL bulunamadı. Lütfen bağlantıyı tekrar gönderin.",
    },
    # ── Transcriber ───────────────────────────────────────────────────────────
    "tr_hint": {
        "ar": "🎙️ أرسل رسالة صوتية أو مقطع فيديو لتحويله إلى نص.",
        "en": "🎙️ Send a voice message, video, or audio file to transcribe it.",
        "fr": "🎙️ Envoyez un message vocal ou une vidéo pour le transcrire.",
        "tr": "🎙️ Sesli mesaj veya video gönderin, metne dönüştüreyim.",
    },
    "tr_transcribing": {
        "ar": "🎙️ جارٍ النسخ...", "en": "🎙️ Transcribing...",
        "fr": "🎙️ Transcription en cours...", "tr": "🎙️ Yazıya dökülüyor...",
    },
    "tr_summarizing": {
        "ar": "⏳ جارٍ التلخيص...", "en": "⏳ Summarizing...",
        "fr": "⏳ Résumé en cours...", "tr": "⏳ Özetleniyor...",
    },
    "tr_no_speech": {
        "ar": "❌ لم يُتعرَّف على أي كلام.", "en": "❌ No speech detected in the file.",
        "fr": "❌ Aucune parole détectée.", "tr": "❌ Konuşma algılanamadı.",
    },
    "tr_no_key": {
        "ar": "❌ مفتاح Groq غير مُهيَّأ.", "en": "❌ Groq API key is not configured.",
        "fr": "❌ Clé Groq non configurée.", "tr": "❌ Groq API anahtarı yapılandırılmamış.",
    },
    "tr_no_ffmpeg": {
        "ar": "⚠️ تعذّر استخراج الصوت. أرسل ملف صوت مباشرةً.",
        "en": "⚠️ Could not extract audio. Please send an audio file directly.",
        "fr": "⚠️ Extraction audio impossible. Envoyez un fichier audio directement.",
        "tr": "⚠️ Ses çıkarılamadı. Lütfen doğrudan ses dosyası gönderin.",
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
            logger.info(f"[cache] Backend: Redis @ {settings.redis_url[:40]}")
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
            # Just log — do NOT message admin (clutters the chat when admin is a regular user)
            logger.warning(f"[ALERT] {source_name} failed {count} times consecutively — fallbacks active")

    @classmethod
    async def report_success(cls, source_name: str) -> None:
        """Report API recovery."""
        if source_name in cls._alerted:
            cls._alerted.discard(source_name)
            cls._failed_sources.pop(source_name, None)
            logger.info(f"[RECOVERED] {source_name} is back online")
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
            logger.warning("No models available, using Pollinations fallback")
            fallback = next((m for m in AI_MODELS if m["provider"] in ("pollinations", "llm7")), AI_MODELS[-1])
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

FILES["services/cards.py"] = r'''
"""Visual card formatters for all Omega Bot services.

Each function returns a Markdown-formatted string with emojis and bold prices.
All functions accept a `lang` parameter ("ar" | "en").
"""
from datetime import datetime
from typing import Optional


# ── helpers ──────────────────────────────────────────────────────────────────

def _sep() -> str:
    return "━━━━━━━━━━━━━━"


def _dir(lang: str) -> str:
    """Return RLM prefix for Arabic text in Telegram."""
    return "\u200F" if lang == "ar" else ""


# ── fuel card ────────────────────────────────────────────────────────────────

def fuel_card(
    prices_llp: dict,
    rate: float,
    lang: str,
    source: str,
    ago: str,
) -> str:
    """Format Lebanon fuel prices card.

    prices_llp: dict keyed by Arabic fuel name → "XXX,XXX ل.ل." strings.
    rate: LBP per 1 USD (e.g. 89700).
    lang: "ar" or "en".
    source: source label string.
    ago: human-readable age string like "5 دقائق" or "5 minutes".
    """
    import re

    def _parse_llp(val: str) -> Optional[float]:
        """Extract numeric LBP value from string."""
        m = re.search(r"([\d,]+)", str(val))
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                pass
        return None

    def _fmt_llp(val_str: str) -> str:
        """Return clean LBP string from raw value like '2,460,000 ل.ل.'"""
        v = _parse_llp(val_str)
        if v:
            return f"{v:,.0f} ل.ل."
        return str(val_str)

    def _usd_20l(llp_price: float) -> str:
        if rate and rate > 0:
            usd = llp_price / rate
            return f"≈ ${usd:.2f} / 20L"
        return ""

    def _usd_10kg(llp_price: float) -> str:
        if rate and rate > 0:
            usd = llp_price / rate
            return f"≈ ${usd:.2f}"
        return ""

    def _fuel_line(emoji: str, label_ar: str, label_en: str,
                   key_ar: str, key_en: str, is_20l: bool) -> str:
        """Build one fuel price line, always showing LBP value."""
        val_str = (prices_llp.get(key_ar)
                   or next((v for k, v in prices_llp.items()
                            if key_en.lower() in k.lower() or key_ar in k), None))
        if val_str:
            v = _parse_llp(str(val_str))
            llp_display = _fmt_llp(str(val_str))
            usd_display = (_usd_20l(v) if is_20l else _usd_10kg(v)) if v else ""
            return f"• {emoji} {label_en if lang != 'ar' else label_ar}:  {llp_display}  {usd_display}".rstrip()
        return f"• {emoji} {label_en if lang != 'ar' else label_ar}:  {'غير متاح' if lang == 'ar' else 'N/A'}"

    today = datetime.now().strftime("%Y-%m-%d")

    if lang == "ar":
        title = "⛽ *أسعار المحروقات — لبنان* 🇱🇧"
        date_line = f"📅 {today}"
        rate_line = f"💱 سعر الصرف: 1$ = {rate:,.0f} ل.ل." if rate else "💱 سعر الصرف: غير متاح"
        footer = f"🔄 منذ {ago} | {source}"
        lines = [title, date_line, ""]
        lines.append(_fuel_line("🔵", "بنزين 98", "Benzin 98", "بنزين 98", "98", True))
        lines.append(_fuel_line("🔵", "بنزين 95", "Benzin 95", "بنزين 95", "95", True))
        lines.append(_fuel_line("⚫", "ديزل",     "Diesel",    "ديزل",     "diesel", True))
        lines.append(_fuel_line("🟠", "غاز (10kg)", "Gas (10kg)", "غاز 10kg", "gas", False))
        lines.extend(["", rate_line, footer])
    else:
        title = "⛽ *Lebanon Fuel Prices* 🇱🇧"
        date_line = f"📅 {today}"
        rate_line = f"💱 Exchange Rate: 1$ = {rate:,.0f} LBP" if rate else "💱 Exchange Rate: unavailable"
        footer = f"🔄 {ago} ago | {source}"
        lines = [title, date_line, ""]
        lines.append(_fuel_line("🔵", "بنزين 98", "Benzin 98", "بنزين 98", "98", True))
        lines.append(_fuel_line("🔵", "بنزين 95", "Benzin 95", "بنزين 95", "95", True))
        lines.append(_fuel_line("⚫", "ديزل",     "Diesel",    "ديزل",     "diesel", True))
        lines.append(_fuel_line("🟠", "غاز (10kg)", "Gas (10kg)", "غاز 10kg", "gas", False))
        lines.extend(["", rate_line, footer])

    return "\n".join(lines)


# ── weather card ─────────────────────────────────────────────────────────────

def weather_card(data: dict, lang: str) -> str:
    """Format weather data into a visual card."""
    from datetime import datetime as _dt
    city        = data.get("city", "")
    country     = data.get("country", "")
    temp        = data.get("temperature", "N/A")
    feels       = data.get("feels_like", "N/A")
    humidity    = data.get("humidity", "N/A")
    wind        = data.get("wind_speed", "N/A")
    wind_dir    = data.get("wind_direction", "")
    precip      = data.get("precipitation")
    sunrise     = data.get("sunrise", "")
    sunset      = data.get("sunset", "")
    description = data.get("description", "")
    observed_at = data.get("observed_at", "")
    is_stale    = data.get("stale", False)

    obs_str = ""
    if observed_at:
        try:
            obs_str = _dt.fromisoformat(observed_at.replace("Z", "+00:00")).strftime("%H:%M")
        except Exception:
            obs_str = observed_at[:16] if len(observed_at) >= 16 else observed_at

    sep      = _sep()
    location = f"{city}, {country}" if country else city

    def _compass(deg) -> str:
        try:
            d = float(deg)
            dirs = ["N","NE","E","SE","S","SW","W","NW"]
            return dirs[int((d + 22.5) / 45) % 8]
        except Exception:
            return str(deg) if deg else ""

    wind_label = _compass(wind_dir) if wind_dir else ""

    if lang == "ar":
        lines = [
            f"{description or '🌤'} *{location}*",
            sep,
            f"🌡 *{temp}°C*  •  يُحسّ كـ {feels}°C",
            f"💧 الرطوبة: {humidity}%   💨 الرياح: {wind} كم/س {wind_label}",
        ]
        if precip is not None and float(precip) > 0:
            lines.append(f"🌧 هطول: {precip} مم")
        if sunrise and sunset:
            lines.append(f"🌅 {sunrise}  |  🌇 {sunset}")
        stale_note = " _(بيانات قديمة)_" if is_stale else ""
        ts_line = f"🕐 آخر تحديث: {obs_str}{stale_note}" if obs_str else ("⚠️ _(بيانات قديمة)_" if is_stale else "")
        if ts_line:
            lines.append(ts_line)
    else:
        lines = [
            f"{description or '🌤'} *{location}*",
            sep,
            f"🌡 *{temp}°C*  •  feels like {feels}°C",
            f"💧 Humidity: {humidity}%   💨 Wind: {wind} km/h {wind_label}",
        ]
        if precip is not None and float(precip) > 0:
            lines.append(f"🌧 Precipitation: {precip} mm")
        if sunrise and sunset:
            lines.append(f"🌅 {sunrise}  |  🌇 {sunset}")
        stale_note = " _(stale)_" if is_stale else ""
        ts_line = f"🕐 Updated: {obs_str}{stale_note}" if obs_str else ("⚠️ _(stale data)_" if is_stale else "")
        if ts_line:
            lines.append(ts_line)

    return "\n".join(lines)


# ── gold card ─────────────────────────────────────────────────────────────────

def gold_card(data: dict, lang: str) -> str:
    """Format precious metals prices into a visual card."""
    sep = _sep()
    xau = data.get("price_per_ounce", 0)
    xag = data.get("silver_per_ounce", 0)
    xpt = data.get("platinum_per_ounce", 0)
    gram = xau / 31.1035 if xau else 0
    change = data.get("change_24h_pct", None)
    change_str = f"{change:+.2f}%" if change is not None else "N/A"
    change_emoji = "📈" if (change or 0) >= 0 else "📉"

    if lang == "ar":
        lines = [
            "🥇 *أسعار الذهب والمعادن*",
            sep,
            f"💛 ذهب 24K: *${xau:,.2f}* / أونصة",
            f"   *${gram:,.2f}* / غرام",
        ]
        if xag:
            lines.append(f"🥈 فضة:    *${xag:,.2f}* / أونصة")
        if xpt:
            lines.append(f"🔘 بلاتين: *${xpt:,.2f}* / أونصة")
        lines.append(f"{change_emoji} تغيير 24س: *{change_str}*")
    else:
        lines = [
            "🥇 *Gold & Precious Metals*",
            sep,
            f"💛 Gold 24K: *${xau:,.2f}* / oz",
            f"   *${gram:,.2f}* / gram",
        ]
        if xag:
            lines.append(f"🥈 Silver:   *${xag:,.2f}* / oz")
        if xpt:
            lines.append(f"🔘 Platinum: *${xpt:,.2f}* / oz")
        lines.append(f"{change_emoji} 24h Change: *{change_str}*")

    return "\n".join(lines)


# ── crypto card ───────────────────────────────────────────────────────────────

def crypto_card(data: dict, lang: str) -> str:
    """Format cryptocurrency data into a visual card."""
    sep = _sep()
    name = data.get("name", "")
    symbol = data.get("symbol", "")
    price = data.get("price", 0)
    change_24h = data.get("change_24h", 0) or 0
    change_7d = data.get("change_7d", None)
    rank = data.get("rank", "N/A")
    mcap = data.get("market_cap", 0) or 0
    emoji = "📈" if change_24h >= 0 else "📉"

    if lang == "ar":
        lines = [
            f"₿ *{name} ({symbol})*",
            sep,
            f"💰 السعر: *${price:,.2f}*",
            f"{emoji} 24س: *{change_24h:+.2f}%*",
        ]
        if change_7d is not None:
            lines.append(f"📊 7 أيام: *{change_7d:+.2f}%*")
        lines.append(f"🏆 الترتيب: *#{rank}*")
        if mcap:
            lines.append(f"💎 القيمة السوقية: *${mcap:,.0f}*")
    else:
        lines = [
            f"₿ *{name} ({symbol})*",
            sep,
            f"💰 Price: *${price:,.2f}*",
            f"{emoji} 24h: *{change_24h:+.2f}%*",
        ]
        if change_7d is not None:
            lines.append(f"📊 7d: *{change_7d:+.2f}%*")
        lines.append(f"🏆 Rank: *#{rank}*")
        if mcap:
            lines.append(f"💎 Market Cap: *${mcap:,.0f}*")

    return "\n".join(lines)


# ── stock card ────────────────────────────────────────────────────────────────

def stock_card(data: dict, lang: str) -> str:
    """Format stock quote data into a visual card."""
    sep = _sep()
    name        = data.get("name", "") or data.get("symbol", "")
    symbol      = data.get("symbol", "")
    price       = data.get("price", 0) or 0
    change      = data.get("change", 0) or 0
    change_pct  = data.get("change_percent", 0) or 0
    try:
        change_pct = float(str(change_pct).replace("%",""))
    except Exception:
        change_pct = 0.0
    volume      = data.get("volume", 0) or 0
    mcap        = data.get("market_cap", 0) or 0
    pe          = data.get("pe_ratio", None)
    exchange    = data.get("exchange", "") or ""
    updated     = data.get("last_updated", "") or ""
    stale       = data.get("stale", False)
    emoji       = "📈" if change >= 0 else "📉"

    if lang == "ar":
        lines = [
            f"📊 *{name}*",
            f"🏷️ `{symbol}`" + (f"  |  🏦 {exchange}" if exchange else ""),
            sep,
            f"💰 السعر: *${price:,.2f}*",
            f"{emoji} التغيير: *{change:+,.2f}  ({change_pct:+.2f}%)*",
        ]
        if volume:
            lines.append(f"📦 الحجم: {volume:,}")
        if mcap:
            lines.append(f"💎 القيمة السوقية: ${mcap:,.0f}")
        if pe:
            lines.append(f"📐 P/E: {pe:.2f}")
        lines.append(sep)
        note = "⚠️ آخر سعر معروف" if stale else "🟢 بيانات حية"
        lines.append(f"🕐 {updated}  {note}" if updated else note)
    else:
        lines = [
            f"📊 *{name}*",
            f"🏷️ `{symbol}`" + (f"  |  🏦 {exchange}" if exchange else ""),
            sep,
            f"💰 Price: *${price:,.2f}*",
            f"{emoji} Change: *{change:+,.2f}  ({change_pct:+.2f}%)*",
        ]
        if volume:
            lines.append(f"📦 Volume: {volume:,}")
        if mcap:
            lines.append(f"💎 Market Cap: ${mcap:,.0f}")
        if pe:
            lines.append(f"📐 P/E: {pe:.2f}")
        lines.append(sep)
        note = "⚠️ Last known price" if stale else "🟢 Live"
        lines.append(f"🕐 {updated}  {note}" if updated else note)

    return "\n".join(lines)


# ── currency card ─────────────────────────────────────────────────────────────

def currency_card(data: dict, base: str, lang: str) -> str:
    """Format currency exchange rates into a visual card."""
    sep = _sep()
    rates = data.get("rates", {})
    updated = data.get("updated", "")

    DISPLAY_CURRENCIES = [
        ("USD", "🇺🇸", "دولار", "Dollar"),
        ("EUR", "🇪🇺", "يورو", "Euro"),
        ("GBP", "🇬🇧", "جنيه", "Pound"),
        ("AED", "🇦🇪", "درهم", "Dirham"),
        ("SAR", "🇸🇦", "ريال سعودي", "SAR"),
        ("TRY", "🇹🇷", "ليرة تركية", "TRY"),
        ("LBP", "🇱🇧", "ل.ل.", "LBP"),
        ("EGP", "🇪🇬", "جنيه مصري", "EGP"),
    ]

    if lang == "ar":
        lines = [f"💱 *أسعار العملات — أساس: {base}*", sep]
        for code, flag, name_ar, _ in DISPLAY_CURRENCIES:
            if code == base:
                continue
            rate = rates.get(code)
            if rate is not None:
                lines.append(f"{flag} {name_ar}: *{rate:,.4f}*")
    else:
        lines = [f"💱 *Currency Rates — Base: {base}*", sep]
        for code, flag, _, name_en in DISPLAY_CURRENCIES:
            if code == base:
                continue
            rate = rates.get(code)
            if rate is not None:
                lines.append(f"{flag} {name_en}: *{rate:,.4f}*")

    if updated:
        lines.append(f"\n🕐 Updated: {updated}")

    return "\n".join(lines)
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


# Static fallback rates — used when ALL live APIs are down.
# Updated manually to reflect approximate real-world rates (April 2024 basis).
_STATIC_FALLBACK: dict[tuple, float] = {
    ("USD", "EUR"): 0.921,  ("USD", "GBP"): 0.789,  ("USD", "JPY"): 149.5,
    ("USD", "CHF"): 0.891,  ("USD", "CAD"): 1.362,  ("USD", "AUD"): 1.529,
    ("USD", "LBP"): 89500.0,("USD", "SAR"): 3.750,  ("USD", "AED"): 3.672,
    ("USD", "EGP"): 48.85,  ("USD", "TRY"): 32.5,   ("USD", "JOD"): 0.709,
    ("USD", "KWD"): 0.307,  ("USD", "QAR"): 3.640,  ("USD", "BHD"): 0.376,
    ("USD", "OMR"): 0.385,  ("USD", "IQD"): 1310.0, ("USD", "SYP"): 13000.0,
    ("USD", "MAD"): 9.97,   ("USD", "DZD"): 134.5,  ("USD", "TND"): 3.11,
    ("EUR", "USD"): 1.085,  ("EUR", "GBP"): 0.857,  ("EUR", "LBP"): 97020.0,
    ("GBP", "USD"): 1.267,  ("GBP", "EUR"): 1.167,  ("GBP", "LBP"): 113300.0,
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
'''

FILES["api_clients/omega_fuel.py"] = r'''
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

_STATIC_FUEL_PRICES: dict[str, dict] = {
    "SA": {"بنزين 91": "0.208 USD/L", "بنزين 95": "0.240 USD/L", "ديزل": "0.067 USD/L"},
    "AE": {"بنزين 91 (E-Plus)": "0.720 USD/L", "بنزين 95 (Special)": "0.757 USD/L", "بنزين 98 (Super)": "0.786 USD/L", "ديزل": "0.736 USD/L"},
    "EG": {"بنزين 92": "0.275 USD/L", "بنزين 95": "0.327 USD/L", "ديزل": "0.168 USD/L"},
    "KW": {"بنزين 91 (Premium)": "0.197 USD/L", "بنزين 95 (Super)": "0.230 USD/L", "ديزل": "0.197 USD/L"},
    "QA": {"بنزين 91 (Special)": "0.449 USD/L", "بنزين 95 (Premium)": "0.461 USD/L", "ديزل": "0.449 USD/L"},
    "JO": {"بنزين 90": "1.061 USD/L", "بنزين 95": "1.229 USD/L", "ديزل": "1.272 USD/L"},
    "IQ": {"بنزين": "0.307 USD/L", "ديزل": "0.230 USD/L"},
    "DZ": {"بنزين": "0.277 USD/L", "ديزل": "0.166 USD/L"},
    "MA": {"بنزين 95": "1.230 USD/L", "ديزل": "1.010 USD/L"},
    "TN": {"بنزين 91": "0.820 USD/L", "بنزين 95": "0.899 USD/L", "ديزل": "0.690 USD/L"},
    "TR": {"بنزين 95": "1.260 USD/L", "ديزل": "1.140 USD/L"},
    "US": {"Gasoline (Regular)": "0.950 USD/L", "Diesel": "1.000 USD/L"},
    "DE": {"Super E10 (95)": "1.750 USD/L", "Diesel": "1.600 USD/L"},
    "FR": {"SP95-E10": "1.700 USD/L", "Diesel": "1.550 USD/L"},
    "GB": {"Petrol E10": "1.650 USD/L", "Diesel": "1.680 USD/L"},
    "JP": {"Regular": "1.200 USD/L", "Diesel": "1.150 USD/L"},
    "IN": {"Petrol": "1.300 USD/L", "Diesel": "1.100 USD/L"},
    "BR": {"Gasoline": "1.200 USD/L", "Diesel": "1.000 USD/L"},
    "RU": {"AI-95": "0.620 USD/L", "Diesel": "0.580 USD/L"},
    "CN": {"No. 92": "1.050 USD/L", "Diesel": "0.990 USD/L"},
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

        # Source 0a: ScraperAPI proxy — bypasses Render IP block (1 credit/call)
        _skey = getattr(settings, "scraper_api_key", "") or ""
        if _skey:
            import httpx as _httpx
            try:
                async with _httpx.AsyncClient(timeout=15.0) as _cl:
                    _r = await _cl.get(
                        "https://api.scraperapi.com/",
                        params={"api_key": _skey,
                                "url": "https://www.iptgroup.com.lb/ipt/en/our-stations/fuel-prices"},
                    )
                    if _r.status_code == 200 and len(_r.text) > 500:
                        _plain = re.sub(r'<[^>]+>', ' ', _r.text)
                        _prices = _extract_llp_prices(_plain)
                        if not _prices:
                            _prices = _extract_llp_prices(_r.text)
                        if len(_prices) >= 2:
                            _pub = _extract_date(_plain)
                            _prices["__scraped_at__"] = _NOW_ISO
                            _prices["__published_date__"] = _pub
                            logger.info(f"ScraperAPI IPT prices: {_prices}")
                            return _prices
            except Exception as _exc:
                logger.debug(f"ScraperAPI IPT error: {_exc}")

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
        Scrape the GlobalPetrolPrices main listing pages (gasoline + diesel)
        which list ALL countries in one table — far more reliable than per-country pages.
        Cached 12 hours.
        """
        cache_key = "gpp:listing"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        import re as _re
        from bs4 import BeautifulSoup

        result: dict[str, dict] = {}

        for fuel_key, url_path in [("gasoline", "gasoline_prices"), ("diesel", "diesel_prices")]:
            url = f"https://www.globalpetrolprices.com/{url_path}/"
            try:
                html = await self._scraper.fetch_html(url, headers=_GPP_BROWSER_HEADERS)
                if not html or len(html) < 2000:
                    continue
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
            except Exception as exc:
                logger.debug(f"_fetch_gpp_all {fuel_key}: {exc}")

        if result:
            await cache.set(cache_key, result, ttl=3600 * 12)
        return result

    async def _get_global_prices(self, country_code: str) -> dict[str, Any]:
        """Get fuel prices: tries GPP listing page first, then static fallback."""
        if country_code in ARAB_FUEL_SOURCES:
            name_ar = ARAB_FUEL_SOURCES[country_code]["name_ar"]
            name_en = ARAB_FUEL_SOURCES[country_code]["name_en"]
        else:
            name_ar, name_en = _COUNTRY_NAMES.get(country_code, (country_code, country_code))

        all_prices = await self._fetch_gpp_all()
        if country_code in all_prices:
            return {
                "country_code":    country_code,
                "country_name_ar": name_ar,
                "country_name_en": name_en,
                "prices":          all_prices[country_code],
                "source":          "GlobalPetrolPrices",
                "error":           False,
            }

        static = _STATIC_FUEL_PRICES.get(country_code)
        if static:
            return {
                "country_code":    country_code,
                "country_name_ar": name_ar,
                "country_name_en": name_en,
                "prices":          static,
                "source":          "static",
                "stale":           True,
                "error":           False,
            }

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
                obs_time = current.get("time", "")
                return {
                    "temperature": current["temperature_2m"],
                    "feels_like": current["apparent_temperature"],
                    "humidity": current["relative_humidity_2m"],
                    "precipitation": current["precipitation"],
                    "wind_speed": current["windspeed_10m"],
                    "wind_direction": current["winddirection_10m"],
                    "weather_code": current["weathercode"],
                    "description": self._weather_code_to_text(current["weathercode"], lang),
                    "observed_at": obs_time,
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
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from config import settings, CACHE_TTL
from services.cache_service import cache

logger = logging.getLogger(__name__)

BASE = "https://v3.football.api-sports.io"
CURRENT_SEASON = 2024

MAJOR_LEAGUES = {
    "PL":  {"id": 39,  "name": "Premier League",        "name_ar": "الدوري الإنجليزي",       "country": "England"},
    "PD":  {"id": 140, "name": "La Liga",               "name_ar": "الدوري الإسباني",        "country": "Spain"},
    "SA":  {"id": 135, "name": "Serie A",               "name_ar": "الدوري الإيطالي",        "country": "Italy"},
    "BL1": {"id": 78,  "name": "Bundesliga",            "name_ar": "الدوري الألماني",        "country": "Germany"},
    "FL1": {"id": 61,  "name": "Ligue 1",               "name_ar": "الدوري الفرنسي",         "country": "France"},
    "CL":  {"id": 2,   "name": "Champions League",      "name_ar": "دوري أبطال أوروبا",      "country": "Europe"},
    "SPL": {"id": 307, "name": "Saudi Pro League",      "name_ar": "دوري روشن",              "country": "Saudi Arabia"},
    "ELC": {"id": 40,  "name": "Championship",          "name_ar": "دوري الدرجة الأولى",     "country": "England"},
}

_TSDB_LEAGUE_IDS: dict[str, int] = {
    "PL":  4328,  # Premier League
    "PD":  4335,  # La Liga
    "SA":  4332,  # Serie A
    "BL1": 4331,  # Bundesliga
    "FL1": 4334,  # Ligue 1
    "CL":  4480,  # UEFA Champions League
    "ELC": 4336,  # Championship
}

_TSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"

# Sofascore tournament IDs (free, no API key)
_SF_TOURNAMENT_IDS: dict[str, int] = {
    "PL":  17,
    "PD":  8,
    "SA":  23,
    "BL1": 35,
    "FL1": 37,
    "CL":  7,
    "SPL": 679,
    "ELC": 44,
}

_SF_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
}

# Hardcoded team lists (2024-25 seasons) — last-resort fallback when every
# live source (Sofascore standings + day scan) fails or returns empty.
_FALLBACK_TEAMS: dict[str, list[str]] = {
    "PL": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town",
        "Leicester City", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham",
        "West Ham", "Wolverhampton",
    ],
    "PD": [
        "Alavés", "Athletic Club", "Atlético Madrid", "Barcelona",
        "Celta Vigo", "Espanyol", "Getafe", "Girona", "Las Palmas",
        "Leganés", "Mallorca", "Osasuna", "Rayo Vallecano", "Real Betis",
        "Real Madrid", "Real Sociedad", "Sevilla", "Valencia",
        "Valladolid", "Villarreal",
    ],
    "SA": [
        "Atalanta", "Bologna", "Cagliari", "Como", "Empoli",
        "Fiorentina", "Genoa", "Hellas Verona", "Inter", "Juventus",
        "Lazio", "Lecce", "Milan", "Monza", "Napoli",
        "Parma", "Roma", "Torino", "Udinese", "Venezia",
    ],
    "BL1": [
        "Augsburg", "Bayer Leverkusen", "Bayern München", "Bochum", "Borussia Dortmund",
        "Borussia Mönchengladbach", "Eintracht Frankfurt", "FC St. Pauli", "Freiburg",
        "Heidenheim", "Hoffenheim", "Holstein Kiel", "Mainz 05", "RB Leipzig",
        "Stuttgart", "Union Berlin", "Werder Bremen", "Wolfsburg",
    ],
    "FL1": [
        "Angers", "Auxerre", "Brest", "Le Havre", "Lens",
        "Lille", "Lyon", "Marseille", "Monaco", "Montpellier",
        "Nantes", "Nice", "Paris Saint-Germain", "Reims", "Rennes",
        "Saint-Étienne", "Strasbourg", "Toulouse",
    ],
    "SPL": [
        "Al-Ahli", "Al-Ettifaq", "Al-Fateh", "Al-Fayha", "Al-Hilal",
        "Al-Ittihad", "Al-Kholood", "Al-Nassr", "Al-Okhdood", "Al-Orobah",
        "Al-Qadsiah", "Al-Raed", "Al-Riyadh", "Al-Shabab", "Al-Taawoun",
        "Al-Wehda", "Damac", "Al-Khaleej",
    ],
    "ELC": [
        "Blackburn", "Bristol City", "Burnley", "Cardiff City", "Coventry City",
        "Derby County", "Hull City", "Leeds United", "Luton Town", "Middlesbrough",
        "Millwall", "Norwich City", "Oxford United", "Plymouth Argyle",
        "Portsmouth", "Preston North End", "Queens Park Rangers", "Sheffield United",
        "Sheffield Wednesday", "Stoke City", "Sunderland", "Swansea City",
        "Watford", "West Bromwich Albion",
    ],
    "CL": [
        "Real Madrid", "Manchester City", "Bayern München", "Paris Saint-Germain",
        "Liverpool", "Arsenal", "Barcelona", "Inter", "Borussia Dortmund",
        "Atlético Madrid", "RB Leipzig", "Bayer Leverkusen", "Milan", "Juventus",
        "Celtic", "Feyenoord", "PSV Eindhoven", "Benfica", "Sporting CP",
        "Atalanta", "Aston Villa", "Monaco", "Brest", "Lille",
        "Club Brugge", "Young Boys", "Shakhtar Donetsk", "Dinamo Zagreb",
        "Red Star Belgrade", "Sparta Prague", "Slovan Bratislava", "Sturm Graz",
        "Girona", "Salzburg", "Bologna", "Stuttgart",
    ],
}


def _sf_tid(ev: dict) -> int | None:
    """Get the uniqueTournament ID from a Sofascore event (not the stage/round ID)."""
    t = ev.get("tournament", {})
    return t.get("uniqueTournament", {}).get("id") or t.get("id")


def _headers() -> dict:
    return {"x-apisports-key": settings.api_football_key}


def _normalize_sofascore(event: dict) -> dict | None:
    """Normalize a Sofascore event into the standard fixture dict."""
    try:
        home = event.get("homeTeam", {}).get("name", "")
        away = event.get("awayTeam", {}).get("name", "")
        if not home or not away:
            return None
        status_obj  = event.get("status", {})
        status_type = status_obj.get("type", "notstarted")
        elapsed     = status_obj.get("description", "")
        _STATUS_MAP = {
            "notstarted": "NS", "inprogress": "1H",
            "finished": "FT",  "halftime": "HT",
            "postponed": "PST","cancelled": "CANC",
        }
        status = _STATUS_MAP.get(status_type, status_type.upper()[:3])
        scores = event.get("homeScore", {}), event.get("awayScore", {})
        h_score = scores[0].get("current") if status not in ("NS",) else None
        a_score = scores[1].get("current") if status not in ("NS",) else None
        tournament = event.get("tournament", {})
        league_name = tournament.get("name", "")
        import datetime as _dt
        start_ts = event.get("startTimestamp", 0)
        date_utc = ""
        if start_ts:
            date_utc = _dt.datetime.fromtimestamp(
                start_ts, tz=_dt.timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        return {
            "fixture_id":     event.get("id"),
            "league":         league_name,
            "league_ar":      league_name,  # Sofascore doesn't have Arabic names
            "home":           home,
            "away":           away,
            "home_score":     h_score,
            "away_score":     a_score,
            "status":         status,
            "status_elapsed": elapsed,
            "venue":          event.get("venue", {}).get("name", ""),
            "date_utc":       date_utc,
            "source":         "sofascore",
        }
    except Exception:
        return None


def _normalize_fixture(fixture: dict, league_code: str) -> dict:
    f = fixture.get("fixture", {})
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    status = f.get("status", {})
    venue = f.get("venue", {})
    league_info = MAJOR_LEAGUES.get(league_code, {})
    return {
        "fixture_id": f.get("id"),
        "league": league_info.get("name", league_code),
        "league_ar": league_info.get("name_ar", league_code),
        "home": teams.get("home", {}).get("name", ""),
        "away": teams.get("away", {}).get("name", ""),
        "home_score": goals.get("home"),
        "away_score": goals.get("away"),
        "status": status.get("short", "NS"),
        "status_elapsed": status.get("elapsed"),
        "venue": venue.get("name", ""),
        "date_utc": f.get("date", ""),
    }


class OmegaFootball:

    async def _get(self, path: str, params: dict) -> Optional[dict]:
        if not settings.api_football_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{BASE}{path}", params=params, headers=_headers())
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning(f"api-football error: {exc}")
            return None

    def _normalize_tsdb(self, ev: dict, league_code: str) -> dict | None:
        """Normalize a TheSportsDB event into the standard fixture dict."""
        try:
            home = ev.get("strHomeTeam", "") or ""
            away = ev.get("strAwayTeam", "") or ""
            if not home or not away:
                return None
            raw_status = (ev.get("strStatus") or ev.get("strProgress") or "").strip()
            _ST = {
                "Match Finished": "FT", "FT": "FT",
                "Not Started": "NS",    "NS": "NS",
                "In Progress": "1H",
                "Half Time": "HT",
                "Postponed": "PST",
                "Cancelled": "CANC",
            }
            status = _ST.get(raw_status, "NS" if not raw_status else raw_status[:3])
            h_score: int | None = None
            a_score: int | None = None
            if status == "FT":
                try:
                    h_score = int(ev.get("intHomeScore") or 0)
                    a_score = int(ev.get("intAwayScore") or 0)
                except (TypeError, ValueError):
                    pass
            # Build UTC timestamp from dateEvent + strTime
            date_utc = ""
            date_ev  = ev.get("strTimestamp") or ev.get("dateEvent", "")
            time_ev  = ev.get("strTime", "")
            if date_ev and "T" in date_ev:
                date_utc = date_ev if date_ev.endswith("Z") else date_ev + "+00:00"
            elif date_ev and time_ev:
                try:
                    date_utc = f"{date_ev}T{time_ev}+00:00"
                except Exception:
                    date_utc = date_ev
            info = MAJOR_LEAGUES.get(league_code.upper(), {})
            return {
                "fixture_id":     ev.get("idEvent"),
                "league":         info.get("name", league_code),
                "league_ar":      info.get("name_ar", league_code),
                "home":           home,
                "away":           away,
                "home_score":     h_score,
                "away_score":     a_score,
                "status":         status,
                "status_elapsed": None,
                "venue":          ev.get("strVenue", ""),
                "date_utc":       date_utc,
                "source":         "thesportsdb",
            }
        except Exception:
            return None

    async def _fetch_thesportsdb(self, league_code: str) -> list:
        """Fetch recent + upcoming fixtures from TheSportsDB (free, no key)."""
        tsdb_id = _TSDB_LEAGUE_IDS.get(league_code.upper())
        if not tsdb_id:
            return []
        fixtures: list[dict] = []
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                for endpoint in ("eventsnextleague", "eventspastleague"):
                    r = await client.get(
                        f"{_TSDB_BASE}/{endpoint}.php",
                        params={"id": tsdb_id},
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    if r.status_code == 200:
                        for ev in (r.json().get("events") or []):
                            n = self._normalize_tsdb(ev, league_code)
                            if n:
                                fixtures.append(n)
        except Exception as exc:
            logger.warning(f"TheSportsDB fixtures {league_code}: {exc}")
        return fixtures

    async def _fetch_thesportsdb_team(self, team_name: str) -> tuple[str, list, list]:
        """Search team on TheSportsDB → (team_id, last_5, next_5)."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                r = await client.get(
                    f"{_TSDB_BASE}/searchteams.php",
                    params={"t": team_name},
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                if r.status_code != 200:
                    return "", [], []
                teams = r.json().get("teams") or []
                if not teams:
                    return "", [], []
                team_id = teams[0].get("idTeam", "")
                if not team_id:
                    return "", [], []
                past_raw:     list = []
                upcoming_raw: list = []
                for endpoint, dest in (("eventslast", past_raw), ("eventsnext", upcoming_raw)):
                    r2 = await client.get(
                        f"{_TSDB_BASE}/{endpoint}.php",
                        params={"id": team_id},
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    if r2.status_code == 200:
                        dest += r2.json().get("events") or []
                return team_id, past_raw, upcoming_raw
        except Exception as exc:
            logger.warning(f"TheSportsDB team search '{team_name}': {exc}")
        return "", [], []

    async def get_fixtures(self, league_code: str, status: str = "all") -> list | dict:
        league_info = MAJOR_LEAGUES.get(league_code.upper())
        if not league_info:
            return {"error": True, "message": "Unknown league"}
        league_id   = league_info["id"]
        league_code_up = league_code.upper()
        cache_key = f"apifb:fixtures:{league_code_up}:{status}"
        ttl = CACHE_TTL.get("football_live", 60) if status.upper() == "LIVE" else CACHE_TTL.get("football_static", 3600)
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        from datetime import date, timedelta
        today = date.today()

        # Source 1 — API-Football (RapidAPI)
        if settings.api_football_key:
            params: dict[str, Any] = {"league": league_id, "season": CURRENT_SEASON}
            if status.upper() == "LIVE":
                params["live"] = "all"
            elif status.upper() not in ("ALL", ""):
                params["status"] = status.upper()
            else:
                params["from"] = (today - timedelta(days=3)).isoformat()
                params["to"]   = (today + timedelta(days=4)).isoformat()
            data = await self._get("/fixtures", params)
            if data and "response" in data:
                fixtures = [_normalize_fixture(f, league_code_up) for f in data["response"]]
                await cache.set(cache_key, fixtures, ttl=ttl)
                return fixtures

        # Source 2 — football-data.org (free key)
        if settings.football_data_key:
            fd_fixtures = await self._fetch_football_data(league_code_up, today, timedelta)
            if fd_fixtures:
                await cache.set(cache_key, fd_fixtures, ttl=ttl)
                return fd_fixtures

        # Source 3 — Sofascore (no key, always free) — filter strictly by this league
        sf_id    = _SF_TOURNAMENT_IDS.get(league_code_up)
        league_ar_name = MAJOR_LEAGUES.get(league_code_up, {}).get("name_ar", "")
        all_fixtures: list[dict] = []
        if sf_id:
            for delta in (0, -1, 1, -2, 2, 3):
                d = (today + timedelta(days=delta)).strftime("%Y-%m-%d")
                events = await self._sofascore_raw_day(d)
                for ev in events:
                    if _sf_tid(ev) != sf_id:
                        continue
                    n = _normalize_sofascore(ev)
                    if n:
                        if league_ar_name:
                            n["league_ar"] = league_ar_name
                        all_fixtures.append(n)
        if all_fixtures:
            await cache.set(cache_key, all_fixtures, ttl=ttl)
            return all_fixtures

        # Source 4 — TheSportsDB (free, no key)
        tsdb_fixtures = await self._fetch_thesportsdb(league_code_up)
        if tsdb_fixtures:
            await cache.set(cache_key, tsdb_fixtures, ttl=ttl)
            return tsdb_fixtures

        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def _fetch_football_data(self, league_code: str, today, timedelta) -> list:
        """Fetch from football-data.org v4 (free key)."""
        # football-data.org uses competition codes directly
        _FD_CODES = {
            "PL": "PL", "PD": "PD", "SA": "SA",
            "BL1": "BL1", "FL1": "FL1", "CL": "CL",
        }
        fd_code = _FD_CODES.get(league_code)
        if not fd_code:
            return []
        date_from = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        date_to   = (today + timedelta(days=4)).strftime("%Y-%m-%d")
        url = f"https://api.football-data.org/v4/competitions/{fd_code}/matches"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    url,
                    params={"dateFrom": date_from, "dateTo": date_to},
                    headers={"X-Auth-Token": settings.football_data_key},
                )
                if r.status_code != 200:
                    logger.debug(f"football-data.org {r.status_code}")
                    return []
                matches = r.json().get("matches", [])
                fixtures = []
                for m in matches:
                    home = m.get("homeTeam", {}).get("name", "")
                    away = m.get("awayTeam", {}).get("name", "")
                    if not home:
                        continue
                    score = m.get("score", {})
                    ft    = score.get("fullTime", {})
                    status_raw = m.get("status", "SCHEDULED")
                    _ST = {
                        "SCHEDULED": "NS", "TIMED": "NS", "IN_PLAY": "1H",
                        "PAUSED": "HT", "FINISHED": "FT",
                        "POSTPONED": "PST", "CANCELLED": "CANC",
                    }
                    league_info = MAJOR_LEAGUES.get(league_code, {})
                    fixtures.append({
                        "fixture_id":     m.get("id"),
                        "league":         league_info.get("name", fd_code),
                        "league_ar":      league_info.get("name_ar", fd_code),
                        "home":           home,
                        "away":           away,
                        "home_score":     ft.get("home"),
                        "away_score":     ft.get("away"),
                        "status":         _ST.get(status_raw, status_raw[:3]),
                        "status_elapsed": m.get("minute"),
                        "venue":          m.get("venue", ""),
                        "date_utc":       m.get("utcDate", ""),
                        "source":         "football-data.org",
                    })
                return fixtures
        except Exception as exc:
            logger.warning(f"football-data.org error: {exc}")
            return []

    async def get_standings(self, league_code: str) -> dict:
        league_info = MAJOR_LEAGUES.get(league_code.upper())
        if not league_info:
            return {"error": True}
        league_id = league_info["id"]
        cache_key = f"apifb:standings:{league_code}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._get("/standings", {"league": league_id, "season": CURRENT_SEASON})
        if data and "response" in data:
            try:
                raw = data["response"][0]["league"]["standings"][0]
                standings = []
                for entry in raw:
                    team = entry.get("team", {})
                    all_s = entry.get("all", {})
                    goals = all_s.get("goals", {})
                    standings.append({
                        "position": entry.get("rank"),
                        "team": team.get("name", ""),
                        "played": all_s.get("played", 0),
                        "won": all_s.get("win", 0),
                        "draw": all_s.get("draw", 0),
                        "lost": all_s.get("lose", 0),
                        "goals_for": goals.get("for", 0),
                        "goals_against": goals.get("against", 0),
                        "goal_diff": entry.get("goalsDiff", 0),
                        "points": entry.get("points", 0),
                    })
                result = {
                    "league": league_code.upper(),
                    "league_name": league_info["name"],
                    "league_name_ar": league_info["name_ar"],
                    "standings": standings,
                    "error": False,
                }
                await cache.set(cache_key, result, ttl=CACHE_TTL.get("football_static", 3600))
                return result
            except (IndexError, KeyError) as exc:
                logger.warning(f"standings parse: {exc}")
        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def get_live(self) -> list | dict:
        cache_key = "apifb:live"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        # Try API-Football first
        if settings.api_football_key:
            league_ids = "-".join(str(v["id"]) for v in MAJOR_LEAGUES.values())
            data = await self._get("/fixtures", {"live": league_ids})
            if data and "response" in data:
                fixtures = []
                for raw in data["response"]:
                    lid = raw.get("league", {}).get("id")
                    code = next((k for k, v in MAJOR_LEAGUES.items() if v["id"] == lid), "")
                    fixtures.append(_normalize_fixture(raw, code))
                await cache.set(cache_key, fixtures, ttl=CACHE_TTL.get("football_live", 60))
                return fixtures
        # Sofascore fallback — free, no key
        return await self._sofascore_live()

    async def _sofascore_live(self) -> list | dict:
        """Fetch live matches from Sofascore (no API key needed)."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                r = await client.get(
                    "https://api.sofascore.com/api/v1/sport/football/events/live",
                    headers=_SF_HEADERS,
                )
                if r.status_code == 200:
                    events = r.json().get("events", [])
                    fixtures = [_normalize_sofascore(e) for e in events[:20]]
                    fixtures = [f for f in fixtures if f]
                    await cache.set("apifb:live", fixtures, ttl=CACHE_TTL.get("football_live", 60))
                    return fixtures if fixtures else {"error": True, "message": "No live matches"}
        except Exception as exc:
            logger.warning(f"Sofascore live error: {exc}")
        stale = await cache.get_stale("apifb:live")
        if stale and stale.get("data"):
            return stale["data"]
        return {"error": True}

    async def _sofascore_raw_day(self, date_str: str) -> list:
        """Fetch and cache raw Sofascore events for one day (un-normalized, includes tournament ID)."""
        cache_key = f"sfsc:raw:{date_str}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
                r = await client.get(
                    f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}",
                    headers=_SF_HEADERS,
                )
                if r.status_code == 200:
                    events = r.json().get("events", [])
                    await cache.set(cache_key, events, ttl=3600 * 6)
                    return events
        except Exception as exc:
            logger.warning(f"Sofascore raw day {date_str}: {exc}")
        return []

    async def _sofascore_scheduled(self, date_str: str) -> list | dict:
        """Fetch scheduled/recent matches from Sofascore for a date (normalized)."""
        cache_key = f"sofascore:sched:{date_str}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        events = await self._sofascore_raw_day(date_str)
        if events:
            _SF_LEAGUE_IDS = set(_SF_TOURNAMENT_IDS.values())
            filtered = [e for e in events if _sf_tid(e) in _SF_LEAGUE_IDS]
            if not filtered:
                return {"error": True}
            fixtures = [_normalize_sofascore(e) for e in filtered[:20]]
            fixtures = [f for f in fixtures if f]
            if fixtures:
                await cache.set(cache_key, fixtures, ttl=CACHE_TTL.get("football_static", 3600))
                return fixtures
        return {"error": True}

    async def get_league_teams(self, league_code: str) -> list[dict]:
        """Return hardcoded [{id, name}] for a league — no API calls, no cache."""
        _TEAMS: dict[str, list[str]] = {
            "PD":  ["Alavés","Athletic Club","Atlético Madrid","Barcelona","Celta Vigo","Espanyol","Getafe","Girona","Las Palmas","Leganés","Mallorca","Osasuna","Rayo Vallecano","Real Betis","Real Madrid","Real Sociedad","Sevilla","Valencia","Valladolid","Villarreal"],
            "PL":  ["Arsenal","Aston Villa","Bournemouth","Brentford","Brighton","Chelsea","Crystal Palace","Everton","Fulham","Ipswich","Leicester","Liverpool","Man City","Man United","Newcastle","Nottm Forest","Southampton","Spurs","West Ham","Wolves"],
            "SA":  ["AC Milan","Atalanta","Bologna","Cagliari","Como","Empoli","Fiorentina","Genoa","Inter","Juventus","Lazio","Lecce","Monza","Napoli","Parma","Roma","Torino","Udinese","Venezia","Verona"],
            "BL1": ["Augsburg","Bayern Munich","Bochum","Borussia Dortmund","Eintracht Frankfurt","Freiburg","Hamburg","Heidenheim","Hoffenheim","Köln","Leverkusen","Mainz","Mönchengladbach","RB Leipzig","St. Pauli","Stuttgart","Union Berlin","Werder Bremen"],
            "FL1": ["Auxerre","Brest","Lens","Lille","Lyon","Marseille","Monaco","Montpellier","Nantes","Nice","Paris FC","PSG","Reims","Rennes","Saint-Etienne","Strasbourg","Toulouse"],
            "CL":  ["Arsenal","Atlético Madrid","Atalanta","Aston Villa","Barcelona","Bayern Munich","Benfica","Bologna","Brest","Celtic","Club Brugge","Dortmund","Feyenoord","Girona","Inter","Juventus","Leverkusen","Lille","Liverpool","Man City","Monaco","PSG","PSV","RB Leipzig","Real Madrid","Salzburg","Shakhtar","Slovan","Sparta Prague","Sporting CP","Sturm Graz","Stuttgart"],
            "SPL": ["Al-Ahli","Al-Ettifaq","Al-Fateh","Al-Fayha","Al-Hazem","Al-Hilal","Al-Ittihad","Al-Khaleej","Al-Nassr","Al-Okhdood","Al-Orubah","Al-Qadisiyah","Al-Qadsiah","Al-Raed","Al-Riyadh","Al-Shabab","Al-Taawoun","Al-Wehda"],
            "ELC": ["Birmingham","Blackburn","Bristol City","Burnley","Cardiff","Coventry","Derby","Leeds","Luton","Middlesbrough","Millwall","Norwich","Oxford","Plymouth","Portsmouth","Preston","QPR","Sheffield United","Sheffield Wed","Stoke","Sunderland","Swansea","Watford","West Brom"],
        }
        lc = league_code.upper()
        return [{"id": i, "name": n} for i, n in enumerate(_TEAMS.get(lc, []))]

    async def get_team_schedule(self, team_id: int) -> dict:
        """Fetch last-5 + next-5 matches for a team from Sofascore."""
        cache_key = f"sfsc:team_sched:{team_id}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        past: list[dict] = []
        upcoming_raw: list[dict] = []

        for path, dest in (("events/last/0", past), ("events/next/0", upcoming_raw)):
            try:
                async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                    r = await client.get(
                        f"https://api.sofascore.com/api/v1/team/{team_id}/{path}",
                        headers=_SF_HEADERS,
                    )
                    if r.status_code == 200:
                        for ev in r.json().get("events", []):
                            n = _normalize_sofascore(ev)
                            if n:
                                dest.append(n)
            except Exception as exc:
                logger.warning(f"Sofascore team {path}: {exc}")

        # most recent first; cap at 5
        past = past[:5]   # events/last/0 returns most-recent first
        live     = [f for f in upcoming_raw if f["status"] not in ("NS", "TBD", "PST", "CANC")]
        upcoming = [f for f in upcoming_raw if f["status"] in ("NS", "TBD")][:5]

        has_data = bool(past or live or upcoming)
        result = {"past": past, "live": live, "upcoming": upcoming, "error": not has_data}
        await cache.set(cache_key, result, ttl=60 if live else 300)
        return result

    @staticmethod
    def _name_matches(query: str, candidate: str) -> bool:
        """Fuzzy team name match: handles accents, abbreviations, partial names."""
        import unicodedata as _ud
        def _norm(s: str) -> str:
            s = _ud.normalize("NFD", s.lower())
            return "".join(c for c in s if _ud.category(c) != "Mn")

        q = _norm(query)
        c = _norm(candidate)
        if q == c or q in c or c in q:
            return True
        q_tokens = set(q.split())
        c_tokens = set(c.split())
        if q_tokens and len(q_tokens & c_tokens) / len(q_tokens) >= 0.5:
            return True
        return False

    async def get_team_schedule_by_name(self, team_name: str, league_code: str = "") -> dict:
        """Fetch team schedule via API-Football league fixtures filtered by team name."""
        cache_key = f"tsched_name:{league_code}:{team_name}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        past: list[dict] = []
        upcoming: list[dict] = []
        live: list[dict] = []

        league_info = MAJOR_LEAGUES.get(league_code.upper(), {}) if league_code else {}
        league_id   = league_info.get("id")

        # Source 1 — API-Football: fetch league fixtures, filter by team name
        if settings.api_football_key and league_id:
            for season in (2025, 2024):
                try:
                    data = await self._get("/fixtures", {"league": league_id, "season": season, "next": 10})
                    past_data = await self._get("/fixtures", {"league": league_id, "season": season, "last": 10})
                    all_raw: list[dict] = []
                    if data and "response" in data:
                        all_raw += data["response"]
                    if past_data and "response" in past_data:
                        all_raw += past_data["response"]
                    matched = []
                    for f in all_raw:
                        home = f.get("teams", {}).get("home", {}).get("name", "")
                        away = f.get("teams", {}).get("away", {}).get("name", "")
                        if self._name_matches(team_name, home) or self._name_matches(team_name, away):
                            matched.append(_normalize_fixture(f, league_code.upper()))
                    if matched:
                        for n in matched:
                            status = n.get("status", "NS")
                            if status in ("1H", "2H", "HT", "ET", "PEN"):
                                live.append(n)
                            elif status == "FT":
                                past.append(n)
                            else:
                                upcoming.append(n)
                        break   # found results — no need to try next season
                except Exception as exc:
                    logger.warning(f"API-Football team schedule {team_name}: {exc}")

        # Source 2 — TheSportsDB (if API-Football unavailable or returned nothing)
        if not (past or live or upcoming):
            _, past_raw, upcoming_raw = await self._fetch_thesportsdb_team(team_name)
            for ev in past_raw:
                n = self._normalize_tsdb(ev, league_code)
                if n:
                    past.append(n)
            for ev in upcoming_raw:
                n = self._normalize_tsdb(ev, league_code)
                if n:
                    status = n.get("status", "NS")
                    if status in ("1H", "2H", "HT", "ET", "PEN"):
                        live.append(n)
                    elif status == "FT":
                        past.append(n)
                    else:
                        upcoming.append(n)

        past.sort(key=lambda x: x.get("date_utc", ""), reverse=True)
        upcoming.sort(key=lambda x: x.get("date_utc", ""))

        has_data = bool(past or live or upcoming)
        result = {
            "past": past[:5],
            "live": live,
            "upcoming": upcoming[:5],
            "error": not has_data,
        }
        if has_data:
            await cache.set(cache_key, result, ttl=60 if live else 300)
        return result

    async def get_events(self, fixture_id: int) -> list | dict:
        """Fetch match events: goals, cards, substitutions."""
        cache_key = f"apifb:events:{fixture_id}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        data = await self._get("/fixtures/events", {"fixture": fixture_id})
        if data and "response" in data:
            events = []
            for ev in data["response"]:
                ev_time = ev.get("time", {})
                events.append({
                    "team":    ev.get("team",   {}).get("name", ""),
                    "player":  ev.get("player", {}).get("name", ""),
                    "assist":  ev.get("assist", {}).get("name", ""),
                    "type":    ev.get("type",   ""),
                    "detail":  ev.get("detail", ""),
                    "elapsed": ev_time.get("elapsed", ""),
                    "extra":   ev_time.get("extra"),
                })
            await cache.set(cache_key, events, ttl=CACHE_TTL.get("football_live", 60))
            return events
        return {"error": True}


omega_football = OmegaFootball()
'''

FILES["api_clients/omega_movies.py"] = r'''
import logging
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL

# TMDB genre ID → name (covers movies + TV)
_GENRE_MAP: dict[int, str] = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
    53: "Thriller", 10752: "War", 37: "Western", 10759: "Action & Adventure",
    10762: "Kids", 10763: "News", 10764: "Reality", 10765: "Sci-Fi & Fantasy",
    10766: "Soap", 10767: "Talk", 10768: "War & Politics", 10770: "TV Movie",
}
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
                    "genres": [_GENRE_MAP[g] for g in item.get("genre_ids", []) if g in _GENRE_MAP][:3],
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
                    "genres": [_GENRE_MAP[g] for g in item.get("genre_ids", []) if g in _GENRE_MAP][:3],
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

    async def get_by_genre(self, genre_id: int, lang: str = "en") -> dict[str, Any]:
        """Get top movies by TMDB genre ID using discover endpoint."""
        cache_key = f"movie:genre:{genre_id}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached
        try:
            tmdb_lang = "ar" if lang == "ar" else "en-US"
            data = await self._tmdb.get(
                "/discover/movie",
                params={
                    "api_key": settings.tmdb_api_key,
                    "with_genres": genre_id,
                    "sort_by": "popularity.desc",
                    "language": tmdb_lang,
                    "vote_count.gte": 200,
                    "page": 1,
                },
            )
            if data and "results" in data:
                results = [
                    {
                        "id": item["id"],
                        "title": item.get("title") or item.get("name", ""),
                        "overview": (item.get("overview") or "")[:200],
                        "release_date": item.get("release_date") or item.get("first_air_date", ""),
                        "vote_average": round(item.get("vote_average", 0), 1),
                        "genres": [_GENRE_MAP[g] for g in item.get("genre_ids", []) if g in _GENRE_MAP][:3],
                        "media_type": "movie",
                    }
                    for item in data["results"][:10]
                    if item.get("vote_average", 0) >= 6.0
                ]
                result = {"results": results, "error": False}
                await cache.set(cache_key, result, ttl=CACHE_TTL["movies"])
                return result
        except Exception as exc:
            logger.debug(f"get_by_genre error: {exc}")
        return {"results": [], "error": True}

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
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from api_clients.base_client import BaseAPIClient
from config import CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)

# Common company name → ticker (Arabic + English)
_NAME_MAP: dict[str, str] = {
    "apple": "AAPL", "ابل": "AAPL", "آبل": "AAPL",
    "microsoft": "MSFT", "مايكروسوفت": "MSFT", "ميكروسوفت": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "جوجل": "GOOGL",
    "amazon": "AMZN", "امازون": "AMZN", "أمازون": "AMZN",
    "tesla": "TSLA", "تسلا": "TSLA",
    "meta": "META", "facebook": "META", "ميتا": "META", "فيسبوك": "META",
    "nvidia": "NVDA", "انفيديا": "NVDA", "نفيديا": "NVDA",
    "samsung": "005930.KS", "سامسونج": "005930.KS",
    "saudi aramco": "2222.SR", "أرامكو": "2222.SR", "ارامكو": "2222.SR",
    "stc": "7010.SR", "اتصالات السعودية": "7010.SR",
    "sabic": "2010.SR", "سابك": "2010.SR",
    "netflix": "NFLX", "نتفليكس": "NFLX",
    "disney": "DIS", "ديزني": "DIS",
    "snapchat": "SNAP", "snap": "SNAP", "سناب": "SNAP",
    "twitter": "X", "تويتر": "X",
    "uber": "UBER", "اوبر": "UBER",
    "paypal": "PYPL", "بيبال": "PYPL",
    "intel": "INTC", "انتل": "INTC",
    "amd": "AMD",
    "qualcomm": "QCOM", "كوالكوم": "QCOM",
    "alibaba": "BABA", "علي بابا": "BABA",
    "berkshire": "BRK-B",
    "johnson": "JNJ", "jpmorgan": "JPM", "goldman": "GS",
}


def _resolve_name(query: str) -> Optional[str]:
    """Try to resolve company name to ticker symbol."""
    q = query.strip().lower()
    # Direct map lookup
    if q in _NAME_MAP:
        return _NAME_MAP[q]
    # Partial match
    for name, ticker in _NAME_MAP.items():
        if name in q or q in name:
            return ticker
    return None


class OmegaStocks:

    def __init__(self):
        self._alpha = BaseAPIClient("alpha_vantage", "https://www.alphavantage.co")

    async def resolve_symbol(self, query: str) -> str:
        """Turn company name / Arabic name into a ticker symbol."""
        q = query.strip()
        # Already looks like a ticker (short, uppercase-able, no spaces)
        if len(q) <= 6 and q.replace(".", "").replace("-", "").isalnum():
            return q.upper()
        # Static map
        mapped = _resolve_name(q)
        if mapped:
            return mapped
        # yfinance Search fallback
        try:
            import yfinance as yf
            def _search():
                results = yf.Search(q, max_results=5).quotes
                for r in results:
                    sym = r.get("symbol", "")
                    qt  = r.get("quoteType", "")
                    if sym and qt in ("EQUITY", "ETF"):
                        return sym
                return None
            loop = asyncio.get_event_loop()
            sym = await asyncio.wait_for(loop.run_in_executor(None, _search), timeout=10.0)
            if sym:
                return sym
        except Exception as exc:
            logger.debug(f"yfinance search error: {exc}")
        return q.upper()

    async def get_quote(self, query: str) -> dict[str, Any]:
        symbol = await self.resolve_symbol(query)
        cache_key = f"stock:{symbol}"
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
            return result

        stale = await cache.get_stale(cache_key)
        if stale and stale.get("data"):
            r = stale["data"]
            r["stale"] = True
            return r

        return {"error": True, "symbol": symbol, "message": "البيانات غير متوفرة حالياً من المصادر الحية"}

    async def _fetch_yfinance(self, symbol: str) -> Optional[dict]:
        try:
            import yfinance as yf

            def _sync():
                t = yf.Ticker(symbol)
                fi = t.fast_info
                price = fi.last_price
                if not price or price <= 0:
                    hist = t.history(period="2d")
                    if hist.empty:
                        return None
                    price = float(hist["Close"].iloc[-1])
                prev  = getattr(fi, "previous_close", None) or price
                chg   = price - prev
                chg_p = (chg / prev * 100) if prev else 0
                mcap  = getattr(fi, "market_cap", 0) or 0
                exch  = getattr(fi, "exchange", "") or ""
                info  = {}
                try:
                    info = t.info or {}
                except Exception:
                    pass
                name = info.get("shortName") or info.get("longName") or symbol.upper()
                now  = datetime.now(timezone.utc).strftime("%H:%M UTC")
                return {
                    "symbol":         symbol.upper(),
                    "name":           name,
                    "price":          float(price),
                    "change":         float(chg),
                    "change_percent": float(chg_p),
                    "market_cap":     float(mcap),
                    "exchange":       exch,
                    "last_updated":   now,
                    "source":         "yfinance",
                    "error":          False,
                }

            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(loop.run_in_executor(None, _sync), timeout=25.0)
        except Exception as exc:
            logger.debug(f"yfinance {symbol}: {exc}")
        return None

    async def _fetch_alpha_vantage(self, symbol: str) -> Optional[dict]:
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
                now = datetime.now(timezone.utc).strftime("%H:%M UTC")
                return {
                    "symbol":         q.get("01. symbol", symbol),
                    "name":           q.get("01. symbol", symbol),
                    "price":          float(q.get("05. price", 0)),
                    "change":         float(q.get("09. change", 0)),
                    "change_percent": float(q.get("10. change percent", "0").replace("%", "")),
                    "volume":         int(q.get("06. volume", 0)),
                    "last_updated":   now,
                    "source":         "Alpha Vantage",
                    "error":          False,
                }
        except Exception as exc:
            logger.debug(f"AlphaVantage {symbol}: {exc}")
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
import xml.etree.ElementTree as ET
import html as html_mod
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

from api_clients.base_client import BaseAPIClient
from config import settings, CACHE_TTL
from services.cache_service import cache
from services.rate_limiter import quota

logger = logging.getLogger(__name__)

# Browser-like headers — prevents 403 from news CDNs
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

# RSS feeds that reliably serve cloud/datacenter IPs
_RSS_FEEDS = {
    "en": [
        "https://news.google.com/rss?hl=en&gl=US&ceid=US:en",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.skynews.com/feeds/rss/world.xml",
        "https://www.theguardian.com/world/rss",
        "https://feeds.reuters.com/reuters/topNews",
    ],
    "ar": [
        "https://news.google.com/rss?hl=ar&gl=SA&ceid=SA:ar",
        "https://news.google.com/rss?hl=ar&gl=LB&ceid=LB:ar",
        "https://www.aljazeera.net/xml/rss/all.xml",
        "https://www.bbc.com/arabic/rss.xml",
        "https://www.skynewsarabia.com/rss.xml",
        "https://arabic.rt.com/rss/",
    ],
}


def _parse_rss_xml(raw: str) -> list[dict]:
    """Parse RSS/Atom XML into article dicts."""
    articles: list[dict] = []
    try:
        raw_clean = raw.strip().lstrip("\ufeff")
        # Strip XML declaration if malformed
        raw_clean = re.sub(r"^<\?xml[^?]*\?>", "", raw_clean).strip()
        root = ET.fromstring(raw_clean)
        items = root.findall(".//item")[:10]
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")[:10]
        for item in items:
            def _t(tag: str, ns: str = "") -> str:
                el = item.find(f"{{{ns}}}{tag}" if ns else tag)
                if el is None:
                    return ""
                txt = (el.text or el.get("href", "")).strip()
                return html_mod.unescape(txt)
            title = _t("title")
            if not title or title.lower() in ("", "[removed]"):
                continue
            link = _t("link")
            if not link:
                link_el = item.find("link")
                if link_el is not None:
                    link = (link_el.tail or "").strip() or link_el.get("href", "")
            desc = _t("description") or _t("summary", "http://www.w3.org/2005/Atom")
            # Remove HTML tags from description
            desc = re.sub(r"<[^>]+>", "", desc)[:300]
            articles.append({
                "title":        title[:150],
                "description":  desc,
                "url":          link,
                "source":       _t("source") or "RSS",
                "published_at": _t("pubDate") or _t("updated", "http://www.w3.org/2005/Atom"),
            })
    except Exception as exc:
        logger.debug(f"RSS parse error: {exc}")
    return articles


class OmegaNews:
    """News aggregation: NewsAPI → GNews → Google News RSS → fallback RSS."""

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

        result = None
        # Tier 1 — keyed APIs
        if quota.has_quota("newsapi"):
            result = await self._fetch_newsapi(category, country)
            if result and not result.get("error"):
                quota.use_quota("newsapi")
        if (not result or result.get("error")) and quota.has_quota("gnews"):
            result = await self._fetch_gnews(category, lang)
            if result and not result.get("error"):
                quota.use_quota("gnews")
        # Tier 2 — Google News RSS (free, no key, cloud-friendly)
        if not result or result.get("error"):
            result = await self._fetch_google_news_rss(lang)
        # Tier 3 — fallback RSS feeds
        if not result or result.get("error"):
            result = await self._fetch_rss(lang)

        if result and not result.get("error"):
            await cache.set(cache_key, result, ttl=CACHE_TTL["news"])

        return result or {"articles": [], "error": True}

    async def search_news(self, query: str, lang: str = "en") -> dict[str, Any]:
        """Search news by keyword — prefers last 24h, falls back to 72h."""
        cache_key = f"news:search:{query}:{lang}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)

        if settings.newsapi_key:
            # Try 24h window first, widen to 72h if empty
            for hours in (24, 72):
                from_dt = (now - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
                try:
                    data = await self._newsapi.get(
                        "/everything",
                        params={
                            "apiKey": settings.newsapi_key,
                            "q": query,
                            "language": lang,
                            "pageSize": 10,
                            "sortBy": "publishedAt",
                            "from": from_dt,
                        },
                    )
                    if data and data.get("status") == "ok":
                        articles = self._parse_newsapi_articles(data.get("articles", []))
                        if articles or hours == 72:
                            result = {"articles": articles, "query": query,
                                      "error": False, "window_hours": hours}
                            await cache.set(cache_key, result, ttl=CACHE_TTL["news"])
                            return result
                except Exception as exc:
                    logger.debug(f"NewsAPI search error ({hours}h): {exc}")
                    break

        # Google News RSS search (no API key needed)
        gn_lang = "ar" if lang == "ar" else "en"
        gn_region = "SA" if lang == "ar" else "US"
        gn_ceid = f"{gn_region}:{gn_lang}"
        gn_url = f"https://news.google.com/rss/search?q={query}&hl={gn_lang}&gl={gn_region}&ceid={gn_ceid}"
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=_HEADERS) as client:
                r = await client.get(gn_url)
                if r.status_code == 200:
                    articles = _parse_rss_xml(r.text)
                    if articles:
                        result = {"articles": articles[:10], "query": query,
                                  "error": False, "window_hours": 72, "source": "Google News"}
                        await cache.set(cache_key, result, ttl=CACHE_TTL["news"])
                        return result
        except Exception as exc:
            logger.debug(f"Google News search error: {exc}")

        return {"articles": [], "error": True}

    async def _fetch_newsapi(self, category: str, country: str) -> Optional[dict]:
        """Fetch from NewsAPI — top headlines within the last 24 h."""
        if not settings.newsapi_key:
            return None
        from datetime import datetime, timedelta, timezone
        from_dt = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            data = await self._newsapi.get(
                "/top-headlines",
                params={
                    "apiKey": settings.newsapi_key,
                    "category": category,
                    "country": country,
                    "pageSize": 20,
                    "from": from_dt,
                },
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

    async def _fetch_google_news_rss(self, lang: str) -> Optional[dict]:
        """Google News RSS — free, no key, works from cloud IPs."""
        gn_lang = "ar" if lang == "ar" else "en"
        region  = "SA" if lang == "ar" else "US"
        url = f"https://news.google.com/rss?hl={gn_lang}&gl={region}&ceid={region}:{gn_lang}"
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=_HEADERS) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    articles = _parse_rss_xml(r.text)
                    if articles:
                        logger.info(f"Google News RSS OK → {len(articles)} articles")
                        return {"articles": articles[:10], "source": "Google News", "error": False}
        except Exception as exc:
            logger.debug(f"Google News RSS error: {exc}")
        return None

    async def _fetch_rss(self, lang: str) -> Optional[dict]:
        """Fetch from RSS feeds using browser-like headers to bypass CDN blocks."""
        urls = _RSS_FEEDS.get(lang, _RSS_FEEDS["en"])
        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True,
            headers=_HEADERS,
        ) as client:
            for url in urls:
                try:
                    r = await client.get(url)
                    if r.status_code != 200 or len(r.text) < 300:
                        logger.debug(f"RSS {url} → HTTP {r.status_code}")
                        continue
                    articles = _parse_rss_xml(r.text)
                    if articles:
                        logger.info(f"RSS OK: {url} → {len(articles)} articles")
                        return {"articles": articles[:10], "source": "RSS", "error": False}
                except Exception as exc:
                    logger.debug(f"RSS error {url}: {exc}")
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
from handlers.downloader import register_downloader_handlers
from handlers.transcriber import register_transcriber_handlers

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
    # Downloader and Transcriber must come before the AI catch-all
    register_downloader_handlers(dp)
    register_transcriber_handlers(dp)

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
import os
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.filters import Command, CommandStart

from config import t, settings
from database.connection import get_session
from database.crud import CRUDManager

logger = logging.getLogger(__name__)
router = Router(name="start")

# ── Reply Keyboard layout ─────────────────────────────────────────────────────
# Bilingual button labels. The text sent to the bot is the Arabic or English label.
_KB_AR = [
    ["⛽ محروقات",  "🌤 طقس",      "🥇 ذهب"],
    ["💱 عملة",     "⚽ كرة قدم",  "🎬 أفلام"],
    ["🤖 ذكاء اصطناعي", "✈️ رحلات", "🌍 زلازل"],
    ["📥 تحميل",   "🎙️ نسخ صوتي"],
    ["⚙️ إعدادات"],
]
_KB_EN = [
    ["⛽ Fuel",     "🌤 Weather",  "🥇 Gold"],
    ["💱 Currency", "⚽ Football", "🎬 Movies"],
    ["🤖 AI Chat",  "✈️ Flights",  "🌍 Quakes"],
    ["📥 Downloader", "🎙️ Transcriber"],
    ["⚙️ Settings"],
]

# Flat lookup: button text → internal key (for routing)
_BTN_MAP: dict[str, str] = {}
for _row in _KB_AR:
    for _lbl in _row:
        _key = _lbl.split()[-1].lower()  # last word as key
        _BTN_MAP[_lbl] = _key
for _row in _KB_EN:
    for _lbl in _row:
        _key = _lbl.split()[-1].lower()
        _BTN_MAP[_lbl] = _key

# Extra exact mappings for ambiguous labels
_BTN_MAP.update({
    "⛽ محروقات": "fuel",        "⛽ Fuel": "fuel",
    "🌤 طقس": "weather",         "🌤 Weather": "weather",
    "🥇 ذهب": "gold",            "🥇 Gold": "gold",
    "💱 عملة": "currency",       "💱 Currency": "currency",
    "⚽ كرة قدم": "football",    "⚽ Football": "football",
    "🎬 أفلام": "movies",        "🎬 Movies": "movies",
    "🤖 ذكاء اصطناعي": "ai",    "🤖 AI Chat": "ai",
    "✈️ رحلات": "flights",      "✈️ Flights": "flights",
    "🌍 زلازل": "quakes",       "🌍 Quakes": "quakes",
    "📥 تحميل": "downloader",   "📥 Downloader": "downloader",
    "🎙️ نسخ صوتي": "transcriber", "🎙️ Transcriber": "transcriber",
    "⚙️ إعدادات": "settings",   "⚙️ Settings": "settings",
})


def _build_reply_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    layout = _KB_AR if lang == "ar" else _KB_EN
    rows = [[KeyboardButton(text=lbl) for lbl in row] for row in layout]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="اكتب رسالتك..." if lang == "ar" else "Type a message...",
    )


async def _dispatch_key(message: Message, key: str, lang: str) -> None:
    """Route a menu key to the correct handler."""
    try:
        if key == "fuel":
            from handlers.fuel import cmd_fuel
            await cmd_fuel(message, lang=lang)
        elif key == "weather":
            hint = "🌤 أرسل اسم المدينة — مثال: بيروت" if lang == "ar" else "🌤 Send a city name — e.g. Beirut"
            await message.answer(hint)
        elif key == "gold":
            from handlers.gold import cmd_gold
            await cmd_gold(message, lang=lang)
        elif key == "currency":
            from handlers.currency import cmd_currency
            await cmd_currency(message, lang=lang)
        elif key == "crypto":
            from handlers.crypto import cmd_crypto
            await cmd_crypto(message, lang=lang)
        elif key == "stocks":
            hint = "📈 أرسل رمز السهم — مثال: AAPL" if lang == "ar" else "📈 Send a stock symbol — e.g. AAPL"
            await message.answer(hint)
        elif key == "news":
            from handlers.news import cmd_news
            await cmd_news(message, lang=lang)
        elif key == "football":
            from handlers.football import cmd_football
            await cmd_football(message, lang=lang)
        elif key == "movies":
            from handlers.movies import cmd_movie
            await cmd_movie(message, lang=lang)
        elif key == "ai":
            hint = "🤖 اكتب سؤالك مباشرةً!" if lang == "ar" else "🤖 Just type your question!"
            await message.answer(hint)
        elif key == "flights":
            hint = "✈️ أرسل رمز المطار — مثال: BEY" if lang == "ar" else "✈️ Send airport code — e.g. BEY"
            await message.answer(hint)
        elif key == "quakes":
            from api_clients.omega_quakes import omega_quakes
            await message.answer("🌍 ..." if lang != "ar" else "🌍 جارٍ الجلب...")
            result = await omega_quakes.get_recent(min_magnitude=4.0, limit=8)
            if result.get("error") or not result.get("quakes"):
                await message.answer(t("error", lang))
                return
            lines = ["🌍 *زلازل حديثة (M4+)*\n" if lang == "ar" else "🌍 *Recent Earthquakes (M4+)*\n"]
            for q in result["quakes"][:8]:
                mag = q.get("magnitude", 0)
                place = q.get("place", "Unknown")
                e = "🟥" if mag >= 6 else ("🟧" if mag >= 5 else "🟨")
                lines.append(f"{e} M{mag:.1f} — {place}")
            await message.answer("\n".join(lines), parse_mode="Markdown")
        elif key == "downloader":
            from handlers.downloader import cmd_download
            await cmd_download(message, lang=lang)
        elif key == "transcriber":
            from handlers.transcriber import cmd_transcribe
            await cmd_transcribe(message, lang=lang)
        elif key == "settings":
            from handlers.settings import cmd_settings
            await cmd_settings(message, lang=lang)
    except Exception as exc:
        logger.error(f"Menu dispatch error for key={key!r}: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str = "en") -> None:
    try:
        name = message.from_user.first_name or "User"
        welcome = t("welcome", lang, name=name)
        await message.answer(welcome, reply_markup=_build_reply_keyboard(lang))
    except Exception as exc:
        logger.error(f"Start error: {exc}", exc_info=True)
        await message.answer(t("error", "en"))


@router.message(Command("menu"))
async def cmd_menu(message: Message, lang: str = "en") -> None:
    label = "اختر خدمة:" if lang == "ar" else "Choose a service:"
    await message.answer(label, reply_markup=_build_reply_keyboard(lang))


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "en") -> None:
    await message.answer(t("help_text", lang), parse_mode="Markdown")


@router.message(F.text.func(lambda t: t in _BTN_MAP))
async def handle_menu_button(message: Message, lang: str = "en") -> None:
    """Intercept reply-keyboard button taps before the AI catch-all."""
    key = _BTN_MAP[message.text]
    await _dispatch_key(message, key, lang)


def register_start_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/gold.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_metals import omega_metals
from services.cards import gold_card
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

        # Enrich data with silver + platinum for the card
        try:
            ag = await omega_metals.get_prices("XAG", "USD")
            if not ag.get("error"):
                data["silver_per_ounce"] = ag.get("price_per_ounce", 0)
        except Exception:
            pass
        try:
            pt = await omega_metals.get_prices("XPT", "USD")
            if not pt.get("error"):
                data["platinum_per_ounce"] = pt.get("price_per_ounce", 0)
        except Exception:
            pass

        text = gold_card(data, lang)
        # Add karat detail if available
        if data.get("karats"):
            sep = "━━━━━━━━━━━━━━"
            karat_lines = [f"\n{sep}"]
            karat_label = "💛 أسعار الكيلو غرام" if lang == "ar" else "💛 Karat Prices (per gram)"
            karat_lines.append(karat_label)
            for k in ["24K", "22K", "21K", "18K", "14K", "9K"]:
                if k in data["karats"]:
                    karat_lines.append(f"  {k}: *${data['karats'][k]['per_gram']:,.2f}*")
            text += "\n".join(karat_lines)

        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_refresh", lang), callback_data="gold:refresh"),
             InlineKeyboardButton(text=t("btn_silver", lang), callback_data="metal:XAG"),
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
        text = f"🪙 *{name}*\n\n💰 ${data['price_per_ounce']:,.2f}"
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
import re
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_currency import omega_currency
from config import t

logger = logging.getLogger(__name__)
router = Router(name="currency")

# ─────────────────────────── NLP currency name map ───────────────────────────
# Sorted longest-first so multi-word names match before single words.
_CURRENCY_NAMES: dict[str, str] = {
    # Arabic multi-word first
    "دولار امريكي": "USD",  "دولار أمريكي": "USD",
    "ليرة لبنانية": "LBP",  "ليرة سورية": "SYP",  "ليرة تركية": "TRY",
    "جنيه إسترليني": "GBP", "جنيه استرليني": "GBP",
    "جنيه مصري": "EGP",
    "ريال سعودي": "SAR",    "ريال قطري": "QAR",   "ريال عماني": "OMR",
    "درهم إماراتي": "AED",  "درهم اماراتي": "AED", "درهم مغربي": "MAD",
    "دينار أردني": "JOD",   "دينار اردني": "JOD",
    "دينار كويتي": "KWD",
    "دينار بحريني": "BHD",
    "دينار عراقي": "IQD",
    "فرنك سويسري": "CHF",
    "دولار كندي": "CAD",    "دولار أسترالي": "AUD", "دولار استرالي": "AUD",
    "فرنك سويسري": "CHF",
    # Arabic single-word
    "دولار": "USD",  "الدولار": "USD",
    "يورو": "EUR",   "اليورو": "EUR",
    "جنيه": "GBP",   "الجنيه": "GBP",
    "ين": "JPY",     "الين": "JPY",
    "ليرة": "LBP",   "اللبنانية": "LBP",  "ليرات": "LBP",
    "ريال": "SAR",   "السعودي": "SAR",
    "درهم": "AED",   "الاماراتي": "AED",   "الإماراتي": "AED",
    "مصري": "EGP",
    "تركي": "TRY",
    "أردني": "JOD",  "اردني": "JOD",
    "كويتي": "KWD",
    "قطري": "QAR",
    "بحريني": "BHD",
    "عماني": "OMR",
    "عراقي": "IQD",
    "سوري": "SYP",
    "مغربي": "MAD",
    "فرنك": "CHF",
    "كندي": "CAD",
    "أسترالي": "AUD", "استرالي": "AUD",
    # English names
    "dollar": "USD", "dollars": "USD",
    "euro": "EUR",   "euros": "EUR",
    "pound": "GBP",  "pounds": "GBP",
    "yen": "JPY",
    "lira": "LBP",   "lebanese": "LBP",
    "riyal": "SAR",  "saudi": "SAR",
    "dirham": "AED", "emirati": "AED",
    "franc": "CHF",  "swiss": "CHF",
    "canadian": "CAD",
    "australian": "AUD",
}

_ISO_CODES = {
    "USD","EUR","GBP","JPY","CHF","CAD","AUD",
    "LBP","SAR","AED","EGP","TRY","JOD","KWD",
    "QAR","BHD","OMR","IQD","SYP","MAD",
}


def _parse_conversion(text: str) -> dict | None:
    """
    Parse NL currency query into {base, target, amount}.
    Handles Arabic colloquial:
      "حول 100 يورو لليرة"      → EUR 100 → LBP
      "كم تساوي الليرة بالدرهم" → LBP → AED  (amount=1)
      "دولار على ليرة"          → USD → LBP
      "EUR LBP"                  → USD=EUR, target=LBP
    """
    # Extract numeric amount (Arabic & Western digits)
    ar_num = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    amount_match = re.search(r"[\d,\.]+", ar_num)
    amount = float(amount_match.group().replace(",", "")) if amount_match else 1.0

    found: list[tuple[int, str]] = []

    # Check raw ISO codes first
    for iso in _ISO_CODES:
        m = re.search(r"\b" + iso + r"\b", text, re.IGNORECASE)
        if m:
            found.append((m.start(), iso))

    # Check name map (longest names first to avoid partial matches)
    names_sorted = sorted(_CURRENCY_NAMES.keys(), key=len, reverse=True)
    for name in names_sorted:
        pattern = re.sub(r"\s+", r"\\s*", re.escape(name))
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            code = _CURRENCY_NAMES[name]
            # Skip if position already covered by a longer match
            already = any(abs(pos - m.start()) < 3 for pos, _ in found)
            if not already:
                found.append((m.start(), code))

    # Sort by position in text, deduplicate consecutive same code
    found.sort(key=lambda x: x[0])
    seen: list[tuple[int, str]] = []
    for pos, code in found:
        if not seen or seen[-1][1] != code:
            seen.append((pos, code))

    if len(seen) >= 2:
        return {"base": seen[0][1], "target": seen[1][1], "amount": amount}
    if len(seen) == 1:
        # Single currency → show multi-rate with it as base
        code = seen[0][1]
        return {"base": code, "target": None, "amount": amount}
    return None


def _stale_note(lang: str) -> str:
    return "\n\n⚠️ _البيانات الحية غير متاحة — يُعرض آخر سعر معروف_" if lang == "ar" \
        else "\n\n⚠️ _Live data unavailable — showing last known rate_"


def _fmt_rate(rate: float) -> str:
    if rate >= 1000:
        return f"{rate:,.0f}"
    if rate >= 1:
        return f"{rate:,.4f}"
    return f"{rate:,.6f}"


async def _send_pair(message: Message, base: str, target: str,
                     amount: float, lang: str) -> None:
    """Fetch and send a single currency pair card."""
    data = await omega_currency.get_rate(base, target)
    if data.get("error"):
        err = "البيانات غير متوفرة حالياً" if lang == "ar" else "Rate unavailable"
        await message.answer(f"⚠️ {err}")
        return

    rate = data["rate"]
    converted = rate * amount
    rate_str   = _fmt_rate(rate)
    conv_str   = _fmt_rate(converted)

    header = f"💱 *{base} → {target}*"
    body   = f"\n\n  1 {base} = `{rate_str}` {target}"
    if amount != 1.0:
        body += f"\n  {amount:g} {base} = `{conv_str}` {target}"

    if data.get("has_parallel") and data.get("parallel_rate"):
        par = data["parallel_rate"]
        body += f"\n\n  📊 _السوق الموازي:_ `{par:,.0f}` {target}"

    stale = _stale_note(lang) if data.get("stale") else ""
    await message.answer(header + body + stale, parse_mode="Markdown")


_QUICK_PAIRS = [
    # USD base
    ("USD", "LBP"), ("USD", "EUR"), ("USD", "SAR"), ("USD", "AED"),
    # EUR base
    ("EUR", "USD"), ("EUR", "GBP"), ("EUR", "TRY"), ("EUR", "LBP"),
    # other
    ("GBP", "USD"), ("SAR", "USD"), ("USD", "EGP"), ("USD", "TRY"),
]


def _currency_quick_kb() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text=f"{b}→{tgt}", callback_data=f"cur_q:{b}:{tgt}")
        for b, tgt in _QUICK_PAIRS
    ]
    rows = [btns[i:i+4] for i in range(0, len(btns), 4)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("currency"))
async def cmd_currency(message: Message, lang: str = "en") -> None:
    raw = message.text or ""

    # ── /currency command with explicit args ──────────────────────────────────
    if raw.strip().startswith("/currency"):
        parts = raw.split()[1:]
        base   = parts[0].upper() if len(parts) >= 1 else "USD"
        target = parts[1].upper() if len(parts) >= 2 else None
        amount = 1.0
        try:
            amount = float(parts[2]) if len(parts) >= 3 else 1.0
        except ValueError:
            pass
        if target:
            await _send_pair(message, base, target, amount, lang)
        else:
            await _send_multi(message, base, lang)
        return

    # ── Natural language ──────────────────────────────────────────────────────
    parsed = _parse_conversion(raw)
    if parsed:
        if parsed.get("target"):
            await _send_pair(message, parsed["base"], parsed["target"],
                             parsed["amount"], lang)
        else:
            await _send_multi(message, parsed["base"], lang)
    else:
        # Button tap with no specific pair — show prompt + quick-select keyboard
        hint = (
            "💱 *تحويل العملات*\n\n"
            "اكتب مثال:\n"
            "  `100 دولار بيورو`\n"
            "  `USD EUR`\n"
            "  `كم يساوي الدولار بالليرة`\n\n"
            "أو اختر زوجاً سريعاً:"
            if lang == "ar"
            else
            "💱 *Currency Converter*\n\n"
            "Type e.g.:\n"
            "  `100 USD to EUR`\n"
            "  `euro to lira`\n\n"
            "Or pick a quick pair:"
        )
        await message.answer(hint, parse_mode="Markdown", reply_markup=_currency_quick_kb())


async def _send_multi(message: Message, base: str, lang: str) -> None:
    """Send multi-rate overview for a base currency."""
    data = await omega_currency.get_multiple_rates(base)
    lines: list[str] = []
    any_stale = False

    for cur, info in data.items():
        if info.get("error"):
            continue
        rate = info["rate"]
        rate_fmt   = _fmt_rate(rate)
        stale_mark = " ⚠️" if info.get("stale") else ""
        parallel   = ""
        if info.get("has_parallel") and info.get("parallel_rate"):
            parallel = f" _(موازي: {info['parallel_rate']:,.0f})_"
        lines.append(f"  `{cur}` {rate_fmt}{stale_mark}{parallel}")
        if info.get("stale"):
            any_stale = True

    if not lines:
        await message.answer(t("error", lang))
        return

    header = f"💱 *أسعار الصرف — أساس: {base}*\n\n" if lang == "ar" \
        else f"💱 *Exchange Rates — Base: {base}*\n\n"
    text = header + "\n".join(lines)
    if any_stale:
        text += _stale_note(lang)
    await message.answer(text, parse_mode="Markdown")


@router.callback_query(lambda c: c.data and c.data.startswith("cur_q:"))
async def handle_cur_quick_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    base, target = parts[1], parts[2]
    await _send_pair(callback.message, base, target, 1.0, lang)


def register_currency_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/fuel.py"] = r'''
import logging
import httpx
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_fuel import omega_fuel
from config import t, settings
from services.cards import fuel_card

logger = logging.getLogger(__name__)
router = Router(name="fuel")

# BDL official rate fixed at 89,500 LBP/USD since Feb 2023.
# Valid range check: if scraped value is outside 80,000–150,000 it's rejected.
_FALLBACK_RATE = 89500.0  # LBP per 1 USD — BDL official (Feb 2023 onwards)

# Canonical Arabic names for the 4 fuel types shown on the card
_FUEL_KEYS = {
    "98":                                              "بنزين 98",
    "95":                                              "بنزين 95",
    "diesel|ديزل|مازوت|mazout|gasoil|gas oil":         "ديزل",
    "gas|غاز|lpg|butane|gaz":                          "غاز 10kg",
}


_CANONICAL_LB_KEYS = {"بنزين 98", "بنزين 95", "ديزل", "غاز 10kg"}


def _has_canonical_prices(d: dict) -> bool:
    """Return True only when at least 2 canonical Lebanon fuel keys are present."""
    return sum(1 for k in d if k in _CANONICAL_LB_KEYS) >= 2


def _normalize_fuel_keys(prices: dict) -> dict:
    """Map any scraped key names to standard Arabic canonical names."""
    out: dict = {}
    for raw_key, val in prices.items():
        kl = raw_key.lower()
        matched = False
        for patterns_str, canonical in _FUEL_KEYS.items():
            if canonical in out:          # already set by a better match
                continue
            for p in patterns_str.split("|"):
                if p in kl or p in raw_key:
                    out[canonical] = val
                    matched = True
                    break
            if matched:
                break
        if not matched:
            out[raw_key] = val            # keep as-is if no mapping found
    return out


async def _fetch_exchange_rate() -> float:
    """Fetch live USD→LBP rate. Tries 3 sources in order, falls back to BDL official."""
    import re as _re

    # Source 1: ExchangeRate-API (uses EXCHANGE_RATE_KEY)
    key = getattr(settings, "exchange_rate_key", "") or ""
    if key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                url = f"https://v6.exchangerate-api.com/v6/{key}/pair/USD/LBP"
                resp = await client.get(url)
                resp.raise_for_status()
                js = resp.json()
                rate = float(js.get("conversion_rate", 0))
                if 80000 < rate < 150000:
                    logger.debug(f"LBP rate from exchangerate-api: {rate}")
                    return rate
        except Exception as exc:
            logger.debug(f"ExchangeRate-API failed: {exc}")

    # Source 2: lirarate.org (live Lebanese market rate, no key needed)
    try:
        async with httpx.AsyncClient(
            timeout=8.0,
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
        ) as client:
            resp = await client.get("https://lirarate.org/")
            resp.raise_for_status()
            # Look for large numbers like 89,500 or 89500 in the page text
            nums = _re.findall(r'\b(8[0-9][,\s]?\d{3})\b', resp.text)
            for n in nums:
                try:
                    r = float(n.replace(",", "").replace(" ", ""))
                    if 80000 < r < 150000:
                        logger.debug(f"LBP rate from lirarate.org: {r}")
                        return r
                except ValueError:
                    pass
    except Exception as exc:
        logger.debug(f"lirarate.org failed: {exc}")

    # Source 3: Open-source free API (no key)
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get("https://open.er-api.com/v6/latest/USD")
            resp.raise_for_status()
            js = resp.json()
            rate = float(js.get("rates", {}).get("LBP", 0))
            if 80000 < rate < 150000:
                logger.debug(f"LBP rate from open.er-api: {rate}")
                return rate
    except Exception as exc:
        logger.debug(f"open.er-api failed: {exc}")

    logger.info(f"Using BDL fallback rate: {_FALLBACK_RATE}")
    return _FALLBACK_RATE


# ── Country selector ──────────────────────────────────────────────────────────
_FUEL_COUNTRIES = [
    ("🇱🇧 لبنان",      "LB"), ("🇸🇦 السعودية",  "SA"), ("🇦🇪 الإمارات",  "AE"),
    ("🇪🇬 مصر",        "EG"), ("🇰🇼 الكويت",    "KW"), ("🇶🇦 قطر",       "QA"),
    ("🇯🇴 الأردن",     "JO"), ("🇮🇶 العراق",    "IQ"), ("🇩🇿 الجزائر",   "DZ"),
    ("🇲🇦 المغرب",     "MA"), ("🇹🇳 تونس",      "TN"), ("🇹🇷 تركيا",     "TR"),
    ("🇺🇸 USA",        "US"), ("🇩🇪 Germany",   "DE"), ("🇫🇷 France",    "FR"),
    ("🇬🇧 UK",         "GB"), ("🇯🇵 Japan",     "JP"), ("🇮🇳 India",     "IN"),
    ("🇧🇷 Brazil",     "BR"), ("🇷🇺 Russia",    "RU"), ("🇨🇳 China",     "CN"),
]


def _fuel_country_kb(lang: str = "ar") -> InlineKeyboardMarkup:
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    btns = [
        InlineKeyboardButton(text=name, callback_data=f"fuel_c:{code}")
        for name, code in _FUEL_COUNTRIES
    ]
    rows = [btns[i:i+3] for i in range(0, len(btns), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_fuel(send_to: Message, country: str, lang: str) -> None:
    """Core fuel display — shared by command and callback."""
    await send_to.answer(t("fetching", lang))
    try:
        data = await omega_fuel.get_prices(country)
    except Exception as exc:
        logger.error(f"get_prices failed for {country}: {exc}", exc_info=True)
        data = {"error": True, "prices": {}}

    # ── Lebanon: rich visual card ─────────────────────────────────────────
    if country == "LB":
        try:
            from datetime import date as _date
            prices_raw = data.get("prices", {}) if not data.get("error") else {}
            rate = 89500.0
            try:
                rate = await _fetch_exchange_rate()
            except Exception:
                pass
            source_label = "IPT Group"
            ago = "—"

            published_date = data.get("published_date", "")
            scraped_at     = data.get("scraped_at", "")
            if published_date:
                ago = f"تحديث: {published_date}"
            elif scraped_at:
                try:
                    from datetime import datetime as _dt
                    dt = _dt.fromisoformat(scraped_at)
                    _M = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                          "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
                    ago = f"تحديث: {dt.day} {_M[dt.month-1]} {dt.year}"
                except Exception:
                    pass

            lbp_prices = {
                k: v for k, v in prices_raw.items()
                if k != "note"
                and any(c.isdigit() for c in str(v))
                and any(m in str(v) for m in ("ل.ل", "LL", "LBP", "لل"))
            }
            prices_real = _normalize_fuel_keys(lbp_prices)

            if not _has_canonical_prices(prices_real):
                gpp_prices = {k: v for k, v in prices_raw.items()
                              if k != "note" and "USD" in str(v)
                              and any(c.isdigit() for c in str(v))}
                if gpp_prices and rate:
                    import re as _re
                    raw_converted = {}
                    for fuel_name, usd_str in gpp_prices.items():
                        m = _re.search(r"([\d.]+)", usd_str)
                        if m:
                            usd_per_l = float(m.group(1))
                            llp_20l = int(usd_per_l * rate * 20)
                            raw_converted[fuel_name] = f"{llp_20l:,} ل.ل."
                    converted = _normalize_fuel_keys(raw_converted)
                    if _has_canonical_prices(converted):
                        prices_real = converted
                        source_label = "GlobalPetrolPrices"

            if not _has_canonical_prices(prices_real):
                from datetime import date as _d, timedelta as _td
                today = _d.today()
                days_since_thu = (today.weekday() - 3) % 7
                last_thu = today - _td(days=days_since_thu)
                _M = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
                      "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
                last_thu_ar = f"{last_thu.day} {_M[last_thu.month-1]} {last_thu.year}"
                prices_real = {
                    "بنزين 98": "2,431,000 ل.ل.",
                    "بنزين 95": "2,390,000 ل.ل.",
                    "ديزل":     "2,497,000 ل.ل.",
                    "غاز 10kg": "1,751,000 ل.ل.",
                }
                source_label = "IPT Group"
                ago = f"آخر تحديث: {last_thu_ar}"

            card_text = fuel_card(
                prices_llp=prices_real,
                rate=rate,
                lang=lang,
                source=source_label,
                ago=ago,
            )
            try:
                await send_to.answer(card_text, parse_mode="Markdown")
            except Exception:
                await send_to.answer(card_text)
        except Exception as exc:
            logger.error(f"LB fuel display error: {exc}", exc_info=True)
            await send_to.answer(
                "⛽ أسعار لبنان — آخر معروف:\n"
                "بنزين 98: 2,431,000 ل.ل.\n"
                "بنزين 95: 2,390,000 ل.ل.\n"
                "ديزل: 2,497,000 ل.ل.\n"
                "غاز 10kg: 1,751,000 ل.ل."
            )
        return

    # ── Other countries: simple display ──────────────────────────────────
    try:
        if data.get("error"):
            await send_to.answer(t("error", lang))
            return

        name = data.get("country_name_ar", data.get("country_name_en", country))
        text = t("fuel_title_country", lang, country=name) + "\n\n"
        prices = data.get("prices", {})
        if isinstance(prices, dict):
            for fuel_type, price in prices.items():
                if fuel_type != "note":
                    text += f"  🔹 {fuel_type}: {price}\n"
        if data.get("stale"):
            text += (
                "\n⚠️ آخر بيانات معروفة — أبريل 2026"
                if lang == "ar"
                else "\n⚠️ Last known data — April 2026"
            )
        if data.get("note"):
            text += f"\n{t('label_note', lang)}: {data['note']}"
        try:
            await send_to.answer(text, parse_mode="Markdown")
        except Exception:
            await send_to.answer(text)
    except Exception as exc:
        logger.error(f"Fuel display error for {country}: {exc}", exc_info=True)
        await send_to.answer(t("error", lang))


@router.message(Command("fuel"))
async def cmd_fuel(message: Message, lang: str = "en") -> None:
    args = message.text.split()[1:] if message.text else []
    country = None
    if args:
        candidate = args[0].upper()
        if len(candidate) == 2 and candidate.isalpha():
            country = candidate

    if not country:
        prompt = "⛽ *اختر الدولة:*" if lang == "ar" else "⛽ *Select a country:*"
        await message.answer(prompt, parse_mode="Markdown", reply_markup=_fuel_country_kb(lang))
        return

    await _show_fuel(message, country, lang)


@router.callback_query(lambda c: c.data and c.data.startswith("fuel_c:"))
async def handle_fuel_country_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    country = callback.data.split(":", 1)[1].upper()
    await _show_fuel(callback.message, country, lang)


def register_fuel_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/weather.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_weather import omega_weather
from services.cards import weather_card
from config import t

logger = logging.getLogger(__name__)
router = Router(name="weather")


@router.message(Command("weather"))
async def cmd_weather(message: Message, lang: str = "en") -> None:
    city = message.text.replace("/weather", "").strip() if message.text else ""
    if not city:
        city = "Beirut"

    await message.answer(t("fetching", lang))
    try:
        data = await omega_weather.get_weather(city, lang)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        await message.answer(weather_card(data, lang), parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Weather error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_weather_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/football.py"] = r'''
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_football import omega_football, MAJOR_LEAGUES
from config import t

logger = logging.getLogger(__name__)
router = Router(name="football")

_BEIRUT = ZoneInfo("Asia/Beirut")

_MONTHS_AR = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]


def _league_name(code: str, lang: str) -> str:
    """Return the league display name in the user's language."""
    info = MAJOR_LEAGUES.get(code.upper(), {})
    if lang == "ar":
        return info.get("name_ar") or info.get("name") or code
    return info.get("name") or info.get("name_ar") or code


# ── date helpers ───────────────────────────────────────────────────────────────

def _fmt_local(date_utc: str) -> str:
    try:
        dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00"))
        return dt.astimezone(_BEIRUT).strftime("%H:%M")
    except Exception:
        return "—"


def _fmt_full(date_utc: str, lang: str = "ar") -> str:
    try:
        dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00")).astimezone(_BEIRUT)
        if lang == "ar":
            return f"{dt.day} {_MONTHS_AR[dt.month - 1]}  {dt.strftime('%H:%M')}"
        return dt.strftime("%d %b  %H:%M")
    except Exception:
        return "—"


def _fmt_short_date(date_utc: str) -> str:
    try:
        dt = datetime.fromisoformat(date_utc.replace("Z", "+00:00")).astimezone(_BEIRUT)
        return f"{dt.day:02d}/{dt.month:02d}"
    except Exception:
        return "—"


# ── match card helpers ─────────────────────────────────────────────────────────

def _score_display(f: dict) -> str:
    if f["status"] == "NS":
        return "🆚"
    h = f.get("home_score")
    a = f.get("away_score")
    return f"‹ {h if h is not None else '?'} - {a if a is not None else '?'} ›"


def _status_line(f: dict, lang: str = "ar") -> str:
    s = f.get("status", "NS")
    el = f.get("status_elapsed")
    if lang == "ar":
        if s == "NS":              return "🗓️ موعد"
        if s in ("1H", "2H"):     return f"🔴 مباشر '{el}"
        if s == "HT":             return "⏸️ استراحة"
        if s == "FT":             return "🏁 انتهت"
        if s == "ET":             return "⚡ وقت إضافي"
        if s == "PEN":            return "🎯 ضربات ترجيح"
    else:
        if s == "NS":              return "🗓️ Scheduled"
        if s in ("1H", "2H"):     return f"🔴 Live '{el}"
        if s == "HT":             return "⏸️ Half Time"
        if s == "FT":             return "🏁 Finished"
        if s == "ET":             return "⚡ Extra Time"
        if s == "PEN":            return "🎯 Penalties"
    return s


def _card(f: dict, lang: str = "ar") -> str:
    dt     = _fmt_full(f.get("date_utc", ""), lang)
    score  = _score_display(f)
    status = _status_line(f, lang)
    venue  = f.get("venue") or "—"
    return (
        f"⚽ *{f['league_ar']}*\n"
        f"━━━━━━━━━━━━\n"
        f"  {f['home']}\n"
        f"  {score}\n"
        f"  {f['away']}\n"
        f"━━━━━━━━━━━━\n"
        f"📅 {dt}\n"
        f"{status}\n"
        f"🏟️ {venue}"
    )


def _matchday_card(fixtures: list, league_name: str, lang: str = "ar") -> str:
    """Format all matches as a single matchday overview — like football sites."""
    SEP  = "──────────────"
    live = [f for f in fixtures if f.get("status") in ("1H", "2H", "HT", "ET", "PEN")]
    done = [f for f in fixtures if f.get("status") == "FT"]
    ns   = [f for f in fixtures if f.get("status") == "NS"]

    lines = [f"⚽ *{league_name}*", SEP]

    if live:
        lbl = "🔴 *مباشر*" if lang == "ar" else "🔴 *Live*"
        lines.append(lbl)
        for f in live:
            el   = f.get("status_elapsed", "")
            tag  = f"  `{el}'`" if el else ""
            h, a = f.get("home_score", 0), f.get("away_score", 0)
            lines.append(f"  {f['home']}  `{h} – {a}`  {f['away']}{tag}")
        lines.append(SEP)

    if done:
        lbl = "🏁 *انتهت*" if lang == "ar" else "🏁 *Finished*"
        lines.append(lbl)
        for f in done:
            h, a = f.get("home_score", "?"), f.get("away_score", "?")
            lines.append(f"  {f['home']}  `{h} – {a}`  {f['away']}")
        lines.append(SEP)

    if ns:
        lbl = "🗓️ *المواعيد*" if lang == "ar" else "🗓️ *Scheduled*"
        lines.append(lbl)
        for f in ns:
            time_s = _fmt_local(f.get("date_utc", ""))
            date_s = _fmt_short_date(f.get("date_utc", ""))
            lines.append(f"  `{date_s}  {time_s}`  {f['home']}  🆚  {f['away']}")

    if not (live or done or ns):
        lines.append("لا توجد مباريات متاحة" if lang == "ar" else "No matches available")

    return "\n".join(lines)


def _card_kb(f: dict) -> InlineKeyboardMarkup | None:
    fid = f.get("fixture_id")
    if fid and f.get("status") not in ("NS", "TBD"):
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📋 أحداث | Events", callback_data=f"fb_ev:{fid}")
        ]])
    return None


def _fmt_events(events: list, lang: str = "ar") -> str:
    if not events:
        return "لا توجد أحداث" if lang == "ar" else "No events recorded"
    lines: list[str] = []
    for ev in events:
        ev_type = ev.get("type", "")
        detail  = ev.get("detail", "")
        elapsed = ev.get("elapsed", "?")
        extra   = ev.get("extra")
        player  = ev.get("player", "")
        team    = ev.get("team", "")
        time_str = f"`{elapsed}+{extra}'`" if extra else f"`{elapsed}'`"

        if ev_type == "Goal":
            icon = "🔙" if "Own Goal" in detail else ("🎯" if "Penalty" in detail else "⚽")
        elif ev_type == "Card":
            icon = "🟥" if "Red" in detail else "🟨"
        elif ev_type in ("subst", "Subst"):
            icon = "🔄"
        else:
            icon = "📌"

        line = f"  {icon} {time_str} *{player}*"
        if team:
            line += f"  ({team})"
        lines.append(line)

    header = "📋 *أحداث المباراة*" if lang == "ar" else "📋 *Match Events*"
    return header + "\n\n" + "\n".join(lines)


# ── keyboards ──────────────────────────────────────────────────────────────────

def _league_kb(lang: str = "ar") -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text=_league_name(code, lang), callback_data=f"fb:{code}")
        for code in MAJOR_LEAGUES
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    live_lbl = "🔴 نتائج مباشرة" if lang == "ar" else "🔴 Live Now"
    rows.append([InlineKeyboardButton(text=live_lbl, callback_data="fb:live")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _matchday_kb(league_code: str, lang: str = "ar") -> InlineKeyboardMarkup:
    lc          = league_code.lower()
    team_lbl    = "🔍 اختر فريقاً" if lang == "ar" else "🔍 Choose Team"
    live_lbl    = "🔴 مباشر"       if lang == "ar" else "🔴 Live Now"
    refresh_lbl = "🔄 تحديث"       if lang == "ar" else "🔄 Refresh"
    back_lbl    = "🔙 الدوريات"    if lang == "ar" else "🔙 Leagues"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=team_lbl,    callback_data=f"fb_teams:{lc}")],
        [InlineKeyboardButton(text=live_lbl,    callback_data="fb:live"),
         InlineKeyboardButton(text=refresh_lbl, callback_data=f"fb:{lc}")],
        [InlineKeyboardButton(text=back_lbl,    callback_data="fb:menu")],
    ])


def _team_kb(teams: list, league_code: str, lang: str = "ar") -> InlineKeyboardMarkup:
    """Index-based callback — stays within 64-byte limit."""
    btns = [
        InlineKeyboardButton(
            text=(tm.get("name_ar") or tm["name"]) if lang == "ar" else tm["name"],
            callback_data=f"fb_t:{i}:{league_code}",
        )
        for i, tm in enumerate(teams[:24])
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    back_lbl = "🔙 المباريات" if lang == "ar" else "🔙 Matches"
    rows.append([InlineKeyboardButton(text=back_lbl, callback_data=f"fb:{league_code.lower()}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── team schedule card ─────────────────────────────────────────────────────────

def _result_emoji(f: dict, team_name: str) -> str:
    if f.get("status") != "FT":
        return "⬜"
    h, a = f.get("home_score"), f.get("away_score")
    if h is None or a is None:
        return "⬜"
    is_home = f.get("home", "") == team_name
    my_g = h if is_home else a
    op_g = a if is_home else h
    if my_g > op_g:   return "🟢"
    if my_g == op_g:  return "🟡"
    return "🔴"


def _team_schedule_card(sched: dict, team_name: str, league_name: str, lang: str = "ar") -> str:
    SEP = "━━━━━━━━━━━━"
    lines = [f"⚽ *{league_name}*", f"🏆 *{team_name}*", SEP]

    if sched.get("live"):
        lbl = "🔴 *مباشر الآن*" if lang == "ar" else "🔴 *Live Now*"
        lines.append(lbl)
        for f in sched["live"]:
            el = f.get("status_elapsed", "")
            el_str = f"  `{el}'`" if el else ""
            h_s = f.get("home_score", 0)
            a_s = f.get("away_score", 0)
            lines.append(f"  *{f['home']}*  {h_s} — {a_s}  *{f['away']}*{el_str}")
        lines.append(SEP)

    if sched.get("past"):
        lbl = "📅 *الأخيرة*" if lang == "ar" else "📅 *Recent*"
        lines.append(lbl)
        for f in sched["past"]:
            res = _result_emoji(f, team_name)
            h_s = f.get("home_score", "?")
            a_s = f.get("away_score", "?")
            d   = _fmt_short_date(f.get("date_utc", ""))
            lines.append(f"{res}  `{d}`  {f['home']}  {h_s}–{a_s}  {f['away']}")
        lines.append(SEP)

    if sched.get("upcoming"):
        lbl = "📆 *القادمة*" if lang == "ar" else "📆 *Upcoming*"
        lines.append(lbl)
        for f in sched["upcoming"]:
            dt = _fmt_full(f.get("date_utc", ""), lang)
            lines.append(f"⬜  {f['home']}  🆚  {f['away']}")
            lines.append(f"     `{dt}`")

    if not any(sched.get(k) for k in ("past", "live", "upcoming")):
        no_data = "لا توجد بيانات متاحة" if lang == "ar" else "No data available"
        lines.append(no_data)

    return "\n".join(lines)


# ── internal send helpers ──────────────────────────────────────────────────────

def _today(fixtures: list) -> list:
    today = datetime.now(timezone.utc).date().isoformat()
    return [f for f in fixtures if f.get("date_utc", "").startswith(today)]


def _nearest(fixtures: list) -> list:
    upcoming = sorted(
        [f for f in fixtures if f.get("status") == "NS"],
        key=lambda f: f.get("date_utc", ""),
    )
    if upcoming:
        return upcoming[:8]
    return sorted(
        [f for f in fixtures if f.get("status") == "FT"],
        key=lambda f: f.get("date_utc", ""),
        reverse=True,
    )[:8]


async def _send_fixtures(target, league_code: str, lang: str) -> None:
    send = target.answer if isinstance(target, Message) else target.message.answer
    try:
        data = await omega_football.get_fixtures(league_code)
    except Exception as exc:
        logger.error(f"get_fixtures error {league_code}: {exc}", exc_info=True)
        data = {"error": True}
    if isinstance(data, dict) and data.get("error"):
        no_data = "لا تتوفر بيانات حالياً — اضغط تحديث" if lang == "ar" else "No data available right now — press Refresh"
        try:
            await send(no_data, reply_markup=_matchday_kb(league_code.upper(), lang))
        except Exception:
            await send(no_data)
        return
    selection = _today(data) or _nearest(data)
    if not selection:
        try:
            await send(t("fb_no_live", lang), reply_markup=_matchday_kb(league_code.upper(), lang))
        except Exception:
            await send(t("fb_no_live", lang))
        return
    league_name = _league_name(league_code, lang)
    card = _matchday_card(selection[:12], league_name, lang)
    kb   = _matchday_kb(league_code.upper(), lang)
    try:
        await send(card, parse_mode="Markdown", reply_markup=kb)
    except Exception:
        await send(card, reply_markup=kb)


async def _send_live(target, lang: str) -> None:
    send = target.answer if isinstance(target, Message) else target.message.answer
    try:
        data = await omega_football.get_live()
    except Exception as exc:
        logger.error(f"get_live error: {exc}", exc_info=True)
        await send(t("fb_no_live", lang))
        return
    if isinstance(data, dict) and data.get("error"):
        await send(t("fb_no_live", lang))
        return
    if not data:
        await send(t("fb_no_live", lang))
        return
    by_league: dict[str, list] = {}
    for f in data[:20]:
        if lang == "ar":
            key = f.get("league_ar") or f.get("league", "Football")
        else:
            key = f.get("league") or f.get("league_ar", "Football")
        by_league.setdefault(key, []).append(f)
    for league_name, matches in by_league.items():
        card = _matchday_card(matches, league_name, lang)
        try:
            await send(card, parse_mode="Markdown")
        except Exception:
            await send(card)


# ── command handler ────────────────────────────────────────────────────────────

@router.message(Command("football"))
async def cmd_football(message: Message, lang: str = "en") -> None:
    raw = (message.text or "").strip()
    for prefix in ("/football", "⚽ كرة قدم", "⚽ Football", "⚽"):
        if raw.upper().startswith(prefix.upper()):
            raw = raw[len(prefix):].strip()
            break
    arg = raw.upper()

    if not arg:
        await message.answer(
            t("fb_choose_league", lang), parse_mode="Markdown",
            reply_markup=_league_kb(lang),
        )
        return
    if arg == "LIVE":
        await _send_live(message, lang)
    elif arg in MAJOR_LEAGUES:
        await _send_fixtures(message, arg, lang)
    else:
        await message.answer(
            t("fb_choose_league", lang), parse_mode="Markdown",
            reply_markup=_league_kb(lang),
        )


# ── callback: league / live / back ────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb:"))
async def handle_fb_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    parts  = callback.data.split(":")
    action = parts[1] if len(parts) > 1 else ""

    if action == "live":
        await _send_live(callback, lang)
        return

    if action == "menu":
        try:
            await callback.message.edit_text(
                t("fb_choose_league", lang),
                parse_mode="Markdown",
                reply_markup=_league_kb(lang),
            )
        except Exception:
            await callback.message.answer(
                t("fb_choose_league", lang),
                parse_mode="Markdown",
                reply_markup=_league_kb(lang),
            )
        return

    league_code = action.upper()
    if league_code not in MAJOR_LEAGUES:
        return

    await _send_fixtures(callback, league_code, lang)


# ── callback: team list ───────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb_teams:"))
async def handle_fb_teams_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    league_code = callback.data.split(":", 1)[1].upper()
    logger.info(f"DEBUG fb_teams: raw='{callback.data}' → league_code='{league_code}' lang='{lang}'")
    league_name = _league_name(league_code, lang)

    teams = []
    try:
        teams = await omega_football.get_league_teams(league_code)
    except Exception as exc:
        logger.error(f"get_league_teams error {league_code}: {exc}", exc_info=True)
    logger.info(f"DEBUG teams result: count={len(teams)} first={teams[:2] if teams else 'EMPTY'}")

    if not teams:
        from api_clients.omega_football import _FALLBACK_TEAMS
        fb = _FALLBACK_TEAMS.get(league_code, [])
        teams = [{"id": i, "name": n} for i, n in enumerate(sorted(fb))]

    if not teams:
        no_teams = "لا توجد فرق متاحة حالياً" if lang == "ar" else "No teams available right now"
        await callback.message.answer(no_teams)
        return

    choose_lbl = "🏟️ اختر الفريق:" if lang == "ar" else "🏟️ Choose a team:"
    text = f"⚽ *{league_name}*\n\n{choose_lbl}"
    logger.info(f"DEBUG before keyboard: teams={len(teams)} league={league_code} lang={lang}")
    kb = _team_kb(teams, league_code, lang)
    logger.info(f"DEBUG kb built: rows={len(kb.inline_keyboard)} first_row_btns={len(kb.inline_keyboard[0]) if kb.inline_keyboard else 0}")
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception as exc:
        logger.warning(f"DEBUG edit_text failed: {exc}")
        try:
            await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as exc2:
            logger.error(f"DEBUG answer failed: {exc2}", exc_info=True)


# ── callback: team schedule ───────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb_t:"))
async def handle_fb_team_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    parts = callback.data.split(":")
    if len(parts) < 3:
        return
    try:
        team_idx    = int(parts[1])
        league_code = parts[2].upper()
    except (ValueError, IndexError):
        return

    league_name = _league_name(league_code, lang)

    teams = []
    try:
        teams = await omega_football.get_league_teams(league_code)
    except Exception as exc:
        logger.error(f"get_league_teams error {league_code}: {exc}", exc_info=True)

    if not teams:
        from api_clients.omega_football import _FALLBACK_TEAMS
        fb = _FALLBACK_TEAMS.get(league_code, [])
        teams = [{"id": i, "name": n} for i, n in enumerate(sorted(fb))]

    if team_idx >= len(teams):
        await callback.message.answer(t("error", lang))
        return
    team_name = teams[team_idx]["name"]

    try:
        sched = await omega_football.get_team_schedule_by_name(team_name, league_code)
    except Exception as exc:
        logger.error(f"get_team_schedule_by_name error: {exc}", exc_info=True)
        await callback.message.answer(t("error", lang))
        return
    card  = _team_schedule_card(sched, team_name, league_name, lang)

    back_lbl   = "🔙 الفرق"  if lang == "ar" else "🔙 Teams"
    reload_lbl = "🔄 تحديث"  if lang == "ar" else "🔄 Refresh"
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=back_lbl,   callback_data=f"fb_teams:{league_code.lower()}"),
        InlineKeyboardButton(text=reload_lbl, callback_data=f"fb_t:{team_idx}:{league_code}"),
    ]])
    try:
        await callback.message.answer(card, parse_mode="Markdown", reply_markup=back_kb)
    except Exception:
        await callback.message.answer(card, reply_markup=back_kb)


# ── callback: match events ─────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("fb_ev:"))
async def handle_fb_events_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    try:
        fixture_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        return
    try:
        events = await omega_football.get_events(fixture_id)
    except Exception as exc:
        logger.error(f"get_events error: {exc}", exc_info=True)
        await callback.message.answer(t("error", lang))
        return
    if isinstance(events, dict) and events.get("error"):
        await callback.message.answer(t("error", lang))
        return
    text = _fmt_events(events if isinstance(events, list) else [], lang)
    try:
        await callback.message.answer(text, parse_mode="Markdown")
    except Exception:
        await callback.message.answer(text)


def register_football_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/movies.py"] = r'''
import logging
import re

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from api_clients.omega_movies import omega_movies
from config import t

logger = logging.getLogger(__name__)
router = Router(name="movies")

_YEAR_RE = re.compile(r"\b(19[0-9]{2}|20[0-9]{2})\b")

# Genre list: (tmdb_id, ar_label, en_label)
_GENRES = [
    (28,    "🎬 أكشن",       "🎬 Action"),
    (35,    "😂 كوميدي",     "😂 Comedy"),
    (18,    "🎭 دراما",      "🎭 Drama"),
    (27,    "👻 رعب",        "👻 Horror"),
    (10749, "❤️ رومانسي",   "❤️ Romance"),
    (878,   "🚀 خيال علمي",  "🚀 Sci-Fi"),
    (53,    "🔍 إثارة",      "🔍 Thriller"),
    (16,    "🎨 أنيمي",      "🎨 Animation"),
    (80,    "🔫 جريمة",      "🔫 Crime"),
    (12,    "🌍 مغامرة",     "🌍 Adventure"),
]


def _genre_kb(lang: str) -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(
            text=(ar if lang == "ar" else en),
            callback_data=f"mv_g:{gid}",
        )
        for gid, ar, en in _GENRES
    ]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _extract_year(text: str) -> tuple:
    m = _YEAR_RE.search(text)
    if m:
        return _YEAR_RE.sub("", text).strip(), int(m.group(1))
    return text, None


def _item_year(item: dict) -> int | None:
    rd = item.get("release_date", "")
    try:
        return int(rd[:4]) if rd else None
    except ValueError:
        return None


def _caption(item: dict) -> str:
    """Clean text-only card — no poster."""
    title = item.get("title", "")
    rd = item.get("release_date", "")
    year = rd[:4] if rd else "?"
    vote = item.get("vote_average", 0)
    genres = item.get("genres", [])
    genres_str = " · ".join(genres[:2]) if genres else "—"
    overview = (item.get("overview") or "")
    preview = overview[:180] + ("..." if len(overview) > 180 else "")
    return (
        f"🎬 *{title}* `({year})`\n"
        f"⭐ `{vote}/10`  ·  🎭 {genres_str}\n"
        f"📝 {preview}"
    )


async def _send_card(msg: Message, item: dict, lang: str) -> None:
    cap = _caption(item)
    await msg.answer(cap, parse_mode="Markdown")


@router.message(Command("movie"))
async def cmd_movie(message: Message, lang: str = "en") -> None:
    raw = message.text or ""
    for prefix in ("/movie", "🎬 أفلام", "🎬 Movies", "🎬"):
        if raw.lower().startswith(prefix.lower()):
            raw = raw[len(prefix):].strip()
            break

    # No query → show genre selector
    if not raw:
        prompt = "🎬 *اختر النوع أو ابحث باسم الفيلم:*" if lang == "ar" \
            else "🎬 *Pick a genre or search by name:*"
        await message.answer(prompt, parse_mode="Markdown", reply_markup=_genre_kb(lang))
        return

    query, requested_year = _extract_year(raw)
    if not query:
        query = raw

    try:
        data = await omega_movies.search(query)
        if data.get("error") or not data.get("results"):
            await message.answer(t("not_found", lang))
            return

        results = data["results"]
        if requested_year is not None:
            filtered = [r for r in results if _item_year(r) == requested_year]
            if not filtered:
                no_result = (
                    f"❌ لا توجد نتائج في {requested_year}"
                    if lang == "ar"
                    else f"❌ No results found for {requested_year}"
                )
                await message.answer(no_result)
                return
            results = filtered

        for item in results[:3]:
            await _send_card(message, item, lang)

    except Exception as exc:
        logger.error(f"Movie error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


@router.callback_query(lambda c: c.data and c.data.startswith("mv_g:"))
async def handle_genre_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer("⏳")
    try:
        genre_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        return

    data = await omega_movies.get_by_genre(genre_id, lang=lang)
    if data.get("error") or not data.get("results"):
        await callback.message.answer(t("not_found", lang))
        return

    for item in data["results"][:5]:
        await _send_card(callback.message, item, lang)


@router.callback_query(lambda c: c.data and c.data.startswith("mv:"))
async def handle_mv_cb(callback: CallbackQuery, lang: str = "en") -> None:
    parts = callback.data.split(":")
    await callback.answer()
    if parts[1] != "detail" or len(parts) < 4:
        return
    try:
        tmdb_id, media_type = int(parts[2]), parts[3]
    except (ValueError, IndexError):
        return

    data = await omega_movies.get_details(tmdb_id, media_type)
    if data.get("error"):
        await callback.message.answer(t("error", lang))
        return

    title = data.get("title", "")
    rd = data.get("release_date", "")
    year = rd[:4] if rd else "?"
    vote = data.get("vote_average", 0)
    genres = " · ".join(data.get("genres", [])[:3])
    overview = (data.get("overview") or "")[:200]

    text = (
        f"🎬 *{title}* `({year})`\n"
        f"⭐ `{vote}/10`  ·  🎭 {genres}\n"
        f"📅 {rd}"
    )
    if data.get("runtime"):
        text += f"  ·  ⏱ {data['runtime']} min"
    if data.get("tagline"):
        text += f"\n\n_{data['tagline']}_"
    if data.get("director"):
        text += f"\n\n🎬 {t('label_director', lang)}: {data['director']}"
    if data.get("cast"):
        names = ", ".join(c["name"] for c in data["cast"][:4])
        text += f"\n🌟 {t('label_cast', lang)}: {names}"
    if overview:
        text += f"\n\n📝 {overview}"
    if data.get("trailer_url"):
        text += f"\n\n🎥 [Trailer]({data['trailer_url']})"

    await callback.message.answer(text, parse_mode="Markdown")


def register_movies_handlers(dp) -> None:
    dp.include_router(router)
'''



FILES["handlers/ai_chat.py"] = r'''
import logging
import re
import time
import urllib.parse
from typing import Optional
from collections import defaultdict
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

# ── Per-user conversation memory (in-process, max 10 messages, 30-min TTL) ──
_USER_HISTORY: dict = defaultdict(list)
_MAX_HIST = 10
_HISTORY_TTL = 1800  # 30 minutes in seconds

def _history_prune(uid: int) -> None:
    """Drop entries older than 30 min and reset history if all entries expired."""
    cutoff = time.time() - _HISTORY_TTL
    _USER_HISTORY[uid] = [m for m in _USER_HISTORY[uid] if m.get("ts", 0) > cutoff]

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
            from handlers.downloader import _pending_urls, _format_kb
            _pending_urls[message.from_user.id] = url
            prompt = "🎬 اختر صيغة التحميل:" if lang == "ar" else "🎬 Choose download format:"
            await message.answer(prompt, reply_markup=_format_kb(lang))
        else:
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
            if not data.get("error"):
                text = f"🌤 *{data.get('city', city)}*\n\n"
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

        # Build query with conversation history for context
        history_text = _history_get(user_id)
        query_with_ctx = f"{history_text}\nUser: {query}" if history_text else query

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

        await message.answer(text, parse_mode="Markdown")

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


def register_ai_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/stocks.py"] = r'''
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_stocks import omega_stocks
from services.cards import stock_card
from config import t

logger = logging.getLogger(__name__)
router = Router(name="stocks")


@router.message(Command("stock"))
async def cmd_stock(message: Message, lang: str = "en") -> None:
    query = message.text.replace("/stock", "", 1).strip() if message.text else ""
    if not query:
        hint = "📈 أرسل اسم الشركة أو رمز السهم\nمثال: /stock ابل  أو  /stock AAPL" if lang == "ar" \
            else "📈 Send a company name or ticker\nExample: /stock Apple  or  /stock AAPL"
        await message.answer(hint)
        return

    try:
        data = await omega_stocks.get_quote(query)
        if data.get("error"):
            msg = f"❌ البيانات غير متوفرة حالياً من المصادر الحية\nالرمز: `{query}`" if lang == "ar" \
                else f"❌ No live data available for `{query}`"
            await message.answer(msg, parse_mode="Markdown")
            return
        await message.answer(stock_card(data, lang), parse_mode="Markdown")
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
from services.cards import crypto_card
from config import t

logger = logging.getLogger(__name__)
router = Router(name="crypto")


@router.message(Command("crypto"))
async def cmd_crypto(message: Message, lang: str = "en") -> None:
    raw = message.text or ""
    for prefix in ("/crypto", "₿ كريبتو", "₿ Crypto", "₿"):
        if raw.lower().startswith(prefix.lower()):
            raw = raw[len(prefix):].strip()
            break
    coin = raw.lower()
    if not coin:
        # Show top 10 as a compact list card
        data = await omega_crypto.get_top_coins(10)
        if data.get("error"):
            await message.answer(t("error", lang))
            return
        sep = "━━━━━━━━━━━━━━"
        title = "₿ *أفضل 10 عملات رقمية*" if lang == "ar" else "₿ *Top 10 Crypto*"
        lines = [title, sep]
        for c in data["coins"]:
            emoji = "📈" if (c.get("change_24h") or 0) >= 0 else "📉"
            lines.append(f"*#{c['rank']}* {c['symbol']} — *${c['price']:,.2f}* {emoji} {c.get('change_24h', 0):+.1f}%")
        await message.answer("\n".join(lines), parse_mode="Markdown")
        return

    await message.answer(t("fetching", lang))
    try:
        data = await omega_crypto.get_price(coin)
        if data.get("error"):
            await message.answer(t("not_found", lang))
            return
        await message.answer(crypto_card(data, lang), parse_mode="Markdown")
    except Exception as exc:
        logger.error(f"Crypto error: {exc}", exc_info=True)
        await message.answer(t("error", lang))


def register_crypto_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/news.py"] = r'''
import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from api_clients.omega_news import omega_news
from config import t

logger = logging.getLogger(__name__)
router = Router(name="news")


def _time_ago(ts: str) -> str:
    if not ts:
        return ""
    fmts = [
        "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
    ]
    dt = None
    for fmt in fmts:
        try:
            dt = datetime.strptime(ts, fmt)
            break
        except ValueError:
            continue
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    mins = int(delta.total_seconds() / 60)
    if mins < 60:
        return f"{mins}m"
    hours = mins // 60
    if hours < 24:
        return f"{hours}h"
    return f"{hours // 24}d"


def _card(article: dict, lang: str) -> str:
    rtl = "\u200f" if lang == "ar" else ""
    title = article.get("title", "").strip()
    desc = (article.get("description", "") or "").strip()
    source = (article.get("source", "") or "").strip() or "—"
    url = article.get("url", "")
    ago = _time_ago(article.get("published_at", ""))
    desc_short = desc[:200] + ("..." if len(desc) > 200 else "")
    read_lbl = "📖 اقرأ المزيد" if lang == "ar" else "📖 Read more"
    parts = [f"{rtl}📰 *{title}*", ""]
    if desc_short:
        parts.append(f"{rtl}{desc_short}")
        parts.append("")
    meta = f"{rtl}📍 {source}"
    if ago:
        meta += f"  |  🕐 {ago}"
    parts.append(meta)
    if url:
        parts.append(f"{rtl}[{read_lbl}]({url})")
    return "\n".join(parts)


@router.message(Command("news"))
async def cmd_news(message: Message, lang: str = "en") -> None:
    raw = message.text or ""
    for prefix in ("/news", "📰 أخبار", "📰 News", "📰"):
        if raw.lower().startswith(prefix.lower()):
            raw = raw[len(prefix):].strip()
            break
    query = raw
    try:
        if query:
            data = await omega_news.search_news(query, lang=lang)
        else:
            data = await omega_news.get_headlines(lang=lang)

        if data.get("error") or not data.get("articles"):
            await message.answer(t("not_found", lang))
            return

        articles = data["articles"][:5]
        window   = data.get("window_hours")

        # Header note when we widened the search window to 72 h
        if window == 72 and query:
            note = f"⏱ _لم أجد نتائج للـ 24 ساعة الماضية — عرض آخر 72 ساعة_" if lang == "ar" \
                else f"⏱ _No results in last 24h — showing last 72h_"
            await message.answer(note, parse_mode="Markdown")

        for article in articles:
            card = _card(article, lang)
            if not card.strip():
                continue
            try:
                await message.answer(card, parse_mode="Markdown", disable_web_page_preview=False)
            except Exception as exc:
                logger.warning(f"News card send error: {exc}")

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
            text = f"✈️ *{query}*\n\n"
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
            text = f"✈️ *{data['callsign']}*\n\n"
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

FILES["handlers/downloader.py"] = r'''
import logging
import asyncio
import re
from typing import Optional

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command

from config import t

logger = logging.getLogger(__name__)
router = Router(name="downloader")

_SUPPORTED_DOMAINS = (
    "youtube.com", "youtu.be",
    "tiktok.com", "vm.tiktok.com",
    "instagram.com", "instagr.am",
    "twitter.com", "x.com",
    "facebook.com", "fb.watch",
    "vimeo.com",
    "reddit.com", "v.redd.it",
)

_pending_urls: dict[int, str] = {}


def _is_media_url(text: str) -> bool:
    text = (text or "").strip().lower()
    return text.startswith("http") and any(d in text for d in _SUPPORTED_DOMAINS)


def _format_kb(lang: str) -> InlineKeyboardMarkup:
    if lang == "ar":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📹 جودة عالية", callback_data="dl:high"),
                InlineKeyboardButton(text="📱 جودة منخفضة", callback_data="dl:low"),
            ],
            [InlineKeyboardButton(text="🎵 صوت فقط", callback_data="dl:mp3")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📹 High Quality", callback_data="dl:high"),
            InlineKeyboardButton(text="📱 Low Quality", callback_data="dl:low"),
        ],
        [InlineKeyboardButton(text="🎵 Audio Only", callback_data="dl:mp3")],
    ])


def _fmt_duration(secs: int) -> str:
    if not secs:
        return ""
    m, s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _extract_direct_url(url: str, fmt: str) -> dict:
    """Use yt-dlp info extraction (no download) to get the direct CDN stream URL."""
    import yt_dlp

    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }
    if fmt == "mp3":
        opts["format"] = "bestaudio/best"
    elif fmt == "low":
        opts["format"] = "bestvideo[height<=480]+bestaudio/best[height<=480]/worst"
    else:
        opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    direct = info.get("url", "")
    if not direct:
        fmts = info.get("formats") or []
        if fmts:
            direct = fmts[-1].get("url", "")

    return {
        "title": info.get("title", ""),
        "duration": info.get("duration", 0),
        "direct_url": direct,
        "ext": info.get("ext", "mp4"),
        "is_youtube": "youtube" in url or "youtu.be" in url,
    }


@router.message(Command("download"))
async def cmd_download(message: Message, lang: str = "en") -> None:
    hint = (
        "📥 أرسل رابطاً من يوتيوب أو تيك توك أو إنستغرام..."
        if lang == "ar"
        else "📥 Send a YouTube, TikTok, or Instagram link to download it."
    )
    await message.answer(hint)


@router.message(F.text.func(_is_media_url))
async def handle_media_url(message: Message, lang: str = "en") -> None:
    url = (message.text or "").strip()
    _pending_urls[message.from_user.id] = url
    prompt = "🎬 اختر الجودة:" if lang == "ar" else "🎬 Choose quality:"
    await message.answer(prompt, reply_markup=_format_kb(lang))


@router.callback_query(lambda c: c.data and c.data.startswith("dl:"))
async def handle_dl_cb(callback: CallbackQuery, lang: str = "en") -> None:
    await callback.answer()
    user_id = callback.from_user.id
    url = _pending_urls.get(user_id)
    if not url:
        no_url = (
            "❌ لم يُعثر على رابط. أرسل الرابط مجدداً."
            if lang == "ar"
            else "❌ No URL found. Please send the link again."
        )
        await callback.message.answer(no_url)
        return

    fmt = callback.data.split(":")[1]
    status_msg = await callback.message.answer(
        "⏳ جارٍ استخراج الرابط..." if lang == "ar" else "⏳ Extracting link..."
    )

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _extract_direct_url, url, fmt)

        direct = data["direct_url"]
        title = data["title"] or "—"
        dur = _fmt_duration(data["duration"])

        if direct:
            dur_line = f"\n⏱ {dur}" if dur else ""
            if lang == "ar":
                text = (
                    f"🎬 *{title}*{dur_line}\n\n"
                    f"🔗 [افتح / حمّل الرابط المباشر]({direct})\n\n"
                    f"_⚠️ الرابط مؤقت — افتحه في المتصفح للتحميل_"
                )
            else:
                text = (
                    f"🎬 *{title}*{dur_line}\n\n"
                    f"🔗 [Open / Download Direct Link]({direct})\n\n"
                    f"_⚠️ Link is temporary — open in browser to save_"
                )
        else:
            if lang == "ar":
                text = (
                    f"🎬 *{title}*\n\n"
                    f"⚠️ تعذّر استخراج رابط مباشر.\n"
                    f"افتح الرابط الأصلي في متصفحك:\n{url}"
                )
            else:
                text = (
                    f"🎬 *{title}*\n\n"
                    f"⚠️ Could not extract a direct link.\n"
                    f"Open the original link in your browser:\n{url}"
                )

        await status_msg.edit_text(text, parse_mode="Markdown")
        _pending_urls.pop(user_id, None)

    except Exception as exc:
        logger.error(f"URL extraction error for {url!r}: {exc}", exc_info=True)
        if lang == "ar":
            fallback = (
                f"⚠️ تعذّر معالجة الرابط تلقائياً.\n"
                f"يمكنك استخدام الرابط الأصلي مع أداة تحميل خارجية:\n{url}"
            )
        else:
            fallback = (
                f"⚠️ Could not process this link automatically.\n"
                f"Use the original link with an external downloader:\n{url}"
            )
        try:
            await status_msg.edit_text(fallback)
        except Exception:
            pass


def register_downloader_handlers(dp) -> None:
    dp.include_router(router)
'''

FILES["handlers/transcriber.py"] = r'''
import logging
import os
import asyncio
import tempfile
import shutil
import subprocess
from typing import Optional

import httpx
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import t, settings

logger = logging.getLogger(__name__)
router = Router(name="transcriber")

_GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
_GROQ_MODEL = "whisper-large-v3"
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.0-flash:generateContent"
)
_SUMMARY_THRESHOLD = 500


async def _transcribe(audio_path: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        with open(audio_path, "rb") as fh:
            resp = await client.post(
                _GROQ_STT_URL,
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                files={"file": (os.path.basename(audio_path), fh, "audio/ogg")},
                data={"model": _GROQ_MODEL, "response_format": "text"},
            )
        resp.raise_for_status()
        return resp.text.strip()


async def _summarize(text: str, lang: str) -> Optional[str]:
    if not settings.gemini_api_key:
        return None
    prompt = (
        f"لخّص النص التالي في 3 نقاط رئيسية موجزة:\n\n{text}"
        if lang == "ar"
        else f"Summarize the following text in exactly 3 concise bullet points:\n\n{text}"
    )
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{_GEMINI_URL}?key={settings.gemini_api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            resp.raise_for_status()
            data = resp.json()
            parts = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])
            )
            return (parts[0].get("text") or "").strip() or None
    except Exception as exc:
        logger.warning(f"Gemini summary failed: {exc}")
        return None


def _extract_audio(input_path: str, output_path: str) -> bool:
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", input_path,
                "-vn", "-ar", "16000", "-ac", "1", "-ab", "128k",
                "-f", "mp3", output_path, "-y",
            ],
            capture_output=True,
            timeout=120,
        )
        return result.returncode == 0 and os.path.exists(output_path)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        logger.warning(f"ffmpeg unavailable: {exc}")
        return False


async def _process(message: Message, file_id: str, ext: str, lang: str) -> None:
    wait_msg = await message.answer(
        "🎙️ جارٍ النسخ..." if lang == "ar" else "🎙️ Transcribing..."
    )
    tmp_dir = tempfile.mkdtemp(prefix="vx_tr_")
    try:
        if not settings.groq_api_key:
            await wait_msg.edit_text(
                "❌ مفتاح Groq غير مُهيَّأ." if lang == "ar"
                else "❌ Groq API key is not configured."
            )
            return

        audio_path = os.path.join(tmp_dir, f"input.{ext}")
        await message.bot.download(file_id, destination=audio_path)

        if ext in ("mp4", "webm", "avi", "mov", "mkv"):
            extracted = os.path.join(tmp_dir, "audio.mp3")
            ok = await asyncio.get_event_loop().run_in_executor(
                None, _extract_audio, audio_path, extracted
            )
            if ok:
                audio_path = extracted
            else:
                await wait_msg.edit_text(
                    "⚠️ تعذّر استخراج الصوت. أرسل ملف صوت مباشرةً."
                    if lang == "ar"
                    else "⚠️ Could not extract audio. Please send an audio file directly."
                )
                return

        text = await _transcribe(audio_path)
        if not text:
            await wait_msg.edit_text(
                "❌ لم يُتعرَّف على أي كلام." if lang == "ar"
                else "❌ No speech detected in the file."
            )
            return

        header = "🎙️ *النص المستخرج:*\n\n" if lang == "ar" else "🎙️ *Transcription:*\n\n"
        body = text if len(text) <= 3800 else text[:3800] + "…"
        await wait_msg.edit_text(header + body, parse_mode="Markdown")

        if len(text) > _SUMMARY_THRESHOLD:
            await message.answer("⏳ جارٍ التلخيص..." if lang == "ar" else "⏳ Summarizing...")
            summary = await _summarize(text, lang)
            if summary:
                sum_header = "📝 *الملخص:*\n\n" if lang == "ar" else "📝 *Summary:*\n\n"
                await message.answer(sum_header + summary, parse_mode="Markdown")

    except Exception as exc:
        logger.error(f"Transcription error: {exc}", exc_info=True)
        err = (
            f"❌ فشل النسخ: {type(exc).__name__}"
            if lang == "ar"
            else f"❌ Transcription failed: {type(exc).__name__}"
        )
        try:
            await wait_msg.edit_text(err)
        except Exception:
            pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.message(Command("transcribe"))
async def cmd_transcribe(message: Message, lang: str = "en") -> None:
    hint = (
        "🎙️ أرسل رسالة صوتية أو مقطع فيديو لتحويله إلى نص."
        if lang == "ar"
        else "🎙️ Send a voice message, video, or audio file to transcribe it."
    )
    await message.answer(hint)


@router.message(F.voice)
async def handle_voice(message: Message, lang: str = "en") -> None:
    await _process(message, message.voice.file_id, "ogg", lang)


@router.message(F.video_note)
async def handle_video_note(message: Message, lang: str = "en") -> None:
    await _process(message, message.video_note.file_id, "mp4", lang)


@router.message(F.video)
async def handle_video(message: Message, lang: str = "en") -> None:
    await _process(message, message.video.file_id, "mp4", lang)


@router.message(F.audio)
async def handle_audio_file(message: Message, lang: str = "en") -> None:
    ext = "mp3"
    if message.audio.file_name:
        ext = message.audio.file_name.rsplit(".", 1)[-1].lower() or "mp3"
    await _process(message, message.audio.file_id, ext, lang)


def register_transcriber_handlers(dp) -> None:
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


@router.message(Command("flushteams"))
async def cmd_flushteams(message: Message, lang: str = "en") -> None:
    if message.from_user.id not in settings.admin_id_list:
        await message.answer(t("admin_only", lang))
        return

    from services.cache_service import _get_redis, _get_disk_cache

    redis = await _get_redis()
    if redis:
        backend = f"Redis @ {settings.redis_url[:30]}..."
    else:
        backend = "diskcache (local filesystem)"
    logger.info(f"[flushteams] Cache backend: {backend}")

    keys = [
        "sfsc:league_teams:PD",  "sfsc:league_teams:PL",
        "sfsc:league_teams:SA",  "sfsc:league_teams:BL1",
        "sfsc:league_teams:FL1", "sfsc:league_teams:CL",
        "sfsc:league_teams:SPL", "sfsc:league_teams:ELC",
    ]

    deleted = []
    skipped = []
    if redis:
        for k in keys:
            existed = await redis.delete(k)
            (deleted if existed else skipped).append(k)
            await redis.delete(f"backup:{k}")
    else:
        dc = _get_disk_cache()
        for k in keys:
            existed = k in dc
            dc.delete(k)
            dc.delete(f"backup:{k}")
            (deleted if existed else skipped).append(k)

    report = (
        f"✅ *Cache flush complete*\n"
        f"Backend: `{backend}`\n"
        f"Deleted ({len(deleted)}): `{'`, `'.join(k.split(':')[-1] for k in deleted) or 'none'}`\n"
        f"Not found ({len(skipped)}): `{'`, `'.join(k.split(':')[-1] for k in skipped) or 'none'}`"
    )
    logger.info(f"[flushteams] Deleted={deleted} Skipped={skipped}")
    await message.answer(report, parse_mode="Markdown")


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
            # Also detect Arabic from callback's attached message text
            elif isinstance(event, CallbackQuery) and event.message:
                cb_text = (event.message.text or event.message.caption or "")
                if cb_text and re.search(r'[\u0600-\u06FF]', cb_text):
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
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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
    from handlers.start import _BTN_MAP as _START_BUTTONS
    from aiogram.filters import StateFilter
    from aiogram.fsm.state import default_state

    # Catch-all for natural language messages.
    # Explicitly EXCLUDES keyboard button texts so the start router handles them first.
    @dp.message(
        StateFilter(default_state),
        lambda m: (
            m.text is not None
            and not m.text.startswith("/")
            and m.text not in _START_BUTTONS   # ← skip Reply Keyboard button presses
        ),
    )
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

    asyncio.create_task(_clear_fuel_caches())
    asyncio.create_task(_clear_stale_team_caches())
    asyncio.create_task(_fuel_refresh_loop())
    logger.info("✅ Fuel auto-refresh task started (24 h interval)")

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

# Mount static files (TWA menu HTML + any other assets)
_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(_STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/menu", response_class=HTMLResponse)
async def menu_page():
    """Redirect-friendly entry point for the TWA menu page."""
    menu_html = os.path.join(_STATIC_DIR, "menu.html")
    try:
        with open(menu_html, "r", encoding="utf-8") as fh:
            return HTMLResponse(content=fh.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Menu not found</h1>", status_code=404)


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


async def _clear_fuel_caches():
    """Clear all cached fuel data at startup so stale/bad results are discarded."""
    from services.cache_service import cache as _cache
    from api_clients.omega_fuel import ARAB_FUEL_SOURCES
    await asyncio.sleep(3)
    keys_to_clear = [f"fuel:{code}" for code in ARAB_FUEL_SOURCES]
    keys_to_clear += ["fuel:US","fuel:DE","fuel:FR","fuel:GB","fuel:JP","fuel:IN","fuel:BR","fuel:RU","fuel:CN","gpp:listing"]
    for key in keys_to_clear:
        await _cache.delete(key)
    logger.info(f"✅ Cleared {len(keys_to_clear)} fuel cache entries")


async def _clear_stale_team_caches():
    """One-time flush of all league team caches on startup — remove after first deploy."""
    from services.cache_service import cache as _cache
    await asyncio.sleep(5)
    keys = [
        "sfsc:league_teams:PD", "sfsc:league_teams:PL",
        "sfsc:league_teams:SA", "sfsc:league_teams:BL1",
        "sfsc:league_teams:FL1", "sfsc:league_teams:CL",
        "sfsc:league_teams:SPL", "sfsc:league_teams:ELC",
    ]
    for k in keys:
        await _cache.delete(k)
    logger.info(f"✅ Flushed {len(keys)} league team cache keys")


async def _fuel_refresh_loop():
    """Fetch Lebanon fuel prices once at startup then every 24 h."""
    from api_clients.omega_fuel import omega_fuel
    await asyncio.sleep(15)
    while True:
        try:
            result = await omega_fuel.get_prices("LB", force=True)
            if result and not result.get("error"):
                pub = result.get("published_date") or result.get("scraped_at", "")[:10]
                logger.info(f"✅ Fuel LB refreshed — date: {pub}")
            else:
                logger.warning("⚠️ Fuel LB refresh returned no data")
        except Exception as exc:
            logger.warning(f"Fuel refresh error: {exc}")
        await asyncio.sleep(86400)


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

FILES["static/menu.html"] = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Omega Bot Menu</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans Arabic', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 12px;
    overflow-x: hidden;
  }

  h1 {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    margin-bottom: 14px;
    text-align: center;
    letter-spacing: 0.5px;
    text-shadow: 0 0 20px rgba(100,160,255,0.4);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    width: 100%;
    max-width: 360px;
  }

  .btn {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 14px 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    cursor: pointer;
    transition: all 0.18s ease;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    min-height: 84px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.08);
  }

  .btn:hover {
    background: rgba(255,255,255,0.14);
    border-color: rgba(255,255,255,0.25);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.12);
  }

  .btn:active {
    transform: scale(0.94) translateY(0);
    background: rgba(100,160,255,0.2);
    border-color: rgba(100,160,255,0.5);
  }

  .btn .icon {
    font-size: 1.9rem;
    line-height: 1;
    display: block;
    animation: float 3s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
  }

  .btn .label {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.82);
    text-align: center;
    line-height: 1.25;
    font-weight: 500;
  }

  .btn .label-en {
    font-size: 0.63rem;
    color: rgba(255,255,255,0.45);
    text-align: center;
    margin-top: 1px;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-3px); }
  }

  /* Unique accent colours per button */
  .btn[data-key="gold"]     { --accent: #ffd700; }
  .btn[data-key="currency"] { --accent: #4caf96; }
  .btn[data-key="fuel"]     { --accent: #ff8c42; }
  .btn[data-key="weather"]  { --accent: #64b5f6; }
  .btn[data-key="football"] { --accent: #81c784; }
  .btn[data-key="movies"]   { --accent: #ce93d8; }
  .btn[data-key="cv"]       { --accent: #80cbc4; }
  .btn[data-key="logo"]     { --accent: #ffb74d; }
  .btn[data-key="ai"]       { --accent: #4dd0e1; }
  .btn[data-key="stocks"]   { --accent: #a5d6a7; }
  .btn[data-key="crypto"]   { --accent: #f48fb1; }
  .btn[data-key="news"]     { --accent: #90caf9; }
  .btn[data-key="flights"]  { --accent: #b0bec5; }
  .btn[data-key="quakes"]   { --accent: #ef9a9a; }
  .btn[data-key="settings"] { --accent: #ffe082; }

  .btn .icon { color: var(--accent, #ffffff); }

  .btn:hover {
    border-color: var(--accent, rgba(255,255,255,0.25));
    box-shadow: 0 8px 24px rgba(0,0,0,0.35),
                0 0 12px rgba(var(--accent-rgb, 255,255,255), 0.15),
                inset 0 1px 0 rgba(255,255,255,0.12);
  }
</style>
</head>
<body>
<h1 id="title">⚡ Omega Bot</h1>
<div class="grid" id="grid"></div>

<script>
const tg = window.Telegram && window.Telegram.WebApp;
if (tg) { tg.ready(); tg.expand(); }

const lang = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.language_code) || 'en';
const isAr = lang === 'ar';

document.documentElement.dir = isAr ? 'rtl' : 'ltr';
document.documentElement.lang = isAr ? 'ar' : 'en';
document.getElementById('title').textContent = isAr ? '⚡ أوميغا بوت' : '⚡ Omega Bot';

const BUTTONS = [
  { key:'gold',     icon:'🥇', ar:'ذهب',     en:'Gold'     },
  { key:'currency', icon:'💱', ar:'عملة',    en:'Currency' },
  { key:'fuel',     icon:'⛽', ar:'محروقات', en:'Fuel'     },
  { key:'weather',  icon:'🌤', ar:'طقس',     en:'Weather'  },
  { key:'football', icon:'⚽', ar:'كرة قدم', en:'Football' },
  { key:'movies',   icon:'🎬', ar:'أفلام',   en:'Movies'   },
  { key:'cv',       icon:'📄', ar:'CV',       en:'CV'       },
  { key:'logo',     icon:'🎨', ar:'شعار',    en:'Logo'     },
  { key:'ai',       icon:'🤖', ar:'ذكاء اصطناعي', en:'AI Chat' },
  { key:'stocks',   icon:'📈', ar:'أسهم',    en:'Stocks'   },
  { key:'crypto',   icon:'₿',  ar:'كريبتو',  en:'Crypto'   },
  { key:'news',     icon:'📰', ar:'أخبار',   en:'News'     },
  { key:'flights',  icon:'✈️', ar:'رحلات',   en:'Flights'  },
  { key:'quakes',   icon:'🌍', ar:'زلازل',   en:'Quakes'   },
  { key:'settings', icon:'⚙️', ar:'إعدادات', en:'Settings' },
];

const grid = document.getElementById('grid');

BUTTONS.forEach((b, i) => {
  const btn = document.createElement('button');
  btn.className = 'btn';
  btn.dataset.key = b.key;
  btn.style.setProperty('--delay', `${(i * 0.13).toFixed(2)}s`);
  btn.innerHTML = `
    <span class="icon">${b.icon}</span>
    <span class="label">${isAr ? b.ar : b.en}</span>
    <span class="label-en">${isAr ? b.en : b.ar}</span>
  `;
  btn.addEventListener('click', () => {
    btn.style.transition = 'none';
    btn.style.transform = 'scale(0.90)';
    setTimeout(() => {
      if (tg) {
        tg.sendData(b.key);
        tg.close();
      } else {
        alert('Selected: ' + b.key);
      }
    }, 120);
  });
  grid.appendChild(btn);
});
</script>
</body>
</html>
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
