#!/usr/bin/env python
"""
Create test user for login testing
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_user():
    """Create a test user for login testing"""
    phone = "+233548577399"
    password = "Kingsco45@1"
    
    # Check if user already exists
    existing_user = User.objects.filter(phone_number=phone).first()
    
    if existing_user:
        print(f"✅ User already exists: {existing_user.username}")
        print(f"   Phone: {existing_user.phone_number}")
        print(f"   Active: {existing_user.is_active}")
        return existing_user
    
    try:
        # Create new user
        user = User.objects.create_user(
            username='test_login_user',
            phone_number=phone,
            password=password,
            first_name='Test',
            last_name='User',
            is_active=True,
            is_verified=True
        )
        
        print(f"✅ Created test user: {user.username}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Password: {password}")
        print(f"   Active: {user.is_active}")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Creating test user for login testing...")
    create_test_user()
    print("✅ Done!")
