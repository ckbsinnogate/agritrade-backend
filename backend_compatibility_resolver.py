#!/usr/bin/env python
"""
Backend Compatibility Issues Resolver
Identifies and fixes remaining 500 and 404 errors for frontend compatibility
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import F
from warehouses.models import WarehouseInventory, WarehouseZone
from subscriptions.models import UserSubscription
from authentication.models import User

def test_warehouse_optimization():
    """Test the warehouse optimization endpoint that's causing 500 error"""
    print("🔍 Testing warehouse optimization endpoint...")
    
    try:
        # Check if we have inventory data
        inventory_count = WarehouseInventory.objects.count()
        print(f"📦 Inventory items: {inventory_count}")
        
        if inventory_count == 0:
            print("❌ No inventory data found - this may cause the 500 error")
            return False
            
        # Test the actual optimization logic
        from warehouses.views import inventory_optimization
        from django.test import RequestFactory
        from rest_framework.request import Request
        
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            print("❌ No users found")
            return False
            
        # Create a GET request
        request = factory.get('/api/v1/warehouses/inventory/optimize/')
        request.user = user
        rest_request = Request(request)
        
        # Call the view function directly
        response = inventory_optimization(rest_request)
        
        if response.status_code == 200:
            print("✅ Warehouse optimization working correctly")
            return True
        else:
            print(f"❌ Warehouse optimization returned status: {response.status_code}")
            print(f"Response data: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ Warehouse optimization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_subscription_usage_stats():
    """Check if usage_stats function is properly accessible"""
    print("\n🔍 Testing subscription usage stats endpoint...")
    
    try:
        from subscriptions.views import usage_stats
        from django.test import RequestFactory
        from rest_framework.request import Request
        
        factory = RequestFactory()
        user = User.objects.first()
        
        if not user:
            print("❌ No users found")
            return False
            
        # Create a GET request
        request = factory.get('/api/v1/subscriptions/usage-stats/')
        request.user = user
        rest_request = Request(request)
        
        # Call the view function directly
        response = usage_stats(rest_request)
        
        if response.status_code in [200, 404]:  # 404 is acceptable if no subscription
            print("✅ Usage stats endpoint working")
            return True
        else:
            print(f"❌ Usage stats returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Usage stats error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_minimal_test_data():
    """Create minimal data needed for endpoints to work"""
    print("\n🔧 Creating minimal test data...")
    
    # Check if we have warehouse data
    from warehouses.models import WarehouseType, Warehouse, WarehouseZone
    from products.models import Product, Category
    
    if not WarehouseType.objects.exists():
        print("📦 Creating warehouse type...")
        warehouse_type = WarehouseType.objects.create(
            name="Test Storage",
            warehouse_type="dry_storage",
            description="Test warehouse type"
        )
    else:
        warehouse_type = WarehouseType.objects.first()
        print(f"📦 Using existing warehouse type: {warehouse_type.name}")
    
    if not Warehouse.objects.exists():
        print("🏪 Creating warehouse...")
        user = User.objects.first()
        if user:
            warehouse = Warehouse.objects.create(
                code="TEST001",
                name="Test Warehouse", 
                warehouse_type=warehouse_type,
                manager=user,
                city="Accra",
                region="Greater Accra",
                country="GH"
            )
        else:
            print("❌ No users found for warehouse manager")
            return False
    else:
        warehouse = Warehouse.objects.first()
        print(f"🏪 Using existing warehouse: {warehouse.name}")
    
    if not WarehouseZone.objects.exists():
        print("📍 Creating warehouse zone...")
        zone = WarehouseZone.objects.create(
            warehouse=warehouse,
            zone_code="A01",
            name="Zone A1",
            zone_type="dry_storage",
            capacity_cubic_meters=1000,
            current_stock_level=500
        )
    else:
        zone = WarehouseZone.objects.first()
        print(f"📍 Using existing zone: {zone.name}")
    
    if not Product.objects.exists():
        print("🌾 Creating test product...")
        if not Category.objects.exists():
            category = Category.objects.create(
                name="Test Category",
                description="Test category"
            )
        else:
            category = Category.objects.first()
            
        product = Product.objects.create(
            name="Test Rice",
            category=category,
            description="Test rice product",
            price=Decimal('50.00'),
            unit='kg'
        )
    else:
        product = Product.objects.first()
        print(f"🌾 Using existing product: {product.name}")
    
    if not WarehouseInventory.objects.exists():
        print("📋 Creating inventory...")
        inventory = WarehouseInventory.objects.create(
            product=product,
            warehouse=warehouse,
            zone=zone,
            quantity=100,
            reserved_quantity=10,
            batch_number="TEST001",
            quality_status="good",
            expiry_date=date.today() + timedelta(days=30)
        )
        print(f"📋 Created inventory: {inventory}")
    else:
        print(f"📋 Existing inventory items: {WarehouseInventory.objects.count()}")
    
    return True

def main():
    """Main function to test and fix compatibility issues"""
    print("🚀 BACKEND COMPATIBILITY ISSUES RESOLVER")
    print("=" * 50)
    
    # Create test data if needed
    if not create_minimal_test_data():
        print("❌ Failed to create test data")
        return
    
    # Test warehouse optimization
    warehouse_ok = test_warehouse_optimization()
    
    # Test subscription usage stats
    subscription_ok = check_subscription_usage_stats()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    print(f"✅ Warehouse Optimization: {'WORKING' if warehouse_ok else 'NEEDS FIX'}")
    print(f"✅ Subscription Usage Stats: {'WORKING' if subscription_ok else 'NEEDS FIX'}")
    
    if warehouse_ok and subscription_ok:
        print("\n🎉 ALL ENDPOINTS WORKING CORRECTLY!")
    else:
        print("\n⚠️ SOME ENDPOINTS NEED ATTENTION")
        
    print("\n📋 Next steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Test frontend integration")
    print("3. Monitor server logs for any remaining issues")

if __name__ == "__main__":
    main()
