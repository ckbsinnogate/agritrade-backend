#!/usr/bin/env python
"""
Complete Authentication Flow Test
Test the entire login process to verify frontend-backend connectivity
"""

import os
import sys
import django
import requests
import json
from time import sleep

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_complete_auth_flow():
    """Test the complete authentication flow"""
    print("🔐 COMPLETE AUTHENTICATION FLOW TEST")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: API Root Endpoint
    print("\n1️⃣ Testing API Root Endpoint")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/api/v1/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API Root accessible")
        else:
            print("   ❌ API Root not accessible")
    except Exception as e:
        print(f"   ❌ API Root error: {e}")
    
    # Test 2: Authentication Root Endpoint
    print("\n2️⃣ Testing Authentication Root Endpoint")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/api/v1/auth/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Auth endpoints accessible")
            data = response.json()
            print(f"   📋 Available endpoints: {list(data.keys())}")
        else:
            print("   ❌ Auth endpoints not accessible")
    except Exception as e:
        print(f"   ❌ Auth endpoints error: {e}")
    
    # Test 3: Login Endpoint with Test User
    print("\n3️⃣ Testing Login Endpoint")
    print("-" * 40)
    
    login_data = {
        "identifier": "+233548577399",
        "password": "Kingsco45@1"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ LOGIN SUCCESSFUL!")
            data = response.json()
            
            # Check response structure
            if 'access' in data:
                print(f"   🎫 Access token received (length: {len(data['access'])})")
            if 'refresh' in data:
                print(f"   🔄 Refresh token received (length: {len(data['refresh'])})")
            if 'user' in data:
                user_data = data['user']
                print(f"   👤 User data received:")
                print(f"      - ID: {user_data.get('id')}")
                print(f"      - Username: {user_data.get('username')}")
                print(f"      - Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"      - Phone: {user_data.get('phone_number')}")
                print(f"      - Roles: {user_data.get('roles')}")
                print(f"      - Roles Display: {user_data.get('roles_display')}")
                print(f"      - Verified: {user_data.get('is_verified')}")
                
                # Test 4: Protected Endpoint with Token
                print("\n4️⃣ Testing Protected Endpoint with Token")
                print("-" * 40)
                
                access_token = data.get('access')
                if access_token:
                    try:
                        profile_response = requests.get(
                            f"{base_url}/api/v1/auth/profile/",
                            headers={
                                'Authorization': f'Bearer {access_token}',
                                'Content-Type': 'application/json'
                            },
                            timeout=5
                        )
                        
                        print(f"   Status: {profile_response.status_code}")
                        if profile_response.status_code == 200:
                            print("   ✅ Protected endpoint accessible with token")
                            profile_data = profile_response.json()
                            print(f"   👤 Profile data: {json.dumps(profile_data, indent=6, default=str)}")
                        else:
                            print("   ❌ Protected endpoint not accessible")
                            print(f"   Error: {profile_response.text}")
                    except Exception as e:
                        print(f"   ❌ Protected endpoint error: {e}")
                else:
                    print("   ❌ No access token received")
            else:
                print("   ⚠️  No user data in response")
                
        elif response.status_code == 400:
            print("   ❌ LOGIN FAILED - Bad Request")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=6)}")
            except:
                print(f"   Raw error: {response.text}")
        elif response.status_code == 401:
            print("   ❌ LOGIN FAILED - Invalid Credentials")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=6)}")
            except:
                print(f"   Raw error: {response.text}")
        elif response.status_code == 500:
            print("   ❌ LOGIN FAILED - Internal Server Error")
            print("   🚨 This indicates the fix may not have resolved all issues")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=6)}")
            except:
                print(f"   Raw error: {response.text}")
        else:
            print(f"   ❌ LOGIN FAILED - Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - Is the Django server running?")
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

def test_serializer_directly():
    """Test UserProfileSerializer directly"""
    print("\n🔍 DIRECT SERIALIZER TEST")
    print("=" * 60)
    
    try:
        from django.contrib.auth import get_user_model
        from authentication.serializers import UserProfileSerializer
        
        User = get_user_model()
        
        # Get test user
        user = User.objects.filter(phone_number="+233548577399").first()
        
        if user:
            print(f"✅ Found test user: {user.username}")
            print(f"📱 Phone: {user.phone_number}")
            print(f"🎭 Roles count: {user.roles.count()}")
            
            # List user roles
            if user.roles.exists():
                roles = [role.name for role in user.roles.all()]
                print(f"🎭 User roles: {roles}")
            else:
                print("⚠️  User has no roles assigned")
            
            # Test serializer
            try:
                serializer = UserProfileSerializer(user)
                data = serializer.data
                print("✅ UserProfileSerializer works correctly!")
                print(f"📄 Serialized data:")
                print(json.dumps(data, indent=4, default=str))
                
            except Exception as e:
                print(f"❌ Serializer error: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("❌ Test user not found in database")
            
            # Check if any users exist
            total_users = User.objects.count()
            print(f"📊 Total users in database: {total_users}")
            
            if total_users > 0:
                sample_user = User.objects.first()
                print(f"📝 Sample user: {sample_user.username} ({sample_user.phone_number or sample_user.email})")
                
    except Exception as e:
        print(f"❌ Direct serializer test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serializer_directly()
    test_complete_auth_flow()
    
    print("\n🎯 CONCLUSION")
    print("=" * 60)
    print("If all tests pass, the frontend-backend connectivity issue is resolved!")
    print("The React frontend should now be able to successfully authenticate users.")
