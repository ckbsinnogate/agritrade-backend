#!/usr/bin/env python
"""
Display Farmer Profile Information
Show farmer profile structure and current data from AgriConnect platform
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from users.models import FarmerProfile
from authentication.models import User
from traceability.models import Farm

def display_farmer_profile():
    """Display comprehensive farmer profile information"""
    
    print("🚜 AGRICONNECT FARMER PROFILE INFORMATION")
    print("=" * 60)
    
    # Show FarmerProfile model structure
    print("\n📋 FARMER PROFILE MODEL FIELDS:")
    print("-" * 40)
    
    farmer_fields = FarmerProfile._meta.get_fields()
    for i, field in enumerate(farmer_fields, 1):
        field_type = field.__class__.__name__
        help_text = getattr(field, 'help_text', '')
        print(f"{i:2d}. {field.name:25} | {field_type:15} | {help_text}")
    
    # Show current farmer profiles
    print(f"\n📊 FARMER PROFILES IN DATABASE:")
    print("-" * 40)
    
    farmer_profiles = FarmerProfile.objects.all()
    total_farmers = farmer_profiles.count()
    print(f"Total Farmer Profiles: {total_farmers}")
    
    if farmer_profiles.exists():
        for i, profile in enumerate(farmer_profiles, 1):
            user = profile.user
            print(f"\n👨‍🌾 FARMER PROFILE #{i}")
            print(f"   📧 Email: {user.email}")
            print(f"   📱 Phone: {user.phone_number}")
            print(f"   👤 Name: {user.get_full_name()}")
            print(f"   🌾 Farm Size: {profile.farm_size_acres} acres")
            print(f"   🌱 Primary Crops: {profile.primary_crops}")
            print(f"   📅 Experience: {profile.farming_experience_years} years")
            print(f"   🏆 Organic Certified: {'✅ Yes' if profile.organic_certified else '❌ No'}")
            print(f"   🗣️  Preferred Language: {profile.preferred_language}")
            print(f"   📍 Location: {profile.location}")
            print(f"   💰 Annual Income: {profile.annual_income_range}")
            print(f"   📱 Mobile Money: {profile.mobile_money_number}")
            print(f"   📅 Joined: {profile.created_at.strftime('%Y-%m-%d')}")
            
            # Show associated farms
            farms = Farm.objects.filter(owner=user)
            if farms.exists():
                print(f"   🏭 Associated Farms ({farms.count()}):")
                for farm in farms:
                    print(f"      • {farm.name} - {farm.size_acres} acres ({farm.farm_type})")
                    print(f"        Location: {farm.location}")
                    print(f"        Organic: {'✅' if farm.organic_certified else '❌'}")
            else:
                print("   🏭 No farms registered yet")
    else:
        print("   ⚠️ No farmer profiles found in database")
        print("   💡 Farmers are created automatically when users are assigned FARMER role")
    
    # Show users with FARMER role
    print(f"\n👥 USERS WITH FARMER ROLE:")
    print("-" * 40)
    
    try:
        from users.models import UserRole
        farmer_role = UserRole.objects.filter(name='FARMER').first()
        if farmer_role:
            farmer_users = User.objects.filter(roles=farmer_role)
            print(f"Total users with FARMER role: {farmer_users.count()}")
            
            for user in farmer_users:
                has_profile = hasattr(user, 'farmerprofile')
                print(f"   👤 {user.get_full_name()} - Profile: {'✅' if has_profile else '❌'}")
        else:
            print("   ⚠️ FARMER role not found")
    except Exception as e:
        print(f"   ❌ Error checking farmer roles: {e}")
    
    # Show farmer capabilities
    print(f"\n🌟 FARMER PROFILE CAPABILITIES:")
    print("-" * 40)
    print("✅ Farm registration and verification")
    print("✅ Product listing with organic certification")
    print("✅ Multi-farm inventory management")
    print("✅ Order processing and fulfillment")
    print("✅ Escrow payment protection")
    print("✅ Blockchain product traceability")
    print("✅ SMS/Email notifications")
    print("✅ Weather data integration")
    print("✅ Contract farming partnerships")
    print("✅ Microfinance access")
    print("✅ Premium subscription services")
    print("✅ Agricultural extension services")
    print("✅ Revenue analytics and reporting")
    
    return total_farmers

if __name__ == "__main__":
    try:
        farmer_count = display_farmer_profile()
        print(f"\n✅ Successfully displayed {farmer_count} farmer profile(s)!")
    except Exception as e:
        print(f"\n❌ Error displaying farmer profile: {e}")
        import traceback
        traceback.print_exc()
