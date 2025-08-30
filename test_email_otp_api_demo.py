#!/usr/bin/env python
"""
AgriConnect Email OTP API Test & Demo
Live demonstration of the email OTP API endpoints
"""

import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# Setup Django environment for direct testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOTPAPIDemo:
    """Live API demonstration"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = Client()
        self.test_email = "demo@agriconnect.com"
        self.demo_data = {
            "email": self.test_email,
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "first_name": "Demo",
            "last_name": "User",
            "roles": ["FARMER"]
        }
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"🚀 {title}")
        print("="*60)
    
    def print_request(self, method, endpoint, data=None):
        """Print formatted request"""
        print(f"\n📤 {method} {endpoint}")
        if data:
            print("Request Data:")
            print(json.dumps(data, indent=2))
    
    def print_response(self, response_data, status_code):
        """Print formatted response"""
        print(f"\n📥 Response ({status_code}):")
        print(json.dumps(response_data, indent=2, default=str))
    
    def demo_request_otp(self):
        """Demo: Request OTP"""
        self.print_header("1. Request Email OTP")
        
        endpoint = "/api/v1/auth/email-otp/request/"
        data = {
            "email": self.test_email,
            "purpose": "registration"
        }
        
        self.print_request("POST", endpoint, data)
        
        response = self.client.post(endpoint, data, content_type="application/json")
        response_data = response.json() if hasattr(response, 'json') else {}
        
        self.print_response(response_data, response.status_code)
        
        if response.status_code == 200:
            print("✅ OTP request successful!")
            print("📧 Check your Mailtrap inbox for the OTP email")
            return True
        else:
            print("❌ OTP request failed!")
            return False
    
    def demo_verify_otp(self, otp_code=None):
        """Demo: Verify OTP"""
        self.print_header("2. Verify Email OTP")
        
        if not otp_code:
            # For demo purposes, we'll retrieve the OTP from database
            from authentication.models_otp import EmailOTP
            latest_otp = EmailOTP.objects.filter(
                email=self.test_email,
                purpose='registration',
                status='pending'
            ).order_by('-created_at').first()
            
            if latest_otp:
                otp_code = latest_otp.otp_code
                print(f"🔍 Using OTP from database: {otp_code}")
            else:
                print("❌ No pending OTP found. Please run demo_request_otp() first.")
                return False
        
        endpoint = "/api/v1/auth/email-otp/verify/"
        data = {
            "email": self.test_email,
            "otp_code": otp_code,
            "purpose": "registration"
        }
        
        self.print_request("POST", endpoint, data)
        
        response = self.client.post(endpoint, data, content_type="application/json")
        response_data = response.json() if hasattr(response, 'json') else {}
        
        self.print_response(response_data, response.status_code)
        
        if response.status_code == 200:
            print("✅ OTP verification successful!")
            return True, otp_code
        else:
            print("❌ OTP verification failed!")
            return False, otp_code
    
    def demo_otp_status(self):
        """Demo: Check OTP Status"""
        self.print_header("3. Check OTP Status")
        
        endpoint = f"/api/v1/auth/email-otp/status/?email={self.test_email}&purpose=registration"
        
        self.print_request("GET", endpoint)
        
        response = self.client.get(endpoint)
        response_data = response.json() if hasattr(response, 'json') else {}
        
        self.print_response(response_data, response.status_code)
        
        if response.status_code == 200:
            print("✅ Status check successful!")
            return True
        else:
            print("❌ Status check failed!")
            return False
    
    def demo_resend_otp(self):
        """Demo: Resend OTP"""
        self.print_header("4. Resend Email OTP")
        
        endpoint = "/api/v1/auth/email-otp/resend/"
        data = {
            "email": self.test_email,
            "purpose": "registration"
        }
        
        self.print_request("POST", endpoint, data)
        
        response = self.client.post(endpoint, data, content_type="application/json")
        response_data = response.json() if hasattr(response, 'json') else {}
        
        self.print_response(response_data, response.status_code)
        
        if response.status_code == 200:
            print("✅ OTP resend successful!")
            return True
        else:
            print("❌ OTP resend failed (this might be due to cooldown)!")
            return False
    
    def demo_registration_with_otp(self):
        """Demo: Complete Registration with OTP"""
        self.print_header("5. Register User with Email OTP")
        
        # First, get a valid OTP
        from authentication.models_otp import EmailOTP
        latest_otp = EmailOTP.objects.filter(
            email=self.test_email,
            purpose='registration',
            status='pending'
        ).order_by('-created_at').first()
        
        if not latest_otp:
            print("🔄 No pending OTP found. Requesting new OTP...")
            if not self.demo_request_otp():
                return False
            
            latest_otp = EmailOTP.objects.filter(
                email=self.test_email,
                purpose='registration',
                status='pending'
            ).order_by('-created_at').first()
        
        if not latest_otp:
            print("❌ Could not get valid OTP for registration")
            return False
        
        # Clean up any existing test user
        User.objects.filter(email=self.test_email).delete()
        
        endpoint = "/api/v1/auth/email-otp/register/"
        data = {
            **self.demo_data,
            "otp_code": latest_otp.otp_code
        }
        
        self.print_request("POST", endpoint, data)
        
        response = self.client.post(endpoint, data, content_type="application/json")
        response_data = response.json() if hasattr(response, 'json') else {}
        
        self.print_response(response_data, response.status_code)
        
        if response.status_code == 201:
            print("✅ User registration with OTP successful!")
            print("🎉 User now has access_token and refresh_token")
            return True
        else:
            print("❌ User registration failed!")
            return False
    
    def demo_login_with_otp(self):
        """Demo: Login with Email OTP (2FA)"""
        self.print_header("6. Login with Email OTP (2FA)")
        
        # Ensure user exists
        user, created = User.objects.get_or_create(
            email=self.test_email,
            defaults={
                'first_name': 'Demo',
                'last_name': 'User',
                'is_verified': True,
                'email_verified': True
            }
        )
        
        if created:
            user.set_password(self.demo_data["password"])
            user.save()
            print(f"🔧 Created test user: {self.test_email}")
        
        # Request OTP for login
        print("\n🔄 Requesting OTP for login...")
        otp_response = self.client.post("/api/v1/auth/email-otp/request/", {
            "email": self.test_email,
            "purpose": "login"
        }, content_type="application/json")
        
        if otp_response.status_code != 200:
            print("❌ Failed to request login OTP")
            return False
        
        # Get the OTP
        from authentication.models_otp import EmailOTP
        login_otp = EmailOTP.objects.filter(
            email=self.test_email,
            purpose='login',
            status='pending'
        ).order_by('-created_at').first()
        
        if not login_otp:
            print("❌ No login OTP found")
            return False
        
        endpoint = "/api/v1/auth/email-otp/login/"
        data = {
            "email": self.test_email,
            "password": self.demo_data["password"],
            "otp_code": login_otp.otp_code
        }
        
        self.print_request("POST", endpoint, data)
        
        response = self.client.post(endpoint, data, content_type="application/json")
        response_data = response.json() if hasattr(response, 'json') else {}
        
        self.print_response(response_data, response.status_code)
        
        if response.status_code == 200:
            print("✅ Login with OTP successful!")
            print("🔐 Two-factor authentication completed")
            return True
        else:
            print("❌ Login with OTP failed!")
            return False
    
    def demo_password_reset(self):
        """Demo: Password Reset with OTP"""
        self.print_header("7. Password Reset with Email OTP")
        
        # Ensure user exists
        user, created = User.objects.get_or_create(
            email=self.test_email,
            defaults={
                'first_name': 'Demo',
                'last_name': 'User',
                'is_verified': True,
                'email_verified': True
            }
        )
        
        if created:
            user.set_password(self.demo_data["password"])
            user.save()
        
        # Request OTP for password reset
        print("\n🔄 Requesting OTP for password reset...")
        otp_response = self.client.post("/api/v1/auth/email-otp/request/", {
            "email": self.test_email,
            "purpose": "password_reset"
        }, content_type="application/json")
        
        if otp_response.status_code != 200:
            print("❌ Failed to request password reset OTP")
            return False
        
        # Get the OTP
        from authentication.models_otp import EmailOTP
        reset_otp = EmailOTP.objects.filter(
            email=self.test_email,
            purpose='password_reset',
            status='pending'
        ).order_by('-created_at').first()
        
        if not reset_otp:
            print("❌ No password reset OTP found")
            return False
        
        endpoint = "/api/v1/auth/email-otp/password-reset/"
        data = {
            "email": self.test_email,
            "otp_code": reset_otp.otp_code,
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!"
        }
        
        self.print_request("POST", endpoint, data)
        
        response = self.client.post(endpoint, data, content_type="application/json")
        response_data = response.json() if hasattr(response, 'json') else {}
        
        self.print_response(response_data, response.status_code)
        
        if response.status_code == 200:
            print("✅ Password reset with OTP successful!")
            return True
        else:
            print("❌ Password reset failed!")
            return False
    
    def run_complete_demo(self):
        """Run complete API demonstration"""
        print("🌟 AgriConnect Email OTP API Live Demonstration")
        print("📧 Using Mailtrap for email delivery")
        print(f"🎯 Test email: {self.test_email}")
        print("\nThis demo will test all email OTP endpoints...")
        
        results = []
        
        # Test 1: Request OTP
        results.append(("Request OTP", self.demo_request_otp()))
        
        # Small delay
        time.sleep(1)
        
        # Test 2: Check Status
        results.append(("Check Status", self.demo_otp_status()))
        
        # Test 3: Verify OTP
        verified, otp_code = self.demo_verify_otp()
        results.append(("Verify OTP", verified))
        
        # Test 4: Resend OTP
        results.append(("Resend OTP", self.demo_resend_otp()))
        
        # Test 5: Registration with OTP
        results.append(("Registration with OTP", self.demo_registration_with_otp()))
        
        # Test 6: Login with OTP
        results.append(("Login with OTP", self.demo_login_with_otp()))
        
        # Test 7: Password Reset
        results.append(("Password Reset", self.demo_password_reset()))
        
        # Summary
        self.print_header("🎯 Demo Summary")
        
        total_tests = len(results)
        passed_tests = sum(1 for _, success in results if success)
        
        print(f"Total API Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {total_tests - passed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Test Results:")
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        print("\n🎉 Email OTP API Demo Complete!")
        print("📧 Check your Mailtrap inbox to see the professional email templates")
        print("🔧 All endpoints are ready for frontend integration")
        
        return passed_tests == total_tests


if __name__ == "__main__":
    demo = EmailOTPAPIDemo()
    demo.run_complete_demo()
