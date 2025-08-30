#!/usr/bin/env python3
"""
Quick Multi-Zone Warehouse Architecture Verification
Checks PRD Section 4.1.1 requirements implementation
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from warehouses.models import WarehouseType, Warehouse, WarehouseZone

def main():
    print("🌾 AgriConnect Multi-Zone Warehouse Architecture Check")
    print("=" * 60)
    
    # Check zone types available
    print("\n📊 Zone Type Analysis:")
    
    zone_choices = dict(WarehouseZone.ZONE_TYPE_CHOICES)
    print(f"Available zone types: {len(zone_choices)}")
    
    for zone_code, zone_name in zone_choices.items():
        count = WarehouseZone.objects.filter(zone_type=zone_code).count()
        print(f"  • {zone_name}: {count} zones")
    
    # Check warehouse types
    print("\n🏢 Warehouse Type Analysis:")
    
    warehouse_type_choices = dict(WarehouseType.WAREHOUSE_TYPE_CHOICES)
    print(f"Available warehouse types: {len(warehouse_type_choices)}")
    
    for wh_code, wh_name in warehouse_type_choices.items():
        count = WarehouseType.objects.filter(warehouse_type=wh_code).count()
        warehouses = Warehouse.objects.filter(warehouse_type__warehouse_type=wh_code).count()
        print(f"  • {wh_name}: {count} types, {warehouses} warehouses")
    
    # Check specific PRD 4.1.1 requirements
    print("\n✅ PRD Section 4.1.1 Requirements Check:")
    
    requirements = {
        "Cold Storage Zones": WarehouseZone.objects.filter(zone_type='cold_storage').count(),
        "Organic Separation": WarehouseZone.objects.filter(zone_type='organic').count(), 
        "Dry Storage": WarehouseZone.objects.filter(zone_type='dry_storage').count(),
        "Processing Areas": WarehouseZone.objects.filter(zone_type='processing').count(),
        "Quality Control": WarehouseZone.objects.filter(zone_type='quality_control').count(),
        "Loading/Unloading": WarehouseZone.objects.filter(zone_type='loading').count(),
    }
    
    implemented = 0
    total = len(requirements)
    
    for requirement, count in requirements.items():
        status = "✅ IMPLEMENTED" if count > 0 else "❌ MISSING"
        print(f"  {requirement}: {count} zones {status}")
        if count > 0:
            implemented += 1
    
    print(f"\n📈 Implementation Status: {implemented}/{total} requirements met")
    
    if implemented == total:
        print("🎉 ALL MULTI-ZONE WAREHOUSE ARCHITECTURE REQUIREMENTS IMPLEMENTED!")
    else:
        print(f"⚠️  {total - implemented} requirements need implementation")
    
    # Show sample warehouse details
    print("\n🏪 Sample Warehouse Details:")
    for warehouse in Warehouse.objects.all()[:2]:
        print(f"\n  📍 {warehouse.name} ({warehouse.code})")
        print(f"     Type: {warehouse.warehouse_type.get_warehouse_type_display()}")
        print(f"     Location: {warehouse.address}")
        print(f"     Organic Certified: {warehouse.organic_certified}")
        print(f"     Loading Dock: {warehouse.has_loading_dock}")
        
        zones = warehouse.zones.all()
        print(f"     Zones ({zones.count()}):")
        for zone in zones:
            print(f"       └─ {zone.name} ({zone.get_zone_type_display()})")

if __name__ == "__main__":
    main()
