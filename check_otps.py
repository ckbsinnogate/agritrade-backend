#!/usr/bin/env python
"""
Quick SMS OTP Admin Test
Check what OTPs are generated and test verification
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

from authentication.services_sms_otp import SMSOTPService
from authentication.models import OTPCode
from django.utils import timezone

def check_recent_otps():
    """Check recent OTPs for the test phone number"""
    phone_number = "+233273735500"
    
    print("🔍 Checking Recent OTPs")
    print("=" * 50)
    
    # Get recent OTPs for this phone number
    recent_otps = OTPCode.objects.filter(
        phone_number=phone_number
    ).order_by('-created_at')[:5]
    
    if recent_otps:
        print(f"📱 Recent OTPs for {phone_number}:")
        for i, otp in enumerate(recent_otps, 1):
            status = "✅ Valid" if not otp.is_used and otp.expires_at > timezone.now() else "❌ Expired/Used"
            print(f"{i}. Code: {otp.code} | Purpose: {otp.purpose} | Status: {status}")
            print(f"   Created: {otp.created_at} | Expires: {otp.expires_at}")
            
        # Test verification with the most recent valid OTP
        latest_otp = recent_otps[0]
        if not latest_otp.is_used and latest_otp.expires_at > timezone.now():
            print(f"\n🧪 Testing verification with latest OTP: {latest_otp.code}")
            
            sms_service = SMSOTPService()
            success, message, otp_instance = sms_service.verify_otp(
                phone_number=phone_number,
                otp_code=latest_otp.code,
                purpose=latest_otp.purpose
            )
            
            print(f"Verification Result: {success}")
            print(f"Message: {message}")
            
    else:
        print(f"❌ No OTPs found for {phone_number}")

if __name__ == "__main__":
    check_recent_otps()
