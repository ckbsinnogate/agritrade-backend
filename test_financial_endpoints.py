#!/usr/bin/env python3
"""
Financial API Endpoints Test
Simple test to verify all financial endpoints are working
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_financial_api():
    print("🏦 TESTING AGRICONNECT FINANCIAL API")
    print("=" * 50)
    
    # Test 1: Financial API Root
    print("1. Testing Financial API Root...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/financial/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Name: {data.get('name')}")
            print(f"   ✅ Status: {data.get('status')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print("\n" + "-" * 50)
    
    # Test 2: Authentication
    print("2. Testing Authentication...")
    auth_data = {
        "email": "fab1@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login/", json=auth_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("   ✅ Authentication Successful")
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
            
            # Set up headers for authenticated requests
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            print("\n" + "-" * 50)
            
            # Test 3: Financial Stats Overview (was causing 404)
            print("3. Testing Financial Stats Overview...")
            response = requests.get(f"{BASE_URL}/api/v1/financial/stats/overview/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Financial Stats Working")
                if 'data' in data:
                    overview = data['data']
                    print(f"   📊 Total Loans: {overview.get('total_loans_issued', 0)}")
                    print(f"   💰 Total Amount: GHS {overview.get('total_loan_amount', '0')}")
                    print(f"   📈 Investments: {overview.get('total_investments', 0)}")
                    print(f"   📊 Portfolio Performance: {overview.get('portfolio_performance', '0')}%")
            else:
                print(f"   ❌ Error: {response.text}")
            
            print("\n" + "-" * 50)
            
            # Test 4: Loans endpoint (was causing 404)
            print("4. Testing Loans Endpoint...")
            response = requests.get(f"{BASE_URL}/api/v1/financial/loans/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Loans Endpoint Working")
                if 'results' in data:
                    loans = data['results']
                    print(f"   📋 Found {len(loans)} loan applications")
                    for loan in loans[:3]:  # Show first 3
                        print(f"   • {loan.get('applicant_name')} - {loan.get('status_display')}")
            else:
                print(f"   ❌ Error: {response.text}")
            
            print("\n" + "-" * 50)
            
            # Test 5: Investments endpoint
            print("5. Testing Investments Endpoint...")
            response = requests.get(f"{BASE_URL}/api/v1/financial/investments/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Investments Endpoint Working")
                if 'results' in data:
                    investments = data['results']
                    print(f"   📈 Found {len(investments)} investments")
                    for inv in investments[:2]:  # Show first 2
                        print(f"   • {inv.get('title')} - GHS {inv.get('current_value', '0')}")
            else:
                print(f"   ❌ Error: {response.text}")
            
            print("\n" + "-" * 50)
            
            # Test 6: Logout (was causing 401)
            print("6. Testing Logout...")
            logout_data = {'refresh': refresh_token}
            response = requests.post(f"{BASE_URL}/api/v1/auth/logout/", json=logout_data, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Logout Successful")
            else:
                print(f"   ❌ Logout Error: {response.text}")
        
        else:
            print(f"   ❌ Authentication Failed: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎯 FINANCIAL API TESTING COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_financial_api()
