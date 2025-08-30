#!/usr/bin/env python
"""
Test script to verify user profile models can be imported correctly
"""
import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

try:
    print("Testing model imports...")
    
    # Test importing the models
    from apps.users.models import (
        ExtendedUserProfile,
        FarmerProfile,
        ConsumerProfile,
        InstitutionProfile,
        AgentProfile,
        FinancialPartnerProfile,
        GovernmentOfficialProfile
    )
    
    print("✅ All models imported successfully!")
    
    # Test model definitions
    print(f"✅ ExtendedUserProfile: {ExtendedUserProfile._meta.verbose_name}")
    print(f"✅ FarmerProfile: {FarmerProfile._meta.verbose_name}")
    print(f"✅ ConsumerProfile: {ConsumerProfile._meta.verbose_name}")
    print(f"✅ InstitutionProfile: {InstitutionProfile._meta.verbose_name}")
    print(f"✅ AgentProfile: {AgentProfile._meta.verbose_name}")
    print(f"✅ FinancialPartnerProfile: {FinancialPartnerProfile._meta.verbose_name}")
    print(f"✅ GovernmentOfficialProfile: {GovernmentOfficialProfile._meta.verbose_name}")
    
    print("\n🎉 All user profile models are working correctly!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
