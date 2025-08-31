#!/usr/bin/env python
"""
Production Debugging Script for AgriTrade DigitalOcean App Platform
This script helps diagnose deployment issues by testing Django configuration
"""
import os
import sys
import django
from pathlib import Path

def test_django_configuration():
    """Test Django configuration for production deployment"""
    print("=== AgriTrade Production Debug ===")
    print(f"Python version: {sys.version}")
    print(f"Django version: {django.VERSION}")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings_appplatform')
    
    try:
        django.setup()
        print("✅ Django setup successful")
        
        # Test imports
        from django.conf import settings
        print(f"✅ Settings imported successfully")
        print(f"   - DEBUG: {settings.DEBUG}")
        print(f"   - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   - SECRET_KEY set: {'Yes' if settings.SECRET_KEY else 'No'}")
        
        # Test database connection
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
        
        # Test installed apps
        print(f"✅ Installed apps ({len(settings.INSTALLED_APPS)}):")
        for app in settings.INSTALLED_APPS:
            try:
                __import__(app)
                print(f"   ✅ {app}")
            except ImportError as e:
                print(f"   ❌ {app}: {e}")
        
        # Test URL configuration
        try:
            from django.urls import reverse
            from django.test import Client
            client = Client()
            
            # Test health endpoint
            response = client.get('/api/health/')
            print(f"✅ Health endpoint status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
            
        except Exception as e:
            print(f"❌ URL/Health check failed: {e}")
            
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_django_configuration()
