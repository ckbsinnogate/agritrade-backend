#!/usr/bin/env python
"""
Create superuser with phone number - no prompts
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User

def create_superuser_phone():
    """Create superuser with phone number"""
    
    phone = "+233273735500"
    password = "admin123456"  # Change this to a secure password
    
    try:
        # Check if user exists
        existing = User.objects.filter(phone_number=phone).first()
        if existing:
            print(f"✅ Superuser already exists:")
            print(f"   Phone: {existing.phone_number}")
            print(f"   Username: {existing.username}")
            print(f"   Is Superuser: {existing.is_superuser}")
            return existing
        
        # Create superuser
        print(f"🔧 Creating superuser with phone: {phone}")
        
        user = User.objects.create_user(
            identifier=phone,
            password=password,
            first_name="Admin",
            last_name="User",
            roles=['ADMIN']
        )
        
        # Set superuser privileges
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.phone_verified = True
        user.save()
        
        print(f"✅ SUPERUSER CREATED!")
        print(f"   Phone: {user.phone_number}")
        print(f"   Username: {user.username}")
        print(f"   Password: {password}")
        print(f"   Is Superuser: {user.is_superuser}")
        print(f"   Is Staff: {user.is_staff}")
        
        return user
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    try:
        print("Starting superuser creation...")
        create_superuser_phone()
        print("Script completed.")
    except Exception as e:
        print(f"SCRIPT ERROR: {e}")
        import traceback
        traceback.print_exc()
