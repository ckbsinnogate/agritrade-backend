"""
AgriConnect API - User Models

Core user management models including enhanced User model with international support,
role-based permissions, and profile management for the agricultural eCommerce platform.

Components:
- Permission and Role system
- Enhanced User model with email/phone authentication
- UserProfile, FarmerProfile, ConsumerProfile, InstitutionProfile
- International user support with multi-language and timezone capabilities

Author: GitHub Copilot
Created: July 1, 2025
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, EmailValidator, FileExtensionValidator
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
import uuid
import re
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from PIL import Image
import os


# Import User model from authentication app
User = get_user_model()


# ======================== VALIDATORS AND UTILITY FUNCTIONS ========================

# Enhanced phone validator for international numbers
phone_validator = RegexValidator(
    regex=r"^\+?[1-9]\d{1,14}$",
    message=_("Phone number must be entered in international format: '+1234567890' (1-15 digits)")
)

# Ghana-specific phone validator for local users
ghana_phone_validator = RegexValidator(
    regex=r"^\+?233[0-9]{9}$|^0[0-9]{9}$",
    message=_("Ghana phone number must be in format: '+233549577086' or '0549577086'")
)

def validate_international_phone(value):
    """Validate international phone numbers with country-specific rules"""
    if not value:
        return
    
    # Remove spaces and dashes
    clean_number = re.sub(r'[\s\-()]', '', value)
    
    # Check if it starts with + and has valid length
    if clean_number.startswith('+'):
        if len(clean_number) < 8 or len(clean_number) > 16:
            raise ValidationError(_("International phone number must be between 8-16 digits including country code"))
    else:
        # Local number validation (Ghana format)
        if not (clean_number.startswith('0') and len(clean_number) == 10):
            raise ValidationError(_("Local phone number must be 10 digits starting with 0, or use international format with country code"))

def validate_email_or_phone(value):
    """Validate that the value is either a valid email or phone number"""
    if not value:
        raise ValidationError(_("Email or phone number is required"))
    
    # Check if it looks like an email
    if '@' in value:
        try:
            EmailValidator()(value)
            return 'email'
        except ValidationError:
            raise ValidationError(_("Invalid email format"))
    else:
        # Assume it's a phone number
        try:
            validate_international_phone(value)
            return 'phone'
        except ValidationError as e:
            raise ValidationError(f"Invalid phone number: {e.message}")

def validate_image_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError(_("Maximum allowed file size is 5MB."))

def validate_hex_color(value):
    if not value.startswith('#') or len(value) != 7:
        raise ValidationError(_("Color must be in hex format (#RRGGBB)"))


# ======================== ROLE AND PERMISSION SYSTEM ========================

class Permission(models.Model):
    """Custom permission model for fine-grained access control"""
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['codename']),
        ]


class Role(models.Model):
    """Role model for managing user permissions and access levels"""
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ======================== ENHANCED USER MANAGER ========================

class UserManager(BaseUserManager):
    """Enhanced user manager with international support and flexible authentication"""
    
    def _normalize_identifier(self, identifier):
        """Normalize email or phone number identifier"""
        if not identifier:
            return identifier
        
        identifier = identifier.strip()
        
        # If it's an email, normalize it
        if '@' in identifier:
            return self.normalize_email(identifier)
        
        # If it's a phone number, normalize it
        # Remove spaces, dashes, parentheses
        clean_phone = re.sub(r'[\s\-()]', '', identifier)
        
        # Convert Ghana local format to international
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        elif not clean_phone.startswith('+'):
            # Assume it needs a + prefix if it doesn't have one
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
        identifier_type = validate_email_or_phone(normalized_identifier)        # Set the appropriate field based on identifier type
        if identifier_type == 'email':
            extra_fields['email'] = normalized_identifier
            # Ensure phone_number is None for email users
            extra_fields['phone_number'] = None
            # Generate a unique username from email
            username = normalized_identifier.split('@')[0] + str(uuid.uuid4().hex[:6])
            extra_fields.setdefault('username', username)
        else:  # phone
            extra_fields['phone_number'] = normalized_identifier
            # Ensure email is None for phone users
            extra_fields['email'] = None
            # Generate a unique username from phone
            username = 'user_' + normalized_identifier.replace('+', '').replace('-', '')[-10:] + str(uuid.uuid4().hex[:4])
            extra_fields.setdefault('username', username)

        # Ensure username is unique
        original_username = extra_fields['username']
        counter = 1
        while User.objects.filter(username=extra_fields['username']).exists():
            extra_fields['username'] = f"{original_username}_{counter}"
            counter += 1

        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Assign roles
        for role_name in roles:
            role, _ = Role.objects.get_or_create(name=role_name)
            user.roles.add(role)        # Create user profile and role-specific profiles
        self._create_profiles(user)
        return user

    def create_user_with_email(self, email, password=None, roles=None, **extra_fields):
        """Create user specifically with email"""
        return self.create_user(identifier=email, password=password, roles=roles, **extra_fields)
    
    def create_user_with_phone(self, phone_number, password=None, roles=None, **extra_fields):
        """Create user specifically with phone number"""
        return self.create_user(identifier=phone_number, password=password, roles=roles, **extra_fields)
    
    def _create_profiles(self, user):
        """Create user profile and role-specific profiles"""
        # Import here to avoid circular imports
        UserProfile.objects.get_or_create(user=user)
        
        # Create role-specific profiles after saving
        if user.has_role('FARMER'):
            FarmerProfile.objects.get_or_create(
                user=user,
                defaults={'farm_size': 1.0, 'production_capacity': 100.0}
            )
        if user.has_role('CONSUMER'):
            ConsumerProfile.objects.get_or_create(user=user)
        if user.has_role('INSTITUTION'):
            InstitutionProfile.objects.get_or_create(user=user)
        if user.has_role('AGENT'):
            AgentProfile.objects.get_or_create(
                user=user,
                defaults={'agent_type': 'sales_representative', 'target_farmers': 100}
            )
        if user.has_role('FINANCIAL_PARTNER'):
            FinancialPartnerProfile.objects.get_or_create(
                user=user,
                defaults={'institution_name': f"{user.get_full_name()} Financial Services"}
            )
        if user.has_role('GOVERNMENT_OFFICIAL'):
            GovernmentOfficialProfile.objects.get_or_create(
                user=user,
                defaults={
                    'official_title': 'Agricultural Officer',
                    'department': 'Agricultural Development',
                    'ministry': 'Ministry of Food and Agriculture'
                }
            )

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        """Create superuser - compatible with Django's createsuperuser command"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        # Determine identifier from username parameter
        # Django's createsuperuser passes the input as 'username'
        identifier = username or email
        if not identifier:
            raise ValueError("Email or phone number is required for superuser")

        return self.create_user(identifier=identifier, password=password, roles=['SUPER_ADMIN'], **extra_fields)

    def get_by_natural_key(self, username):
        """Allow authentication with email, phone, or username"""
        # Try to find user by username first
        try:
            return self.get(username=username)
        except User.DoesNotExist:
            pass
        
        # Try email
        if '@' in username:
            try:
                return self.get(email=username)
            except User.DoesNotExist:
                pass
        
        # Try phone number
        normalized_phone = self._normalize_identifier(username)
        try:
            return self.get(phone_number=normalized_phone)
        except User.DoesNotExist:
            pass
            
        raise User.DoesNotExist(f"User with identifier '{username}' does not exist")


