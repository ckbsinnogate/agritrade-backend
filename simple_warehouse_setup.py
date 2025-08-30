#!/usr/bin/env python
"""
AgriConnect Warehouse Management System - Simple Demo Setup
Creates basic warehouse data to test the system
"""

import os
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from warehouses.models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, TemperatureLog, QualityInspection
)

User = get_user_model()

def create_simple_warehouse_data():
    print("Creating Warehouse Management Demo Data...")
    
    # Create a simple warehouse type
    cold_storage_type, created = WarehouseType.objects.get_or_create(
        name="Cold Storage Facility",
        defaults={
            'warehouse_type': 'cold_storage',
            'description': 'Temperature-controlled storage for perishable products',
            'temperature_range_min': Decimal('2.0'),
            'temperature_range_max': Decimal('8.0'),
            'humidity_range_min': Decimal('80.0'),
            'humidity_range_max': Decimal('95.0')
        }
    )
    
    print(f"Created warehouse type: {cold_storage_type.name}")
    
    # Create a warehouse manager user
    manager, created = User.objects.get_or_create(
        username='warehouse_manager',
        defaults={
            'email': 'manager@warehouse.com',
            'phone_number': '+233244567890',
            'first_name': 'Kwame',
            'last_name': 'Asante',
            'country': 'GH',
            'region': 'Greater Accra',
            'is_verified': True,
            'email_verified': True,
            'phone_verified': True
        }
    )
    
    print(f"Created warehouse manager: {manager.first_name} {manager.last_name}")
    
    # Create a warehouse
    warehouse, created = Warehouse.objects.get_or_create(
        code="ACC-WH-001",
        defaults={
            'name': 'AgriConnect Accra Central Warehouse',
            'warehouse_type': cold_storage_type,
            'country': 'Ghana',
            'region': 'Greater Accra',
            'city': 'Accra',
            'address': {
                'street': 'Industrial Area Road',
                'district': 'Tema',
                'postal_code': 'GA-456-7890'
            },
            'gps_coordinates': '5.6037,-0.1870',
            'capacity_cubic_meters': Decimal('5000.00'),
            'current_utilization_percent': Decimal('65.5'),
            'temperature_controlled': True,
            'humidity_controlled': True,
            'organic_certified': True,
            'has_loading_dock': True,
            'manager': manager,
            'status': 'active',
            'contact_info': {
                'phone': '+233302123456',
                'email': 'accra@agriconnect.com'
            }
        }
    )
    
    print(f"Created warehouse: {warehouse.name}")
    
    # Create warehouse zones
    cold_zone, created = WarehouseZone.objects.get_or_create(
        warehouse=warehouse,
        zone_code="COLD-A",
        defaults={
            'name': 'Cold Storage Zone A',
            'zone_type': 'cold_storage',
            'capacity_cubic_meters': Decimal('1500.00'),
            'current_stock_level': Decimal('980.50'),
            'temperature_range': {'min': 2, 'max': 8},
            'is_active': True
        }
    )
    
    organic_zone, created = WarehouseZone.objects.get_or_create(
        warehouse=warehouse,
        zone_code="ORG-A",
        defaults={
            'name': 'Organic Products Zone',
            'zone_type': 'organic_zone',
            'capacity_cubic_meters': Decimal('1200.00'),
            'current_stock_level': Decimal('750.25'),
            'temperature_range': {'min': 10, 'max': 20},
            'is_active': True
        }
    )
    
    print(f"Created {WarehouseZone.objects.filter(warehouse=warehouse).count()} warehouse zones")
    
    # Create warehouse staff
    staff, created = WarehouseStaff.objects.get_or_create(
        warehouse=warehouse,
        user=manager,
        defaults={
            'role': 'manager',
            'access_zones': [str(cold_zone.id), str(organic_zone.id)],
            'permissions': {
                'inventory_management': True,
                'staff_management': True,
                'quality_control': True
            },
            'is_active': True,
            'hired_date': date.today(),
            'performance_rating': Decimal('4.8')
        }
    )
    
    print(f"Created warehouse staff: {staff.user.first_name} as {staff.role}")
    
    print("\nWarehouse Management System Demo Data Created Successfully!")
    print(f"Warehouses: {Warehouse.objects.count()}")
    print(f"Warehouse Types: {WarehouseType.objects.count()}")
    print(f"Zones: {WarehouseZone.objects.count()}")
    print(f"Staff: {WarehouseStaff.objects.count()}")
    
    print("\nAPI Endpoints Ready:")
    print("http://127.0.0.1:8000/api/v1/warehouses/")
    print("http://127.0.0.1:8000/api/v1/warehouses/warehouses/")
    print("http://127.0.0.1:8000/api/v1/warehouses/zones/")
    print("http://127.0.0.1:8000/api/v1/warehouses/staff/")

if __name__ == '__main__':
    create_simple_warehouse_data()
