#!/usr/bin/env python3
"""
AgriConnect Missing Warehouse Zones Implementation
Adds the missing multi-zone warehouse architecture components for PRD Section 4.1.1 compliance
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

django.setup()

from warehouses.models import Warehouse, WarehouseZone, WarehouseType

def create_missing_zones():
    """Create missing warehouse zones for PRD compliance"""
    
    print("🏗️  Creating Missing Multi-Zone Warehouse Architecture Components")
    print("="*80)
    
    # Get existing warehouses
    warehouses = Warehouse.objects.all()
    if not warehouses.exists():
        print("❌ No warehouses found! Please create warehouses first.")
        return
        
    print(f"📋 Found {warehouses.count()} warehouses to enhance")
    
    zones_created = 0
    
    for warehouse in warehouses:
        print(f"\n🏢 Processing: {warehouse.name} ({warehouse.code})")
        
        # 1. Add Organic Zones (if warehouse supports organic)
        if not warehouse.zones.filter(zone_type='organic').exists():
            organic_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"ORG-{len(warehouse.zones.all()) + 1:02d}",
                name=f"Organic Products Zone",
                zone_type='organic',
                capacity_cubic_meters=Decimal('500.00'),
                current_stock_level=Decimal('0.00'),
                temperature_range={'min': 10, 'max': 20},
                humidity_range={'min': 40, 'max': 60},
                special_conditions={
                    'organic_certified': True,
                    'segregation_required': True,
                    'certification_bodies': ['IFOAM', 'USDA Organic']
                },
                requires_certification=True,
                access_restrictions=['organic_handler_certification']
            )
            print(f"  ✅ Created Organic Zone: {organic_zone.zone_code}")
            zones_created += 1
        
        # 2. Add Processing Areas
        if not warehouse.zones.filter(zone_type='processing').exists():
            processing_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"PROC-{len(warehouse.zones.all()) + 1:02d}",
                name=f"Processing Area",
                zone_type='processing',
                capacity_cubic_meters=Decimal('300.00'),
                current_stock_level=Decimal('0.00'),
                temperature_range={'min': 15, 'max': 25},
                humidity_range={'min': 30, 'max': 70},
                special_conditions={
                    'processing_equipment': True,
                    'value_addition': True,
                    'clean_room_standards': True
                },
                requires_certification=True,
                access_restrictions=['food_handler_certification']
            )
            print(f"  ✅ Created Processing Zone: {processing_zone.zone_code}")
            zones_created += 1
        
        # 3. Add Packaging Areas
        if not warehouse.zones.filter(zone_type='packaging').exists():
            packaging_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"PKG-{len(warehouse.zones.all()) + 1:02d}",
                name=f"Packaging Facility",
                zone_type='packaging',
                capacity_cubic_meters=Decimal('200.00'),
                current_stock_level=Decimal('0.00'),
                temperature_range={'min': 18, 'max': 24},
                humidity_range={'min': 35, 'max': 65},
                special_conditions={
                    'packaging_equipment': True,
                    'labeling_station': True,
                    'quality_sealing': True
                },
                requires_certification=False,
                access_restrictions=['packaging_training']
            )
            print(f"  ✅ Created Packaging Zone: {packaging_zone.zone_code}")
            zones_created += 1
        
        # 4. Add Loading/Unloading Bays
        if not warehouse.zones.filter(zone_type='loading').exists():
            loading_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"LOAD-{len(warehouse.zones.all()) + 1:02d}",
                name=f"Loading/Unloading Bay",
                zone_type='loading',
                capacity_cubic_meters=Decimal('150.00'),
                current_stock_level=Decimal('0.00'),
                temperature_range={'min': 0, 'max': 35},
                humidity_range={'min': 20, 'max': 80},
                special_conditions={
                    'truck_access': True,
                    'dock_doors': 4,
                    'container_handling': True,
                    'weighing_station': True
                },
                requires_certification=False,
                access_restrictions=['forklift_certification']
            )
            print(f"  ✅ Created Loading Bay: {loading_zone.zone_code}")
            zones_created += 1
            
            # Update warehouse to indicate it has loading dock
            if not warehouse.has_loading_dock:
                warehouse.has_loading_dock = True
                warehouse.save()
                print(f"  ✅ Updated warehouse loading dock status")
        
        # 5. Add Quarantine Zones (for quality control)
        if not warehouse.zones.filter(zone_type='quarantine').exists():
            quarantine_zone = WarehouseZone.objects.create(
                warehouse=warehouse,
                zone_code=f"QUAR-{len(warehouse.zones.all()) + 1:02d}",
                name=f"Quarantine Zone",
                zone_type='quarantine',
                capacity_cubic_meters=Decimal('100.00'),
                current_stock_level=Decimal('0.00'),
                temperature_range={'min': 5, 'max': 25},
                humidity_range={'min': 40, 'max': 70},
                special_conditions={
                    'isolated_storage': True,
                    'inspection_required': True,
                    'restricted_access': True
                },
                requires_certification=True,
                access_restrictions=['quality_inspector_only']
            )
            print(f"  ✅ Created Quarantine Zone: {quarantine_zone.zone_code}")
            zones_created += 1
    
    print(f"\n🎉 Created {zones_created} new warehouse zones!")
    
    # Create missing warehouse types if needed
    print(f"\n🏭 Checking Warehouse Types...")
    
    required_types = [
        ('organic_only', 'Organic Only Warehouse'),
        ('processing', 'Processing Facility')
    ]
    
    for type_code, type_name in required_types:
        warehouse_type, created = WarehouseType.objects.get_or_create(
            warehouse_type=type_code,
            defaults={
                'name': type_name,
                'description': f'Specialized {type_name.lower()} for agricultural products',
                'special_requirements': {
                    'certification_required': type_code == 'organic_only',
                    'specialized_equipment': type_code == 'processing'
                }
            }
        )
        if created:
            print(f"  ✅ Created WarehouseType: {type_name}")
    
    print(f"\n📊 Final Status Summary:")
    print(f"  🏢 Total Warehouses: {Warehouse.objects.count()}")
    print(f"  🏗️  Total Zones: {WarehouseZone.objects.count()}")
    print(f"  📦 Zone Types Distribution:")
    
    for zone_type, zone_name in WarehouseZone.ZONE_TYPE_CHOICES:
        count = WarehouseZone.objects.filter(zone_type=zone_type).count()
        print(f"    • {zone_name}: {count} zones")
    
    print(f"\n✅ Multi-Zone Warehouse Architecture Implementation Complete!")

if __name__ == "__main__":
    try:
        create_missing_zones()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
