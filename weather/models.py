"""
Weather Models
Database models for weather data and alerts
"""

from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class WeatherLocation(models.Model):
    """Weather location tracking"""
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    region = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'region']
    
    def __str__(self):
        return f"{self.name}, {self.region}"


class CurrentWeather(models.Model):
    """Current weather data cache"""
    location = models.ForeignKey(WeatherLocation, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    weather_condition = models.CharField(max_length=100)
    rainfall_prediction = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pressure = models.DecimalField(max_digits=7, decimal_places=2, default=1013.25)
    visibility = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    uv_index = models.IntegerField(default=5)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"Weather for {self.location.name} - {self.weather_condition}"


class WeatherAlert(models.Model):
    """Weather alerts and warnings"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    TYPE_CHOICES = [
        ('rainfall', 'Rainfall'),
        ('temperature', 'Temperature'),
        ('drought', 'Drought'),
        ('flood', 'Flood'),
        ('storm', 'Storm'),
        ('general', 'General'),
    ]
    
    location = models.ForeignKey(WeatherLocation, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    recommendations = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type.title()} Alert for {self.location.name}"


class WeatherForecast(models.Model):
    """Weather forecast data"""
    location = models.ForeignKey(WeatherLocation, on_delete=models.CASCADE)
    forecast_date = models.DateField()
    temp_high = models.DecimalField(max_digits=5, decimal_places=2)
    temp_low = models.DecimalField(max_digits=5, decimal_places=2)
    condition = models.CharField(max_length=100)
    rainfall_probability = models.IntegerField(default=0)  # 0-100 percentage
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['location', 'forecast_date']
        ordering = ['forecast_date']
    
    def __str__(self):
        return f"Forecast for {self.location.name} on {self.forecast_date}"
