#!/usr/bin/env python
"""
Direct test of FrontendUserRegistrationSerializer
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
sys.path.insert(0, os.path.abspath('.'))
django.setup()

from authentication.frontend_serializers import FrontendUserRegistrationSerializer
import traceback

def test_serializer_directly():
    print("🧪 Testing FrontendUserRegistrationSerializer directly")
    print("=" * 60)
    
    # Test data with phone number
    phone_data = {
        "phone_number": "+233273735996",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "SMS"
    }
    
    print("📱 Testing with phone number:")
    print(f"Data: {phone_data}")
    
    try:
        serializer = FrontendUserRegistrationSerializer(data=phone_data)
        print(f"✅ Serializer created")
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            print(f"Validated data: {serializer.validated_data}")
            
            # Try to save
            user = serializer.save()
            print(f"✅ User created successfully: {user.username}")
            
        else:
            print("❌ Serializer validation failed")
            print(f"Errors: {serializer.errors}")
            
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    
    # Test data with email
    email_data = {
        "email": "test999@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "Email"
    }
    
    print("📧 Testing with email:")
    print(f"Data: {email_data}")
    
    try:
        serializer = FrontendUserRegistrationSerializer(data=email_data)
        print(f"✅ Serializer created")
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            print(f"Validated data: {serializer.validated_data}")
            
            # Try to save
            user = serializer.save()
            print(f"✅ User created successfully: {user.username}")
            
        else:
            print("❌ Serializer validation failed")
            print(f"Errors: {serializer.errors}")
            
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_serializer_directly()
