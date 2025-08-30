#!/usr/bin/env python3
"""
Test script to verify the login endpoint works correctly
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
django.setup()

def test_login_endpoint():
    """Test the login endpoint with the correct credentials"""
    
    # Test data
    login_data = {
        "identifier": "+233548577399",
        "password": "Kingsco45@1"
    }
    
    url = "http://127.0.0.1:8000/api/v1/auth/login/"
    
    print("Testing login endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(login_data, indent=2)}")
    
    try:
        # Make the request
        response = requests.post(
            url,
            json=login_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
        except ValueError:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            if 'access' in response_data:
                print(f"Access token received: {response_data['access'][:50]}...")
            return True
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure Django server is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_login_endpoint()
