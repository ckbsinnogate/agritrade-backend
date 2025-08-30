# filepath: c:\Users\user\Desktop\mywebproject\myapiproject\apps\users\models.py
"""
AgriConnect API - User Profile Models

Profile models for the agricultural eCommerce platform.
These models extend the User model from the authentication app.

Components:
- UserProfile, FarmerProfile, ConsumerProfile, InstitutionProfile
- AgentProfile, FinancialPartnerProfile, GovernmentOfficialProfile
- International user support with multi-language and timezone capabilities

Author: GitHub Copilot
Created: July 4, 2025
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, EmailValidator, FileExtensionValidator
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
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
        return f"{self.user.get_full_name()} Profile"

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

    def __str__(self):
        return f"{self.user.get_full_name()} - Farmer Profile"

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

    def __str__(self):
        return f"{self.user.get_full_name()} - Consumer Profile"

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
        if not self.employee_id:
            self.employee_id = f"AGT{self.user.id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_agent_type_display()}"

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
        if not self.employee_id:
            self.employee_id = f"GOV{self.user.id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.official_title} ({self.department})"

    class Meta:
        verbose_name = "Government Official Profile"
        verbose_name_plural = "Government Official Profiles"
