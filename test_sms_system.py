"""
Simple SMS System Test - Validates SMS endpoints are working
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_sms_endpoints():
    """Test SMS endpoints"""
    print("🚀 Testing SMS Endpoints")
    print("=" * 50)
    
    # Test 1: SMS Test Endpoint
    print("\n📱 Testing SMS Test Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sms/sms/test/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ SMS Test Endpoint: WORKING")
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Supported Commands: {len(data.get('supported_commands', []))}")
        else:
            print(f"❌ SMS Test Endpoint: FAILED (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ SMS Test Endpoint: ERROR - {str(e)}")
    
    # Test 2: USSD Test Endpoint
    print("\n📞 Testing USSD Test Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sms/ussd/test/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ USSD Test Endpoint: WORKING")
            print(f"   Service: {data.get('service')}")
            print(f"   USSD Code: {data.get('ussd_code')}")
            print(f"   Menu Options: {len(data.get('menu_structure', {}))}")
        else:
            print(f"❌ USSD Test Endpoint: FAILED (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ USSD Test Endpoint: ERROR - {str(e)}")
    
    # Test 3: SMS Command Test
    print("\n💬 Testing SMS Command Processing...")
    try:
        test_data = {
            'phone_number': '+233123456789',
            'message': 'HELP'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/sms/sms/test/",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ SMS Command Processing: WORKING")
                print(f"   Response: {data.get('response_message')[:50]}...")
            else:
                print(f"❌ SMS Command Processing: FAILED - {data.get('error')}")
        else:
            print(f"❌ SMS Command Processing: FAILED (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"❌ SMS Command Processing: ERROR - {str(e)}")
    
    # Test 4: USSD Session Test
    print("\n🎯 Testing USSD Session Handling...")
    try:
        test_data = {
            'sessionId': 'test-session-123',
            'serviceCode': '*123#',
            'phoneNumber': '+233123456789',
            'text': ''
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/sms/ussd/test/",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ USSD Session Handling: WORKING")
                print(f"   Response: {data.get('response')[:50]}...")
            else:
                print(f"❌ USSD Session Handling: FAILED - {data.get('error')}")
        else:
            print(f"❌ USSD Session Handling: FAILED (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"❌ USSD Session Handling: ERROR - {str(e)}")
    
    # Test 5: Analytics
    print("\n📊 Testing SMS Analytics...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sms/analytics/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ SMS Analytics: WORKING")
            print(f"   Total SMS Users: {data.get('sms_analytics', {}).get('total_sms_users', 0)}")
            print(f"   Supported Countries: {len(data.get('supported_countries', []))}")
        else:
            print(f"❌ SMS Analytics: FAILED (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ SMS Analytics: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 SMS System Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_sms_endpoints()
