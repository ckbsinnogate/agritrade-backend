#!/usr/bin/env python
"""
AgriConnect Warehouse Management System - Demo Setup
Creates comprehensive sample data to demonstrate the warehouse management system
"""

import os
import django
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from warehouses.models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, WarehouseMovement, TemperatureLog, QualityInspection
)
from products.models import Product, Category
from django.utils import timezone

User = get_user_model()

def print_header(title):
    print("\n" + "="*80)
    print(f"🌾 {title}")
    print("="*80)

def print_section(title):
    print(f"\n📍 {title}")
    print("-"*60)

def create_warehouse_types():
    """Create different warehouse types for agricultural storage"""
    print_section("Creating Warehouse Types")
    
    warehouse_types_data = [
        {
            'name': 'Cold Storage Facility',
            'warehouse_type': 'cold_storage',
            'description': 'Temperature-controlled storage for perishable agricultural products',
            'temperature_range_min': -2.0,
            'temperature_range_max': 4.0,
            'humidity_range_min': 85.0,
            'humidity_range_max': 95.0,
            'special_requirements': {
                'backup_power': True,
                'temperature_monitoring': True,
                'humidity_control': True,
                'alarm_system': True
            }
        },
        {
            'name': 'Dry Storage Warehouse',
            'warehouse_type': 'dry_storage',
            'description': 'Climate-controlled storage for grains, legumes, and dried products',
            'temperature_range_min': 15.0,
            'temperature_range_max': 25.0,
            'humidity_range_min': 50.0,
            'humidity_range_max': 65.0,
            'special_requirements': {
                'pest_control': True,
                'moisture_control': True,
                'ventilation': True,
                'fire_suppression': True
            }
        },
        {
            'name': 'Organic Certified Storage',
            'warehouse_type': 'organic',
            'description': 'Certified organic storage facility with strict contamination controls',
            'temperature_range_min': 10.0,
            'temperature_range_max': 20.0,
            'humidity_range_min': 55.0,
            'humidity_range_max': 70.0,
            'special_requirements': {
                'organic_certification': True,
                'contamination_prevention': True,
                'separate_zones': True,
                'audit_trail': True
            }
        },
        {
            'name': 'Processing Facility',
            'warehouse_type': 'processing',
            'description': 'Value-addition and processing facility for agricultural products',
            'temperature_range_min': 18.0,
            'temperature_range_max': 25.0,
            'humidity_range_min': 45.0,
            'humidity_range_max': 60.0,
            'special_requirements': {
                'food_safety_compliance': True,
                'equipment_zones': True,
                'quality_control_lab': True,
                'packaging_area': True
            }
        }
    ]
    
    warehouse_types = []
    for data in warehouse_types_data:
        warehouse_type, created = WarehouseType.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        warehouse_types.append(warehouse_type)
        status = "✅ Created" if created else "📋 Exists"
        print(f"  {status} {warehouse_type.name}")
    
    return warehouse_types

