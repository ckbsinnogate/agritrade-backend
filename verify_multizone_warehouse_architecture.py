#!/usr/bin/env python3
"""
AgriConnect Multi-Zone Warehouse Architecture Verification
This script verifies that all PRD Section 4.1.1 Multi-Zone Warehouse Architecture requirements are implemented
"""

import os
import sys
import django

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

django.setup()

from warehouses.models import WarehouseType, Warehouse, WarehouseZone, WarehouseInventory, WarehouseStaff

def print_section(title, color="36"):  # Cyan
    print(f"\n\033[{color}m{'='*80}\033[0m")
    print(f"\033[{color}m{title.center(80)}\033[0m")
    print(f"\033[{color}m{'='*80}\033[0m")

def print_requirement(req_num, title, status="", color="32"):
    status_icon = "✅" if status == "IMPLEMENTED" else "❌" if status == "MISSING" else "🔍"
    print(f"\n\033[{color}m{req_num}. {title} {status_icon}\033[0m")

def verify_cold_storage_zones():
    """Verify Cold Storage Zones implementation"""
    print_requirement("4.1.1.1", "Cold Storage Zones: Temperature-controlled areas for perishables")
    
    # Check for cold storage warehouse types
    cold_storage_types = WarehouseType.objects.filter(warehouse_type='cold_storage')
    print(f"   📊 Cold Storage Warehouse Types: {cold_storage_types.count()}")
    
    # Check for cold storage warehouses
    cold_storage_warehouses = Warehouse.objects.filter(warehouse_type__warehouse_type='cold_storage')
    print(f"   🏢 Cold Storage Warehouses: {cold_storage_warehouses.count()}")
    
    # Check for cold storage zones
    cold_storage_zones = WarehouseZone.objects.filter(zone_type='cold_storage')
    print(f"   ❄️  Cold Storage Zones: {cold_storage_zones.count()}")
    
    # Display details
    for warehouse in cold_storage_warehouses:
        print(f"      • {warehouse.name} ({warehouse.code})")
        zones = warehouse.zones.filter(zone_type='cold_storage')
        for zone in zones:
            temp_range = zone.temperature_range
            print(f"        └─ {zone.name} ({zone.zone_code}) - Temp: {temp_range.get('min', 'N/A')}°C to {temp_range.get('max', 'N/A')}°C")
    
    is_implemented = cold_storage_types.count() > 0 and cold_storage_warehouses.count() > 0 and cold_storage_zones.count() > 0
    return is_implemented

def verify_organic_separation():
    """Verify Organic Separation implementation"""
    print_requirement("4.1.1.2", "Organic Separation: Dedicated zones for certified organic products")
    
    # Check for organic warehouse types
    organic_types = WarehouseType.objects.filter(warehouse_type='organic')
    print(f"   📊 Organic Warehouse Types: {organic_types.count()}")
    
    # Check for organic certified warehouses
    organic_warehouses = Warehouse.objects.filter(organic_certified=True)
    print(f"   🌱 Organic Certified Warehouses: {organic_warehouses.count()}")
    
    # Check for organic zones
    organic_zones = WarehouseZone.objects.filter(zone_type='organic')
    print(f"   🌿 Organic-Only Zones: {organic_zones.count()}")
    
    # Display details
    for warehouse in organic_warehouses:
        print(f"      • {warehouse.name} ({warehouse.code}) - Organic Certified: {warehouse.organic_certified}")
        zones = warehouse.zones.filter(zone_type='organic')
        for zone in zones:
            print(f"        └─ {zone.name} ({zone.zone_code}) - Type: {zone.get_zone_type_display()}")
    
    is_implemented = organic_types.count() > 0 and organic_warehouses.count() > 0 and organic_zones.count() > 0
    return is_implemented

