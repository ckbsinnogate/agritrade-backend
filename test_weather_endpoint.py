#!/usr/bin/env python
"""
Test Weather Endpoint
"""
import requests
import json

def test_weather_endpoint():
    try:
        print("Testing weather endpoint...")
        response = requests.get('http://127.0.0.1:8000/api/v1/weather/current/')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Weather endpoint is working!")
            data = response.json()
            print("Response structure:")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure Django server is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_weather_endpoint()
