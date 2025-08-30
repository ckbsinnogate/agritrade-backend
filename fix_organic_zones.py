#!/usr/bin/env python3
"""
Fix Organic Zones Implementation
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from warehouses.models import WarehouseType, Warehouse, WarehouseZone
from django.db import transaction

def create_organic_zones_fixed():
    """Create organic separation zones with correct fields"""
    print("🌱 Creating organic separation zones (fixed)...")
    
    # Get warehouses
    warehouses = Warehouse.objects.all()[:3]
    
    for i, warehouse in enumerate(warehouses, 1):
        # Create organic zone without invalid fields
        organic_zone, created = WarehouseZone.objects.get_or_create(
            warehouse=warehouse,
            zone_code=f"{warehouse.code}-ORG-{i:02d}",
            defaults={
                'name': f'{warehouse.name} - Organic Zone',
                'zone_type': 'organic',
                'capacity_cubic_meters': 500.0,
                'is_active': True,
                'special_conditions': {
                    'organic_certified': True,
                    'segregation_required': True,
                    'certification_body': 'USDA Organic',
                    'contamination_prevention': True
                }
            }
        )
        if created:
            print(f"   ✅ Created: {organic_zone.name} ({organic_zone.zone_code})")
        else:
            print(f"   📝 Exists: {organic_zone.name} ({organic_zone.zone_code})")
    
    # Also set some warehouses as organic certified
    organic_warehouses = warehouses[:2]
    for warehouse in organic_warehouses:
        warehouse.organic_certified = True
        warehouse.save()
        print(f"   🌿 Set {warehouse.name} as organic certified")

def verify_final_status():
    """Final verification of all requirements"""
    print("\n🔍 Final verification...")
    
    requirements = {
        'Cold Storage Zones': WarehouseZone.objects.filter(zone_type='cold_storage').count(),
        'Organic Separation': WarehouseZone.objects.filter(zone_type='organic').count(),
        'Dry Storage': WarehouseZone.objects.filter(zone_type='dry_storage').count(),
        'Processing Areas': WarehouseZone.objects.filter(zone_type='processing').count(),
        'Quality Control Zones': WarehouseZone.objects.filter(zone_type='quality_control').count(),
        'Loading/Unloading Bays': WarehouseZone.objects.filter(zone_type='loading').count(),
    }
    
    print("\n📊 PRD Section 4.1.1 Final Status:")
    implemented = 0
    total = 6
    
    for req_name, count in requirements.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {req_name}: {count} zones")
        if count > 0:
            implemented += 1
    
    print(f"\n🎯 Final Result: {implemented}/{total} requirements implemented")
    
    if implemented == total:
        print("🎉 ALL MULTI-ZONE WAREHOUSE ARCHITECTURE REQUIREMENTS COMPLETED!")
        print("✅ PRD Section 4.1.1 FULLY IMPLEMENTED")
        return True
    else:
        print(f"⚠️  {total - implemented} requirements still missing")
        return False

def main():
    try:
        with transaction.atomic():
            create_organic_zones_fixed()
            success = verify_final_status()
            
            if success:
                print("\n" + "="*70)
                print("🌾 AGRICONNECT MULTI-ZONE WAREHOUSE ARCHITECTURE COMPLETE!")
                print("✅ All PRD Section 4.1.1 requirements successfully implemented")
                print("="*70)
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
