#!/usr/bin/env python
"""
Test script for checking the three problematic endpoints
"""
import requests
import json
from django.core.management import execute_from_command_line
import os
import sys

# Add Django to path
sys.path.append('c:\\Users\\user\\Desktop\\mywebproject\\backup_v1\\myapiproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from authentication.models import UserRole

def test_endpoints():
    """Test the three problematic endpoints"""
    
    # Create test client
    client = APIClient()
    User = get_user_model()
    
    # Create a test user with admin role
    try:
        user = User.objects.create_user(
            identifier='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            roles=['ADMIN']
        )
        print("Created test user")
    except Exception as e:
        # User might already exist, try to get it
        try:
            user = User.objects.get(email='test@example.com')
            print("Using existing test user")
        except User.DoesNotExist:
            print(f"Error creating user: {e}")
            return
    
    # Authenticate
    client.force_authenticate(user=user)
    
    # Test endpoints
    endpoints = [
        ('/api/v1/analytics/farmer-stats/', 'Analytics farmer-stats'),
        ('/api/v1/warehouses/inventory/optimize/', 'Warehouse inventory optimization'),
        ('/api/v1/advertisements/dashboard/', 'Advertisement dashboard')
    ]
    
    for endpoint, description in endpoints:
        try:
            print(f"\nTesting {description}: {endpoint}")
            response = client.get(endpoint)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS")
                data = response.json()
                if 'success' in data:
                    print(f"Response success: {data['success']}")
                else:
                    print(f"Response keys: {list(data.keys())}")
            else:
                print("❌ FAILED")
                if hasattr(response, 'json'):
                    try:
                        error_data = response.json()
                        print(f"Error: {error_data}")
                    except:
                        print(f"Response content: {response.content}")
                        
        except Exception as e:
            print(f"❌ Exception testing {description}: {e}")

if __name__ == '__main__':
    test_endpoints()
