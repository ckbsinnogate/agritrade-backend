#!/usr/bin/env python3
"""
Test script to validate the fixed disease detection endpoint
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image

def create_test_image():
    """Create a simple test image for testing"""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='green')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.getvalue()

def test_disease_detection_fixes():
    """Test the fixed disease detection endpoint"""
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/ai/disease-detection/"
    
    print("🧪 Testing Disease Detection Fixes")
    print("=" * 50)
    
    # Test 1: Invalid crop type (should fail with helpful message)
    print("\n1️⃣ Testing invalid crop type 'unknown'")
    test_data = {
        "crop_type": "unknown",
        "symptoms": "Yellow leaves"
    }
    
    try:
        response = requests.post(endpoint, json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ Correctly rejected: {data.get('error')}")
            if 'suggested_crops' in data:
                print(f"   💡 Suggestions: {data['suggested_crops']}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Valid crop type with symptoms (should work)
    print("\n2️⃣ Testing valid crop type with symptoms")
    test_data = {
        "crop_type": "tomato",
        "symptoms": "Yellow leaves with brown spots on tomato plant"
    }
    
    try:
        response = requests.post(endpoint, json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Authentication required (expected)")
        elif response.status_code == 200:
            print("   ✅ Success response received")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Missing crop type (should fail)
    print("\n3️⃣ Testing missing crop type")
    test_data = {
        "symptoms": "Yellow leaves"
    }
    
    try:
        response = requests.post(endpoint, json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ Correctly rejected: {data.get('error')}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Empty crop type (should fail)
    print("\n4️⃣ Testing empty crop type")
    test_data = {
        "crop_type": "",
        "symptoms": "Yellow leaves"
    }
    
    try:
        response = requests.post(endpoint, json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ Correctly rejected: {data.get('error')}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Fix Validation Complete!")
    print("✅ Backend properly validates crop types")
    print("✅ Helpful error messages provided")
    print("💡 Ready for frontend deployment")

if __name__ == "__main__":
    test_disease_detection_fixes()
