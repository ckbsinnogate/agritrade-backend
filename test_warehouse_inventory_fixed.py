#!/usr/bin/env python
"""
Test Warehouse Inventory API After Date Fix
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
import json

def test_warehouse_inventory_fixed():
    print("🔍 Testing Fixed Warehouse Inventory API...")
    
    # Login
    login_data = {'identifier': '+233548577399', 'password': 'Kingsco45@1'}
    resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data)
    
    if resp.status_code == 200:
        token = resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test warehouse inventory endpoint
        print('\n🏢 Testing /api/v1/warehouses/inventory/')
        resp = requests.get('http://127.0.0.1:8000/api/v1/warehouses/inventory/', headers=headers)
        print(f'Status: {resp.status_code}')
        
        if resp.status_code == 200:
            data = resp.json()
            print(f'✅ Success! Found {len(data.get("results", []))} inventory items')
            
            if data.get('results'):
                item = data['results'][0]
                print('\n📊 Sample item date fields:')
                date_fields = ['manufacturing_date', 'harvest_date', 'expiry_date', 'created_at', 'updated_at']
                for field in date_fields:
                    if field in item:
                        value = item[field]
                        print(f'  {field}: {value} ({type(value).__name__})')
                        
                        # Check for problematic values
                        if value == '' or value == 'null':
                            print(f'    ⚠️  Empty string or null string detected')
                        elif value is None:
                            print(f'    ✅ Properly null')
                        else:
                            print(f'    ✅ Valid value')
                            
                print(f'\n📋 Full item for frontend testing:')
                print(json.dumps(item, indent=2, default=str))
                
        else:
            print(f'❌ Error: {resp.text[:500]}')
            
        # Test individual warehouse inventory
        print('\n🏢 Testing individual warehouse inventory...')
        resp = requests.get('http://127.0.0.1:8000/api/v1/warehouses/', headers=headers)
        if resp.status_code == 200:
            warehouses = resp.json()
            if 'results' in warehouses and warehouses['results']:
                warehouse_id = warehouses['results'][0]['id']
                resp = requests.get(f'http://127.0.0.1:8000/api/v1/warehouses/{warehouse_id}/inventory/', headers=headers)
                print(f'Individual warehouse inventory status: {resp.status_code}')
                
                if resp.status_code == 200:
                    data = resp.json()
                    print(f'✅ Individual warehouse inventory working! Found {len(data)} items')
                else:
                    print(f'❌ Individual warehouse error: {resp.text[:200]}')
                    
    else:
        print(f'❌ Login failed: {resp.text}')

if __name__ == "__main__":
    test_warehouse_inventory_fixed()
