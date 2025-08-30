"""
AgriConnect Email OTP Services
Professional email OTP implementation with Mailtrap integration
"""

import logging
import time
from typing import Dict, Optional, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from .models_otp import EmailOTP
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.db import transaction

from .models_otp import EmailOTP, EmailOTPAttempt, EmailOTPRateLimit

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailOTPService:
    """Professional email OTP service with comprehensive features"""
    
    def __init__(self):
        self.settings = getattr(settings, 'EMAIL_OTP_SETTINGS', {})
        self.default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@agriconnect.com')    
    def generate_and_send_otp(self, 
                             email: str, 
                             purpose: str = 'registration',
                             user: Optional['AbstractUser'] = None,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None,
                             extra_context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional['EmailOTP']]:
        """
        Generate and send OTP to email address
        
        Returns:
            Tuple[bool, str, Optional[EmailOTP]]: (success, message, otp_instance)
        """
        
        try:
            with transaction.atomic():
                # Check rate limiting
                is_limited, limit_message = self._check_rate_limits(email, purpose, ip_address)
                if is_limited:
                    logger.warning(f"Rate limit exceeded for {email}: {limit_message}")
                    return False, f"Rate limit exceeded: {limit_message}", None
                
                # Invalidate any existing pending OTPs for same email/purpose
                self._invalidate_existing_otps(email, purpose)
                
                # Create new OTP
                otp = EmailOTP.objects.create(
                    email=email,
                    user=user,
                    purpose=purpose,
                    ip_address=ip_address,
                    user_agent=user_agent or '',
                    metadata=extra_context or {}
                )
                
                # Send email
                email_sent = self._send_otp_email(otp, extra_context or {})
                
                if email_sent:
                    # Update rate limiting
                    self._update_rate_limits(email, purpose, ip_address)
                    
                    logger.info(f"OTP sent successfully to {email} for {purpose}")
                    return True, "OTP sent successfully", otp
                else:
                    # Mark OTP as failed if email sending failed
                    otp.status = 'failed'
                    otp.save()
                    
                    logger.error(f"Failed to send OTP email to {email}")
                    return False, "Failed to send OTP email", None
        
        except Exception as e:
            logger.error(f"Error generating OTP for {email}: {str(e)}")
            return False, f"Internal error: {str(e)}", None
    
    def verify_otp(self, 
                   email: str, 
                   otp_code: str,
                   purpose: str = 'registration',
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> Tuple[bool, str, Optional[EmailOTP]]:
        """
        Verify OTP code
        
        Returns:
            Tuple[bool, str, Optional[EmailOTP]]: (success, message, otp_instance)
        """
        
        start_time = time.time()
        
        try:
            # Find the most recent valid OTP
            otp = EmailOTP.objects.filter(
                email=email,
                purpose=purpose,
                status='pending'
            ).order_by('-created_at').first()
            
            # Record attempt
            attempt = EmailOTPAttempt.objects.create(
                email_otp=otp if otp else None,
                attempted_code=otp_code,
                ip_address=ip_address,
                user_agent=user_agent or '',
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            
            if not otp:
                attempt.failure_reason = "No pending OTP found"
                attempt.save()
                logger.warning(f"No pending OTP found for {email} ({purpose})")
                return False, "No pending OTP found", None
            
            # Check if OTP is still valid
            if not otp.is_valid():
                failure_reason = "OTP expired" if otp.is_expired() else "Maximum attempts exceeded"
                attempt.failure_reason = failure_reason
                attempt.save()
                
                if otp.is_expired():
                    otp.status = 'expired'
                    otp.save()
                
                logger.warning(f"Invalid OTP attempt for {email}: {failure_reason}")
                return False, failure_reason, otp
            
            # Verify the code
            if otp.otp_code == otp_code:
                # Success!
                otp.mark_as_verified()
                attempt.is_successful = True
                attempt.response_time_ms = int((time.time() - start_time) * 1000)
                attempt.save()
                
                logger.info(f"OTP verified successfully for {email} ({purpose})")
                return True, "OTP verified successfully", otp
            else:
                # Incorrect code
                otp.increment_attempts()
                attempt.failure_reason = "Incorrect OTP code"
                attempt.response_time_ms = int((time.time() - start_time) * 1000)
                attempt.save()
                
                remaining_attempts = otp.max_attempts - otp.attempts_count
                if remaining_attempts > 0:
                    message = f"Incorrect OTP. {remaining_attempts} attempts remaining"
                else:
                    message = "Maximum attempts exceeded. Please request a new OTP"
                
                logger.warning(f"Incorrect OTP for {email}: {remaining_attempts} attempts remaining")
                return False, message, otp
        
        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {str(e)}")
            return False, f"Internal error: {str(e)}", None
    
    def resend_otp(self, 
                   email: str, 
                   purpose: str = 'registration',
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> Tuple[bool, str, Optional[EmailOTP]]:
        """
        Resend OTP (with cooldown check)
        
        Returns:
            Tuple[bool, str, Optional[EmailOTP]]: (success, message, otp_instance)
        """
        
        # Check if there's a recent OTP that's still in cooldown
        cooldown_seconds = self.settings.get('RESEND_COOLDOWN_SECONDS', 60)
        recent_cutoff = timezone.now() - timedelta(seconds=cooldown_seconds)
        
        recent_otp = EmailOTP.objects.filter(
            email=email,
            purpose=purpose,
            created_at__gt=recent_cutoff
        ).first()
        
        if recent_otp:
            remaining_seconds = int((recent_otp.created_at + timedelta(seconds=cooldown_seconds) - timezone.now()).total_seconds())
            if remaining_seconds > 0:
                return False, f"Please wait {remaining_seconds} seconds before requesting a new OTP", None
        
        # Generate new OTP
        return self.generate_and_send_otp(
            email=email,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def _check_rate_limits(self, email: str, purpose: str, ip_address: Optional[str]) -> Tuple[bool, str]:
        """Check if email/IP is rate limited"""
        
        rate_limit, created = EmailOTPRateLimit.objects.get_or_create(
            email=email,
            purpose=purpose,
            defaults={'ip_address': ip_address}
        )
        
        return rate_limit.is_rate_limited()
    
    def _update_rate_limits(self, email: str, purpose: str, ip_address: Optional[str]):
        """Update rate limiting counters"""
        
        rate_limit, created = EmailOTPRateLimit.objects.get_or_create(
            email=email,
            purpose=purpose,
            defaults={'ip_address': ip_address}
        )
        
        rate_limit.increment_counters()
    
    def _invalidate_existing_otps(self, email: str, purpose: str):
        """Invalidate any existing pending OTPs"""
        
        EmailOTP.objects.filter(
            email=email,
            purpose=purpose,
            status='pending'
        ).update(status='expired')
    
    def _send_otp_email(self, otp: EmailOTP, extra_context: Dict) -> bool:
        """Send OTP email using Django's email backend"""
        
        try:
            # Prepare context for email template
            context = {
                'otp_code': otp.otp_code,
                'email': otp.email,
                'purpose': otp.get_purpose_display(),
                'purpose_code': otp.purpose,
                'expires_at': otp.expires_at,
                'expiry_minutes': self.settings.get('OTP_EXPIRY_MINUTES', 10),
                'user': otp.user,
                **self.settings.get('TEMPLATE_CONTEXT', {}),
                **extra_context
            }
            
            # Subject line based on purpose
            subject_map = {
                'registration': f"Welcome to {context.get('company_name', 'AgriConnect')} - Verify Your Email",
                'login': f"Login Verification Code - {context.get('company_name', 'AgriConnect')}",
                'password_reset': f"Password Reset Code - {context.get('company_name', 'AgriConnect')}",
                'email_verification': f"Email Verification Code - {context.get('company_name', 'AgriConnect')}",
                'account_security': f"Security Verification Code - {context.get('company_name', 'AgriConnect')}",
                'profile_update': f"Profile Update Verification - {context.get('company_name', 'AgriConnect')}",
                'sensitive_action': f"Action Verification Code - {context.get('company_name', 'AgriConnect')}"
            }
            
            subject = subject_map.get(otp.purpose, f"Verification Code - {context.get('company_name', 'AgriConnect')}")
            
            # Prepare email content
            if self.settings.get('SEND_HTML', True):
                # HTML email
                html_message = render_to_string('emails/otp_email.html', context)
                text_message = render_to_string('emails/otp_email.txt', context)
                
                # Send email with both HTML and text
                sent = send_mail(
                    subject=subject,
                    message=text_message,
                    from_email=self.default_from_email,
                    recipient_list=[otp.email],
                    html_message=html_message,
                    fail_silently=False
                )
            else:
                # Text-only email
                text_message = render_to_string('emails/otp_email.txt', context)
                
                sent = send_mail(
                    subject=subject,
                    message=text_message,
                    from_email=self.default_from_email,
                    recipient_list=[otp.email],
                    fail_silently=False
                )
            
            return sent == 1  # send_mail returns number of emails sent
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {otp.email}: {str(e)}")
            return False
    
    def cleanup_expired_otps(self):
        """Clean up expired OTPs (can be called by a periodic task)"""
        
        try:
            # Mark expired OTPs
            expired_count = EmailOTP.objects.filter(
                status='pending',
                expires_at__lt=timezone.now()
            ).update(status='expired')
            
            # Optionally delete very old OTPs (older than 30 days)
            cutoff_date = timezone.now() - timedelta(days=30)
            deleted_count = EmailOTP.objects.filter(
                created_at__lt=cutoff_date
            ).delete()[0]
            
            logger.info(f"Cleanup: Marked {expired_count} OTPs as expired, deleted {deleted_count} old OTPs")
            
        except Exception as e:
            logger.error(f"Error during OTP cleanup: {str(e)}")
    
    def get_otp_statistics(self, email: Optional[str] = None, days: int = 7) -> Dict:
        """Get OTP usage statistics"""
        
        start_date = timezone.now() - timedelta(days=days)
        
        base_query = EmailOTP.objects.filter(created_at__gte=start_date)
        if email:
            base_query = base_query.filter(email=email)
        
        stats = {
            'total_sent': base_query.count(),
            'verified': base_query.filter(status='verified').count(),
            'expired': base_query.filter(status='expired').count(),
            'failed': base_query.filter(status='failed').count(),
            'pending': base_query.filter(status='pending').count(),
        }
        
        # Calculate success rate
        if stats['total_sent'] > 0:
            stats['success_rate'] = round((stats['verified'] / stats['total_sent']) * 100, 2)
        else:
            stats['success_rate'] = 0.0
        
        # Purpose breakdown
        stats['by_purpose'] = {}
        for purpose, _ in EmailOTP.PURPOSE_CHOICES:
            count = base_query.filter(purpose=purpose).count()
            if count > 0:
                stats['by_purpose'][purpose] = count
        
        return stats