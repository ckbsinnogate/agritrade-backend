"""
Farmer Dashboard Django App Tests
Comprehensive test suite for farmer dashboard functionality
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
import json

from .models import FarmerDashboardPreferences, FarmerAlert, FarmerDashboardMetrics, FarmerGoal

User = get_user_model()


class FarmerDashboardModelTests(TestCase):
    """Test farmer dashboard models"""
    
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='testpass123'
        )
    
    def test_farmer_dashboard_preferences_creation(self):
        """Test farmer dashboard preferences model"""
        preferences = FarmerDashboardPreferences.objects.create(
            farmer=self.farmer,
            default_currency='GHS',
            preferred_language='en',
            dashboard_theme='light'
        )
        
        self.assertEqual(preferences.farmer, self.farmer)
        self.assertEqual(preferences.default_currency, 'GHS')
        self.assertTrue(preferences.weather_alerts)
        self.assertTrue(preferences.market_price_alerts)
        
    def test_farmer_alert_creation(self):
        """Test farmer alert model"""
        alert = FarmerAlert.objects.create(
            farmer=self.farmer,
            title='Weather Alert',
            message='Heavy rainfall expected',
            alert_type='weather',
            priority='high'
        )
        
        self.assertEqual(alert.farmer, self.farmer)
        self.assertEqual(alert.alert_type, 'weather')
        self.assertEqual(alert.priority, 'high')
        self.assertFalse(alert.is_read)
        self.assertFalse(alert.is_expired)
    
    def test_farmer_goal_creation(self):
        """Test farmer goal model"""
        goal = FarmerGoal.objects.create(
            farmer=self.farmer,
            title='Revenue Target',
            goal_type='revenue',
            target_value=Decimal('10000'),
            current_value=Decimal('2500'),
            start_date=date.today(),
            target_date=date.today() + timedelta(days=365)
        )
        
        self.assertEqual(goal.farmer, self.farmer)
        self.assertEqual(goal.progress_percentage, 25.0)
        self.assertEqual(goal.status, 'active')
    
    def test_farmer_metrics_creation(self):
        """Test farmer dashboard metrics model"""
        metrics = FarmerDashboardMetrics.objects.create(
            farmer=self.farmer,
            date=date.today(),
            total_revenue=Decimal('1500'),
            orders_count=5,
            total_products=10
        )
        
        self.assertEqual(metrics.farmer, self.farmer)
        self.assertEqual(metrics.total_revenue, Decimal('1500'))
        self.assertEqual(metrics.orders_count, 5)


class FarmerDashboardAPITests(APITestCase):
    """Test farmer dashboard API endpoints"""
    
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.farmer)
    
    def test_farmer_dashboard_api_root(self):
        """Test farmer dashboard API root endpoint"""
        url = reverse('farmer_dashboard:farmer-dashboard-root')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('endpoints', response.data)
        self.assertIn('sections', response.data)
    
    def test_farmer_dashboard_overview(self):
        """Test farmer dashboard overview endpoint"""
        url = reverse('farmer_dashboard:farmer-dashboard-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('data', response.data)
        
        # Check required overview fields
        data = response.data['data']
        required_fields = [
            'today_revenue', 'week_revenue', 'month_revenue',
            'total_orders', 'total_products', 'total_farms'
        ]
        for field in required_fields:
            self.assertIn(field, data)
    
    def test_farmer_products_view(self):
        """Test farmer products endpoint"""
        url = reverse('farmer_dashboard:farmer-dashboard-products')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('count', response.data)
        self.assertIn('data', response.data)
    
    def test_farmer_orders_view(self):
        """Test farmer orders endpoint"""
        url = reverse('farmer_dashboard:farmer-dashboard-orders')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('count', response.data)
        self.assertIn('data', response.data)
    
    def test_farmer_farms_view(self):
        """Test farmer farms endpoint"""
        url = reverse('farmer_dashboard:farmer-dashboard-farms')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('count', response.data)
        self.assertIn('data', response.data)
    
    def test_farmer_weather_view(self):
        """Test farmer weather endpoint"""
        url = reverse('farmer_dashboard:farmer-dashboard-weather')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('data', response.data)
        
        # Check weather data structure
        data = response.data['data']
        required_fields = [
            'location', 'current_temperature', 'humidity',
            'weather_condition', 'alerts', 'recommendations'
        ]
        for field in required_fields:
            self.assertIn(field, data)
    
    def test_farmer_market_insights_view(self):
        """Test farmer market insights endpoint"""
        url = reverse('farmer_dashboard:farmer-dashboard-market-insights')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('data', response.data)
        
        # Check market insights structure
        data = response.data['data']
        required_fields = [
            'trending_products', 'price_changes', 'demand_forecast',
            'opportunities', 'recommendations'
        ]
        for field in required_fields:
            self.assertIn(field, data)
    
    def test_farmer_preferences_crud(self):
        """Test farmer preferences CRUD operations"""
        # Create preferences
        url = reverse('farmer_dashboard:farmer-preferences-list')
        data = {
            'default_currency': 'USD',
            'preferred_language': 'en',
            'dashboard_theme': 'dark',
            'weather_alerts': True,
            'market_price_alerts': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get preferences
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_farmer_alerts_crud(self):
        """Test farmer alerts CRUD operations"""
        # Create alert
        url = reverse('farmer_dashboard:farmer-alerts-list')
        data = {
            'title': 'Test Alert',
            'message': 'This is a test alert',
            'alert_type': 'general',
            'priority': 'medium'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get alerts
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Mark alert as read
        alert_id = response.data['results'][0]['id']
        mark_read_url = reverse('farmer_dashboard:farmer-alerts-mark-read', args=[alert_id])
        response = self.client.post(mark_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_farmer_goals_crud(self):
        """Test farmer goals CRUD operations"""
        # Create goal
        url = reverse('farmer_dashboard:farmer-goals-list')
        data = {
            'title': 'Revenue Goal',
            'description': 'Achieve target revenue',
            'goal_type': 'revenue',
            'target_value': '5000.00',
            'current_value': '1000.00',
            'unit': 'GHS',
            'start_date': date.today().isoformat(),
            'target_date': (date.today() + timedelta(days=180)).isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get goals
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update goal progress
        goal_id = response.data['results'][0]['id']
        update_url = reverse('farmer_dashboard:farmer-goals-update-progress', args=[goal_id])
        progress_data = {'current_value': '2500.00'}
        response = self.client.post(update_url, progress_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to farmer dashboard"""
        self.client.force_authenticate(user=None)
        
        url = reverse('farmer_dashboard:farmer-dashboard-overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FarmerDashboardIntegrationTests(APITestCase):
    """Integration tests for farmer dashboard with other systems"""
    
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='integrationfarmer',
            email='integration@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.farmer)
    
    def test_dashboard_overview_integration(self):
        """Test dashboard overview integration with products, orders, farms"""
        # Create some test data first (this would require the other apps)
        
        # Test overview endpoint
        url = reverse('farmer_dashboard:farmer-dashboard-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        
        # Verify the structure includes integration points
        data = response.data['data']
        self.assertIn('recent_orders', data)
        self.assertIn('recent_products', data)
        self.assertIn('low_stock_alerts', data)
    
    def test_api_error_handling(self):
        """Test API error handling"""
        # Test invalid endpoint
        response = self.client.get('/api/v1/farmer-dashboard/invalid/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test malformed request
        url = reverse('farmer_dashboard:farmer-goals-list')
        invalid_data = {'invalid_field': 'invalid_value'}
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
