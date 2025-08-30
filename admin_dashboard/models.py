"""
Administrator Dashboard Backend Implementation
Complete backend system for Administrator Dashboard Platform Overview & Management

This module provides comprehensive backend APIs for all admin dashboard sections:
- Settings Section: System configuration and preferences management
- System Section: Platform health, monitoring, and maintenance
- Analytics Section: Comprehensive analytics and reporting
- Content Section: Content management and moderation
- Users Section: Advanced user management and administration

Built with 40+ years of web development experience and Django best practices.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


# ======================== SETTINGS SECTION MODELS ========================

class SystemSettings(models.Model):
    """System-wide configuration settings"""
    
    SETTING_CATEGORIES = [
        ('GENERAL', 'General Settings'),
        ('SECURITY', 'Security Configuration'),
        ('EMAIL', 'Email Configuration'),
        ('SMS', 'SMS Configuration'),
        ('PAYMENT', 'Payment Settings'),
        ('API', 'API Configuration'),
        ('FEATURE', 'Feature Toggles'),
        ('NOTIFICATION', 'Notification Settings'),
    ]
    
    category = models.CharField(max_length=20, choices=SETTING_CATEGORIES)
    key = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)  # Can be accessed by non-admin users
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_settings')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_settings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['category', 'key']
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.category}.{self.key}"


class AdminPreferences(models.Model):
    """Individual admin user preferences"""
    
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_preferences')
    dashboard_layout = models.JSONField(default=dict)  # Dashboard widget layout
    notification_settings = models.JSONField(default=dict)  # Admin notification preferences
    theme_settings = models.JSONField(default=dict)  # UI theme preferences
    default_filters = models.JSONField(default=dict)  # Default filter settings
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    items_per_page = models.IntegerField(default=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.admin_user.username}"


# ======================== SYSTEM SECTION MODELS ========================

class SystemHealthCheck(models.Model):
    """System health monitoring"""
    
    HEALTH_STATUS = [
        ('HEALTHY', 'Healthy'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('DOWN', 'Down'),
    ]
    
    SERVICE_TYPES = [
        ('DATABASE', 'Database'),
        ('REDIS', 'Redis Cache'),
        ('EMAIL', 'Email Service'),
        ('SMS', 'SMS Service'),
        ('PAYMENT', 'Payment Gateway'),
        ('STORAGE', 'File Storage'),
        ('API', 'External API'),
        ('QUEUE', 'Background Queue'),
    ]
    
    service_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    status = models.CharField(max_length=20, choices=HEALTH_STATUS)
    response_time = models.FloatField(help_text="Response time in milliseconds")
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.service_name} - {self.status}"


class SystemMaintenanceLog(models.Model):
    """System maintenance and updates log"""
    
    MAINTENANCE_TYPES = [
        ('UPDATE', 'System Update'),
        ('PATCH', 'Security Patch'),
        ('MIGRATION', 'Database Migration'),
        ('CLEANUP', 'Data Cleanup'),
        ('BACKUP', 'System Backup'),
        ('RESTORE', 'System Restore'),
        ('CONFIG', 'Configuration Change'),
    ]
    
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    was_successful = models.BooleanField(default=True)
    affected_services = models.JSONField(default=list)
    downtime_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.maintenance_type}: {self.title}"


# ======================== ANALYTICS SECTION MODELS ========================

class AnalyticsSnapshot(models.Model):
    """Daily analytics snapshots for historical data"""
    
    date = models.DateField()
    total_users = models.IntegerField()
    active_users = models.IntegerField()
    new_registrations = models.IntegerField()
    total_orders = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    total_products = models.IntegerField()
    total_transactions = models.IntegerField()
    platform_usage_hours = models.FloatField()
    api_requests = models.IntegerField()
    errors_count = models.IntegerField()
    conversion_rate = models.FloatField()
    metadata = models.JSONField(default=dict)  # Additional custom metrics
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"


class CustomAnalyticsReport(models.Model):
    """Custom analytics reports created by admins"""
    
    REPORT_TYPES = [
        ('USER', 'User Analytics'),
        ('SALES', 'Sales Analytics'),
        ('PRODUCT', 'Product Analytics'),
        ('ENGAGEMENT', 'Engagement Analytics'),
        ('FINANCIAL', 'Financial Analytics'),
        ('CUSTOM', 'Custom Query'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    query_config = models.JSONField()  # Report configuration and filters
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)  # daily, weekly, monthly
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)  # Share with other admins
    last_generated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


# ======================== CONTENT SECTION MODELS ========================

class ContentModerationQueue(models.Model):
    """Content moderation queue for review"""
    
    CONTENT_TYPES = [
        ('USER_PROFILE', 'User Profile'),
        ('PRODUCT', 'Product Listing'),
        ('REVIEW', 'Product Review'),
        ('COMMENT', 'Comment'),
        ('IMAGE', 'Image Upload'),
        ('RECIPE', 'Processing Recipe'),
        ('ADVERTISEMENT', 'Advertisement'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FLAGGED', 'Flagged for Admin'),
        ('SPAM', 'Marked as Spam'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.CharField(max_length=100)  # ID of the content being moderated
    content_title = models.CharField(max_length=200)
    content_preview = models.TextField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_content')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_content')
    moderation_notes = models.TextField(blank=True)
    priority = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    auto_flagged = models.BooleanField(default=False)
    flag_reasons = models.JSONField(default=list)
    submitted_at = models.DateTimeField(auto_now_add=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['priority', '-submitted_at']
    
    def __str__(self):
        return f"{self.content_type}: {self.content_title}"


class ContentPolicy(models.Model):
    """Content policies and guidelines"""
    
    POLICY_TYPES = [
        ('GENERAL', 'General Content'),
        ('PRODUCT', 'Product Listings'),
        ('REVIEWS', 'Reviews and Ratings'),
        ('IMAGES', 'Image Content'),
        ('SPAM', 'Spam Detection'),
        ('SAFETY', 'Safety Guidelines'),
    ]
    
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    rules = models.JSONField()  # Detailed policy rules
    auto_enforcement = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.policy_type}: {self.title}"


# ======================== USERS SECTION MODELS ========================

class UserActivityLog(models.Model):
    """Detailed user activity tracking for admin analysis"""
    
    ACTIVITY_TYPES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('ORDER_PLACED', 'Order Placed'),
        ('PRODUCT_CREATED', 'Product Created'),
        ('REVIEW_POSTED', 'Review Posted'),
        ('PAYMENT_MADE', 'Payment Made'),
        ('SUPPORT_TICKET', 'Support Ticket'),
        ('VIOLATION', 'Policy Violation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.activity_type}"


class UserSecurityEvent(models.Model):
    """Security-related events for users"""
    
    EVENT_TYPES = [
        ('SUSPICIOUS_LOGIN', 'Suspicious Login Attempt'),
        ('MULTIPLE_FAILURES', 'Multiple Login Failures'),
        ('PASSWORD_RESET', 'Password Reset Request'),
        ('ACCOUNT_LOCKED', 'Account Locked'),
        ('UNUSUAL_ACTIVITY', 'Unusual Activity Detected'),
        ('DATA_BREACH', 'Potential Data Breach'),
        ('ADMIN_ACTION', 'Administrative Action'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    description = models.CharField(max_length=200)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_security_events')
    resolution_notes = models.TextField(blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-occurred_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.event_type} ({self.severity})"


class AdminActionLog(models.Model):
    """Log of all administrative actions"""
    
    ACTION_TYPES = [
        ('USER_CREATE', 'User Created'),
        ('USER_UPDATE', 'User Updated'),
        ('USER_DELETE', 'User Deleted'),
        ('USER_VERIFY', 'User Verified'),
        ('USER_SUSPEND', 'User Suspended'),
        ('SETTING_CHANGE', 'Setting Changed'),
        ('CONTENT_MODERATE', 'Content Moderated'),
        ('SYSTEM_MAINTENANCE', 'System Maintenance'),
        ('REPORT_GENERATE', 'Report Generated'),
        ('POLICY_UPDATE', 'Policy Updated'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_received')
    description = models.CharField(max_length=200)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.admin_user.username}: {self.action_type}"
