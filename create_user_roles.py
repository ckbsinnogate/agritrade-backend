#!/usr/bin/env python
"""
Create all 11 user roles in the database
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import UserRole

def create_user_roles():
    """Create all user roles from the PRD"""
    roles_data = [
        ('FARMER', 'Agricultural producers and crop growers'),
        ('PROCESSOR', 'Food processors and value-addition companies'),
        ('CONSUMER', 'End consumers purchasing agricultural products'),
        ('INSTITUTION', 'Institutional buyers like restaurants, hotels, schools'),
        ('ADMINISTRATOR', 'System administrators and platform managers'),
        ('WAREHOUSE_MANAGER', 'Warehouse and storage facility managers'),
        ('QUALITY_INSPECTOR', 'Quality control and certification inspectors'),
        ('LOGISTICS_PARTNER', 'Transportation and logistics service providers'),
        ('AGENT', 'Sales representatives and field officers'),
        ('FINANCIAL_PARTNER', 'Banks, mobile money operators, microfinance institutions'),
        ('GOVERNMENT_OFFICIAL', 'Agricultural ministry representatives and officials'),
    ]
    
    created_count = 0
    existing_count = 0
    
    print("Creating user roles...")
    
    for role_name, description in roles_data:
        role, created = UserRole.objects.get_or_create(
            name=role_name,
            defaults={'description': description}
        )
        
        if created:
            print(f"✅ Created: {role_name}")
            created_count += 1
        else:
            print(f"ℹ️  Exists: {role_name}")
            existing_count += 1
    
    print(f"\n📊 Summary:")
    print(f"Created: {created_count}")
    print(f"Already existed: {existing_count}")
    print(f"Total roles: {created_count + existing_count}")
    
    # Verify all roles exist
    all_roles = UserRole.objects.all().values_list('name', flat=True)
    print(f"\n🔍 All roles in database: {list(all_roles)}")
    
    if len(all_roles) == 11:
        print("🎉 SUCCESS: All 11 user types are now in the database!")
    else:
        print(f"⚠️  Warning: Expected 11 roles, found {len(all_roles)}")

if __name__ == "__main__":
    create_user_roles()
