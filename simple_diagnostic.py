#!/usr/bin/env python
"""
Simple Backend Diagnostic
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
import json

def test_backend():
    base_url = "http://127.0.0.1:8000"
    
    print("🔐 Testing Authentication...")
    # Test login
    response = requests.post(f"{base_url}/api/v1/auth/login/", json={
        "identifier": "+233548577399",
        "password": "Kingsco45@1"
    })
    
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        user_data = data.get('user', {})
        print(f"✅ Login successful")
        print(f"User Type: {user_data.get('user_type', 'NOT_FOUND')}")
        print(f"Roles: {user_data.get('roles', 'NOT_FOUND')}")
        
        token = data.get('access')
        headers = {'Authorization': f'Bearer {token}'}
        
        print("\n📊 Testing Dashboard Endpoints...")
        
        # Test key endpoints
        endpoints = [
            ('/api/v1/analytics/dashboard-stats/', 'Dashboard Stats'),
            ('/api/v1/analytics/revenue-overview/', 'Revenue Overview'),
            ('/api/v1/analytics/user-analytics/', 'User Analytics'),
            ('/api/v1/products/', 'Products'),
            ('/api/v1/warehouses/', 'Warehouses'),
            ('/api/v1/subscriptions/', 'Subscriptions')
        ]
        
        for endpoint, name in endpoints:
            try:
                resp = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
                status = "✅" if resp.status_code == 200 else "❌"
                print(f"{status} {name}: Status {resp.status_code}")
                
                if resp.status_code != 200:
                    error_text = resp.text[:500] if resp.text else "No error message"
                    print(f"   Error: {error_text}")
                    
            except Exception as e:
                print(f"❌ {name}: Connection Error - {str(e)}")
        
        print("\n🛠️ Testing POST Operations...")
        
        # Test product creation
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price_per_unit": 10.00,
            "category_id": 10,  # Use valid category_id from available categories (10-15)
            "stock_quantity": 100,
            "unit": "kg",
            "product_type": "raw",
            "organic_status": "non_organic",
            "origin_country": "Ghana"
        }
        
        try:
            resp = requests.post(f"{base_url}/api/v1/products/products/", 
                               json=product_data, headers=headers, timeout=10)
            status = "✅" if resp.status_code in [200, 201] else "❌"
            print(f"{status} Product Creation: Status {resp.status_code}")
            
            if resp.status_code not in [200, 201]:
                print(f"   Error: {resp.text[:500]}")
                
        except Exception as e:
            print(f"❌ Product Creation: Error - {str(e)}")
            
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_backend()
