#!/usr/bin/env python
"""
OpenAI API Integration Test for AgriConnect
Test the AI service implementation
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from ai.services import ai_service_manager

User = get_user_model()

def test_ai_services():
    """Test all AI services"""
    print("🤖 Testing AgriConnect AI Services...")
    print("=" * 50)
    
    # Get or create test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    # Test 1: Conversational AI
    print("\n1. Testing Conversational AI...")
    try:
        conversation_service = ai_service_manager.get_service('conversation')
        result = conversation_service.chat(
            user=user,
            message="Hello! I'm a farmer in Ghana. Can you help me with maize farming?",
            language='en'
        )
        
        if result['success']:
            print(f"✅ Conversational AI Success!")
            print(f"Response: {result['response'][:100]}...")
            print(f"Tokens used: {result['tokens_used']}")
        else:
            print(f"❌ Conversational AI Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Conversational AI Error: {str(e)}")
    
    # Test 2: Crop Advisory
    print("\n2. Testing Crop Advisory...")
    try:
        crop_service = ai_service_manager.get_service('crop')
        result = crop_service.get_crop_advice(
            user=user,
            crop_type='maize',
            farming_stage='planting',
            location='Ghana',
            season='rainy',
            specific_question='What is the best planting density for maize?'
        )
        
        if result['success']:
            print(f"✅ Crop Advisory Success!")
            print(f"Advice: {result['advice'][:100]}...")
            print(f"Confidence: {result['confidence_score']}")
        else:
            print(f"❌ Crop Advisory Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Crop Advisory Error: {str(e)}")
    
    # Test 3: Disease Detection
    print("\n3. Testing Disease Detection...")
    try:
        disease_service = ai_service_manager.get_service('disease')
        result = disease_service.detect_disease(
            user=user,
            crop_type='tomato',
            symptoms='Yellow leaves with brown spots, wilting plants',
            location='Ghana'
        )
        
        if result['success']:
            print(f"✅ Disease Detection Success!")
            print(f"Diagnosis: {result['diagnosis'][:100]}...")
            print(f"Confidence: {result['confidence_score']}")
        else:
            print(f"❌ Disease Detection Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Disease Detection Error: {str(e)}")
    
    # Test 4: Market Intelligence
    print("\n4. Testing Market Intelligence...")
    try:
        market_service = ai_service_manager.get_service('market')
        result = market_service.get_market_intelligence(
            user=user,
            crop_type='cocoa',
            location='Ghana',
            market_type='export'
        )
        
        if result['success']:
            print(f"✅ Market Intelligence Success!")
            print(f"Intelligence: {result['intelligence'][:100]}...")
            print(f"Confidence: {result['confidence_score']}")
        else:
            print(f"❌ Market Intelligence Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Market Intelligence Error: {str(e)}")
    
    # Test 5: Analytics
    print("\n5. Testing Analytics...")
    try:
        analytics_service = ai_service_manager.get_service('analytics')
        result = analytics_service.get_user_analytics(user=user, days=30)
        
        if 'error' not in result:
            print(f"✅ Analytics Success!")
            print(f"Total requests: {result['total_requests']}")
            print(f"Total tokens: {result['total_tokens_used']}")
        else:
            print(f"❌ Analytics Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Analytics Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Services Test Complete!")

if __name__ == "__main__":
    test_ai_services()
