#!/usr/bin/env python3
"""
Test Disease Detection Endpoint
Quick test to identify the 400 Bad Request issue
"""

import requests
import json

# Test data
test_data = {
    "crop_type": "tomatoes",
    "symptoms": "yellow leaves with brown spots"
}

# First test without auth to see the auth error
print("Testing disease detection endpoint...")
print("=" * 50)

# Test 1: Without authentication
print("1. Testing without authentication:")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/ai/disease-detection/",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)

# Test 2: With invalid auth token
print("2. Testing with invalid auth token:")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/ai/disease-detection/",
        json=test_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid_token"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)

# Test 3: Test other AI endpoints for comparison
print("3. Testing AI chat endpoint (for comparison):")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/ai/chat/",
        json={"message": "test"},
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid_token"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)

# Test 4: Test with missing required fields
print("4. Testing with missing crop_type:")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/ai/disease-detection/",
        json={"symptoms": "yellow leaves"},
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid_token"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)

# Test 5: Test with missing symptoms and image_url
print("5. Testing with missing symptoms and image_url:")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/ai/disease-detection/",
        json={"crop_type": "tomatoes"},
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid_token"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Test complete!")
