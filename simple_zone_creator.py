#!/usr/bin/env python3
"""
Simple Multi-Zone Warehouse Implementation
"""

import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from warehouses.models import Warehouse, WarehouseZone, WarehouseType

print("🏗️  AgriConnect Multi-Zone Warehouse Implementation")
print("="*60)

# Get warehouses
warehouses = Warehouse.objects.all()
print(f"📋 Found {warehouses.count()} warehouses")

zones_created = 0

for warehouse in warehouses:
    print(f"\n🏢 {warehouse.name} ({warehouse.code})")
    
    # Check what zones already exist
    existing_zones = list(warehouse.zones.values_list('zone_type', flat=True))
    print(f"   Existing zones: {existing_zones}")
    
    # Add missing zones
    missing_zones = []
    
    # 1. Organic Zone
    if 'organic' not in existing_zones:
        try:
            organic_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"ORG-01",
                name="Organic Products Zone",
                zone_type='organic',
                capacity_cubic_meters=Decimal('500.00'),
                temperature_range={'min': 10, 'max': 20},
                requires_certification=True
            )
            print(f"   ✅ Created Organic Zone: {organic_zone.zone_code}")
            zones_created += 1
        except Exception as e:
            print(f"   ❌ Failed to create organic zone: {e}")
    
    # 2. Processing Zone
    if 'processing' not in existing_zones:
        try:
            processing_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"PROC-01",
                name="Processing Area",
                zone_type='processing',
                capacity_cubic_meters=Decimal('300.00'),
                temperature_range={'min': 15, 'max': 25}
            )
            print(f"   ✅ Created Processing Zone: {processing_zone.zone_code}")
            zones_created += 1
        except Exception as e:
            print(f"   ❌ Failed to create processing zone: {e}")
    
    # 3. Packaging Zone
    if 'packaging' not in existing_zones:
        try:
            packaging_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"PKG-01",
                name="Packaging Facility",
                zone_type='packaging',
                capacity_cubic_meters=Decimal('200.00'),
                temperature_range={'min': 18, 'max': 24}
            )
            print(f"   ✅ Created Packaging Zone: {packaging_zone.zone_code}")
            zones_created += 1
        except Exception as e:
            print(f"   ❌ Failed to create packaging zone: {e}")
    
    # 4. Loading Zone
    if 'loading' not in existing_zones:
        try:
            loading_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"LOAD-01",
                name="Loading/Unloading Bay",
                zone_type='loading',
                capacity_cubic_meters=Decimal('150.00'),
                special_conditions={'truck_access': True, 'dock_doors': 4}
            )
            print(f"   ✅ Created Loading Zone: {loading_zone.zone_code}")
            zones_created += 1
            
            # Update warehouse loading dock status
            warehouse.has_loading_dock = True
            warehouse.save()
            print(f"   ✅ Updated loading dock status")
        except Exception as e:
            print(f"   ❌ Failed to create loading zone: {e}")

print(f"\n🎉 Implementation Complete!")
print(f"   📊 Total zones created: {zones_created}")
print(f"   🏗️  Total zones now: {WarehouseZone.objects.count()}")

# Check zone distribution
print(f"\n📊 Zone Type Distribution:")
for zone_type, zone_name in WarehouseZone.ZONE_TYPE_CHOICES:
    count = WarehouseZone.objects.filter(zone_type=zone_type).count()
    print(f"   • {zone_name}: {count} zones")

print(f"\n✅ Multi-Zone Warehouse Architecture Ready!")
