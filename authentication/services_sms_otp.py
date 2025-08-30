"""
AgriConnect SMS OTP Service
Professional SMS OTP implementation using AVRSMS API
Integrates with existing authentication system
"""

import logging
import time
import secrets
import string
from typing import Dict, Optional, Tuple, Any, TYPE_CHECKING
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

from .models import OTPCode
from communications.services import AVRSMSService

User = get_user_model()
logger = logging.getLogger(__name__)


class SMSOTPService:
    """Professional SMS OTP service with AVRSMS integration"""
    
    def __init__(self):
        self.sms_service = AVRSMSService()
        self.settings = getattr(settings, 'SMS_OTP_SETTINGS', {})
        self.default_sender = getattr(settings, 'SMS_SENDER_ID', 'AgriConnect')
        
    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number to international format"""
        # Remove all non-digits
        digits = phone_number.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # Handle Ghana local format (starts with 0)
        if digits.startswith('0') and len(digits) == 10:
            return '+233' + digits[1:]
        
        # Add + if missing
        if not phone_number.startswith('+'):
            return '+' + digits
        
        return phone_number

    def generate_and_send_otp(self,
                             phone_number: str,
                             purpose: str = 'registration',
                             user: Optional['AbstractUser'] = None,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None,
                             brand: str = "AgriConnect") -> Tuple[bool, str, Optional['OTPCode']]:
        """
        Generate and send SMS OTP
        Returns:
            Tuple[bool, str, Optional[OTPCode]]: (success, message, otp_instance)
        """
        try:
            # Format phone number
            phone_number = self._format_phone_number(phone_number)
            
            # Rate limiting check
            if not self._check_rate_limits(phone_number, purpose, ip_address):
                return False, "Rate limit exceeded. Please wait before requesting another SMS OTP", None
            
            # Generate OTP code
            otp_code = self._generate_otp()
            expires_at = timezone.now() + timedelta(minutes=self.settings.get('OTP_EXPIRY_MINUTES', 10))
            
            # Create OTP record
            with transaction.atomic():
                otp = OTPCode.objects.create(
                    user=user,
                    phone_number=phone_number,
                    code=otp_code,
                    purpose=purpose,
                    expires_at=expires_at
                )
                
                # Send SMS
                sms_success = self._send_otp_sms(phone_number, otp_code, purpose, brand)
                
                if sms_success:
                    # Update rate limits
                    self._update_rate_limits(phone_number, purpose, ip_address)
                    logger.info(f"SMS OTP sent successfully to {phone_number} for {purpose}")
                    return True, "SMS OTP sent successfully", otp
                else:
                    # Mark OTP as failed if SMS sending failed
                    otp.delete()  # Remove failed OTP record
                    logger.error(f"Failed to send SMS OTP to {phone_number}")
                    return False, "Failed to send SMS OTP", None
                    
        except Exception as e:
            logger.error(f"Error generating SMS OTP for {phone_number}: {str(e)}")
            return False, f"Internal error: {str(e)}", None

    def verify_otp(self,
                   phone_number: str,
                   otp_code: str,
                   purpose: str = 'registration',
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> Tuple[bool, str, Optional['OTPCode']]:
        """
        Verify SMS OTP code
        Returns:
            Tuple[bool, str, Optional[OTPCode]]: (success, message, otp_instance)
        """
        try:
            # Format phone number
            phone_number = self._format_phone_number(phone_number)
            
            # Find the most recent valid OTP
            otp = OTPCode.objects.filter(
                phone_number=phone_number,
                purpose=purpose,
                is_used=False,
                expires_at__gt=timezone.now()
            ).order_by('-created_at').first()
            
            if not otp:
                logger.warning(f"No valid SMS OTP found for {phone_number} ({purpose})")
                return False, "Invalid or expired OTP code", None
            
            # Check if OTP code matches
            if otp.code == otp_code:
                # Success - mark as used
                otp.is_used = True
                otp.used_at = timezone.now()
                otp.save()
                
                logger.info(f"SMS OTP verified successfully for {phone_number} ({purpose})")
                return True, "SMS OTP verified successfully", otp
            else:
                # Incorrect code - increment attempts
                attempts = getattr(otp, 'attempts', 0) + 1
                max_attempts = self.settings.get('MAX_ATTEMPTS', 3)
                
                if attempts >= max_attempts:
                    # Max attempts reached - mark as expired
                    otp.is_used = True
                    otp.save()
                    message = "Maximum attempts exceeded. Please request a new OTP"
                else:
                    # Update attempts count
                    otp.attempts = attempts
                    otp.save()
                    remaining = max_attempts - attempts
                    message = f"Incorrect OTP. {remaining} attempts remaining"
                
                logger.warning(f"Incorrect SMS OTP for {phone_number}: {remaining if attempts < max_attempts else 0} attempts remaining")
                return False, message, otp
                
        except Exception as e:
            logger.error(f"Error verifying SMS OTP for {phone_number}: {str(e)}")
            return False, f"Internal error: {str(e)}", None

    def resend_otp(self,
                   phone_number: str,
                   purpose: str = 'registration',
                   ip_address: Optional[str] = None,
                   brand: str = "AgriConnect") -> Tuple[bool, str, Optional['OTPCode']]:
        """
        Resend SMS OTP (invalidates previous OTP)
        """
        try:
            # Format phone number
            phone_number = self._format_phone_number(phone_number)
            
            # Invalidate existing OTPs for this phone/purpose
            OTPCode.objects.filter(
                phone_number=phone_number,
                purpose=purpose,
                is_used=False
            ).update(is_used=True)
            
            # Generate and send new OTP
            return self.generate_and_send_otp(
                phone_number=phone_number,
                purpose=purpose,
                ip_address=ip_address,
                brand=brand
            )
            
        except Exception as e:
            logger.error(f"Error resending SMS OTP for {phone_number}: {str(e)}")
            return False, f"Internal error: {str(e)}", None
    
    def _generate_otp(self, length: int = 6) -> str:
        """Generate secure numeric OTP code"""
        length = self.settings.get('OTP_LENGTH', length)
        # Ensure first digit is not 0 for better UX
        first_digit = secrets.choice('123456789')
        remaining = ''.join(secrets.choice('0123456789') for _ in range(length - 1))
        return first_digit + remaining
    
    def _send_otp_sms(self, phone_number: str, otp_code: str, purpose: str, brand: str) -> bool:
        """Send OTP SMS using AVRSMS service"""
        try:
            # Prepare message based on purpose
            message_templates = {
                'registration': f"Your {brand} verification code is {otp_code}. Valid for 10 minutes. Do not share this code.",
                'login': f"Your {brand} login code is {otp_code}. Valid for 10 minutes.",
                'password_reset': f"Your {brand} password reset code is {otp_code}. Valid for 10 minutes.",
                'phone_verification': f"Your {brand} phone verification code is {otp_code}. Valid for 10 minutes.",
                'account_security': f"Your {brand} security code is {otp_code}. Valid for 10 minutes."
            }
            
            message = message_templates.get(purpose, f"Your {brand} OTP is: {otp_code}. Valid for 10 minutes.")
              # Send SMS via AVRSMS
            result = self.sms_service.send_sms(
                phone_number=phone_number,
                message=message
            )
            
            if result.get('success', False):
                logger.info(f"SMS OTP sent successfully via AVRSMS: {phone_number}")
                return True
            else:
                logger.error(f"AVRSMS SMS sending failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending SMS OTP via AVRSMS: {str(e)}")
            return False
    
    def _check_rate_limits(self, phone_number: str, purpose: str, ip_address: Optional[str]) -> bool:
        """Check rate limiting for SMS OTP requests"""
        try:
            # Phone number rate limit (5 per hour)
            phone_key = f"sms_otp_rate_{phone_number}"
            phone_requests = cache.get(phone_key, 0)
            phone_limit = self.settings.get('RATE_LIMIT_PHONE_PER_HOUR', 5)
            if phone_requests >= phone_limit:
                return False
            
            # IP address rate limit (10 per hour) if provided
            if ip_address:
                ip_key = f"sms_otp_rate_ip_{ip_address}"
                ip_requests = cache.get(ip_key, 0)
                ip_limit = self.settings.get('RATE_LIMIT_IP_PER_HOUR', 10)
                if ip_requests >= ip_limit:
                    return False
            
            # Global rate limit (20 per minute)
            global_key = "sms_otp_rate_global"
            global_requests = cache.get(global_key, 0)
            global_limit = self.settings.get('RATE_LIMIT_GLOBAL_PER_MINUTE', 20)
            if global_requests >= global_limit:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {str(e)}")
            return True  # Allow if rate limit check fails
    
    def _update_rate_limits(self, phone_number: str, purpose: str, ip_address: Optional[str]):
        """Update rate limiting counters"""
        try:
            # Update phone number counter (1 hour)
            phone_key = f"sms_otp_rate_{phone_number}"
            cache.set(phone_key, cache.get(phone_key, 0) + 1, 3600)
            
            # Update IP address counter if provided (1 hour)
            if ip_address:
                ip_key = f"sms_otp_rate_ip_{ip_address}"
                cache.set(ip_key, cache.get(ip_key, 0) + 1, 3600)
            
            # Update global counter (1 minute for burst protection)
            global_key = "sms_otp_rate_global"
            cache.set(global_key, cache.get(global_key, 0) + 1, 60)
            
        except Exception as e:
            logger.error(f"Error updating rate limits: {str(e)}")
    
    def get_otp_status(self, phone_number: str, purpose: str = 'registration') -> Dict:
        """Get OTP status for a phone number"""
        try:
            phone_number = self._format_phone_number(phone_number)
            
            otp = OTPCode.objects.filter(
                phone_number=phone_number,
                purpose=purpose
            ).order_by('-created_at').first()
            
            if not otp:
                return {
                    'status': 'not_found',
                    'phone_number': phone_number,
                    'purpose': purpose,
                    'message': 'No OTP found for this phone number'
                }
            
            if otp.is_used and otp.used_at:
                return {
                    'status': 'verified',
                    'phone_number': phone_number,
                    'purpose': purpose,
                    'verified_at': otp.used_at.isoformat(),
                    'message': 'OTP has been verified'
                }
            
            if otp.expires_at <= timezone.now():
                return {
                    'status': 'expired',
                    'phone_number': phone_number,
                    'purpose': purpose,
                    'expires_at': otp.expires_at.isoformat(),
                    'message': 'OTP has expired'
                }
            
            return {
                'status': 'pending',
                'phone_number': phone_number,
                'purpose': purpose,
                'expires_at': otp.expires_at.isoformat(),
                'attempts': getattr(otp, 'attempts', 0),
                'max_attempts': self.settings.get('MAX_ATTEMPTS', 3),
                'message': 'OTP is pending verification'
            }
            
        except Exception as e:
            logger.error(f"Error getting OTP status: {str(e)}")
            return {
                'status': 'error',
                'message': 'Error checking OTP status'
            }
    
    def cleanup_expired_otps(self):
        """Clean up expired OTP records"""
        try:
            # Mark expired OTPs as used
            expired_count = OTPCode.objects.filter(
                expires_at__lt=timezone.now(),
                is_used=False
            ).update(is_used=True)
            
            # Delete very old OTP records (older than 7 days)
            cleanup_days = self.settings.get('CLEANUP_AFTER_DAYS', 7)
            old_date = timezone.now() - timedelta(days=cleanup_days)
            deleted_count = OTPCode.objects.filter(
                created_at__lt=old_date
            ).delete()[0]
            
            logger.info(f"SMS OTP cleanup: {expired_count} expired, {deleted_count} old records removed")
            return {
                'expired_marked': expired_count,
                'old_deleted': deleted_count,
                'total_processed': expired_count + deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired OTPs: {str(e)}")
            return {'error': str(e)}
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Get SMS OTP usage statistics"""
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Total SMS OTPs sent (filter by phone_number not null)
            total_sent = OTPCode.objects.filter(
                phone_number__isnull=False,
                created_at__gte=start_date
            ).count()
            
            # Verified SMS OTPs
            verified = OTPCode.objects.filter(
                phone_number__isnull=False,
                created_at__gte=start_date,
                is_used=True,
                used_at__isnull=False
            ).count()
            
            # Expired SMS OTPs
            expired = OTPCode.objects.filter(
                phone_number__isnull=False,
                created_at__gte=start_date,
                expires_at__lt=timezone.now(),
                is_used=False
            ).count()
            
            # Failed SMS OTPs (expired without being used)
            failed = OTPCode.objects.filter(
                phone_number__isnull=False,
                created_at__gte=start_date,
                is_used=True,
                used_at__isnull=True  # Marked used but no verification time = failed
            ).count()
            
            # Success rate
            success_rate = (verified / total_sent * 100) if total_sent > 0 else 0
            
            # Purpose breakdown
            purpose_stats = {}
            purposes = OTPCode.objects.filter(
                phone_number__isnull=False,
                created_at__gte=start_date
            ).values_list('purpose', flat=True).distinct()
            
            for purpose in purposes:
                purpose_count = OTPCode.objects.filter(
                    phone_number__isnull=False,
                    created_at__gte=start_date,
                    purpose=purpose
                ).count()
                purpose_stats[purpose] = purpose_count
            
            # Country breakdown (by phone prefix)
            country_stats = {}
            country_codes = {
                '+233': 'Ghana',
                '+234': 'Nigeria',
                '+254': 'Kenya',
                '+27': 'South Africa',
                '+221': 'Senegal',
                '+255': 'Tanzania',
                '+256': 'Uganda',
                '+260': 'Zambia',
                '+225': 'Ivory Coast',
                '+223': 'Mali'
            }
            
            for code, country in country_codes.items():
                count = OTPCode.objects.filter(
                    phone_number__isnull=False,
                    phone_number__startswith=code,
                    created_at__gte=start_date
                ).count()
                if count > 0:
                    country_stats[code] = count
            
            return {
                'period_days': days,
                'total_sent': total_sent,
                'total_verified': verified,
                'total_expired': expired,
                'total_failed': failed,
                'success_rate': round(success_rate, 1),
                'by_purpose': purpose_stats,
                'by_country': country_stats,
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting SMS OTP statistics: {str(e)}")
            return {
                'error': str(e),
                'generated_at': timezone.now().isoformat()
            }
