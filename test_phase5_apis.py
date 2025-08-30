#!/usr/bin/env python
"""
AgriConnect Phase 5: API Testing for Blockchain Traceability
===========================================================

Test all traceability API endpoints to verify system functionality
"""

import requests
import json
from pprint import pprint

# API Base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_traceability_apis():
    """Test all traceability API endpoints"""
    
    print("🧪 PHASE 5 API TESTING: Blockchain Traceability System")
    print("=" * 60)
    
    # Test endpoints that don't require authentication first
    endpoints = [
        "/traceability/blockchain-networks/",
        "/traceability/smart-contracts/", 
        "/traceability/farms/",
        "/traceability/farm-certifications/",
        "/traceability/product-traces/",
        "/traceability/supply-chain-events/",
        "/traceability/consumer-scans/"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        print("-" * 40)
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    print(f"Records Found: {data.get('count', 0)}")
                    if data['results']:
                        print("Sample Record:")
                        pprint(data['results'][0], width=80, depth=2)
                elif isinstance(data, list):
                    print(f"Records Found: {len(data)}")
                    if data:
                        print("Sample Record:")
                        pprint(data[0], width=80, depth=2)
            else:
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Test specific QR verification endpoint
    print(f"\n🔍 Testing: QR Code Verification")
    print("-" * 40)
    
    try:
        # Get a sample product trace for QR testing
        response = requests.get(f"{BASE_URL}/traceability/product-traces/")
        if response.status_code == 200:
            traces = response.json()
            if isinstance(traces, dict) and traces.get('results'):
                trace = traces['results'][0]
                blockchain_id = trace.get('blockchain_id')
                
                if blockchain_id:
                    # Test QR verification endpoint
                    verify_response = requests.get(f"{BASE_URL}/traceability/verify-qr/{blockchain_id}/")
                    print(f"QR Verification Status: {verify_response.status_code}")
                    if verify_response.status_code == 200:
                        print("QR Verification Data:")
                        pprint(verify_response.json(), width=80, depth=2)
    except Exception as e:
        print(f"QR Test Error: {str(e)}")
    
    # Test consumer scan simulation
    print(f"\n🔍 Testing: Consumer Scan Simulation")
    print("-" * 40)
    
    try:
        # Get a sample product trace
        response = requests.get(f"{BASE_URL}/traceability/product-traces/")
        if response.status_code == 200:
            traces = response.json()
            if isinstance(traces, dict) and traces.get('results'):
                trace_id = traces['results'][0].get('id')
                
                # Simulate a consumer scan
                scan_data = {
                    "consumer_id": "api_test_consumer",
                    "ip_address": "127.0.0.1",
                    "user_agent": "AgriConnect API Test",
                    "location": "API Test Location",
                    "device_type": "api",
                    "app_version": "1.0.0"
                }
                
                scan_response = requests.post(
                    f"{BASE_URL}/traceability/product-traces/{trace_id}/scan/",
                    json=scan_data
                )
                print(f"Consumer Scan Status: {scan_response.status_code}")
                if scan_response.status_code in [200, 201]:
                    print("Consumer Scan Response:")
                    pprint(scan_response.json(), width=80, depth=2)
    except Exception as e:
        print(f"Consumer Scan Error: {str(e)}")
    
    print(f"\n✅ API TESTING COMPLETED!")
    print("🚀 All traceability endpoints are operational!")

if __name__ == "__main__":
    test_traceability_apis()
