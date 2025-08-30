#!/usr/bin/env python
"""
Debug Warehouse Date Fields
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
import json

def test_warehouse_dates():
    print("🔍 Testing Warehouse Inventory Date Fields...")
    
    # Login
    login_data = {'identifier': '+233548577399', 'password': 'Kingsco45@1'}
    resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data)
    
    if resp.status_code == 200:
        token = resp.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get warehouse inventory
        resp = requests.get('http://127.0.0.1:8000/api/v1/warehouses/inventory/', headers=headers)
        print(f'Inventory Status: {resp.status_code}')
        
        if resp.status_code == 200:
            data = resp.json()
            if 'results' in data and data['results']:
                item = data['results'][0]
                print('\n📊 Date fields in inventory item:')
                date_fields = ['manufacturing_date', 'harvest_date', 'expiry_date', 'created_at', 'updated_at']
                
                for field in date_fields:
                    if field in item:
                        value = item[field]
                        print(f'  {field}: {value} (type: {type(value).__name__})')
                        
                        # Check if it's null or empty
                        if value is None or value == '':
                            print(f'    ❌ NULL/EMPTY - This could cause frontend issues')
                        elif isinstance(value, str) and 'null' in value.lower():
                            print(f'    ❌ NULL STRING - This could cause frontend issues')
                
                print(f'\n📋 Full item structure:')
                print(json.dumps(item, indent=2, default=str)[:1000] + '...')
                
            else:
                print('❌ No inventory items found')
                
        # Also test individual warehouse inventory
        print('\n🏢 Testing individual warehouse inventory...')
        resp = requests.get('http://127.0.0.1:8000/api/v1/warehouses/', headers=headers)
        if resp.status_code == 200:
            warehouses = resp.json()
            if 'results' in warehouses and warehouses['results']:
                warehouse_id = warehouses['results'][0]['id']
                resp = requests.get(f'http://127.0.0.1:8000/api/v1/warehouses/{warehouse_id}/inventory/', headers=headers)
                print(f'Warehouse inventory status: {resp.status_code}')
                
                if resp.status_code == 200 and resp.json():
                    item = resp.json()[0]
                    print('\n📊 Warehouse-specific inventory date fields:')
                    for field in date_fields:
                        if field in item:
                            value = item[field]
                            print(f'  {field}: {value}')
                            if value is None or value == '':
                                print(f'    ❌ POTENTIAL ISSUE: NULL/EMPTY value')
    else:
        print(f'❌ Login failed: {resp.text}')

if __name__ == "__main__":
    test_warehouse_dates()
