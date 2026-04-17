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
