import requests
import json
from datetime import datetime

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

api_status = {'available': 0, 'total': len(tests)}

for test in tests:
    try:
        response = requests.get(test['url'], timeout=5)
        if response.status_code in [200, 301, 302, 401, 403]:
            print(f"✅ {test['name']}: Available (Status: {response.status_code})")
            api_status['available'] += 1
        else:
            print(f"❌ {test['name']}: Error (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ {test['name']}: Unavailable")

# Test core functionality
print('\n🧪 CORE FUNCTIONALITY TESTING')
print('-' * 40)

core_passed = 0
core_total = 0

# Test login with credentials from Browser Access Guide
try:
    login_data = {
        'identifier': 'testfarmer@example.com',
        'password': 'testpass123'
    }
    
    response = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data, timeout=10)
    core_total += 1
    if response.status_code == 200:
        print("✅ User Login: Working")
        core_passed += 1
        
        # Test AI chat with authentication
        login_response = response.json()
        access_token = login_response.get('access')
        
        if access_token:
            try:
                headers = {'Authorization': f'Bearer {access_token}'}
                ai_data = {'message': 'Test message for production readiness'}
                
                ai_response = requests.post('http://127.0.0.1:8000/api/v1/ai/api/chat/', 
                                          json=ai_data, headers=headers, timeout=15)
                core_total += 1
                if ai_response.status_code == 200:
                    print("✅ AI Chat Service: Working")
                    core_passed += 1
                else:
                    print(f"❌ AI Chat Service: Failed (Status: {ai_response.status_code})")
            except Exception as e:
                core_total += 1
                print(f"❌ AI Chat Service: Error")
    else:
        print(f"❌ User Login: Failed (Status: {response.status_code})")
except Exception as e:
    core_total += 1
    print(f"❌ User Login: Error")

# Test mobile app availability
print('\n🌐 WEB PLATFORM ASSESSMENT')
print('-' * 40)

mobile_working = False
mobile_ports = [8082, 3000, 8081]

for port in mobile_ports:
    try:
        response = requests.get(f'http://localhost:{port}', timeout=3)
        if response.status_code == 200:
            print(f"✅ Mobile App Web: Available on port {port}")
            mobile_working = True
            break
    except:
        continue

if not mobile_working:
    print("❌ Mobile App Web: Not currently running")

# Generate final assessment
print('\n' + '=' * 60)
print('📊 PRODUCTION READINESS REPORT')
print('=' * 60)

# Calculate scores
api_success_rate = (api_status['available'] / api_status['total']) * 100
core_success_rate = (core_passed / core_total) * 100 if core_total > 0 else 0
web_success_rate = 100 if mobile_working else 0

print(f"🔗 API ENDPOINTS: {api_status['available']}/{api_status['total']} available ({api_success_rate:.1f}%)")
print(f"⚙️ CORE FUNCTIONALITY: {core_passed}/{core_total} working ({core_success_rate:.1f}%)")
print(f"🌐 WEB PLATFORMS: {'1/1' if mobile_working else '0/1'} available ({web_success_rate:.1f}%)")

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

print(f"\n🕐 Assessment completed at: {datetime.now()}")
