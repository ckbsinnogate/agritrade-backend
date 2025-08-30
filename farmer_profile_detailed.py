#!/usr/bin/env python
"""
Farmer Profile Display Script for AgriConnect Platform
Shows detailed farmer profile structure and real data
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from users.models import FarmerProfile
from authentication.models import User
from traceability.models import Farm
from products.models import Product, Category

def main():
    print("🚜 AGRICONNECT FARMER PROFILE DETAILED DISPLAY")
    print("=" * 70)
    
    # Get all farmer profiles
    farmer_profiles = FarmerProfile.objects.all()
    total_farmers = farmer_profiles.count()
    
    print(f"\n📊 FARMER STATISTICS:")
    print(f"   • Total Farmer Profiles: {total_farmers}")
    
    if total_farmers == 0:
        print("   ❌ No farmer profiles found in the system")
        return
    
    print(f"\n👨‍🌾 DETAILED FARMER PROFILE INFORMATION:")
    print("-" * 70)
    
    for i, profile in enumerate(farmer_profiles, 1):
        user = profile.user
        
        print(f"\n🔹 FARMER PROFILE #{i}")
        print(f"   📋 BASIC INFORMATION:")
        print(f"      • Profile ID: {profile.id}")
        print(f"      • User ID: {user.id}")
        print(f"      • Email: {user.email}")
        print(f"      • Phone: {user.phone_number or 'Not provided'}")
        print(f"      • Full Name: {user.get_full_name() or user.username}")
        print(f"      • Account Status: {'✅ Active' if user.is_active else '❌ Inactive'}")
        print(f"      • Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get all available fields from the farmer profile
        print(f"\n   🌾 FARMER PROFILE DETAILS:")
        profile_fields = profile._meta.get_fields()
        
        for field in profile_fields:
            if hasattr(profile, field.name) and field.name not in ['id', 'user']:
                try:
                    value = getattr(profile, field.name)
                    if value is not None:
                        if field.name in ['created_at', 'updated_at']:
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        print(f"      • {field.name.replace('_', ' ').title()}: {value}")
                except Exception as e:
                    print(f"      • {field.name}: Error retrieving value")
        
        # Get associated farms
        try:
            farms = Farm.objects.filter(farmer=user)
            print(f"\n   🏭 ASSOCIATED FARMS ({farms.count()}):")
            if farms.exists():
                for j, farm in enumerate(farms, 1):
                    print(f"      {j}. Farm Name: {farm.name}")
                    print(f"         Size: {farm.size} hectares")
                    print(f"         Location: {farm.location}")
                    print(f"         Farm Type: {getattr(farm, 'farm_type', 'Not specified')}")
                    print(f"         Organic: {'✅ Yes' if getattr(farm, 'is_organic', False) else '❌ No'}")
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
                    print(f"         Price: ${product.price_per_unit}")
                    print(f"         Unit: {product.unit}")
                    print(f"         Stock: {product.quantity_available}")
                    print(f"         Description: {product.description[:50]}..." if len(product.description) > 50 else f"         Description: {product.description}")
            else:
                print("      • No products listed yet")
        except Exception as e:
            print(f"      • Error fetching products: {e}")
        
        print("-" * 70)
    
    # Display model structure
    print(f"\n🔧 FARMER PROFILE MODEL STRUCTURE:")
    print("-" * 50)
    
    farmer_profile_fields = FarmerProfile._meta.get_fields()
    print(f"   📋 Total Fields: {len(farmer_profile_fields)}")
    
    for i, field in enumerate(farmer_profile_fields, 1):
        field_type = field.__class__.__name__
        print(f"   {i:2d}. {field.name:25} | {field_type}")
    
    print(f"\n✅ Farmer profile display completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
