#!/usr/bin/env python
"""
Test Product Creation
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
import json

def test_product_creation():
    try:
        # Get a fresh token
        print("🔐 Getting authentication token...")
        login_resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json={
            'identifier': '+233548577399',
            'password': 'Kingsco45@1'
        })

        if login_resp.status_code == 200:
            token = login_resp.json().get('access')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            print("✅ Authentication successful")
            
            # Test product creation with correct field names
            product_data = {
                'name': 'Test Product Django',
                'description': 'Test Description from diagnostic',
                'price_per_unit': 10.00,
                'category_id': 1,
                'stock_quantity': 100,
                'unit': 'kg',
                'product_type': 'raw',
                'organic_status': 'non_organic',
                'origin_country': 'Ghana'
            }
            
            print("🛠️ Testing product creation...")
            resp = requests.post('http://127.0.0.1:8000/api/v1/products/products/', 
                                json=product_data, headers=headers, timeout=10)
            print(f"Product Creation: Status {resp.status_code}")
            
            if resp.status_code in [200, 201]:
                print("✅ Product created successfully!")
                response_data = resp.json()
                print(f"Product ID: {response_data.get('id')}")
                print(f"Product Name: {response_data.get('name')}")
            elif resp.status_code == 405:
                print("❌ Method not allowed - checking allowed methods")
                allowed = resp.headers.get('Allow', 'Not specified')
                print(f"Allowed methods: {allowed}")
            else:
                print(f"❌ Error {resp.status_code}")
                print(f"Response: {resp.text[:500]}")
                
        else:
            print(f"❌ Login failed: {login_resp.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_product_creation()