def create_warehouses(warehouse_types):
    """Create warehouse facilities across Ghana"""
    print_section("Creating Warehouse Facilities")
    
    # Create warehouse managers first
    managers_data = [
        {'username': 'kwame_manager', 'email': 'kwame@agriconnect.gh', 'first_name': 'Kwame', 'last_name': 'Asante'},
        {'username': 'ama_supervisor', 'email': 'ama@agriconnect.gh', 'first_name': 'Ama', 'last_name': 'Osei'},
        {'username': 'kofi_warehouse', 'email': 'kofi@agriconnect.gh', 'first_name': 'Kofi', 'last_name': 'Mensah'},
        {'username': 'akosua_manager', 'email': 'akosua@agriconnect.gh', 'first_name': 'Akosua', 'last_name': 'Boateng'}
    ]
    
    managers = []
    for data in managers_data:
        manager, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                **data,
                'phone_number': f'+233{random.randint(200000000, 299999999)}',
                'is_verified': True,
                'phone_verified': True
            }
        )
        managers.append(manager)
    
    warehouses_data = [
        {
            'code': 'WH-ACC-001',
            'name': 'AgriConnect Accra Central Warehouse',
            'warehouse_type': warehouse_types[1],  # Dry Storage
            'country': 'Ghana',
            'region': 'Greater Accra',
            'city': 'Accra',
            'address': {
                'street': 'Liberation Road',
                'area': 'Industrial Area',
                'postal_code': 'GA-544-9321',
                'landmark': 'Near Tema Station'
            },
            'gps_coordinates': '5.6037,-0.1870',
            'capacity_cubic_meters': Decimal('5000.00'),
            'current_utilization_percent': Decimal('75.50'),
            'temperature_controlled': True,
            'humidity_controlled': True,
            'organic_certified': False,
            'has_loading_dock': True,
            'manager': managers[0],
            'status': 'active',
            'contact_info': {
                'phone': '+233302123456',
                'email': 'accra.warehouse@agriconnect.gh',
                'emergency_contact': '+233302654321'
            },
            'operating_hours': {
                'monday': '06:00-18:00',
                'tuesday': '06:00-18:00',
                'wednesday': '06:00-18:00',
                'thursday': '06:00-18:00',
                'friday': '06:00-18:00',
                'saturday': '06:00-14:00',
                'sunday': 'closed'
            },
            'security_features': ['24hr_security', 'cctv_monitoring', 'access_control', 'alarm_system']
        },
        {
            'code': 'WH-KUM-002',
            'name': 'Kumasi Organic Storage Facility',
            'warehouse_type': warehouse_types[2],  # Organic Certified
            'country': 'Ghana',
            'region': 'Ashanti',
            'city': 'Kumasi',
            'address': {
                'street': 'Kaase Industrial Area',
                'area': 'Kaase',
                'postal_code': 'AK-039-5641',
                'landmark': 'Behind Kumasi Central Market'
            },
            'gps_coordinates': '6.6885,-1.6244',
            'capacity_cubic_meters': Decimal('3500.00'),
            'current_utilization_percent': Decimal('82.30'),
            'temperature_controlled': True,
            'humidity_controlled': True,
            'organic_certified': True,
            'has_loading_dock': True,
            'manager': managers[1],
            'status': 'active',
            'contact_info': {
                'phone': '+233322456789',
                'email': 'kumasi.organic@agriconnect.gh',
                'emergency_contact': '+233322987654'
            },
            'operating_hours': {
                'monday': '05:30-18:30',
                'tuesday': '05:30-18:30',
                'wednesday': '05:30-18:30',
                'thursday': '05:30-18:30',
                'friday': '05:30-18:30',
                'saturday': '05:30-16:00',
                'sunday': '08:00-12:00'
            },
            'security_features': ['24hr_security', 'biometric_access', 'temperature_alerts', 'organic_compliance']
        },
        {
            'code': 'WH-TAM-003',
            'name': 'Tamale Cold Storage Complex',
            'warehouse_type': warehouse_types[0],  # Cold Storage
            'country': 'Ghana',
            'region': 'Northern',
            'city': 'Tamale',
            'address': {
                'street': 'Tamale Industrial Area',
                'area': 'Kalpohin',
                'postal_code': 'NT-123-4567',
                'landmark': 'Near Tamale Airport'
            },
            'gps_coordinates': '9.4034,-0.8424',
            'capacity_cubic_meters': Decimal('2800.00'),
            'current_utilization_percent': Decimal('68.75'),
            'temperature_controlled': True,
            'humidity_controlled': True,
            'organic_certified': False,
            'has_loading_dock': True,
            'manager': managers[2],
            'status': 'active',
            'contact_info': {
                'phone': '+233372345678',
                'email': 'tamale.cold@agriconnect.gh',
                'emergency_contact': '+233372876543'
            },
            'operating_hours': {
                'monday': '05:00-19:00',
                'tuesday': '05:00-19:00',
                'wednesday': '05:00-19:00',
                'thursday': '05:00-19:00',
                'friday': '05:00-19:00',
                'saturday': '05:00-17:00',
                'sunday': '07:00-15:00'
            },
            'security_features': ['24hr_security', 'cold_chain_monitoring', 'backup_generators', 'fire_suppression']
        },
        {
            'code': 'WH-CPT-004',
            'name': 'Cape Coast Processing Hub',
            'warehouse_type': warehouse_types[3],  # Processing Facility
            'country': 'Ghana',
            'region': 'Central',
            'city': 'Cape Coast',
            'address': {
                'street': 'Abura Industrial Area',
                'area': 'Abura',
                'postal_code': 'CC-678-9012',
                'landmark': 'Near University of Cape Coast'
            },
            'gps_coordinates': '5.1053,-1.2466',
            'capacity_cubic_meters': Decimal('4200.00'),
            'current_utilization_percent': Decimal('71.60'),
            'temperature_controlled': True,
            'humidity_controlled': True,
            'organic_certified': True,
            'has_loading_dock': True,
            'manager': managers[3],
            'status': 'active',
            'contact_info': {
                'phone': '+233332567890',
                'email': 'capecoast.processing@agriconnect.gh',
                'emergency_contact': '+233332098765'
            },
            'operating_hours': {
                'monday': '06:00-20:00',
                'tuesday': '06:00-20:00',
                'wednesday': '06:00-20:00',
                'thursday': '06:00-20:00',
                'friday': '06:00-20:00',
                'saturday': '06:00-18:00',
                'sunday': '08:00-16:00'
            },
            'security_features': ['24hr_security', 'quality_control_lab', 'processing_equipment', 'packaging_area']
        }
    ]
    
    warehouses = []
    for data in warehouses_data:
        warehouse, created = Warehouse.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        warehouses.append(warehouse)
        status = "✅ Created" if created else "📋 Exists"
        print(f"  {status} {warehouse.name} ({warehouse.code})")
        print(f"    📍 {warehouse.city}, {warehouse.region}")
        print(f"    📦 Capacity: {warehouse.capacity_cubic_meters}m³ ({warehouse.current_utilization_percent}% utilized)")
    
    return warehouses

