#!/usr/bin/env python3
"""
Final Verification Script for AgriConnect Backend API Fixes
Tests all previously failing endpoints to confirm resolution
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_endpoint(name, url, method='GET', data=None, auth_token=None):
    """Test an endpoint and return status info"""
    try:
        headers = HEADERS.copy()
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, json=data, timeout=10)
        
        return {
            'name': name,
            'url': url,
            'status_code': response.status_code,
            'success': response.status_code in [200, 201, 204, 302],
            'response_size': len(response.content),
            'content_type': response.headers.get('content-type', 'unknown')
        }
    except requests.exceptions.RequestException as e:
        return {
            'name': name,
            'url': url,
            'status_code': 'ERROR',
            'success': False,
            'error': str(e)
        }

def get_auth_token():
    """Get authentication token for testing protected endpoints"""
    try:
        login_data = {
            "identifier": "testuser@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login/", 
                               headers=HEADERS, json=login_data, timeout=10)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Login failed: {response.status_code} - Creating test user...")
            # Try to create a test user
            register_data = {
                "identifier": "testuser@example.com",
                "email": "testuser@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User",
                "user_type": "farmer"
            }
            reg_response = requests.post(f"{BASE_URL}/api/v1/auth/register/", 
                                       headers=HEADERS, json=register_data, timeout=10)
            if reg_response.status_code in [200, 201]:
                # Try login again
                login_response = requests.post(f"{BASE_URL}/api/v1/auth/login/", 
                                             headers=HEADERS, json=login_data, timeout=10)
                if login_response.status_code == 200:
                    return login_response.json().get('access_token')
    except Exception as e:
        print(f"Auth setup error: {e}")
    return None

def main():
    print("=" * 70)
    print("🔍 FINAL VERIFICATION: AgriConnect Backend API Fixes")
    print("=" * 70)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get authentication token
    print("🔐 Setting up authentication...")
    auth_token = get_auth_token()
    if auth_token:
        print("✅ Authentication token obtained")
    else:
        print("⚠️  Could not obtain auth token, testing without authentication")
    print()

    # Define test cases for previously failing endpoints
    test_cases = [
        # Originally 404 endpoints
        {
            'name': '🏦 Financial Stats Overview (was 404)',
            'url': f'{BASE_URL}/api/v1/financial/stats/overview/',
            'method': 'GET'
        },
        {
            'name': '💰 Loans Endpoint (was 404)', 
            'url': f'{BASE_URL}/api/v1/financial/loans/',
            'method': 'GET'
        },
        
        # Originally 401 endpoint
        {
            'name': '🚪 Logout Endpoint (was 401)',
            'url': f'{BASE_URL}/api/v1/auth/logout/',
            'method': 'DELETE',
            'data': {'refresh_token': 'dummy_token'}  # Test graceful handling
        },
        
        # Additional financial endpoints
        {
            'name': '🏦 Financial API Root',
            'url': f'{BASE_URL}/api/v1/financial/',
            'method': 'GET'
        },
        {
            'name': '📊 Investments Endpoint',
            'url': f'{BASE_URL}/api/v1/financial/investments/',
            'method': 'GET'
        },
        {
            'name': '💳 Repayments Endpoint',
            'url': f'{BASE_URL}/api/v1/financial/repayments/',
            'method': 'GET'
        },
        
        # Core API endpoints
        {
            'name': '🔑 Authentication Root',
            'url': f'{BASE_URL}/api/v1/auth/',
            'method': 'GET'
        },
        {
            'name': '🌐 API Root',
            'url': f'{BASE_URL}/api/v1/',
            'method': 'GET'
        },
        
        # Admin interface (originally 500 error)
        {
            'name': '⚙️ Django Admin (was 500)',
            'url': f'{BASE_URL}/admin/',
            'method': 'GET'
        }
    ]

    # Run tests
    results = []
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        result = test_endpoint(
            test_case['name'],
            test_case['url'],
            test_case.get('method', 'GET'),
            test_case.get('data'),
            auth_token if 'logout' in test_case['url'].lower() else None
        )
        results.append(result)
        
        # Print immediate result
        if result['success']:
            print(f"   ✅ {result['status_code']} - Success")
        else:
            print(f"   ❌ {result.get('status_code', 'ERROR')} - Failed")
            if 'error' in result:
                print(f"      Error: {result['error']}")
        print()

    # Summary
    print("=" * 70)
    print("📋 FINAL VERIFICATION SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    print()
    
    print("📊 Detailed Results:")
    print("-" * 70)
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} | {result['status_code']:>4} | {result['name']}")
    
    print()
    if success_count == total_count:
        print("🎉 ALL TESTS PASSED! Backend API issues have been resolved.")
    else:
        print("⚠️  Some tests failed. Review the results above.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
