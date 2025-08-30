#!/usr/bin/env python3
"""
Test Fixed API Endpoints
Test the 4 API endpoints we fixed to see if they're working
"""

import requests
import json
from datetime import datetime

def test_fixed_endpoints():
    """Test the 4 endpoints that were reported as having issues"""
    
    print("🔧 TESTING FIXED API ENDPOINTS")
    print("=" * 50)
    print(f"📅 Test Date: {datetime.now()}")
    print()
    
    base_url = "http://127.0.0.1:8000/api/v1"
    
    endpoints_to_test = [
        f"{base_url}/payments/",
        f"{base_url}/reviews/", 
        f"{base_url}/communications/",
        f"{base_url}/ai/"
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: Working (Status: {response.status_code})")
                results.append({'endpoint': endpoint, 'status': 'working', 'code': response.status_code})
            elif response.status_code == 401:
                print(f"✅ {endpoint}: Working - Authentication required (Status: {response.status_code})")
                results.append({'endpoint': endpoint, 'status': 'working', 'code': response.status_code})
            else:
                print(f"⚠️ {endpoint}: Response code {response.status_code}")
                results.append({'endpoint': endpoint, 'status': 'issue', 'code': response.status_code})
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Django server not running")
            results.append({'endpoint': endpoint, 'status': 'server_down', 'code': 'N/A'})
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)}")
            results.append({'endpoint': endpoint, 'status': 'error', 'code': str(e)})
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    
    working = len([r for r in results if r['status'] == 'working'])
    total = len(results)
    
    print(f"✅ Working Endpoints: {working}/{total}")
    
    if working == total:
        print("🎉 ALL ENDPOINTS FIXED! ✅")
    elif working > 0:
        print("🔧 Some endpoints fixed, server might need to be started")
    else:
        print("❌ Django server needs to be started")
    
    return results

if __name__ == "__main__":
    test_fixed_endpoints()
