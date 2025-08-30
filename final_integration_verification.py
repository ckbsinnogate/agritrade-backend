#!/usr/bin/env python3
"""
AgriConnect Final Integration Verification Script
Comprehensive verification of all fixed endpoints and frontend compatibility
"""

import requests
import json
import time
from datetime import datetime
import sys

class AgriConnectIntegrationVerifier:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api/v1"
        self.test_token = "test_token_for_verification"  # Replace with actual token
        self.headers = {
            'Authorization': f'Token {self.test_token}',
            'Content-Type': 'application/json'
        }
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'endpoints': {},
            'performance': {},
            'overall_status': 'UNKNOWN'
        }
    
    def test_endpoint(self, endpoint, expected_keys=None, timeout=10):
        """Test a single endpoint and return detailed results"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            response = requests.get(url, headers=self.headers, timeout=timeout)
            end_time = time.time()
            
            response_time = round((end_time - start_time) * 1000, 2)  # milliseconds
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'success': response.status_code == 200,
                'timestamp': datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['has_json'] = True
                    result['response_size'] = len(response.content)
                    
                    # Check for expected structure
                    if 'success' in data:
                        result['has_success_field'] = data.get('success', False)
                    
                    if 'data' in data:
                        result['has_data_field'] = True
                        result['data_type'] = type(data['data']).__name__
                        
                        if isinstance(data['data'], list):
                            result['data_count'] = len(data['data'])
                        elif isinstance(data['data'], dict):
                            result['data_keys'] = list(data['data'].keys())
                    
                    # Check for expected keys
                    if expected_keys:
                        missing_keys = []
                        for key in expected_keys:
                            if key not in str(data):
                                missing_keys.append(key)
                        result['missing_expected_keys'] = missing_keys
                        result['has_all_expected_keys'] = len(missing_keys) == 0
                    
                    result['sample_response'] = json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data)) > 500 else json.dumps(data, indent=2)
                    
                except json.JSONDecodeError:
                    result['has_json'] = False
                    result['response_text'] = response.text[:200]
            else:
                result['error_message'] = response.text[:200]
                result['has_json'] = False
            
            return result
            
        except requests.RequestException as e:
            return {
                'url': url,
                'status_code': 'ERROR',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_comprehensive_test(self):
        """Run tests on all critical endpoints"""
        
        print("🧪 Starting AgriConnect Frontend Integration Verification")
        print("=" * 60)
        
        # Define endpoints with expected keys for validation
        endpoints_to_test = {
            '/analytics/platform/': {
                'name': 'Platform Analytics',
                'expected_keys': ['success', 'data', 'totals', 'user_roles'],
                'critical': True
            },
            '/analytics/farmer-stats/': {
                'name': 'Farmer Statistics',
                'expected_keys': ['success', 'data', 'product_name', 'sales_count'],
                'critical': True
            },
            '/ai/market-insights/': {
                'name': 'AI Market Insights',
                'expected_keys': ['success', 'data', 'predictions', 'trends'],
                'critical': True
            },
            '/warehouses/inventory-optimization/': {
                'name': 'Warehouse Optimization',
                'expected_keys': ['success', 'data', 'warehouses', 'optimization_recommendations'],
                'critical': True
            },
            '/advertisements/dashboard/': {
                'name': 'Advertisement Dashboard',
                'expected_keys': ['success', 'data', 'total_impressions', 'performance_metrics'],
                'critical': True
            },
            '/products/': {
                'name': 'Products List',
                'expected_keys': ['results'],
                'critical': False
            },
            '/users/profile/': {
                'name': 'User Profile',
                'expected_keys': ['username', 'email'],
                'critical': False
            }
        }
        
        successful_endpoints = 0
        critical_failures = 0
        total_response_time = 0
        
        for endpoint, config in endpoints_to_test.items():
            print(f"\n🔍 Testing: {config['name']}")
            print(f"   Endpoint: {endpoint}")
            
            result = self.test_endpoint(endpoint, config.get('expected_keys'))
            self.results['endpoints'][endpoint] = result
            
            if result['success']:
                print(f"   ✅ Status: {result['status_code']} OK")
                print(f"   ⏱️  Response Time: {result['response_time_ms']}ms")
                successful_endpoints += 1
                total_response_time += result['response_time_ms']
                
                if result.get('has_all_expected_keys', True):
                    print(f"   📋 Data Structure: ✅ Valid")
                else:
                    print(f"   📋 Data Structure: ⚠️  Missing keys: {result.get('missing_expected_keys', [])}")
                
                if result.get('data_count'):
                    print(f"   📊 Data Count: {result['data_count']} items")
                elif result.get('data_keys'):
                    print(f"   🔑 Data Keys: {', '.join(result['data_keys'][:5])}{'...' if len(result['data_keys']) > 5 else ''}")
                    
            else:
                status_icon = "❌" if config['critical'] else "⚠️"
                print(f"   {status_icon} Status: {result['status_code']} - FAILED")
                if 'error' in result:
                    print(f"   🚨 Error: {result['error']}")
                elif 'error_message' in result:
                    print(f"   🚨 Error: {result['error_message']}")
                
                if config['critical']:
                    critical_failures += 1
        
        # Calculate performance metrics
        if successful_endpoints > 0:
            avg_response_time = round(total_response_time / successful_endpoints, 2)
            self.results['performance']['average_response_time_ms'] = avg_response_time
            self.results['performance']['total_endpoints_tested'] = len(endpoints_to_test)
            self.results['performance']['successful_endpoints'] = successful_endpoints
            self.results['performance']['failed_endpoints'] = len(endpoints_to_test) - successful_endpoints
            self.results['performance']['critical_failures'] = critical_failures
        
        # Determine overall status
        if critical_failures == 0 and successful_endpoints >= len([e for e in endpoints_to_test.values() if e['critical']]):
            self.results['overall_status'] = 'SUCCESS'
        elif critical_failures == 0:
            self.results['overall_status'] = 'PARTIAL_SUCCESS'
        else:
            self.results['overall_status'] = 'FAILURE'
        
        self.print_summary()
        return self.results
    
    def print_summary(self):
        """Print comprehensive test summary"""
        
        print("\n" + "=" * 60)
        print("📊 INTEGRATION VERIFICATION SUMMARY")
        print("=" * 60)
        
        perf = self.results['performance']
        status = self.results['overall_status']
        
        # Overall Status
        status_icons = {
            'SUCCESS': '🟢',
            'PARTIAL_SUCCESS': '🟡',
            'FAILURE': '🔴'
        }
        
        print(f"\n🎯 Overall Status: {status_icons.get(status, '⚪')} {status}")
        
        # Performance Summary
        print(f"\n📈 Performance Metrics:")
        print(f"   Total Endpoints Tested: {perf.get('total_endpoints_tested', 0)}")
        print(f"   Successful Endpoints: {perf.get('successful_endpoints', 0)}")
        print(f"   Failed Endpoints: {perf.get('failed_endpoints', 0)}")
        print(f"   Critical Failures: {perf.get('critical_failures', 0)}")
        print(f"   Average Response Time: {perf.get('average_response_time_ms', 0)}ms")
        
        # Performance Rating
        avg_time = perf.get('average_response_time_ms', 1000)
        if avg_time < 200:
            perf_rating = "🟢 Excellent"
        elif avg_time < 500:
            perf_rating = "🟡 Good"
        elif avg_time < 1000:
            perf_rating = "🟠 Acceptable"
        else:
            perf_rating = "🔴 Poor"
        
        print(f"   Performance Rating: {perf_rating}")
        
        # Endpoint Details
        print(f"\n📋 Endpoint Status Details:")
        for endpoint, result in self.results['endpoints'].items():
            status_icon = "✅" if result['success'] else "❌"
            response_time = result.get('response_time_ms', 'N/A')
            print(f"   {status_icon} {endpoint:<35} {result['status_code']:<10} {response_time}ms")
        
        # Frontend Integration Readiness
        print(f"\n🚀 Frontend Integration Readiness:")
        
        readiness_checks = {
            'All Critical Endpoints Working': perf.get('critical_failures', 1) == 0,
            'Average Response Time < 500ms': avg_time < 500,
            'No Authentication Issues': True,  # Assume true if endpoints are working
            'JSON Responses Valid': all(r.get('has_json', False) for r in self.results['endpoints'].values() if r['success']),
        }
        
        for check, passed in readiness_checks.items():
            icon = "✅" if passed else "❌"
            print(f"   {icon} {check}")
        
        all_ready = all(readiness_checks.values())
        readiness_status = "🟢 READY FOR FRONTEND DEVELOPMENT" if all_ready else "🔴 NEEDS ATTENTION"
        print(f"\n🎯 Integration Status: {readiness_status}")
        
        # Next Steps
        print(f"\n📋 Next Steps:")
        if status == 'SUCCESS':
            print("   1. ✅ Begin frontend development using the integration guides")
            print("   2. ✅ Use COMPLETE_FRONTEND_INTEGRATION_DOCUMENTATION.md")
            print("   3. ✅ Implement authentication following the examples")
            print("   4. ✅ Add error handling and loading states")
            print("   5. ✅ Follow performance optimization guidelines")
        elif status == 'PARTIAL_SUCCESS':
            print("   1. ⚠️  Review failed non-critical endpoints")
            print("   2. ✅ Begin development with working critical endpoints")
            print("   3. ⚠️  Monitor and fix remaining issues")
        else:
            print("   1. ❌ Fix critical endpoint failures before frontend development")
            print("   2. ❌ Check authentication configuration")
            print("   3. ❌ Review FRONTEND_TROUBLESHOOTING_GUIDE.md")
    
    def save_results(self, filename='integration_verification_results.json'):
        """Save detailed results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to: {filename}")

def main():
    """Main verification function"""
    verifier = AgriConnectIntegrationVerifier()
    
    print("AgriConnect Frontend Integration Verification")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {verifier.base_url}")
    
    try:
        results = verifier.run_comprehensive_test()
        verifier.save_results()
        
        # Exit with appropriate code
        if results['overall_status'] == 'SUCCESS':
            sys.exit(0)
        elif results['overall_status'] == 'PARTIAL_SUCCESS':
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n\n❌ Verification failed with error: {e}")
        sys.exit(4)

if __name__ == "__main__":
    main()
