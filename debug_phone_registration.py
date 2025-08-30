#!/usr/bin/env python
"""
Debug Phone Registration Issue
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
sys.path.insert(0, os.path.abspath('.'))
django.setup()

from authentication.frontend_serializers import FrontendUserRegistrationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def debug_phone_registration():
    """Debug phone registration step by step"""
    print("🔍 Debugging Phone Registration")
    print("=" * 50)
    
    # Test data
    phone_data = {
        "phone_number": "+233273735993",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "Phone"
    }
    
    print(f"📝 Test Data: {json.dumps(phone_data, indent=2)}")
    
    try:
        # Step 1: Create serializer
        print("\n1️⃣ Creating serializer...")
        serializer = FrontendUserRegistrationSerializer(data=phone_data)
        print("✅ Serializer created successfully")
        
        # Step 2: Validate
        print("\n2️⃣ Validating data...")
        if serializer.is_valid():
            print("✅ Validation passed")
            print(f"📊 Validated data: {serializer.validated_data}")
            
            # Step 3: Try to save
            print("\n3️⃣ Attempting to save...")
            user = serializer.save()
            print(f"✅ User created successfully!")
            print(f"👤 Username: {user.username}")
            print(f"📱 Phone: {user.phone_number}")
            print(f"📧 Email: {user.email}")
            
            # Clean up
            user.delete()
            print("🗑️ Test user cleaned up")
            
        else:
            print("❌ Validation failed")
            print(f"📋 Errors: {serializer.errors}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {str(e)}")
        import traceback
        print("\n📚 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_phone_registration()
