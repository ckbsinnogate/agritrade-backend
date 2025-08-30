"""
Enhanced Email OTP Models for AgriConnect
Professional email OTP implementation with comprehensive features
"""

import uuid
import secrets
import string
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOTP(models.Model):
    """Enhanced Email OTP model with professional features"""
    
    PURPOSE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login Verification'),
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
        ('account_security', 'Account Security'),
        ('profile_update', 'Profile Update'),
        ('sensitive_action', 'Sensitive Action'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='email_otps')
    
    # OTP details
    otp_code = models.CharField(max_length=10, db_index=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='registration')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Security and tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    
    # Timing and attempts
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    attempts_count = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'email_otps'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'purpose', 'status']),
            models.Index(fields=['otp_code', 'status']),
            models.Index(fields=['expires_at', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Email OTP {self.otp_code} for {self.email} ({self.purpose})"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            from django.conf import settings
            expiry_minutes = getattr(settings, 'EMAIL_OTP_SETTINGS', {}).get('OTP_EXPIRY_MINUTES', 10)
            self.expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_otp(cls, length=6):
        """Generate secure OTP code"""
        from django.conf import settings
        otp_settings = getattr(settings, 'EMAIL_OTP_SETTINGS', {})
        
        length = otp_settings.get('OTP_LENGTH', length)
        charset = otp_settings.get('OTP_CHARSET', 'numeric')
        
        if charset == 'numeric':
            # Ensure first digit is not 0 for better UX
            first_digit = secrets.choice('123456789')
            remaining = ''.join(secrets.choice('0123456789') for _ in range(length - 1))
            return first_digit + remaining
        elif charset == 'alphanumeric':
            return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
        else:
            return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    def is_valid(self):
        """Check if OTP is valid for verification"""
        now = timezone.now()
        return (
            self.status == 'pending' and
            self.expires_at > now and
            self.attempts_count < self.max_attempts
        )
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def mark_as_verified(self):
        """Mark OTP as successfully verified"""
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.save(update_fields=['status', 'verified_at'])
    
    def mark_as_failed(self):
        """Mark OTP as failed after max attempts"""
        self.status = 'failed'
        self.save(update_fields=['status'])
    
    def increment_attempts(self):
        """Increment verification attempts"""
        self.attempts_count += 1
        if self.attempts_count >= self.max_attempts:
            self.mark_as_failed()
        else:
            self.save(update_fields=['attempts_count'])


class EmailOTPAttempt(models.Model):
    """Track individual OTP verification attempts"""
    
    email_otp = models.ForeignKey(EmailOTP, on_delete=models.CASCADE, related_name='attempts')
    attempted_code = models.CharField(max_length=10)
    is_successful = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    # Additional tracking
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'email_otp_attempts'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['email_otp', 'attempted_at']),
            models.Index(fields=['is_successful', 'attempted_at']),
        ]
    
    def __str__(self):
        status = "Success" if self.is_successful else "Failed"
        return f"{status} attempt for {self.email_otp.email} at {self.attempted_at}"


class EmailOTPRateLimit(models.Model):
    """Rate limiting for email OTP sends"""
    
    email = models.EmailField(db_index=True)
    purpose = models.CharField(max_length=20, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    
    # Counters
    daily_count = models.PositiveIntegerField(default=0)
    hourly_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    first_request_today = models.DateTimeField(auto_now_add=True)
    last_request_at = models.DateTimeField(auto_now=True)
    reset_date = models.DateField(auto_now_add=True)
    
    # Blocking
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    block_reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'email_otp_rate_limits'
        unique_together = [('email', 'purpose')]
        indexes = [
            models.Index(fields=['email', 'purpose']),
            models.Index(fields=['ip_address', 'last_request_at']),
            models.Index(fields=['is_blocked', 'blocked_until']),
        ]
    
    def __str__(self):
        return f"Rate limit for {self.email} ({self.purpose}): {self.daily_count}/day"
    
    def is_rate_limited(self):
        """Check if email/IP is rate limited"""
        from django.conf import settings
        otp_settings = getattr(settings, 'EMAIL_OTP_SETTINGS', {})
        
        max_daily = otp_settings.get('MAX_DAILY_SENDS', 10)
        max_hourly = otp_settings.get('MAX_HOURLY_SENDS', 5)
        
        # Check if blocked
        if self.is_blocked and self.blocked_until and timezone.now() < self.blocked_until:
            return True, f"Blocked until {self.blocked_until}"
        
        # Reset counters if new day
        today = timezone.now().date()
        if self.reset_date < today:
            self.daily_count = 0
            self.hourly_count = 0
            self.reset_date = today
            self.is_blocked = False
            self.blocked_until = None
            self.save()
        
        # Reset hourly counter
        if timezone.now() - self.last_request_at > timedelta(hours=1):
            self.hourly_count = 0
        
        # Check limits
        if self.daily_count >= max_daily:
            return True, f"Daily limit exceeded ({max_daily}/day)"
        
        if self.hourly_count >= max_hourly:
            return True, f"Hourly limit exceeded ({max_hourly}/hour)"
        
        return False, ""
    
    def increment_counters(self):
        """Increment send counters"""
        self.daily_count += 1
        self.hourly_count += 1
        self.save()
    
    def block_email(self, duration_hours=24, reason="Suspicious activity"):
        """Block email for specified duration"""
        self.is_blocked = True
        self.blocked_until = timezone.now() + timedelta(hours=duration_hours)
        self.block_reason = reason
        self.save()