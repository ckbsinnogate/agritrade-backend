#!/usr/bin/env python3
"""
Test Mobile App API Integration
Tests all API endpoints that the mobile app will use
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_api_endpoint(endpoint, method='GET', data=None, files=None):
    """Test a single API endpoint"""
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        print()
        
        return response.status_code, response.json() if response.text else None
        
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {str(e)}")
        print()
        return None, None

def main():
    """Test all mobile app API endpoints"""
    print("🧪 MOBILE APP API INTEGRATION TEST")
    print("=" * 50)
    print(f"Testing Django Backend: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test AI endpoints
    print("🤖 AI SERVICE ENDPOINTS")
    print("-" * 30)
    
    # 1. Health Check
    test_api_endpoint("ai/health/")
    
    # 2. Chat/AgriBot
    test_api_endpoint("ai/chat/", method='POST', data={
        "message": "Hello AgriBot, can you help me with crop recommendations?",
        "context": {"crop_type": "maize", "location": "Ghana"}
    })
    
    # 3. Crop Advisory
    test_api_endpoint("ai/crop-advisory/", method='POST', data={
        "crop_type": "maize",
        "location": "Ghana",
        "soil_type": "clay",
        "weather": {"temperature": 28, "humidity": 75}
    })
    
    # 4. Disease Detection (without image for now)
    test_api_endpoint("ai/disease-detection/", method='POST', data={
        "crop_type": "maize",
        "symptoms": ["yellowing leaves", "brown spots"]
    })
    
    # 5. Market Intelligence
    test_api_endpoint("ai/market-intelligence/", method='POST', data={
        "crop_type": "maize",
        "location": "Ghana",
        "quantity": 100
    })
    
    # Test Authentication endpoints
    print("🔐 AUTHENTICATION ENDPOINTS")
    print("-" * 30)
    
    # 6. Register endpoint
    test_api_endpoint("auth/register/", method='POST', data={
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    })
    
    # 7. Login endpoint
    test_api_endpoint("auth/login/", method='POST', data={
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Test Product endpoints
    print("🛒 PRODUCT ENDPOINTS")
    print("-" * 30)
    
    # 8. Products list
    test_api_endpoint("products/")
    
    # 9. Product categories
    test_api_endpoint("products/categories/")
    
    print("🎯 INTEGRATION TEST COMPLETED")
    print("Now test from mobile app using Expo dev tools!")

if __name__ == "__main__":
    main()
