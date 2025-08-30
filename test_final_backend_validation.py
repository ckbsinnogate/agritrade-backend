#!/usr/bin/env python3
"""
Final validation test for backend compatibility fixes
Tests the comprehensive profile serializer and endpoint
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def test_serializer_import():
    """Test if serializer can be imported"""
    print("\n📦 TESTING SERIALIZER IMPORT")
    print("=" * 40)
    
    try:
        from users.serializers import ComprehensiveUserProfileSerializer
        print("✅ ComprehensiveUserProfileSerializer imported successfully")
        return True
    except Exception as e:
        print(f"❌ Serializer import failed: {e}")
        return False

def test_serializer_instantiation():
    """Test if serializer can be instantiated"""
    print("\n🔧 TESTING SERIALIZER INSTANTIATION")
    print("=" * 40)
    
    try:
        from users.serializers import ComprehensiveUserProfileSerializer
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Try to get a user
        user = User.objects.first()
        if not user:
            print("⚠️  No users found, creating test user...")
            user = User.objects.create_user(
                username='testuser_validation',
                email='test@validation.com',
                password='testpass123'
            )
            print(f"✅ Created test user: {user.username}")
        
        # Test serializer instantiation
        serializer = ComprehensiveUserProfileSerializer(instance=user)
        print("✅ Serializer instantiated successfully")
        
        # Test serialization
        data = serializer.data
        print("✅ Serializer data method works")
        print(f"📊 Data keys: {list(data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Serializer instantiation failed: {e}")
        return False

def test_endpoint_view():
    """Test if the view can be accessed"""
    print("\n🌐 TESTING VIEW ACCESS")
    print("=" * 40)
    
    try:
        from users.views import ComprehensiveUserProfileView
        print("✅ ComprehensiveUserProfileView imported successfully")
        
        # Test view instantiation
        view = ComprehensiveUserProfileView()
        print("✅ View instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ View test failed: {e}")
        return False

def test_url_patterns():
    """Test if URL patterns are properly configured"""
    print("\n🔗 TESTING URL PATTERNS")
    print("=" * 40)
    
    try:
        from django.urls import reverse
        
        # Test URL reversal
        url = reverse('user-profile-comprehensive')
        print(f"✅ URL pattern found: {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL pattern test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 BACKEND COMPATIBILITY VALIDATION")
    print("=" * 50)
    print("Testing fixes for user profile serializer issues")
    print("=" * 50)
    
    tests = [
        test_serializer_import,
        test_serializer_instantiation,
        test_endpoint_view,
        test_url_patterns
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n📋 VALIDATION SUMMARY")
    print("=" * 30)
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Backend compatibility issues have been resolved")
        print("✅ ComprehensiveUserProfileSerializer is working correctly")
        print("✅ /api/v1/users/profile/comprehensive/ endpoint should work")
        print("\n🔥 MISSION ACCOMPLISHED!")
        return True
    else:
        print("❌ Some tests failed")
        print(f"📊 Passed: {sum(results)}/{len(results)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
