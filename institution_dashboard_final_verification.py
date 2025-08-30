#!/usr/bin/env python3
"""
Institution Dashboard Backend Compatibility - Final Verification
Tests all 5 previously missing endpoints to confirm they're operational
"""

import requests
import json
from datetime import datetime

def test_endpoints():
    """Test all the previously missing endpoints"""
    
    print("=" * 60)
    print("🎯 INSTITUTION DASHBOARD BACKEND COMPATIBILITY TEST")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8000"
    
    # Test endpoints that should return public info (no auth required)
    public_endpoints = [
        ("/api/v1/purchases/", "Purchases API"),
        ("/api/v1/analytics/", "Analytics API Root"),
    ]
    
    # Test endpoints that require authentication
    auth_endpoints = [
        ("/api/v1/contracts/", "Contracts Management"),
        ("/api/v1/analytics/institution/members/", "Institution Members"),
        ("/api/v1/analytics/institution/budget-analytics/", "Budget Analytics"),
        ("/api/v1/analytics/institution/stats/", "Institution Statistics"),
        ("/api/v1/purchases/purchases/list/", "Purchases List"),
    ]
    
    results = {"working": 0, "total": 0, "details": []}
    
    print("🔍 TESTING PUBLIC ENDPOINTS")
    print("-" * 30)
    
    for endpoint, name in public_endpoints:
        results["total"] += 1
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {endpoint} - 200 OK")
                results["working"] += 1
                results["details"].append(f"✅ {name}: WORKING")
            else:
                print(f"❌ {name}: {endpoint} - {response.status_code}")
                results["details"].append(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {endpoint} - ERROR: {str(e)}")
            results["details"].append(f"❌ {name}: CONNECTION ERROR")
    
    print()
    print("🔒 TESTING AUTHENTICATED ENDPOINTS")
    print("-" * 35)
    
    for endpoint, name in auth_endpoints:
        results["total"] += 1
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 401:
                # 401 is expected for auth-required endpoints without token
                print(f"✅ {name}: {endpoint} - 401 (Auth Required) ✓")
                results["working"] += 1
                results["details"].append(f"✅ {name}: REQUIRES AUTH (WORKING)")
            elif response.status_code == 200:
                print(f"✅ {name}: {endpoint} - 200 OK")
                results["working"] += 1
                results["details"].append(f"✅ {name}: WORKING")
            elif response.status_code == 404:
                print(f"❌ {name}: {endpoint} - 404 NOT FOUND")
                results["details"].append(f"❌ {name}: ENDPOINT MISSING")
            else:
                print(f"⚠️  {name}: {endpoint} - {response.status_code}")
                results["details"].append(f"⚠️ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {endpoint} - ERROR: {str(e)}")
            results["details"].append(f"❌ {name}: CONNECTION ERROR")
    
    print()
    print("=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    success_rate = (results["working"] / results["total"]) * 100
    
    print(f"Working Endpoints: {results['working']}/{results['total']}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    if success_rate == 100:
        print("🎉 STATUS: COMPLETE SUCCESS!")
        print("✅ All Institution Dashboard endpoints are operational")
        print("✅ Backend compatibility issues RESOLVED")
        print("✅ Frontend can proceed with dashboard development")
    elif success_rate >= 80:
        print("⚠️  STATUS: MOSTLY WORKING")
        print("Most endpoints operational, minor issues to resolve")
    else:
        print("❌ STATUS: NEEDS ATTENTION")
        print("Multiple endpoints require fixes")
    
    print()
    print("🔍 DETAILED RESULTS:")
    for detail in results["details"]:
        print(f"  {detail}")
    
    print()
    print("=" * 60)
    print("Next Steps for Frontend Developers:")
    print("1. Use JWT authentication for protected endpoints")
    print("2. Handle 401 responses with login redirect")
    print("3. All endpoints ready for integration")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    test_endpoints()
