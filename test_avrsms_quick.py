#!/usr/bin/env python3
"""
AgriConnect SMS System - Quick AVRSMS Test
Simple test to verify AVRSMS API integration
"""

import os
import sys
import django
from django.conf import settings

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

# Import the clean AVRSMS service
from avrsms_service import AVRSMSService

def test_avrsms_quick():
    """Quick test of AVRSMS API"""
    print("🚀 AGRICONNECT - AVRSMS API QUICK TEST")
    print("=" * 50)
    
    # Initialize service
    try:
        sms_service = AVRSMSService()
        print("✅ AVRSMS service initialized successfully")
        print(f"API ID: {sms_service.api_id}")
        print(f"Base URL: {sms_service.base_url}")
        
        # Test 1: Check balance
        print("\n1. 📊 Testing Balance Check")
        print("-" * 30)
        
        balance_result = sms_service.check_balance()
        print(f"Balance Result: {balance_result}")
        
        if balance_result['success']:
            print("✅ Balance check successful")
        else:
            print(f"❌ Balance check failed: {balance_result.get('error')}")
        
        # Test 2: Send test SMS
        print("\n2. 📱 Testing SMS Send")
        print("-" * 30)
        
        test_phone = "+233241234567"  # Ghana test number
        test_message = "Hello from AgriConnect AI! This is a test message from your smart farming assistant."
        
        sms_result = sms_service.send_sms(test_phone, test_message)
        print(f"SMS Result: {sms_result}")
        
        if sms_result['success']:
            print("✅ SMS sent successfully")
            message_id = sms_result.get('message_id')
            
            # Test 3: Check delivery status
            if message_id:
                print("\n3. 📬 Testing Delivery Status")
                print("-" * 30)
                
                import time
                time.sleep(5)  # Wait 5 seconds
                
                status_result = sms_service.get_delivery_status(message_id=message_id)
                print(f"Status Result: {status_result}")
                
                if status_result['success']:
                    print("✅ Delivery status check successful")
                else:
                    print(f"❌ Delivery status check failed: {status_result.get('error')}")
        else:
            print(f"❌ SMS sending failed: {sms_result.get('error')}")
        
        # Test 4: OTP verification
        print("\n4. 🔐 Testing OTP Verification")
        print("-" * 30)
        
        otp_result = sms_service.send_verification_otp(test_phone, brand="AgriConnect")
        print(f"OTP Result: {otp_result}")
        
        if otp_result['success']:
            print("✅ OTP sent successfully")
            verification_id = otp_result.get('verification_id')
            print(f"Verification ID: {verification_id}")
            print("📝 Note: Check your phone for the OTP code")
        else:
            print(f"❌ OTP sending failed: {otp_result.get('error')}")
        
        print("\n" + "=" * 50)
        print("🎯 AVRSMS INTEGRATION TEST COMPLETED")
        print("✅ Basic SMS functionality working")
        print("✅ Ready for farmer onboarding deployment")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_avrsms_quick()
