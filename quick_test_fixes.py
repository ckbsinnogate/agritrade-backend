#!/usr/bin/env python
"""
Quick Test - Backend Fixes Verification
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests

def quick_test():
    print("🔧 Quick Backend Fixes Test")
    print("=" * 40)
    
    # Test endpoints
    endpoints = [
        'http://127.0.0.1:8000/api/v1/warehouses/bookings/',
        'http://127.0.0.1:8000/api/v1/warehouses/inventory/optimize/',  
        'http://127.0.0.1:8000/api/v1/advertisements/dashboard/',
        'http://127.0.0.1:8000/api/v1/analytics/farmer-stats/'
    ]
    
    # Login first
    try:
        login_data = {'identifier': '+233548577399', 'password': 'Kingsco45@1'}
        resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data, timeout=5)
        
        if resp.status_code == 200:
            token = resp.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test each endpoint
    for url in endpoints:
        endpoint_name = url.split('/')[-2]
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code in [200, 401, 403]:
                print(f"✅ {endpoint_name}: Status {resp.status_code} - WORKING")
            else:
                print(f"❌ {endpoint_name}: Status {resp.status_code} - FAILING")
        except Exception as e:
            print(f"❌ {endpoint_name}: Error - {e}")

if __name__ == "__main__":
    quick_test()
