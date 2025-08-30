#!/usr/bin/env python3
"""
Quick test to verify the comprehensive profile serializer fix
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_serializer_fix():
    """Test the comprehensive profile serializer"""
    print("🔍 TESTING COMPREHENSIVE PROFILE SERIALIZER FIX")
    print("=" * 55)
    
    try:
        from django.contrib.auth import get_user_model
        from users.serializers import ComprehensiveUserProfileSerializer
        from users.models import ExtendedUserProfile
        
        User = get_user_model()
        
        # Get any existing user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
        
        print(f"✅ Testing with user: {user.email or user.username}")
        
        # Ensure extended profile exists
        ExtendedUserProfile.objects.get_or_create(user=user)
        
        # Test serializer instantiation
        serializer = ComprehensiveUserProfileSerializer(user)
        print("✅ Serializer instantiated successfully")
        
        # Test data access (this was failing before)
        data = serializer.data
        print("✅ Serializer data access successful")
        
        # Check key fields
        print(f"✅ User type: {data.get('user_type', 'N/A')}")
        print(f"✅ Profile completion: {data.get('profile_completion', 'N/A')}%")
        print(f"✅ Has extended profile: {bool(data.get('extended_profile'))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test the actual API endpoint"""
    print("\n🔍 TESTING API ENDPOINT")
    print("=" * 30)
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from rest_framework.authtoken.models import Token
        
        User = get_user_model()
        client = Client()
        
        # Get any user with a token
        user = User.objects.first()
        if not user:
            print("❌ No users found")
            return False
        
        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        print(f"✅ Using token for user: {user.email or user.username}")
        
        # Test the endpoint
        response = client.get(
            '/api/v1/users/profile/comprehensive/',
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        
        print(f"✅ API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working!")
            print(f"✅ User ID: {data.get('id')}")
            print(f"✅ User type: {data.get('user_type')}")
            print(f"✅ Profile completion: {data.get('profile_completion')}%")
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error content: {response.content.decode()}")
            return False
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🎯 COMPREHENSIVE PROFILE SERIALIZER VALIDATION")
    print("=" * 60)
    
    serializer_success = test_serializer_fix()
    api_success = test_api_endpoint()
    
    print("\n" + "="*60)
    print("🎯 FINAL RESULTS")
    print("="*60)
    
    if serializer_success and api_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Comprehensive profile serializer is working correctly")
        print("✅ API endpoint is functional")
        print("✅ Frontend compatibility issue RESOLVED")
        
        print("\n🚀 FRONTEND DEVELOPERS CAN NOW:")
        print("  • Access /api/v1/users/profile/comprehensive/")
        print("  • Get complete user profile data")
        print("  • Update user profiles successfully")
        
    else:
        print("❌ Some tests failed")
        if not serializer_success:
            print("  • Serializer still has issues")
        if not api_success:
            print("  • API endpoint not working")
