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
