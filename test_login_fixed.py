#!/usr/bin/env python
"""
Test login endpoint after fixing UserProfileSerializer
"""

import os
import sys
import django
import requests
import json

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_login_api():
    """Test the login API endpoint"""
    print("🔍 Testing Login API Endpoint After Fix")
    print("=" * 50)
    
    # Test data
    login_data = {
        "identifier": "+233548577399",
        "password": "Kingsco45@1"
    }
    
    try:
        # Make API request
        url = "http://127.0.0.1:8000/api/v1/auth/login/"
        headers = {'Content-Type': 'application/json'}
        
        print(f"📡 Making POST request to: {url}")
        print(f"📋 Request data: {login_data}")
        
        response = requests.post(url, json=login_data, headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ LOGIN SUCCESSFUL!")
            response_data = response.json()
            print(f"🎉 Response Data: {json.dumps(response_data, indent=2)}")
            
            # Check if user profile is included
            if 'user' in response_data:
                user_data = response_data['user']
                print(f"\n👤 User Profile Data:")
                print(f"   - ID: {user_data.get('id')}")
                print(f"   - Username: {user_data.get('username')}")
                print(f"   - Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"   - Email: {user_data.get('email')}")
                print(f"   - Phone: {user_data.get('phone_number')}")
                print(f"   - Roles: {user_data.get('roles')}")
                print(f"   - Roles Display: {user_data.get('roles_display')}")
                print(f"   - Country: {user_data.get('country')}")
                print(f"   - Verified: {user_data.get('is_verified')}")
                
        else:
            print(f"❌ LOGIN FAILED!")
            try:
                error_data = response.json()
                print(f"🚨 Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"🚨 Raw Response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

def test_user_profile_serializer():
    """Test UserProfileSerializer directly"""
    print("\n🔍 Testing UserProfileSerializer Directly")
    print("=" * 50)
    
    try:
        from django.contrib.auth import get_user_model
        from authentication.serializers import UserProfileSerializer
        
        User = get_user_model()
        
        # Get the test user
        user = User.objects.filter(phone_number="+233548577399").first()
        
        if user:
            print(f"👤 Found user: {user.username}")
            print(f"📱 Phone: {user.phone_number}")
            print(f"🎭 Roles count: {user.roles.count()}")
            
            # Test the serializer
            serializer = UserProfileSerializer(user)
            data = serializer.data
            
            print(f"✅ Serializer worked successfully!")
            print(f"📄 Serialized data: {json.dumps(data, indent=2)}")
            
        else:
            print("❌ Test user not found")
            
    except Exception as e:
        print(f"❌ Serializer Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_profile_serializer()
    test_login_api()
