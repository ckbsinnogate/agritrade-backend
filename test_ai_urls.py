#!/usr/bin/env python3
"""
Test AI URL Configuration
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.urls import reverse, resolve
from django.conf import settings

def test_ai_urls():
    """Test AI URL configuration"""
    print("🔍 Testing AI URL Configuration...")
    
    # Check if ai app is in installed apps
    print(f"✅ AI app in INSTALLED_APPS: {'ai' in settings.INSTALLED_APPS}")
    
    try:
        # Import AI URLs
        from ai.urls import urlpatterns as ai_patterns
        print(f"✅ AI URL patterns loaded: {len(ai_patterns)}")
        
        # Check individual patterns
        for pattern in ai_patterns:
            print(f"   - {pattern}")
        
        # Test URL resolution
        from django.urls import get_resolver
        resolver = get_resolver()
        
        # Look for AI patterns in resolver
        ai_found = False
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'namespace') and pattern.namespace == 'api-v1-ai':
                ai_found = True
                print(f"✅ AI namespace found: {pattern}")
                break
        
        if not ai_found:
            print("❌ AI namespace not found in resolver")
          # Test specific URLs - Updated for URL fix
        test_urls = [
            '/api/v1/ai/',                    # AI root
            '/api/v1/ai/api/',               # API root (corrected)
            '/api/v1/ai/api/health/',        # Health check (corrected)
            '/api/v1/ai/api/chat/',          # Chat endpoint (corrected)
            '/api/v1/ai/api/crop-advisory/', # Crop advisory (corrected)
        ]
        
        for url in test_urls:
            try:
                match = resolve(url)
                print(f"✅ URL {url} resolves to: {match.view_name}")
            except Exception as e:
                print(f"❌ URL {url} failed to resolve: {e}")
        
    except Exception as e:
        print(f"❌ Error testing AI URLs: {e}")

if __name__ == "__main__":
    test_ai_urls()
