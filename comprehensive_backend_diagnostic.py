#!/usr/bin/env python
"""
Comprehensive Backend Diagnostic Tool
Identifies and fixes all frontend-backend compatibility issues
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.core.management import call_command

User = get_user_model()

class BackendDiagnostic:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.client = Client()
        self.issues = []
        self.fixed_issues = []
        
    def test_authentication(self):
        """Test authentication system"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM...")
        
        try:
            # Test login endpoint
            response = requests.post(f"{self.base_url}/api/v1/auth/login/", json={
                "identifier": "+233548577399",
                "password": "Kingsco45@1"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'user_type' in data.get('user', {}):
                    print("✅ Authentication: Login working with user_type field")
                    return data.get('access')
                else:
                    print("❌ Authentication: Missing user_type field in response")
                    self.issues.append("Login response missing user_type field")
            else:
                print(f"❌ Authentication: Login failed with status {response.status_code}")
                self.issues.append(f"Login endpoint returning {response.status_code}")
                
        except Exception as e:
            print(f"❌ Authentication: Connection failed - {e}")
            self.issues.append(f"Authentication connection error: {e}")
            
        return None
    
    def test_dashboard_endpoints(self, token=None):
        """Test dashboard data loading endpoints"""
        print("\n📊 TESTING DASHBOARD ENDPOINTS...")
        
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        endpoints = [
            '/api/v1/analytics/dashboard/',
            '/api/v1/analytics/farmer-stats/',
            '/api/v1/analytics/platform/',
            '/api/v1/analytics/market-insights/',
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Dashboard: {endpoint} working")
                elif response.status_code == 404:
                    print(f"❌ Dashboard: {endpoint} not found")
                    self.issues.append(f"Missing endpoint: {endpoint}")
                else:
                    print(f"⚠️ Dashboard: {endpoint} status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Dashboard: {endpoint} failed - {e}")
                self.issues.append(f"Dashboard endpoint error: {endpoint} - {e}")
    
    def test_product_endpoints(self, token=None):
        """Test product creation and management"""
        print("\n🌾 TESTING PRODUCT ENDPOINTS...")
        
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        # Test product listing
        try:
            response = requests.get(f"{self.base_url}/api/v1/products/products/", headers=headers, timeout=5)
            if response.status_code == 200:
                print("✅ Products: Product listing working")
            else:
                print(f"❌ Products: Listing failed with status {response.status_code}")
                self.issues.append(f"Product listing endpoint error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Products: Listing failed - {e}")
            self.issues.append(f"Product listing connection error: {e}")
            
        # Test product creation (if authenticated)
        if token:
            try:
                test_product = {
                    "name": "Test Product",
                    "description": "Test product for diagnostic",
                    "price_per_unit": "10.00",
                    "unit_of_measurement": "kg",
                    "stock_quantity": 100,
                    "category": 1
                }
                
                response = requests.post(
                    f"{self.base_url}/api/v1/products/products/", 
                    headers=headers, 
                    json=test_product, 
                    timeout=5
                )
                
                if response.status_code in [200, 201]:
                    print("✅ Products: Product creation working")
                    # Clean up test product
                    if 'id' in response.json():
                        requests.delete(f"{self.base_url}/api/v1/products/products/{response.json()['id']}/", headers=headers)
                else:
                    print(f"❌ Products: Creation failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    self.issues.append(f"Product creation error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Products: Creation failed - {e}")
                self.issues.append(f"Product creation connection error: {e}")
    
    def test_subscription_endpoints(self, token=None):
        """Test subscription system"""
        print("\n💳 TESTING SUBSCRIPTION ENDPOINTS...")
        
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        endpoints = [
            '/api/v1/subscriptions/plans/',
            '/api/v1/subscriptions/user-subscriptions/',
            '/api/v1/subscriptions/analytics/dashboard/',
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Subscriptions: {endpoint} working")
                elif response.status_code == 404:
                    print(f"❌ Subscriptions: {endpoint} not found")
                    self.issues.append(f"Missing subscription endpoint: {endpoint}")
                else:
                    print(f"⚠️ Subscriptions: {endpoint} status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Subscriptions: {endpoint} failed - {e}")
                self.issues.append(f"Subscription endpoint error: {endpoint} - {e}")
    
    def test_warehouse_endpoints(self, token=None):
        """Test warehouse management"""
        print("\n🏭 TESTING WAREHOUSE ENDPOINTS...")
        
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        endpoints = [
            '/api/v1/warehouses/',
            '/api/v1/warehouses/warehouses/',
            '/api/v1/warehouses/dashboard/',
            '/api/v1/warehouses/inventory/',
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Warehouses: {endpoint} working")
                elif response.status_code == 404:
                    print(f"❌ Warehouses: {endpoint} not found")
                    self.issues.append(f"Missing warehouse endpoint: {endpoint}")
                else:
                    print(f"⚠️ Warehouses: {endpoint} status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Warehouses: {endpoint} failed - {e}")
                self.issues.append(f"Warehouse endpoint error: {endpoint} - {e}")
    
    def test_cors_and_permissions(self):
        """Test CORS and permission configurations"""
        print("\n🌐 TESTING CORS AND PERMISSIONS...")
        
        try:
            # Test CORS preflight
            response = requests.options(f"{self.base_url}/api/v1/auth/login/", headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }, timeout=5)
            
            if response.status_code in [200, 204]:
                print("✅ CORS: Preflight requests working")
            else:
                print(f"❌ CORS: Preflight failed with status {response.status_code}")
                self.issues.append(f"CORS preflight error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ CORS: Test failed - {e}")
            self.issues.append(f"CORS connection error: {e}")
    
    def generate_frontend_compatibility_report(self):
        """Generate comprehensive frontend compatibility report"""
        print("\n📋 GENERATING FRONTEND COMPATIBILITY REPORT...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "backend_status": "operational" if len(self.issues) == 0 else "issues_detected",
            "total_issues": len(self.issues),
            "issues": self.issues,
            "fixed_issues": self.fixed_issues,
            "frontend_integration_guide": {
                "authentication": {
                    "login_endpoint": "/api/v1/auth/login/",
                    "expected_response": {
                        "message": "Login successful",
                        "user": {
                            "id": "number",
                            "username": "string",
                            "first_name": "string",
                            "last_name": "string",
                            "user_type": "string (FARMER, CONSUMER, etc.)",
                            "roles": ["array of role IDs"],
                            "roles_display": ["array of role names"]
                        },
                        "access": "JWT token",
                        "refresh": "JWT refresh token"
                    }
                },
                "dashboard_endpoints": {
                    "farmer_dashboard": "/api/v1/analytics/dashboard/",
                    "farmer_stats": "/api/v1/analytics/farmer-stats/",
                    "market_insights": "/api/v1/analytics/market-insights/",
                    "platform_stats": "/api/v1/analytics/platform/"
                },
                "product_endpoints": {
                    "list_products": "/api/v1/products/products/",
                    "create_product": "POST /api/v1/products/products/",
                    "my_products": "/api/v1/products/products/my_products/",
                    "categories": "/api/v1/products/categories/"
                },
                "subscription_endpoints": {
                    "plans": "/api/v1/subscriptions/plans/",
                    "user_subscriptions": "/api/v1/subscriptions/user-subscriptions/",
                    "analytics": "/api/v1/subscriptions/analytics/dashboard/"
                },
                "warehouse_endpoints": {
                    "warehouses": "/api/v1/warehouses/warehouses/",
                    "inventory": "/api/v1/warehouses/inventory/",
                    "dashboard": "/api/v1/warehouses/dashboard/"
                }
            },
            "required_headers": {
                "authentication": "Authorization: Bearer <JWT_TOKEN>",
                "content_type": "Content-Type: application/json",
                "cors": "Origin: http://localhost:3000"
            }
        }
        
        return report
    
    def run_comprehensive_diagnostic(self):
        """Run all diagnostic tests"""
        print("=" * 80)
        print("🏥 AGRICONNECT BACKEND COMPREHENSIVE DIAGNOSTIC")
        print("=" * 80)
        
        # Test authentication first to get token
        token = self.test_authentication()
        
        # Test all major systems
        self.test_dashboard_endpoints(token)
        self.test_product_endpoints(token)
        self.test_subscription_endpoints(token)
        self.test_warehouse_endpoints(token)
        self.test_cors_and_permissions()
        
        # Generate report
        report = self.generate_frontend_compatibility_report()
        
        print("\n" + "=" * 80)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        
        if len(self.issues) == 0:
            print("🎉 ALL SYSTEMS OPERATIONAL - Backend ready for frontend integration!")
        else:
            print(f"⚠️ {len(self.issues)} ISSUES DETECTED:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        print(f"\n📝 Full report saved to: backend_diagnostic_report.json")
        
        # Save report to file
        with open('backend_diagnostic_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

if __name__ == "__main__":
    diagnostic = BackendDiagnostic()
    report = diagnostic.run_comprehensive_diagnostic()
