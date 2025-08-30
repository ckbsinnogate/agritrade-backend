import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from users.models import FarmerProfile
from authentication.models import User

# Execute the farmer profile display
farmer_profiles = FarmerProfile.objects.all()
total_farmers = farmer_profiles.count()

print("="*60)
print("AGRICONNECT FARMER PROFILE DISPLAY")
print("="*60)
print(f"Total Farmer Profiles: {total_farmers}")

if farmer_profiles.exists():
    for i, profile in enumerate(farmer_profiles, 1):
        user = profile.user
        print(f"\nFARMER PROFILE #{i}")
        print(f"Email: {user.email}")
        print(f"Phone: {user.phone_number or 'Not provided'}")
        print(f"Name: {user.get_full_name() or user.username}")
        print(f"Farm Name: {profile.farm_name or 'Not specified'}")
        print(f"Farm Size: {profile.farm_size} hectares")
        print(f"Farm Type: {profile.get_farm_type_display() if profile.farm_type else 'Not specified'}")
        print(f"Experience: {profile.years_of_experience} years")
        print(f"Production: {profile.production_capacity} kg/year")
        print(f"Organic: {'Yes' if profile.organic_certified else 'No'}")
        print(f"Primary Crops: {profile.primary_crops}")
        print(f"Created: {profile.created_at.strftime('%Y-%m-%d')}")
else:
    print("No farmer profiles found")

print("="*60)