# ======================== ENHANCED USER MODEL ========================

class User(AbstractUser, PermissionsMixin):
    """Enhanced user model with international support and flexible authentication"""
    
    # Keep username for Django compatibility but make it auto-generated
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_('Auto-generated unique identifier'),
        validators=[],
    )
    
    # Enhanced email field for international users
    email = models.EmailField(
        _('email address'),
        unique=True,
        null=True,
        blank=True,
        help_text=_('Email address for international users')
    )
    
    # Enhanced phone number field
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_international_phone],
        help_text=_('Phone number in international format (+1234567890)')
    )
    
    # User verification and preferences
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('both', 'Both')
        ],
        default='email'
    )
    
    # Location and regional settings
    wallet_address = models.CharField(max_length=42, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Ghana')
    timezone = models.CharField(max_length=50, blank=True, default='Africa/Accra')
    language = models.CharField(max_length=10, blank=True, default='en')
    
    # User roles and permissions
    roles = models.ManyToManyField(Role, related_name="users", blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # Temporary: was PointField
    
    # Enhanced name fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Use username as the primary identifier for Django compatibility
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["wallet_address"]),
            models.Index(fields=["country", "region"]),
        ]
        ordering = ["-created_at"]
        constraints = [
            # Ensure at least one contact method is provided
            models.CheckConstraint(
                check=models.Q(email__isnull=False) | models.Q(phone_number__isnull=False),
                name='user_must_have_email_or_phone'
            ),
        ]

    def clean(self):
        """Validate user data"""
        super().clean()
        
        # Ensure at least one contact method is provided
        if not self.email and not self.phone_number:
            raise ValidationError(_("Either email or phone number must be provided"))
        
        # Validate email if provided
        if self.email:
            try:
                EmailValidator()(self.email)
            except ValidationError:
                raise ValidationError({'email': _("Invalid email format")})
          # Validate phone if provided
        if self.phone_number:
            try:
                validate_international_phone(self.phone_number)
            except ValidationError as e:
                raise ValidationError({'phone_number': e.message})
    
    def save(self, *args, **kwargs):
        # Normalize email and phone before saving
        if self.email:
            self.email = self.email.lower().strip()
            # If email becomes empty after stripping, set to None to avoid unique constraint issues
            if not self.email:
                self.email = None
        else:
            # Ensure empty string emails are set to None for unique constraint
            self.email = None
        
        if self.phone_number:
            self.phone_number = User.objects._normalize_identifier(self.phone_number)
            # If phone becomes empty after normalization, set to None
            if not self.phone_number:
                self.phone_number = None
        else:
            # Ensure empty string phones are set to None for unique constraint
            self.phone_number = None
        
        # Auto-generate username if not provided
        if not self.username:
            if self.email:
                base_username = self.email.split('@')[0]
            elif self.phone_number:
                base_username = 'user_' + self.phone_number.replace('+', '').replace('-', '')[-10:]
            else:
                base_username = 'user_' + str(uuid.uuid4().hex[:8])
            
            # Ensure uniqueness
            username = base_username + str(uuid.uuid4().hex[:6])
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            self.username = username
        
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self):
        """Get display name for the user"""
        if self.full_name.strip():
            return self.full_name
        elif self.email:
            return self.email.split('@')[0]
        elif self.phone_number:
            return self.phone_number
        return self.username

    @property
    def primary_contact(self):
        """Get primary contact method"""
        if self.preferred_contact_method == 'email' and self.email:
            return self.email
        elif self.preferred_contact_method == 'phone' and self.phone_number:
            return self.phone_number
        elif self.email:
            return self.email
        elif self.phone_number:
            return self.phone_number
        return self.username

    @property
    def is_international_user(self):
        """Check if user is international (not from Ghana)"""
        if self.country and self.country.lower() != 'ghana':
            return True
        if self.phone_number and not self.phone_number.startswith('+233'):
            return True
        return False

    @property
    def contact_methods(self):
        """Get available contact methods"""
        methods = []
        if self.email:
            methods.append('email')
        if self.phone_number:
            methods.append('phone')
        return methods

    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.roles.filter(name=role_name).exists()

    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission"""
        if self.is_superuser:
            return True
        return any(
            perm in [p.codename for p in role.permissions.all()]
            for role in self.roles.all()
        )

    def get_absolute_url(self):
        """Return the absolute URL for the user"""
        return f"/users/{self.username}/"

    def get_verification_status(self):
        """Get comprehensive verification status"""
        return {
            'email_verified': self.email_verified if self.email else None,
            'phone_verified': self.phone_verified if self.phone_number else None,
            'is_verified': self.is_verified,
            'verification_required': not self.is_verified,
        }

    def send_verification_code(self, method='auto'):
        """Send verification code via email or SMS"""
        # This would integrate with your notification system
        # Implementation depends on your SMS/Email service
        pass

    def verify_contact_method(self, method, code):
        """Verify email or phone with provided code"""
        # Implementation depends on your verification system
        pass


# ======================== PROFILE MODELS ========================

def user_directory_path(instance, filename):
    """Generate upload path for user files"""
    return f'user_{instance.user.id}/{filename}'


class UserProfile(models.Model):
    """Extended user profile with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to=user_directory_path,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image_size
        ],
        blank=True,
        null=True
    )
    
    # Additional profile fields for international users
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say')
        ],
        blank=True
    )
    
    # Address information
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.display_name} Profile"

    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state_province,
            self.postal_code,
            self.user.country
        ]
        return ', '.join([part for part in address_parts if part])


