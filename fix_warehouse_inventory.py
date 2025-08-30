#!/usr/bin/env python
"""
Warehouse Inventory Issue Fix
Creates sample data and tests endpoints
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from warehouses.models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory
)
from products.models import Product, Category
from authentication.models import User
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
import requests

def create_sample_warehouse_data():
    """Create minimal warehouse data for testing"""
    print("🏗️ Creating warehouse sample data...")
    
    # Create warehouse type
    warehouse_type, created = WarehouseType.objects.get_or_create(
        name="General Storage",
        defaults={
            'warehouse_type': 'dry_storage',
            'description': 'General dry storage facility',
            'temperature_range_min': 15.0,
            'temperature_range_max': 25.0,
        }
    )
    
    # Get or create a manager user
    manager, created = User.objects.get_or_create(
        username='warehouse_manager',
        defaults={
            'email': 'manager@warehouse.com',
            'phone_number': '+233123456789',
            'first_name': 'Manager',
            'last_name': 'Warehouse',
            'is_verified': True,
        }
    )
    
    # Create warehouse
    warehouse, created = Warehouse.objects.get_or_create(
        code='WH001',
        defaults={
            'name': 'Test Warehouse',
            'warehouse_type': warehouse_type,
            'manager': manager,
            'country': 'GH',
            'region': 'Greater Accra',
            'city': 'Accra',
            'address': 'Test Address',
            'capacity_cubic_meters': 1000,
            'current_utilization_percent': 50,
            'status': 'active',
        }
    )
    
    # Create warehouse zone
    zone, created = WarehouseZone.objects.get_or_create(
        warehouse=warehouse,
        zone_code='A1',
        defaults={
            'name': 'Zone A1',
            'zone_type': 'dry_storage',
            'capacity_cubic_meters': 200,
            'current_stock_level': 100,
            'is_active': True,
        }
    )
    
    # Get products
    products = Product.objects.all()[:2]
    if not products.exists():
        print("❌ No products found. Creating sample product...")
        category, _ = Category.objects.get_or_create(
            name="Grains",
            defaults={'description': 'Grain products'}
        )
        product = Product.objects.create(
            name="Test Grain",
            description="Test grain product",
            category=category,
            price_per_unit=10.00,
            unit="kg",
            product_type="raw",
            organic_status="non_organic",
            origin_country="GH"
        )
        products = [product]
    
    # Create inventory items with safe dates
    print("📦 Creating inventory items...")
    for i, product in enumerate(products):
        inventory, created = WarehouseInventory.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            zone=zone,
            batch_number=f'BATCH{i+1:03d}',
            defaults={
                'quantity': Decimal('100.000'),
                'reserved_quantity': Decimal('10.000'),
                'manufacturing_date': date.today() - timedelta(days=30),
                'harvest_date': date.today() - timedelta(days=45),
                'expiry_date': date.today() + timedelta(days=180),
                'quality_status': 'good',
                'lot_number': f'LOT{i+1:03d}',
                'storage_conditions': {'temperature': 20, 'humidity': 60},
                'notes': 'Test inventory item',
            }
        )
        if created:
            print(f"  ✅ Created inventory: {inventory}")
        else:
            print(f"  📋 Inventory exists: {inventory}")
    
    print(f"✅ Warehouse data setup complete!")
    print(f"   Warehouses: {Warehouse.objects.count()}")
    print(f"   Zones: {WarehouseZone.objects.count()}")
    print(f"   Inventory Items: {WarehouseInventory.objects.count()}")

def test_warehouse_api():
    """Test warehouse inventory API"""
    print("\n🔍 Testing Warehouse API...")
    
    try:
        # Login
        login_resp = requests.post(
            'http://127.0.0.1:8000/api/v1/auth/login/',
            json={'identifier': '+233548577399', 'password': 'Kingsco45@1'},
            timeout=10
        )
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.status_code}")
            return
        
        token = login_resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test warehouse inventory endpoint
        print("📊 Testing inventory endpoint...")
        resp = requests.get(
            'http://127.0.0.1:8000/api/v1/warehouses/inventory/',
            headers=headers,
            timeout=10
        )
        
        print(f"Inventory Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('results', [])
            print(f"✅ SUCCESS: Found {len(items)} inventory items")
            
            if items:
                item = items[0]
                print("\n📋 Sample inventory item:")
                print(f"  Product: {item.get('product_name', 'N/A')}")
                print(f"  Warehouse: {item.get('warehouse_name', 'N/A')}")
                print(f"  Zone: {item.get('zone_name', 'N/A')}")
                print(f"  Quantity: {item.get('quantity', 'N/A')}")
                print(f"  Manufacturing Date: {item.get('manufacturing_date', 'N/A')}")
                print(f"  Expiry Date: {item.get('expiry_date', 'N/A')}")
                print(f"  Days Until Expiry: {item.get('days_until_expiry', 'N/A')}")
                
                # Check for problematic date values
                date_fields = ['manufacturing_date', 'harvest_date', 'expiry_date']
                issues = []
                for field in date_fields:
                    value = item.get(field)
                    if value == '' or value == 'null':
                        issues.append(f"{field} is empty string")
                    elif value is None:
                        print(f"  ✅ {field}: properly null")
                    else:
                        print(f"  ✅ {field}: {value}")
                
                if issues:
                    print(f"  ⚠️  Issues found: {issues}")
                else:
                    print("  ✅ All date fields look good")
        else:
            print(f"❌ API Error: {resp.text[:300]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    create_sample_warehouse_data()
    test_warehouse_api()
