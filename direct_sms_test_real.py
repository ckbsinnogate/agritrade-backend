#!/usr/bin/env python3
"""
Direct SMS Test to +233273735500
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

def test_direct_sms():
    """Test SMS directly using AVRSMS API"""
    
    print("🔐 Direct SMS Test to +233273735500")
    print("=" * 50)
    
    # AVRSMS Configuration from smsapi.yaml
    api_id = "API113898428691"
    api_password = "Kingsco45@1"
    base_url = "https://api.avrsms.com/api"
    sender_id = "AgriConnect"
    
    # Your phone number (remove + as per API requirements)
    phone_number = "233273735500"  # Ghana number without +
    
    # Test message
    message = "AgriConnect Test: Your verification code is 123456. Valid for 10 minutes."
    
    print(f"📱 Sending to: +{phone_number}")
    print(f"📡 API ID: {api_id}")
    print(f"🏢 Sender: {sender_id}")
    print(f"💬 Message: {message}")
    print()
    
    # Prepare payload according to AVRSMS API documentation
    payload = {
        "api_id": api_id,
        "api_password": api_password,
        "sms_type": "T",  # Transactional
        "encoding": "T",   # Text
        "sender_id": sender_id,
        "phonenumber": phone_number,
        "textmessage": message,
        "uid": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }
    
    try:
        print("📤 Sending request to AVRSMS API...")
        response = requests.post(f"{base_url}/SendSMS", json=payload, timeout=30)
        
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("📋 Response JSON:")
                print(json.dumps(result, indent=2))
                
                if result.get('status') == 'S':
                    print("✅ SMS sent successfully!")
                    print(f"📨 Message ID: {result.get('message_id')}")
                    print("📱 Check your phone for the SMS!")
                    return True
                else:
                    print("❌ SMS sending failed!")
                    print(f"Status: {result.get('status')}")
                    print(f"Remarks: {result.get('remarks')}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_direct_sms()
    print("\n" + "=" * 50)
    if success:
        print("🎉 SMS test completed successfully!")
        print("📱 You should receive the SMS shortly.")
    else:
        print("❌ SMS test failed. Check the error details above.")
    print("=" * 50)