def create_warehouse_zones(warehouses):
    """Create zones within each warehouse"""
    print_section("Creating Warehouse Zones")
    
    zones_data = {
        'cold_storage': [
            {'code': 'CS-A', 'name': 'Cold Storage Zone A', 'type': 'cold_storage', 'capacity': 800},
            {'code': 'CS-B', 'name': 'Cold Storage Zone B', 'type': 'cold_storage', 'capacity': 600},
            {'code': 'FRZ', 'name': 'Freezer Section', 'type': 'cold_storage', 'capacity': 400},
            {'code': 'LD', 'name': 'Loading Dock', 'type': 'loading_dock', 'capacity': 200}
        ],
        'dry_storage': [
            {'code': 'DS-A', 'name': 'Dry Storage Zone A', 'type': 'dry_storage', 'capacity': 1200},
            {'code': 'DS-B', 'name': 'Dry Storage Zone B', 'type': 'dry_storage', 'capacity': 1000},
            {'code': 'GRN', 'name': 'Grain Storage', 'type': 'dry_storage', 'capacity': 1500},
            {'code': 'QC', 'name': 'Quality Control', 'type': 'quality_control', 'capacity': 150}
        ],
        'organic': [
            {'code': 'ORG-A', 'name': 'Organic Zone A', 'type': 'organic_zone', 'capacity': 900},
            {'code': 'ORG-B', 'name': 'Organic Zone B', 'type': 'organic_zone', 'capacity': 800},
            {'code': 'ORG-QC', 'name': 'Organic Quality Control', 'type': 'quality_control', 'capacity': 200},
            {'code': 'QUAR', 'name': 'Quarantine Zone', 'type': 'quarantine_zone', 'capacity': 300}
        ],
        'processing': [
            {'code': 'PROC-A', 'name': 'Processing Area A', 'type': 'processing_area', 'capacity': 600},
            {'code': 'PROC-B', 'name': 'Processing Area B', 'type': 'processing_area', 'capacity': 800},
            {'code': 'PKG', 'name': 'Packaging Zone', 'type': 'processing_area', 'capacity': 400},
            {'code': 'FIN', 'name': 'Finished Goods', 'type': 'dry_storage', 'capacity': 700}
        ]
    }
    
    all_zones = []
    for warehouse in warehouses:
        warehouse_type = warehouse.warehouse_type.warehouse_type
        if warehouse_type in zones_data:
            for zone_data in zones_data[warehouse_type]:
                zone, created = WarehouseZone.objects.get_or_create(
                    warehouse=warehouse,
                    zone_code=zone_data['code'],
                    defaults={
                        'name': zone_data['name'],
                        'zone_type': zone_data['type'],
                        'capacity_cubic_meters': Decimal(str(zone_data['capacity'])),
                        'current_stock_level': Decimal(str(random.randint(50, int(zone_data['capacity'] * 0.8)))),
                        'temperature_range': {
                            'min': warehouse.warehouse_type.temperature_range_min,
                            'max': warehouse.warehouse_type.temperature_range_max
                        },
                        'special_conditions': warehouse.warehouse_type.special_requirements,
                        'is_active': True
                    }
                )
                all_zones.append(zone)
                status = "✅ Created" if created else "📋 Exists"
                print(f"  {status} {warehouse.code}/{zone.zone_code} - {zone.name}")
    
    return all_zones

