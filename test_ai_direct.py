#!/usr/bin/env python3
"""
Direct AI API Test using Django Test Client
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_ai_endpoints_direct():
    print("🤖 Testing AI API Endpoints with Django Test Client...")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Get or create test user
    try:
        user, created = User.objects.get_or_create(
            username='aitest',
            defaults={
                'email': 'aitest@example.com',
                'first_name': 'AI',
                'last_name': 'Tester'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Using existing user: {user.username}")
        
        # Get JWT token
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        print(f"✅ Generated JWT token")
        
        # Headers for authentication
        headers = {
            'HTTP_AUTHORIZATION': f'Bearer {token}',
            'CONTENT_TYPE': 'application/json'
        }
        
        # Test results
        results = []
        
        # Test 1: Health Check
        print("\n1️⃣ Testing Health Check...")
        response = client.get('/api/v1/ai/api/health/', **headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data}")
            results.append(('health_check', True))
        else:
            print(f"   ❌ FAILED: {response.content.decode()}")
            results.append(('health_check', False))
        
        # Test 2: Chat (AgriBot)
        print("\n2️⃣ Testing AgriBot Chat...")
        chat_data = {
            'message': 'Hello! I need help with maize farming in Ghana.',
            'language': 'en'
        }
        response = client.post(
            '/api/v1/ai/api/chat/',
            data=json.dumps(chat_data),
            **headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS")
            print(f"   📝 Response: {data.get('response', 'No response')[:100]}...")
            results.append(('conversation', True))
        else:
            print(f"   ❌ FAILED: {response.content.decode()[:200]}")
            results.append(('conversation', False))
        
        # Test 3: Crop Advisory
        print("\n3️⃣ Testing Crop Advisory...")
        crop_data = {
            'crop_type': 'maize',
            'farming_stage': 'planting',
            'location': 'Ghana',
            'season': 'rainy'
        }
        response = client.post(
            '/api/v1/ai/api/crop-advisory/',
            data=json.dumps(crop_data),
            **headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS")
            print(f"   📝 Advice: {data.get('advice', 'No advice')[:100]}...")
            results.append(('crop_advisory', True))
        else:
            print(f"   ❌ FAILED: {response.content.decode()[:200]}")
            results.append(('crop_advisory', False))
        
        # Test 4: Disease Detection
        print("\n4️⃣ Testing Disease Detection...")
        disease_data = {
            'crop_type': 'tomato',
            'symptoms': 'Yellow leaves with brown spots, wilting plants',
            'location': 'Ghana'
        }
        response = client.post(
            '/api/v1/ai/api/disease-detection/',
            data=json.dumps(disease_data),
            **headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS")
            print(f"   📝 Diagnosis: {data.get('diagnosis', 'No diagnosis')[:100]}...")
            results.append(('disease_detection', True))
        else:
            print(f"   ❌ FAILED: {response.content.decode()[:200]}")
            results.append(('disease_detection', False))
        
        # Test 5: Market Intelligence
        print("\n5️⃣ Testing Market Intelligence...")
        market_data = {
            'crop_type': 'cocoa',
            'location': 'Ghana',
            'market_type': 'export'
        }
        response = client.post(
            '/api/v1/ai/api/market-intelligence/',
            data=json.dumps(market_data),
            **headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS")
            print(f"   📝 Intelligence: {data.get('intelligence', 'No intelligence')[:100]}...")
            results.append(('market_intelligence', True))
        else:
            print(f"   ❌ FAILED: {response.content.decode()[:200]}")
            results.append(('market_intelligence', False))
        
        # Summary
        print("\n" + "=" * 60)
        print("🌾 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for _, success in results if success)
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
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {name}: {status}")
        
        if passed == total:
            print("\n⚠️  Some endpoints need attention.")
            print("🔧 Please check the Django logs for more details.")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_endpoints_direct()
    
    if success:
        print("\n🎉 AI API Implementation Complete!")
        print("✅ Ready for production deployment!")
    else:
        print("\n🔧 Debugging needed for failing endpoints.")
