#!/usr/bin/env python3
"""
🔧 AgriConnect AI Disease Detection - Fixed Endpoint Tester
Tests the corrected disease detection endpoint with various scenarios
"""

import os
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class AIDiseaseDetectionTester:
    """Test the fixed AI disease detection endpoint"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.test_user = None
        self.auth_token = None
        
    def setup_test_user(self):
        """Create or get test user and auth token"""
        try:
            # Create test user if doesn't exist
            self.test_user, created = User.objects.get_or_create(
                username='ai_tester',
                defaults={
                    'email': 'ai_tester@agriconnect.com',
                    'first_name': 'AI',
                    'last_name': 'Tester'
                }
            )
            
            if created:
                self.test_user.set_password('testpass123')
                self.test_user.save()
                print("✅ Created test user: ai_tester")
            else:
                print("✅ Using existing test user: ai_tester")
            
            # Generate JWT token
            refresh = RefreshToken.for_user(self.test_user)
            self.auth_token = str(refresh.access_token)
            
            # Set auth headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            })
            
            print(f"✅ Generated auth token for testing")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup test user: {str(e)}")
            return False
    
    def test_health_endpoint(self):
        """Test AI health endpoint"""
        print("\n🔍 Testing AI Health Endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ai/api/health/")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data}")
                print("   ✅ Health endpoint working")
                return True
            else:
                print(f"   ❌ Health endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health endpoint error: {str(e)}")
            return False
    
    def test_disease_detection_scenarios(self):
        """Test various disease detection scenarios"""
        print("\n🦠 Testing Disease Detection Scenarios...")
        
        scenarios = [
            {
                "name": "Valid: Symptoms Only",
                "data": {
                    "crop_type": "tomato",
                    "symptoms": "Yellow leaves with brown spots, wilting plants",
                    "location": "Ghana"
                },
                "expected_status": 200,
                "should_succeed": True
            },
            {
                "name": "Valid: Image URL Only", 
                "data": {
                    "crop_type": "maize",
                    "image_url": "https://example.com/plant-disease.jpg",
                    "location": "Nigeria"
                },
                "expected_status": 200,
                "should_succeed": True
            },
            {
                "name": "Valid: Both Symptoms and Image",
                "data": {
                    "crop_type": "cassava",
                    "symptoms": "Mosaic pattern on leaves",
                    "image_url": "https://example.com/cassava-disease.jpg",
                    "location": "Kenya"
                },
                "expected_status": 200,
                "should_succeed": True
            },
            {
                "name": "Invalid: Missing crop_type",
                "data": {
                    "symptoms": "Yellow leaves with spots"
                },
                "expected_status": 400,
                "should_succeed": False,
                "expected_error": "crop_type is required"
            },
            {
                "name": "Invalid: Missing both symptoms and image",
                "data": {
                    "crop_type": "tomato",
                    "location": "Ghana"
                },
                "expected_status": 400,
                "should_succeed": False,
                "expected_error": "Either symptoms description or image_url must be provided"
            },
            {
                "name": "Valid: Minimal Required Data",
                "data": {
                    "crop_type": "rice",
                    "symptoms": "Brown spots"
                },
                "expected_status": 200,
                "should_succeed": True
            }
        ]
        
        results = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n   Test {i}: {scenario['name']}")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/ai/api/disease-detection/",
                    json=scenario['data']
                )
                
                print(f"      Status Code: {response.status_code}")
                print(f"      Expected: {scenario['expected_status']}")
                
                # Check status code
                status_ok = response.status_code == scenario['expected_status']
                
                if response.status_code in [200, 400, 401, 500]:
                    try:
                        response_data = response.json()
                        print(f"      Response: {json.dumps(response_data, indent=2)[:200]}...")
                        
                        # Check success/failure expectation
                        if scenario['should_succeed']:
                            success_ok = response_data.get('success', False)
                            test_passed = status_ok and success_ok
                        else:
                            error_ok = 'error' in response_data
                            if 'expected_error' in scenario:
                                error_msg_ok = scenario['expected_error'] in response_data.get('error', '')
                                test_passed = status_ok and error_ok and error_msg_ok
                            else:
                                test_passed = status_ok and error_ok
                        
                    except json.JSONDecodeError:
                        print(f"      Response (text): {response.text[:200]}...")
                        test_passed = status_ok
                else:
                    print(f"      Response: {response.text[:200]}...")
                    test_passed = status_ok
                
                result = {
                    'scenario': scenario['name'],
                    'passed': test_passed,
                    'status_code': response.status_code,
                    'expected_status': scenario['expected_status']
                }
                
                if test_passed:
                    print(f"      ✅ PASSED")
                else:
                    print(f"      ❌ FAILED")
                
                results.append(result)
                
            except Exception as e:
                print(f"      ❌ ERROR: {str(e)}")
                results.append({
                    'scenario': scenario['name'],
                    'passed': False,
                    'error': str(e)
                })
        
        return results
    
    def test_other_ai_endpoints(self):
        """Test other AI endpoints for completeness"""
        print("\n🤖 Testing Other AI Endpoints...")
        
        endpoints = [
            {
                "name": "AI Chat",
                "url": "/api/v1/ai/api/chat/",
                "method": "POST",
                "data": {
                    "message": "Hello, can you help me with farming?",
                    "language": "en"
                }
            },
            {
                "name": "Crop Advisory", 
                "url": "/api/v1/ai/api/crop-advisory/",
                "method": "POST",
                "data": {
                    "crop_type": "tomato",
                    "location": "Ghana",
                    "season": "dry"
                }
            },
            {
                "name": "Market Intelligence",
                "url": "/api/v1/ai/api/market-intelligence/",
                "method": "POST", 
                "data": {
                    "crop_type": "maize",
                    "location": "Lagos",
                    "analysis_type": "price_prediction"
                }
            }
        ]
        
        results = []
        
        for endpoint in endpoints:
            print(f"\n   Testing {endpoint['name']}...")
            
            try:
                if endpoint['method'] == 'POST':
                    response = self.session.post(
                        f"{self.base_url}{endpoint['url']}",
                        json=endpoint['data']
                    )
                else:
                    response = self.session.get(f"{self.base_url}{endpoint['url']}")
                
                print(f"      Status Code: {response.status_code}")
                
                # Check if endpoint exists and is accessible
                if response.status_code == 404:
                    print(f"      ❌ Endpoint not found")
                    results.append({'endpoint': endpoint['name'], 'status': 'NOT_FOUND'})
                elif response.status_code == 401:
                    print(f"      ⚠️ Authentication required (endpoint exists)")
                    results.append({'endpoint': endpoint['name'], 'status': 'AUTH_REQUIRED'})
                elif response.status_code in [200, 400, 500]:
                    print(f"      ✅ Endpoint accessible")
                    results.append({'endpoint': endpoint['name'], 'status': 'ACCESSIBLE'})
                else:
                    print(f"      ⚠️ Unexpected status: {response.status_code}")
                    results.append({'endpoint': endpoint['name'], 'status': f'STATUS_{response.status_code}'})
                
            except Exception as e:
                print(f"      ❌ ERROR: {str(e)}")
                results.append({'endpoint': endpoint['name'], 'status': 'ERROR', 'error': str(e)})
        
        return results
    
    def generate_report(self, disease_results, other_results):
        """Generate comprehensive test report"""
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_summary': {
                'total_disease_tests': len(disease_results),
                'disease_tests_passed': sum(1 for r in disease_results if r.get('passed', False)),
                'other_endpoints_tested': len(other_results),
            },
            'disease_detection_results': disease_results,
            'other_endpoints_results': other_results,
            'recommendations': []
        }
        
        # Add recommendations based on results
        failed_disease_tests = [r for r in disease_results if not r.get('passed', False)]
        if failed_disease_tests:
            report['recommendations'].append(
                f"Fix {len(failed_disease_tests)} failing disease detection scenarios"
            )
        
        not_found_endpoints = [r for r in other_results if r.get('status') == 'NOT_FOUND']
        if not_found_endpoints:
            report['recommendations'].append(
                f"Fix {len(not_found_endpoints)} missing AI endpoints"
            )
        
        if not failed_disease_tests and not not_found_endpoints:
            report['recommendations'].append("All tests passed! AI endpoints are working correctly.")
        
        return report
    
    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🧪 AgriConnect AI Disease Detection - Comprehensive Test")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Cannot proceed without test user setup")
            return
        
        # Test health endpoint
        health_ok = self.test_health_endpoint()
        
        # Test disease detection scenarios
        disease_results = self.test_disease_detection_scenarios()
        
        # Test other AI endpoints
        other_results = self.test_other_ai_endpoints()
        
        # Generate report
        report = self.generate_report(disease_results, other_results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Disease Detection Tests: {report['test_summary']['disease_tests_passed']}/{report['test_summary']['total_disease_tests']} passed")
        print(f"Other Endpoints Tested: {report['test_summary']['other_endpoints_tested']}")
        
        if report['recommendations']:
            print("\n📋 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        # Save report
        with open('ai_endpoints_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: ai_endpoints_test_report.json")
        
        return report

def main():
    """Main function"""
    tester = AIDiseaseDetectionTester()
    report = tester.run_comprehensive_test()
    
    # Return success if all disease detection tests passed
    disease_success = report['test_summary']['disease_tests_passed'] == report['test_summary']['total_disease_tests']
    
    if disease_success:
        print("\n🎉 SUCCESS: All disease detection tests passed!")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the report for details.")
        return False

if __name__ == "__main__":
    main()
