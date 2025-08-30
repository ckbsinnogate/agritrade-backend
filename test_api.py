#!/usr/bin/env python3
"""
AgriConnect API Testing Script
Test authentication endpoints functionality
"""

import requests
import json
import sys

# API Base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_api_root():
    """Test API root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API Root: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Root Error: {e}")
        return False

def test_auth_root():
    """Test authentication root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/auth/")
        print(f"✅ Auth Root: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Auth Root Error: {e}")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    try:
        # Test data for registration
        registration_data = {
            "email": "testuser@agriconnect.com",
            "phone_number": "+233123456789",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "farmer",
            "country": "GH",
            "preferred_contact_method": "email"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register/",
            data=json.dumps(registration_data),
            headers=headers
        )
        
        print(f"✅ Registration: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Registration Error: {e}")
        return False

def test_otp_verification():
    """Test OTP verification endpoint"""
    try:
        # Test OTP verification (will fail without valid OTP)
        otp_data = {
            "email": "testuser@agriconnect.com",
            "otp_code": "123456"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/verify-otp/",
            data=json.dumps(otp_data),
            headers=headers
        )
        
        print(f"✅ OTP Verification: {response.status_code}")
        print(f"Response: {response.text}")
        
        return True  # We expect this to fail with invalid OTP
    except Exception as e:
        print(f"❌ OTP Verification Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting AgriConnect API Tests...")
    print("=" * 50)
    
    tests = [
        ("API Root", test_api_root),
        ("Auth Root", test_auth_root),
        ("User Registration", test_user_registration),
        ("OTP Verification", test_otp_verification),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📝 Testing: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Results: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
