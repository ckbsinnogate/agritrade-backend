#!/usr/bin/env python
"""
Test login endpoint to debug 500 error
"""
import os
import sys
import django
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_login_endpoint():
    """Test the login endpoint with the exact data from frontend"""
    
    url = "http://127.0.0.1:8000/api/v1/auth/login/"
    data = {
        "identifier": "+233548577399",
        "password": "Kingsco45@1"
    }
    
    print("🔍 Testing login endpoint...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error detected!")
            
            # Check if user exists
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.get(phone_number="+233548577399")
                print(f"✅ User found: {user.phone_number} - {user.first_name} {user.last_name}")
                print(f"User is active: {user.is_active}")
                print(f"User roles: {[role.name for role in user.roles.all()]}")
            except User.DoesNotExist:
                print("❌ User does not exist in database")
                
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def check_authentication_views():
    """Check if authentication views are properly configured"""
    try:
        from authentication.views import LoginView
        print("✅ LoginView imported successfully")
        
        from authentication.serializers import LoginSerializer
        print("✅ LoginSerializer imported successfully")
        
        # Test serializer validation
        serializer = LoginSerializer(data={
            "identifier": "+233548577399",
            "password": "Kingsco45@1"
        })
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
        else:
            print(f"❌ Serializer validation failed: {serializer.errors}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error checking authentication views: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("  DEBUGGING LOGIN 500 ERROR")
    print("=" * 60)
    
    print("\n1. Checking authentication views...")
    check_authentication_views()
    
    print("\n2. Testing login endpoint...")
    test_login_endpoint()
    
    print("\n" + "=" * 60)
    print("  DEBUGGING COMPLETE")
    print("=" * 60)
