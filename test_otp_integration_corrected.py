#!/usr/bin/env python
"""
AgriConnect OTP Integration Test - CORRECTED FORMAT
Tests the exact OTP verification format that the frontend should use

This script verifies:
1. Registration with frontend endpoint
2. OTP verification with CORRECT format (identifier + otp_code)
3. Token generation and user verification
4. Resend OTP functionality
"""

import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

from authentication.models import User, OTPCode

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_subsection(title):
    """Print subsection header"""
    print(f"\n🔸 {title}")
    print("-" * 40)

def test_corrected_otp_format():
    """Test OTP verification with the CORRECT format"""
    print_section("AgriConnect OTP Integration Test - CORRECTED FORMAT")
    
    # Test phone number
    test_phone = "+233548577000"
    
    print(f"📱 Testing with phone number: {test_phone}")
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Clean up any existing test data
    print_subsection("Cleanup Previous Test Data")
    try:
        # Delete existing test user if exists
        User.objects.filter(phone_number=test_phone).delete()
        print(f"✅ Cleaned up existing test user: {test_phone}")
    except Exception as e:
        print(f"⚠️ Cleanup note: {e}")
    
    # Step 2: Register user with frontend endpoint
    print_subsection("User Registration")
    registration_data = {
        "phone_number": test_phone,
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "FARMER",
        "country": "Ghana",
        "region": "Greater Accra",
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register-frontend/",
            headers=HEADERS,
            data=json.dumps(registration_data)
        )
        
        print(f"Registration Status: {response.status_code}")
        
        if response.status_code == 201:
            reg_data = response.json()
            print("✅ Registration successful!")
            print(f"Contact: {reg_data.get('contact_value')}")
            print(f"OTP Required: {reg_data.get('otp_required')}")
            contact_value = reg_data.get('contact_value')
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Step 3: Get OTP from database (simulating SMS reception)
    print_subsection("OTP Retrieval (Simulating SMS)")
    try:
        user = User.objects.get(phone_number=test_phone)
        otp_record = OTPCode.objects.filter(
            user=user,
            purpose='registration',
            is_used=False
        ).order_by('-created_at').first()
        
        if otp_record:
            otp_code = otp_record.code
            print(f"✅ OTP found: {otp_code}")
            print(f"Expires at: {otp_record.expires_at}")
            print(f"Purpose: {otp_record.purpose}")
        else:
            print("❌ No OTP found in database")
            return False
            
    except Exception as e:
        print(f"❌ OTP retrieval error: {e}")
        return False
    
    # Step 4: Test OTP verification with CORRECT format
    print_subsection("OTP Verification - CORRECT FORMAT")
    
    # CORRECT FORMAT - What frontend should send
    otp_verification_data = {
        "identifier": contact_value,      # ✅ CORRECT: Use "identifier"
        "otp_code": otp_code,            # ✅ CORRECT: Use "otp_code"
        "purpose": "registration"        # ✅ CORRECT: Optional purpose
    }
    
    print("📤 Sending OTP verification with CORRECT format:")
    print(json.dumps(otp_verification_data, indent=2))
    
    try:
        otp_response = requests.post(
            f"{API_BASE_URL}/auth/verify-otp/",
            headers=HEADERS,
            data=json.dumps(otp_verification_data)
        )
        
        print(f"\n📨 OTP Verification Status: {otp_response.status_code}")
        
        if otp_response.status_code == 200:
            otp_result = otp_response.json()
            print("✅ OTP verification successful!")
            print(f"Message: {otp_result.get('message')}")
            print(f"User verified: {otp_result.get('user', {}).get('is_verified')}")
            print(f"Access token received: {'access' in otp_result}")
            print(f"Refresh token received: {'refresh' in otp_result}")
            
            # Show user data
            user_data = otp_result.get('user', {})
            print(f"\n👤 User Profile:")
            print(f"   ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Phone: {user_data.get('phone_number')}")
            print(f"   Roles: {user_data.get('roles')}")
            print(f"   Phone Verified: {user_data.get('phone_verified')}")
            print(f"   Is Verified: {user_data.get('is_verified')}")
            
        else:
            print("❌ OTP verification failed")
            print(f"Error: {otp_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OTP verification error: {e}")
        return False
    
    # Step 5: Test wrong formats (should fail)
    print_subsection("Testing WRONG Formats (Should Fail)")
    
    # Wrong format 1: Using "phone_number" instead of "identifier"
    wrong_format_1 = {
        "phone_number": test_phone,  # ❌ WRONG: Should be "identifier"
        "otp_code": "123456"
    }
    
    print("🚫 Testing wrong format 1 (phone_number field):")
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/verify-otp/",
            headers=HEADERS,
            data=json.dumps(wrong_format_1)
        )
        print(f"Status: {response.status_code} (Expected: 400)")
        if response.status_code == 400:
            print("✅ Correctly rejected wrong format")
        else:
            print("❌ Wrong format was accepted (unexpected)")
    except Exception as e:
        print(f"Error testing wrong format: {e}")
    
    # Wrong format 2: Using "code" instead of "otp_code"
    wrong_format_2 = {
        "identifier": test_phone,
        "code": "123456"  # ❌ WRONG: Should be "otp_code"
    }
    
    print("\n🚫 Testing wrong format 2 (code field):")
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/verify-otp/",
            headers=HEADERS,
            data=json.dumps(wrong_format_2)
        )
        print(f"Status: {response.status_code} (Expected: 400)")
        if response.status_code == 400:
            print("✅ Correctly rejected wrong format")
        else:
            print("❌ Wrong format was accepted (unexpected)")
    except Exception as e:
        print(f"Error testing wrong format: {e}")
    
    # Step 6: Test resend OTP
    print_subsection("Testing Resend OTP")
    resend_data = {
        "identifier": contact_value,
        "purpose": "registration"
    }
    
    try:
        resend_response = requests.post(
            f"{API_BASE_URL}/auth/resend-otp/",
            headers=HEADERS,
            data=json.dumps(resend_data)
        )
        
        print(f"Resend OTP Status: {resend_response.status_code}")
        if resend_response.status_code == 200:
            print("✅ Resend OTP successful!")
            resend_result = resend_response.json()
            print(f"Message: {resend_result.get('message')}")
        elif resend_response.status_code == 429:
            print("⚠️ Rate limited (expected behavior)")
        else:
            print(f"❌ Resend OTP failed: {resend_response.text}")
            
    except Exception as e:
        print(f"❌ Resend OTP error: {e}")
    
    # Step 7: Verify database state
    print_subsection("Database Verification")
    try:
        user = User.objects.get(phone_number=test_phone)
        print(f"✅ User found in database:")
        print(f"   Username: {user.username}")
        print(f"   Phone Verified: {user.phone_verified}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Roles: {[role.name for role in user.roles.all()]}")
        
        # Check OTP records
        otp_records = OTPCode.objects.filter(user=user).order_by('-created_at')
        print(f"\n📋 OTP Records: {otp_records.count()}")
        for i, otp in enumerate(otp_records[:3], 1):
            print(f"   {i}. Code: {otp.code}, Used: {otp.is_used}, Purpose: {otp.purpose}")
            
    except Exception as e:
        print(f"❌ Database verification error: {e}")
    
    # Step 8: Generate summary
    print_section("TEST SUMMARY")
    print("✅ CORRECT OTP Format:")
    print(json.dumps({
        "identifier": "+233548577000",
        "otp_code": "123456",
        "purpose": "registration"
    }, indent=2))
    
    print("\n❌ WRONG Formats (Don't use):")
    print("• phone_number field instead of identifier")
    print("• code field instead of otp_code")
    print("• email field instead of identifier")
    print("• verification_code field instead of otp_code")
    
    print("\n🎯 Frontend Implementation Notes:")
    print("1. Always use 'identifier' field for phone/email")
    print("2. Always use 'otp_code' field for the 6-digit code")
    print("3. Purpose field is optional but recommended")
    print("4. Store JWT tokens from successful verification")
    print("5. Handle 400 errors gracefully for invalid OTP")
    
    return True

