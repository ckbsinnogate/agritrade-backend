#!/usr/bin/env python
"""
Simple SMS OTP API Test with debug
"""
import requests
import json

def test_simple():
    print("🔍 Simple SMS OTP Test")
    print("=" * 30)
    
    try:
        # Test the API directly
        url = "http://localhost:8000/api/auth/sms-otp/request/"
        data = {
            "phone_number": "+233273735500",
            "purpose": "login"
        }
        
        print(f"📡 Making request to: {url}")
        print(f"📨 Data: {data}")
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"💬 Response Text: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"📄 Response JSON: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
