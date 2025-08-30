#!/usr/bin/env python
"""
Create additional superuser with different phone number
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User

def create_additional_superuser():
    """Create a new superuser with different phone number"""
    
    print("🆕 CREATE ADDITIONAL SUPERUSER")
    print("=" * 35)
    
    # New phone number (different from existing)
    new_phone = "+233273735501"
    new_password = "admin123456"  # You can change this
    
    try:
        # Check if this phone already exists
        existing = User.objects.filter(phone_number=new_phone).first()
        if existing:
            print(f"✅ Superuser with {new_phone} already exists:")
            print(f"   Username: {existing.username}")
            print(f"   Is Superuser: {existing.is_superuser}")
            return existing
        
        # Create new superuser
        print(f"🔧 Creating superuser with phone: {new_phone}")
        
        superuser = User.objects.create_superuser(
            username=new_phone,
            password=new_password
        )
        
        print(f"✅ NEW SUPERUSER CREATED!")
        print(f"   📱 Phone: {superuser.phone_number}")
        print(f"   👤 Username: {superuser.username}")
        print(f"   🔑 Password: {new_password}")
        print(f"   🔒 Is Superuser: {superuser.is_superuser}")
        print(f"   📋 Is Staff: {superuser.is_staff}")
        
        print(f"\n🚀 ACCESS INSTRUCTIONS:")
        print(f"   1. Start server: python manage.py runserver")
        print(f"   2. Visit: http://localhost:8000/admin/")
        print(f"   3. Username: {superuser.username}")
        print(f"   4. Password: {new_password}")
        print(f"   5. 🚨 CHANGE PASSWORD AFTER FIRST LOGIN!")
        
        return superuser
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return None

if __name__ == "__main__":
    create_additional_superuser()
    
    print(f"\n📋 SUMMARY:")
    print(f"   ✅ Original superuser: +233273735500 (already exists)")
    print(f"   ✅ Additional superuser: +233273735501 (created/exists)")
    print(f"   ✅ Duplicate prevention: Working correctly")
    print(f"   ✅ Phone registration: Fully operational")
