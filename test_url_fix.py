#!/usr/bin/env python3
"""
Test URL Fix for AI Assistant 404 Issues
"""

import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_url_fix():
    """Test the corrected URL structure"""
    print("🔧 Testing AI Assistant URL Fix...")
    print("=" * 50)
    
    # URLs to test
    test_urls = [
        "http://127.0.0.1:8000/api/v1/ai/",  # AI root
        "http://127.0.0.1:8000/api/v1/ai/api/",  # API root (corrected)
        "http://127.0.0.1:8000/api/v1/ai/api/health/",  # Health check (corrected)
        "http://127.0.0.1:8000/api/v1/ai/api/chat/",  # Chat endpoint (corrected)
    ]
    
    for url in test_urls:
        try:
            print(f"\n🌐 Testing: {url}")
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS")
                try:
                    data = response.json()
                    if 'name' in data:
                        print(f"   📋 Service: {data.get('name', 'Unknown')}")
                    elif 'endpoints' in data:
                        print(f"   📋 Available endpoints: {len(data['endpoints'])}")
                except:
                    print(f"   📋 Response received (non-JSON)")
            elif response.status_code == 401:
                print(f"   🔐 AUTHENTICATION REQUIRED (Expected for protected endpoints)")
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND - URL structure issue")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR - Server not running")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)[:50]}...")
    
    # Test authenticated request to chat endpoint
    print(f"\n🔐 Testing Authenticated Chat Request...")
    try:
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='urltest',
            defaults={
                'email': 'urltest@example.com',
                'first_name': 'URL',
                'last_name': 'Tester'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        # Get JWT token
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        
        # Test chat endpoint with authentication
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        chat_data = {
            'message': 'Hello! This is a test message to verify the URL fix.',
            'language': 'en'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/ai/api/chat/',
            json=chat_data,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ CHAT ENDPOINT WORKING!")
            data = response.json()
            if 'response' in data:
                print(f"   💬 AI Response: {data['response'][:100]}...")
        else:
            print(f"   ❌ Chat failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Authentication test error: {str(e)[:50]}...")
    
    print(f"\n📋 URL Fix Test Complete!")

if __name__ == "__main__":
    test_url_fix()
