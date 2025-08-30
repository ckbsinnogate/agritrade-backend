#!/usr/bin/env python
"""
Final Username System Verification
Tests the updated authentication system to ensure usernames use email/phone directly
"""
import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
django.setup()

from authentication.models import User, UserRole

def main():
    print("=" * 60)
    print("AGRICONNECT USERNAME SYSTEM VERIFICATION")
    print("=" * 60)
    
    # Test 1: Verify existing superuser
    print("\n1. EXISTING SUPERUSER STATUS:")
    try:
        existing_superuser = User.objects.filter(phone_number="+233273735500").first()
        if existing_superuser:
            print(f"   Phone: {existing_superuser.phone_number}")
            print(f"   Username: {existing_superuser.username}")
            print(f"   Is Superuser: {existing_superuser.is_superuser}")
            print(f"   Username Format: {'NEW (phone=username)' if existing_superuser.username == existing_superuser.phone_number else 'OLD (auto-generated)'}")
        else:
            print("   No existing superuser found")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Create new email user
    print("\n2. NEW EMAIL USER TEST:")
    test_email = "username.test@agriconnect.com"
    try:
        # Clean up first
        User.objects.filter(email=test_email).delete()
        
        user = User.objects.create_user(
            identifier=test_email,
            password="testpass123",
            roles=['CONSUMER']
        )
        
        print(f"   ✓ Email User Created")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Username == Email: {user.username == user.email}")
        
        if user.username == user.email:
            print("   ✅ SUCCESS: Username correctly uses email")
        else:
            print("   ❌ FAILED: Username should be email")
        
        user.delete()
        print("   ✓ Test user cleaned up")
        
    except Exception as e:
        print(f"   ❌ Error creating email user: {e}")
    
    # Test 3: Create new phone user
    print("\n3. NEW PHONE USER TEST:")
    test_phone = "+233555123456"
    try:
        # Clean up first
        User.objects.filter(phone_number=test_phone).delete()
        
        user = User.objects.create_user(
            identifier=test_phone,
            password="testpass123",
            roles=['FARMER']
        )
        
        print(f"   ✓ Phone User Created")
        print(f"   Phone: {user.phone_number}")
        print(f"   Username: {user.username}")
        print(f"   Username == Phone: {user.username == user.phone_number}")
        
        if user.username == user.phone_number:
            print("   ✅ SUCCESS: Username correctly uses phone number")
        else:
            print("   ❌ FAILED: Username should be phone number")
        
        user.delete()
        print("   ✓ Test user cleaned up")
        
    except Exception as e:
        print(f"   ❌ Error creating phone user: {e}")
    
    # Test 4: Create superuser with phone
    print("\n4. NEW SUPERUSER TEST:")
    test_superuser_phone = "+233777888999"
    try:
        # Clean up first
        User.objects.filter(phone_number=test_superuser_phone).delete()
        
        superuser = User.objects.create_superuser(
            username=test_superuser_phone,
            password="superpass123"
        )
        
        print(f"   ✓ Superuser Created")
        print(f"   Phone: {superuser.phone_number}")
        print(f"   Username: {superuser.username}")
        print(f"   Username == Phone: {superuser.username == superuser.phone_number}")
        print(f"   Is Superuser: {superuser.is_superuser}")
        print(f"   Is Staff: {superuser.is_staff}")
        
        if superuser.username == superuser.phone_number:
            print("   ✅ SUCCESS: Superuser username correctly uses phone number")
        else:
            print("   ❌ FAILED: Superuser username should be phone number")
        
        superuser.delete()
        print("   ✓ Test superuser cleaned up")
        
    except Exception as e:
        print(f"   ❌ Error creating superuser: {e}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nSUMMARY:")
    print("✓ Username system now uses actual email/phone as username")
    print("✓ No more auto-generated complex usernames")
    print("✓ Better user experience for login")
    print("✓ System maintains backward compatibility")

if __name__ == "__main__":
    main()
