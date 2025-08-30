#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from users.models import FarmerProfile
from authentication.models import User
from traceability.models import Farm
from products.models import Product

def main():
    print("========================================================================")
    print("                    AGRICONNECT FARMER PROFILE DISPLAY")
    print("========================================================================")
    
    # Get farmer profiles
    farmer_profiles = FarmerProfile.objects.all()
    total_farmers = farmer_profiles.count()
    
    print(f"📊 FARMER STATISTICS:")
    print(f"   • Total Farmer Profiles: {total_farmers}")
    
    if total_farmers == 0:
        print("   ❌ No farmer profiles found in the system")
        return
    
    print("\n👨‍🌾 FARMER PROFILE DETAILS:")
    print("------------------------------------------------------------------------")
    
    for i, profile in enumerate(farmer_profiles, 1):
        user = profile.user
        
        print(f"\n🔹 FARMER PROFILE #{i}")
        print(f"   📋 BASIC INFORMATION:")
        print(f"      • Profile ID: {profile.id}")
        print(f"      • User ID: {user.id}")
        print(f"      • Email: {user.email}")
        print(f"      • Phone: {user.phone_number or 'Not provided'}")
        print(f"      • Full Name: {user.get_full_name() or user.username}")
        print(f"      • Account Status: {'Active' if user.is_active else 'Inactive'}")
        print(f"      • Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n   🌾 FARM INFORMATION:")
        print(f"      • Farm Name: {profile.farm_name or 'Not specified'}")
        print(f"      • Farm Size: {profile.farm_size} hectares")
        print(f"      • Farm Type: {profile.get_farm_type_display() if profile.farm_type else 'Not specified'}")
        print(f"      • Years of Experience: {profile.years_of_experience}")
        print(f"      • Production Capacity: {profile.production_capacity} kg/year")
        print(f"      • Organic Certified: {'Yes' if profile.organic_certified else 'No'}")
        print(f"      • Primary Crops: {profile.primary_crops}")
        print(f"      • Profile Created: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      • Last Updated: {profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get associated farms
        try:
            farms = Farm.objects.filter(farmer=user)
            print(f"\n   🏭 ASSOCIATED FARMS ({farms.count()}):")
            if farms.exists():
                for j, farm in enumerate(farms, 1):
                    print(f"      {j}. {farm.name}")
                    print(f"         • Size: {farm.farm_size_hectares} hectares")
                    print(f"         • Location: {farm.location}")
                    print(f"         • Organic Certified: {'Yes' if farm.organic_certified else 'No'}")
            else:
                print("      • No farms registered yet")
        except Exception as e:
            print(f"      • Error fetching farms: {e}")
        
        # Get farmer's products
        try:
            products = Product.objects.filter(farmer=user)
            print(f"\n   📦 FARMER'S PRODUCTS ({products.count()}):")
            if products.exists():
                for j, product in enumerate(products, 1):
                    category_name = product.category.name if product.category else 'No category'
                    print(f"      {j}. {product.name} ({category_name})")
                    print(f"         • Price: ${product.price_per_unit}")
                    print(f"         • Unit: {product.unit}")
                    print(f"         • Stock: {product.quantity_available}")
            else:
                print("      • No products listed yet")
        except Exception as e:
            print(f"      • Error fetching products: {e}")
        
        print("------------------------------------------------------------------------")
    
    # Display model structure
    print(f"\n🔧 FARMER PROFILE MODEL STRUCTURE:")
    print("----------------------------------------------------")
    
    farmer_profile_fields = FarmerProfile._meta.get_fields()
    print(f"   📋 Total Fields: {len(farmer_profile_fields)}")
    
    for i, field in enumerate(farmer_profile_fields, 1):
        field_type = field.__class__.__name__
        print(f"   {i:2d}. {field.name:25} | {field_type}")
    
    print(f"\n✅ Farmer profile display completed successfully!")
    print("========================================================================")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