def verify_dry_storage():
    """Verify Dry Storage implementation"""
    print_requirement("4.1.1.3", "Dry Storage: Grains, legumes, and non-perishable items")
    
    # Check for dry storage warehouse types
    dry_storage_types = WarehouseType.objects.filter(warehouse_type='dry_storage')
    print(f"   📊 Dry Storage Warehouse Types: {dry_storage_types.count()}")
    
    # Check for dry storage warehouses
    dry_storage_warehouses = Warehouse.objects.filter(warehouse_type__warehouse_type='dry_storage')
    print(f"   🌾 Dry Storage Warehouses: {dry_storage_warehouses.count()}")
    
    # Check for dry storage zones
    dry_storage_zones = WarehouseZone.objects.filter(zone_type='dry_storage')
    print(f"   📦 Dry Storage Zones: {dry_storage_zones.count()}")
    
    # Display details
    for warehouse in dry_storage_warehouses:
        print(f"      • {warehouse.name} ({warehouse.code})")
        zones = warehouse.zones.filter(zone_type='dry_storage')
        for zone in zones:
            print(f"        └─ {zone.name} ({zone.zone_code}) - Capacity: {zone.capacity_cubic_meters}m³")
    
    is_implemented = dry_storage_types.count() > 0 and dry_storage_warehouses.count() > 0 and dry_storage_zones.count() > 0
    return is_implemented

def verify_processing_areas():
    """Verify Processing Areas implementation"""
    print_requirement("4.1.1.4", "Processing Areas: Value-addition and packaging facilities")
    
    # Check for processing warehouse types
    processing_types = WarehouseType.objects.filter(warehouse_type='processing')
    print(f"   📊 Processing Warehouse Types: {processing_types.count()}")
    
    # Check for processing warehouses
    processing_warehouses = Warehouse.objects.filter(warehouse_type__warehouse_type='processing')
    print(f"   🏭 Processing Warehouses: {processing_warehouses.count()}")
    
    # Check for processing zones
    processing_zones = WarehouseZone.objects.filter(zone_type='processing')
    print(f"   ⚙️  Processing Zones: {processing_zones.count()}")
    
    # Check for packaging zones
    packaging_zones = WarehouseZone.objects.filter(zone_type='packaging')
    print(f"   📦 Packaging Zones: {packaging_zones.count()}")
    
    # Display details
    for warehouse in processing_warehouses:
        print(f"      • {warehouse.name} ({warehouse.code})")
        processing_zone_list = warehouse.zones.filter(zone_type='processing')
        packaging_zone_list = warehouse.zones.filter(zone_type='packaging')
        for zone in processing_zone_list:
            print(f"        └─ {zone.name} ({zone.zone_code}) - Processing Area")
        for zone in packaging_zone_list:
            print(f"        └─ {zone.name} ({zone.zone_code}) - Packaging Area")
    
    is_implemented = processing_types.count() > 0 and processing_warehouses.count() > 0 and (processing_zones.count() > 0 or packaging_zones.count() > 0)
    return is_implemented

def verify_quality_control_zones():
    """Verify Quality Control Zones implementation"""
    print_requirement("4.1.1.5", "Quality Control Zones: Inspection and certification areas")
    
    # Check for quality control zones
    quality_control_zones = WarehouseZone.objects.filter(zone_type='quality_control')
    print(f"   🔬 Quality Control Zones: {quality_control_zones.count()}")
    
    # Check for quarantine zones (also quality control related)
    quarantine_zones = WarehouseZone.objects.filter(zone_type='quarantine')
    print(f"   🚫 Quarantine Zones: {quarantine_zones.count()}")
    
    # Display details by warehouse
    warehouses_with_qc = Warehouse.objects.filter(
        zones__zone_type__in=['quality_control', 'quarantine']
    ).distinct()
    
    for warehouse in warehouses_with_qc:
        print(f"      • {warehouse.name} ({warehouse.code})")
        qc_zones = warehouse.zones.filter(zone_type='quality_control')
        quarantine_zone_list = warehouse.zones.filter(zone_type='quarantine')
        for zone in qc_zones:
            print(f"        └─ {zone.name} ({zone.zone_code}) - Quality Control")
        for zone in quarantine_zone_list:
            print(f"        └─ {zone.name} ({zone.zone_code}) - Quarantine")
    
    is_implemented = quality_control_zones.count() > 0 or quarantine_zones.count() > 0
    return is_implemented

