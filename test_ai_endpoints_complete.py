#!/usr/bin/env python3
"""
Test AI API Endpoints - Complete Validation
"""

import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_auth_token():
    """Get authentication token for testing"""
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found. Creating test user...")
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
        
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        return None

def test_ai_endpoints():
    """Test all AI endpoints"""
    print("🤖 Testing AI API Endpoints...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000/api/v1/ai/api"
    
    # Get auth token
    token = get_auth_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}' if token else ''
    }
    
    # Test endpoints
    endpoints = [
        {
            'name': 'Health Check',
            'url': f'{base_url}/health/',
            'method': 'GET',
            'data': None
        },
        {
            'name': 'Chat (AgriBot)',
            'url': f'{base_url}/chat/',
            'method': 'POST',
            'data': {
                'message': 'Hello! I need help with maize farming in Ghana.',
                'language': 'en'
            }
        },
        {
            'name': 'Crop Advisory',
            'url': f'{base_url}/crop-advisory/',
            'method': 'POST',
            'data': {
                'crop_type': 'maize',
                'farming_stage': 'planting',
                'location': 'Ghana',
                'season': 'rainy',
                'specific_question': 'What is the best planting spacing for maize?'
            }
        },
        {
            'name': 'Disease Detection',
            'url': f'{base_url}/disease-detection/',
            'method': 'POST',
            'data': {
                'crop_type': 'tomato',
                'symptoms': 'Yellow leaves with brown spots, wilting',
                'location': 'Ghana'
            }
        },
        {
            'name': 'Market Intelligence',
            'url': f'{base_url}/market-intelligence/',
            'method': 'POST',
            'data': {
                'crop_type': 'cocoa',
                'location': 'Ghana',
                'market_type': 'export'
            }
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint['name']}...")
        print(f"   URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers)
            else:
                response = requests.post(
                    endpoint['url'], 
                    headers=headers, 
                    data=json.dumps(endpoint['data'])
                )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS")
                try:
                    data = response.json()
                    if 'response' in data:
                        print(f"   📝 Response: {data['response'][:100]}...")
                    elif 'advice' in data:
                        print(f"   📝 Advice: {data['advice'][:100]}...")
                    elif 'diagnosis' in data:
                        print(f"   📝 Diagnosis: {data['diagnosis'][:100]}...")
                    elif 'intelligence' in data:
                        print(f"   📝 Intelligence: {data['intelligence'][:100]}...")
                    else:
                        print(f"   📝 Data: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   📝 Raw: {response.text[:100]}...")
                results.append(True)
            else:
                print(f"   ❌ FAILED")
                print(f"   📝 Error: {response.text[:200]}...")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("🌾 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"📊 Tests Passed: {passed}/{total}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! AI API is working perfectly!")
    elif passed > 0:
        print("⚠️  Some tests passed. AI API is partially working.")
    else:
        print("❌ All tests failed. Please check the implementation.")
    
    print("\n🔍 Individual Results:")
    for i, (endpoint, result) in enumerate(zip(endpoints, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {endpoint['name'].lower().replace(' ', '_')}: {status}")
    
    return passed == total

if __name__ == "__main__":
    success = test_ai_endpoints()
    
    if success:
        print("\n🎉 AI API Implementation Complete!")
        print("✅ Ready for production deployment!")
    else:
        print("\n⚠️  Some endpoints need attention.")
        print("🔧 Please check the Django logs for more details.")
