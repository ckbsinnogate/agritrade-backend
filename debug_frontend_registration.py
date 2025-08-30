#!/usr/bin/env python
"""
Debug Frontend Registration Issue
"""
import os
import sys
import django
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
sys.path.insert(0, os.path.abspath('.'))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

def debug_frontend_registration():
    """Debug the frontend registration endpoint"""
    print("🔍 Debugging Frontend Registration Endpoint")
    print("=" * 50)
    
    client = Client()
    
    # Test data
    test_data = {
        "username": "debuguser123",
        "phone_number": "+233273735997",
        "password": "TestPass123!",
        "first_name": "Debug",
        "last_name": "User"
    }
    
    print(f"📝 Test Data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Attempt registration
        response = client.post(
            '/api/v1/auth/register-frontend/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Content: {response.content.decode()}")
        
        if response.status_code != 201:
            print("❌ Registration failed!")
            
            # Try to get the response data
            try:
                response_data = response.json()
                print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print("📊 Could not parse response as JSON")
        else:
            print("✅ Registration successful!")
            response_data = response.json()
            print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {str(e)}")
        print(f"📚 Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_frontend_registration()
