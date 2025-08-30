#!/usr/bin/env python
"""
Test script to verify UserProfileSerializer fix
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User
from authentication.serializers import UserProfileSerializer

def test_serializer():
    print("============================================================")
    print("  TESTING UserProfileSerializer FIX")
    print("============================================================")
    
    try:
        # Get test user
        user = User.objects.get(phone_number='+233548577399')
        print(f"✅ User found: {user.first_name} {user.last_name}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Roles: {[role.name for role in user.roles.all()]}")
        
        # Test serializer
        print("\n🔍 Testing UserProfileSerializer...")
        serializer = UserProfileSerializer(user)
        
        print("✅ Serializer created successfully!")
        
        # Try to access the data
        print("\n🔍 Accessing serializer data...")
        data = serializer.data
        
        print("✅ Serializer data accessed successfully!")
        print(f"   Data keys: {list(data.keys())}")
        print(f"   Roles field: {data.get('roles', 'Not found')}")
        print(f"   Roles display: {data.get('roles_display', 'Not found')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_serializer()
    if success:
        print("\n✅ UserProfileSerializer is working correctly!")
    else:
        print("\n❌ UserProfileSerializer still has issues!")
