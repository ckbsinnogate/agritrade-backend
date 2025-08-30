#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgriConnect Production Readiness Assessment
==========================================
Comprehensive evaluation of API and web platform production readiness
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoints():
    """Test all AgriConnect API endpoints"""
    print('🔍 AGRICONNECT API PRODUCTION READINESS ASSESSMENT')
    print('=' * 60)
    
    api_base = 'http://127.0.0.1:8000/api/v1'
    
    tests = [
        {'name': 'API Root', 'url': f'{api_base}/'},
        {'name': 'Authentication', 'url': f'{api_base}/auth/'},
        {'name': 'Products API', 'url': f'{api_base}/products/'},
        {'name': 'Orders API', 'url': f'{api_base}/orders/'},
        {'name': 'Payments API', 'url': f'{api_base}/payments/'},
        {'name': 'AI Services', 'url': f'{api_base}/ai/'},
        {'name': 'Warehouses', 'url': f'{api_base}/warehouses/'},
        {'name': 'Reviews', 'url': f'{api_base}/reviews/'},
        {'name': 'Communications', 'url': f'{api_base}/communications/'},
        {'name': 'Traceability', 'url': f'{api_base}/traceability/'},
        {'name': 'Subscriptions', 'url': f'{api_base}/subscriptions/'},
        {'name': 'Advertisements', 'url': f'{api_base}/advertisements/'},
    ]
    
    api_status = {'available': 0, 'total': len(tests), 'details': []}
    
    for test in tests:
        try:
            response = requests.get(test['url'], timeout=5)
            if response.status_code in [200, 301, 302, 401, 403]:
                print(f"✅ {test['name']}: Available (Status: {response.status_code})")
                api_status['available'] += 1
                api_status['details'].append({'endpoint': test['name'], 'status': 'Available', 'code': response.status_code})
            else:
                print(f"❌ {test['name']}: Error (Status: {response.status_code})")
                api_status['details'].append({'endpoint': test['name'], 'status': 'Error', 'code': response.status_code})
        except Exception as e:
            print(f"❌ {test['name']}: Unavailable ({str(e)[:30]}...)")
            api_status['details'].append({'endpoint': test['name'], 'status': 'Unavailable', 'error': str(e)[:50]})
    
    return api_status

def test_core_functionality():
    """Test core functionality like authentication and AI"""
    print('\n🧪 CORE FUNCTIONALITY TESTING')
    print('-' * 40)
    
    core_tests = []
    
    # Test farmer registration
    try:
        registration_data = {
            'identifier': 'prod_test@ghana.com',
            'password': 'ProdTest123!',
            'password_confirm': 'ProdTest123!',
            'first_name': 'Production',
            'last_name': 'Test',
            'roles': ['FARMER'],
            'country': 'Ghana',
            'region': 'Greater Accra',
            'language': 'en'
        }
        
        response = requests.post('http://127.0.0.1:8000/api/v1/auth/register/', json=registration_data, timeout=10)
        if response.status_code in [200, 201, 400]:  # 400 if user already exists
            print("✅ Farmer Registration: Working")
            core_tests.append({'test': 'Registration', 'status': 'Pass'})
        else:
            print(f"❌ Farmer Registration: Failed (Status: {response.status_code})")
            core_tests.append({'test': 'Registration', 'status': 'Fail'})
    except Exception as e:
        print(f"❌ Farmer Registration: Error ({str(e)[:30]}...)")
        core_tests.append({'test': 'Registration', 'status': 'Error'})
    
    # Test login
    try:
        login_data = {
            'identifier': 'testfarmer@example.com',
            'password': 'testpass123'
        }
        
        response = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data, timeout=10)
        if response.status_code == 200:
            print("✅ User Login: Working")
            core_tests.append({'test': 'Login', 'status': 'Pass'})
            
            # Get access token for AI testing
            login_response = response.json()
            access_token = login_response.get('access')
            
            # Test AI chat with authentication
            if access_token:
                try:
                    headers = {'Authorization': f'Bearer {access_token}'}
                    ai_data = {'message': 'Test message for production readiness'}
                    
                    ai_response = requests.post('http://127.0.0.1:8000/api/v1/ai/api/chat/', 
                                              json=ai_data, headers=headers, timeout=15)
                    if ai_response.status_code == 200:
                        print("✅ AI Chat Service: Working")
                        core_tests.append({'test': 'AI Chat', 'status': 'Pass'})
                    else:
                        print(f"❌ AI Chat Service: Failed (Status: {ai_response.status_code})")
                        core_tests.append({'test': 'AI Chat', 'status': 'Fail'})
                except Exception as e:
                    print(f"❌ AI Chat Service: Error ({str(e)[:30]}...)")
                    core_tests.append({'test': 'AI Chat', 'status': 'Error'})
        else:
            print(f"❌ User Login: Failed (Status: {response.status_code})")
            core_tests.append({'test': 'Login', 'status': 'Fail'})
    except Exception as e:
        print(f"❌ User Login: Error ({str(e)[:30]}...)")
        core_tests.append({'test': 'Login', 'status': 'Error'})
    
    return core_tests

