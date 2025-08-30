"""
AgriConnect OpenRouter AI Integration - Comprehensive Testing Suite
Tests all AI functionality for Ghana agricultural platform
"""

import os
import sys
import json
import time
import base64
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test OpenRouter AI Integration
def test_openrouter_comprehensive():
    """Comprehensive test of OpenRouter AI integration for AgriConnect Ghana"""
    
    print("🇬🇭 AGRICONNECT GHANA - AI INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Python version: {sys.version}")
    
    # Test results tracking
    test_results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    def run_test(test_name, test_func):
        """Run individual test and track results"""
        test_results['total_tests'] += 1
        print(f"\n🧪 Running: {test_name}")
        print("-" * 60)
        
        try:
            success = test_func()
            if success:
                test_results['passed'] += 1
                print(f"✅ PASSED: {test_name}")
            else:
                test_results['failed'] += 1
                test_results['errors'].append(f"FAILED: {test_name}")
                print(f"❌ FAILED: {test_name}")
        except Exception as e:
            test_results['failed'] += 1
            error_msg = f"ERROR in {test_name}: {str(e)}"
            test_results['errors'].append(error_msg)
            print(f"💥 ERROR: {test_name} - {str(e)}")
    
    # Test 1: Environment Setup
    def test_environment():
        """Test environment variables and dependencies"""
        print("🔍 Checking environment setup...")
        
        # Check API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            # Try getting from .env file
            try:
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.getenv('OPENROUTER_API_KEY')
            except ImportError:
                pass
        
        if api_key:
            print(f"✅ OpenRouter API key found: {api_key[:20]}...")
        else:
            print("❌ OpenRouter API key not found")
            return False
        
        # Check required packages
        required_packages = ['requests', 'django']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} available")
            except ImportError:
                print(f"❌ {package} not available")
                return False
        
        return True
    
    # Test 2: API Connection
    def test_api_connection():
        """Test OpenRouter API connection"""
        print("🌐 Testing OpenRouter API connection...")
        
        try:
            import requests
            
            api_key = os.getenv('OPENROUTER_API_KEY', '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')
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://agriconnect-ghana.com",
                "X-Title": "AgriConnect Ghana"
            }
            
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                models = response.json().get('data', [])
                print(f"✅ API connected successfully! {len(models)} models available")
                return True
            else:
                print(f"❌ API connection failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ API connection error: {str(e)}")
            return False
    
    # Test 3: AI Chat Completion
    def test_ai_response():
        """Test basic AI chat completion"""
        print("🤖 Testing AI response generation...")
        
        try:
            import requests
            
            api_key = os.getenv('OPENROUTER_API_KEY', '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')
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an agricultural expert for Ghana farmers."
                    },
                    {
                        "role": "user",
                        "content": "Give one piece of advice for cocoa farming in Ghana."
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
                print(f"✅ AI Response: {ai_response[:100]}...")
                
                # Check usage stats
                usage = result.get('usage', {})
                print(f"📊 Tokens used: {usage.get('total_tokens', 0)}")
                return True
            else:
                print(f"❌ AI request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ AI response error: {str(e)}")
            return False
    
    # Test 4: Ghana Agricultural Knowledge
    def test_ghana_agricultural_knowledge():
        """Test Ghana-specific agricultural AI responses"""
        print("🇬🇭 Testing Ghana agricultural knowledge...")
        
        try:
            import requests
            
            api_key = os.getenv('OPENROUTER_API_KEY', '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')
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Test Ghana crop knowledge
            payload = {
                "model": "anthropic/claude-3.5-sonnet:beta",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert on Ghana's agriculture, climate zones, and farming practices."
                    },
                    {
                        "role": "user",
                        "content": "What are the best 3 crops for Ashanti Region during major season? List only crop names."
                    }
                ],
                "max_tokens": 80,
                "temperature": 0.3
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
                print(f"✅ Ghana Agricultural Knowledge: {ai_response}")
                
                # Check if response mentions relevant Ghana crops
                ghana_crops = ['cocoa', 'maize', 'cassava', 'yam', 'plantain', 'rice', 'tomato']
                response_lower = ai_response.lower()
                relevant_crops = [crop for crop in ghana_crops if crop in response_lower]
                
                if relevant_crops:
                    print(f"✅ Found relevant Ghana crops: {', '.join(relevant_crops)}")
                    return True
                else:
                    print("⚠️ Response doesn't mention common Ghana crops")
                    return False
            else:
                print(f"❌ Ghana agricultural test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ghana agricultural knowledge error: {str(e)}")
            return False
    
    # Test 5: Integration Module
    def test_integration_module():
        """Test Django integration module"""
        print("⚙️ Testing Django integration module...")
        
        try:
            # Try to import the integration module
            from openrouter_django_integration import openrouter_ai
            print("✅ Integration module imported successfully")
            
            # Test status check
            status = openrouter_ai.get_api_status()
            if status.get('status') == 'operational':
                print("✅ Integration module API status check passed")
                return True
            else:
                print(f"❌ Integration module status check failed: {status}")
                return False
                
        except ImportError as e:
            print(f"❌ Failed to import integration module: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Integration module error: {str(e)}")
            return False
    
    # Test 6: Crop Analysis Function
    def test_crop_analysis():
        """Test crop suitability analysis function"""
        print("🌾 Testing crop analysis function...")
        
        try:
            from openrouter_django_integration import openrouter_ai
            
            # Test crop analysis
            result = openrouter_ai.analyze_crop_suitability(
                location="Ashanti Region",
                soil_type="Clay loam",
                crop="Maize",
                season="Major season"
            )
            
            if 'error' not in result:
                print("✅ Crop analysis function working")
                print(f"📊 Analysis model: {result.get('model_used', 'Unknown')}")
                return True
            else:
                print(f"❌ Crop analysis failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Crop analysis function error: {str(e)}")
            return False
    
    # Run all tests
    run_test("Environment Setup", test_environment)
    run_test("API Connection", test_api_connection)
    run_test("AI Response Generation", test_ai_response)
    run_test("Ghana Agricultural Knowledge", test_ghana_agricultural_knowledge)
    run_test("Integration Module", test_integration_module)
    run_test("Crop Analysis Function", test_crop_analysis)
    
    # Final Results
    print("\n" + "=" * 80)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 80)
    print(f"📊 Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%")
    
    if test_results['failed'] > 0:
        print(f"\n💥 Failed Tests:")
        for error in test_results['errors']:
            print(f"   - {error}")
    
    print(f"\n⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if test_results['failed'] == 0:
        print("🎉 ALL TESTS PASSED! OpenRouter AI Integration is READY for production!")
        print("🚀 AgriConnect Ghana AI capabilities are FULLY OPERATIONAL!")
        return True
    else:
        print("⚠️ Some tests failed. Please review and fix issues before production.")
        return False

if __name__ == "__main__":
    success = test_openrouter_comprehensive()
    sys.exit(0 if success else 1)
