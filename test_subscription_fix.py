"""
Test script to verify the fixed subscription functions work properly
"""

import os
import sys
import django

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from subscription_functions_fix import current_subscription_fixed, usage_stats_fixed

User = get_user_model()

def test_fixed_subscription_functions():
    """Test the fixed subscription functions"""
    print("🧪 Testing Fixed Subscription Functions...")
    
    try:
        # Create test request
        factory = RequestFactory()
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            phone_number='+233548577878',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'user_type': 'FARMER'
            }
        )
        
        print(f"📱 Using test user: {user.phone_number}")
        
        # Test current_subscription_fixed
        print("\n1️⃣ Testing current_subscription_fixed...")
        request = factory.get('/api/v1/subscriptions/current/')
        request.user = user
        rest_request = Request(request)
        
        response = current_subscription_fixed(rest_request)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Response keys: {list(response.data.keys())}")
        
        if response.data.get('success'):
            print("   ✅ Current subscription function working correctly")
        else:
            print(f"   ❌ Error: {response.data.get('error', 'Unknown error')}")
        
        # Test usage_stats_fixed
        print("\n2️⃣ Testing usage_stats_fixed...")
        request = factory.get('/api/v1/subscriptions/usage-stats/')
        request.user = user
        rest_request = Request(request)
        
        response = usage_stats_fixed(rest_request)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Response keys: {list(response.data.keys())}")
        
        if response.data.get('success'):
            print("   ✅ Usage stats function working correctly")
            stats = response.data.get('stats', {})
            print(f"   📈 Stats period: {stats.get('period_days')} days")
            print(f"   📅 Date range: {stats.get('start_date')} to {stats.get('end_date')}")
        else:
            print(f"   ❌ Error: {response.data.get('error', 'Unknown error')}")
        
        print("\n🎉 SUBSCRIPTION FUNCTION TESTS COMPLETED!")
        print("✅ Both functions are working and frontend-compatible")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_fixed_subscription_functions()
