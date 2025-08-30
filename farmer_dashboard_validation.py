#!/usr/bin/env python
"""
Farmer Dashboard Backend Validation Script
Comprehensive testing and validation of farmer dashboard implementation
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from farmer_dashboard.models import (
    FarmerDashboardPreferences, FarmerAlert, 
    FarmerDashboardMetrics, FarmerGoal
)

User = get_user_model()


class FarmerDashboardValidator:
    """Comprehensive farmer dashboard validation"""
    
    def __init__(self):
        self.client = APIClient()
        self.test_farmer = None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_results': [],
            'api_endpoints': [],
            'errors': []
        }
    
    def run_validation(self):
        """Run complete validation suite"""
        print("🌾 FARMER DASHBOARD BACKEND VALIDATION")
        print("=" * 60)
        
        try:
            # Setup test environment
            self.setup_test_environment()
            
            # Run validation tests
            self.validate_models()
            self.validate_api_endpoints()
            self.validate_dashboard_overview()
            self.validate_product_management()
            self.validate_order_management()
            self.validate_farm_management()
            self.validate_weather_insights()
            self.validate_market_insights()
            self.validate_preferences()
            self.validate_alerts()
            self.validate_goals()
            self.validate_metrics()
            self.validate_management_commands()
            
            # Generate summary
            self.generate_summary()
            
        except Exception as e:
            self.log_error(f"Validation failed: {str(e)}")
        
        finally:
            self.cleanup_test_environment()
        
        return self.results
    
    def setup_test_environment(self):
        """Setup test environment"""
        print("\n🔧 Setting up test environment...")
        
        # Create test farmer
        self.test_farmer, created = User.objects.get_or_create(
            username='test_farmer_validation',
            defaults={
                'email': 'testfarmer@validation.com',
                'first_name': 'Test',
                'last_name': 'Farmer',
                'is_active': True
            }
        )
        
        if created:
            self.test_farmer.set_password('testpass123')
            self.test_farmer.save()
        
        # Authenticate API client
        self.client.force_authenticate(user=self.test_farmer)
        
        self.log_success("Test environment setup completed")
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        try:
            # Clean test data
            if self.test_farmer:
                FarmerDashboardPreferences.objects.filter(farmer=self.test_farmer).delete()
                FarmerAlert.objects.filter(farmer=self.test_farmer).delete()
                FarmerGoal.objects.filter(farmer=self.test_farmer).delete()
                FarmerDashboardMetrics.objects.filter(farmer=self.test_farmer).delete()
                # Don't delete the user in case it's used elsewhere
            
            print("Test environment cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def validate_models(self):
        """Validate farmer dashboard models"""
        print("\n📊 Validating models...")
        
        # Test FarmerDashboardPreferences
        try:
            preferences = FarmerDashboardPreferences.objects.create(
                farmer=self.test_farmer,
                default_currency='GHS',
                preferred_language='en',
                dashboard_theme='light'
            )
            self.log_success("FarmerDashboardPreferences model working")
            preferences.delete()
        except Exception as e:
            self.log_error(f"FarmerDashboardPreferences model error: {e}")
        
        # Test FarmerAlert
        try:
            alert = FarmerAlert.objects.create(
                farmer=self.test_farmer,
                title='Test Alert',
                message='Test message',
                alert_type='general',
                priority='medium'
            )
            self.log_success("FarmerAlert model working")
            alert.delete()
        except Exception as e:
            self.log_error(f"FarmerAlert model error: {e}")
        
        # Test FarmerGoal
        try:
            from datetime import date, timedelta
            goal = FarmerGoal.objects.create(
                farmer=self.test_farmer,
                title='Test Goal',
                goal_type='revenue',
                target_value=Decimal('1000'),
                start_date=date.today(),
                target_date=date.today() + timedelta(days=30)
            )
            
            # Test calculated properties
            assert goal.progress_percentage == 0
            assert goal.days_remaining >= 0
            
            self.log_success("FarmerGoal model working")
            goal.delete()
        except Exception as e:
            self.log_error(f"FarmerGoal model error: {e}")
    
    def validate_api_endpoints(self):
        """Validate API endpoint accessibility"""
        print("\n🔗 Validating API endpoints...")
        
        endpoints = [
            '/api/v1/farmer-dashboard/',
            '/api/v1/farmer-dashboard/overview/',
            '/api/v1/farmer-dashboard/products/',
            '/api/v1/farmer-dashboard/orders/',
            '/api/v1/farmer-dashboard/farms/',
            '/api/v1/farmer-dashboard/weather/',
            '/api/v1/farmer-dashboard/market-insights/',
            '/api/v1/farmer-dashboard/preferences/',
            '/api/v1/farmer-dashboard/alerts/',
            '/api/v1/farmer-dashboard/goals/',
            '/api/v1/farmer-dashboard/metrics/',
        ]
        
        for endpoint in endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 201]:
                    self.log_success(f"GET {endpoint} - Status: {response.status_code}")
                    self.results['api_endpoints'].append({
                        'endpoint': endpoint,
                        'method': 'GET',
                        'status': response.status_code,
                        'working': True
                    })
                else:
                    self.log_error(f"GET {endpoint} - Status: {response.status_code}")
                    self.results['api_endpoints'].append({
                        'endpoint': endpoint,
                        'method': 'GET',
                        'status': response.status_code,
                        'working': False
                    })
            except Exception as e:
                self.log_error(f"GET {endpoint} - Error: {e}")
                self.results['api_endpoints'].append({
                    'endpoint': endpoint,
                    'method': 'GET',
                    'status': 'error',
                    'error': str(e),
                    'working': False
                })
    
    def validate_dashboard_overview(self):
        """Validate dashboard overview endpoint"""
        print("\n📈 Validating dashboard overview...")
        
        try:
            response = self.client.get('/api/v1/farmer-dashboard/overview/')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = [
                    'success', 'data', 'message'
                ]
                
                overview_fields = [
                    'today_revenue', 'week_revenue', 'month_revenue',
                    'total_orders', 'total_products', 'total_farms',
                    'recent_orders', 'recent_products', 'trending_crops'
                ]
                
                all_fields_present = True
                for field in required_fields:
                    if field not in data:
                        self.log_error(f"Missing field in overview response: {field}")
                        all_fields_present = False
                
                if 'data' in data:
                    for field in overview_fields:
                        if field not in data['data']:
                            self.log_error(f"Missing field in overview data: {field}")
                            all_fields_present = False
                
                if all_fields_present:
                    self.log_success("Dashboard overview structure validation passed")
                
            else:
                self.log_error(f"Dashboard overview returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Dashboard overview validation error: {e}")
    
    def validate_product_management(self):
        """Validate product management functionality"""
        print("\n📦 Validating product management...")
        
        try:
            response = self.client.get('/api/v1/farmer-dashboard/products/')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'count', 'data', 'message']
                if all(field in data for field in required_fields):
                    self.log_success("Product management endpoint structure valid")
                else:
                    self.log_error("Product management endpoint missing required fields")
            else:
                self.log_error(f"Product management returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Product management validation error: {e}")
    
    def validate_order_management(self):
        """Validate order management functionality"""
        print("\n📋 Validating order management...")
        
        try:
            response = self.client.get('/api/v1/farmer-dashboard/orders/')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'count', 'data', 'message']
                if all(field in data for field in required_fields):
                    self.log_success("Order management endpoint structure valid")
                else:
                    self.log_error("Order management endpoint missing required fields")
            else:
                self.log_error(f"Order management returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Order management validation error: {e}")
    
    def validate_farm_management(self):
        """Validate farm management functionality"""
        print("\n🏭 Validating farm management...")
        
        try:
            response = self.client.get('/api/v1/farmer-dashboard/farms/')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'count', 'data', 'message']
                if all(field in data for field in required_fields):
                    self.log_success("Farm management endpoint structure valid")
                else:
                    self.log_error("Farm management endpoint missing required fields")
            else:
                self.log_error(f"Farm management returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Farm management validation error: {e}")
    
    def validate_weather_insights(self):
        """Validate weather insights functionality"""
        print("\n🌤️ Validating weather insights...")
        
        try:
            response = self.client.get('/api/v1/farmer-dashboard/weather/')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'success' in data and 'data' in data:
                    weather_data = data['data']
                    weather_fields = [
                        'location', 'current_temperature', 'humidity',
                        'weather_condition', 'alerts', 'recommendations'
                    ]
                    
                    if all(field in weather_data for field in weather_fields):
                        self.log_success("Weather insights endpoint structure valid")
                    else:
                        self.log_error("Weather insights endpoint missing required fields")
                else:
                    self.log_error("Weather insights endpoint missing required response fields")
            else:
                self.log_error(f"Weather insights returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Weather insights validation error: {e}")
    
    def validate_market_insights(self):
        """Validate market insights functionality"""
        print("\n📊 Validating market insights...")
        
        try:
            response = self.client.get('/api/v1/farmer-dashboard/market-insights/')
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'success' in data and 'data' in data:
                    market_data = data['data']
                    market_fields = [
                        'trending_products', 'price_changes', 'demand_forecast',
                        'opportunities', 'recommendations'
                    ]
                    
                    if all(field in market_data for field in market_fields):
                        self.log_success("Market insights endpoint structure valid")
                    else:
                        self.log_error("Market insights endpoint missing required fields")
                else:
                    self.log_error("Market insights endpoint missing required response fields")
            else:
                self.log_error(f"Market insights returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Market insights validation error: {e}")
    
    def validate_preferences(self):
        """Validate preferences management"""
        print("\n⚙️ Validating preferences management...")
        
        try:
            # Create preferences
            preferences_data = {
                'default_currency': 'USD',
                'preferred_language': 'en',
                'dashboard_theme': 'dark',
                'weather_alerts': True,
                'market_price_alerts': False
            }
            
            response = self.client.post('/api/v1/farmer-dashboard/preferences/', preferences_data)
            
            if response.status_code == 201:
                self.log_success("Preferences creation working")
                
                # Get preferences
                response = self.client.get('/api/v1/farmer-dashboard/preferences/')
                if response.status_code == 200:
                    self.log_success("Preferences retrieval working")
                else:
                    self.log_error(f"Preferences retrieval failed: {response.status_code}")
            else:
                self.log_error(f"Preferences creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Preferences validation error: {e}")
    
    def validate_alerts(self):
        """Validate alerts management"""
        print("\n🔔 Validating alerts management...")
        
        try:
            # Create alert
            alert_data = {
                'title': 'Test Alert',
                'message': 'This is a test alert for validation',
                'alert_type': 'general',
                'priority': 'medium'
            }
            
            response = self.client.post('/api/v1/farmer-dashboard/alerts/', alert_data)
            
            if response.status_code == 201:
                self.log_success("Alert creation working")
                
                # Get alerts
                response = self.client.get('/api/v1/farmer-dashboard/alerts/')
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        alert_id = data['results'][0]['id']
                        
                        # Test mark as read
                        mark_read_response = self.client.post(
                            f'/api/v1/farmer-dashboard/alerts/{alert_id}/mark_read/'
                        )
                        
                        if mark_read_response.status_code == 200:
                            self.log_success("Alert mark as read working")
                        else:
                            self.log_error(f"Alert mark as read failed: {mark_read_response.status_code}")
                        
                    self.log_success("Alert retrieval working")
                else:
                    self.log_error(f"Alert retrieval failed: {response.status_code}")
            else:
                self.log_error(f"Alert creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Alerts validation error: {e}")
    
    def validate_goals(self):
        """Validate goals management"""
        print("\n🎯 Validating goals management...")
        
        try:
            from datetime import date, timedelta
            
            # Create goal
            goal_data = {
                'title': 'Test Revenue Goal',
                'description': 'Test goal for validation',
                'goal_type': 'revenue',
                'target_value': '5000.00',
                'current_value': '1000.00',
                'unit': 'GHS',
                'start_date': date.today().isoformat(),
                'target_date': (date.today() + timedelta(days=90)).isoformat()
            }
            
            response = self.client.post('/api/v1/farmer-dashboard/goals/', goal_data)
            
            if response.status_code == 201:
                self.log_success("Goal creation working")
                
                # Get goals
                response = self.client.get('/api/v1/farmer-dashboard/goals/')
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        goal_id = data['results'][0]['id']
                        
                        # Test progress update
                        progress_data = {'current_value': '2500.00'}
                        progress_response = self.client.post(
                            f'/api/v1/farmer-dashboard/goals/{goal_id}/update_progress/',
                            progress_data
                        )
                        
                        if progress_response.status_code == 200:
                            self.log_success("Goal progress update working")
                        else:
                            self.log_error(f"Goal progress update failed: {progress_response.status_code}")
                        
                    self.log_success("Goal retrieval working")
                else:
                    self.log_error(f"Goal retrieval failed: {response.status_code}")
            else:
                self.log_error(f"Goal creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Goals validation error: {e}")
    
    def validate_metrics(self):
        """Validate metrics functionality"""
        print("\n📊 Validating metrics...")
        
        try:
            response = self.client.get('/api/v1/farmer-dashboard/metrics/')
            
            if response.status_code == 200:
                self.log_success("Metrics endpoint accessible")
            else:
                self.log_error(f"Metrics endpoint returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Metrics validation error: {e}")
    
    def validate_management_commands(self):
        """Validate management commands"""
        print("\n⚙️ Validating management commands...")
        
        try:
            from django.core.management import call_command
            from io import StringIO
            
            # Test generate_farmer_metrics command
            out = StringIO()
            call_command('generate_farmer_metrics', '--help', stdout=out)
            if 'Generate daily farmer dashboard metrics' in out.getvalue():
                self.log_success("generate_farmer_metrics command available")
            else:
                self.log_error("generate_farmer_metrics command not working properly")
            
            # Test create_sample_farmer_data command
            out = StringIO()
            call_command('create_sample_farmer_data', '--help', stdout=out)
            if 'Create sample farmer dashboard data' in out.getvalue():
                self.log_success("create_sample_farmer_data command available")
            else:
                self.log_error("create_sample_farmer_data command not working properly")
                
        except Exception as e:
            self.log_error(f"Management commands validation error: {e}")
    
    def log_success(self, message):
        """Log successful test"""
        print(f"✅ {message}")
        self.results['tests_run'] += 1
        self.results['tests_passed'] += 1
        self.results['test_results'].append({
            'status': 'PASS',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_error(self, message):
        """Log failed test"""
        print(f"❌ {message}")
        self.results['tests_run'] += 1
        self.results['tests_failed'] += 1
        self.results['test_results'].append({
            'status': 'FAIL',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        self.results['errors'].append(message)
    
    def generate_summary(self):
        """Generate validation summary"""
        print("\n" + "=" * 60)
        print("📋 FARMER DASHBOARD VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = self.results['tests_run']
        passed_tests = self.results['tests_passed']
        failed_tests = self.results['tests_failed']
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests Run: {total_tests}")
        print(f"Tests Passed: {passed_tests}")
        print(f"Tests Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\nAPI Endpoints Tested: {len(self.results['api_endpoints'])}")
        working_endpoints = sum(1 for ep in self.results['api_endpoints'] if ep.get('working', False))
        print(f"Working Endpoints: {working_endpoints}")
        
        if self.results['errors']:
            print(f"\n⚠️ Errors Found: {len(self.results['errors'])}")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.results['errors']) > 5:
                print(f"  ... and {len(self.results['errors']) - 5} more errors")
        
        # Overall status
        if success_rate >= 90:
            print(f"\n🎉 FARMER DASHBOARD VALIDATION: EXCELLENT")
            self.results['overall_status'] = 'EXCELLENT'
        elif success_rate >= 75:
            print(f"\n✅ FARMER DASHBOARD VALIDATION: GOOD")
            self.results['overall_status'] = 'GOOD'
        elif success_rate >= 50:
            print(f"\n⚠️ FARMER DASHBOARD VALIDATION: NEEDS IMPROVEMENT")
            self.results['overall_status'] = 'NEEDS_IMPROVEMENT'
        else:
            print(f"\n❌ FARMER DASHBOARD VALIDATION: FAILED")
            self.results['overall_status'] = 'FAILED'
        
        print("=" * 60)


def main():
    """Main validation function"""
    validator = FarmerDashboardValidator()
    results = validator.run_validation()
    
    # Save results
    with open('farmer_dashboard_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Validation results saved to: farmer_dashboard_validation_results.json")
    
    return results


if __name__ == "__main__":
    try:
        results = main()
        
        # Exit with appropriate code
        if results['overall_status'] in ['EXCELLENT', 'GOOD']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Validation script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
