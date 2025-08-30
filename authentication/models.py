"""
AgriConnect Authentication Models
Dual Authentication System: Phone OR Email + OTP

Based on comprehensive PRD Section 6: Dual Authentication System & SMS/OTP Integration
Supports farmers, processors, consumers, and institutions across Africa
"""

import uuid
import re
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserRole(models.Model):
    """User roles for the agricultural platform"""
    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('PROCESSOR', 'Processor'),
        ('CONSUMER', 'Consumer'),
        ('INSTITUTION', 'Institution'),
        ('WAREHOUSE_MANAGER', 'Warehouse Manager'),
        ('QUALITY_INSPECTOR', 'Quality Inspector'),
        ('LOGISTICS_PARTNER', 'Logistics Partner'),
        ('AGENT', 'Sales Agent/Field Officer'),
        ('FINANCIAL_PARTNER', 'Financial Partner'),
        ('GOVERNMENT_OFFICIAL', 'Government Official'),
        ('ADMIN', 'Administrator'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()


def validate_international_phone(value):
    """Validate international phone number format"""
    phone_pattern = re.compile(r'^\+[1-9]\d{1,14}$')
    if not phone_pattern.match(value):
        raise ValidationError(
            _('Phone number must be in international format (+1234567890)')
        )


class UserManager(BaseUserManager):
    """Enhanced user manager with dual authentication support"""
    
    def _normalize_identifier(self, identifier):
        """Normalize email or phone number identifier"""
        if not identifier:
            return identifier
        
        identifier = identifier.strip()
        
        # If it's an email, normalize it
        if '@' in identifier:
            return self.normalize_email(identifier)
        
        # If it's a phone number, normalize it
        clean_phone = re.sub(r'[\s\-()]', '', identifier)
          # Convert Ghana local format to international
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
            
        return clean_phone
    
    def create_user(self, identifier=None, password=None, roles=None, **extra_fields):
        """Create user with email or phone number"""
        if not identifier:
            raise ValueError("Email or phone number is required")
        if not password:
            raise ValueError("Password is required")
        if not roles:
            roles = ['CONSUMER']  # Default role

        # Normalize and validate the identifier
        normalized_identifier = self._normalize_identifier(identifier)
        
        # Check for existing user to prevent duplicates
        existing_user = None
        if '@' in normalized_identifier:
            existing_user = self.filter(email=normalized_identifier).first()
        else:
            existing_user = self.filter(phone_number=normalized_identifier).first()
            
        if existing_user:
            raise ValueError(f"User with this {'email' if '@' in normalized_identifier else 'phone number'} already exists")
          # Determine if identifier is email or phone
        if '@' in normalized_identifier:
            # Email registration - use email as username
            extra_fields['email'] = normalized_identifier
            extra_fields['phone_number'] = None
            username = normalized_identifier  # Use email directly as username
        else:
            # Phone registration - use phone as username
            extra_fields['phone_number'] = normalized_identifier
            extra_fields['email'] = None
            username = normalized_identifier  # Use phone directly as username
        
        # Check if username already exists (should not happen due to unique constraints on email/phone)
        if self.filter(username=username).exists():
            raise ValueError(f"Username {username} already exists")

        extra_fields.setdefault('username', username)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
          # Assign roles
        for role_name in roles:
            role, _ = UserRole.objects.get_or_create(name=role_name)
            user.roles.add(role)

        return user

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        """Create superuser - compatible with Django's createsuperuser command"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        # Determine identifier from username or email
        # Django management command passes username, but we need email or phone
        identifier = None
        if username:
            if '@' in username:
                # Username is actually an email
                identifier = username
                extra_fields['email'] = username
                # Set username to be same as email for consistency
                extra_fields['username'] = username
                
                # Check for existing user with this email
                existing_user = self.filter(email=identifier).first()
                if existing_user:
                    if existing_user.is_superuser:
                        raise ValueError(f"Superuser with email {identifier} already exists")
                    else:
                        # Upgrade existing user to superuser
                        existing_user.is_staff = True
                        existing_user.is_superuser = True
                        existing_user.is_verified = True
                        # Update username to match email/phone if it doesn't already
                        existing_user.username = identifier
                        existing_user.save()
                        return existing_user
                        
            elif username.startswith('+') or username.startswith('0') or username.replace('+', '').isdigit():
                # Username is a phone number
                identifier = self._normalize_identifier(username)
                extra_fields['phone_number'] = identifier
                # Set username to be same as normalized phone for consistency
                extra_fields['username'] = identifier
                
                # Check for existing user with this phone number
                existing_user = self.filter(phone_number=identifier).first()
                if existing_user:
                    if existing_user.is_superuser:
                        raise ValueError(f"Superuser with phone number {identifier} already exists")
                    else:
                        # Upgrade existing user to superuser
                        existing_user.is_staff = True
                        existing_user.is_superuser = True
                        existing_user.is_verified = True
                        existing_user.phone_verified = True
                        # Update username to match email/phone if it doesn't already
                        existing_user.username = identifier
                        existing_user.save()
                        return existing_user
                        
            else:
                # Username is a regular username, require email input
                if not email:
                    raise ValueError("For regular usernames, email must be provided")
                identifier = email
                extra_fields['email'] = email
                # Use email as username instead of the provided username for consistency
                extra_fields['username'] = email
                
                # Check for existing user with this email
                existing_user = self.filter(email=identifier).first()
                if existing_user:
                    if existing_user.is_superuser:
                        raise ValueError(f"Superuser with email {identifier} already exists")
                    else:
                        # Upgrade existing user to superuser
                        existing_user.is_staff = True
                        existing_user.is_superuser = True
                        existing_user.is_verified = True
                        # Update username to match email for consistency
                        existing_user.username = identifier
                        existing_user.save()
                        return existing_user
                        
        elif email:
            identifier = email
            extra_fields['email'] = email
            # Set username to be same as email for consistency
            extra_fields['username'] = email
            
            # Check for existing user with this email
            existing_user = self.filter(email=identifier).first()
            if existing_user:
                if existing_user.is_superuser:
                    raise ValueError(f"Superuser with email {identifier} already exists")
                else:
                    # Upgrade existing user to superuser
                    existing_user.is_staff = True
                    existing_user.is_superuser = True
                    existing_user.is_verified = True
                    # Update username to match email for consistency
                    existing_user.username = identifier
                    existing_user.save()
                    return existing_user
        else:
            raise ValueError("Username (email/phone) or email is required for superuser")

        return self.create_user(identifier=identifier, password=password, roles=['ADMIN'], **extra_fields)


class User(AbstractUser):
    """Enhanced user model with dual authentication support"""
    
    # Remove default username requirement for flexibility
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_('Auto-generated unique identifier'),
    )
    
    # Enhanced email field for international users
    email = models.EmailField(
        _('email address'),
        unique=True,
        null=True,
        blank=True,
        help_text=_('Email address for international users and processors')
    )
    
    # Enhanced phone number field for local users
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_international_phone],
        help_text=_('Phone number in international format (+233xxxxxxxxx)')
    )
    
    # User verification and preferences
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Contact preferences
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
        ],
        default='sms'
    )
    
    # Profile information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Location information
    country = models.CharField(max_length=100, default='Ghana')
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    # Language and localization
    language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('fr', 'French'),
            ('tw', 'Twi'),
            ('ee', 'Ewe'),
            ('ha', 'Hausa'),
            ('yo', 'Yoruba'),
            ('sw', 'Swahili'),
        ],
        default='en'
    )
    
    # Business information
    business_name = models.CharField(max_length=200, blank=True)
    business_registration_number = models.CharField(max_length=100, blank=True)
    tax_identification_number = models.CharField(max_length=100, blank=True)
    
    # User roles (many-to-many for flexibility)
    roles = models.ManyToManyField(UserRole, related_name='users')
    
    # Security and tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    # Update USERNAME_FIELD to support dual authentication
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__isnull=False) | models.Q(phone_number__isnull=False),
                name='user_must_have_email_or_phone'
            )
        ]
    
    def __str__(self):
        if self.email:
            return f"{self.get_full_name()} ({self.email})"
        elif self.phone_number:
            return f"{self.get_full_name()} ({self.phone_number})"
        return self.username
    
    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_primary_contact(self):
        """Get primary contact method (email or phone)"""
        return self.email or self.phone_number
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.roles.filter(name=role_name).exists()
    
    def get_roles_list(self):
        """Get list of user role names"""
        return list(self.roles.values_list('name', flat=True))
    
    def is_account_locked(self):
        """Check if account is temporarily locked"""
        return (
            self.account_locked_until and 
            self.account_locked_until > timezone.now()
        )
    
    def can_receive_sms(self):
        """Check if user can receive SMS"""
        return bool(self.phone_number and self.phone_verified)
    
    def can_receive_email(self):
        """Check if user can receive email"""
        return bool(self.email and self.email_verified)


class OTPCode(models.Model):
    """OTP management for verification and authentication"""
    PURPOSE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
        ('phone_verification', 'Phone Verification'),
        ('email_verification', 'Email Verification'),
        ('transaction', 'Transaction'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    
    # Expiry and limits
    expires_at = models.DateTimeField()
    attempts_count = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    # Status
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'otp_codes'
        indexes = [
            models.Index(fields=['phone_number', 'purpose', 'expires_at']),
            models.Index(fields=['email', 'purpose', 'expires_at']),
        ]
    
    def __str__(self):
        contact = self.phone_number or self.email
        return f"OTP {self.code} for {contact} ({self.purpose})"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return (
            not self.is_used and 
            self.expires_at > timezone.now() and
            self.attempts_count < self.max_attempts
        )


class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Agricultural information
    farming_experience_years = models.PositiveIntegerField(null=True, blank=True)
    farm_size_hectares = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    primary_crops = models.JSONField(default=list, blank=True)
    processing_capabilities = models.JSONField(default=list, blank=True)
    
    # Verification status
    id_document_verified = models.BooleanField(default=False)
    business_license_verified = models.BooleanField(default=False)
    farm_verified = models.BooleanField(default=False)
    
    # Subscription and preferences
    subscription_plan = models.CharField(max_length=50, default='free')
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # Statistics
    total_transactions = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"
