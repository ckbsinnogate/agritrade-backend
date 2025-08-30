#!/usr/bin/env python3
"""
Test Registration with Correct Format
"""

import requests
import json
from datetime import datetime

def test_registration():
    print('🧪 TESTING REGISTRATION WITH CORRECT FORMAT')
    print('=' * 50)
    
    # Correct format for registration based on serializer
    test_user = {
        'identifier': 'testfarmer@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'Test',
        'last_name': 'Farmer',
        'roles': ['FARMER'],
        'country': 'Ghana',
        'region': 'Greater Accra',
        'language': 'en'
    }

    try:
        response = requests.post('http://127.0.0.1:8000/api/v1/auth/register/', json=test_user)
        print(f'Registration Status: {response.status_code}')
        print(f'Response: {response.text}')

        if response.status_code == 201:
            print('✅ User Registration: SUCCESS')
            data = response.json()
            print(f'User ID: {data.get("user_id")}')
            print(f'OTP Required: {data.get("otp_required")}')
        elif response.status_code == 400:
            print('❌ Registration failed - User might already exist')
            # Try login instead
            test_login()
        else:
            print(f'❌ Registration failed with status {response.status_code}')

    except Exception as e:
        print(f'❌ Authentication Error: {e}')

def test_login():
    print('\n🔐 TESTING LOGIN')
    print('-' * 30)
    
    login_data = {
        'identifier': 'testfarmer@example.com',
        'password': 'testpass123'
    }

    try:
        response = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data)
        print(f'Login Status: {response.status_code}')
        print(f'Response: {response.text}')

        if response.status_code == 200:
            print('✅ User Login: SUCCESS')
            data = response.json()
            access_token = data.get('access_token')
            if access_token:
                print(f'Access Token: {access_token[:20]}...')
                
                # Test authenticated AI endpoint
                test_ai_with_token(access_token)
        else:
            print(f'❌ Login failed with status {response.status_code}')

    except Exception as e:
        print(f'❌ Login Error: {e}')

def test_ai_with_token(access_token):
    print('\n🤖 TESTING AI ENDPOINT WITH TOKEN')
    print('-' * 30)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    ai_data = {
        'message': 'Hello AgriBot, can you help me with crop recommendations?',
        'language': 'en'
    }

    try:
        response = requests.post('http://127.0.0.1:8000/api/v1/ai/api/chat/', json=ai_data, headers=headers)
        print(f'AI Chat Status: {response.status_code}')
        print(f'Response: {response.text}')

        if response.status_code == 200:
            print('✅ AI Chat: SUCCESS')
            print('🎯 Mobile app integration is ready!')
        else:
            print(f'❌ AI Chat failed with status {response.status_code}')

    except Exception as e:
        print(f'❌ AI Chat Error: {e}')

if __name__ == "__main__":
    test_registration()
