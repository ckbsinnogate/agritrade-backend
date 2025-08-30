#!/usr/bin/env python
"""
Test Username Fix - Verify new registration uses email/phone as username
"""
import os
import sys
import django

# Add the project root to Python path
project_root = r'c:\Users\user\Desktop\mywebproject\backup_v1\myapiproject'
sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
django.setup()

from authentication.models import User, UserRole

def test_username_system():
    """Test that new users get email/phone as username"""
    print("=== Testing Updated Username System ===\n")
    
    # Test 1: Email registration
    print("Test 1: Email Registration")
    test_email = "test.user@example.com"
    test_password = "testpass123"
    
    try:
        # Check if user already exists
        existing_user = User.objects.filter(email=test_email).first()
        if existing_user:
            print(f"   Deleting existing test user: {existing_user.username}")
            existing_user.delete()
        
        # Create new user with email
        user = User.objects.create_user(
            identifier=test_email,
            password=test_password,
            roles=['CONSUMER']
        )
        
        print(f"   ✓ User created successfully")
        print(f"   ✓ Email: {user.email}")
        print(f"   ✓ Username: {user.username}")
        print(f"   ✓ Username matches email: {user.username == user.email}")
        
        if user.username != user.email:
            print(f"   ❌ ERROR: Username should be email but got '{user.username}'")
        else:
            print(f"   ✅ SUCCESS: Username correctly set to email")
        
        # Clean up
        user.delete()
        
    except Exception as e:
        print(f"   ❌ Email registration failed: {e}")
    
    print()
    
    # Test 2: Phone registration
    print("Test 2: Phone Registration")
    test_phone = "+233123456789"
    
    try:
        # Check if user already exists
        existing_user = User.objects.filter(phone_number=test_phone).first()
        if existing_user:
            print(f"   Deleting existing test user: {existing_user.username}")
            existing_user.delete()
        
        # Create new user with phone
        user = User.objects.create_user(
            identifier=test_phone,
            password=test_password,
            roles=['FARMER']
        )
        
        print(f"   ✓ User created successfully")
        print(f"   ✓ Phone: {user.phone_number}")
        print(f"   ✓ Username: {user.username}")
        print(f"   ✓ Username matches phone: {user.username == user.phone_number}")
        
        if user.username != user.phone_number:
            print(f"   ❌ ERROR: Username should be phone but got '{user.username}'")
        else:
            print(f"   ✅ SUCCESS: Username correctly set to phone number")
        
        # Clean up
        user.delete()
        
    except Exception as e:
        print(f"   ❌ Phone registration failed: {e}")
    
    print()
    
    # Test 3: Superuser creation with phone
    print("Test 3: Superuser Creation with Phone")
    test_superuser_phone = "+233987654321"
    
    try:
        # Check if superuser already exists
        existing_user = User.objects.filter(phone_number=test_superuser_phone).first()
        if existing_user:
            print(f"   Deleting existing test superuser: {existing_user.username}")
            existing_user.delete()
        
        # Create superuser with phone
        superuser = User.objects.create_superuser(
            username=test_superuser_phone,
            password=test_password
        )
        
        print(f"   ✓ Superuser created successfully")
        print(f"   ✓ Phone: {superuser.phone_number}")
        print(f"   ✓ Username: {superuser.username}")
        print(f"   ✓ Username matches phone: {superuser.username == superuser.phone_number}")
        print(f"   ✓ Is superuser: {superuser.is_superuser}")
        print(f"   ✓ Is staff: {superuser.is_staff}")
        
        if superuser.username != superuser.phone_number:
            print(f"   ❌ ERROR: Username should be phone but got '{superuser.username}'")
        else:
            print(f"   ✅ SUCCESS: Superuser username correctly set to phone number")
        
        # Clean up
        superuser.delete()
        
    except Exception as e:
        print(f"   ❌ Superuser creation failed: {e}")
    
    print()
    
    # Test 4: Existing user check
    print("Test 4: Check Existing Superuser")
    try:
        existing_superuser = User.objects.filter(phone_number="+233273735500").first()
        if existing_superuser:
            print(f"   ✓ Found existing superuser")
            print(f"   ✓ Phone: {existing_superuser.phone_number}")
            print(f"   ✓ Username: {existing_superuser.username}")
            print(f"   ✓ Is superuser: {existing_superuser.is_superuser}")
            
            # Check if username follows old or new pattern
            if existing_superuser.username == existing_superuser.phone_number:
                print(f"   ✅ Existing user already has correct username format")
            else:
                print(f"   ⚠️  Existing user has old username format: {existing_superuser.username}")
                print(f"   ⚠️  Consider updating to new format: {existing_superuser.phone_number}")
        else:
            print(f"   ❌ No existing superuser found with phone +233273735500")
    except Exception as e:
        print(f"   ❌ Error checking existing user: {e}")
    
    print("\n=== Username System Test Complete ===")

if __name__ == "__main__":
    test_username_system()
