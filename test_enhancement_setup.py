#!/usr/bin/env python3
"""
Simple test to verify enhancement script setup
"""

import os
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    import django
    django.setup()
    print("✅ Django setup successful")
    
    from products.models import Product, Category, ProductAttribute
    print("✅ Product models imported")
    
    from warehouses.models import Warehouse, WarehouseZone
    print("✅ Warehouse models imported")
    
    from orders.models import Order, OrderItem
    print("✅ Order models imported")
    
    from authentication.models import User
    print("✅ User model imported")
    
    # Test basic functionality
    product_count = Product.objects.count()
    print(f"✅ Products in database: {product_count}")
    
    print("\n🎉 All imports successful! Ready to run enhancements.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
