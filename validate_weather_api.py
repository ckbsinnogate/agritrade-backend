#!/usr/bin/env python
"""
Weather API Validation Script
Final validation to ensure the weather endpoint works
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.test import Client
from django.urls import reverse
import json

def validate_weather_api():
    print("🌤️ WEATHER API VALIDATION")
    print("=" * 50)
    
    client = Client()
    
    try:
        # Test weather current endpoint
        print("\n1. Testing /api/v1/weather/current/")
        response = client.get('/api/v1/weather/current/')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS! Weather endpoint is working!")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=4, default=str)[:500]}...")
        else:
            print(f"   ❌ FAILED! Status: {response.status_code}")
            print(f"   Response: {response.content}")
            
        # Test weather root endpoint
        print("\n2. Testing /api/v1/weather/")
        response = client.get('/api/v1/weather/')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Weather API root working!")
        else:
            print(f"   ❌ Weather API root failed: {response.status_code}")
            
        # Test with location parameter
        print("\n3. Testing with location parameter")
        response = client.get('/api/v1/weather/current/?location=Kumasi&region=Ashanti')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Location-based weather working!")
        else:
            print(f"   ❌ Location-based weather failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    validate_weather_api()
