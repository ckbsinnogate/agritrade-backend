#!/usr/bin/env python3
"""
Detailed Phone Registration Debug Script
This script debugs the phone registration issue step by step
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.frontend_serializers import FrontendUserRegistrationSerializer
from authentication.models import User
from django.db import transaction
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_phone_registration():
    """Debug phone registration step by step"""
    
    print("🔍 Detailed Phone Registration Debug")
    print("=" * 60)
    
    # Test data
    test_data = {
        "phone_number": "+233273735997",
        "password": "TestPass123!",
        "first_name": "Debug",
        "last_name": "Phone"
    }
    
    print(f"📝 Test Data: {test_data}")
    
    try:
        # Step 1: Test serializer creation
        print("\n1️⃣ Creating serializer...")
        serializer = FrontendUserRegistrationSerializer(data=test_data)
        print("✅ Serializer created successfully")
        
        # Step 2: Test validation
        print("\n2️⃣ Validating data...")
        is_valid = serializer.is_valid()
        print(f"Validation result: {is_valid}")
        
        if not is_valid:
            print(f"❌ Validation errors: {serializer.errors}")
            return
        
        print("✅ Validation passed")
        print(f"📊 Validated data: {serializer.validated_data}")
        
        # Step 3: Test user creation in transaction
        print("\n3️⃣ Testing user creation within transaction...")
        
        with transaction.atomic():
            print("Starting atomic transaction...")
            user = serializer.save()
            print(f"✅ User created successfully!")
            print(f"👤 User ID: {user.id}")
            print(f"📱 Phone: {user.phone_number}")
            print(f"📧 Email: {user.email}")
            print(f"🏷️ Username: {user.username}")
            print(f"🎭 Roles: {user.roles}")
            
            # Step 4: Test contact method determination
            print("\n4️⃣ Testing contact method determination...")
            contact_method = 'email' if user.email else 'phone'
            print(f"📞 Contact method: {contact_method}")
            
            # Step 5: Test SMS OTP service import
            print("\n5️⃣ Testing SMS OTP service import...")
            try:
                from authentication.services_sms_otp import SMSOTPService
                print("✅ SMS OTP service imported successfully")
                
                sms_service = SMSOTPService()
                print("✅ SMS OTP service instantiated successfully")
                
                # Step 6: Test SMS OTP sending
                print("\n6️⃣ Testing SMS OTP sending...")
                success, message, otp_instance = sms_service.send_otp(
                    phone_number=user.phone_number,
                    purpose='registration',
                    ip_address='127.0.0.1',
                    user_agent='DebugScript'
                )
                
                print(f"SMS OTP Result: success={success}, message={message}")
                if success:
                    print(f"✅ SMS OTP sent successfully!")
                    print(f"📨 OTP Instance ID: {otp_instance.id if otp_instance else 'None'}")
                else:
                    print(f"⚠️ SMS OTP failed: {message}")
                    
            except Exception as sms_error:
                print(f"❌ SMS OTP service error: {str(sms_error)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
            
            # Clean up test user
            print("\n🗑️ Cleaning up test user...")
            user.delete()
            print("✅ Test user deleted")
            
    except Exception as e:
        print(f"❌ Error during debugging: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_phone_registration()
