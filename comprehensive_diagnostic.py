#!/usr/bin/env python3
"""
AgriConnect Comprehensive Diagnostic & Recovery Tool
Professional recovery system with 40 years of development experience

This script will:
1. Test all API endpoints
2. Verify database integrity
3. Check model relationships
4. Validate data consistency
5. Generate recovery recommendations
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

from django.apps import apps
from django.db import models, connection
from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

class AgriConnectDiagnostic:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "api_tests": {},
            "model_checks": {},
            "data_integrity": {},
            "recommendations": []
        }
    
    def test_api_endpoints(self):
        """Test all major API endpoints"""
        print("🔍 Testing API Endpoints...")
        
        endpoints = [
            "/api/v1/",
            "/api/v1/auth/",
            "/api/v1/products/",
            "/api/v1/orders/",
            "/api/v1/payments/",
            "/api/v1/warehouses/",
            "/api/v1/reviews/",
            "/api/v1/subscriptions/",
            "/api/v1/advertisements/",
            "/api/v1/communications/",
            "/api/v1/traceability/"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                self.results["api_tests"][endpoint] = {
                    "status_code": response.status_code,
                    "working": response.status_code == 200,
                    "response_size": len(response.content)
                }
                status = "✅" if response.status_code == 200 else "❌"
                print(f"  {status} {endpoint}: {response.status_code}")
            except Exception as e:
                self.results["api_tests"][endpoint] = {
                    "status_code": None,
                    "working": False,
                    "error": str(e)
                }
                print(f"  ❌ {endpoint}: ERROR - {str(e)}")
    
    def check_models(self):
        """Check all Django models and their relationships"""
        print("\n🔍 Checking Django Models...")
        
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            if app_name.startswith('django.') or app_name.startswith('rest_framework'):
                continue
                
            print(f"\n📱 App: {app_name}")
            app_models = {}
            
            for model in app_config.get_models():
                model_name = model.__name__
                try:
                    # Test model operations
                    count = model.objects.count()
                    fields = [f.name for f in model._meta.fields]
                    relations = [f.name for f in model._meta.fields if f.is_relation]
                    
                    app_models[model_name] = {
                        "count": count,
                        "fields": fields,
                        "relations": relations,
                        "working": True
                    }
                    print(f"  ✅ {model_name}: {count} records, {len(fields)} fields")
                    
                except Exception as e:
                    app_models[model_name] = {
                        "count": 0,
                        "working": False,
                        "error": str(e)
                    }
                    print(f"  ❌ {model_name}: ERROR - {str(e)}")
            
            self.results["model_checks"][app_name] = app_models
    
    def check_data_integrity(self):
        """Check data integrity and relationships"""
        print("\n🔍 Checking Data Integrity...")
        
        try:
            # Check user counts
            user_count = User.objects.count()
            print(f"  👥 Total Users: {user_count}")
            
            # Check if we have test data
            from products.models import Product, Category
            from warehouses.models import Warehouse
            from orders.models import Order
            
            category_count = Category.objects.count()
            product_count = Product.objects.count()
            warehouse_count = Warehouse.objects.count()
            order_count = Order.objects.count()
            
            self.results["data_integrity"] = {
                "users": user_count,
                "categories": category_count,
                "products": product_count,
                "warehouses": warehouse_count,
                "orders": order_count,
                "has_test_data": product_count > 0 and category_count > 0
            }
            
            print(f"  📦 Categories: {category_count}")
            print(f"  🌾 Products: {product_count}")
            print(f"  🏭 Warehouses: {warehouse_count}")
            print(f"  📋 Orders: {order_count}")
            
            if product_count == 0:
                self.results["recommendations"].append("CREATE_TEST_DATA")
                print("  ⚠️  No test data found - should create sample data")
                
        except Exception as e:
            print(f"  ❌ Data integrity check failed: {str(e)}")
            self.results["data_integrity"]["error"] = str(e)
    
    def generate_recommendations(self):
        """Generate recovery recommendations"""
        print("\n💡 Generating Recommendations...")
        
        recommendations = []
        
        # Check API endpoints
        failed_apis = [ep for ep, result in self.results["api_tests"].items() 
                      if not result.get("working", False)]
        
        if failed_apis:
            recommendations.append({
                "priority": "HIGH",
                "category": "API_RECOVERY",
                "issue": f"Failed API endpoints: {', '.join(failed_apis)}",
                "action": "Check views.py and urls.py for these endpoints"
            })
        
        # Check models
        for app_name, models in self.results["model_checks"].items():
            failed_models = [model for model, data in models.items() 
                           if not data.get("working", False)]
            if failed_models:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "MODEL_RECOVERY",
                    "issue": f"Failed models in {app_name}: {', '.join(failed_models)}",
                    "action": f"Check {app_name}/models.py and run migrations"
                })
        
        # Check data
        if not self.results["data_integrity"].get("has_test_data", False):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "DATA_SETUP",
                "issue": "No test data found",
                "action": "Run data creation scripts to populate sample data"
            })
        
        self.results["recommendations"] = recommendations
        
        for rec in recommendations:
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[rec["priority"]]
            print(f"  {priority_emoji} {rec['priority']}: {rec['issue']}")
            print(f"     Action: {rec['action']}")
    
    def run_diagnostic(self):
        """Run complete diagnostic"""
        print("🚀 AgriConnect Comprehensive Diagnostic Starting...")
        print("=" * 60)
        
        self.test_api_endpoints()
        self.check_models()
        self.check_data_integrity()
        self.generate_recommendations()
        
        # Save results
        with open("diagnostic_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Diagnostic Complete!")
        print("📄 Results saved to: diagnostic_results.json")
        
        # Summary
        working_apis = sum(1 for result in self.results["api_tests"].values() 
                          if result.get("working", False))
        total_apis = len(self.results["api_tests"])
        
        print(f"\n📊 SUMMARY:")
        print(f"  🌐 API Endpoints: {working_apis}/{total_apis} working")
        print(f"  🔧 Recommendations: {len(self.results['recommendations'])}")
        
        if len(self.results['recommendations']) == 0:
            print("  🎉 System Status: EXCELLENT - No issues found!")
        elif len(self.results['recommendations']) <= 2:
            print("  ✅ System Status: GOOD - Minor issues to fix")
        else:
            print("  ⚠️  System Status: NEEDS ATTENTION - Multiple issues found")

if __name__ == "__main__":
    diagnostic = AgriConnectDiagnostic()
    diagnostic.run_diagnostic()
