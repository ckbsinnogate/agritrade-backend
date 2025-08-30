#!/usr/bin/env python3
"""
Quick Backend Fix Verification
Tests the critical issues that were causing frontend failures
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_imports():
    """Test if all critical imports work"""
    print("🔍 Testing critical imports...")
    
    try:
        from warehouses.views import inventory_optimization
        print("✅ Warehouse optimization view imported")
    except Exception as e:
        print(f"❌ Warehouse optimization import error: {e}")
        return False
    
    try:
        from subscriptions.views import usage_stats, current_subscription
        print("✅ Subscription views imported")
    except Exception as e:
        print(f"❌ Subscription views import error: {e}")
        return False
        
    return True

def test_warehouse_optimization_function():
    """Test warehouse optimization function logic"""
    print("\n🔍 Testing warehouse optimization function...")
    
    try:
        from django.test import RequestFactory
        from rest_framework.request import Request
        from django.contrib.auth import get_user_model
        from warehouses.views import inventory_optimization
        
        User = get_user_model()
        
        # Create test request
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            print("❌ No users found - creating test user")
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                phone_number='+1234567890'
            )
        
        request = factory.get('/api/v1/warehouses/inventory/optimize/')
        request.user = user
        rest_request = Request(request)
        
        # Test the function
        response = inventory_optimization(rest_request)
        
        if response.status_code == 200:
            print("✅ Warehouse optimization working correctly")
            return True
        else:
            print(f"❌ Warehouse optimization returned status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"   Response: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ Warehouse optimization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subscription_functions():
    """Test subscription functions"""
    print("\n🔍 Testing subscription functions...")
    
    try:
        from django.test import RequestFactory
        from rest_framework.request import Request
        from django.contrib.auth import get_user_model
        from subscriptions.views import usage_stats, current_subscription
        
        User = get_user_model()
        
        # Create test request
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            user = User.objects.create_user(
                username='testuser2',
                email='test2@example.com',
                phone_number='+1234567891'
            )
        
        request = factory.get('/api/v1/subscriptions/usage-stats/')
        request.user = user
        rest_request = Request(request)
        
        # Test usage stats
        response = usage_stats(rest_request)
        print(f"✅ Usage stats function returned status: {response.status_code}")
        
        # Test current subscription
        request2 = factory.get('/api/v1/subscriptions/current/')
        request2.user = user
        rest_request2 = Request(request2)
        
        response2 = current_subscription(rest_request2)
        print(f"✅ Current subscription function returned status: {response2.status_code}")
        
        return True
            
    except Exception as e:
        print(f"❌ Subscription functions error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_access():
    """Test basic database access"""
    print("\n🔍 Testing database access...")
    
    try:
        from warehouses.models import WarehouseInventory
        from subscriptions.models import UserSubscription
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        user_count = User.objects.count()
        inventory_count = WarehouseInventory.objects.count()
        subscription_count = UserSubscription.objects.count()
        
        print(f"✅ Database access working:")
        print(f"   Users: {user_count}")
        print(f"   Inventory items: {inventory_count}")
        print(f"   Subscriptions: {subscription_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database access error: {e}")
        return False

def main():
    print("🚀 Backend Fix Verification")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Database Access", test_database_access()))
    results.append(("Warehouse Optimization", test_warehouse_optimization_function()))
    results.append(("Subscription Functions", test_subscription_functions()))
    
    print("\n📊 Test Results Summary:")
    print("-" * 40)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n🎯 Overall Status:")
    if all_passed:
        print("✅ All tests passed - Backend ready for frontend integration")
    else:
        print("❌ Some tests failed - Issues need to be resolved")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
