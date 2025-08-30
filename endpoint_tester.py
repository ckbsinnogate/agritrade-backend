#!/usr/bin/env python
"""
Simple Backend Endpoint Tester
Tests the specific endpoints causing 500 and 404 errors
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
import json
from authentication.models import User

def test_subscription_endpoints():
    """Test subscription endpoints causing frontend errors"""
    print("🔍 Testing Subscription Endpoints...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # First login to get token
        login_data = {
            "identifier": "+233548577878",  # Phone from logs
            "password": "test123"  # Try common password
        }
        
        login_resp = requests.post(f"{base_url}/api/v1/auth/login/", 
                                 json=login_data, 
                                 timeout=10)
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.status_code}")
            print(f"Response: {login_resp.text}")
            return False
            
        token = login_resp.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test usage-stats endpoint
        print("📊 Testing usage-stats endpoint...")
        usage_resp = requests.get(f"{base_url}/api/v1/subscriptions/usage-stats/",
                                headers=headers,
                                timeout=10)
        
        print(f"Usage Stats Status: {usage_resp.status_code}")
        if usage_resp.status_code == 404:
            print("❌ usage-stats endpoint returning 404 - URL issue")
        elif usage_resp.status_code == 500:
            print("❌ usage-stats endpoint returning 500 - server error")
        else:
            print("✅ usage-stats endpoint working")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is Django running?")
        return False
    except Exception as e:
        print(f"❌ Error testing subscriptions: {e}")
        return False

def test_warehouse_optimization():
    """Test warehouse optimization endpoint"""
    print("\n🏭 Testing Warehouse Optimization Endpoint...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Login first
        login_data = {
            "identifier": "+233548577878",
            "password": "test123"
        }
        
        login_resp = requests.post(f"{base_url}/api/v1/auth/login/", 
                                 json=login_data, 
                                 timeout=10)
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.status_code}")
            return False
            
        token = login_resp.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test warehouse optimization endpoint
        print("📦 Testing inventory optimization endpoint...")
        warehouse_resp = requests.get(f"{base_url}/api/v1/warehouses/inventory/optimize/",
                                    headers=headers,
                                    timeout=10)
        
        print(f"Warehouse Optimization Status: {warehouse_resp.status_code}")
        if warehouse_resp.status_code == 500:
            print("❌ Warehouse optimization returning 500 - server error")
            print(f"Response: {warehouse_resp.text}")
        else:
            print("✅ Warehouse optimization endpoint working")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is Django running?")
        return False
    except Exception as e:
        print(f"❌ Error testing warehouse: {e}")
        return False

def check_server_status():
    """Check if Django server is running"""
    print("🌐 Checking Django Server Status...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is running")
            return True
        else:
            print(f"⚠️ Django server responded with: {response.status_code}")
            return True  # Still running, just different response
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running")
        print("💡 Start with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 BACKEND ENDPOINT COMPATIBILITY TESTER")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_status():
        return
    
    # Test subscription endpoints
    test_subscription_endpoints()
    
    # Test warehouse endpoints
    test_warehouse_optimization()
    
    print("\n" + "=" * 50)
    print("📋 TESTING COMPLETE")
    print("Check the results above for any issues to fix")

if __name__ == "__main__":
    main()
