#!/usr/bin/env python3
"""
Test AI endpoints with authentication to identify 400 error causes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_auth_token():
    """Get authentication token for testing"""
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            email='test400@example.com',
            defaults={
                'first_name': 'Test400',
                'last_name': 'User',
                'phone_number': '+233123456789',
                'is_active': True
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            print(f"✅ Created test user: {user.email}")
        else:
            print(f"✅ Using existing user: {user.email}")
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
        
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        return None

def test_authenticated_requests():
    """Test authenticated requests to identify 400 errors"""
    print("🔐 TESTING WITH AUTHENTICATION - 400 ERROR INVESTIGATION")
    print("=" * 65)
    
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Test cases that frontend might send
    test_cases = [
        # Disease Detection Tests
        {
            'name': 'Disease Detection - Empty Data (Frontend Issue)',
            'url': 'http://127.0.0.1:8000/api/v1/ai/disease-detection/',
            'data': {}
        },
        {
            'name': 'Disease Detection - Missing Symptoms',
            'url': 'http://127.0.0.1:8000/api/v1/ai/disease-detection/',
            'data': {'crop_type': 'maize'}
        },
        {
            'name': 'Disease Detection - Empty Symptoms Array',
            'url': 'http://127.0.0.1:8000/api/v1/ai/disease-detection/',
            'data': {'crop_type': 'maize', 'symptoms': []}
        },
        {
            'name': 'Disease Detection - Invalid Symptoms Format',
            'url': 'http://127.0.0.1:8000/api/v1/ai/disease-detection/',
            'data': {'crop_type': 'maize', 'symptoms': 'yellowing'}
        },
        {
            'name': 'Disease Detection - Valid Data',
            'url': 'http://127.0.0.1:8000/api/v1/ai/disease-detection/',
            'data': {'crop_type': 'maize', 'symptoms': ['yellowing_leaves']}
        },
        
        # Chat Tests
        {
            'name': 'Chat - Empty Data',
            'url': 'http://127.0.0.1:8000/api/v1/ai/chat/',
            'data': {}
        },
        {
            'name': 'Chat - Empty Message',
            'url': 'http://127.0.0.1:8000/api/v1/ai/chat/',
            'data': {'message': ''}
        },
        {
            'name': 'Chat - Valid Message',
            'url': 'http://127.0.0.1:8000/api/v1/ai/chat/',
            'data': {'message': 'Hello, I need farming advice'}
        },
        
        # Market Insights Tests
        {
            'name': 'Market Insights - Empty Data',
            'url': 'http://127.0.0.1:8000/api/v1/ai/market-insights/',
            'data': {}
        },
        {
            'name': 'Market Insights - Missing Location',
            'url': 'http://127.0.0.1:8000/api/v1/ai/market-insights/',
            'data': {'crop_type': 'maize'}
        },
        {
            'name': 'Market Insights - Valid Data',
            'url': 'http://127.0.0.1:8000/api/v1/ai/market-insights/',
            'data': {'crop_type': 'maize', 'location': 'Ghana'}
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print(f"   📍 URL: {test_case['url']}")
        print(f"   📨 Data: {json.dumps(test_case['data'])}")
        
        try:
            response = requests.post(
                test_case['url'], 
                json=test_case['data'], 
                headers=headers, 
                timeout=15
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 400:
                print(f"   ❌ 400 ERROR FOUND!")
                try:
                    error_data = response.json()
                    print(f"   📋 Error Details: {json.dumps(error_data, indent=4)}")
                except:
                    print(f"   📋 Raw Error: {response.text}")
                    
                results.append({
                    'test': test_case['name'],
                    'status': '400 BAD REQUEST',
                    'data_sent': test_case['data'],
                    'error_response': response.text
                })
                
            elif response.status_code == 200:
                print(f"   ✅ SUCCESS")
                try:
                    success_data = response.json()
                    print(f"   📋 Success Response: {success_data.get('message', 'Response received')}")
                except:
                    pass
                    
                results.append({
                    'test': test_case['name'],
                    'status': 'SUCCESS',
                    'data_sent': test_case['data']
                })
                
            else:
                print(f"   ⚠️  Other Status: {response.status_code}")
                print(f"   📋 Response: {response.text[:100]}")
                
                results.append({
                    'test': test_case['name'],
                    'status': f'HTTP {response.status_code}',
                    'data_sent': test_case['data']
                })
                
        except Exception as e:
            print(f"   ❌ Request Error: {e}")
            results.append({
                'test': test_case['name'],
                'status': 'REQUEST ERROR',
                'error': str(e)
            })
    
    # Analyze results
    print(f"\n🎯 ANALYSIS RESULTS")
    print("=" * 30)
    
    bad_requests = [r for r in results if r['status'] == '400 BAD REQUEST']
    successful = [r for r in results if r['status'] == 'SUCCESS']
    
    print(f"📊 Total Tests: {len(results)}")
    print(f"❌ 400 Errors: {len(bad_requests)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"⚠️  Other: {len(results) - len(bad_requests) - len(successful)}")
    
    if bad_requests:
        print(f"\n❌ 400 ERROR PATTERNS:")
        for result in bad_requests:
            print(f"   • {result['test']}")
            print(f"     Data: {result['data_sent']}")
    
    if successful:
        print(f"\n✅ SUCCESSFUL PATTERNS:")
        for result in successful:
            print(f"   • {result['test']}")
            print(f"     Data: {result['data_sent']}")
    
    # Generate frontend fixes
    print(f"\n🔧 FRONTEND FIXES NEEDED:")
    print("=" * 35)
    
    if any('Empty Data' in r['test'] for r in bad_requests):
        print("1. ❌ CRITICAL: Frontend sending empty objects {}")
        print("   Fix: Validate required fields before API calls")
    
    if any('Missing' in r['test'] for r in bad_requests):
        print("2. ❌ CRITICAL: Missing required fields")
        print("   Fix: Ensure all required fields are populated")
    
    if any('Empty' in r['test'] and 'Array' in r['test'] for r in bad_requests):
        print("3. ❌ CRITICAL: Empty arrays for required fields")
        print("   Fix: Validate arrays have at least one item")
    
    print(f"\n💡 RECOMMENDED FRONTEND VALIDATION:")
    print("""
// Disease Detection Validation
if (!formData.crop_type || !formData.symptoms || formData.symptoms.length === 0) {
    setError('Crop type and at least one symptom are required');
    return;
}

// Chat Validation  
if (!formData.message || formData.message.trim() === '') {
    setError('Message is required');
    return;
}

// Market Insights Validation
if (!formData.crop_type || !formData.location) {
    setError('Crop type and location are required');
    return;
}
""")

if __name__ == "__main__":
    test_authenticated_requests()
    print(f"\n🎉 400 ERROR INVESTIGATION COMPLETE!")
    print("📋 Use the analysis above to fix frontend validation issues")
