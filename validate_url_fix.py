#!/usr/bin/env python3
"""
Validate AI URL Fix - Django URL Resolution Test
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.urls import resolve, reverse
from django.conf import settings

def validate_url_fix():
    """Validate that the URL routing fix is working"""
    print("🔧 Validating AI Assistant URL Fix...")
    print("=" * 50)
    
    # Test URL patterns that should now work
    test_urls = [
        '/api/v1/ai/api/',
        '/api/v1/ai/api/chat/',
        '/api/v1/ai/api/health/',
        '/api/v1/ai/api/crop-advisory/',
        '/api/v1/ai/api/disease-detection/',
    ]
    
    print("🌐 Testing URL Resolution...")
    success_count = 0
    total_count = len(test_urls)
    
    for url in test_urls:
        try:
            match = resolve(url)
            print(f"✅ {url} -> {match.view_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {url} -> ERROR: {e}")
    
    print(f"\n📊 URL Resolution Results: {success_count}/{total_count} successful")
    
    # Test reverse URL generation
    print(f"\n🔄 Testing Reverse URL Generation...")
    try:
        # Test if we can reverse the URLs
        api_root = reverse('api-v1-ai:api-root')
        print(f"✅ AI API Root: {api_root}")
        
        chat_url = reverse('api-v1-ai:chat')
        print(f"✅ AI Chat: {chat_url}")
        
        health_url = reverse('api-v1-ai:health-check')
        print(f"✅ AI Health: {health_url}")
        
        crop_url = reverse('api-v1-ai:crop-advisory')
        print(f"✅ AI Crop Advisory: {crop_url}")
        
        print(f"\n✅ All reverse URL lookups successful!")
        
    except Exception as e:
        print(f"❌ Reverse URL error: {e}")
    
    # Expected vs Actual comparison
    print(f"\n📋 URL Structure Comparison:")
    print(f"Frontend Expected: /api/v1/ai/api/chat/")
    print(f"Backend Provides: {reverse('api-v1-ai:chat') if success_count > 0 else 'ERROR'}")
    
    if success_count == total_count:
        print(f"\n🎉 SUCCESS: URL fix is working!")
        print(f"✅ Frontend can now access: /api/v1/ai/api/chat/")
        print(f"✅ All AI endpoints should be accessible")
        return True
    else:
        print(f"\n❌ ISSUES: Some URLs still not working")
        return False

if __name__ == "__main__":
    success = validate_url_fix()
    if success:
        print(f"\n📝 Next Steps:")
        print(f"1. ✅ Backend URL routing fixed")
        print(f"2. 🚀 Start Django server: python manage.py runserver")
        print(f"3. 🧪 Test frontend AI chat functionality")
        print(f"4. 📖 Update API documentation")
    else:
        print(f"\n🔧 Additional debugging needed")
