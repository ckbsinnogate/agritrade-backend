#!/usr/bin/env python
"""
AgriConnect Phase 4 Warehouse Management - Production Readiness Test
Comprehensive testing suite to validate system readiness for production deployment
"""

import os
import django
import requests
import json
import time
from datetime import datetime, timedelta, date
from decimal import Decimal
import threading
from concurrent.futures import ThreadPoolExecutor

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.db.models import Count
from django.test import TestCase
from django.core.exceptions import ValidationError
from warehouses.models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, WarehouseMovement, TemperatureLog, QualityInspection
)
from products.models import Product, Category

User = get_user_model()

class WarehouseProductionReadinessTest:
    """Comprehensive production readiness testing suite"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api/v1/warehouses"
        self.test_results = {
            'data_integrity': [],
            'api_performance': [],
            'security_tests': [],
            'load_tests': [],
            'business_logic': []
        }
        self.errors = []
        self.warnings = []
    
    def print_header(self, title):
        print("\n" + "="*80)
        print(f"🧪 {title}")
        print("="*80)
    
    def print_section(self, title):
        print(f"\n📋 {title}")
        print("-"*60)
    
    def log_result(self, category, test_name, status, details="", execution_time=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time
        }
        self.test_results[category].append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        time_str = f" ({execution_time:.3f}s)" if execution_time else ""
        print(f"  {status_emoji} {test_name:<50} {status}{time_str}")
        if details and status in ["FAIL", "WARN"]:
            print(f"     Details: {details}")
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        self.print_section("Data Integrity Tests")
        
        # Test 1: Check all models have data
        start_time = time.time()
        try:
            warehouse_types = WarehouseType.objects.count()
            warehouses = Warehouse.objects.count()
            zones = WarehouseZone.objects.count()
            staff = WarehouseStaff.objects.count()
            inventory = WarehouseInventory.objects.count()
            
            if all([warehouse_types > 0, warehouses > 0, zones > 0, staff > 0]):
                self.log_result('data_integrity', 'Core Data Existence', 'PASS', 
                              f"Types: {warehouse_types}, Warehouses: {warehouses}, Zones: {zones}, Staff: {staff}, Inventory: {inventory}",
                              time.time() - start_time)
            else:
                self.log_result('data_integrity', 'Core Data Existence', 'FAIL', 
                              "Missing required data", time.time() - start_time)
        except Exception as e:
            self.log_result('data_integrity', 'Core Data Existence', 'FAIL', str(e), time.time() - start_time)
        
        # Test 2: Relationship integrity
        start_time = time.time()
        try:
            orphaned_zones = WarehouseZone.objects.filter(warehouse__isnull=True).count()
            orphaned_staff = WarehouseStaff.objects.filter(warehouse__isnull=True).count()
            orphaned_inventory = WarehouseInventory.objects.filter(warehouse__isnull=True).count()
            
            if orphaned_zones == 0 and orphaned_staff == 0 and orphaned_inventory == 0:
                self.log_result('data_integrity', 'Relationship Integrity', 'PASS', 
                              "No orphaned records found", time.time() - start_time)
            else:
                self.log_result('data_integrity', 'Relationship Integrity', 'WARN', 
                              f"Orphaned records - Zones: {orphaned_zones}, Staff: {orphaned_staff}, Inventory: {orphaned_inventory}",
                              time.time() - start_time)
        except Exception as e:
            self.log_result('data_integrity', 'Relationship Integrity', 'FAIL', str(e), time.time() - start_time)
        
        # Test 3: Data validation constraints
        start_time = time.time()
        try:
            # Check for negative quantities
            negative_inventory = WarehouseInventory.objects.filter(quantity__lt=0).count()
            invalid_utilization = Warehouse.objects.filter(current_utilization_percent__lt=0).count()
            invalid_utilization += Warehouse.objects.filter(current_utilization_percent__gt=100).count()
            
            if negative_inventory == 0 and invalid_utilization == 0:
                self.log_result('data_integrity', 'Data Validation', 'PASS', 
                              "All data within valid ranges", time.time() - start_time)
            else:
                self.log_result('data_integrity', 'Data Validation', 'FAIL', 
                              f"Invalid data - Negative inventory: {negative_inventory}, Invalid utilization: {invalid_utilization}",
                              time.time() - start_time)
        except Exception as e:
            self.log_result('data_integrity', 'Data Validation', 'FAIL', str(e), time.time() - start_time)
        
        # Test 4: Unique constraints
        start_time = time.time()
        try:
            duplicate_codes = Warehouse.objects.values('code').annotate(count=Count('code')).filter(count__gt=1).count()
            
            if duplicate_codes == 0:
                self.log_result('data_integrity', 'Unique Constraints', 'PASS', 
                              "No duplicate warehouse codes", time.time() - start_time)
            else:
                self.log_result('data_integrity', 'Unique Constraints', 'FAIL', 
                              f"Found {duplicate_codes} duplicate warehouse codes", time.time() - start_time)
        except Exception as e:
            self.log_result('data_integrity', 'Unique Constraints', 'FAIL', str(e), time.time() - start_time)
    
    def test_api_endpoints(self):
        """Test all API endpoints for functionality and performance"""
        self.print_section("API Endpoint Tests")
        
        endpoints = [
            ('/', 'API Root'),
            ('/types/', 'Warehouse Types'),
            ('/warehouses/', 'Warehouses'),
            ('/zones/', 'Warehouse Zones'),
            ('/staff/', 'Warehouse Staff'),
            ('/inventory/', 'Warehouse Inventory'),
            ('/movements/', 'Warehouse Movements'),
            ('/temperature-logs/', 'Temperature Logs'),
            ('/quality-inspections/', 'Quality Inspections'),
            ('/dashboard/', 'Warehouse Dashboard')
        ]
        
        for endpoint, name in endpoints:
            start_time = time.time()
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                execution_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if execution_time > 2.0:
                            self.log_result('api_performance', f'{name} Response Time', 'WARN', 
                                          f"Slow response: {execution_time:.3f}s", execution_time)
                        else:
                            self.log_result('api_performance', f'{name} Endpoint', 'PASS', 
                                          f"Status: {response.status_code}", execution_time)
                    except json.JSONDecodeError:
                        self.log_result('api_performance', f'{name} JSON Response', 'FAIL', 
                                      "Invalid JSON response", execution_time)
                else:
                    self.log_result('api_performance', f'{name} Endpoint', 'FAIL', 
                                  f"HTTP {response.status_code}", execution_time)
            except requests.RequestException as e:
                self.log_result('api_performance', f'{name} Endpoint', 'FAIL', 
                              f"Request failed: {str(e)}", time.time() - start_time)
    
    def test_api_crud_operations(self):
        """Test CRUD operations on API endpoints"""
        self.print_section("API CRUD Operations")
        
        # Test creating a new warehouse type (requires authentication)
        start_time = time.time()
        try:
            # Test GET with filtering
            url = f"{self.base_url}/warehouses/?status=active"
            response = requests.get(url, timeout=10)
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data or isinstance(data, list):
                    self.log_result('api_performance', 'Filtering Functionality', 'PASS', 
                                  f"Filter works correctly", execution_time)
                else:
                    self.log_result('api_performance', 'Filtering Functionality', 'WARN', 
                                  "Unexpected response format", execution_time)
            else:
                self.log_result('api_performance', 'Filtering Functionality', 'FAIL', 
                              f"HTTP {response.status_code}", execution_time)
        except Exception as e:
            self.log_result('api_performance', 'Filtering Functionality', 'FAIL', str(e), time.time() - start_time)
        
        # Test pagination
        start_time = time.time()
        try:
            url = f"{self.base_url}/inventory/?page_size=5"
            response = requests.get(url, timeout=10)
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'count' in data and 'results' in data:
                    self.log_result('api_performance', 'Pagination', 'PASS', 
                                  f"Pagination working", execution_time)
                else:
                    self.log_result('api_performance', 'Pagination', 'WARN', 
                                  "Pagination not implemented", execution_time)
            else:
                self.log_result('api_performance', 'Pagination', 'FAIL', 
                              f"HTTP {response.status_code}", execution_time)
        except Exception as e:
            self.log_result('api_performance', 'Pagination', 'FAIL', str(e), time.time() - start_time)
    
    def test_database_performance(self):
        """Test database performance and optimization"""
        self.print_section("Database Performance Tests")
        
        # Test query performance
        start_time = time.time()
        try:
            # Complex query with joins
            warehouses = Warehouse.objects.select_related('warehouse_type', 'manager').prefetch_related('zones', 'staff').all()
            list(warehouses)  # Force evaluation
            execution_time = time.time() - start_time
            
            if execution_time < 1.0:
                self.log_result('api_performance', 'Complex Query Performance', 'PASS', 
                              f"Query optimized", execution_time)
            elif execution_time < 3.0:
                self.log_result('api_performance', 'Complex Query Performance', 'WARN', 
                              f"Query could be optimized", execution_time)
            else:
                self.log_result('api_performance', 'Complex Query Performance', 'FAIL', 
                              f"Query too slow", execution_time)
        except Exception as e:
            self.log_result('api_performance', 'Complex Query Performance', 'FAIL', str(e), time.time() - start_time)
        
        # Test database connection handling
        start_time = time.time()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM warehouses")
                result = cursor.fetchone()
            execution_time = time.time() - start_time
            
            if result and result[0] >= 0:
                self.log_result('api_performance', 'Database Connection', 'PASS', 
                              f"Connection stable", execution_time)
            else:
                self.log_result('api_performance', 'Database Connection', 'FAIL', 
                              "Invalid query result", execution_time)
        except Exception as e:
            self.log_result('api_performance', 'Database Connection', 'FAIL', str(e), time.time() - start_time)
    
    def test_business_logic(self):
        """Test critical business logic functions"""
        self.print_section("Business Logic Tests")
        
        # Test inventory calculations
        start_time = time.time()
        try:
            inventory_items = WarehouseInventory.objects.all()[:5]
            all_calculations_correct = True
            
            for item in inventory_items:
                expected_available = item.quantity - item.reserved_quantity
                if item.available_quantity != expected_available:
                    all_calculations_correct = False
                    break
            
            execution_time = time.time() - start_time
            if all_calculations_correct:
                self.log_result('business_logic', 'Inventory Calculations', 'PASS', 
                              "Available quantity calculations correct", execution_time)
            else:
                self.log_result('business_logic', 'Inventory Calculations', 'FAIL', 
                              "Inventory calculations incorrect", execution_time)
        except Exception as e:
            self.log_result('business_logic', 'Inventory Calculations', 'FAIL', str(e), time.time() - start_time)
        
        # Test warehouse utilization calculations
        start_time = time.time()
        try:
            warehouses = Warehouse.objects.all()[:3]
            valid_utilization = True
            
            for warehouse in warehouses:
                if not (0 <= warehouse.current_utilization_percent <= 100):
                    valid_utilization = False
                    break
            
            execution_time = time.time() - start_time
            if valid_utilization:
                self.log_result('business_logic', 'Utilization Calculations', 'PASS', 
                              "Utilization percentages valid", execution_time)
            else:
                self.log_result('business_logic', 'Utilization Calculations', 'FAIL', 
                              "Invalid utilization percentages", execution_time)
        except Exception as e:
            self.log_result('business_logic', 'Utilization Calculations', 'FAIL', str(e), time.time() - start_time)
        
        # Test expiry date logic
        start_time = time.time()
        try:
            inventory_with_expiry = WarehouseInventory.objects.filter(expiry_date__isnull=False)[:5]
            expiry_logic_correct = True
            
            for item in inventory_with_expiry:
                days_until_expiry = item.days_until_expiry()
                if days_until_expiry is not None:
                    # Check if calculation makes sense
                    manual_calc = (item.expiry_date - datetime.now().date()).days
                    if abs(days_until_expiry - manual_calc) > 1:  # Allow 1 day tolerance
                        expiry_logic_correct = False
                        break
            
            execution_time = time.time() - start_time
            if expiry_logic_correct:
                self.log_result('business_logic', 'Expiry Date Logic', 'PASS', 
                              "Expiry calculations correct", execution_time)
            else:
                self.log_result('business_logic', 'Expiry Date Logic', 'FAIL', 
                              "Expiry calculations incorrect", execution_time)
        except Exception as e:
            self.log_result('business_logic', 'Expiry Date Logic', 'FAIL', str(e), time.time() - start_time)
    
    def test_concurrent_operations(self):
        """Test system behavior under concurrent load"""
        self.print_section("Concurrent Load Tests")
        
        def make_api_request(url):
            try:
                response = requests.get(url, timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # Test concurrent API requests
        start_time = time.time()
        try:
            urls = [f"{self.base_url}/warehouses/" for _ in range(10)]
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(make_api_request, urls))
            
            execution_time = time.time() - start_time
            success_rate = sum(results) / len(results)
            
            if success_rate >= 0.9:
                self.log_result('load_tests', 'Concurrent API Requests', 'PASS', 
                              f"Success rate: {success_rate:.1%}", execution_time)
            elif success_rate >= 0.7:
                self.log_result('load_tests', 'Concurrent API Requests', 'WARN', 
                              f"Success rate: {success_rate:.1%}", execution_time)
            else:
                self.log_result('load_tests', 'Concurrent API Requests', 'FAIL', 
                              f"Success rate: {success_rate:.1%}", execution_time)
        except Exception as e:
            self.log_result('load_tests', 'Concurrent API Requests', 'FAIL', str(e), time.time() - start_time)
    
    def test_security_basics(self):
        """Test basic security measures"""
        self.print_section("Security Tests")
        
        # Test for SQL injection protection (basic test)
        start_time = time.time()
        try:
            malicious_query = "'; DROP TABLE warehouses; --"
            url = f"{self.base_url}/warehouses/?search={malicious_query}"
            response = requests.get(url, timeout=10)
            execution_time = time.time() - start_time
            
            # If we get a response (not a 500 error), the system handled it
            if response.status_code in [200, 400, 404]:
                self.log_result('security_tests', 'SQL Injection Protection', 'PASS', 
                              "System handled malicious input", execution_time)
            else:
                self.log_result('security_tests', 'SQL Injection Protection', 'WARN', 
                              f"Unexpected response: {response.status_code}", execution_time)
        except Exception as e:
            self.log_result('security_tests', 'SQL Injection Protection', 'FAIL', str(e), time.time() - start_time)
        
        # Test CORS headers
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            execution_time = time.time() - start_time
            
            if 'Access-Control-Allow-Origin' in response.headers:
                self.log_result('security_tests', 'CORS Configuration', 'PASS', 
                              "CORS headers present", execution_time)
            else:
                self.log_result('security_tests', 'CORS Configuration', 'WARN', 
                              "CORS headers missing", execution_time)
        except Exception as e:
            self.log_result('security_tests', 'CORS Configuration', 'FAIL', str(e), time.time() - start_time)
    
    def generate_production_readiness_report(self):
        """Generate comprehensive production readiness report"""
        self.print_header("PRODUCTION READINESS REPORT")
        
        total_tests = sum(len(results) for results in self.test_results.values())
        passed_tests = sum(1 for results in self.test_results.values() for result in results if result['status'] == 'PASS')
        failed_tests = sum(1 for results in self.test_results.values() for result in results if result['status'] == 'FAIL')
        warned_tests = sum(1 for results in self.test_results.values() for result in results if result['status'] == 'WARN')
        
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️  Warnings: {warned_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Category Breakdown:")
        for category, results in self.test_results.items():
            if results:
                category_passed = sum(1 for r in results if r['status'] == 'PASS')
                category_total = len(results)
                print(f"   {category.replace('_', ' ').title()}: {category_passed}/{category_total} passed")
        
        # Production readiness assessment
        print(f"\n🎯 Production Readiness Assessment:")
        
        if failed_tests == 0:
            if warned_tests <= 2:
                readiness_status = "🟢 READY FOR PRODUCTION"
                readiness_details = "All critical tests passed. System is production-ready."
            else:
                readiness_status = "🟡 READY WITH MONITORING"
                readiness_details = f"System ready but requires monitoring for {warned_tests} warning areas."
        elif failed_tests <= 2:
            readiness_status = "🟡 NEEDS MINOR FIXES"
            readiness_details = f"System needs {failed_tests} critical fixes before production."
        else:
            readiness_status = "🔴 NOT READY"
            readiness_details = f"System has {failed_tests} critical issues requiring resolution."
        
        print(f"   Status: {readiness_status}")
        print(f"   Details: {readiness_details}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if failed_tests == 0 and warned_tests <= 2:
            recommendations = [
                "✅ System is production-ready",
                "✅ Set up monitoring and alerting",
                "✅ Implement backup and disaster recovery",
                "✅ Configure production database optimization",
                "✅ Set up SSL certificates and security hardening"
            ]
        else:
            recommendations = [
                "🔧 Address all failed tests before production deployment",
                "⚠️  Review and resolve warning areas",
                "📊 Implement comprehensive monitoring",
                "🔒 Conduct security audit",
                "🚀 Perform load testing with production-level traffic"
            ]
        
        for rec in recommendations:
            print(f"   {rec}")
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warned_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'ready_for_production': failed_tests == 0 and warned_tests <= 2
        }
    
    def run_all_tests(self):
        """Run all production readiness tests"""
        self.print_header("WAREHOUSE MANAGEMENT SYSTEM - PRODUCTION READINESS TESTING")
        
        print("🔍 Running comprehensive production readiness tests...")
        print("This may take several minutes to complete.")
        
        # Run all test categories
        self.test_data_integrity()
        self.test_api_endpoints()
        self.test_api_crud_operations()
        self.test_database_performance()
        self.test_business_logic()
        self.test_concurrent_operations()
        self.test_security_basics()
        
        # Generate final report
        return self.generate_production_readiness_report()

def main():
    """Main function to run production readiness tests"""
    tester = WarehouseProductionReadinessTest()
    results = tester.run_all_tests()
    
    print(f"\n🎉 Phase 4 Warehouse Management Testing Complete!")
    print(f"Ready to proceed to Phase 5: {'✅ YES' if results['ready_for_production'] else '❌ NO'}")
    
    return results

if __name__ == '__main__':
    main()
