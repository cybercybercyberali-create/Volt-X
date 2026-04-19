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
