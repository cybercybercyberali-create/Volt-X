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
