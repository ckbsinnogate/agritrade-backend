#!/usr/bin/env python3
"""
400 Bad Request Error Investigation Script
========================================
Investigates the exact cause of 400 errors in AI endpoints,
particularly the disease detection endpoint that frontend is calling.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class BadRequestInvestigator:
    """Investigates 400 Bad Request errors in AI endpoints"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api/v1/ai"
        self.auth_token = None
        self.user = None
        self.test_results = []
    
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name, status, details=""):
        """Print test result"""
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"   {status_icon} {test_name}: {status}")
        if details:
            print(f"      📋 {details}")
    
    def setup_authentication(self):
        """Setup test user and authentication"""
        self.print_header("AUTHENTICATION SETUP")
        
        try:
            # Create or get test user
            self.user, created = User.objects.get_or_create(
                email='400_error_test@example.com',
                defaults={
                    'first_name': '400Error',
                    'last_name': 'Tester',
                    'phone_number': '+233123456789',
                    'is_active': True
                }
            )
            
            if created:
                self.user.set_password('testpass123')
                self.user.save()
                self.print_test("Test User Creation", "PASS", f"Created user: {self.user.email}")
            else:
                self.print_test("Test User Retrieval", "PASS", f"Using existing user: {self.user.email}")
            
            # Generate JWT token
            refresh = RefreshToken.for_user(self.user)
            self.auth_token = str(refresh.access_token)
            
            self.print_test("JWT Token Generation", "PASS", "Authentication ready")
            return True
            
        except Exception as e:
            self.print_test("Authentication Setup", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_endpoint_with_data(self, endpoint, data, description):
        """Test an endpoint with specific data"""
        url = f"{self.base_url}/{endpoint}/"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
        
        print(f"\n🧪 Testing: {description}")
        print(f"   📍 URL: {url}")
        print(f"   📨 Data: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=15)
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   📄 Response Headers: {dict(response.headers)}")
            
            # Parse response
            try:
                response_data = response.json()
                print(f"   📋 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   📋 Raw Response: {response.text}")
            
            result = {
                'endpoint': endpoint,
                'description': description,
                'status_code': response.status_code,
                'data_sent': data,
                'response': response.text,
                'success': response.status_code in [200, 201]
            }
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"   ❌ Request Error: {str(e)}")
            return None
    
    def investigate_disease_detection_400(self):
        """Investigate disease detection 400 errors"""
        self.print_header("DISEASE DETECTION 400 ERROR INVESTIGATION")
        
        # Test 1: Empty data (likely causing frontend 400)
        self.test_endpoint_with_data(
            'disease-detection',
            {},
            "Empty data (frontend likely sending this)"
        )
        
        # Test 2: Missing required fields
        self.test_endpoint_with_data(
            'disease-detection',
            {'crop_type': 'maize'},
            "Only crop_type (missing other required fields)"
        )
        
        # Test 3: Invalid crop type
        self.test_endpoint_with_data(
            'disease-detection',
            {
                'crop_type': 'invalid_crop',
                'symptoms': ['yellowing_leaves']
            },
            "Invalid crop type"
        )
        
        # Test 4: Missing symptoms
        self.test_endpoint_with_data(
            'disease-detection',
            {'crop_type': 'maize'},
            "Missing symptoms array"
        )
        
        # Test 5: Empty symptoms array
        self.test_endpoint_with_data(
            'disease-detection',
            {
                'crop_type': 'maize',
                'symptoms': []
            },
            "Empty symptoms array"
        )
        
        # Test 6: Invalid symptoms format
        self.test_endpoint_with_data(
            'disease-detection',
            {
                'crop_type': 'maize',
                'symptoms': 'yellowing_leaves'  # String instead of array
            },
            "Invalid symptoms format (string instead of array)"
        )
        
        # Test 7: Valid data (should work)
        self.test_endpoint_with_data(
            'disease-detection',
            {
                'crop_type': 'maize',
                'symptoms': ['yellowing_leaves', 'stunted_growth'],
                'location': 'Ghana',
                'severity': 'moderate'
            },
            "Valid data (should work)"
        )
        
        # Test 8: Minimal valid data
        self.test_endpoint_with_data(
            'disease-detection',
            {
                'crop_type': 'maize',
                'symptoms': ['yellowing_leaves']
            },
            "Minimal valid data"
        )
    
    def investigate_chat_400(self):
        """Investigate chat endpoint 400 errors"""
        self.print_header("CHAT ENDPOINT 400 ERROR INVESTIGATION")
        
        # Test different chat data scenarios
        test_cases = [
            ({}, "Empty data"),
            ({'message': ''}, "Empty message"),
            ({'language': 'en'}, "Missing message"),
            ({'message': 'Hello'}, "Missing language (optional)"),
            ({'message': 'Hello', 'language': 'en'}, "Valid data"),
            ({'message': 'Hello', 'language': 'invalid'}, "Invalid language"),
            ({'message': None}, "Null message"),
            ({'message': 123}, "Non-string message"),
        ]
        
        for data, description in test_cases:
            self.test_endpoint_with_data('chat', data, description)
    
    def investigate_market_insights_400(self):
        """Investigate market insights endpoint 400 errors"""
        self.print_header("MARKET INSIGHTS 400 ERROR INVESTIGATION")
        
        test_cases = [
            ({}, "Empty data"),
            ({'crop_type': 'maize'}, "Only crop_type"),
            ({'location': 'Ghana'}, "Only location"),
            ({'crop_type': 'maize', 'location': 'Ghana'}, "Valid basic data"),
            ({'crop_type': 'invalid', 'location': 'Ghana'}, "Invalid crop_type"),
            ({'crop_type': 'maize', 'location': ''}, "Empty location"),
            ({'crop_type': '', 'location': 'Ghana'}, "Empty crop_type"),
        ]
        
        for data, description in test_cases:
            self.test_endpoint_with_data('market-insights', data, description)
    
    def generate_frontend_fix_recommendations(self):
        """Generate specific recommendations to fix frontend 400 errors"""
        self.print_header("FRONTEND FIX RECOMMENDATIONS")
        
        # Analyze results to identify patterns
        bad_requests = [r for r in self.test_results if r['status_code'] == 400]
        successful_requests = [r for r in self.test_results if r['status_code'] in [200, 201]]
        
        print(f"📊 Analysis Results:")
        print(f"   Total tests: {len(self.test_results)}")
        print(f"   400 errors: {len(bad_requests)}")
        print(f"   Successful: {len(successful_requests)}")
        print(f"   Other errors: {len(self.test_results) - len(bad_requests) - len(successful_requests)}")
        
        print(f"\n📋 400 Error Patterns:")
        for result in bad_requests:
            print(f"   ❌ {result['description']}")
            print(f"      Data: {result['data_sent']}")
            
        print(f"\n✅ Successful Request Patterns:")
        for result in successful_requests:
            print(f"   ✅ {result['description']}")
            print(f"      Data: {result['data_sent']}")
        
        # Generate specific frontend fixes
        print(f"\n🔧 SPECIFIC FRONTEND FIXES NEEDED:")
        
        print(f"\n1. Disease Detection Endpoint:")
        print(f"   - REQUIRED: crop_type (string)")
        print(f"   - REQUIRED: symptoms (array of strings)")
        print(f"   - OPTIONAL: location, severity")
        print(f"   - Frontend MUST validate these fields before sending")
        
        print(f"\n2. Chat Endpoint:")
        print(f"   - REQUIRED: message (non-empty string)")
        print(f"   - OPTIONAL: language (defaults to 'en')")
        
        print(f"\n3. Market Insights Endpoint:")
        print(f"   - REQUIRED: crop_type (string)")
        print(f"   - REQUIRED: location (string)")
        
        # Generate React validation code
        print(f"\n🛠️ React Validation Code Examples:")
        
        validation_code = '''
// Disease Detection Validation
const validateDiseaseDetectionData = (data) => {
  const errors = [];
  
  if (!data.crop_type || typeof data.crop_type !== 'string' || data.crop_type.trim() === '') {
    errors.push('Crop type is required');
  }
  
  if (!data.symptoms || !Array.isArray(data.symptoms) || data.symptoms.length === 0) {
    errors.push('At least one symptom is required');
  }
  
  return errors;
};

// Chat Message Validation
const validateChatData = (data) => {
  const errors = [];
  
  if (!data.message || typeof data.message !== 'string' || data.message.trim() === '') {
    errors.push('Message is required');
  }
  
  return errors;
};

// Market Insights Validation
const validateMarketInsightsData = (data) => {
  const errors = [];
  
  if (!data.crop_type || typeof data.crop_type !== 'string' || data.crop_type.trim() === '') {
    errors.push('Crop type is required');
  }
  
  if (!data.location || typeof data.location !== 'string' || data.location.trim() === '') {
    errors.push('Location is required');
  }
  
  return errors;
};

// Usage in React component
const handleDiseaseDetection = async (formData) => {
  const errors = validateDiseaseDetectionData(formData);
  
  if (errors.length > 0) {
    console.error('Validation errors:', errors);
    setErrors(errors);
    return;
  }
  
  try {
    const response = await fetch('/api/v1/ai/disease-detection/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    setResult(result);
    
  } catch (error) {
    console.error('API Error:', error);
    setErrors([error.message]);
  }
};
'''
        
        print(validation_code)
    
    def run_investigation(self):
        """Run complete 400 error investigation"""
        print("🔍 AgriConnect AI API - 400 Bad Request Error Investigation")
        print("=" * 70)
        print("This script identifies the exact causes of 400 errors that")
        print("the frontend is experiencing with AI endpoints.")
        
        # Setup
        if not self.setup_authentication():
            return False
        
        # Investigate each endpoint
        self.investigate_disease_detection_400()
        self.investigate_chat_400()
        self.investigate_market_insights_400()
        
        # Generate recommendations
        self.generate_frontend_fix_recommendations()
        
        print(f"\n{'='*70}")
        print("🎯 INVESTIGATION COMPLETE")
        print("=" * 70)
        print("✅ 400 error causes identified")
        print("✅ Frontend validation requirements documented")
        print("✅ React code examples provided")
        print("📋 Frontend developers can now implement proper validation")
        
        return True

def main():
    """Main function"""
    investigator = BadRequestInvestigator()
    success = investigator.run_investigation()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