class FarmerProfile(models.Model):
    """Profile for farmers with agricultural information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_size = models.FloatField(
        validators=[MinValueValidator(Decimal('0.1'))],
        default=1.0,
        help_text="Farm size in hectares"
    )
    organic_certified = models.BooleanField(default=False)
    geo_location = models.CharField(max_length=255, blank=True, null=True)  # Temporary: was PointField
    certification_files = models.FileField(upload_to='certifications/', blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    production_capacity = models.FloatField(
        help_text="Annual production in kg",
        default=100.0
    )
    
    # Enhanced fields for international farmers
    farm_name = models.CharField(max_length=200, blank=True)
    farm_type = models.CharField(
        max_length=50,
        choices=[
            ('crop', 'Crop Farming'),
            ('livestock', 'Livestock'),
            ('mixed', 'Mixed Farming'),
            ('organic', 'Organic Farming'),
            ('hydroponic', 'Hydroponic'),
            ('greenhouse', 'Greenhouse'),
        ],
        blank=True
    )
    primary_crops = models.JSONField(default=list, blank=True)
    farming_methods = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user.has_role('FARMER'):
            raise ValueError("User must have the 'FARMER' role")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.display_name} - Farmer Profile"

    class Meta:
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"


class ConsumerProfile(models.Model):
    """Profile for consumers with preferences and delivery info"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='consumer_profile')
    delivery_address = models.CharField(max_length=200, blank=True, null=True)
    preferences = models.CharField(max_length=100, blank=True, null=True)
    
    # Enhanced fields for international consumers
    dietary_restrictions = models.JSONField(default=list, blank=True)
    preferred_categories = models.JSONField(default=list, blank=True)
    budget_range = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Budget-friendly'),
            ('medium', 'Mid-range'),
            ('high', 'Premium'),
            ('luxury', 'Luxury')
        ],
        blank=True
    )
    delivery_preferences = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user.has_role('CONSUMER'):
            raise ValueError("User must have the 'CONSUMER' role")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.display_name} - Consumer Profile"

    class Meta:
        verbose_name = "Consumer Profile"
        verbose_name_plural = "Consumer Profiles"


