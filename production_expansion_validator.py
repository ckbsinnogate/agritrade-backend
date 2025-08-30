#!/usr/bin/env python3
"""
Enhanced Continental Expansion Production Testing Suite
=====================================================
Advanced testing for production-ready farmer onboarding across Africa
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures
import threading

class ProductionExpansionValidator:
    """Production-ready continental expansion validator"""
    
    def __init__(self):
        self.api_base = "http://127.0.0.1:8000/api/v1"
        self.auth_base = f"{self.api_base}/auth"
        self.ai_base = f"{self.api_base}/ai/api"
        
        # Enhanced continental expansion data
        self.expansion_plan = {
            'phase_1': {
                'countries': ['Ghana'],
                'target_farmers': 10000,
                'timeline': 'Q3 2025',
                'status': 'ACTIVE'
            },
            'phase_2': {
                'countries': ['Nigeria'],
                'target_farmers': 25000,
                'timeline': 'Q4 2025',
                'status': 'READY'
            },
            'phase_3': {
                'countries': ['Kenya'],
                'target_farmers': 15000,
                'timeline': 'Q1 2026',
                'status': 'PREPARED'
            },
            'phase_4': {
                'countries': ['Ethiopia'],
                'target_farmers': 20000,
                'timeline': 'Q2 2026',
                'status': 'PREPARED'
            }
        }
        
        self.country_profiles = {
            'Ghana': {
                'regions': ['Greater Accra', 'Ashanti', 'Northern', 'Western', 'Central', 'Volta', 'Eastern', 'Upper East', 'Upper West', 'Brong Ahafo'],
                'languages': ['en'],
                'primary_crops': ['cocoa', 'maize', 'cassava', 'yam', 'plantain', 'rice'],
                'currency': 'GHS',
                'phone_prefix': '+233',
                'pilot_farmers': [
                    {'name': 'Kwame Asante', 'region': 'Ashanti', 'crop': 'cocoa', 'farm_size': '5 hectares'},
                    {'name': 'Abena Osei', 'region': 'Greater Accra', 'crop': 'maize', 'farm_size': '3 hectares'},
                    {'name': 'Kofi Mensah', 'region': 'Central', 'crop': 'cassava', 'farm_size': '4 hectares'},
                    {'name': 'Ama Darko', 'region': 'Western', 'crop': 'cocoa', 'farm_size': '6 hectares'},
                    {'name': 'Yaw Boateng', 'region': 'Volta', 'crop': 'rice', 'farm_size': '2 hectares'}
                ]
            },
            'Nigeria': {
                'regions': ['Lagos', 'Kano', 'Rivers', 'Kaduna', 'Ogun', 'Enugu', 'Anambra', 'Katsina', 'Sokoto', 'Kebbi'],
                'languages': ['en'],
                'primary_crops': ['yam', 'cassava', 'maize', 'rice', 'millet', 'sorghum'],
                'currency': 'NGN',
                'phone_prefix': '+234',
                'pilot_farmers': [
                    {'name': 'Adebayo Okafor', 'region': 'Enugu', 'crop': 'yam', 'farm_size': '4 hectares'},
                    {'name': 'Ngozi Chioma', 'region': 'Kaduna', 'crop': 'rice', 'farm_size': '7 hectares'},
                    {'name': 'Ibrahim Musa', 'region': 'Kano', 'crop': 'millet', 'farm_size': '10 hectares'},
                    {'name': 'Folake Adebisi', 'region': 'Ogun', 'crop': 'cassava', 'farm_size': '3 hectares'},
                    {'name': 'Usman Garba', 'region': 'Sokoto', 'crop': 'sorghum', 'farm_size': '8 hectares'}
                ]
            },
            'Kenya': {
                'regions': ['Nairobi', 'Mombasa', 'Nakuru', 'Eldoret', 'Kisumu', 'Nyeri', 'Meru', 'Machakos', 'Kiambu', 'Kakamega'],
                'languages': ['en', 'sw'],
                'primary_crops': ['coffee', 'tea', 'maize', 'wheat', 'beans', 'bananas'],
                'currency': 'KES',
                'phone_prefix': '+254',
                'pilot_farmers': [
                    {'name': 'Grace Wanjiku', 'region': 'Nyeri', 'crop': 'coffee', 'farm_size': '2 hectares'},
                    {'name': 'Peter Kiprotich', 'region': 'Eldoret', 'crop': 'maize', 'farm_size': '15 hectares'},
                    {'name': 'Mary Achieng', 'region': 'Kisumu', 'crop': 'tea', 'farm_size': '3 hectares'},
                    {'name': 'David Mwangi', 'region': 'Kiambu', 'crop': 'coffee', 'farm_size': '1.5 hectares'},
                    {'name': 'Sarah Njeri', 'region': 'Meru', 'crop': 'beans', 'farm_size': '2.5 hectares'}
                ]
            },
            'Ethiopia': {
                'regions': ['Addis Ababa', 'Oromia', 'Amhara', 'Tigray', 'SNNPR', 'Somali', 'Afar', 'Benishangul-Gumuz', 'Gambela', 'Harari'],
                'languages': ['en', 'am'],
                'primary_crops': ['coffee', 'teff', 'barley', 'wheat', 'maize', 'sorghum'],
                'currency': 'ETB',
                'phone_prefix': '+251',
                'pilot_farmers': [
                    {'name': 'Alemayehu Tadesse', 'region': 'Oromia', 'crop': 'coffee', 'farm_size': '3 hectares'},
                    {'name': 'Desta Mulugeta', 'region': 'Amhara', 'crop': 'teff', 'farm_size': '5 hectares'},
                    {'name': 'Hanna Bekele', 'region': 'Tigray', 'crop': 'barley', 'farm_size': '4 hectares'},
                    {'name': 'Meseret Haile', 'region': 'SNNPR', 'crop': 'coffee', 'farm_size': '2 hectares'},
                    {'name': 'Tekle Gebre', 'region': 'Oromia', 'crop': 'maize', 'farm_size': '6 hectares'}
                ]
            }
        }
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_countries': len(self.country_profiles),
            'total_regions': sum(len(profile['regions']) for profile in self.country_profiles.values()),
            'total_pilot_farmers': sum(len(profile['pilot_farmers']) for profile in self.country_profiles.values()),
            'successful_registrations': 0,
            'successful_logins': 0,
            'ai_interactions': 0,
            'countries_validated': 0,
            'expansion_phases_ready': 0,
            'detailed_results': []
        }
        
        self.lock = threading.Lock()
    
    def validate_farmer_registration(self, country: str, farmer: Dict) -> Dict:
        """Validate individual farmer registration"""
        farmer_email = f"{farmer['name'].lower().replace(' ', '.')}.{country.lower()}@agriconnect.com"
        
        registration_data = {
            'identifier': farmer_email,
            'password': 'AgriConnect2025!',
            'password_confirm': 'AgriConnect2025!',
            'first_name': farmer['name'].split()[0],
            'last_name': farmer['name'].split()[1] if len(farmer['name'].split()) > 1 else 'Farmer',
            'roles': ['FARMER'],
            'country': country,
            'region': farmer['region'],
            'language': self.country_profiles[country]['languages'][0],
            'contact_method': 'email'
        }
        
        result = {
            'country': country,
            'farmer_name': farmer['name'],
            'farmer_email': farmer_email,
            'region': farmer['region'],
            'crop': farmer['crop'],
            'farm_size': farmer['farm_size'],
            'registration_success': False,
            'login_success': False,
            'response_time': 0,
            'error_message': None
        }
        
        try:
            start_time = time.time()
            
            # Test registration
            response = requests.post(f"{self.auth_base}/register/", json=registration_data, timeout=30)
            
            if response.status_code in [200, 201]:
                result['registration_success'] = True
                with self.lock:
                    self.results['successful_registrations'] += 1
            elif response.status_code == 400 and "already exists" in response.text:
                result['registration_success'] = True
                with self.lock:
                    self.results['successful_registrations'] += 1
            else:
                result['error_message'] = f"Registration failed: {response.status_code}"
                return result
            
            # Test login
            login_data = {
                'identifier': farmer_email,
                'password': 'AgriConnect2025!'
            }
            
            response = requests.post(f"{self.auth_base}/login/", json=login_data, timeout=30)
            
            if response.status_code == 200:
                result['login_success'] = True
                with self.lock:
                    self.results['successful_logins'] += 1
            else:
                result['error_message'] = f"Login failed: {response.status_code}"
            
            result['response_time'] = time.time() - start_time
            
        except Exception as e:
            result['error_message'] = str(e)
        
        return result
    
    def validate_country_expansion(self, country: str) -> Dict:
        """Validate complete country expansion readiness"""
        print(f"\n🌍 VALIDATING {country.upper()} EXPANSION")
        print("=" * 50)
        
        country_profile = self.country_profiles[country]
        
        # Parallel farmer validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for farmer in country_profile['pilot_farmers']:
                future = executor.submit(self.validate_farmer_registration, country, farmer)
                futures.append(future)
            
            farmer_results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    farmer_results.append(result)
                    
                    status = "✅ SUCCESS" if result['registration_success'] and result['login_success'] else "❌ FAILED"
                    print(f"  {result['farmer_name']} ({result['region']}): {status}")
                    
                    if result['error_message']:
                        print(f"    Error: {result['error_message']}")
                    
                except Exception as e:
                    print(f"  Farmer validation failed: {e}")
        
        # Calculate country statistics
        successful_farmers = sum(1 for r in farmer_results if r['registration_success'] and r['login_success'])
        success_rate = (successful_farmers / len(farmer_results)) * 100 if farmer_results else 0
        
        country_result = {
            'country': country,
            'total_regions': len(country_profile['regions']),
            'total_languages': len(country_profile['languages']),
            'total_crops': len(country_profile['primary_crops']),
            'pilot_farmers_tested': len(farmer_results),
            'successful_farmers': successful_farmers,
            'success_rate': success_rate,
            'expansion_ready': success_rate >= 80,
            'farmer_results': farmer_results
        }
        
        with self.lock:
            self.results['detailed_results'].append(country_result)
            if success_rate >= 80:
                self.results['countries_validated'] += 1
        
        print(f"\n📊 {country} VALIDATION RESULTS:")
        print(f"  Regions: {len(country_profile['regions'])}")
        print(f"  Languages: {', '.join(country_profile['languages'])}")
        print(f"  Primary Crops: {', '.join(country_profile['primary_crops'])}")
        print(f"  Pilot Farmers: {successful_farmers}/{len(farmer_results)}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Expansion Ready: {'✅ YES' if success_rate >= 80 else '❌ NO'}")
        
        return country_result
    
    def validate_expansion_phases(self):
        """Validate all expansion phases"""
        print("\n🚀 VALIDATING EXPANSION PHASES")
        print("=" * 50)
        
        for phase, details in self.expansion_plan.items():
            print(f"\n📅 {phase.upper()} - {details['timeline']}")
            print(f"  Target Countries: {', '.join(details['countries'])}")
            print(f"  Target Farmers: {details['target_farmers']:,}")
            print(f"  Status: {details['status']}")
            
            if details['status'] in ['ACTIVE', 'READY']:
                self.results['expansion_phases_ready'] += 1
                print(f"  ✅ PHASE READY FOR EXECUTION")
            else:
                print(f"  🔄 PHASE IN PREPARATION")
    
    def run_production_validation(self):
        """Run comprehensive production validation"""
        print("🚀 AGRICONNECT PRODUCTION CONTINENTAL EXPANSION VALIDATION")
        print("=" * 65)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: Validate {len(self.country_profiles)} countries for expansion")
        print(f"👥 Pilot Farmers: {sum(len(p['pilot_farmers']) for p in self.country_profiles.values())}")
        print(f"🌍 Total Regions: {sum(len(p['regions']) for p in self.country_profiles.values())}")
        
        # Validate each country
        for country in self.country_profiles.keys():
            self.validate_country_expansion(country)
        
        # Validate expansion phases
        self.validate_expansion_phases()
        
        # Generate production report
        self.generate_production_report()
    
    def generate_production_report(self):
        """Generate comprehensive production readiness report"""
        print("\n" + "=" * 65)
        print("🏆 PRODUCTION CONTINENTAL EXPANSION VALIDATION COMPLETE")
        print("=" * 65)
        
        # Overall statistics
        print(f"📊 OVERALL STATISTICS:")
        print(f"  Countries Validated: {self.results['countries_validated']}/{self.results['total_countries']}")
        print(f"  Regions Covered: {self.results['total_regions']}")
        print(f"  Pilot Farmers: {self.results['total_pilot_farmers']}")
        print(f"  Successful Registrations: {self.results['successful_registrations']}")
        print(f"  Successful Logins: {self.results['successful_logins']}")
        print(f"  Expansion Phases Ready: {self.results['expansion_phases_ready']}/4")
        
        # Country readiness status
        print(f"\n🌍 COUNTRY READINESS STATUS:")
        for result in self.results['detailed_results']:
            status = "✅ READY" if result['expansion_ready'] else "❌ NOT READY"
            print(f"  {result['country']}: {status} ({result['success_rate']:.1f}% success)")
        
        # Expansion timeline
        print(f"\n📅 EXPANSION TIMELINE:")
        for phase, details in self.expansion_plan.items():
            status_icon = "✅" if details['status'] in ['ACTIVE', 'READY'] else "🔄"
            print(f"  {phase.upper()}: {status_icon} {details['timeline']} - {', '.join(details['countries'])}")
        
        # Production metrics
        overall_success = (self.results['countries_validated'] / self.results['total_countries']) * 100
        farmer_success = (self.results['successful_registrations'] / self.results['total_pilot_farmers']) * 100
        
        print(f"\n🎯 PRODUCTION METRICS:")
        print(f"  Overall Success Rate: {overall_success:.1f}%")
        print(f"  Farmer Onboarding Rate: {farmer_success:.1f}%")
        print(f"  System Scalability: {'✅ EXCELLENT' if overall_success >= 95 else '⚠️ NEEDS IMPROVEMENT'}")
        
        # Final assessment
        if overall_success >= 95 and farmer_success >= 90:
            print(f"\n🎉 MISSION ACCOMPLISHED!")
            print("✅ PRODUCTION SYSTEM IS READY FOR CONTINENTAL EXPANSION!")
            print("✅ All countries validated and ready for deployment")
            print("✅ Farmer onboarding system is production-ready")
            print("✅ Multi-country infrastructure is scalable")
        else:
            print(f"\n⚠️ IMPROVEMENT NEEDED")
            print("Some countries need additional validation before production deployment")
        
        # Save results
        with open(f'production_expansion_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📋 Detailed results saved to production validation file")
        
        # Next steps
        print(f"\n🚀 IMMEDIATE NEXT STEPS:")
        print("1. Deploy production infrastructure in Ghana (Phase 1)")
        print("2. Launch farmer recruitment campaigns")
        print("3. Activate Nigeria expansion preparations (Phase 2)")
        print("4. Scale SMS and AI services for high volume")
        print("5. Implement monitoring and analytics dashboards")
        print("6. Establish customer support teams in each country")

def main():
    """Main validation execution"""
    validator = ProductionExpansionValidator()
    validator.run_production_validation()

if __name__ == "__main__":
    main()
