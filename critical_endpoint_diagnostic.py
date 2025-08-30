#!/usr/bin/env python3
"""
Critical Endpoint Diagnostic Script
Tests the specific 500/404 errors reported in the logs
"""
import os
import django
import requests
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.request import Request
from warehouses.views import inventory_optimization
from subscriptions.views import usage_stats, current_subscription

User = get_user_model()

def test_warehouse_optimization_direct():
    """Test warehouse optimization function directly"""
    print("🔍 Testing warehouse optimization directly...")
    
    try:
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            print("❌ No users found in database")
            return False
            
        # Create a GET request
        request = factory.get('/api/v1/warehouses/inventory/optimize/')
        request.user = user
        rest_request = Request(request)
        
        # Call the view function directly
        response = inventory_optimization(rest_request)
        
        print(f"✅ Direct call status: {response.status_code}")
        print(f"📊 Response: {response.data if hasattr(response, 'data') else 'No data'}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Direct call error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subscription_usage_stats_direct():
    """Test subscription usage stats function directly"""
    print("\n🔍 Testing subscription usage stats directly...")
    
    try:
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            print("❌ No users found in database")
            return False
            
        # Create a GET request
        request = factory.get('/api/v1/subscriptions/usage-stats/')
        request.user = user
        rest_request = Request(request)
        
        # Call the view function directly
        response = usage_stats(rest_request)
        
        print(f"✅ Direct call status: {response.status_code}")
        print(f"📊 Response: {response.data if hasattr(response, 'data') else 'No data'}")
        
        return response.status_code in [200, 404]  # 404 is acceptable if no subscription
        
    except Exception as e:
        print(f"❌ Direct call error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_current_subscription_direct():
    """Test current subscription function directly"""
    print("\n🔍 Testing current subscription directly...")
    
    try:
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            print("❌ No users found in database")
            return False
            
        # Create a GET request
        request = factory.get('/api/v1/subscriptions/current/')
        request.user = user
        rest_request = Request(request)
        
        # Call the view function directly
        response = current_subscription(rest_request)
        
        print(f"✅ Direct call status: {response.status_code}")
        print(f"📊 Response: {response.data if hasattr(response, 'data') else 'No data'}")
        
        return response.status_code in [200, 404]  # 404 is acceptable if no subscription
        
    except Exception as e:
        print(f"❌ Direct call error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_http_requests():
    """Test endpoints with actual HTTP requests (if server is running)"""
    print("\n🌐 Testing with HTTP requests...")
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        "/api/v1/warehouses/inventory/optimize/",
        "/api/v1/subscriptions/usage-stats/", 
        "/api/v1/subscriptions/current/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"📡 {endpoint}: {response.status_code} {response.reason}")
            
            if response.status_code not in [200, 401, 404]:
                print(f"   ⚠️  Unexpected status code")
                
        except requests.exceptions.ConnectionError:
            print(f"📡 {endpoint}: Connection failed (server not running)")
        except Exception as e:
            print(f"📡 {endpoint}: Error - {e}")

def main():
    print("🚀 Critical Endpoint Diagnostic")
    print("=" * 50)
    
    results = {
        'warehouse_optimization': test_warehouse_optimization_direct(),
        'subscription_usage_stats': test_subscription_usage_stats_direct(),
        'current_subscription': test_current_subscription_direct()
    }
    
    print("\n📊 Direct Function Test Results:")
    print("-" * 40)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Test HTTP requests if possible
    test_with_http_requests()
    
    print("\n🎯 Summary:")
    if all(results.values()):
        print("✅ All direct function calls working")
    else:
        print("❌ Some direct function calls failing")
        
    print("\n💡 Next Steps:")
    print("1. Fix any failing direct function calls")
    print("2. Start Django server: python manage.py runserver")
    print("3. Test endpoints with HTTP requests")

if __name__ == "__main__":
    main()