class InstitutionProfile(models.Model):
    """Profile for institutional buyers like restaurants, hotels, etc."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='institution_profile')
    organization_name = models.CharField(max_length=100)
    organization_type = models.CharField(
        max_length=50,
        choices=[
            ('restaurant', 'Restaurant'),
            ('hotel', 'Hotel'),
            ('school', 'School'),
            ('hospital', 'Hospital'),
            ('retailer', 'Retailer'),
            ('distributor', 'Distributor'),
            ('processor', 'Food Processor'),
            ('other', 'Other')
        ]
    )
    tax_id = models.CharField(max_length=50, blank=True, null=True)
      # Enhanced fields for international institutions
    business_license = models.CharField(max_length=100, blank=True)
    annual_volume = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Annual purchase volume in kg"
    )
    procurement_schedule = models.JSONField(default=dict, blank=True)
    quality_requirements = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user.has_role('INSTITUTION'):
            raise ValueError("User must have the 'INSTITUTION' role")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.organization_name} - Institution Profile"

    class Meta:
        verbose_name = "Institution Profile"
        verbose_name_plural = "Institution Profiles"


class AgentProfile(models.Model):
    """Profile for sales agents and field officers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    agent_type = models.CharField(
        max_length=50,
        choices=[
            ('sales_representative', 'Sales Representative'),
            ('field_officer', 'Field Officer'),
            ('extension_agent', 'Agricultural Extension Agent'),
            ('technical_advisor', 'Technical Advisor'),
            ('market_liaison', 'Market Liaison Officer'),
            ('customer_support', 'Customer Support Agent'),
        ],
        default='sales_representative'
    )
    
    # Territory and Coverage
    assigned_regions = models.JSONField(default=list, blank=True, help_text="Regions this agent covers")
    territory_size_km = models.PositiveIntegerField(null=True, blank=True, help_text="Territory coverage in sq km")
    target_farmers = models.PositiveIntegerField(default=100, help_text="Target number of farmers to manage")
    
    # Performance Metrics
    farmers_registered = models.PositiveIntegerField(default=0)
    total_sales_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, help_text="Commission percentage")
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    # Contact and Training
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    training_certifications = models.JSONField(default=list, blank=True)
    languages_spoken = models.JSONField(default=list, blank=True)
    vehicle_type = models.CharField(max_length=50, blank=True, help_text="Transportation method")
    
    # Status
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_field_visit = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user.has_role('AGENT'):
            raise ValueError("User must have the 'AGENT' role")
        if not self.employee_id:
            self.employee_id = f"AGT{self.user.id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.display_name} - {self.get_agent_type_display()}"

    class Meta:
        verbose_name = "Agent Profile"
        verbose_name_plural = "Agent Profiles"


