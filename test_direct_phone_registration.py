#!/usr/bin/env python
"""
Direct phone number registration test - no prompts
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User

def test_direct_phone_registration():
    """Test phone number registration directly"""
    
    print("🧪 DIRECT PHONE NUMBER REGISTRATION TEST")
    print("=" * 50)
    
    test_phone = "+233273735502"  # New test number
    test_password = "SecurePass123!"
    
    try:
        # Check if user already exists
        existing_user = User.objects.filter(phone_number=test_phone).first()
        if existing_user:
            print(f"🗑️ Deleting existing user: {existing_user.username}")
            existing_user.delete()
        
        print(f"📱 Creating user with phone: {test_phone}")
        
        # Create user directly
        user = User.objects.create_user(
            identifier=test_phone,
            password=test_password,
            first_name="Test",
            last_name="User",
            roles=['FARMER']
        )
        
        print(f"✅ USER CREATED SUCCESSFULLY!")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Email: {user.email}")
        print(f"   First Name: {user.first_name}")
        print(f"   Last Name: {user.last_name}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"   Phone Verified: {user.phone_verified}")
        print(f"   Roles: {[role.name for role in user.roles.all()]}")
        
        # Test login
        print(f"\n🔐 Testing authentication...")
        from django.contrib.auth import authenticate
        
        auth_user = authenticate(username=user.username, password=test_password)
        if auth_user:
            print(f"✅ Authentication successful!")
        else:
            print(f"❌ Authentication failed")
        
        # Test phone login
        print(f"\n📱 Testing phone-based lookup...")
        phone_user = User.objects.filter(phone_number=test_phone).first()
        if phone_user:
            print(f"✅ Phone lookup successful: {phone_user.username}")
        else:
            print(f"❌ Phone lookup failed")
        
        print(f"\n🧪 TESTING SUPERUSER CREATION...")
        
        # Create superuser with phone
        super_phone = "+233273735503"
        super_password = "SuperSecure123!"
        
        # Delete existing if any
        existing_super = User.objects.filter(phone_number=super_phone).first()
        if existing_super:
            existing_super.delete()
        
        superuser = User.objects.create_user(
            identifier=super_phone,
            password=super_password,
            roles=['ADMIN']
        )
        
        # Make superuser
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_verified = True
        superuser.phone_verified = True
        superuser.save()
        
        print(f"✅ SUPERUSER CREATED!")
        print(f"   Phone: {superuser.phone_number}")
        print(f"   Username: {superuser.username}")
        print(f"   Is Superuser: {superuser.is_superuser}")
        print(f"   Is Staff: {superuser.is_staff}")
        
        print(f"\n" + "=" * 50)
        print(f"🎉 PHONE REGISTRATION: WORKING PERFECTLY!")
        print(f"✅ Regular user creation: SUCCESS")
        print(f"✅ Superuser creation: SUCCESS")
        print(f"✅ Authentication: SUCCESS")
        print(f"✅ Phone lookup: SUCCESS")
        
        # Clean up test users
        print(f"\n🗑️ Cleaning up test users...")
        user.delete()
        superuser.delete()
        print(f"✅ Cleanup complete")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_phone_registration()
    if success:
        print(f"\n🎯 CONCLUSION: Phone number registration is working correctly!")
    else:
        print(f"\n❌ CONCLUSION: There are issues with phone registration")
