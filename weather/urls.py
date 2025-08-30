"""
Weather URLs
URL patterns for weather API endpoints
"""

from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random
from .simple_views import weather_api_root, SimpleCurrentWeatherView

app_name = 'weather'

@api_view(['GET'])
@permission_classes([AllowAny])
def current_weather(request):
    """Current weather endpoint"""
    location = request.query_params.get('location', 'Accra')
    
    # Mock weather data
    weather_data = {
        'location': location,
        'region': 'Greater Accra',
        'current_temperature': Decimal('28.5'),
        'humidity': Decimal('75.0'),
        'weather_condition': 'Partly Cloudy',
        'rainfall_prediction': Decimal('15.0'),
        'wind_speed': Decimal(str(random.uniform(5, 20))),
        'pressure': Decimal('1013.25'),
        'visibility': Decimal('10.0'),
        'uv_index': 5,
        'alerts': [],
        'recommendations': [
            'Optimal time for planting tomatoes',
            'Monitor crop moisture levels',
            'Check weather updates regularly'
        ],
        'forecast': [
            {'day': 'Today', 'temp_high': 30, 'temp_low': 22, 'condition': 'Sunny'},
            {'day': 'Tomorrow', 'temp_high': 28, 'temp_low': 20, 'condition': 'Cloudy'},
        ],
        'last_updated': timezone.now().isoformat()
    }
    
    return Response({
        'success': True,
        'data': weather_data,
        'message': 'Current weather data retrieved successfully'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def weather_forecast(request):
    """Weather forecast endpoint"""
    location = request.query_params.get('location', 'Accra')
    
    forecast_data = {
        'location': location,
        'region': 'Greater Accra',
        'forecast': [
            {'day': 'Today', 'temp_high': 30, 'temp_low': 22, 'condition': 'Sunny', 'rainfall_probability': 10},
            {'day': 'Tomorrow', 'temp_high': 28, 'temp_low': 20, 'condition': 'Cloudy', 'rainfall_probability': 40},
            {'day': 'Day 3', 'temp_high': 26, 'temp_low': 19, 'condition': 'Rainy', 'rainfall_probability': 80},
        ]
    }
    
    return Response({
        'success': True,
        'data': forecast_data,
        'message': '7-day forecast retrieved successfully'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def weather_alerts(request):
    """Weather alerts endpoint"""
    alerts_data = {
        'alerts': [
            {
                'id': 1,
                'location_name': 'Accra',
                'alert_type': 'general',
                'severity': 'low',
                'title': 'Normal Weather Conditions',
                'message': 'Weather conditions are normal for farming activities.',
                'recommendations': ['Continue regular farming activities'],
                'is_active': True,
                'created_at': timezone.now().isoformat(),
            }
        ],
        'count': 1
    }
    
    return Response({
        'success': True,
        'data': alerts_data,
        'message': 'Weather alerts retrieved successfully'
    })

urlpatterns = [
    # Weather API Root
    path('', weather_api_root, name='weather-api-root'),
    
    # Current weather endpoint (the missing one causing 404s)
    path('current/', SimpleCurrentWeatherView.as_view(), name='current-weather'),
    
    # Weather forecast
    path('forecast/', weather_forecast, name='weather-forecast'),
    
    # Weather alerts
    path('alerts/', weather_alerts, name='weather-alerts'),
]
