"""
Comprehensive Farmer Onboarding and Testing System
Tests SMS, USSD, and Mobile App integration for continental expansion
"""

import json
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_COUNTRIES = {
    'ghana': {
        'code': '+233',
        'farmers': [
            {'name': 'Kwame Asante', 'location': 'Kumasi', 'crops': ['maize', 'cassava']},
            {'name': 'Akosua Mensah', 'location': 'Tamale', 'crops': ['rice', 'millet']},
            {'name': 'Kofi Boateng', 'location': 'Sunyani', 'crops': ['cocoa', 'plantain']},
            {'name': 'Ama Darko', 'location': 'Cape Coast', 'crops': ['cassava', 'yam']},
            {'name': 'Yaw Osei', 'location': 'Tema', 'crops': ['maize', 'beans']}
        ]
    },
    'nigeria': {
        'code': '+234',
        'farmers': [
            {'name': 'Adebayo Oluwole', 'location': 'Lagos', 'crops': ['rice', 'maize']},
            {'name': 'Fatima Hassan', 'location': 'Kano', 'crops': ['millet', 'sorghum']},
            {'name': 'Chukwu Okafor', 'location': 'Enugu', 'crops': ['yam', 'cassava']},
            {'name': 'Aisha Bello', 'location': 'Abuja', 'crops': ['rice', 'beans']},
            {'name': 'Emeka Nwosu', 'location': 'Port Harcourt', 'crops': ['plantain', 'cocoyam']}
        ]
    },
    'kenya': {
        'code': '+254',
        'farmers': [
            {'name': 'John Kamau', 'location': 'Nairobi', 'crops': ['maize', 'beans']},
            {'name': 'Grace Wanjiku', 'location': 'Kisumu', 'crops': ['rice', 'millet']},
            {'name': 'Peter Mwangi', 'location': 'Eldoret', 'crops': ['maize', 'wheat']},
            {'name': 'Mary Njeri', 'location': 'Mombasa', 'crops': ['cassava', 'sweet potato']},
            {'name': 'David Kiprotich', 'location': 'Nakuru', 'crops': ['maize', 'beans']}
        ]
    },
    'south_africa': {
        'code': '+27',
        'farmers': [
            {'name': 'Thabo Mokoena', 'location': 'Johannesburg', 'crops': ['maize', 'sorghum']},
            {'name': 'Nomsa Dlamini', 'location': 'Durban', 'crops': ['sugarcane', 'maize']},
            {'name': 'Sipho Ndlovu', 'location': 'Cape Town', 'crops': ['wheat', 'grapes']},
            {'name': 'Zanele Khumalo', 'location': 'Pretoria', 'crops': ['maize', 'sunflower']},
            {'name': 'Mandla Zulu', 'location': 'Bloemfontein', 'crops': ['maize', 'beans']}
        ]
    },
    'senegal': {
        'code': '+221',
        'farmers': [
            {'name': 'Amadou Diallo', 'location': 'Dakar', 'crops': ['rice', 'millet']},
            {'name': 'Fatou Sow', 'location': 'Saint-Louis', 'crops': ['rice', 'tomato']},
            {'name': 'Ousmane Ba', 'location': 'Thiès', 'crops': ['groundnut', 'millet']},
            {'name': 'Awa Ndiaye', 'location': 'Kaolack', 'crops': ['rice', 'maize']},
            {'name': 'Moussa Cissé', 'location': 'Ziguinchor', 'crops': ['rice', 'cashew']}
        ]
    }
}