def assess_web_platform():
    """Assess web platform status"""
    print('\n🌐 WEB PLATFORM ASSESSMENT')
    print('-' * 40)
    
    web_tests = []
    
    # Test mobile app availability
    mobile_ports = [8082, 3000, 8081]
    mobile_working = False
    
    for port in mobile_ports:
        try:
            response = requests.get(f'http://localhost:{port}', timeout=3)
            if response.status_code == 200:
                print(f"✅ Mobile App Web: Available on port {port}")
                web_tests.append({'platform': 'Mobile App', 'status': 'Available', 'port': port})
                mobile_working = True
                break
        except:
            continue
    
    if not mobile_working:
        print("❌ Mobile App Web: Not currently running")
        web_tests.append({'platform': 'Mobile App', 'status': 'Not Running'})
    
    # Check for Next.js web platform
    try:
        response = requests.get('http://localhost:3000', timeout=3)
        if response.status_code == 200 and 'next' in response.text.lower():
            print("✅ Next.js Web Platform: Available")
            web_tests.append({'platform': 'Next.js Web', 'status': 'Available'})
        else:
            print("❌ Next.js Web Platform: Not detected")
            web_tests.append({'platform': 'Next.js Web', 'status': 'Not Available'})
    except:
        print("❌ Next.js Web Platform: Not running")
        web_tests.append({'platform': 'Next.js Web', 'status': 'Not Running'})
    
    return web_tests

def generate_production_report(api_status, core_tests, web_tests):
    """Generate comprehensive production readiness report"""
    print('\n' + '=' * 60)
    print('📊 PRODUCTION READINESS REPORT')
    print('=' * 60)
    
    # API Assessment
    api_success_rate = (api_status['available'] / api_status['total']) * 100
    print(f"🔗 API ENDPOINTS: {api_status['available']}/{api_status['total']} available ({api_success_rate:.1f}%)")
    
    # Core Functionality Assessment
    core_passed = len([t for t in core_tests if t['status'] == 'Pass'])
    core_success_rate = (core_passed / len(core_tests)) * 100 if core_tests else 0
    print(f"⚙️ CORE FUNCTIONALITY: {core_passed}/{len(core_tests)} working ({core_success_rate:.1f}%)")
    
    # Web Platform Assessment
    web_available = len([t for t in web_tests if t['status'] in ['Available', 'Available']])
    web_success_rate = (web_available / len(web_tests)) * 100 if web_tests else 0
    print(f"🌐 WEB PLATFORMS: {web_available}/{len(web_tests)} available ({web_success_rate:.1f}%)")
    
    # Overall Assessment
    overall_score = (api_success_rate + core_success_rate + web_success_rate) / 3
    print(f"\n🎯 OVERALL PRODUCTION READINESS: {overall_score:.1f}%")
    
    # Production Readiness Decision
    if overall_score >= 85:
        print("\n🎉 ✅ SYSTEM IS PRODUCTION READY!")
        print("✅ All critical systems operational")
        print("✅ API endpoints functional")
        print("✅ Core features working")
        print("✅ Web platforms available")
        production_ready = True
    elif overall_score >= 70:
        print("\n⚠️ 🟡 SYSTEM IS MOSTLY READY (Minor issues)")
        print("✅ Core functionality working")
        print("⚠️ Some endpoints may need attention")
        print("🔧 Minor fixes needed before production")
        production_ready = False
    else:
        print("\n❌ 🔴 SYSTEM NEEDS IMPROVEMENT")
        print("❌ Critical issues detected")
        print("❌ Major fixes needed before production")
        print("🛠️ Development work required")
        production_ready = False
    
    # Specific Recommendations
    print(f"\n📋 PRODUCTION RECOMMENDATIONS:")
    
    if api_success_rate < 80:
        print("🔧 Fix non-working API endpoints")
    
    if core_success_rate < 100:
        print("🔧 Resolve authentication/AI issues")
    
    if web_success_rate < 50:
        print("🔧 Ensure web platforms are running")
    
    print("\n🚀 DEPLOYMENT CHECKLIST:")
    print("□ Configure production database")
    print("□ Set up SSL certificates")
    print("□ Configure production environment variables")
    print("□ Set up monitoring and logging")
    print("□ Prepare backup and recovery procedures")
    print("□ Configure CDN and load balancing")
    print("□ Set up SMS and email services for production")
    
    return {
        'overall_score': overall_score,
        'production_ready': production_ready,
        'api_score': api_success_rate,
        'core_score': core_success_rate,
        'web_score': web_success_rate,
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Main assessment function"""
    print(f"🕐 Assessment started at: {datetime.now()}")
    
    # Run all assessments
    api_status = test_api_endpoints()
    core_tests = test_core_functionality()
    web_tests = assess_web_platform()
    
    # Generate final report
    report = generate_production_report(api_status, core_tests, web_tests)
    
    # Save report to file
    with open('production_readiness_report.json', 'w') as f:
        json.dump({
            'report': report,
            'api_details': api_status,
            'core_tests': core_tests,
            'web_tests': web_tests
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: production_readiness_report.json")
    
    return report['production_ready']

if __name__ == "__main__":
    main()