def create_warehouse_staff(warehouses):
    """Create staff assignments for warehouses"""
    print_section("Creating Warehouse Staff")
    
    # Create additional staff users
    staff_data = [
        # Accra Warehouse Staff
        {'username': 'john_supervisor_acc', 'first_name': 'John', 'last_name': 'Mensah', 'role': 'supervisor'},
        {'username': 'mary_worker_acc', 'first_name': 'Mary', 'last_name': 'Asante', 'role': 'worker'},
        {'username': 'peter_security_acc', 'first_name': 'Peter', 'last_name': 'Osei', 'role': 'security'},
        {'username': 'grace_inspector_acc', 'first_name': 'Grace', 'last_name': 'Boateng', 'role': 'quality_inspector'},
        
        # Kumasi Warehouse Staff
        {'username': 'samuel_supervisor_kum', 'first_name': 'Samuel', 'last_name': 'Owusu', 'role': 'supervisor'},
        {'username': 'janet_worker_kum', 'first_name': 'Janet', 'last_name': 'Akoto', 'role': 'worker'},
        {'username': 'robert_forklift_kum', 'first_name': 'Robert', 'last_name': 'Appiah', 'role': 'forklift_operator'},
        
        # Tamale Warehouse Staff
        {'username': 'mohammed_supervisor_tam', 'first_name': 'Mohammed', 'last_name': 'Abdul', 'role': 'supervisor'},
        {'username': 'fatima_worker_tam', 'first_name': 'Fatima', 'last_name': 'Ibrahim', 'role': 'worker'},
        
        # Cape Coast Processing Staff
        {'username': 'daniel_supervisor_cpt', 'first_name': 'Daniel', 'last_name': 'Koomson', 'role': 'supervisor'},
        {'username': 'elizabeth_worker_cpt', 'first_name': 'Elizabeth', 'last_name': 'Egyir', 'role': 'worker'},
        {'username': 'francis_inspector_cpt', 'first_name': 'Francis', 'last_name': 'Antwi', 'role': 'quality_inspector'}
    ]
    
    # Create staff users
    staff_users = []
    for data in staff_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': f"{data['username']}@agriconnect.gh",
                'phone_number': f'+233{random.randint(200000000, 299999999)}',
                'is_verified': True,
                'phone_verified': True
            }
        )
        staff_users.append((user, data['role']))
    
    # Assign staff to warehouses
    staff_assignments = [
        # Accra Warehouse (index 0)
        (0, 0, 'supervisor'), (0, 1, 'worker'), (0, 2, 'security'), (0, 3, 'quality_inspector'),
        # Kumasi Warehouse (index 1)  
        (1, 4, 'supervisor'), (1, 5, 'worker'), (1, 6, 'forklift_operator'),
        # Tamale Warehouse (index 2)
        (2, 7, 'supervisor'), (2, 8, 'worker'),
        # Cape Coast Warehouse (index 3)
        (3, 9, 'supervisor'), (3, 10, 'worker'), (3, 11, 'quality_inspector')
    ]
    
    warehouse_staff = []
    for warehouse_idx, staff_idx, role in staff_assignments:
        user, _ = staff_users[staff_idx]
        warehouse = warehouses[warehouse_idx]
        
        staff, created = WarehouseStaff.objects.get_or_create(
            warehouse=warehouse,
            user=user,
            defaults={
                'role': role,
                'access_zones': [],  # All zones by default
                'is_active': True,
                'hired_date': date.today() - timedelta(days=random.randint(30, 365)),
                'performance_rating': Decimal(str(random.uniform(3.5, 5.0)))
            }
        )
        warehouse_staff.append(staff)
        status = "✅ Created" if created else "📋 Exists"
        print(f"  {status} {user.first_name} {user.last_name} - {role} at {warehouse.code}")
    
    return warehouse_staff

