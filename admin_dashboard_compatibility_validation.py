#!/usr/bin/env python3
"""
Administrator Dashboard Compatibility Validation
Final verification test for all compatibility fixes

This script validates that all frontend compatibility issues have been resolved:
1. Individual system setting endpoints (404 errors fixed)
2. Content moderation action endpoints (404 errors fixed)
3. All endpoints return proper responses

Built with 40+ years of web development experience.
"""

import os
import sys
import django
import json
from datetime import datetime
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework import status

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
django.setup()

from admin_dashboard.models import SystemSettings, ContentModerationQueue

User = get_user_model()

class AdminDashboardCompatibilityTest:
    """Comprehensive compatibility validation"""
    
    def __init__(self):
        self.client = Client()
        self.results = {
            'test_run_time': datetime.now().isoformat(),
            'compatibility_fixes': {},
            'endpoint_tests': {},
            'overall_status': 'UNKNOWN',
            'issues_resolved': [],
            'remaining_issues': []
        }
        
    def setup_test_environment(self):
        """Setup test environment with admin user"""
        print("🔧 Setting up test environment...")
        
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        if created:
            admin_user.set_password('testpass123')
            admin_user.save()
            
        # Login as admin
        login_success = self.client.login(username='admin_test', password='testpass123')
        if not login_success:
            print("❌ Failed to login as admin user")
            return False
            
        print("✅ Test environment setup complete")
        return True
        
    def test_individual_system_setting_endpoints(self):
        """Test individual system setting endpoints that were causing 404s"""
        print("\n🧪 Testing Individual System Setting Endpoints...")
        
        test_results = {
            'maintenanceMode': {'tested': False, 'success': False, 'response_code': None},
            'emailVerificationRequired': {'tested': False, 'success': False, 'response_code': None},
            'userRegistrationEnabled': {'tested': False, 'success': False, 'response_code': None}
        }
        
        setting_keys = ['maintenanceMode', 'emailVerificationRequired', 'userRegistrationEnabled']
        
        for key in setting_keys:
            try:
                # Test GET request
                url = f'/api/v1/admin-dashboard/settings/system/{key}/'
                print(f"  📍 Testing GET {url}")
                
                response = self.client.get(url)
                test_results[key]['tested'] = True
                test_results[key]['response_code'] = response.status_code
                
                if response.status_code in [200, 201]:
                    print(f"    ✅ GET {key}: {response.status_code}")
                    test_results[key]['success'] = True
                    
                    # Test PUT request to update setting
                    put_data = {'value': 'true' if key == 'maintenanceMode' else 'false'}
                    put_response = self.client.put(
                        url, 
                        data=json.dumps(put_data),
                        content_type='application/json'
                    )
                    
                    if put_response.status_code in [200, 201]:
                        print(f"    ✅ PUT {key}: {put_response.status_code}")
                        test_results[key]['put_success'] = True
                    else:
                        print(f"    ⚠️  PUT {key}: {put_response.status_code}")
                        test_results[key]['put_success'] = False
                        
                else:
                    print(f"    ❌ GET {key}: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error testing {key}: {str(e)}")
                test_results[key]['error'] = str(e)
                
        self.results['compatibility_fixes']['individual_settings'] = test_results
        return test_results
        
    def test_content_moderation_endpoints(self):
        """Test content moderation action endpoints that were causing 404s"""
        print("\n🧪 Testing Content Moderation Action Endpoints...")
        
        test_results = {
            'approve_endpoint': {'tested': False, 'success': False, 'response_code': None},
            'reject_endpoint': {'tested': False, 'success': False, 'response_code': None}
        }
        
        # Create a test content moderation item
        try:
            content_item = ContentModerationQueue.objects.create(
                content_type='comment',
                content_title='Test Content for Validation',
                content_text='This is test content for validation',
                reported_by_username='test_user',
                status='PENDING',
                priority='MEDIUM'
            )
            
            # Test approve endpoint
            approve_url = f'/api/v1/admin-dashboard/content/moderation/{content_item.id}/approve/'
            print(f"  📍 Testing POST {approve_url}")
            
            approve_response = self.client.post(
                approve_url,
                data=json.dumps({'notes': 'Approved for testing'}),
                content_type='application/json'
            )
            
            test_results['approve_endpoint']['tested'] = True
            test_results['approve_endpoint']['response_code'] = approve_response.status_code
            
            if approve_response.status_code in [200, 201]:
                print(f"    ✅ POST approve: {approve_response.status_code}")
                test_results['approve_endpoint']['success'] = True
            else:
                print(f"    ❌ POST approve: {approve_response.status_code}")
                
            # Create another item for reject test
            content_item_2 = ContentModerationQueue.objects.create(
                content_type='post',
                content_title='Test Content for Rejection',
                content_text='This is test content for rejection',
                reported_by_username='test_user',
                status='PENDING',
                priority='MEDIUM'
            )
            
            # Test reject endpoint
            reject_url = f'/api/v1/admin-dashboard/content/moderation/{content_item_2.id}/reject/'
            print(f"  📍 Testing POST {reject_url}")
            
            reject_response = self.client.post(
                reject_url,
                data=json.dumps({'notes': 'Rejected for testing', 'reason': 'Test rejection'}),
                content_type='application/json'
            )
            
            test_results['reject_endpoint']['tested'] = True
            test_results['reject_endpoint']['response_code'] = reject_response.status_code
            
            if reject_response.status_code in [200, 201]:
                print(f"    ✅ POST reject: {reject_response.status_code}")
                test_results['reject_endpoint']['success'] = True
            else:
                print(f"    ❌ POST reject: {reject_response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error testing content moderation: {str(e)}")
            test_results['error'] = str(e)
            
        self.results['compatibility_fixes']['content_moderation'] = test_results
        return test_results
        
    def test_url_resolution(self):
        """Test that URLs properly resolve to view functions"""
        print("\n🧪 Testing URL Resolution...")
        
        url_tests = {
            'individual_setting': '/api/v1/admin-dashboard/settings/system/testKey/',
            'approve_content': '/api/v1/admin-dashboard/content/moderation/1/approve/',
            'reject_content': '/api/v1/admin-dashboard/content/moderation/1/reject/'
        }
        
        resolution_results = {}
        
        for name, url in url_tests.items():
            try:
                resolved = resolve(url)
                resolution_results[name] = {
                    'url': url,
                    'resolved': True,
                    'view_name': resolved.view_name,
                    'func_name': resolved.func.__name__ if hasattr(resolved, 'func') else 'N/A'
                }
                print(f"  ✅ {name}: {url} → {resolved.func.__name__}")
            except Exception as e:
                resolution_results[name] = {
                    'url': url,
                    'resolved': False,
                    'error': str(e)
                }
                print(f"  ❌ {name}: {url} → {str(e)}")
                
        self.results['endpoint_tests']['url_resolution'] = resolution_results
        return resolution_results
        
    def generate_compatibility_report(self):
        """Generate final compatibility report"""
        print("\n📊 Generating Compatibility Report...")
        
        # Count successful fixes
        individual_settings = self.results['compatibility_fixes'].get('individual_settings', {})
        content_moderation = self.results['compatibility_fixes'].get('content_moderation', {})
        
        # Individual settings success count
        settings_success = sum(1 for test in individual_settings.values() if test.get('success', False))
        total_settings = len(individual_settings)
        
        # Content moderation success count
        moderation_success = sum(1 for test in content_moderation.values() if test.get('success', False))
        total_moderation = len(content_moderation)
        
        # URL resolution success count
        url_resolution = self.results['endpoint_tests'].get('url_resolution', {})
        resolution_success = sum(1 for test in url_resolution.values() if test.get('resolved', False))
        total_resolution = len(url_resolution)
        
        # Determine overall status
        total_tests = total_settings + total_moderation + total_resolution
        total_success = settings_success + moderation_success + resolution_success
        
        if total_success == total_tests:
            self.results['overall_status'] = 'ALL_COMPATIBILITY_ISSUES_RESOLVED'
            self.results['issues_resolved'] = [
                f"Individual system setting endpoints: {settings_success}/{total_settings}",
                f"Content moderation action endpoints: {moderation_success}/{total_moderation}",
                f"URL resolution: {resolution_success}/{total_resolution}"
            ]
        else:
            self.results['overall_status'] = 'PARTIAL_COMPATIBILITY_RESOLUTION'
            self.results['remaining_issues'] = [
                f"Settings endpoints failing: {total_settings - settings_success}",
                f"Moderation endpoints failing: {total_moderation - moderation_success}",
                f"URL resolution failing: {total_resolution - resolution_success}"
            ]
            
        print(f"\n🎯 COMPATIBILITY STATUS: {self.results['overall_status']}")
        print(f"   Success Rate: {total_success}/{total_tests} ({(total_success/total_tests)*100:.1f}%)")
        
        return self.results
        
    def run_validation(self):
        """Run complete validation suite"""
        print("🚀 Starting Administrator Dashboard Compatibility Validation")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_environment():
            return False
            
        # Run tests
        self.test_individual_system_setting_endpoints()
        self.test_content_moderation_endpoints()
        self.test_url_resolution()
        
        # Generate report
        final_report = self.generate_compatibility_report()
        
        # Save results
        with open('admin_dashboard_compatibility_validation_results.json', 'w') as f:
            json.dump(final_report, f, indent=2)
            
        print(f"\n✅ Validation complete! Results saved to admin_dashboard_compatibility_validation_results.json")
        
        return final_report

def main():
    """Main execution function"""
    validator = AdminDashboardCompatibilityTest()
    results = validator.run_validation()
    
    if results['overall_status'] == 'ALL_COMPATIBILITY_ISSUES_RESOLVED':
        print("\n🎉 ALL COMPATIBILITY ISSUES HAVE BEEN SUCCESSFULLY RESOLVED!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Compatibility validation completed with status: {results['overall_status']}")
        sys.exit(1)

if __name__ == '__main__':
    main()