def verify_loading_unloading_bays():
    """Verify Loading/Unloading Bays implementation"""
    print_requirement("4.1.1.6", "Loading/Unloading Bays: Truck and container management")
    
    # Check for loading/unloading zones
    loading_zones = WarehouseZone.objects.filter(zone_type='loading')
    print(f"   🚛 Loading/Unloading Zones: {loading_zones.count()}")
    
    # Check for warehouses with loading docks
    warehouses_with_docks = Warehouse.objects.filter(has_loading_dock=True)
    print(f"   🏢 Warehouses with Loading Docks: {warehouses_with_docks.count()}")
    
    # Display details
    for warehouse in warehouses_with_docks:
        print(f"      • {warehouse.name} ({warehouse.code}) - Has Loading Dock: {warehouse.has_loading_dock}")
        loading_zone_list = warehouse.zones.filter(zone_type='loading')
        for zone in loading_zone_list:
            print(f"        └─ {zone.name} ({zone.zone_code}) - Loading/Unloading Bay")
    
    is_implemented = loading_zones.count() > 0 or warehouses_with_docks.count() > 0
    return is_implemented

def main():
    """Main verification function"""
    print_section("AGRICONNECT MULTI-ZONE WAREHOUSE ARCHITECTURE VERIFICATION", "33")
    print("\033[33mPRD Section 4.1.1 Requirements Verification\033[0m")
    
    # Track implementation status
    results = {}
    
    print_section("REQUIREMENT VERIFICATION", "36")
    
    # Verify each requirement
    results["cold_storage"] = verify_cold_storage_zones()
    results["organic_separation"] = verify_organic_separation()
    results["dry_storage"] = verify_dry_storage()
    results["processing_areas"] = verify_processing_areas()
    results["quality_control"] = verify_quality_control_zones()
    results["loading_bays"] = verify_loading_unloading_bays()
    
    # Summary
    print_section("IMPLEMENTATION SUMMARY", "32")
    
    implemented_count = sum(1 for status in results.values() if status)
    total_count = len(results)
    
    print(f"\n📊 \033[32mImplementation Status: {implemented_count}/{total_count} Requirements Met\033[0m")
    
    for requirement, status in results.items():
        status_text = "✅ IMPLEMENTED" if status else "❌ MISSING"
        color = "32" if status else "31"
        print(f"   \033[{color}m{requirement.upper().replace('_', ' ')}: {status_text}\033[0m")
    
    # Overall status
    if implemented_count == total_count:
        print(f"\n🎉 \033[32mALL MULTI-ZONE WAREHOUSE ARCHITECTURE REQUIREMENTS IMPLEMENTED!\033[0m")
    else:
        print(f"\n⚠️  \033[33m{total_count - implemented_count} REQUIREMENTS NEED ATTENTION\033[0m")
    
    # Database statistics
    print_section("DATABASE STATISTICS", "34")
    print(f"📊 Total Warehouse Types: {WarehouseType.objects.count()}")
    print(f"🏢 Total Warehouses: {Warehouse.objects.count()}")
    print(f"🏗️  Total Warehouse Zones: {WarehouseZone.objects.count()}")
    print(f"📦 Total Inventory Items: {WarehouseInventory.objects.count()}")
    print(f"👥 Total Warehouse Staff: {WarehouseStaff.objects.count()}")
    
    # Zone type distribution
    print(f"\n🏗️  Zone Type Distribution:")
    zone_types = WarehouseZone.objects.values_list('zone_type', flat=True)
    for zone_type in WarehouseZone.ZONE_TYPE_CHOICES:
        count = zone_types.filter(zone_type=zone_type[0]).count() if hasattr(zone_types, 'filter') else sum(1 for zt in zone_types if zt == zone_type[0])
        print(f"   • {zone_type[1]}: {count} zones")

if __name__ == "__main__":
    main()
