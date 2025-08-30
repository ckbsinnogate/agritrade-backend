#!/usr/bin/env python3
"""
Test Real SMS OTP Delivery
Replace YOUR_PHONE_NUMBER with your actual phone number
"""

import requests
import json

# Configuration
API_BASE = "http://localhost:8000/api/v1/auth/sms-otp"
YOUR_PHONE_NUMBER = "+233273735500"  # Your real Ghana number

def test_real_sms():
    """Test SMS OTP with real phone number"""
    
    print("🔐 Testing Real SMS OTP Delivery")
    print("=" * 50)
    
    # Step 1: Request SMS OTP
    print(f"📱 Requesting SMS OTP for {YOUR_PHONE_NUMBER}...")
    
    request_data = {
        "phone_number": YOUR_PHONE_NUMBER,
        "purpose": "registration"
    }
    
    try:
        response = requests.post(f"{API_BASE}/request/", json=request_data)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ SMS OTP sent successfully!")
            print(f"📨 Message: {result.get('message', 'SMS sent')}")
            print(f"📞 Phone: {result.get('phone_number', YOUR_PHONE_NUMBER)}")
            
            # Wait for user to enter OTP
            print("\n🔢 Check your phone for the SMS and enter the 6-digit code:")
            otp_code = input("Enter OTP code: ").strip()
            
            if len(otp_code) == 6 and otp_code.isdigit():
                # Step 2: Verify SMS OTP
                verify_data = {
                    "phone_number": YOUR_PHONE_NUMBER,
                    "otp_code": otp_code,
                    "purpose": "registration"
                }
                
                verify_response = requests.post(f"{API_BASE}/verify/", json=verify_data)
                verify_result = verify_response.json()
                
                if verify_response.status_code == 200:
                    print("🎉 SMS OTP verified successfully!")
                    print(f"✅ Status: {verify_result.get('message', 'Verified')}")
                else:
                    print("❌ SMS OTP verification failed!")
                    print(f"Error: {verify_result}")
            else:
                print("❌ Invalid OTP format. Should be 6 digits.")
                
        else:
            print("❌ Failed to send SMS OTP!")
            print(f"Error: {result}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        print("Make sure Django server is running on localhost:8000")
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    if "YOUR_PHONE_NUMBER" in YOUR_PHONE_NUMBER:
        print("⚠️  Please replace YOUR_PHONE_NUMBER with your actual phone number!")
        print("Example: +233244123456 (for Ghana)")
        print("Edit this file and replace the phone number, then run again.")
    else:
        test_real_sms()
