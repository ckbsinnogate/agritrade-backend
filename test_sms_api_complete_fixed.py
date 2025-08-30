#!/usr/bin/env python
"""
Complete SMS OTP API Test
Test all the API endpoints with real SMS delivery
"""
import os
import sys
import django
import requests
import json
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.services_sms_otp import SMSOTPService

def test_sms_otp_api_endpoints():
    """Test SMS OTP API endpoints"""
    base_url = "http://localhost:8000"
    phone_number = "+233273735500"
    
    print("🚀 Testing SMS OTP API Endpoints")
    print("=" * 50)
    
    # Test 1: Request SMS OTP
    print("\n1️⃣ Testing SMS OTP Request")
    request_url = f"{base_url}/api/auth/sms-otp/request/"
    request_data = {
        "phone_number": phone_number,
        "purpose": "login"
    }
    
    try:
        response = requests.post(request_url, json=request_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ SMS OTP request successful!")
        else:
            print("❌ SMS OTP request failed!")
            return
            
    except Exception as e:
        print(f"❌ Error testing SMS OTP request: {str(e)}")
        return
    
    # Wait a moment for SMS to be sent
    print("\n⏳ Waiting 5 seconds for SMS delivery...")
    time.sleep(5)
    
    # Test 2: Get the OTP from database (since we can't read SMS)
    print("\n2️⃣ Getting OTP from database for testing")
    from authentication.models import OTPCode
    from django.utils import timezone
    
    latest_otp = OTPCode.objects.filter(
        phone_number=phone_number,
        purpose="login",
        is_used=False,
        expires_at__gt=timezone.now()
    ).order_by('-created_at').first()
    
    if not latest_otp:
        print("❌ No valid OTP found in database")
        return
        
    otp_code = latest_otp.code
    print(f"📱 Found OTP: {otp_code}")
    
    # Test 3: Verify SMS OTP
    print("\n3️⃣ Testing SMS OTP Verification")
    verify_url = f"{base_url}/api/auth/sms-otp/verify/"
    verify_data = {
        "phone_number": phone_number,
        "otp_code": otp_code,
        "purpose": "login"
    }
    
    try:
        response = requests.post(verify_url, json=verify_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ SMS OTP verification successful!")
        else:
            print("❌ SMS OTP verification failed!")
            
    except Exception as e:
        print(f"❌ Error testing SMS OTP verification: {str(e)}")
    
    # Test 4: Status Check
    print("\n4️⃣ Testing SMS OTP Status")
    status_url = f"{base_url}/api/auth/sms-otp/status/"
    status_data = {
        "phone_number": phone_number,
        "purpose": "login"
    }
    
    try:
        response = requests.post(status_url, json=status_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ SMS OTP status check successful!")
        else:
            print("❌ SMS OTP status check failed!")
            
    except Exception as e:
        print(f"❌ Error testing SMS OTP status: {str(e)}")

if __name__ == "__main__":
    test_sms_otp_api_endpoints()
