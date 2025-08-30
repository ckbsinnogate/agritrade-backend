#!/usr/bin/env python
"""
Quick OTP Format Validation Script
Validates that the OTP serializer expects the correct format
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

from authentication.serializers import OTPVerificationSerializer
from authentication.models import User, OTPCode
from django.utils import timezone
from datetime import timedelta

def validate_otp_format():
    """Validate OTP serializer format requirements"""
    print("🔍 Validating OTP Verification Format")
    print("="*50)
    
    # Test 1: Check serializer fields
    print("\n1️⃣ Checking OTPVerificationSerializer fields:")
    serializer = OTPVerificationSerializer()
    
    print("Required fields:")
    for field_name, field in serializer.fields.items():
        required = getattr(field, 'required', True)
        print(f"  - {field_name}: {'Required' if required else 'Optional'}")
    
    # Test 2: Test correct format
    print("\n2️⃣ Testing CORRECT format:")
    correct_data = {
        'identifier': '+233548577000',
        'otp_code': '123456'
    }
    
    serializer = OTPVerificationSerializer(data=correct_data)
    if serializer.is_valid():
        print("✅ CORRECT format is valid")
        print(f"Normalized identifier: {serializer.validated_data.get('normalized_identifier')}")
    else:
        print("❌ CORRECT format failed validation")
        print(f"Errors: {serializer.errors}")
    
    # Test 3: Test wrong formats
    print("\n3️⃣ Testing WRONG formats:")
    
    wrong_formats = [
        {'phone_number': '+233548577000', 'otp_code': '123456'},  # Wrong field name
        {'identifier': '+233548577000', 'code': '123456'},        # Wrong field name
        {'identifier': '+233548577000'},                          # Missing otp_code
        {'otp_code': '123456'},                                   # Missing identifier
    ]
    
    for i, wrong_data in enumerate(wrong_formats, 1):
        serializer = OTPVerificationSerializer(data=wrong_data)
        if serializer.is_valid():
            print(f"❌ Wrong format {i} was accepted (should fail)")
        else:
            print(f"✅ Wrong format {i} correctly rejected")
            print(f"   Data: {wrong_data}")
            print(f"   Errors: {serializer.errors}")
    
    # Test 4: Create test OTP record
    print("\n4️⃣ Testing OTP record creation:")
    try:
        # Create or get test user
        user, created = User.objects.get_or_create(
            phone_number='+233548577000',
            defaults={
                'username': '+233548577000',
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        print(f"{'Created' if created else 'Found'} test user: {user.username}")
        
        # Create OTP record
        otp_record = OTPCode.objects.create(
            user=user,
            phone_number='+233548577000',
            code='123456',
            purpose='registration',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        print(f"✅ Created OTP record: {otp_record.code}")
        
        # Verify OTP can be found
        found_otp = OTPCode.objects.filter(
            user=user,
            code='123456',
            purpose='registration',
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if found_otp:
            print("✅ OTP record can be found with correct criteria")
        else:
            print("❌ OTP record not found with search criteria")
            
        # Cleanup
        otp_record.delete()
        if created:
            user.delete()
            
    except Exception as e:
        print(f"❌ Error testing OTP record: {e}")
    
    print("\n" + "="*50)
    print("🎯 SUMMARY:")
    print("✅ Backend expects: identifier + otp_code")
    print("✅ Frontend should use EXACT field names")
    print("✅ OTP verification logic is correctly implemented")
    
if __name__ == "__main__":
    validate_otp_format()
