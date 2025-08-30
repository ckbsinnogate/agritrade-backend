"""
Weather Views
API views for weather data endpoints
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import random
import logging

from .models import WeatherLocation, CurrentWeather, WeatherAlert, WeatherForecast
from .serializers import (
    CurrentWeatherSerializer, WeatherAlertSerializer, 
    WeatherForecastSerializer, ComprehensiveWeatherSerializer
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def weather_api_root(request, format=None):
    """Weather API Root"""
    return Response({
        'name': 'AgriConnect Weather API',
        'description': 'Current weather data and forecasting for agricultural planning',
        'version': '1.0',
        'endpoints': {
            'current_weather': request.build_absolute_uri('current/'),
            'forecast': request.build_absolute_uri('forecast/'),
            'alerts': request.build_absolute_uri('alerts/'),
            'locations': request.build_absolute_uri('locations/'),
        },
        'features': [
            'Real-time weather data',
            'Agricultural recommendations', 
            'Weather alerts and warnings',
            'Multi-day forecasting',
            'Location-based services'
        ],
        'status': 'operational'
    })


class CurrentWeatherView(APIView):
    """Current weather data endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get current weather data"""
        try:
            # Get location parameter (optional)
            location_name = request.query_params.get('location', 'Accra')
            region = request.query_params.get('region', 'Greater Accra')
            
            # Try to get user's location from profile if authenticated
            if request.user and request.user.is_authenticated:
                try:
                    if hasattr(request.user, 'farmerprofile'):
                        profile = request.user.farmerprofile
                        if hasattr(profile, 'location') and profile.location:
                            location_name = profile.location
                    elif hasattr(request.user, 'farms') and request.user.farms.exists():
                        farm = request.user.farms.first()
                        if farm.location:
                            location_name = farm.location
                except Exception:
                    pass
            
            # Get or create location
            location, created = WeatherLocation.objects.get_or_create(
                name=location_name,
                region=region,
                defaults={
                    'latitude': self._get_ghana_coordinates(location_name)['lat'],
                    'longitude': self._get_ghana_coordinates(location_name)['lon']
                }
            )
            
            # Get or create current weather data
            current_weather = self._get_or_create_current_weather(location)
            
            # Get active alerts
            alerts = WeatherAlert.objects.filter(
                location=location,
                is_active=True,
                expires_at__gt=timezone.now()
            )
            
            # Get forecast (next 7 days)
            forecast = self._get_or_create_forecast(location)
            
            # Agricultural recommendations based on weather
            recommendations = self._get_agricultural_recommendations(current_weather)
            
            # Prepare comprehensive response
            weather_data = {
                'location': location.name,
                'region': location.region,
                'current_temperature': current_weather.temperature,
                'humidity': current_weather.humidity,
                'weather_condition': current_weather.weather_condition,
                'rainfall_prediction': current_weather.rainfall_prediction,
                'wind_speed': current_weather.wind_speed,
                'pressure': current_weather.pressure,
                'visibility': current_weather.visibility,
                'uv_index': current_weather.uv_index,
                'alerts': WeatherAlertSerializer(alerts, many=True).data,
                'recommendations': recommendations,
                'forecast': WeatherForecastSerializer(forecast[:7], many=True).data,
                'last_updated': current_weather.last_updated
            }
            
            serializer = ComprehensiveWeatherSerializer(weather_data)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Current weather data retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in current weather view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve weather data',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_ghana_coordinates(self, location_name):
        """Get coordinates for Ghana locations"""
        ghana_coordinates = {
            'Accra': {'lat': Decimal('5.6037'), 'lon': Decimal('-0.1870')},
            'Kumasi': {'lat': Decimal('6.6885'), 'lon': Decimal('-1.6244')},
            'Tamale': {'lat': Decimal('9.4034'), 'lon': Decimal('-0.8424')},
            'Cape Coast': {'lat': Decimal('5.1053'), 'lon': Decimal('-1.2466')},
            'Sunyani': {'lat': Decimal('7.3392'), 'lon': Decimal('-2.3265')},
            'Koforidua': {'lat': Decimal('6.0898'), 'lon': Decimal('-0.2591')},
            'Bolgatanga': {'lat': Decimal('10.7858'), 'lon': Decimal('-0.8516')},
            'Wa': {'lat': Decimal('10.0608'), 'lon': Decimal('-2.5067')},
            'Ho': {'lat': Decimal('6.6109'), 'lon': Decimal('0.4717')},
            'Techiman': {'lat': Decimal('7.5928'), 'lon': Decimal('-1.9350')},
        }
        return ghana_coordinates.get(location_name, ghana_coordinates['Accra'])
    
    def _get_or_create_current_weather(self, location):
        """Get or create current weather data with simulated values"""
        # Check if we have recent data (within 1 hour)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_weather = CurrentWeather.objects.filter(
            location=location,
            last_updated__gt=one_hour_ago
        ).first()
        
        if recent_weather:
            return recent_weather
        
        # Create new weather data with realistic values for Ghana
        current_month = datetime.now().month
        
        # Ghana seasonal weather patterns
        if current_month in [12, 1, 2]:  # Harmattan season
            base_temp = Decimal('28.0')
            humidity = Decimal('35.0')
            rainfall_pred = Decimal('5.0')
            condition = random.choice(['Sunny', 'Clear', 'Hazy'])
        elif current_month in [3, 4, 5]:  # Hot dry season
            base_temp = Decimal('32.0')
            humidity = Decimal('60.0')
            rainfall_pred = Decimal('15.0')
            condition = random.choice(['Hot', 'Partly Cloudy', 'Sunny'])
        elif current_month in [6, 7, 8, 9]:  # Rainy season
            base_temp = Decimal('26.0')
            humidity = Decimal('85.0')
            rainfall_pred = Decimal('45.0')
            condition = random.choice(['Rainy', 'Cloudy', 'Thunderstorms'])
        else:  # Transitional months
            base_temp = Decimal('29.0')
            humidity = Decimal('70.0')
            rainfall_pred = Decimal('25.0')
            condition = random.choice(['Partly Cloudy', 'Cloudy', 'Sunny'])
        
        # Add some variation
        temp_variation = Decimal(str(random.uniform(-3, 3)))
        humidity_variation = Decimal(str(random.uniform(-10, 10)))
        
        weather_data = {
            'location': location,
            'temperature': base_temp + temp_variation,
            'humidity': max(Decimal('20'), min(Decimal('95'), humidity + humidity_variation)),
            'weather_condition': condition,
            'rainfall_prediction': rainfall_pred + Decimal(str(random.uniform(-5, 15))),
            'wind_speed': Decimal(str(random.uniform(5, 20))),
            'pressure': Decimal(str(random.uniform(1010, 1020))),
            'visibility': Decimal(str(random.uniform(8, 15))),
            'uv_index': random.randint(3, 10)
        }
        
        return CurrentWeather.objects.create(**weather_data)
    
    def _get_or_create_forecast(self, location):
        """Get or create 7-day forecast"""
        today = date.today()
        forecasts = []
        
        for i in range(7):
            forecast_date = today + timedelta(days=i)
            
            forecast, created = WeatherForecast.objects.get_or_create(
                location=location,
                forecast_date=forecast_date,
                defaults=self._generate_forecast_data(i)
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def _generate_forecast_data(self, day_offset):
        """Generate realistic forecast data"""
        current_month = datetime.now().month
        
        # Base temperatures by season
        if current_month in [12, 1, 2]:  # Harmattan
            base_high, base_low = 30, 18
        elif current_month in [3, 4, 5]:  # Hot dry
            base_high, base_low = 35, 22
        elif current_month in [6, 7, 8, 9]:  # Rainy
            base_high, base_low = 28, 20
        else:  # Transitional
            base_high, base_low = 31, 21
        
        # Add daily variation
        temp_var = random.uniform(-2, 2)
        conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Thunderstorms']
        
        return {
            'temp_high': Decimal(str(base_high + temp_var)),
            'temp_low': Decimal(str(base_low + temp_var)),
            'condition': random.choice(conditions),
            'rainfall_probability': random.randint(10, 80)
        }
    
    def _get_agricultural_recommendations(self, weather):
        """Generate agricultural recommendations based on weather"""
        recommendations = []
        
        # Temperature-based recommendations
        if weather.temperature > 35:
            recommendations.extend([
                'Provide shade for sensitive crops',
                'Increase irrigation frequency',
                'Avoid midday farm activities'
            ])
        elif weather.temperature < 20:
            recommendations.extend([
                'Protect crops from cold stress',
                'Consider covering young plants',
                'Optimal time for cool-season crops'
            ])
        
        # Humidity-based recommendations
        if weather.humidity > 80:
            recommendations.extend([
                'Monitor for fungal diseases',
                'Ensure good air circulation',
                'Consider preventive fungicide application'
            ])
        
        # Rainfall-based recommendations
        if weather.rainfall_prediction > 30:
            recommendations.extend([
                'Prepare drainage systems',
                'Harvest mature crops before heavy rains',
                'Apply protective sprays'
            ])
        elif weather.rainfall_prediction < 10:
            recommendations.extend([
                'Implement water conservation',
                'Schedule irrigation',
                'Mulch around plants to retain moisture'
            ])
        
        # General recommendations
        recommendations.extend([
            'Check weather updates regularly',
            'Plan farm activities based on forecast',
            'Monitor crop health daily'
        ])
        
        return list(set(recommendations))  # Remove duplicates


class WeatherForecastView(APIView):
    """Weather forecast endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get weather forecast"""
        try:
            location_name = request.query_params.get('location', 'Accra')
            region = request.query_params.get('region', 'Greater Accra')
            days = int(request.query_params.get('days', 7))
            
            location = get_object_or_404(WeatherLocation, name=location_name, region=region)
            
            # Get forecast for requested days
            forecasts = WeatherForecast.objects.filter(
                location=location,
                forecast_date__gte=date.today(),
                forecast_date__lte=date.today() + timedelta(days=days)
            )[:days]
            
            serializer = WeatherForecastSerializer(forecasts, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'location': location_name,
                    'region': region,
                    'forecast': serializer.data
                },
                'message': f'{days}-day forecast retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in weather forecast view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve forecast',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WeatherAlertsView(APIView):
    """Weather alerts endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get active weather alerts"""
        try:
            location_name = request.query_params.get('location')
            
            alerts_query = WeatherAlert.objects.filter(
                is_active=True,
                expires_at__gt=timezone.now()
            )
            
            if location_name:
                alerts_query = alerts_query.filter(location__name=location_name)
            
            alerts = alerts_query.order_by('-created_at')
            serializer = WeatherAlertSerializer(alerts, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'alerts': serializer.data,
                    'count': alerts.count()
                },
                'message': 'Weather alerts retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in weather alerts view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve alerts',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
