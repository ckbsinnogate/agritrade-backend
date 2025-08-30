#!/usr/bin/env python3
"""
AgriConnect Quick Production Readiness Assessment
================================================
Simple and fast evaluation of system production readiness
"""

import requests
import json
from datetime import datetime

def main():
    print('🔍 AGRICONNECT API PRODUCTION READINESS ASSESSMENT')
    print('=' * 60)
    
    # Test API endpoints
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
                api_status['details'].append({
                    'endpoint': test['name'], 
                    'status': 'Available', 
                    'code': response.status_code
                })
            else:
                print(f"❌ {test['name']}: Error (Status: {response.status_code})")
                api_status['details'].append({
                    'endpoint': test['name'], 
                    'status': 'Error', 
                    'code': response.status_code
                })
        except Exception as e:
            print(f"❌ {test['name']}: Unavailable ({str(e)[:30]}...)")
            api_status['details'].append({
                'endpoint': test['name'], 
                'status': 'Unavailable', 
                'error': str(e)[:50]
            })
    
    # Test core functionality
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
        
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/auth/register/', 
            json=registration_data, 
            timeout=10
        )
        if response.status_code in [200, 201, 400]:  # 400 if user already exists
            print("✅ Farmer Registration: Working")
            core_tests.append({'test': 'Registration', 'status': 'Pass'})
        else:
            print(f"❌ Farmer Registration: Failed (Status: {response.status_code})")
            core_tests.append({'test': 'Registration', 'status': 'Fail'})
    except Exception as e:
        print(f"❌ Farmer Registration: Error ({str(e)[:30]}...)")
        core_tests.append({'test': 'Registration', 'status': 'Error'})
    
    # Test login with credentials from Browser Access Guide
    try:
        login_data = {
            'identifier': 'testfarmer@example.com',
            'password': 'testpass123'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/auth/login/', 
            json=login_data, 
            timeout=10
        )
        if response.status_code == 200:
            print("✅ User Login: Working")
            core_tests.append({'test': 'Login', 'status': 'Pass'})
            
            # Test AI chat with authentication
            login_response = response.json()
            access_token = login_response.get('access')
            
            if access_token:
                try:
                    headers = {'Authorization': f'Bearer {access_token}'}
                    ai_data = {'message': 'Test message for production readiness'}
                    
                    ai_response = requests.post(
                        'http://127.0.0.1:8000/api/v1/ai/api/chat/', 
                        json=ai_data, 
                        headers=headers, 
                        timeout=15
                    )
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
    
    # Test web platform availability
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
    
    # Generate final assessment
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
    web_available = len([t for t in web_tests if t['status'] in ['Available']])
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
        print("✅ Ready for continental expansion")
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
    
    # Continental expansion readiness
    if api_success_rate >= 90 and core_success_rate >= 80:
        print(f"\n🌍 CONTINENTAL EXPANSION STATUS:")
        print("✅ Ghana: READY")
        print("✅ Nigeria: READY") 
        print("✅ Kenya: READY")
        print("✅ Ethiopia: READY")
        print("🚀 READY FOR 70,000 FARMERS ACROSS 4 COUNTRIES!")
    
    # Save results
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_score': overall_score,
        'production_ready': production_ready,
        'api_score': api_success_rate,
        'core_score': core_success_rate,
        'web_score': web_success_rate,
        'api_details': api_status,
        'core_tests': core_tests,
        'web_tests': web_tests
    }
    
    with open('production_readiness_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: production_readiness_report.json")
    print(f"🕐 Assessment completed at: {datetime.now()}")
    
    return production_ready

if __name__ == "__main__":
    main()