class FinancialPartnerProfile(models.Model):
    """Profile for financial partners including banks, mobile money operators, and microfinance institutions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_partner_profile')
    
    # Organization Details
    institution_name = models.CharField(max_length=200)
    institution_type = models.CharField(
        max_length=50,
        choices=[
            ('commercial_bank', 'Commercial Bank'),
            ('mobile_money', 'Mobile Money Operator'),
            ('microfinance', 'Microfinance Institution'),
            ('cooperative_bank', 'Cooperative Bank'),
            ('development_bank', 'Development Bank'),
            ('payment_processor', 'Payment Processor'),
            ('fintech', 'FinTech Company'),
            ('insurance', 'Insurance Company'),
        ]
    )
    
    # Registration and Compliance
    registration_number = models.CharField(max_length=100, blank=True)
    central_bank_license = models.CharField(max_length=100, blank=True)
    regulatory_authority = models.CharField(max_length=200, blank=True)
    
    # Services Offered
    services_offered = models.JSONField(default=list, blank=True, help_text="List of financial services")
    supported_currencies = models.JSONField(default=list, blank=True)
    minimum_transaction = models.DecimalField(max_digits=15, decimal_places=2, default=1.0)
    maximum_transaction = models.DecimalField(max_digits=15, decimal_places=2, default=1000000.0)
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    
    # Geographic Coverage
    countries_served = models.JSONField(default=list, blank=True)
    regions_served = models.JSONField(default=list, blank=True)
    branch_locations = models.JSONField(default=list, blank=True)
    
    # API and Integration
    api_endpoint = models.URLField(blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    api_key_active = models.BooleanField(default=False)
    integration_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('testing', 'Testing'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
        ],
        default='pending'
    )
    
    # Performance Metrics
    total_transactions_processed = models.BigIntegerField(default=0)
    total_volume_processed = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_processing_time = models.DurationField(default=timedelta(minutes=5))
    
    # Contact Information
    primary_contact_name = models.CharField(max_length=200, blank=True)
    primary_contact_email = models.EmailField(blank=True)
    primary_contact_phone = models.CharField(max_length=20, blank=True)
    technical_support_email = models.EmailField(blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    partnership_start_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user.has_role('FINANCIAL_PARTNER'):
            raise ValueError("User must have the 'FINANCIAL_PARTNER' role")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.institution_name} - {self.get_institution_type_display()}"

    class Meta:
        verbose_name = "Financial Partner Profile"
        verbose_name_plural = "Financial Partner Profiles"


class GovernmentOfficialProfile(models.Model):
    """Profile for government officials and agricultural ministry representatives"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='government_official_profile')
    
    # Official Details
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    official_title = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    ministry = models.CharField(max_length=200, default='Ministry of Food and Agriculture')
    
    # Position and Authority
    position_level = models.CharField(
        max_length=50,
        choices=[
            ('minister', 'Minister'),
            ('deputy_minister', 'Deputy Minister'),
            ('director', 'Director'),
            ('deputy_director', 'Deputy Director'),
            ('principal_officer', 'Principal Officer'),
            ('senior_officer', 'Senior Officer'),
            ('officer', 'Officer'),
            ('field_coordinator', 'Field Coordinator'),
            ('inspector', 'Inspector'),
            ('advisor', 'Technical Advisor'),
        ]
    )
    
    # Jurisdiction and Responsibilities
    jurisdiction_level = models.CharField(
        max_length=30,
        choices=[
            ('national', 'National'),
            ('regional', 'Regional'),
            ('district', 'District'),
            ('local', 'Local'),
        ],
        default='district'
    )
    assigned_regions = models.JSONField(default=list, blank=True, help_text="Regions under jurisdiction")
    policy_areas = models.JSONField(default=list, blank=True, help_text="Agricultural policy areas of expertise")
    
    # Authority and Permissions
    can_approve_certifications = models.BooleanField(default=False)
    can_issue_permits = models.BooleanField(default=False)
    can_conduct_inspections = models.BooleanField(default=False)
    can_authorize_subsidies = models.BooleanField(default=False)
    approval_limit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Contact and Office
    office_address = models.TextField(blank=True)
    office_phone = models.CharField(max_length=20, blank=True)
    office_email = models.EmailField(blank=True)
    superior_officer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Specializations
    agricultural_specializations = models.JSONField(default=list, blank=True)
    certifications_held = models.JSONField(default=list, blank=True)
    years_in_service = models.PositiveIntegerField(default=0)
    
    # Performance and Activity
    farmers_supervised = models.PositiveIntegerField(default=0)
    inspections_conducted = models.PositiveIntegerField(default=0)
    policies_implemented = models.PositiveIntegerField(default=0)
    last_field_activity = models.DateTimeField(null=True, blank=True)
    
    # Status
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('temporary', 'Temporary Assignment'),
            ('transferred', 'Transferred'),
            ('retired', 'Retired'),
            ('suspended', 'Suspended'),
        ],
        default='active'
    )
    security_clearance = models.CharField(max_length=50, blank=True)
    appointment_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user.has_role('GOVERNMENT_OFFICIAL'):
            raise ValueError("User must have the 'GOVERNMENT_OFFICIAL' role")
        if not self.employee_id:
            self.employee_id = f"GOV{self.user.id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.display_name} - {self.official_title} ({self.department})"

    class Meta:
        verbose_name = "Government Official Profile"
        verbose_name_plural = "Government Official Profiles"


# ======================== SIGNALS FOR DEFAULT ROLES ========================

from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    """Create default roles after migration"""
    if sender.name == "apps.users":
        Role.objects.get_or_create(name="CONSUMER", defaults={"is_default": True})
        Role.objects.get_or_create(name="FARMER", defaults={"is_default": True})
        Role.objects.get_or_create(name="INSTITUTION", defaults={"is_default": True})
        Role.objects.get_or_create(name="SUPER_ADMIN", defaults={"is_default": False})
