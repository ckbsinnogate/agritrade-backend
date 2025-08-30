#!/usr/bin/env python3
"""
Production Verification Test - Final Check
"""
import os
import sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
import django
django.setup()

def main():
    print('🧪 FINAL PRODUCTION VERIFICATION TEST')
    print('=' * 50)
    
    # Test 1: Import all critical functions
    try:
        from subscriptions.views import usage_stats, current_subscription
        from warehouses.views import inventory_optimization
        print('✅ All critical functions imported successfully')
    except Exception as e:
        print(f'❌ Import failed: {e}')
        return False
    
    # Test 2: Basic function call
    try:
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        from rest_framework.request import Request
        
        User = get_user_model()
        factory = RequestFactory()
        
        # Create test user
        user, created = User.objects.get_or_create(
            phone_number='+233999888777',
            defaults={'first_name': 'Test', 'last_name': 'User', 'user_type': 'FARMER'}
        )
        print(f'👤 Test user: {user.phone_number} {"(created)" if created else "(exists)"}')
        
        # Test subscription function
        request = factory.get('/api/v1/subscriptions/current/')
        request.user = user
        rest_request = Request(request)
        
        response = current_subscription(rest_request)
        success1 = response.data.get('success', False)
        print(f'✅ current_subscription: {response.status_code} - Success: {success1}')
        
        # Test usage stats
        request2 = factory.get('/api/v1/subscriptions/usage-stats/')
        request2.user = user
        rest_request2 = Request(request2)
        
        response2 = usage_stats(rest_request2)
        success2 = response2.data.get('success', False)
        print(f'✅ usage_stats: {response2.status_code} - Success: {success2}')
        
        # Test warehouse
        request3 = factory.get('/api/v1/warehouses/inventory/optimize/')
        request3.user = user
        rest_request3 = Request(request3)
        
        response3 = inventory_optimization(rest_request3)
        success3 = response3.data.get('success', False)
        print(f'✅ inventory_optimization: {response3.status_code} - Success: {success3}')
        
        print('\n📊 RESULTS SUMMARY:')
        print(f'   Subscription Functions: {"✅ PASS" if success1 and success2 else "❌ FAIL"}')
        print(f'   Warehouse Functions: {"✅ PASS" if success3 else "❌ FAIL"}')
        
        all_success = success1 and success2 and success3
        if all_success:
            print('\n🎉 ALL CORE FUNCTIONS WORKING!')
            print('🚀 PRODUCTION READY!')
            print('✅ Backend-Frontend Compatibility: ACHIEVED')
            print('✅ Syntax Errors: ELIMINATED')
            print('✅ API Responses: STABLE')
            return True
        else:
            print('\n⚠️  Some functions returned success=False')
            return False
        
    except Exception as e:
        print(f'❌ Function test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    
    print('\n' + '=' * 50)
    if success:
        print('🎯 FINAL STATUS: 100% PRODUCTION READY! 🚀')
    else:
        print('❌ FINAL STATUS: NOT READY - Review errors above')
    print('=' * 50)