def test_complete_registration_flow():
    """Test the complete registration flow with corrected OTP"""
    print_section("Complete Registration Flow Test")
    
    test_phone = "+233558667788"
    
    # Clean up
    User.objects.filter(phone_number=test_phone).delete()
    
    # 1. Registration
    registration_data = {
        "phone_number": test_phone,
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Complete",
        "last_name": "Flow",
        "user_type": "CONSUMER",
        "country": "Ghana"
    }
    
    reg_response = requests.post(
        f"{API_BASE_URL}/auth/register-frontend/",
        headers=HEADERS,
        data=json.dumps(registration_data)
    )
    
    if reg_response.status_code != 201:
        print(f"❌ Registration failed: {reg_response.text}")
        return False
    
    reg_data = reg_response.json()
    contact_value = reg_data.get('contact_value')
    print(f"✅ Registration successful for: {contact_value}")
    
    # 2. Get OTP
    user = User.objects.get(phone_number=test_phone)
    otp_record = OTPCode.objects.filter(user=user, is_used=False).first()
    
    if not otp_record:
        print("❌ No OTP generated")
        return False
    
    print(f"✅ OTP generated: {otp_record.code}")
    
    # 3. Verify OTP with CORRECT format
    verification_data = {
        "identifier": contact_value,
        "otp_code": otp_record.code,
        "purpose": "registration"
    }
    
    verify_response = requests.post(
        f"{API_BASE_URL}/auth/verify-otp/",
        headers=HEADERS,
        data=json.dumps(verification_data)
    )
    
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        print("✅ OTP verification successful!")
        print(f"Access token: {verify_data.get('access')[:20]}...")
        print(f"User verified: {verify_data.get('user', {}).get('is_verified')}")
        return True
    else:
        print(f"❌ OTP verification failed: {verify_response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AgriConnect OTP Integration Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Corrected OTP format
        success1 = test_corrected_otp_format()
        
        # Test 2: Complete flow
        success2 = test_complete_registration_flow()
        
        print_section("FINAL RESULTS")
        if success1 and success2:
            print("🎉 ALL TESTS PASSED!")
            print("✅ OTP integration is working correctly")
            print("✅ Frontend can use the corrected format")
        else:
            print("❌ Some tests failed")
            print("Please check the error messages above")
            
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
