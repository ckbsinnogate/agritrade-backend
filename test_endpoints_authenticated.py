#!/usr/bin/env python
"""
Test the three problematic endpoints with proper authentication
"""
import os
import sys
import django

# Setup Django
sys.path.append('c:\\Users\\user\\Desktop\\mywebproject\\backup_v1\\myapiproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from authentication.models import UserRole
import json

def test_endpoints():
    """Test the three problematic endpoints with authentication"""
    
    # Create client and get user model
    client = APIClient()
    User = get_user_model()
    
    # Create or get test admin user
    try:
        admin_role, created = UserRole.objects.get_or_create(name='ADMIN')
        user, created = User.objects.get_or_create(
            email='admin@test.com',
            defaults={
                'username': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            user.roles.add(admin_role)
        print(f'✅ User setup: {user.email} (Staff: {user.is_staff})')
    except Exception as e:
        print(f'❌ User setup error: {e}')
        return
    
    # Authenticate client
    client.force_authenticate(user=user)
    print('✅ Client authenticated')
    
    # Test the three problematic endpoints
    endpoints = [
        ('/api/v1/analytics/farmer-stats/', 'Analytics farmer-stats'),
        ('/api/v1/warehouses/inventory/optimize/', 'Warehouse inventory optimization'),
        ('/api/v1/advertisements/dashboard/', 'Advertisement dashboard')
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            print(f'\n🔍 Testing {description}: {endpoint}')
            response = client.get(endpoint)
            print(f'Status Code: {response.status_code}')
            
            if response.status_code == 200:
                print('✅ SUCCESS')
                data = response.json()
                results[endpoint] = {
                    'status': 'success',
                    'status_code': 200,
                    'has_data': 'data' in data or 'success' in data
                }
                if 'success' in data:
                    print(f'   Response success: {data["success"]}')
                else:
                    print(f'   Response keys: {list(data.keys())[:5]}')
            else:
                print('❌ FAILED')
                results[endpoint] = {
                    'status': 'failed',
                    'status_code': response.status_code
                }
                try:
                    error_data = response.json()
                    print(f'   Error: {error_data}')
                    results[endpoint]['error'] = error_data
                except:
                    content = response.content.decode('utf-8')[:200]
                    print(f'   Response content: {content}')
                    results[endpoint]['content'] = content
                        
        except Exception as e:
            print(f'❌ Exception testing {description}: {e}')
            results[endpoint] = {
                'status': 'exception',
                'error': str(e)
            }
    
    # Summary
    print('\n📋 SUMMARY:')
    print('=' * 50)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    for endpoint, result in results.items():
        status_icon = '✅' if result['status'] == 'success' else '❌'
        print(f'{status_icon} {endpoint}: {result["status"]} ({result.get("status_code", "N/A")})')
    
    print(f'\nOverall: {success_count}/{total_count} endpoints working')
    
    if success_count == total_count:
        print('🎉 ALL ENDPOINTS WORKING! Backend-frontend compatibility issues resolved.')
    else:
        print('⚠️  Some endpoints still need fixes.')
    
    return results

if __name__ == '__main__':
    test_endpoints()
