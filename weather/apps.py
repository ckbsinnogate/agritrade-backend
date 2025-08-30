"""
Weather App Configuration
Provides current weather data API endpoints for AgriConnect platform
"""

from django.apps import AppConfig


class WeatherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather'
    verbose_name = 'Weather Services'
