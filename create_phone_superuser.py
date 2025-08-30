#!/usr/bin/env python
"""
Create superuser with phone number
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User

def create_phone_superuser():
    """Create a superuser with phone number"""
    phone = "+233273735500"
    password = "admin123456"  # You should change this
    
    try:
        # Check if user already exists
        if User.objects.filter(phone_number=phone).exists():
            print(f"❌ User with phone {phone} already exists")
            user = User.objects.get(phone_number=phone)
            print(f"   Username: {user.username}")
            print(f"   Is superuser: {user.is_superuser}")
            return user
        
        # Create superuser
        print(f"🔧 Creating superuser with phone: {phone}")
        user = User.objects.create_user(
            identifier=phone,
            password=password,
            roles=['ADMIN']
        )
        
        # Make superuser
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.phone_verified = True
        user.save()
        
        print(f"✅ Superuser created successfully!")
        print(f"   Phone: {user.phone_number}")
        print(f"   Username: {user.username}")
        print(f"   Password: {password}")
        print(f"   Is superuser: {user.is_superuser}")
        print(f"   Is staff: {user.is_staff}")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_phone_superuser()
