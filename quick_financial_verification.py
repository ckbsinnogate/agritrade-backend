#!/usr/bin/env python3
"""
Quick Financial API Verification
Tests the main endpoints that were causing 404 errors
"""

import os
import django
import requests
import json
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_financial_endpoints():
    """Test the financial endpoints that were causing issues"""
    
    print("🚀 QUICK FINANCIAL API VERIFICATION")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # First authenticate
    auth_data = {
        'email': 'fab1@gmail.com',
        'password': 'password123'
    }
    
    print("🔐 Authenticating...")
    auth_response = requests.post(f"{base_url}/api/v1/auth/login/", json=auth_data)
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        print(auth_response.text)
        return False
    
    tokens = auth_response.json()
    headers = {
        'Authorization': f'Bearer {tokens["access"]}',
        'Content-Type': 'application/json'
    }
    
    print("✅ Authentication successful")
    
    # Test the specific endpoints that were failing
    test_endpoints = [
        ("Financial Stats Overview", f"{base_url}/api/v1/financial/stats/overview/"),
        ("Financial Loans", f"{base_url}/api/v1/financial/loans/"),
        ("Financial Investments", f"{base_url}/api/v1/financial/investments/"),
        ("Financial Repayments", f"{base_url}/api/v1/financial/repayments/"),
    ]
    
    results = {}
    
    print("\n🏦 Testing Financial Endpoints...")
    print("=" * 50)
    
    for name, url in test_endpoints:
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: SUCCESS")
                
                if name == "Financial Stats Overview":
                    if 'data' in data:
                        overview = data['data']
                        print(f"   💰 Total Loans: {overview.get('total_loans_issued', 0)}")
                        print(f"   💵 Loan Amount: GHS {overview.get('total_loan_amount', '0')}")
                        print(f"   📈 Investments: {overview.get('total_investments', 0)}")
                        print(f"   📊 Portfolio Performance: {overview.get('portfolio_performance', '0')}%")
                
                elif name == "Financial Loans":
                    if 'results' in data:
                        loans = data['results']
                        print(f"   📋 Found {len(loans)} loan applications")
                        for loan in loans[:3]:
                            print(f"   • {loan.get('applicant_name')} - {loan.get('status_display')}")
                
                elif name == "Financial Investments":
                    if 'results' in data:
                        investments = data['results']
                        print(f"   📈 Found {len(investments)} investments")
                        for inv in investments[:2]:
                            print(f"   • {inv.get('title')} - GHS {inv.get('current_value', '0')}")
                
                elif name == "Financial Repayments":
                    if 'results' in data:
                        repayments = data['results']
                        print(f"   💳 Found {len(repayments)} repayments")
                
                results[name] = "SUCCESS"
                
            else:
                print(f"❌ {name}: FAILED ({response.status_code})")
                print(f"   Error: {response.text[:200]}")
                results[name] = f"FAILED ({response.status_code})"
                
        except Exception as e:
            print(f"❌ {name}: ERROR - {str(e)}")
            results[name] = f"ERROR - {str(e)}"
    
    # Test logout
    print("\n🚪 Testing Logout...")
    print("=" * 30)
    
    logout_data = {'refresh': tokens.get('refresh')}
    logout_response = requests.post(f"{base_url}/api/v1/auth/logout/", 
                                   json=logout_data, headers=headers)
    
    if logout_response.status_code == 200:
        print("✅ Logout: SUCCESS")
        results["Logout"] = "SUCCESS"
    else:
        print(f"❌ Logout: FAILED ({logout_response.status_code})")
        results["Logout"] = f"FAILED ({logout_response.status_code})"
    
    # Summary
    print("\n📋 VERIFICATION SUMMARY")
    print("=" * 30)
    
    success_count = sum(1 for result in results.values() if result == "SUCCESS")
    total_count = len(results)
    
    for name, result in results.items():
        status_icon = "✅" if result == "SUCCESS" else "❌"
        print(f"{status_icon} {name}: {result}")
    
    print(f"\n🎯 Overall Result: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 ALL FINANCIAL ENDPOINTS ARE WORKING!")
        print("The original 404 errors have been resolved.")
        return True
    else:
        print("⚠️  Some endpoints still need attention.")
        return False

if __name__ == '__main__':
    test_financial_endpoints()
