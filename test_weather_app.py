#!/usr/bin/env python
"""
Weather App Testing Script
Test the weather endpoints to ensure they're working properly
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_weather_endpoints():
    """Test all weather endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🌤️ TESTING WEATHER APP ENDPOINTS")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        "/api/v1/weather/",
        "/api/v1/weather/current/",
        "/api/v1/weather/forecast/",
        "/api/v1/weather/alerts/",
    ]
    
    results = {}
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            status_code = response.status_code
            
            if status_code == 200:
                print(f"✅ SUCCESS: {status_code}")
                try:
                    data = response.json()
                    print(f"📊 Response keys: {list(data.keys())}")
                    results[endpoint] = {"status": "SUCCESS", "code": status_code, "data": data}
                except:
                    print(f"⚠️  Non-JSON response")
                    results[endpoint] = {"status": "SUCCESS", "code": status_code, "data": "Non-JSON"}
            else:
                print(f"❌ FAILED: {status_code}")
                results[endpoint] = {"status": "FAILED", "code": status_code}
                
        except requests.exceptions.ConnectionError:
            print(f"🔌 CONNECTION ERROR: Server not running")
            results[endpoint] = {"status": "CONNECTION_ERROR", "code": None}
        except Exception as e:
            print(f"⚠️  ERROR: {str(e)}")
            results[endpoint] = {"status": "ERROR", "code": None, "error": str(e)}
    
    return results

def test_database_tables():
    """Test if weather database tables exist"""
    print("\n📊 TESTING WEATHER DATABASE TABLES")
    print("=" * 50)
    
    try:
        from weather.models import WeatherLocation, CurrentWeather, WeatherAlert, WeatherForecast
        
        # Test model imports
        print("✅ Weather models imported successfully")
        
        # Test database queries
        location_count = WeatherLocation.objects.count()
        weather_count = CurrentWeather.objects.count()
        alert_count = WeatherAlert.objects.count()
        forecast_count = WeatherForecast.objects.count()
        
        print(f"📍 Weather Locations: {location_count}")
        print(f"🌡️  Current Weather Records: {weather_count}")
        print(f"🚨 Weather Alerts: {alert_count}")
        print(f"📅 Weather Forecasts: {forecast_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        return False

def test_weather_api_creation():
    """Test creating weather data through the API"""
    print("\n🏗️  TESTING WEATHER DATA CREATION")
    print("=" * 50)
    
    try:
        from weather.models import WeatherLocation, CurrentWeather
        from decimal import Decimal
        
        # Create test location
        location, created = WeatherLocation.objects.get_or_create(
            name="Test Location",
            region="Test Region",
            defaults={
                'latitude': Decimal('5.6037'),
                'longitude': Decimal('-0.1870')
            }
        )
        
        if created:
            print("✅ Test location created")
        else:
            print("ℹ️  Test location already exists")
        
        # Create test weather data
        weather, created = CurrentWeather.objects.get_or_create(
            location=location,
            defaults={
                'temperature': Decimal('28.5'),
                'humidity': Decimal('75.0'),
                'weather_condition': 'Test Condition',
                'rainfall_prediction': Decimal('15.0'),
                'wind_speed': Decimal('10.0'),
                'pressure': Decimal('1013.25'),
                'visibility': Decimal('10.0'),
                'uv_index': 5
            }
        )
        
        if created:
            print("✅ Test weather data created")
        else:
            print("ℹ️  Test weather data already exists")
            
        return True
        
    except Exception as e:
        print(f"❌ Creation Error: {str(e)}")
        return False

def main():
    """Main testing function"""
    print(f"🚀 Starting Weather App Tests - {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Database tables
    db_test = test_database_tables()
    
    # Test 2: Create sample data
    creation_test = test_weather_api_creation()
    
    # Test 3: API endpoints
    api_results = test_weather_endpoints()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 50)
    
    print(f"Database Tables: {'✅ PASS' if db_test else '❌ FAIL'}")
    print(f"Data Creation: {'✅ PASS' if creation_test else '❌ FAIL'}")
    
    success_count = 0
    total_count = len(api_results)
    
    for endpoint, result in api_results.items():
        status = "✅ PASS" if result["status"] == "SUCCESS" else "❌ FAIL"
        print(f"API {endpoint}: {status}")
        if result["status"] == "SUCCESS":
            success_count += 1
    
    print(f"\nAPI Success Rate: {success_count}/{total_count} ({(success_count/total_count*100):.1f}%)")
    
    # Check the critical endpoint
    critical_endpoint = "/api/v1/weather/current/"
    if critical_endpoint in api_results:
        if api_results[critical_endpoint]["status"] == "SUCCESS":
            print(f"\n🎯 CRITICAL ENDPOINT {critical_endpoint}: ✅ WORKING")
            print("The 404 error should be resolved!")
        else:
            print(f"\n🎯 CRITICAL ENDPOINT {critical_endpoint}: ❌ STILL FAILING")
    
    return api_results

if __name__ == "__main__":
    results = main()
