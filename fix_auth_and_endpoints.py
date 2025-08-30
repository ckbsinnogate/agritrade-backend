#!/usr/bin/env python3
"""
Quick Authentication and Endpoint Fix
Test authentication and verify all endpoints are working
"""

import requests
import json

def test_endpoints_with_proper_auth():
    print("🔐 TESTING AUTHENTICATION AND FINANCIAL ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Get valid authentication credentials
    print("1. Testing Authentication with correct format...")
    
    # The system uses 'identifier' field, not 'email'
    auth_data = {
        "identifier": "fab1@gmail.com",  # Use identifier instead of email
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login/", 
                               json=auth_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("   ✅ Authentication successful!")
            access_token = tokens.get('access')
            
            # Set up headers for authenticated requests
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            print("\n2. Testing Financial Endpoints with Authentication...")
            
            # Test Financial Stats (was 404, now should work)
            response = requests.get(f"{base_url}/api/v1/financial/stats/overview/", headers=headers)
            print(f"   Financial Stats: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    stats = data['data']
                    print(f"   ✅ Total Loans: {stats.get('total_loans_issued', 0)}")
                    print(f"   ✅ Total Amount: GHS {stats.get('total_loan_amount', '0')}")
            
            # Test Loans Endpoint (was 404, now should work)
            response = requests.get(f"{base_url}/api/v1/financial/loans/", headers=headers)
            print(f"   Loans Endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"   ✅ Found {count} loan applications")
            
            # Test Logout (was 401, now should work)
            logout_data = {'refresh': tokens.get('refresh')}
            response = requests.post(f"{base_url}/api/v1/auth/logout/", 
                                   json=logout_data, headers=headers)
            print(f"   Logout: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Logout successful")
                
        elif response.status_code == 400:
            print("   ❌ Login failed - checking error details...")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw response: {response.text}")
        else:
            print(f"   ❌ Login failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 ENDPOINT VERIFICATION COMPLETE")

if __name__ == "__main__":
    test_endpoints_with_proper_auth()
