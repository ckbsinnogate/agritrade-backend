"""
AgriConnect Processing Recipes Models
Recipe sharing system for processor integration and technical support

Features:
- Processing recipe creation and management
- Recipe sharing between processors
- Technical support documentation
- Quality standards and best practices
- Recipe verification and rating system
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ProcessingRecipe(models.Model):
    """
    Processing recipes for value-addition and technical support.
    Enables processors to share best practices and standardized procedures.
    """
    
    SKILL_LEVEL_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    RECIPE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('public', 'Public'),
        ('verified', 'Verified'),
        ('deprecated', 'Deprecated'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipe_name = models.CharField(max_length=200)
    processor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processing_recipes')
    
    # Recipe Details
    description = models.TextField()
    skill_level_required = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='basic')
    processing_time_minutes = models.PositiveIntegerField(help_text="Total processing time in minutes")
    
    # Input Materials (JSON format)
    input_materials = models.JSONField(
        help_text="List of input materials with quantities",
        default=list
    )
    
    # Processing Steps (JSON format)
    processing_steps = models.JSONField(
        help_text="Detailed step-by-step processing instructions",
        default=list
    )
    
    # Equipment and Requirements
    equipment_required = models.JSONField(
        help_text="List of required equipment and tools",
        default=list
    )
    
    # Output Products (JSON format)
    output_products = models.JSONField(
        help_text="Expected output products with quantities",
        default=list
    )
    
    # Quality Control
    expected_yield_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    quality_checkpoints = models.JSONField(
        help_text="Quality control checkpoints during processing",
        default=list
    )
    quality_standards = models.JSONField(
        help_text="Quality standards and specifications",
        default=dict
    )
    
    # Cost Analysis
    processing_cost_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Processing cost per unit in GHS"
    )
    labor_hours_required = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Labor hours required for processing"
    )
    
    # Environmental Impact
    energy_consumption = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Energy consumption in kWh per unit"
    )
    water_usage_liters = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Water usage in liters"
    )
    waste_generation_kg = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Waste generation in kg"
    )
    
    # Certifications and Compliance
    certifications_achieved = models.JSONField(
        help_text="Certifications achieved using this recipe",
        default=list
    )
    compliance_standards = models.JSONField(
        help_text="Compliance standards met",
        default=list
    )
    
    # Recipe Status and Verification
    status = models.CharField(max_length=20, choices=RECIPE_STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='verified_recipes'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Usage Tracking
    times_used = models.PositiveIntegerField(default=0)
    success_rate_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Recipe Rating
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    rating_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    tags = models.JSONField(default=list, help_text="Recipe tags for categorization")
    seasonal_availability = models.BooleanField(default=False)
    available_seasons = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['processor', '-created_at']),
            models.Index(fields=['status', 'is_public']),
            models.Index(fields=['skill_level_required']),
            models.Index(fields=['-average_rating']),
        ]
    
    def __str__(self):
        return f"{self.recipe_name} by {self.processor.username}"
    
    @property
    def is_active(self):
        """Check if recipe is active and usable"""
        return self.status in ['public', 'verified'] and self.is_public


class RecipeRating(models.Model):
    """
    Rating system for processing recipes
    """
    
    recipe = models.ForeignKey(ProcessingRecipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_ratings')
    
    # Ratings (1-5 scale)
    overall_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    clarity_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How clear and easy to follow are the instructions"
    )
    effectiveness_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How effective is this recipe in achieving results"
    )
    accuracy_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How accurate are the yield and time estimates"
    )
    
    # Review Content
    review_title = models.CharField(max_length=200, blank=True)
    review_content = models.TextField(blank=True)
    
    # Usage Experience
    actual_yield_achieved = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    processing_time_actual = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Actual processing time experienced in minutes"
    )
    
    # Recommendations
    would_recommend = models.BooleanField(default=True)
    improvement_suggestions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['recipe', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rating for {self.recipe.recipe_name} by {self.user.username}"


class RecipeUsageLog(models.Model):
    """
    Track usage of processing recipes for analytics
    """
    
    recipe = models.ForeignKey(ProcessingRecipe, on_delete=models.CASCADE, related_name='usage_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_usage')
    
    # Usage Details
    used_at = models.DateTimeField(auto_now_add=True)
    processing_facility = models.CharField(max_length=200, blank=True)
    batch_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Results
    success = models.BooleanField(default=True)
    actual_yield = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    processing_time_actual = models.PositiveIntegerField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    issues_encountered = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-used_at']
    
    def __str__(self):
        return f"Usage of {self.recipe.recipe_name} by {self.user.username}"


class RecipeComment(models.Model):
    """
    Comments and discussions on processing recipes
    """
    
    recipe = models.ForeignKey(ProcessingRecipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    is_question = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)
    
    # Helpful voting
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment on {self.recipe.recipe_name} by {self.user.username}"


class ProcessorProfile(models.Model):
    """
    Extended profile for processors with specializations and capabilities
    """
    
    PROCESSOR_TYPE_CHOICES = [
        ('mill', 'Milling'),
        ('oil_extraction', 'Oil Extraction'),
        ('food_processing', 'Food Processing'),
        ('packaging', 'Packaging'),
        ('drying', 'Drying'),
        ('sorting', 'Sorting & Grading'),
        ('storage', 'Storage & Warehousing'),
        ('multi_purpose', 'Multi-Purpose'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='processor_profile')
    
    # Business Information
    business_name = models.CharField(max_length=200)
    business_registration_number = models.CharField(max_length=100, blank=True)
    processor_type = models.CharField(max_length=30, choices=PROCESSOR_TYPE_CHOICES)
    
    # Specializations
    specializations = models.JSONField(default=list, help_text="List of processing specializations")
    processing_capabilities = models.JSONField(default=list, help_text="List of processing capabilities")
    
    # Capacity and Equipment
    daily_processing_capacity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    capacity_unit = models.CharField(max_length=20, default='kg')
    equipment_list = models.JSONField(default=list)
    
    # Certifications
    certifications = models.JSONField(default=list)
    health_permits = models.JSONField(default=list)
    quality_standards = models.JSONField(default=list)
    
    # Location and Contact
    location = models.JSONField(default=dict, help_text="Location coordinates and address")
    service_radius_km = models.PositiveIntegerField(default=50)
    
    # Business Hours
    operating_hours = models.JSONField(default=dict)
    seasonal_operation = models.BooleanField(default=False)
    operating_seasons = models.JSONField(default=list)
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_documents = models.JSONField(default=list)
    
    # Metrics
    total_recipes_shared = models.PositiveIntegerField(default=0)
    average_recipe_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00
    )
    total_processing_orders = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business_name} - {self.user.username}"
