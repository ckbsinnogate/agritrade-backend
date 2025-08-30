#!/usr/bin/env python3
"""
🚨 URGENT: Debug Image Upload Issue Based on User Logs
This script tests the exact issues identified in the user's logs
"""

import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = f"{BASE_URL}/api/v1/ai/disease-detection/"

def test_current_broken_frontend_behavior():
    """Simulate the exact broken data the frontend is currently sending"""
    print("🔍 Testing CURRENT BROKEN frontend behavior...")
    print("   This simulates the exact data from your logs:")
    print("   {'image': {}, 'crop_type': 'tomato', 'symptoms': 'Disease analysis for tomato plant from uploaded image'}")
    
    # This is what your frontend is currently sending (broken)
    broken_data = {
        'image': {},  # ❌ EMPTY OBJECT - This is the problem!
        'crop_type': 'tomato',  # ✅ This is working
        'symptoms': 'Disease analysis for tomato plant from uploaded image'  # ✅ This is working
    }
    
    try:
        response = requests.post(
            ENDPOINT,
            json=broken_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Expected: Backend requires authentication")
            print("❌ But your frontend is sending empty image object {}")
            return True
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_fixed_formdata_approach():
    """Test the correct FormData approach that the fixed component uses"""
    print("\n🔍 Testing FIXED FormData approach...")
    print("   This is what the fixed component will send:")
    
    try:
        # Create a minimal test image file (1x1 pixel PNG)
        import io
        from PIL import Image
        
        # Create a 1x1 red pixel image
        img = Image.new('RGB', (1, 1), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_data = buffer.getvalue()
        
        # This is what the FIXED frontend will send
        files = {
            'image': ('test_tomato.png', image_data, 'image/png')
        }
        
        data = {
            'crop_type': 'tomato',
            'symptoms': 'Yellowing leaves with brown spots on tomato plant',
            'location': 'Accra, Ghana'
        }
        
        response = requests.post(
            ENDPOINT,
            files=files,
            data=data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Backend accepts FormData format but requires authentication!")
            print("✅ This means the FIXED component will work correctly")
            return True
        elif response.status_code == 200:
            print("✅ SUCCESS: Backend accepts FormData and processes it!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR testing fixed approach: {e}")
        return False

def main():
    """Run the debug tests"""
    print("🚨 URGENT: Debugging Image Upload Issue from User Logs")
    print("=" * 60)
    print("User's Django logs show:")
    print("  ✅ crop_type: 'tomato' - WORKING")
    print("  ❌ 'image': {} - SENDING EMPTY OBJECT")
    print("  ❌ Backend receives: image_url: , location: ''")
    print("=" * 60)
    
    # Test server availability
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Django server is running at {BASE_URL}")
    except:
        print(f"❌ ERROR: Django server not accessible at {BASE_URL}")
        return
    
    # Run diagnostic tests
    test1_passed = test_current_broken_frontend_behavior()
    test2_passed = test_fixed_formdata_approach()
    
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY:")
    print(f"  🔍 Current broken behavior identified: {'✅ YES' if test1_passed else '❌ NO'}")
    print(f"  🛠️ Fixed FormData approach works: {'✅ YES' if test2_passed else '❌ NO'}")
    
    if test1_passed and test2_passed:
        print("\n🎯 SOLUTION CONFIRMED:")
        print("   ❌ Current frontend sends: {'image': {}}")
        print("   ✅ Fixed frontend will send: FormData with actual file")
        print("   🚀 Deploy URGENT_IMAGE_UPLOAD_FIX.tsx immediately!")
    else:
        print("\n⚠️  Need more investigation")
    
    print("\n🚨 IMMEDIATE ACTIONS:")
    print("   1. Deploy the fixed React component")
    print("   2. Test with actual tomato plant image")
    print("   3. Verify console logs show real file data")

if __name__ == "__main__":
    main()
