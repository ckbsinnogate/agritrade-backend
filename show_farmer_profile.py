#!/usr/bin/env python
"""
Display farmer profile structure and data
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from users.models import FarmerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

def show_farmer_profile_structure():
    print('=' * 60)
    print('AGRICONNECT FARMER PROFILE STRUCTURE')
    print('=' * 60)
    print()
    
    print('FARMER PROFILE MODEL FIELDS:')
    print('-' * 40)
    
    for field in FarmerProfile._meta.fields:
        field_type = field.__class__.__name__
        print(f'  • {field.name}: {field_type}')
        
        if hasattr(field, 'choices') and field.choices:
            print(f'    Choices: {[choice[0] for choice in field.choices]}')
        
        if hasattr(field, 'help_text') and field.help_text:
            print(f'    Help: {field.help_text}')
        
        if hasattr(field, 'default') and field.default is not django.db.models.fields.NOT_PROVIDED:
            print(f'    Default: {field.default}')
        
        print()
    
    print()
    print('CURRENT FARMER PROFILES IN SYSTEM:')
    print('-' * 40)
    
    farmer_profiles = FarmerProfile.objects.all()
    print(f'Total Farmer Profiles: {farmer_profiles.count()}')
    print()
    
    if farmer_profiles.exists():
        for i, profile in enumerate(farmer_profiles, 1):
            print(f'FARMER PROFILE #{i}:')
            print(f'  User: {profile.user.get_full_name()} ({profile.user.email})')
            print(f'  Farm Name: {profile.farm_name or "Not specified"}')
            print(f'  Farm Size: {profile.farm_size} hectares')
            
            farm_type_display = "Not specified"
            if profile.farm_type:
                farm_types = dict(FarmerProfile._meta.get_field('farm_type').choices)
                farm_type_display = farm_types.get(profile.farm_type, profile.farm_type)
            print(f'  Farm Type: {farm_type_display}')
            
            print(f'  Primary Crops: {profile.primary_crops}')
            print(f'  Organic Certified: {"Yes" if profile.organic_certified else "No"}')
            print(f'  Years of Experience: {profile.years_of_experience}')
            print(f'  Production Capacity: {profile.production_capacity} kg/year')
            
            if profile.created_at:
                print(f'  Created: {profile.created_at.strftime("%Y-%m-%d %H:%M")}')
            if profile.updated_at:
                print(f'  Updated: {profile.updated_at.strftime("%Y-%m-%d %H:%M")}')
            print()
    else:
        print('No farmer profiles found in the system.')
    
    print()
    print('FARMER PROFILE FEATURES:')
    print('-' * 40)
    
    features = [
        "✓ Farm size tracking (hectares)",
        "✓ Organic certification status", 
        "✓ Years of farming experience",
        "✓ Annual production capacity",
        "✓ Farm name registration",
        "✓ Farm type categorization (crop/livestock/mixed/organic)",
        "✓ Primary crops management (JSON array)",
        "✓ Automatic timestamps (created/updated)",
        "✓ User relationship (one-to-one with User model)",
        "✓ Data validation (minimum farm size, positive integers)",
        "✓ Django admin integration",
        "✓ String representation for display"
    ]
    
    for feature in features:
        print(f'  {feature}')
    
    print()
    print('=' * 60)

if __name__ == '__main__':
    show_farmer_profile_structure()
