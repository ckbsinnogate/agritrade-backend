#!/usr/bin/env python
"""
Email OTP Test Script for AgriConnect
Test the complete email OTP functionality with Mailtrap integration
"""

import os
import sys
import django
import json
import time
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.conf import settings
from authentication.services_otp import EmailOTPService
from authentication.models_otp import EmailOTP, EmailOTPRateLimit


class EmailOTPTester:
    """Comprehensive email OTP testing suite"""
    
    def __init__(self):
        self.service = EmailOTPService()
        self.test_email = "test@agriconnect.com"
        self.results = []
    
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()
    
    def test_email_configuration(self):
        """Test email configuration"""
        try:
            config = {
                'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'Not set'),
                'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'Not set'),
                'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'Not set'),
                'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'Not set'),
                'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set'),
            }
            
            # Check if Mailtrap is configured
            is_mailtrap = 'mailtrap' in str(config['EMAIL_HOST']).lower()
            
            self.log_result(
                "Email Configuration",
                is_mailtrap,
                "Mailtrap email configuration detected" if is_mailtrap else "No Mailtrap configuration found",
                config
            )
            
            return is_mailtrap
            
        except Exception as e:
            self.log_result("Email Configuration", False, f"Configuration error: {str(e)}")
            return False
    
    def test_otp_generation(self):
        """Test OTP generation"""
        try:
            # Test different purposes
            purposes = ['registration', 'login', 'password_reset']
            
            for purpose in purposes:
                success, message, otp_instance = self.service.generate_and_send_otp(
                    email=self.test_email,
                    purpose=purpose,
                    ip_address="127.0.0.1",
                    user_agent="Email OTP Test Script"
                )
                
                details = {}
                if otp_instance:
                    details = {
                        'otp_code': otp_instance.otp_code,
                        'expires_at': otp_instance.expires_at.isoformat(),
                        'purpose': purpose
                    }
                
                self.log_result(
                    f"OTP Generation ({purpose})",
                    success,
                    message,
                    details
                )
                
                if success and otp_instance:
                    # Test OTP properties
                    self.log_result(
                        f"OTP Validation ({purpose})",
                        otp_instance.is_valid(),
                        f"OTP is {'valid' if otp_instance.is_valid() else 'invalid'}",
                        {
                            'code_length': len(otp_instance.otp_code),
                            'is_numeric': otp_instance.otp_code.isdigit(),
                            'expires_in_minutes': int((otp_instance.expires_at - otp_instance.created_at).total_seconds() / 60)
                        }
                    )
                
                # Small delay between tests
                time.sleep(1)
                
        except Exception as e:
            self.log_result("OTP Generation", False, f"Generation error: {str(e)}")
    
    def test_otp_verification(self):
        """Test OTP verification"""
        try:
            # Generate an OTP first
            success, message, otp_instance = self.service.generate_and_send_otp(
                email=self.test_email,
                purpose='registration',
                ip_address="127.0.0.1"
            )
            
            if success and otp_instance:
                # Test correct verification
                verify_success, verify_message, verified_otp = self.service.verify_otp(
                    email=self.test_email,
                    otp_code=otp_instance.otp_code,
                    purpose='registration',
                    ip_address="127.0.0.1"
                )
                
                self.log_result(
                    "OTP Verification (Correct)",
                    verify_success,
                    verify_message,
                    {
                        'attempted_code': otp_instance.otp_code,
                        'verification_status': verified_otp.status if verified_otp else 'None'
                    }
                )
                
                # Test incorrect verification
                wrong_success, wrong_message, wrong_otp = self.service.verify_otp(
                    email=self.test_email,
                    otp_code="000000",  # Wrong code
                    purpose='registration',
                    ip_address="127.0.0.1"
                )
                
                self.log_result(
                    "OTP Verification (Incorrect)",
                    not wrong_success,  # We expect this to fail
                    wrong_message,
                    {
                        'attempted_code': "000000",
                        'expected_result': 'failure'
                    }
                )
            else:
                self.log_result("OTP Verification", False, "Could not generate OTP for verification test")
                
        except Exception as e:
            self.log_result("OTP Verification", False, f"Verification error: {str(e)}")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        try:
            test_email = "rate_test@agriconnect.com"
            
            # Clear any existing rate limits
            EmailOTPRateLimit.objects.filter(email=test_email).delete()
            
            # Send multiple OTPs quickly to test rate limiting
            send_count = 0
            rate_limited = False
            
            for i in range(6):  # Try to send 6 OTPs
                success, message, otp_instance = self.service.generate_and_send_otp(
                    email=test_email,
                    purpose='registration',
                    ip_address="127.0.0.1"
                )
                
                if success:
                    send_count += 1
                else:
                    if "rate limit" in message.lower() or "limit exceeded" in message.lower():
                        rate_limited = True
                        break
                
                time.sleep(0.1)  # Small delay
            
            self.log_result(
                "Rate Limiting",
                rate_limited or send_count < 6,
                f"Rate limiting {'activated' if rate_limited else 'not activated'} after {send_count} sends",
                {
                    'total_sends': send_count,
                    'rate_limited': rate_limited,
                    'last_message': message
                }
            )
            
        except Exception as e:
            self.log_result("Rate Limiting", False, f"Rate limiting error: {str(e)}")
    
    def test_otp_expiry(self):
        """Test OTP expiry functionality"""
        try:
            # Generate an OTP
            success, message, otp_instance = self.service.generate_and_send_otp(
                email=self.test_email,
                purpose='registration',
                ip_address="127.0.0.1"
            )
            
            if success and otp_instance:
                # Check if OTP is initially valid
                is_valid_before = otp_instance.is_valid()
                
                # Manually expire the OTP by setting expires_at to past
                from django.utils import timezone
                from datetime import timedelta
                
                otp_instance.expires_at = timezone.now() - timedelta(minutes=1)
                otp_instance.save()
                
                # Refresh from database
                otp_instance.refresh_from_db()
                is_expired = otp_instance.is_expired()
                is_valid_after = otp_instance.is_valid()
                
                self.log_result(
                    "OTP Expiry",
                    is_valid_before and is_expired and not is_valid_after,
                    "OTP expiry mechanism working correctly",
                    {
                        'valid_before_expiry': is_valid_before,
                        'is_expired': is_expired,
                        'valid_after_expiry': is_valid_after
                    }
                )
            else:
                self.log_result("OTP Expiry", False, "Could not generate OTP for expiry test")
                
        except Exception as e:
            self.log_result("OTP Expiry", False, f"Expiry test error: {str(e)}")
    
    def test_cleanup_function(self):
        """Test the cleanup function"""
        try:
            initial_count = EmailOTP.objects.count()
            
            # Run cleanup
            self.service.cleanup_expired_otps()
            
            after_cleanup_count = EmailOTP.objects.count()
            
            self.log_result(
                "OTP Cleanup",
                True,  # Cleanup should always succeed
                "Cleanup function executed successfully",
                {
                    'otps_before_cleanup': initial_count,
                    'otps_after_cleanup': after_cleanup_count,
                    'otps_cleaned': initial_count - after_cleanup_count
                }
            )
            
        except Exception as e:
            self.log_result("OTP Cleanup", False, f"Cleanup error: {str(e)}")
    
    def test_statistics(self):
        """Test statistics functionality"""
        try:
            stats = self.service.get_otp_statistics()
            
            expected_keys = ['total_sent', 'verified', 'expired', 'failed', 'pending', 'success_rate', 'by_purpose']
            has_all_keys = all(key in stats for key in expected_keys)
            
            self.log_result(
                "OTP Statistics",
                has_all_keys,
                "Statistics generated successfully",
                stats
            )
            
        except Exception as e:
            self.log_result("OTP Statistics", False, f"Statistics error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AgriConnect Email OTP Test Suite")
        print("=" * 60)
        print()
        
        # Run tests
        self.test_email_configuration()
        self.test_otp_generation()
        self.test_otp_verification()
        self.test_rate_limiting()
        self.test_otp_expiry()
        self.test_cleanup_function()
        self.test_statistics()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
            print()
        
        # Email configuration reminder
        print("📧 EMAIL CONFIGURATION:")
        print(f"HOST: {getattr(settings, 'EMAIL_HOST', 'Not configured')}")
        print(f"PORT: {getattr(settings, 'EMAIL_PORT', 'Not configured')}")
        print(f"USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not configured')}")
        print()
        
        print("🎯 Next Steps:")
        print("1. Check your Mailtrap inbox for test emails")
        print("2. Test the API endpoints using the frontend integration guide")
        print("3. Monitor the email OTP logs for any issues")
        print()
        
        return passed_tests == total_tests


if __name__ == "__main__":
    tester = EmailOTPTester()
    success = tester.run_all_tests()
    
    # Save results to file
    with open('email_otp_test_results.json', 'w') as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"📄 Test results saved to: email_otp_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
