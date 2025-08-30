#!/usr/bin/env python3
"""
OTP Authentication Frontend-Backend Integration Test
Tests the correct API format for OTP verification
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_registration_and_otp():
    """Test the complete registration and OTP verification flow"""
    
    print("🧪 TESTING OTP AUTHENTICATION INTEGRATION")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("\n1️⃣ Testing User Registration...")
    
    test_phone = f"+233548570{datetime.now().strftime('%H%M%S')}"
    
    registration_data = {
        "user_type": "farmer",
        "phone_number": test_phone,
        "password": "testpass123",
        "password_confirm": "testpass123", 
        "first_name": "Test",
        "last_name": "User",
        "country": "Ghana",
        "region": "Greater Accra",
        "preferred_language": "en"
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
            
            # Step 2: Test OTP verification with CORRECT format
            print("\n2️⃣ Testing OTP Verification (CORRECT FORMAT)...")
            
            # Get OTP from logs/database (in real scenario, user gets this via SMS)
            otp_code = input(f"Enter OTP received for {test_phone}: ").strip()
            
            if otp_code:
                # CORRECT FORMAT - What backend expects
                otp_data = {
                    "identifier": test_phone,      # Phone number or email
                    "otp_code": otp_code,         # 6-digit code
                    "purpose": "registration"      # Optional purpose
                }
                
                otp_response = requests.post(
                    f"{API_BASE_URL}/auth/verify-otp/",
                    headers=HEADERS,
                    data=json.dumps(otp_data)
                )
                
                print(f"OTP Verification Status: {otp_response.status_code}")
                
                if otp_response.status_code == 200:
                    otp_result = otp_response.json()
                    print("✅ OTP verification successful!")
                    print(f"User verified: {otp_result.get('user', {}).get('is_verified')}")
                    print(f"Access token received: {'access' in otp_result}")
                else:
                    print("❌ OTP verification failed")
                    print(f"Error: {otp_response.text}")
            
            # Step 3: Test resend OTP
            print("\n3️⃣ Testing Resend OTP...")
            
            resend_data = {
                "identifier": test_phone,
                "purpose": "registration"
            }
            
            resend_response = requests.post(
                f"{API_BASE_URL}/auth/resend-otp/",
                headers=HEADERS,
                data=json.dumps(resend_data)
            )
            
            print(f"Resend OTP Status: {resend_response.status_code}")
            
            if resend_response.status_code == 200:
                print("✅ Resend OTP successful!")
                print(resend_response.json())
            elif resend_response.status_code == 429:
                print("⚠️ Rate limited - too many requests")
            else:
                print("❌ Resend OTP failed")
                print(f"Error: {resend_response.text}")
                
        else:
            print("❌ Registration failed")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

def test_wrong_formats():
    """Test common wrong formats that cause errors"""
    
    print("\n\n🚫 TESTING WRONG FORMATS (Should Fail)")
    print("=" * 50)
    
    test_phone = "+233548577000"  # Use existing number
    
    wrong_formats = [
        {
            "name": "Wrong field names (phone_number + code)",
            "data": {
                "phone_number": test_phone,
                "code": "123456"
            }
        },
        {
            "name": "Wrong field names (contact + otp)",
            "data": {
                "contact": test_phone,
                "otp": "123456"
            }
        },
        {
            "name": "Missing identifier",
            "data": {
                "otp_code": "123456"
            }
        },
        {
            "name": "Wrong OTP length (4 digits)",
            "data": {
                "identifier": test_phone,
                "otp_code": "1234"
            }
        }
    ]
    
    for test_case in wrong_formats:
        print(f"\n⚠️ Testing: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/verify-otp/",
                headers=HEADERS,
                data=json.dumps(test_case['data'])
            )
            
            print(f"Status: {response.status_code} (Expected 400)")
            
            if response.status_code != 200:
                print(f"✅ Failed as expected: {response.text}")
            else:
                print("❌ Unexpectedly succeeded!")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

def print_correct_format():
    """Print the correct format for frontend developers"""
    
    print("\n\n📋 CORRECT FRONTEND FORMAT")
    print("=" * 50)
    
    print("""
✅ CORRECT OTP VERIFICATION REQUEST:

```typescript
const otpVerificationData = {
  identifier: "+233548577037",  // Phone number OR email address
  otp_code: "123456",          // Exactly 6 digits as string
  purpose: "registration"       // Optional: registration, login, password_reset
}

fetch('/api/v1/auth/verify-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(otpVerificationData)
})
```

✅ CORRECT RESEND OTP REQUEST:

```typescript
const resendOTPData = {
  identifier: "+233548577037",  // Phone number OR email address  
  purpose: "registration"       // registration, login, password_reset
}

fetch('/api/v1/auth/resend-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(resendOTPData)
})
```

🔥 KEY POINTS:
1. Field name MUST be "identifier" (not phone_number, email, contact)
2. OTP field MUST be "otp_code" (not code, otp, verification_code)
3. Phone numbers are auto-normalized by backend
4. Purpose is optional but recommended
""")

if __name__ == "__main__":
    print_correct_format()
    
    choice = input("\nDo you want to run the live API test? (y/n): ").lower().strip()
    
    if choice == 'y':
        test_registration_and_otp()
        test_wrong_formats()
    else:
        print("\n✅ Format documentation complete!")
        print("Use the correct format shown above in your frontend code.")
