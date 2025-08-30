#!/usr/bin/env python3
"""
Simple AgriConnect Status Check
"""

import os
import sys
import django
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    print("🚀 AgriConnect Status Check")
    print("=" * 40)
    
    # Check models
    print("\n📊 Model Status:")
    try:
        from products.models import Product, Category
        from warehouses.models import Warehouse
        from orders.models import Order
        from authentication.models import User
        
        print(f"  👥 Users: {User.objects.count()}")
        print(f"  📦 Categories: {Category.objects.count()}")
        print(f"  🌾 Products: {Product.objects.count()}")
        print(f"  🏭 Warehouses: {Warehouse.objects.count()}")
        print(f"  📋 Orders: {Order.objects.count()}")
        
    except Exception as e:
        print(f"  ❌ Model check failed: {e}")
    
    # Test API
    print("\n🌐 API Status:")
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Main API: Working")
        else:
            print(f"  ❌ Main API: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
    
    print("\n✅ Status check complete!")

if __name__ == "__main__":
    main()