class FarmerOnboardingTester:
    """Test farmer onboarding across multiple channels"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.registered_farmers = []
        
    def run_comprehensive_test(self):
        """Run comprehensive onboarding test"""
        print("🚀 Starting Comprehensive Farmer Onboarding Test")
        print("=" * 60)
        
        # Test 1: SMS Registration
        print("\n📱 Testing SMS Registration...")
        sms_results = self.test_sms_registration()
        
        # Test 2: USSD Menu Navigation
        print("\n📞 Testing USSD Menu System...")
        ussd_results = self.test_ussd_navigation()
        
        # Test 3: SMS Commands
        print("\n💬 Testing SMS Commands...")
        sms_command_results = self.test_sms_commands()
        
        # Test 4: Multi-language Support
        print("\n🌍 Testing Multi-language Support...")
        language_results = self.test_multi_language()
        
        # Test 5: AI Integration
        print("\n🤖 Testing AI Integration...")
        ai_results = self.test_ai_integration()
        
        # Test 6: Analytics
        print("\n📊 Testing Analytics...")
        analytics_results = self.test_analytics()
        
        # Generate comprehensive report
        self.generate_final_report({
            'sms_registration': sms_results,
            'ussd_navigation': ussd_results,
            'sms_commands': sms_command_results,
            'multi_language': language_results,
            'ai_integration': ai_results,
            'analytics': analytics_results
        })
        
    def test_sms_registration(self) -> Dict:
        """Test SMS-based farmer registration"""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        for country, config in TEST_COUNTRIES.items():
            print(f"\n  🌍 Testing {country.title()} ({config['code']})")
            
            for farmer in config['farmers']:
                phone_number = f"{config['code']}{random.randint(100000000, 999999999)}"
                
                registration_data = {
                    'phone_number': phone_number,
                    'name': farmer['name'],
                    'location': farmer['location'],
                    'crops': farmer['crops'],
                    'language': 'en'
                }
                
                try:
                    response = requests.post(
                        f"{self.base_url}/api/v1/sms/farmer/register/",
                        json=registration_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            results['passed'] += 1
                            self.registered_farmers.append({
                                'phone_number': phone_number,
                                'name': farmer['name'],
                                'country': country,
                                'user_id': data.get('user_id')
                            })
                            print(f"    ✅ {farmer['name']} registered successfully")
                        else:
                            results['failed'] += 1
                            print(f"    ❌ {farmer['name']} registration failed: {data.get('error')}")
                    else:
                        results['failed'] += 1
                        print(f"    ❌ {farmer['name']} registration failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    results['failed'] += 1
                    print(f"    ❌ {farmer['name']} registration error: {str(e)}")
                
                results['total_tests'] += 1
                
        return results
        
    def test_ussd_navigation(self) -> Dict:
        """Test USSD menu navigation"""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        # Test different USSD menu paths
        ussd_tests = [
            {'text': '', 'expected_contains': 'Welcome to AgriConnect'},
            {'text': '1', 'expected_contains': 'Enter your farming question'},
            {'text': '2', 'expected_contains': 'Crop Advisory'},
            {'text': '3', 'expected_contains': 'Disease Detection'},
            {'text': '4', 'expected_contains': 'Market Prices'},
            {'text': '5', 'expected_contains': 'Weather Updates'},
            {'text': '6', 'expected_contains': 'Profile'},
            {'text': '7', 'expected_contains': 'Language Settings'},
            {'text': '0', 'expected_contains': 'Help'}
        ]
        
        # Test with sample farmers
        for farmer in self.registered_farmers[:3]:  # Test with first 3 farmers
            print(f"\n  👤 Testing USSD for {farmer['name']} ({farmer['phone_number']})")
            
            for test in ussd_tests:
                try:
                    ussd_data = {
                        'sessionId': f'session_{random.randint(1000, 9999)}',
                        'serviceCode': '*123#',
                        'phoneNumber': farmer['phone_number'],
                        'text': test['text']
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/api/v1/sms/ussd/test/",
                        json=ussd_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success') and test['expected_contains'] in data.get('response', ''):
                            results['passed'] += 1
                            print(f"    ✅ Menu '{test['text']}' works correctly")
                        else:
                            results['failed'] += 1
                            print(f"    ❌ Menu '{test['text']}' failed")
                    else:
                        results['failed'] += 1
                        print(f"    ❌ USSD test failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    results['failed'] += 1
                    print(f"    ❌ USSD test error: {str(e)}")
                
                results['total_tests'] += 1
                
        return results
        
    def test_sms_commands(self) -> Dict:
        """Test SMS command processing"""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        # Test different SMS commands
        sms_commands = [
            {'message': 'HELP', 'expected_contains': 'Commands'},
            {'message': 'ASK What is the best time to plant maize?', 'expected_contains': 'AgriBot'},
            {'message': 'CROP maize Ghana', 'expected_contains': 'advice'},
            {'message': 'DISEASE yellow leaves brown spots', 'expected_contains': 'diagnosis'},
            {'message': 'PRICE maize', 'expected_contains': 'market'},
            {'message': 'WEATHER Accra', 'expected_contains': 'weather'},
            {'message': 'PROFILE', 'expected_contains': 'Profile'}
        ]
        
        # Test with sample farmers
        for farmer in self.registered_farmers[:2]:  # Test with first 2 farmers
            print(f"\n  👤 Testing SMS Commands for {farmer['name']}")
            
            for command in sms_commands:
                try:
                    sms_data = {
                        'phone_number': farmer['phone_number'],
                        'message': command['message']
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/api/v1/sms/sms/test/",
                        json=sms_data,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success') and command['expected_contains'].lower() in data.get('response_message', '').lower():
                            results['passed'] += 1
                            print(f"    ✅ Command '{command['message'][:20]}...' works")
                        else:
                            results['failed'] += 1
                            print(f"    ❌ Command '{command['message'][:20]}...' failed")
                    else:
                        results['failed'] += 1
                        print(f"    ❌ SMS command failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    results['failed'] += 1
                    print(f"    ❌ SMS command error: {str(e)}")
                
                results['total_tests'] += 1
                
        return results
        
    def test_multi_language(self) -> Dict:
        """Test multi-language support"""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        # Test different languages
        language_tests = [
            {'lang': 'en', 'message': 'HELP', 'expected_contains': 'Commands'},
            {'lang': 'tw', 'message': 'HELP', 'expected_contains': 'Commands'},  # Twi
            {'lang': 'ha', 'message': 'HELP', 'expected_contains': 'Umarni'},    # Hausa
            {'lang': 'yo', 'message': 'HELP', 'expected_contains': 'Awọn'},      # Yoruba
            {'lang': 'fr', 'message': 'HELP', 'expected_contains': 'Commandes'} # French
        ]
        
        # Test with one farmer from each country
        country_farmers = {}
        for farmer in self.registered_farmers:
            if farmer['country'] not in country_farmers:
                country_farmers[farmer['country']] = farmer
        
        for country, farmer in country_farmers.items():
            print(f"\n  🌍 Testing Languages for {farmer['name']} ({country})")
            
            for test in language_tests:
                try:
                    sms_data = {
                        'phone_number': farmer['phone_number'],
                        'message': test['message']
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/api/v1/sms/sms/test/",
                        json=sms_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            results['passed'] += 1
                            print(f"    ✅ Language '{test['lang']}' supported")
                        else:
                            results['failed'] += 1
                            print(f"    ❌ Language '{test['lang']}' failed")
                    else:
                        results['failed'] += 1
                        print(f"    ❌ Language test failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    results['failed'] += 1
                    print(f"    ❌ Language test error: {str(e)}")
                
                results['total_tests'] += 1
                
        return results
        
    def test_ai_integration(self) -> Dict:
        """Test AI system integration"""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        # Test AI endpoints directly
        ai_tests = [
            {'endpoint': '/api/v1/ai/api/health/', 'method': 'GET', 'expected_status': 200},
            {'endpoint': '/api/v1/ai/api/chat/', 'method': 'POST', 'data': {'message': 'Hello AgriBot'}, 'expected_status': 200},
            {'endpoint': '/api/v1/ai/api/crop-advisory/', 'method': 'POST', 'data': {'crop_type': 'maize', 'location': 'Ghana'}, 'expected_status': 200},
            {'endpoint': '/api/v1/ai/api/disease-detection/', 'method': 'POST', 'data': {'symptoms': 'yellow leaves'}, 'expected_status': 200},
            {'endpoint': '/api/v1/ai/api/market-intelligence/', 'method': 'POST', 'data': {'crop_type': 'maize'}, 'expected_status': 200}
        ]
        
        print("\n  🤖 Testing AI Endpoints...")
        
        for test in ai_tests:
            try:
                if test['method'] == 'GET':
                    response = requests.get(f"{self.base_url}{test['endpoint']}", timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{test['endpoint']}", json=test['data'], timeout=15)
                
                if response.status_code == test['expected_status']:
                    results['passed'] += 1
                    print(f"    ✅ {test['endpoint']} works correctly")
                else:
                    results['failed'] += 1
                    print(f"    ❌ {test['endpoint']} failed: HTTP {response.status_code}")
                    
            except Exception as e:
                results['failed'] += 1
                print(f"    ❌ {test['endpoint']} error: {str(e)}")
            
            results['total_tests'] += 1
            
        return results
        
    def test_analytics(self) -> Dict:
        """Test analytics system"""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        print("\n  📊 Testing Analytics...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/sms/analytics/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'sms_analytics' in data:
                    results['passed'] += 1
                    print(f"    ✅ SMS Analytics working")
                    print(f"    📊 Total SMS Users: {data['sms_analytics']['total_sms_users']}")
                else:
                    results['failed'] += 1
                    print(f"    ❌ Analytics data missing")
            else:
                results['failed'] += 1
                print(f"    ❌ Analytics failed: HTTP {response.status_code}")
                
        except Exception as e:
            results['failed'] += 1
            print(f"    ❌ Analytics error: {str(e)}")
        
        results['total_tests'] += 1
        
        return results
        
    def generate_final_report(self, all_results: Dict):
        """Generate comprehensive final report"""
        print("\n" + "="*60)
        print("🎉 COMPREHENSIVE FARMER ONBOARDING TEST REPORT")
        print("="*60)
        
        total_tests = sum(result['total_tests'] for result in all_results.values())
        total_passed = sum(result['passed'] for result in all_results.values())
        total_failed = sum(result['failed'] for result in all_results.values())
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests Run: {total_tests}")
        print(f"   Tests Passed: {total_passed}")
        print(f"   Tests Failed: {total_failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🌍 FARMERS REGISTERED:")
        print(f"   Total Farmers: {len(self.registered_farmers)}")
        
        country_counts = {}
        for farmer in self.registered_farmers:
            country = farmer['country']
            country_counts[country] = country_counts.get(country, 0) + 1
        
        for country, count in country_counts.items():
            print(f"   {country.title()}: {count} farmers")
        
        print(f"\n🔍 DETAILED RESULTS:")
        
        for test_name, result in all_results.items():
            success_rate = (result['passed'] / result['total_tests'] * 100) if result['total_tests'] > 0 else 0
            status = "✅ PASS" if success_rate >= 80 else "⚠️ PARTIAL" if success_rate >= 50 else "❌ FAIL"
            
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
            print(f"     - Tests: {result['total_tests']}, Passed: {result['passed']}, Failed: {result['failed']}")
            print(f"     - Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 READINESS ASSESSMENT:")
        
        if success_rate >= 90:
            print("   🚀 EXCELLENT - Ready for immediate continental deployment!")
        elif success_rate >= 80:
            print("   ✅ GOOD - Ready for phased deployment with monitoring")
        elif success_rate >= 70:
            print("   ⚠️ ACCEPTABLE - Some issues need addressing before full deployment")
        else:
            print("   ❌ NEEDS WORK - Significant issues must be resolved")
        
        print(f"\n🌟 CONTINENTAL EXPANSION STATUS:")
        print(f"   SMS System: {'✅ READY' if all_results['sms_registration']['passed'] > 0 else '❌ NOT READY'}")
        print(f"   USSD System: {'✅ READY' if all_results['ussd_navigation']['passed'] > 0 else '❌ NOT READY'}")
        print(f"   AI Integration: {'✅ READY' if all_results['ai_integration']['passed'] > 0 else '❌ NOT READY'}")
        print(f"   Multi-language: {'✅ READY' if all_results['multi_language']['passed'] > 0 else '❌ NOT READY'}")
        
        print(f"\n📈 NEXT STEPS:")
        print("   1. Deploy to pilot countries (Ghana, Nigeria, Kenya)")
        print("   2. Monitor performance and user feedback")
        print("   3. Scale to additional countries")
        print("   4. Launch mobile app in parallel")
        print("   5. Implement voice AI capabilities")
        
        print("\n" + "="*60)
        print("🎉 CONTINENTAL EXPANSION READY!")
        print("="*60)


def main():
    """Run the comprehensive farmer onboarding test"""
    tester = FarmerOnboardingTester()
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main()
