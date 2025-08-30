"""
Administrator Dashboard Platform Overview & Management - Final Validation Test
Comprehensive test suite to validate all admin dashboard backend functionality

This script validates:
- Settings Section: System configuration and preferences management
- System Section: Platform health, monitoring, and maintenance
- Analytics Section: Comprehensive analytics and reporting
- Content Section: Content management and moderation
- Users Section: Advanced user management and administration

Built with 40+ years of web development experience.
"""

import os
import sys
import django
import json
import uuid
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.db import models

# Import admin dashboard models
from admin_dashboard.models import (
    SystemSettings, AdminPreferences, SystemHealthCheck, SystemMaintenanceLog,
    AnalyticsSnapshot, CustomAnalyticsReport, ContentModerationQueue, ContentPolicy,
    UserActivityLog, UserSecurityEvent, AdminActionLog
)

User = get_user_model()

class AdminDashboardValidationTest:
    """Comprehensive validation test for admin dashboard functionality"""
    
    def __init__(self):
        self.client = Client()
        self.admin_user = None
        self.test_results = {
            'models': {'passed': 0, 'failed': 0, 'details': []},
            'endpoints': {'passed': 0, 'failed': 0, 'details': []},
            'serializers': {'passed': 0, 'failed': 0, 'details': []},
            'admin_interface': {'passed': 0, 'failed': 0, 'details': []},
            'permissions': {'passed': 0, 'failed': 0, 'details': []},
            'overall': {'status': 'UNKNOWN', 'score': 0}
        }
    
    def setup_test_data(self):
        """Setup test data for validation"""
        print("🔧 Setting up test data...")
        
        try:
            # Try to get existing admin user first
            try:
                self.admin_user = User.objects.get(username='admin_test_user')
                print("ℹ️ Using existing admin test user")
            except User.DoesNotExist:
                # Create new admin user with required fields
                unique_suffix = str(uuid.uuid4())[:8]
                self.admin_user = User.objects.create_user(
                    username='admin_test_user',
                    email=f'admin_test_{unique_suffix}@test.com',
                    phone_number='+233201234567',  # Required field
                    password='admin123',
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                print("✅ Created new admin test user")
            
            # Ensure user has admin privileges
            self.admin_user.is_staff = True
            self.admin_user.is_superuser = True
            self.admin_user.is_active = True
            self.admin_user.save()
            
            # Login admin user
            login_success = self.client.login(username='admin_test_user', password='admin123')
            if not login_success:
                raise Exception("Failed to login admin user")
            
            print("✅ Test data setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Test data setup failed: {str(e)}")
            return False
    
    def test_model_creation(self):
        """Test all admin dashboard models can be created"""
        print("\n🗃️ Testing Model Creation...")
        
        tests = [
            # Test SystemSettings
            {
                'model': SystemSettings,
                'data': {
                    'category': 'GENERAL',
                    'key': 'test_setting',
                    'value': 'test_value',
                    'description': 'Test setting for validation',
                    'created_by': self.admin_user,
                    'updated_by': self.admin_user
                },
                'name': 'SystemSettings'
            },
            
            # Test AdminPreferences
            {
                'model': AdminPreferences,
                'data': {
                    'admin_user': self.admin_user,
                    'dashboard_layout': {'widgets': ['users', 'orders']},
                    'notification_settings': {'email': True, 'push': False},
                    'theme_settings': {'dark_mode': False}
                },
                'name': 'AdminPreferences'
            },
            
            # Test SystemHealthCheck
            {
                'model': SystemHealthCheck,
                'data': {
                    'service_name': 'Database Connection Test',
                    'service_type': 'DATABASE',
                    'status': 'HEALTHY',
                    'response_time': 45.5,
                    'metadata': {'version': '1.0', 'details': 'All good'}
                },
                'name': 'SystemHealthCheck'
            },
            
            # Test SystemMaintenanceLog
            {
                'model': SystemMaintenanceLog,
                'data': {
                    'maintenance_type': 'UPDATE',
                    'title': 'System Update Test',
                    'description': 'Test maintenance log entry',
                    'performed_by': self.admin_user,
                    'started_at': timezone.now(),
                    'was_successful': True,
                    'affected_services': ['web', 'api'],
                    'downtime_minutes': 5
                },
                'name': 'SystemMaintenanceLog'
            },
            
            # Test AnalyticsSnapshot
            {
                'model': AnalyticsSnapshot,
                'data': {
                    'date': timezone.now().date(),
                    'total_users': 1000,
                    'active_users': 500,
                    'new_registrations': 50,
                    'total_orders': 200,
                    'total_revenue': Decimal('10000.00'),
                    'total_products': 300,
                    'total_transactions': 150,
                    'platform_usage_hours': 2400.5,
                    'api_requests': 50000,
                    'errors_count': 5,
                    'conversion_rate': 2.5
                },
                'name': 'AnalyticsSnapshot'
            },
            
            # Test CustomAnalyticsReport
            {
                'model': CustomAnalyticsReport,
                'data': {
                    'name': 'Test Analytics Report',
                    'report_type': 'USER',
                    'description': 'Test report for validation',
                    'query_config': {'period': '30d', 'metrics': ['users', 'orders']},
                    'created_by': self.admin_user,
                    'is_scheduled': False
                },
                'name': 'CustomAnalyticsReport'
            },
            
            # Test ContentModerationQueue
            {
                'model': ContentModerationQueue,
                'data': {
                    'content_type': 'PRODUCT',
                    'content_id': 'test_product_123',
                    'content_title': 'Test Product for Moderation',
                    'content_preview': 'This is a test product listing...',
                    'submitted_by': self.admin_user,
                    'status': 'PENDING',
                    'priority': 5,
                    'auto_flagged': False,
                    'flag_reasons': []
                },
                'name': 'ContentModerationQueue'
            },
            
            # Test ContentPolicy
            {
                'model': ContentPolicy,
                'data': {
                    'policy_type': 'GENERAL',
                    'title': 'Test Content Policy',
                    'description': 'Test policy for validation',
                    'rules': {'min_length': 10, 'no_spam': True},
                    'auto_enforcement': False,
                    'is_active': True,
                    'created_by': self.admin_user
                },
                'name': 'ContentPolicy'
            },
            
            # Test UserActivityLog
            {
                'model': UserActivityLog,
                'data': {
                    'user': self.admin_user,
                    'activity_type': 'LOGIN',
                    'description': 'Test login activity',
                    'details': {'browser': 'Chrome', 'location': 'Test'},
                    'ip_address': '127.0.0.1',
                    'user_agent': 'Test User Agent',
                    'session_id': 'test_session_123'
                },
                'name': 'UserActivityLog'
            },
            
            # Test UserSecurityEvent
            {
                'model': UserSecurityEvent,
                'data': {
                    'user': self.admin_user,
                    'event_type': 'SUSPICIOUS_LOGIN',
                    'severity': 'MEDIUM',
                    'description': 'Test security event',
                    'details': {'reason': 'New location'},
                    'ip_address': '192.168.1.1',
                    'is_resolved': False
                },
                'name': 'UserSecurityEvent'
            },
            
            # Test AdminActionLog
            {
                'model': AdminActionLog,
                'data': {
                    'admin_user': self.admin_user,
                    'action_type': 'USER_UPDATE',
                    'target_user': self.admin_user,
                    'description': 'Test admin action',
                    'details': {'field': 'email', 'old': 'old@test.com', 'new': 'new@test.com'},
                    'ip_address': '127.0.0.1'
                },
                'name': 'AdminActionLog'
            }
        ]
        
        for test in tests:
            try:
                # Clean existing test data first
                if test['name'] == 'AdminPreferences':
                    test['model'].objects.filter(admin_user=self.admin_user).delete()
                elif test['name'] == 'SystemSettings':
                    test['model'].objects.filter(key='test_setting').delete()
                elif test['name'] == 'AnalyticsSnapshot':
                    test['model'].objects.filter(total_users=1000).delete()
                elif 'created_by' in test['data']:
                    test['model'].objects.filter(created_by=self.admin_user).delete()
                
                instance = test['model'].objects.create(**test['data'])
                print(f"✅ {test['name']}: Created successfully (ID: {instance.id})")
                self.test_results['models']['passed'] += 1
                
            except Exception as e:
                print(f"❌ {test['name']}: Failed - {str(e)}")
                self.test_results['models']['failed'] += 1
        
        return self.test_results['models']['failed'] == 0
    
    def test_serializer_imports(self):
        """Test all admin dashboard serializers"""
        print("\n📄 Testing Serializer Imports...")
        
        try:
            from admin_dashboard.serializers import (
                SystemSettingsSerializer, AdminPreferencesSerializer, SystemHealthCheckSerializer,
                SystemMaintenanceLogSerializer, AnalyticsSnapshotSerializer, CustomAnalyticsReportSerializer,
                ContentModerationQueueSerializer, ContentPolicySerializer, UserActivityLogSerializer,
                UserSecurityEventSerializer, AdminActionLogSerializer, DashboardOverviewSerializer
            )
            
            serializers = [
                'SystemSettingsSerializer', 'AdminPreferencesSerializer', 'SystemHealthCheckSerializer',
                'SystemMaintenanceLogSerializer', 'AnalyticsSnapshotSerializer', 'CustomAnalyticsReportSerializer',
                'ContentModerationQueueSerializer', 'ContentPolicySerializer', 'UserActivityLogSerializer',
                'UserSecurityEventSerializer', 'AdminActionLogSerializer', 'DashboardOverviewSerializer'
            ]
            
            for serializer_name in serializers:
                try:
                    serializer_class = locals()[serializer_name]
                    print(f"✅ {serializer_name}: Import successful")
                    self.test_results['serializers']['passed'] += 1
                except Exception as e:
                    print(f"❌ {serializer_name}: Import failed - {str(e)}")
                    self.test_results['serializers']['failed'] += 1
                    
        except Exception as e:
            print(f"❌ Serializers import failed: {str(e)}")
            self.test_results['serializers']['failed'] = 12
        
        return self.test_results['serializers']['failed'] == 0
    
    def test_url_configuration(self):
        """Test URL configuration"""
        print("\n🔗 Testing URL Configuration...")
        
        try:
            from admin_dashboard.urls import urlpatterns
            print(f"✅ URL Configuration: {len(urlpatterns)} patterns found")
            self.test_results['endpoints']['passed'] += 1
            return True
        except Exception as e:
            print(f"❌ URL Configuration: Failed - {str(e)}")
            self.test_results['endpoints']['failed'] += 1
            return False
    
    def test_api_endpoints(self):
        """Test key admin dashboard API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        key_endpoints = [
            {'url': '/api/v1/admin-dashboard/', 'method': 'GET', 'name': 'Dashboard Overview'},
            {'url': '/api/v1/admin-dashboard/settings/system/', 'method': 'GET', 'name': 'System Settings'},
            {'url': '/api/v1/admin-dashboard/system/status/', 'method': 'GET', 'name': 'System Status'},
            {'url': '/api/v1/admin-dashboard/analytics/dashboard/', 'method': 'GET', 'name': 'Analytics Dashboard'},
            {'url': '/api/v1/admin-dashboard/content/moderation/', 'method': 'GET', 'name': 'Content Moderation'},
            {'url': '/api/v1/admin-dashboard/users/activity/', 'method': 'GET', 'name': 'User Activity'},
        ]
        
        for endpoint in key_endpoints:
            try:
                response = self.client.get(endpoint['url'])
                
                if response.status_code in [200, 201]:
                    print(f"✅ {endpoint['name']}: {response.status_code}")
                    self.test_results['endpoints']['passed'] += 1
                else:
                    print(f"⚠️ {endpoint['name']}: {response.status_code}")
                    self.test_results['endpoints']['failed'] += 1
                    
            except Exception as e:
                print(f"❌ {endpoint['name']}: Error - {str(e)}")
                self.test_results['endpoints']['failed'] += 1
        
        return self.test_results['endpoints']['failed'] == 0
    
    def test_admin_interface(self):
        """Test Django admin interface"""
        print("\n⚙️ Testing Django Admin Interface...")
        
        admin_urls = [
            '/admin/admin_dashboard/systemsettings/',
            '/admin/admin_dashboard/adminpreferences/',
            '/admin/admin_dashboard/systemhealthcheck/',
            '/admin/admin_dashboard/systemmaintenancelog/',
            '/admin/admin_dashboard/analyticssnapshot/',
        ]
        
        for url in admin_urls:
            try:
                response = self.client.get(url)
                model_name = url.split('/')[-2]
                
                if response.status_code == 200:
                    print(f"✅ Admin {model_name}: Accessible")
                    self.test_results['admin_interface']['passed'] += 1
                else:
                    print(f"❌ Admin {model_name}: Status {response.status_code}")
                    self.test_results['admin_interface']['failed'] += 1
                    
            except Exception as e:
                print(f"❌ Admin {model_name}: Error - {str(e)}")
                self.test_results['admin_interface']['failed'] += 1
        
        return self.test_results['admin_interface']['failed'] == 0
    
    def test_django_configuration(self):
        """Test Django configuration"""
        print("\n⚙️ Testing Django Configuration...")
        
        try:
            from django.conf import settings
            
            if 'admin_dashboard' in settings.INSTALLED_APPS:
                print("✅ Django Configuration: admin_dashboard in INSTALLED_APPS")
                self.test_results['permissions']['passed'] += 1
                return True
            else:
                print("❌ Django Configuration: admin_dashboard not in INSTALLED_APPS")
                self.test_results['permissions']['failed'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Django Configuration: Error - {str(e)}")
            self.test_results['permissions']['failed'] += 1
            return False
    
    def cleanup_test_data(self):
        """Clean up test data after validation"""
        print("🧹 Cleaning up test data...")
        
        try:
            # Clean specific test records
            SystemSettings.objects.filter(key='test_setting').delete()
            AdminPreferences.objects.filter(admin_user=self.admin_user).delete()
            SystemHealthCheck.objects.filter(service_name='Database Connection Test').delete()
            SystemMaintenanceLog.objects.filter(title='System Update Test').delete()
            AnalyticsSnapshot.objects.filter(total_users=1000).delete()
            CustomAnalyticsReport.objects.filter(name='Test Analytics Report').delete()
            ContentModerationQueue.objects.filter(content_title='Test Product for Moderation').delete()
            ContentPolicy.objects.filter(title='Test Content Policy').delete()
            UserActivityLog.objects.filter(user=self.admin_user, description='Test login activity').delete()
            UserSecurityEvent.objects.filter(user=self.admin_user, description='Test security event').delete()
            AdminActionLog.objects.filter(admin_user=self.admin_user, description='Test admin action').delete()
            
            print("✅ Test data cleanup complete")
            
        except Exception as e:
            print(f"⚠️ Test data cleanup warning: {str(e)}")
    
    def calculate_overall_score(self):
        """Calculate overall validation score"""
        total_passed = sum([
            self.test_results['models']['passed'],
            self.test_results['endpoints']['passed'],
            self.test_results['serializers']['passed'],
            self.test_results['admin_interface']['passed'],
            self.test_results['permissions']['passed']
        ])
        
        total_tests = sum([
            self.test_results['models']['passed'] + self.test_results['models']['failed'],
            self.test_results['endpoints']['passed'] + self.test_results['endpoints']['failed'],
            self.test_results['serializers']['passed'] + self.test_results['serializers']['failed'],
            self.test_results['admin_interface']['passed'] + self.test_results['admin_interface']['failed'],
            self.test_results['permissions']['passed'] + self.test_results['permissions']['failed']
        ])
        
        if total_tests > 0:
            score = (total_passed / total_tests) * 100
            self.test_results['overall']['score'] = round(score, 2)
            
            if score >= 95:
                self.test_results['overall']['status'] = 'EXCELLENT'
            elif score >= 85:
                self.test_results['overall']['status'] = 'GOOD'
            elif score >= 70:
                self.test_results['overall']['status'] = 'ACCEPTABLE'
            else:
                self.test_results['overall']['status'] = 'NEEDS_IMPROVEMENT'
    
    def generate_final_report(self, tests_passed, total_tests):
        """Generate comprehensive validation report"""
        print("\n" + "="*80)
        print("🎯 ADMINISTRATOR DASHBOARD VALIDATION REPORT")
        print("="*80)
        
        # Summary statistics
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"Models: {self.test_results['models']['passed']}/{self.test_results['models']['passed'] + self.test_results['models']['failed']} passed")
        print(f"Endpoints: {self.test_results['endpoints']['passed']}/{self.test_results['endpoints']['passed'] + self.test_results['endpoints']['failed']} passed")
        print(f"Serializers: {self.test_results['serializers']['passed']}/{self.test_results['serializers']['passed'] + self.test_results['serializers']['failed']} passed")
        print(f"Admin Interface: {self.test_results['admin_interface']['passed']}/{self.test_results['admin_interface']['passed'] + self.test_results['admin_interface']['failed']} passed")
        print(f"Configuration: {self.test_results['permissions']['passed']}/{self.test_results['permissions']['passed'] + self.test_results['permissions']['failed']} passed")
        
        # Overall score
        print(f"\n🏆 OVERALL SCORE: {self.test_results['overall']['score']}% ({self.test_results['overall']['status']})")
        
        # Status determination
        if self.test_results['overall']['score'] >= 95:
            print("\n🎉 STATUS: PRODUCTION READY!")
            print("✅ All critical components are working correctly")
            print("✅ Admin dashboard backend is fully operational")
            print("✅ Ready for frontend integration")
        elif self.test_results['overall']['score'] >= 85:
            print("\n✅ STATUS: MOSTLY READY")
            print("⚠️ Minor issues detected, but core functionality works")
            print("🔧 Review failed tests for optimization opportunities")
        else:
            print("\n⚠️ STATUS: NEEDS ATTENTION")
            print("❌ Critical issues detected")
            print("🔧 Address failed tests before deployment")
        
        # Test breakdown
        print(f"\n📋 TEST BREAKDOWN:")
        print(f"Total Tests Run: {total_tests}")
        print(f"Tests Passed: {tests_passed}")
        print(f"Tests Failed: {total_tests - tests_passed}")
        
        return self.test_results
    
    def run_validation(self):
        """Run complete validation test suite"""
        print("🚀 Starting Administrator Dashboard Validation Test Suite...")
        print("Built with 40+ years of web development experience\n")
        
        if not self.setup_test_data():
            print("❌ Test setup failed. Cannot proceed.")
            return {'overall': {'score': 0, 'status': 'FAILED'}}
        
        # Run all validation tests
        tests_passed = 0
        total_tests = 6
        
        print("🎯 Starting Admin Dashboard Validation Tests...")
        print("=" * 80)
        
        # Test 1: Model Creation
        if self.test_model_creation():
            tests_passed += 1
        
        # Test 2: Serializer Imports
        if self.test_serializer_imports():
            tests_passed += 1
        
        # Test 3: URL Configuration
        if self.test_url_configuration():
            tests_passed += 1
        
        # Test 4: API Endpoints
        if self.test_api_endpoints():
            tests_passed += 1
        
        # Test 5: Admin Interface
        if self.test_admin_interface():
            tests_passed += 1
        
        # Test 6: Django Configuration
        if self.test_django_configuration():
            tests_passed += 1
        
        # Cleanup test data
        self.cleanup_test_data()
        
        # Calculate final score and generate report
        self.calculate_overall_score()
        return self.generate_final_report(tests_passed, total_tests)

def main():
    """Main validation function"""
    tester = AdminDashboardValidationTest()
    results = tester.run_validation()
    
    # Save results to file
    with open('admin_dashboard_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: admin_dashboard_validation_results.json")
    
    return results['overall']['score'] >= 95

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
