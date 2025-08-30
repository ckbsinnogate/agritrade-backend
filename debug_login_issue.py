#!/usr/bin/env python
"""
Debug login issues
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

def check_user_exists():
    """Check if the user exists and can be authenticated"""
    phone = "+233548577399"
    password = "Kingsco45@1"
    
    print("🔍 Checking user existence...")
    
    try:
        # Check if user exists by phone
        user = User.objects.filter(phone_number=phone).first()
        
        if not user:
            print(f"❌ No user found with phone number: {phone}")
            
            # Check all users with phone numbers
            users_with_phones = User.objects.filter(phone_number__isnull=False).values_list('phone_number', 'username', 'first_name', 'last_name')
            print(f"📱 Users with phone numbers in database: {list(users_with_phones)}")
            return False
        
        print(f"✅ User found: {user.username} ({user.first_name} {user.last_name})")
        print(f"   Phone: {user.phone_number}")
        print(f"   Email: {user.email}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Is Verified: {getattr(user, 'is_verified', 'N/A')}")
        
        # Try to authenticate
        auth_user = authenticate(username=user.username, password=password)
        
        if auth_user:
            print("✅ Authentication successful")
            return True
        else:
            print("❌ Authentication failed - wrong password")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False

def test_serializer():
    """Test the UserLoginSerializer directly"""
    print("\n🔍 Testing UserLoginSerializer...")
    
    try:
        from authentication.serializers import UserLoginSerializer
        
        data = {
            'identifier': '+233548577399',
            'password': 'Kingsco45@1'
        }
        
        serializer = UserLoginSerializer(data=data)
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            print(f"   Validated data: {serializer.validated_data}")
            return True
        else:
            print("❌ Serializer validation failed")
            print(f"   Errors: {serializer.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing serializer: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  LOGIN DEBUG ANALYSIS")
    print("=" * 60)
    
    check_user_exists()
    test_serializer()
    
    print("\n" + "=" * 60)
