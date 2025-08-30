#!/usr/bin/env python3
"""
Simple script to add missing warehouse zones
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from warehouses.models import Warehouse, WarehouseZone

def add_missing_zones():
    print("Adding missing warehouse zones...")
    
    # Get existing warehouses
    warehouses = list(Warehouse.objects.all())
    if not warehouses:
        print("No warehouses found!")
        return
    
    print(f"Found {len(warehouses)} warehouses")
    
    zones_created = 0
    
    # Add organic zones
    for i, warehouse in enumerate(warehouses[:3]):
        zone, created = WarehouseZone.objects.get_or_create(
            warehouse=warehouse,
            zone_code=f'ORG-{i+1:02d}',
            defaults={
                'name': f'Organic Products Zone {i+1}',
                'zone_type': 'organic',
                'capacity_cubic_meters': Decimal('500.00'),
                'current_stock_level': Decimal('0.00'),
                'temperature_range': {'min': 2, 'max': 8},
                'humidity_range': {'min': 80, 'max': 95},
                'is_organic_certified': True,
            }
        )
        if created:
            zones_created += 1
            print(f"Created organic zone: {zone.name}")
        
        # Mark warehouse as organic certified
        warehouse.organic_certified = True
        warehouse.save()
    
    # Add processing zones
    for i, warehouse in enumerate(warehouses[:4]):
        # Processing zone
        zone, created = WarehouseZone.objects.get_or_create(
            warehouse=warehouse,
            zone_code=f'PROC-{i+1:02d}',
            defaults={
                'name': f'Processing Area {i+1}',
                'zone_type': 'processing',
                'capacity_cubic_meters': Decimal('300.00'),
                'current_stock_level': Decimal('0.00'),
                'temperature_range': {'min': 15, 'max': 25},
                'humidity_range': {'min': 45, 'max': 65},
            }
        )
        if created:
            zones_created += 1
            print(f"Created processing zone: {zone.name}")
        
        # Packaging zone
        zone, created = WarehouseZone.objects.get_or_create(
            warehouse=warehouse,
            zone_code=f'PKG-{i+1:02d}',
            defaults={
                'name': f'Packaging Area {i+1}',
                'zone_type': 'packaging',
                'capacity_cubic_meters': Decimal('200.00'),
                'current_stock_level': Decimal('0.00'),
                'temperature_range': {'min': 18, 'max': 24},
                'humidity_range': {'min': 40, 'max': 60},
            }
        )
        if created:
            zones_created += 1
            print(f"Created packaging zone: {zone.name}")
    
    # Add loading zones
    for i, warehouse in enumerate(warehouses):
        zone, created = WarehouseZone.objects.get_or_create(
            warehouse=warehouse,
            zone_code=f'LOAD-{i+1:02d}',
            defaults={
                'name': f'Loading/Unloading Bay {i+1}',
                'zone_type': 'loading',
                'capacity_cubic_meters': Decimal('150.00'),
                'current_stock_level': Decimal('0.00'),
                'temperature_range': {'min': -5, 'max': 35},
                'humidity_range': {'min': 30, 'max': 90},
            }
        )
        if created:
            zones_created += 1
            print(f"Created loading zone: {zone.name}")
            
            # Update warehouse to have loading dock
            warehouse.has_loading_dock = True
            warehouse.save()
    
    print(f"\nTotal zones created: {zones_created}")
    
    # Verify results
    print("\nCurrent zone counts:")
    print(f"Cold Storage: {WarehouseZone.objects.filter(zone_type='cold_storage').count()}")
    print(f"Organic: {WarehouseZone.objects.filter(zone_type='organic').count()}")
    print(f"Dry Storage: {WarehouseZone.objects.filter(zone_type='dry_storage').count()}")
    print(f"Processing: {WarehouseZone.objects.filter(zone_type='processing').count()}")
    print(f"Packaging: {WarehouseZone.objects.filter(zone_type='packaging').count()}")
    print(f"Quality Control: {WarehouseZone.objects.filter(zone_type='quality_control').count()}")
    print(f"Quarantine: {WarehouseZone.objects.filter(zone_type='quarantine').count()}")
    print(f"Loading: {WarehouseZone.objects.filter(zone_type='loading').count()}")

if __name__ == "__main__":
    add_missing_zones()
