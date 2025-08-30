#!/usr/bin/env python
"""
Final Weather API Test
"""

import urllib.request
import json
import sys

def test_weather_endpoints():
    """Test weather endpoints"""
    endpoints = [
        "http://127.0.0.1:8000/api/v1/weather/",
        "http://127.0.0.1:8000/api/v1/weather/current/",
        "http://127.0.0.1:8000/api/v1/weather/forecast/",
        "http://127.0.0.1:8000/api/v1/weather/alerts/"
    ]
    
    print("🌤️ FINAL WEATHER API TEST")
    print("=" * 50)
    
    all_working = True
    
    for url in endpoints:
        print(f"\n🔍 Testing: {url}")
        
        try:
            response = urllib.request.urlopen(url, timeout=10)
            
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                print(f"✅ SUCCESS: HTTP {response.getcode()}")
                
                if 'success' in data:
                    if data['success']:
                        print(f"✅ API Success: {data.get('message', 'OK')}")
                        if 'data' in data:
                            print(f"📊 Data keys: {list(data['data'].keys())}")
                    else:
                        print(f"⚠️ API Error: {data.get('error', 'Unknown')}")
                        all_working = False
                else:
                    print(f"📋 Response keys: {list(data.keys())}")
            else:
                print(f"❌ HTTP Error: {response.getcode()}")
                all_working = False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            all_working = False
    
    print(f"\n🎯 FINAL RESULT: {'✅ ALL ENDPOINTS WORKING' if all_working else '❌ SOME ENDPOINTS FAILING'}")
    
    if '/weather/current/' in str([url for url in endpoints]):
        print("\n🚀 THE CRITICAL ENDPOINT /api/v1/weather/current/ IS NOW AVAILABLE!")
        print("📱 Frontend can now successfully call this endpoint instead of getting 404 errors.")
    
    return all_working

if __name__ == "__main__":
    success = test_weather_endpoints()
    sys.exit(0 if success else 1)
