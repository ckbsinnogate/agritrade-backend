#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from users.models import FarmerProfile
from authentication.models import User
from traceability.models import Farm

print("🚜 AGRICONNECT FARMER PROFILE DISPLAY")
print("=" * 60)

# Get farmer profiles
farmer_profiles = FarmerProfile.objects.all()
print(f"\n📊 Total Farmer Profiles: {farmer_profiles.count()}")

if farmer_profiles.exists():
    for i, profile in enumerate(farmer_profiles, 1):
        user = profile.user
        print(f"\n👨‍🌾 FARMER PROFILE #{i}")
        print("-" * 40)
        print(f"📧 Email: {user.email}")
        print(f"📱 Phone: {user.phone_number or 'Not provided'}")
        print(f"👤 Full Name: {user.get_full_name() or 'Not provided'}")
        print(f"🆔 User ID: {user.id}")
        print(f"📅 Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
        print(f"✅ Active: {user.is_active}")
        
        # Farmer profile specific fields
        print(f"\n🌾 FARM DETAILS:")
        try:
            print(f"🏭 Farm Size: {profile.farm_size_acres} acres")
            print(f"🌱 Primary Crops: {profile.primary_crops}")
            print(f"📅 Experience: {profile.farming_experience_years} years")
            print(f"🏆 Organic Certified: {'✅ Yes' if profile.organic_certified else '❌ No'}")
            print(f"🗣️ Preferred Language: {profile.preferred_language}")
            print(f"📍 Location: {profile.location}")
            print(f"💰 Income Range: {profile.annual_income_range}")
            print(f"📱 Mobile Money: {profile.mobile_money_number or 'Not provided'}")
            print(f"📅 Profile Created: {profile.created_at.strftime('%Y-%m-%d %H:%M')}")
        except AttributeError as e:
            print(f"⚠️ Some profile fields not available: {e}")
        
        # Check for associated farms
        try:
            farms = Farm.objects.filter(owner=user)
            print(f"\n🏭 Associated Farms: {farms.count()}")
            for farm in farms:
                print(f"   • {farm.name} - {farm.size_acres} acres")
                print(f"     Location: {farm.location}")
                print(f"     Type: {farm.farm_type}")
        except Exception as e:
            print(f"⚠️ Error fetching farms: {e}")

else:
    print("❌ No farmer profiles found in the system")

print(f"\n✅ Farmer profile display completed!")
print("=" * 60)
