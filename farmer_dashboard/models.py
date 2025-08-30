"""
Farmer Dashboard Models
Extended models for farmer dashboard functionality
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class FarmerDashboardPreferences(models.Model):
    """Farmer dashboard preferences and settings"""
    farmer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_preferences')
    
    # Dashboard Settings
    default_currency = models.CharField(max_length=3, default='GHS')
    preferred_language = models.CharField(max_length=10, default='en')
    dashboard_theme = models.CharField(
        max_length=20, 
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='light'
    )
    
    # Notification Preferences
    weather_alerts = models.BooleanField(default=True)
    market_price_alerts = models.BooleanField(default=True)
    order_notifications = models.BooleanField(default=True)
    payment_reminders = models.BooleanField(default=True)
    
    # Analytics Preferences
    show_revenue_trends = models.BooleanField(default=True)
    show_crop_analytics = models.BooleanField(default=True)
    show_market_insights = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Farmer Dashboard Preference"
        verbose_name_plural = "Farmer Dashboard Preferences"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dashboard Preferences - {self.farmer.username}"


class FarmerAlert(models.Model):
    """Farmer alerts and notifications"""
    ALERT_TYPES = [
        ('weather', 'Weather Alert'),
        ('market', 'Market Price Alert'),
        ('inventory', 'Inventory Alert'),
        ('order', 'Order Update'),
        ('payment', 'Payment Reminder'),
        ('crop', 'Crop Advisory'),
        ('general', 'General Notice'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Optional reference to related objects
    related_product_id = models.CharField(max_length=100, blank=True, null=True)
    related_order_id = models.CharField(max_length=100, blank=True, null=True)
    related_farm_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Farmer Alert"
        verbose_name_plural = "Farmer Alerts"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farmer', 'is_read']),
            models.Index(fields=['alert_type', 'priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.farmer.username}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class FarmerDashboardMetrics(models.Model):
    """Daily metrics and analytics for farmers"""
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_metrics')
    date = models.DateField()
    
    # Revenue Metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    orders_count = models.IntegerField(default=0)
    products_sold = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Product Metrics
    total_products = models.IntegerField(default=0)
    active_products = models.IntegerField(default=0)
    low_stock_products = models.IntegerField(default=0)
    out_of_stock_products = models.IntegerField(default=0)
    
    # Customer Metrics
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    total_customers = models.IntegerField(default=0)
    
    # Farm Metrics
    farms_registered = models.IntegerField(default=0)
    total_farm_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Farmer Dashboard Metric"
        verbose_name_plural = "Farmer Dashboard Metrics"
        unique_together = ['farmer', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['farmer', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Metrics - {self.farmer.username} - {self.date}"


class FarmerGoal(models.Model):
    """Farmer goals and targets"""
    GOAL_TYPES = [
        ('revenue', 'Revenue Target'),
        ('production', 'Production Volume'),
        ('customers', 'Customer Acquisition'),
        ('farms', 'Farm Expansion'),
        ('sustainability', 'Sustainability Goal'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    
    target_value = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, default='GHS')
    
    start_date = models.DateField()
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Farmer Goal"
        verbose_name_plural = "Farmer Goals"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.farmer.username}"
    
    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return min(100, (self.current_value / self.target_value) * 100)
        return 0
    
    @property
    def days_remaining(self):
        if self.target_date:
            remaining = (self.target_date - timezone.now().date()).days
            return max(0, remaining)
        return 0
