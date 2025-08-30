"""
Simple OpenRouter API Test
Test the OpenRouter AI integration for AgriConnect Ghana
"""

import os
import requests
import json
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_openrouter_connection():
    """Test basic OpenRouter API connection"""
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        return False
    
    print("🌾 AgriConnect Ghana - OpenRouter AI Test")
    print("=" * 50)
    print(f"🔑 API Key: {api_key[:20]}..." if len(api_key) > 20 else f"🔑 API Key: {api_key}")
    
    # Test API connection
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agriconnect-ghana.com",
        "X-Title": "AgriConnect Ghana - AI Agricultural Platform"
    }
    
    # Test 1: Check available models
    print("\n📡 Testing API Connection...")
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models_data = response.json()
            print(f"✅ API Connection Successful!")
            print(f"📊 Available Models: {len(models_data.get('data', []))}")
            
            # Show some popular models
            models = models_data.get('data', [])[:5]
            print("\n🤖 Sample Available Models:")
            for model in models:
                print(f"   - {model.get('id', 'Unknown')}")
                
        else:
            print(f"❌ API Connection Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {str(e)}")
        return False
    
    # Test 2: Simple AI Request
    print("\n🧠 Testing AI Response...")
    try:
        payload = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an agricultural expert for Ghana farmers."
                },
                {
                    "role": "user", 
                    "content": "Give a brief 2-sentence advice for maize farming in Ghana."
                }
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            print("✅ AI Response Generated Successfully!")
            print(f"🌽 Maize Farming Advice: {ai_response}")
            
            # Show usage stats
            usage = result.get('usage', {})
            print(f"\n📊 Usage Stats:")
            print(f"   - Prompt tokens: {usage.get('prompt_tokens', 0)}")
            print(f"   - Completion tokens: {usage.get('completion_tokens', 0)}")
            print(f"   - Total tokens: {usage.get('total_tokens', 0)}")
            
        else:
            print(f"❌ AI Request Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ AI Request Error: {str(e)}")
        return False
    
    # Test 3: Ghana-specific agricultural query
    print("\n🇬🇭 Testing Ghana Agricultural Intelligence...")
    try:
        payload = {
            "model": "anthropic/claude-3.5-sonnet:beta",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert agricultural advisor specializing in Ghana's farming conditions and climate."
                },
                {
                    "role": "user",
                    "content": "What are the best 3 crops to plant in Ashanti Region during the major season (April-July)? Give brief reasons."
                }
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            print("✅ Ghana Agricultural Intelligence Working!")
            print(f"🌾 Ashanti Region Crop Recommendations:\n{ai_response}")
            
        else:
            print(f"❌ Ghana Agricultural Query Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ghana Agricultural Query Error: {str(e)}")
        return False
    
    print("\n" + "=" * 50)
    print("🚀 OpenRouter AI Integration - FULLY OPERATIONAL!")
    print("✅ Ready for AgriConnect Ghana Production Integration")
    print(f"⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    success = test_openrouter_connection()
    if success:
        print("\n🎉 All tests passed! OpenRouter AI is ready for AgriConnect!")
    else:
        print("\n❌ Tests failed. Please check configuration.")
