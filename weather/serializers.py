"""
Weather Serializers
DRF serializers for weather data
"""

from rest_framework import serializers
from .models import WeatherLocation, CurrentWeather, WeatherAlert, WeatherForecast


class WeatherLocationSerializer(serializers.ModelSerializer):
    """Serializer for weather locations"""
    
    class Meta:
        model = WeatherLocation
        fields = ['id', 'name', 'latitude', 'longitude', 'region']


class CurrentWeatherSerializer(serializers.ModelSerializer):
    """Serializer for current weather data"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    region = serializers.CharField(source='location.region', read_only=True)
    
    class Meta:
        model = CurrentWeather
        fields = [
            'location_name', 'region', 'temperature', 'humidity', 
            'weather_condition', 'rainfall_prediction', 'wind_speed',
            'pressure', 'visibility', 'uv_index', 'last_updated'
        ]


class WeatherAlertSerializer(serializers.ModelSerializer):
    """Serializer for weather alerts"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = WeatherAlert
        fields = [
            'id', 'location_name', 'alert_type', 'severity', 'title',
            'message', 'recommendations', 'is_active', 'created_at', 'expires_at'
        ]


class WeatherForecastSerializer(serializers.ModelSerializer):
    """Serializer for weather forecast"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    day = serializers.CharField(source='forecast_date', read_only=True)
    
    class Meta:
        model = WeatherForecast
        fields = [
            'location_name', 'day', 'temp_high', 'temp_low', 
            'condition', 'rainfall_probability', 'forecast_date'
        ]


class ComprehensiveWeatherSerializer(serializers.Serializer):
    """Comprehensive weather data serializer for frontend"""
    location = serializers.CharField()
    region = serializers.CharField()
    current_temperature = serializers.DecimalField(max_digits=5, decimal_places=2)
    humidity = serializers.DecimalField(max_digits=5, decimal_places=2)
    weather_condition = serializers.CharField()
    rainfall_prediction = serializers.DecimalField(max_digits=5, decimal_places=2)
    wind_speed = serializers.DecimalField(max_digits=5, decimal_places=2)
    pressure = serializers.DecimalField(max_digits=7, decimal_places=2)
    visibility = serializers.DecimalField(max_digits=5, decimal_places=2)
    uv_index = serializers.IntegerField()
    alerts = WeatherAlertSerializer(many=True, read_only=True)
    recommendations = serializers.ListField(child=serializers.CharField())
    forecast = WeatherForecastSerializer(many=True, read_only=True)
    last_updated = serializers.DateTimeField()
