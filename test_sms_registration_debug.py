#!/usr/bin/env python
"""
Test Frontend SMS Registration with Error Capture
"""
import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
sys.path.insert(0, os.path.abspath('.'))
django.setup()

# Configure logging to show all messages
logging.basicConfig(level=logging.DEBUG)

from django.test import Client
import json

def test_sms_registration_with_logging():
    """Test SMS registration with detailed logging"""
    print("🔍 Testing SMS Registration with Error Capture")
    print("=" * 60)
    
    client = Client()
    
    # Test data with phone number
    test_data = {
        "username": "testsms123",
        "phone_number": "+233273735777",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "SMS"
    }
    
    print(f"📝 Test Data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Attempt registration
        print("\n📡 Making request to /api/v1/auth/register-frontend/")
        response = client.post(
            '/api/v1/auth/register-frontend/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Content: {response.content.decode()}")
        
        if response.status_code != 201:
            print("❌ Registration failed!")
            
            # Check if it's a serializer error
            try:
                response_data = response.json()
                print(f"📊 Parsed Response: {json.dumps(response_data, indent=2)}")
            except:
                print("📊 Could not parse response as JSON")
        else:
            print("✅ Registration successful!")
            response_data = response.json()
            print(f"📊 Success Response: {json.dumps(response_data, indent=2)}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_registration_with_logging()
