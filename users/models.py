"""
AgriConnect API - User Profile Models
Profile models for the agricultural eCommerce platform.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from decimal import Decimal
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Import User model from authentication app
User = get_user_model()


def user_directory_path(instance, filename):
    """Generate upload path for user files"""
    return f'user_{instance.user.id}/{filename}'


class ExtendedUserProfile(models.Model):
    """Extended user profile with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="extended_profile")
    bio = models.TextField(blank=True, null=True)
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
    address_line_1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    newsletter_subscription = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

    class Meta:
        verbose_name = "Extended User Profile"
        verbose_name_plural = "Extended User Profiles"


class FarmerProfile(models.Model):
    """Profile for farmers with agricultural information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_size = models.FloatField(
        validators=[MinValueValidator(Decimal('0.1'))],
        default=1.0,
        help_text="Farm size in hectares"
    )
    organic_certified = models.BooleanField(default=False)
    years_of_experience = models.PositiveIntegerField(default=0)
    production_capacity = models.FloatField(default=100.0, help_text="Annual production in kg")
    farm_name = models.CharField(max_length=200, blank=True)
    farm_type = models.CharField(
        max_length=50,
        choices=[
            ('crop', 'Crop Farming'),
            ('livestock', 'Livestock'),
            ('mixed', 'Mixed Farming'),
            ('organic', 'Organic Farming'),
        ],
        blank=True
    )
    primary_crops = models.JSONField(default=list, blank=True)
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
    dietary_restrictions = models.JSONField(default=list, blank=True)
    preferred_categories = models.JSONField(default=list, blank=True)
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
    business_license = models.CharField(max_length=100, blank=True)
    annual_volume = models.PositiveIntegerField(null=True, blank=True, help_text="Annual purchase volume in kg")
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
        ],
        default='sales_representative'
    )
    assigned_regions = models.JSONField(default=list, blank=True)
    target_farmers = models.PositiveIntegerField(default=100)
    farmers_registered = models.PositiveIntegerField(default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
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
    """Profile for financial partners"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_partner_profile')
    institution_name = models.CharField(max_length=200)
    institution_type = models.CharField(
        max_length=50,
        choices=[
            ('commercial_bank', 'Commercial Bank'),
            ('mobile_money', 'Mobile Money Operator'),
            ('microfinance', 'Microfinance Institution'),
            ('fintech', 'FinTech Company'),
        ]
    )
    registration_number = models.CharField(max_length=100, blank=True)
    services_offered = models.JSONField(default=list, blank=True)
    supported_currencies = models.JSONField(default=list, blank=True)
    minimum_transaction = models.DecimalField(max_digits=15, decimal_places=2, default=1.0)
    maximum_transaction = models.DecimalField(max_digits=15, decimal_places=2, default=1000000.0)
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
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
    is_verified = models.BooleanField(default=False)
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
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    official_title = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    ministry = models.CharField(max_length=200, default='Ministry of Food and Agriculture')
    position_level = models.CharField(
        max_length=50,
        choices=[
            ('minister', 'Minister'),
            ('director', 'Director'),
            ('senior_officer', 'Senior Officer'),
            ('officer', 'Officer'),
            ('inspector', 'Inspector'),
        ]
    )
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
    assigned_regions = models.JSONField(default=list, blank=True)
    can_approve_certifications = models.BooleanField(default=False)
    can_issue_permits = models.BooleanField(default=False)
    can_conduct_inspections = models.BooleanField(default=False)
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('temporary', 'Temporary Assignment'),
            ('transferred', 'Transferred'),
            ('retired', 'Retired'),
        ],
        default='active'
    )
    appointment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"GOV{self.user.id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.official_title}"

    class Meta:
        verbose_name = "Government Official Profile"
        verbose_name_plural = "Government Official Profiles"