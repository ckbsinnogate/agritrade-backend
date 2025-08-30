#!/usr/bin/env python
"""
Test Frontend Email OTP Flow
Tests the complete frontend registration flow to ensure emails are sent to Mailtrap
"""
import os
import sys
import django
import requests
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
sys.path.insert(0, os.path.abspath('.'))
django.setup()

from django.contrib.auth import get_user_model
from authentication.models import OTPCode
from authentication.models_otp import EmailOTP

User = get_user_model()

class FrontendEmailFlowTester:
    def __init__(self):
        self.api_base = "http://localhost:8000/api/v1"
        self.test_email = "frontendtest@agriconnect.com"
        self.test_data = {
            "email": self.test_email,
            "password": "TestPassword123!",
            "first_name": "Frontend",
            "last_name": "TestUser",
            "country": "Ghana",
            "region": "Greater Accra",
            "roles": ["CONSUMER"]
        }
        
    def cleanup_test_data(self):
        """Clean up any existing test data"""
        try:
            User.objects.filter(email=self.test_email).delete()
            OTPCode.objects.filter(email=self.test_email).delete()
            EmailOTP.objects.filter(email=self.test_email).delete()
            print("🧹 Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def print_header(self, title):
        print(f"\n{'=' * 50}")
        print(f"🧪 {title}")
        print('=' * 50)
    
    def test_frontend_registration(self):
        """Test the frontend registration endpoint that was having issues"""
        self.print_header("Frontend Registration Test")
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/register-frontend/",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(self.test_data)
            )
            
            print(f"📡 Request Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("✅ Registration successful!")
                print(f"📧 Contact Value: {data.get('contact_value')}")
                print(f"🔐 OTP Required: {data.get('otp_required')}")
                print(f"👤 User ID: {data.get('user_id')}")
                return data.get('contact_value')
            else:
                print("❌ Registration failed!")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return None
    
    def check_otp_creation(self):
        """Check if OTP was created properly"""
        self.print_header("OTP Creation Check")
        
        # Check old OTP system
        old_otp = OTPCode.objects.filter(email=self.test_email).order_by('-created_at').first()
        if old_otp:
            print(f"📜 Old OTP System: {old_otp.code}")
            
        # Check new Email OTP system
        email_otp = EmailOTP.objects.filter(email=self.test_email).order_by('-created_at').first()
        if email_otp:
            print(f"📧 Email OTP System: {email_otp.otp_code}")
            print(f"📧 Status: {email_otp.status}")
            print(f"📧 Purpose: {email_otp.purpose}")
            return email_otp.otp_code
        else:
            print("⚠️ No Email OTP found")
            
        return old_otp.code if old_otp else None
    
    def test_otp_verification(self, contact_value, otp_code):
        """Test OTP verification with the obtained OTP"""
        self.print_header("OTP Verification Test")
        
        if not otp_code:
            print("❌ No OTP code to test")
            return False
            
        verification_data = {
            "identifier": contact_value,
            "otp_code": otp_code,
            "purpose": "registration"
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/verify-otp/",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(verification_data)
            )
            
            print(f"📡 Request Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ OTP verification successful!")
                print(f"🎫 Access Token: {data.get('access', 'N/A')[:20]}...")
                return True
            else:
                print("❌ OTP verification failed!")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
    
    def check_email_sending_logs(self):
        """Check if emails were actually sent"""
        self.print_header("Email Sending Verification")
        
        # Count total email OTPs sent today
        from django.utils import timezone
        from datetime import datetime
        
        today = timezone.now().date()
        total_sent = EmailOTP.objects.filter(
            created_at__date=today,
            status__in=['pending', 'verified']
        ).count()
        
        print(f"📊 Total Email OTPs sent today: {total_sent}")
        
        # Check our specific test email
        test_otps = EmailOTP.objects.filter(email=self.test_email).order_by('-created_at')
        
        for otp in test_otps:
            print(f"📧 OTP {otp.otp_code}: {otp.status} at {otp.created_at}")
            
        if test_otps:
            print("✅ Email OTP records found - emails should be sent to Mailtrap")
            print("📬 Check your Mailtrap inbox for the professional email")
        else:
            print("⚠️ No Email OTP records found")
    
    def run_complete_test(self):
        """Run the complete frontend email flow test"""
        print("🚀 Frontend Email OTP Flow Test")
        print("Testing the complete registration → OTP → verification flow")
        
        # Cleanup first
        self.cleanup_test_data()
        
        # Step 1: Register user
        contact_value = self.test_frontend_registration()
        if not contact_value:
            print("❌ Test failed at registration step")
            return False
            
        # Step 2: Check OTP creation
        time.sleep(1)  # Allow time for OTP creation
        otp_code = self.check_otp_creation()
        
        # Step 3: Verify OTP
        verification_success = self.test_otp_verification(contact_value, otp_code)
        
        # Step 4: Check email sending
        self.check_email_sending_logs()
        
        # Summary
        self.print_header("Test Summary")
        if verification_success:
            print("🎉 SUCCESS: Frontend email OTP flow is working!")
            print("📧 Emails should now be sent to Mailtrap instead of just logged")
            print("📬 Check Mailtrap inbox: https://mailtrap.io/inboxes")
        else:
            print("❌ FAILED: Issues detected in the frontend flow")
            
        return verification_success

if __name__ == "__main__":
    tester = FrontendEmailFlowTester()
    tester.run_complete_test()
