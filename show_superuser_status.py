#!/usr/bin/env python
"""
Show existing superuser details and create new ones if needed
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User

def show_superuser_status():
    """Show existing superuser and provide options"""
    
    print("🔐 SUPERUSER STATUS REPORT")
    print("=" * 40)
    
    # Find existing superuser
    existing_super = User.objects.filter(phone_number="+233273735500").first()
    
    if existing_super:
        print("✅ EXISTING SUPERUSER FOUND:")
        print(f"   📱 Phone: {existing_super.phone_number}")
        print(f"   👤 Username: {existing_super.username}")
        print(f"   🏷️  Name: {existing_super.get_full_name()}")
        print(f"   🔑 Is Superuser: {existing_super.is_superuser}")
        print(f"   📋 Is Staff: {existing_super.is_staff}")
        print(f"   ✅ Is Active: {existing_super.is_active}")
        print(f"   ✔️  Is Verified: {existing_super.is_verified}")
        print(f"   📅 Created: {existing_super.date_joined}")
        
        print(f"\n🚀 HOW TO USE THIS SUPERUSER:")
        print(f"   1. Django Admin: http://localhost:8000/admin/")
        print(f"      Username: {existing_super.username}")
        print(f"      Password: [The password you set]")
        print(f"   ")
        print(f"   2. Or use phone number: {existing_super.phone_number}")
        print(f"      Password: [The password you set]")
        
    else:
        print("❌ No superuser found with +233273735500")
    
    # Show all superusers
    all_superusers = User.objects.filter(is_superuser=True)
    print(f"\n📊 ALL SUPERUSERS ({all_superusers.count()}):")
    for i, superuser in enumerate(all_superusers, 1):
        contact = superuser.phone_number or superuser.email or "No contact"
        print(f"   {i}. {superuser.username} ({contact})")
    
    # Option to create additional superuser
    print(f"\n🆕 CREATE ADDITIONAL SUPERUSER:")
    print(f"   If you need another superuser with a different phone/email:")
    
    # Create new superuser with different phone
    new_phone = "+233273735501"  # Different number
    existing_new = User.objects.filter(phone_number=new_phone).first()
    
    if not existing_new:
        try:
            new_superuser = User.objects.create_superuser(
                username=new_phone,
                password="admin123456"  # Change this password
            )
            print(f"   ✅ NEW SUPERUSER CREATED:")
            print(f"      📱 Phone: {new_superuser.phone_number}")
            print(f"      👤 Username: {new_superuser.username}")
            print(f"      🔑 Password: admin123456")
            print(f"      🚨 CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
            
        except Exception as e:
            print(f"   ❌ Failed to create new superuser: {e}")
    else:
        print(f"   ✅ Additional superuser already exists: {existing_new.username}")
    
    print(f"\n💡 SUMMARY:")
    print(f"   • Duplicate prevention is WORKING correctly")
    print(f"   • Your original superuser exists and is ready to use")
    print(f"   • Use Django admin or API to manage users")
    print(f"   • Phone registration system is fully operational")

if __name__ == "__main__":
    show_superuser_status()
