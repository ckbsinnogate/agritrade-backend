#!/usr/bin/env python
"""
Debug AVRSMS SMS Sending
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from communications.services import AVRSMSService

def test_avrsms_direct():
    """Test AVRSMS service directly"""
    print("🔍 Testing AVRSMS Service Directly")
    print("=" * 50)
    
    try:
        # Initialize service
        sms_service = AVRSMSService()
        print(f"📋 API ID: {sms_service.api_id}")
        print(f"📋 Sender ID: {sms_service.sender_id}")
        print(f"📋 Base URL: {sms_service.base_url}")
        
        # Test SMS
        phone_number = "+233273735500"
        message = "Test SMS from AgriConnect. Your OTP is: 123456. Valid for 10 minutes."
        
        print(f"\n📱 Sending test SMS to {phone_number}")
        print(f"💬 Message: {message}")
        
        result = sms_service.send_sms(phone_number, message)
        
        print(f"\n📊 Result:")
        print(f"Success: {result.get('success', False)}")
        print(f"Message ID: {result.get('message_id', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Remarks: {result.get('remarks', 'N/A')}")
        print(f"Error: {result.get('error', 'N/A')}")
        print(f"Full Response: {result.get('response', {})}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_avrsms_direct()
    if success:
        print("\n✅ AVRSMS test successful!")
    else:
        print("\n❌ AVRSMS test failed!")
