#!/usr/bin/env python3
"""
Test script to verify the comprehensive profile serializer fix
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_comprehensive_profile_serializer():
    """Test the fixed comprehensive profile serializer"""
    print("🔍 TESTING COMPREHENSIVE PROFILE SERIALIZER FIX")
    print("=" * 55)
    
    try:
        # Import all necessary components
        from django.contrib.auth import get_user_model
        from authentication.models import UserRole
        from users.models import ExtendedUserProfile, FarmerProfile
        from users.serializers import ComprehensiveUserProfileSerializer
        
        User = get_user_model()
        
        print("✅ All imports successful")
        
        # Create test user
        test_email = 'comprehensive.test@agriconnect.com'
        User.objects.filter(email=test_email).delete()  # Cleanup
        
        test_user = User.objects.create_user(
            identifier=test_email,
            password='ComprehensiveTest123!',
            first_name='Comprehensive',
            last_name='TestUser',
            roles=['CONSUMER']
        )
        
        print(f"✅ Test user created: {test_user.email}")
        
        # Create extended profile
        extended_profile, created = ExtendedUserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'bio': 'Test comprehensive profile user',
                'gender': 'male',
                'city': 'Accra',
                'address_line_1': '123 Test Street'
            }
        )
        
        print(f"✅ Extended profile created: {created}")
        
        # Test serializer instantiation
        serializer = ComprehensiveUserProfileSerializer(test_user)
        print("✅ Serializer instantiation successful")
        
        # Test data access
        profile_data = serializer.data
        print("✅ Serializer data access successful")
        
        # Check key fields
        print(f"✅ User ID: {profile_data.get('id')}")
        print(f"✅ Username: {profile_data.get('username')}")
        print(f"✅ Full name: {profile_data.get('first_name')} {profile_data.get('last_name')}")
        print(f"✅ Email: {profile_data.get('email')}")
        print(f"✅ User type: {profile_data.get('user_type')}")
        print(f"✅ Roles: {profile_data.get('roles_display')}")
        print(f"✅ Profile completion: {profile_data.get('profile_completion')}%")
        
        # Check extended profile
        extended_data = profile_data.get('extended_profile')
        if extended_data:
            print(f"✅ Extended profile found:")
            print(f"   - Bio: {extended_data.get('bio')}")
            print(f"   - City: {extended_data.get('city')}")
            print(f"   - Gender: {extended_data.get('gender')}")
        else:
            print("⚠️ Extended profile data not found")
        
        # Clean up
        test_user.delete()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test the API endpoint with Django test client"""
    print("\n🔍 TESTING API ENDPOINT")
    print("=" * 30)
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from rest_framework.authtoken.models import Token
        
        User = get_user_model()
        client = Client()
        
        # Create test user with token
        test_email = 'endpoint.test@agriconnect.com'
        User.objects.filter(email=test_email).delete()  # Cleanup
        
        test_user = User.objects.create_user(
            identifier=test_email,
            password='EndpointTest123!',
            first_name='Endpoint',
            last_name='TestUser',
            roles=['CONSUMER']
        )
        
        # Create token for authentication
        token, created = Token.objects.get_or_create(user=test_user)
        
        print(f"✅ Test user created with token")
        
        # Test the endpoint
        response = client.get(
            '/api/v1/users/profile/comprehensive/',
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        
        print(f"✅ API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response data received:")
            print(f"   - User ID: {data.get('id')}")
            print(f"   - Email: {data.get('email')}")
            print(f"   - User type: {data.get('user_type')}")
            print(f"   - Profile completion: {data.get('profile_completion')}%")
        else:
            print(f"❌ API error: {response.content.decode()}")
            return False
        
        # Clean up
        test_user.delete()
        print("✅ Endpoint test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🎯 COMPREHENSIVE PROFILE SERIALIZER VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Serializer Functionality", test_comprehensive_profile_serializer),
        ("API Endpoint", test_api_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*60}")
    print("🎯 FINAL RESULTS")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Comprehensive profile serializer is working correctly")
        print("✅ API endpoint is functional")
        print("✅ Frontend can now access comprehensive profiles")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
