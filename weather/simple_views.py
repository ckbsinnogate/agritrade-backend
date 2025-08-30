"""
Simple Weather Views (No Database Required)
Provide weather endpoints without database dependency for immediate frontend compatibility
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import random
import logging

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


class SimpleCurrentWeatherView(APIView):
    """Simple current weather data endpoint without database dependency"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get current weather data (mock data for immediate frontend compatibility)"""
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
            
            # Generate mock weather data based on Ghana's climate patterns
            weather_data = self._generate_mock_weather_data(location_name, region)
            
            return Response({
                'success': True,
                'data': weather_data,
                'message': 'Current weather data retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in simple weather view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve weather data',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_mock_weather_data(self, location, region):
        """Generate realistic weather data for Ghana"""
        current_month = datetime.now().month
        
        # Ghana seasonal weather patterns
        if current_month in [12, 1, 2]:  # Harmattan season
            base_temp = 28.0
            humidity = 35.0
            rainfall_pred = 5.0
            condition = random.choice(['Sunny', 'Clear', 'Hazy'])
        elif current_month in [3, 4, 5]:  # Hot dry season
            base_temp = 32.0
            humidity = 60.0
            rainfall_pred = 15.0
            condition = random.choice(['Hot', 'Partly Cloudy', 'Sunny'])
        elif current_month in [6, 7, 8, 9]:  # Rainy season
            base_temp = 26.0
            humidity = 85.0
            rainfall_pred = 45.0
            condition = random.choice(['Rainy', 'Cloudy', 'Thunderstorms'])
        else:  # Transitional months
            base_temp = 29.0
            humidity = 70.0
            rainfall_pred = 25.0
            condition = random.choice(['Partly Cloudy', 'Cloudy', 'Sunny'])
        
        # Add variation
        temp_variation = random.uniform(-3, 3)
        humidity_variation = random.uniform(-10, 10)
        
        # Generate agricultural recommendations
        recommendations = self._get_agricultural_recommendations(
            base_temp + temp_variation, 
            humidity + humidity_variation, 
            rainfall_pred
        )
        
        # Generate mock alerts
        alerts = self._generate_mock_alerts(base_temp + temp_variation, rainfall_pred)
        
        # Generate forecast
        forecast = self._generate_mock_forecast()
        
        return {
            'location': location,
            'region': region,
            'current_temperature': round(base_temp + temp_variation, 1),
            'humidity': round(max(20, min(95, humidity + humidity_variation)), 1),
            'weather_condition': condition,
            'rainfall_prediction': round(max(0, rainfall_pred + random.uniform(-5, 15)), 1),
            'wind_speed': round(random.uniform(5, 20), 1),
            'pressure': round(random.uniform(1010, 1020), 2),
            'visibility': round(random.uniform(8, 15), 1),
            'uv_index': random.randint(3, 10),
            'alerts': alerts,
            'recommendations': recommendations,
            'forecast': forecast,
            'last_updated': timezone.now().isoformat()
        }
    
    def _get_agricultural_recommendations(self, temperature, humidity, rainfall):
        """Generate agricultural recommendations based on weather"""
        recommendations = []
        
        # Temperature-based recommendations
        if temperature > 35:
            recommendations.extend([
                'Provide shade for sensitive crops',
                'Increase irrigation frequency',
                'Avoid midday farm activities'
            ])
        elif temperature < 20:
            recommendations.extend([
                'Protect crops from cold stress',
                'Consider covering young plants',
                'Optimal time for cool-season crops'
            ])
        
        # Humidity-based recommendations
        if humidity > 80:
            recommendations.extend([
                'Monitor for fungal diseases',
                'Ensure good air circulation',
                'Consider preventive fungicide application'
            ])
        
        # Rainfall-based recommendations
        if rainfall > 30:
            recommendations.extend([
                'Prepare drainage systems',
                'Harvest mature crops before heavy rains',
                'Apply protective sprays'
            ])
        elif rainfall < 10:
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
    
    def _generate_mock_alerts(self, temperature, rainfall):
        """Generate mock weather alerts"""
        alerts = []
        
        if temperature > 35:
            alerts.append({
                'id': 1,
                'location_name': 'Current Location',
                'alert_type': 'temperature',
                'severity': 'medium',
                'title': 'High Temperature Alert',
                'message': f'High temperatures ({temperature:.1f}°C) expected. Take precautions.',
                'recommendations': ['Provide crop shade', 'Increase watering'],
                'is_active': True,
                'created_at': timezone.now().isoformat(),
                'expires_at': (timezone.now() + timedelta(hours=12)).isoformat()
            })
        
        if rainfall > 30:
            alerts.append({
                'id': 2,
                'location_name': 'Current Location',
                'alert_type': 'rainfall',
                'severity': 'medium',
                'title': 'Heavy Rain Alert',
                'message': f'Heavy rainfall ({rainfall:.1f}mm) expected in the next 24 hours.',
                'recommendations': ['Prepare drainage', 'Harvest mature crops'],
                'is_active': True,
                'created_at': timezone.now().isoformat(),
                'expires_at': (timezone.now() + timedelta(hours=24)).isoformat()
            })
        
        return alerts
    
    def _generate_mock_forecast(self):
        """Generate 7-day mock forecast"""
        forecast = []
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
        
        for i in range(7):
            forecast_date = date.today() + timedelta(days=i)
            temp_var = random.uniform(-2, 2)
            conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Thunderstorms']
            
            if i == 0:
                day_name = 'Today'
            elif i == 1:
                day_name = 'Tomorrow'
            else:
                day_name = f'Day {i+1}'
            
            forecast.append({
                'location_name': 'Current Location',
                'day': day_name,
                'temp_high': round(base_high + temp_var, 1),
                'temp_low': round(base_low + temp_var, 1),
                'condition': random.choice(conditions),
                'rainfall_probability': random.randint(10, 80),
                'forecast_date': forecast_date.isoformat()
            })
        
        return forecast


class SimpleForecastView(APIView):
    """Simple forecast endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get weather forecast"""
        try:
            location_name = request.query_params.get('location', 'Accra')
            region = request.query_params.get('region', 'Greater Accra')
            days = int(request.query_params.get('days', 7))
            
            # Use the same forecast generation from current weather
            weather_view = SimpleCurrentWeatherView()
            forecast = weather_view._generate_mock_forecast()[:days]
            
            return Response({
                'success': True,
                'data': {
                    'location': location_name,
                    'region': region,
                    'forecast': forecast
                },
                'message': f'{days}-day forecast retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in forecast view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve forecast',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleAlertsView(APIView):
    """Simple alerts endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get weather alerts"""
        try:
            # Generate some mock alerts
            alerts = [
                {
                    'id': 1,
                    'location_name': 'Accra',
                    'alert_type': 'general',
                    'severity': 'low',
                    'title': 'Weather Update',
                    'message': 'Normal weather conditions expected for the next 24 hours.',
                    'recommendations': ['Continue regular farming activities'],
                    'is_active': True,
                    'created_at': timezone.now().isoformat(),
                    'expires_at': (timezone.now() + timedelta(hours=24)).isoformat()
                }
            ]
            
            return Response({
                'success': True,
                'data': {
                    'alerts': alerts,
                    'count': len(alerts)
                },
                'message': 'Weather alerts retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in alerts view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve alerts',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
