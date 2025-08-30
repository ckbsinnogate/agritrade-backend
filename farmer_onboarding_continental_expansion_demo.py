#!/usr/bin/env python3
"""
AgriConnect Farmer Onboarding & Continental Expansion Demo
=========================================================
Comprehensive demonstration of farmer onboarding across multiple African countries
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

class FarmerOnboardingDemo:
    """Comprehensive farmer onboarding demonstration"""
    
    def __init__(self):
        self.api_base = "http://127.0.0.1:8000/api/v1"
        self.auth_base = f"{self.api_base}/auth"
        self.ai_base = f"{self.api_base}/ai/api"
        
        # Continental expansion countries
        self.countries = [
            {
                'name': 'Ghana',
                'code': 'GH',
                'regions': ['Greater Accra', 'Ashanti', 'Northern', 'Western', 'Central', 'Volta'],
                'languages': ['en'],
                'currency': 'GHS',
                'phone_prefix': '+233',
                'sample_farmers': [
                    {'name': 'Kwame Asante', 'crop': 'cocoa', 'region': 'Ashanti'},
                    {'name': 'Abena Osei', 'crop': 'maize', 'region': 'Greater Accra'},
                    {'name': 'Kofi Mensah', 'crop': 'cassava', 'region': 'Central'}
                ]
            },
            {
                'name': 'Nigeria',
                'code': 'NG',
                'regions': ['Lagos', 'Kano', 'Rivers', 'Kaduna', 'Ogun', 'Enugu'],
                'languages': ['en'],
                'currency': 'NGN',
                'phone_prefix': '+234',
                'sample_farmers': [
                    {'name': 'Adebayo Okafor', 'crop': 'yam', 'region': 'Enugu'},
                    {'name': 'Ngozi Chioma', 'crop': 'rice', 'region': 'Kaduna'},
                    {'name': 'Ibrahim Musa', 'crop': 'millet', 'region': 'Kano'}
                ]
            },
            {
                'name': 'Kenya',
                'code': 'KE',
                'regions': ['Nairobi', 'Mombasa', 'Nakuru', 'Eldoret', 'Kisumu', 'Nyeri'],
                'languages': ['en', 'sw'],
                'currency': 'KES',
                'phone_prefix': '+254',
                'sample_farmers': [
                    {'name': 'Grace Wanjiku', 'crop': 'coffee', 'region': 'Nyeri'},
                    {'name': 'Peter Kiprotich', 'crop': 'maize', 'region': 'Eldoret'},
                    {'name': 'Mary Achieng', 'crop': 'tea', 'region': 'Kisumu'}
                ]
            },
            {
                'name': 'Ethiopia',
                'code': 'ET',
                'regions': ['Addis Ababa', 'Oromia', 'Amhara', 'Tigray', 'SNNPR', 'Somali'],
                'languages': ['en', 'am'],
                'currency': 'ETB',
                'phone_prefix': '+251',
                'sample_farmers': [
                    {'name': 'Alemayehu Tadesse', 'crop': 'coffee', 'region': 'Oromia'},
                    {'name': 'Desta Mulugeta', 'crop': 'teff', 'region': 'Amhara'},
                    {'name': 'Hanna Bekele', 'crop': 'barley', 'region': 'Tigray'}
                ]
            }
        ]
        
        self.results = {
            'total_farmers_onboarded': 0,
            'countries_active': 0,
            'ai_interactions': 0,
            'successful_logins': 0,
            'regions_covered': 0,
            'crops_supported': set(),
            'languages_active': set(),
            'onboarding_details': []
        }
    
    def demonstrate_farmer_onboarding(self, country: Dict, farmer: Dict):
        """Demonstrate complete farmer onboarding process"""
        print(f"\n👨‍🌾 ONBOARDING FARMER: {farmer['name']} ({country['name']})")
        print("-" * 60)
        
        # Step 1: Registration
        farmer_email = f"{farmer['name'].lower().replace(' ', '.')}@{country['code'].lower()}.agriconnect.com"
        
        registration_data = {
            'identifier': farmer_email,
            'password': 'FarmerPass123!',
            'password_confirm': 'FarmerPass123!',
            'first_name': farmer['name'].split()[0],
            'last_name': farmer['name'].split()[1] if len(farmer['name'].split()) > 1 else 'Farmer',
            'roles': ['FARMER'],
            'country': country['name'],
            'region': farmer['region'],
            'language': country['languages'][0],
            'contact_method': 'email'
        }
        
        try:
            response = requests.post(f"{self.auth_base}/register/", json=registration_data, timeout=30)
            
            if response.status_code in [200, 201]:
                print("✅ Registration: SUCCESS")
                registration_success = True
            elif response.status_code == 400 and "already exists" in response.text:
                print("✅ Registration: SUCCESS (User exists)")
                registration_success = True
            else:
                print(f"❌ Registration: FAILED (Status: {response.status_code})")
                registration_success = False
        except Exception as e:
            print(f"❌ Registration: FAILED ({e})")
            registration_success = False
        
        if not registration_success:
            return False
        
        # Step 2: Login
        login_data = {
            'identifier': farmer_email,
            'password': 'FarmerPass123!'
        }
        
        try:
            response = requests.post(f"{self.auth_base}/login/", json=login_data, timeout=30)
            
            if response.status_code == 200:
                print("✅ Login: SUCCESS")
                login_data_response = response.json()
                access_token = login_data_response.get('access')
                self.results['successful_logins'] += 1
                login_success = True
            else:
                print(f"❌ Login: FAILED (Status: {response.status_code})")
                login_success = False
        except Exception as e:
            print(f"❌ Login: FAILED ({e})")
            login_success = False
        
        if not login_success:
            return False
        
        # Step 3: AI Crop Advisory
        headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        
        crop_question = f"I'm a farmer in {farmer['region']}, {country['name']} and I grow {farmer['crop']}. What advice do you have for me?"
        
        try:
            response = requests.post(f"{self.ai_base}/crop-advisory", json={
                'crop': farmer['crop'],
                'location': f"{farmer['region']}, {country['name']}",
                'question': crop_question
            }, headers=headers, timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json()
                advice = ai_response.get('advice', 'No advice available')
                print("✅ AI Crop Advisory: SUCCESS")
                print(f"   Advice: {advice[:100]}...")
                self.results['ai_interactions'] += 1
                ai_success = True
            else:
                print(f"❌ AI Crop Advisory: FAILED (Status: {response.status_code})")
                ai_success = False
        except Exception as e:
            print(f"❌ AI Crop Advisory: FAILED ({e})")
            ai_success = False
        
        # Step 4: AI Chat Interaction
        try:
            response = requests.post(f"{self.ai_base}/chat", json={
                'message': f"Hello! I'm {farmer['name']} from {farmer['region']}. I need help with {farmer['crop']} farming.",
                'context': {
                    'country': country['name'],
                    'region': farmer['region'],
                    'crop': farmer['crop']
                }
            }, headers=headers, timeout=30)
            
            if response.status_code == 200:
                chat_response = response.json()
                response_text = chat_response.get('response', 'No response available')
                print("✅ AI Chat: SUCCESS")
                print(f"   Response: {response_text[:100]}...")
                self.results['ai_interactions'] += 1
                chat_success = True
            else:
                print(f"❌ AI Chat: FAILED (Status: {response.status_code})")
                chat_success = False
        except Exception as e:
            print(f"❌ AI Chat: FAILED ({e})")
            chat_success = False
        
        # Record results
        if registration_success and login_success:
            self.results['total_farmers_onboarded'] += 1
            self.results['crops_supported'].add(farmer['crop'])
            self.results['languages_active'].update(country['languages'])
            
            self.results['onboarding_details'].append({
                'farmer_name': farmer['name'],
                'country': country['name'],
                'region': farmer['region'],
                'crop': farmer['crop'],
                'email': farmer_email,
                'registration_success': registration_success,
                'login_success': login_success,
                'ai_advisory_success': ai_success,
                'ai_chat_success': chat_success,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ ONBOARDING COMPLETE for {farmer['name']}")
            return True
        
        return False
    
    def demonstrate_country_expansion(self, country: Dict):
        """Demonstrate country expansion with multiple farmers"""
        print(f"\n🌍 EXPANDING TO: {country['name'].upper()}")
        print("=" * 60)
        print(f"📍 Regions: {', '.join(country['regions'])}")
        print(f"🗣️ Languages: {', '.join(country['languages'])}")
        print(f"💰 Currency: {country['currency']}")
        print(f"📞 Phone Prefix: {country['phone_prefix']}")
        
        farmers_onboarded = 0
        
        for farmer in country['sample_farmers']:
            if self.demonstrate_farmer_onboarding(country, farmer):
                farmers_onboarded += 1
        
        if farmers_onboarded > 0:
            self.results['countries_active'] += 1
            self.results['regions_covered'] += len(country['regions'])
        
        print(f"\n📊 {country['name']} EXPANSION RESULTS:")
        print(f"   Farmers Onboarded: {farmers_onboarded}/{len(country['sample_farmers'])}")
        print(f"   Regions Covered: {len(country['regions'])}")
        print(f"   Languages Active: {len(country['languages'])}")
        
        return farmers_onboarded > 0
    
    def run_continental_expansion_demo(self):
        """Run complete continental expansion demonstration"""
        print("🚀 AGRICONNECT CONTINENTAL EXPANSION DEMONSTRATION")
        print("=" * 70)
        print(f"🕐 Started at: {datetime.now()}")
        print(f"🎯 Target: Onboard farmers across {len(self.countries)} African countries")
        print()
        
        # Demonstrate expansion to each country
        for country in self.countries:
            success = self.demonstrate_country_expansion(country)
            if success:
                print(f"✅ {country['name']} expansion: SUCCESSFUL")
            else:
                print(f"❌ {country['name']} expansion: FAILED")
        
        # Generate comprehensive report
        self.generate_expansion_report()
        
        return True
    
    def generate_expansion_report(self):
        """Generate comprehensive expansion report"""
        print("\n" + "=" * 70)
        print("🏆 CONTINENTAL EXPANSION DEMONSTRATION COMPLETE")
        print("=" * 70)
        
        print(f"📊 EXPANSION STATISTICS:")
        print(f"   Total Farmers Onboarded: {self.results['total_farmers_onboarded']}")
        print(f"   Countries Active: {self.results['countries_active']}/{len(self.countries)}")
        print(f"   Regions Covered: {self.results['regions_covered']}")
        print(f"   Successful Logins: {self.results['successful_logins']}")
        print(f"   AI Interactions: {self.results['ai_interactions']}")
        print(f"   Crops Supported: {len(self.results['crops_supported'])}")
        print(f"   Languages Active: {len(self.results['languages_active'])}")
        
        print(f"\n🌾 CROPS SUPPORTED:")
        for crop in sorted(self.results['crops_supported']):
            print(f"   • {crop.title()}")
        
        print(f"\n🗣️ LANGUAGES ACTIVE:")
        for language in sorted(self.results['languages_active']):
            print(f"   • {language.upper()}")
        
        print(f"\n🌍 COUNTRY STATUS:")
        for country in self.countries:
            status = "✅ ACTIVE" if country['name'] in [detail['country'] for detail in self.results['onboarding_details']] else "❌ INACTIVE"
            print(f"   {country['name']}: {status}")
        
        # Save detailed results
        with open('farmer_onboarding_results.json', 'w') as f:
            # Convert sets to lists for JSON serialization
            results_copy = self.results.copy()
            results_copy['crops_supported'] = list(self.results['crops_supported'])
            results_copy['languages_active'] = list(self.results['languages_active'])
            json.dump(results_copy, f, indent=2)
        
        print(f"\n📋 Detailed results saved to: farmer_onboarding_results.json")
        
        # Success metrics
        success_rate = (self.results['total_farmers_onboarded'] / sum(len(c['sample_farmers']) for c in self.countries)) * 100
        
        print(f"\n🎯 SUCCESS METRICS:")
        print(f"   Onboarding Success Rate: {success_rate:.1f}%")
        print(f"   Country Penetration: {(self.results['countries_active'] / len(self.countries)) * 100:.1f}%")
        print(f"   AI Engagement Rate: {(self.results['ai_interactions'] / (self.results['total_farmers_onboarded'] * 2)) * 100:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 MISSION ACCOMPLISHED!")
            print("✅ AgriConnect is ready for continental expansion!")
            print("✅ Farmer onboarding system is fully operational!")
            print("✅ Multi-country deployment is successful!")
        else:
            print("\n⚠️ IMPROVEMENT NEEDED")
            print("Some farmers could not be onboarded. Review system before full deployment.")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Deploy production servers in each country")
        print("2. Launch farmer recruitment campaigns")
        print("3. Partner with local agricultural organizations")
        print("4. Scale SMS and AI services")
        print("5. Monitor farmer engagement metrics")

def main():
    """Main demonstration function"""
    demo = FarmerOnboardingDemo()
    demo.run_continental_expansion_demo()

if __name__ == "__main__":
    main()
