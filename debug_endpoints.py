#!/usr/bin/env python
"""
Debug Specific Endpoint Errors
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
import traceback

def debug_specific_endpoint():
    print("🔍 Debug Specific Endpoint Errors")
    print("=" * 50)
    
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
    
    # Test farmer-stats endpoint with error details
    print("\n🔧 Testing farmer-stats endpoint...")
    try:
        resp = requests.get('http://127.0.0.1:8000/api/v1/analytics/farmer-stats/', headers=headers, timeout=5)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"Response text: {resp.text}")
            try:
                error_data = resp.json()
                print(f"Error data: {error_data}")
            except:
                pass
                
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_specific_endpoint()
