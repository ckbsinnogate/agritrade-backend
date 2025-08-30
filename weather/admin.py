"""
Weather Admin Configuration
Django admin interface for weather data management
"""

from django.contrib import admin
from .models import WeatherLocation, CurrentWeather, WeatherAlert, WeatherForecast


@admin.register(WeatherLocation)
class WeatherLocationAdmin(admin.ModelAdmin):
    """Admin for weather locations"""
    list_display = ['name', 'region', 'latitude', 'longitude', 'created_at']
    list_filter = ['region', 'created_at']
    search_fields = ['name', 'region']
    ordering = ['region', 'name']


@admin.register(CurrentWeather)
class CurrentWeatherAdmin(admin.ModelAdmin):
    """Admin for current weather data"""
    list_display = [
        'location', 'temperature', 'humidity', 'weather_condition', 
        'rainfall_prediction', 'last_updated'
    ]
    list_filter = ['weather_condition', 'last_updated', 'location__region']
    search_fields = ['location__name', 'weather_condition']
    ordering = ['-last_updated']
    readonly_fields = ['last_updated']


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    """Admin for weather alerts"""
    list_display = [
        'title', 'location', 'alert_type', 'severity', 'is_active', 
        'created_at', 'expires_at'
    ]
    list_filter = ['alert_type', 'severity', 'is_active', 'created_at']
    search_fields = ['title', 'message', 'location__name']
    ordering = ['-created_at']
    actions = ['activate_alerts', 'deactivate_alerts']
    
    def activate_alerts(self, request, queryset):
        """Activate selected alerts"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} alerts activated.')
    activate_alerts.short_description = "Activate selected alerts"
    
    def deactivate_alerts(self, request, queryset):
        """Deactivate selected alerts"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} alerts deactivated.')
    deactivate_alerts.short_description = "Deactivate selected alerts"


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    """Admin for weather forecasts"""
    list_display = [
        'location', 'forecast_date', 'temp_high', 'temp_low', 
        'condition', 'rainfall_probability', 'created_at'
    ]
    list_filter = ['forecast_date', 'condition', 'location__region', 'created_at']
    search_fields = ['location__name', 'condition']
    ordering = ['forecast_date', 'location']
    date_hierarchy = 'forecast_date'
