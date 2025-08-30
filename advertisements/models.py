"""
Advertisement & Marketing System Models
Comprehensive advertising platform for AgriConnect
Implements Section 4.6 of PRD requirements
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class AdvertisementPlacement(models.Model):
    """Define where advertisements can be placed"""
    
    LOCATION_CHOICES = [
        ('homepage_banner', 'Homepage Banner'),
        ('search_results', 'Search Results'),
        ('product_detail', 'Product Detail Page'),
        ('category_page', 'Category Page'),
        ('mobile_app', 'Mobile App'),
        ('farmer_dashboard', 'Farmer Dashboard'),
        ('marketplace', 'Marketplace'),
        ('sidebar', 'Sidebar'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    dimensions = models.CharField(max_length=20, blank=True, help_text="e.g., 728x90, 300x250")
    max_file_size_mb = models.PositiveIntegerField(default=5)
    price_per_impression = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal('0.0010'),
        help_text="Cost per thousand impressions (CPM)"
    )
    price_per_click = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal('0.0500'),
        help_text="Cost per click (CPC)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['location', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.location})"

class Advertisement(models.Model):
    """Core advertisement model with comprehensive features"""
    
    AD_TYPE_CHOICES = [
        ('product_promotion', 'Product Promotion'),
        ('farmer_spotlight', 'Farmer Spotlight'),
        ('seasonal_campaign', 'Seasonal Campaign'),
        ('brand_awareness', 'Brand Awareness'),
        ('value_addition', 'Value Addition Services'),
        ('equipment_rental', 'Equipment Rental'),
        ('training_program', 'Training Program'),
        ('market_price_alert', 'Market Price Alert'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    PRICING_MODEL_CHOICES = [
        ('cpm', 'Cost Per Mille (Impressions)'),
        ('cpc', 'Cost Per Click'),
        ('cpa', 'Cost Per Action'),
        ('flat_rate', 'Flat Rate'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advertiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advertisements')
    title = models.CharField(max_length=200)
    description = models.TextField()
    ad_type = models.CharField(max_length=20, choices=AD_TYPE_CHOICES)
    
    # Campaign relationship
    campaign = models.ForeignKey(
        'AdvertisementCampaign', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='advertisements'
    )
    
    # Targeting Configuration (JSON fields for flexibility)
    target_audience = models.JSONField(default=dict, help_text="Age, interests, behavior targeting")
    geographic_targeting = models.JSONField(default=dict, help_text="Countries, regions, cities")
    demographic_targeting = models.JSONField(default=dict, help_text="Gender, occupation, income")
    product_categories = models.JSONField(default=list, help_text="Relevant product categories")
    
    # Creative Assets
    banner_image_url = models.URLField(max_length=500, blank=True)
    banner_mobile_url = models.URLField(max_length=500, blank=True)
    video_url = models.URLField(max_length=500, blank=True)
    landing_page_url = models.URLField(max_length=500, blank=True)
    call_to_action = models.CharField(max_length=50, default="Learn More")
    
    # Campaign Settings
    budget = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('10.00'))])
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0500'))
    pricing_model = models.CharField(max_length=20, choices=PRICING_MODEL_CHOICES, default='cpc')
    currency = models.CharField(max_length=3, default='GHS')
    
    # Schedule
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Status and Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approval_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_ads')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Performance Metrics (updated in real-time)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Placements
    placements = models.ManyToManyField(AdvertisementPlacement, through='AdvertisementPlacementAssignment')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['advertiser', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['ad_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.advertiser.get_full_name()})"
    
    @property
    def is_active(self):
        """Check if advertisement is currently active"""
        now = timezone.now()
        return (
            self.status == 'active' and
            self.start_date <= now <= self.end_date and
            (not self.daily_budget or self.amount_spent < self.budget)
        )
    
    @property
    def click_through_rate(self):
        """Calculate CTR percentage"""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100
    
    @property
    def conversion_rate(self):
        """Calculate conversion rate percentage"""
        if self.clicks == 0:
            return 0.0
        return (self.conversions / self.clicks) * 100
    
    @property
    def cost_per_click(self):
        """Calculate actual CPC"""
        if self.clicks == 0:
            return Decimal('0.00')
        return self.amount_spent / self.clicks
    
    @property
    def cost_per_acquisition(self):
        """Calculate CPA"""
        if self.conversions == 0:
            return Decimal('0.00')
        return self.amount_spent / self.conversions

class AdvertisementPlacementAssignment(models.Model):
    """Through model for advertisement-placement relationship"""
    
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    placement = models.ForeignKey(AdvertisementPlacement, on_delete=models.CASCADE)
    priority = models.PositiveIntegerField(default=1, help_text="Display priority (1=highest)")
    max_impressions = models.PositiveIntegerField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['advertisement', 'placement']
        ordering = ['priority']

class AdvertisementPerformanceLog(models.Model):
    """Track individual advertisement interactions"""
    
    EVENT_TYPE_CHOICES = [
        ('impression', 'Impression'),
        ('click', 'Click'),
        ('conversion', 'Conversion'),
        ('view', 'View'),
        ('engagement', 'Engagement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='performance_logs')
    placement = models.ForeignKey(AdvertisementPlacement, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    
    # User tracking (optional for privacy)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Technical details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(max_length=500, blank=True)
    
    # Cost tracking
    cost = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.0000'))
    
    # Additional data
    metadata = models.JSONField(default=dict, help_text="Additional event data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['advertisement', 'event_type', 'created_at']),
            models.Index(fields=['placement', 'event_type']),
            models.Index(fields=['created_at']),
        ]

class AdvertisementCampaign(models.Model):
    """Group multiple advertisements into campaigns"""
    
    CAMPAIGN_TYPE_CHOICES = [
        ('seasonal', 'Seasonal Campaign'),
        ('product_launch', 'Product Launch'),
        ('brand_awareness', 'Brand Awareness'),
        ('farmer_education', 'Farmer Education'),
        ('market_expansion', 'Market Expansion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
    
    # Campaign manager
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_campaigns')
    
    # Budget and timing
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Goals and KPIs
    target_impressions = models.PositiveIntegerField(null=True, blank=True)
    target_clicks = models.PositiveIntegerField(null=True, blank=True)
    target_conversions = models.PositiveIntegerField(null=True, blank=True)
    target_ctr = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Target CTR %")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def advertisements_count(self):
        return self.advertisements.count()
    
    @property
    def total_spent(self):
        return self.advertisements.aggregate(
            total=models.Sum('amount_spent')
        )['total'] or Decimal('0.00')
    
    @property
    def total_impressions(self):
        return self.advertisements.aggregate(
            total=models.Sum('impressions')
        )['total'] or 0
    
    @property
    def total_clicks(self):
        return self.advertisements.aggregate(
            total=models.Sum('clicks')
        )['total'] or 0

class AdvertisementAnalytics(models.Model):
    """Daily aggregated analytics for advertisements"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='daily_analytics')
    date = models.DateField()
    
    # Daily metrics
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Calculated metrics
    ctr = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    cpc = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.0000'))
    cpa = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.0000'))
      # Audience insights
    audience_demographics = models.JSONField(default=dict)
    geographic_performance = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['advertisement', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['advertisement', 'date']),
            models.Index(fields=['date']),
        ]
