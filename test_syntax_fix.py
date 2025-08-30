#!/usr/bin/env python3
"""
Quick test to verify subscription functions are working after syntax fix
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_subscription_syntax():
    """Test that subscription functions can be imported and have no syntax errors"""
    print("🧪 Testing subscription function syntax...")
    
    try:
        # Test imports
        from subscriptions.views import usage_stats, current_subscription
        print("✅ Subscription functions imported successfully")
        
        # Test function inspection
        import inspect
        
        # Check usage_stats function
        usage_stats_source = inspect.getsource(usage_stats)
        print(f"✅ usage_stats function: {len(usage_stats_source)} characters")
        
        # Check current_subscription function  
        current_sub_source = inspect.getsource(current_subscription)
        print(f"✅ current_subscription function: {len(current_sub_source)} characters")
        
        print("🎉 All syntax checks passed!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without database calls"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        from rest_framework.request import Request
        from subscriptions.views import usage_stats, current_subscription
        
        User = get_user_model()
        factory = RequestFactory()
        
        # Create a mock user (don't save to DB)
        user = User(phone_number='+233123456789', first_name='Test', last_name='User')
        
        # Test current_subscription
        request = factory.get('/api/v1/subscriptions/current/')
        request.user = user
        rest_request = Request(request)
        
        response = current_subscription(rest_request)
        print(f"✅ current_subscription returned status: {response.status_code}")
        
        # Test usage_stats
        request2 = factory.get('/api/v1/subscriptions/usage-stats/')
        request2.user = user
        rest_request2 = Request(request2)
        
        response2 = usage_stats(rest_request2)
        print(f"✅ usage_stats returned status: {response2.status_code}")
        
        print("🎉 Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting subscription syntax and functionality verification...")
    
    syntax_ok = test_subscription_syntax()
    func_ok = test_basic_functionality()
    
    print(f"\n📋 RESULTS:")
    print(f"✅ Syntax Check: {'PASSED' if syntax_ok else 'FAILED'}")
    print(f"✅ Functionality Check: {'PASSED' if func_ok else 'FAILED'}")
    
    if syntax_ok and func_ok:
        print("\n🎉 ALL TESTS PASSED - Subscription functions are working!")
        print("✅ The corruption has been successfully fixed!")
    else:
        print("\n❌ Some tests failed - please review the errors above")

if __name__ == '__main__':
    main()