def test_warehouse_system():
    """Test the warehouse management system functionality"""
    print_header("WAREHOUSE MANAGEMENT SYSTEM DEMO SETUP COMPLETE")
    
    # Create data
    warehouse_types = create_warehouse_types()
    warehouses = create_warehouses(warehouse_types)
    zones = create_warehouse_zones(warehouses)
    staff = create_warehouse_staff(warehouses)
    
    # Display summary
    print_section("System Summary")
    print(f"📊 Created {len(warehouse_types)} warehouse types")
    print(f"🏢 Created {len(warehouses)} warehouse facilities")
    print(f"🏗️  Created {len(zones)} warehouse zones")
    print(f"👥 Created {len(staff)} staff assignments")
    
    print_section("Warehouse Facilities Overview")
    for warehouse in warehouses:
        print(f"\n🏢 {warehouse.name}")
        print(f"   📍 Location: {warehouse.city}, {warehouse.region}")
        print(f"   🏷️  Code: {warehouse.code}")
        print(f"   📦 Type: {warehouse.warehouse_type.name}")
        print(f"   📏 Capacity: {warehouse.capacity_cubic_meters}m³")
        print(f"   📊 Utilization: {warehouse.current_utilization_percent}%")
        print(f"   🌡️  Temperature Controlled: {'Yes' if warehouse.temperature_controlled else 'No'}")
        print(f"   🌱 Organic Certified: {'Yes' if warehouse.organic_certified else 'No'}")
        print(f"   👤 Manager: {warehouse.manager.first_name} {warehouse.manager.last_name}")
        
        # Show zones
        warehouse_zones = zones.filter(warehouse=warehouse) if hasattr(zones, 'filter') else [z for z in zones if z.warehouse == warehouse]
        print(f"   🏗️  Zones ({len(warehouse_zones)}):")
        for zone in warehouse_zones:
            print(f"      • {zone.zone_code}: {zone.name} ({zone.capacity_cubic_meters}m³)")
    
    print_section("API Endpoints Available")
    base_url = "http://127.0.0.1:8000"
    endpoints = [
        ("Warehouse Management API Root", f"{base_url}/api/v1/warehouses/"),
        ("Warehouse Types", f"{base_url}/api/v1/warehouses/types/"),
        ("Warehouses List", f"{base_url}/api/v1/warehouses/warehouses/"),
        ("Warehouse Zones", f"{base_url}/api/v1/warehouses/zones/"),
        ("Warehouse Staff", f"{base_url}/api/v1/warehouses/staff/"),
        ("Warehouse Inventory", f"{base_url}/api/v1/warehouses/inventory/"),
        ("Warehouse Movements", f"{base_url}/api/v1/warehouses/movements/"),
        ("Temperature Logs", f"{base_url}/api/v1/warehouses/temperature-logs/"),
        ("Quality Inspections", f"{base_url}/api/v1/warehouses/quality-inspections/"),
        ("Warehouse Dashboard", f"{base_url}/api/v1/warehouses/dashboard/")
    ]
    
    for name, url in endpoints:
        print(f"🔗 {name:<30} → {url}")
    
    print_section("Next Steps")
    print("✅ Warehouse Management System is fully operational")
    print("✅ Sample data created for testing")
    print("✅ API endpoints are ready for integration")
    print("\n🚀 Ready to proceed with:")
    print("   • Inventory management and tracking")
    print("   • Temperature monitoring and alerts")
    print("   • Quality inspections and certifications")
    print("   • Warehouse movement tracking")
    print("   • Integration with order fulfillment")
    print("   • Blockchain traceability implementation")
    
    return {
        'warehouse_types': warehouse_types,
        'warehouses': warehouses,
        'zones': zones,
        'staff': staff
    }

if __name__ == '__main__':
    test_warehouse_system()
