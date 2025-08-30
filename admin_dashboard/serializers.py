"""
Administrator Dashboard Serializers
Comprehensive API serializers for all admin dashboard backend operations

This module provides serializers for:
- Settings Section: System configuration and preferences management
- System Section: Platform health, monitoring, and maintenance
- Analytics Section: Comprehensive analytics and reporting
- Content Section: Content management and moderation
- Users Section: Advanced user management and administration

Built with 40+ years of web development experience.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

from .models import (
    SystemSettings, AdminPreferences, SystemHealthCheck, SystemMaintenanceLog,
    AnalyticsSnapshot, CustomAnalyticsReport, ContentModerationQueue, ContentPolicy,
    UserActivityLog, UserSecurityEvent, AdminActionLog
)

User = get_user_model()


# ======================== SETTINGS SECTION SERIALIZERS ========================

class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for system settings"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta:
        model = SystemSettings
        fields = [
            'id', 'category', 'key', 'value', 'description', 'is_active', 'is_public',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']


class AdminPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for admin preferences"""
    admin_name = serializers.CharField(source='admin_user.get_full_name', read_only=True)
    
    class Meta:
        model = AdminPreferences
        fields = [
            'id', 'admin_user', 'admin_name', 'dashboard_layout', 'notification_settings',
            'theme_settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ======================== SYSTEM SECTION SERIALIZERS ========================

class SystemHealthCheckSerializer(serializers.ModelSerializer):
    """Serializer for system health checks"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SystemHealthCheck
        fields = [
            'id', 'service_name', 'service_type', 'status', 'status_display', 'response_time', 
            'error_message', 'metadata', 'checked_at'
        ]
        read_only_fields = ['id', 'checked_at']


class SystemMaintenanceLogSerializer(serializers.ModelSerializer):
    """Serializer for system maintenance logs"""
    
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = SystemMaintenanceLog
        fields = [
            'id', 'maintenance_type', 'title', 'description', 'was_successful',
            'started_at', 'completed_at', 'performed_by', 'performed_by_name', 
            'affected_services', 'downtime_minutes', 'notes'
        ]
        read_only_fields = ['id']


# ======================== ANALYTICS SECTION SERIALIZERS ========================

class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for analytics snapshots"""
    
    class Meta:
        model = AnalyticsSnapshot
        fields = [
            'id', 'date', 'total_users', 'new_registrations', 'active_users', 'total_orders',
            'total_revenue', 'total_products', 'total_transactions', 'platform_usage_hours',
            'api_requests', 'errors_count', 'conversion_rate', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CustomAnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer for custom analytics reports"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = CustomAnalyticsReport
        fields = [
            'id', 'name', 'description', 'report_type', 'query_config', 'is_scheduled',
            'schedule_frequency', 'created_by', 'created_by_name', 'is_public',
            'last_generated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_generated', 'created_at', 'updated_at']


# ======================== CONTENT SECTION SERIALIZERS ========================

class ContentModerationQueueSerializer(serializers.ModelSerializer):
    """Serializer for content moderation queue"""
    
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    moderated_by_name = serializers.CharField(source='moderated_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ContentModerationQueue
        fields = [
            'id', 'content_type', 'content_id', 'content_title', 'content_preview', 
            'submitted_by', 'submitted_by_name', 'status', 'status_display',
            'moderated_by', 'moderated_by_name', 'moderation_notes', 'priority',
            'auto_flagged', 'flag_reasons', 'submitted_at', 'moderated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'moderated_at']


class ContentPolicySerializer(serializers.ModelSerializer):
    """Serializer for content policies"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ContentPolicy
        fields = [
            'id', 'policy_type', 'title', 'description', 'rules', 'auto_enforcement',
            'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


# ======================== USERS SECTION SERIALIZERS ========================

class UserActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for user activity logs"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = [
            'id', 'user', 'user_name', 'activity_type', 'description', 'details', 
            'ip_address', 'user_agent', 'session_id', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class UserSecurityEventSerializer(serializers.ModelSerializer):
    """Serializer for user security events"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = UserSecurityEvent
        fields = [
            'id', 'user', 'user_name', 'event_type', 'severity', 'severity_display',
            'description', 'details', 'ip_address', 'is_resolved',
            'resolved_by', 'resolved_by_name', 'resolution_notes', 
            'occurred_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'occurred_at', 'resolved_at']


class AdminActionLogSerializer(serializers.ModelSerializer):
    """Serializer for admin action logs"""
    
    admin_name = serializers.CharField(source='admin_user.get_full_name', read_only=True)
    target_user_name = serializers.CharField(source='target_user.get_full_name', read_only=True)
    
    class Meta:
        model = AdminActionLog
        fields = [
            'id', 'admin_user', 'admin_name', 'action_type', 'target_user', 
            'target_user_name', 'description', 'details', 'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


# ======================== DASHBOARD OVERVIEW SERIALIZERS ========================

class DashboardOverviewSerializer(serializers.Serializer):
    """Serializer for dashboard overview data"""
    
    # General statistics
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    
    # Order statistics
    total_orders = serializers.IntegerField()
    orders_today = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_today = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Product statistics
    total_products = serializers.IntegerField()
    products_added_today = serializers.IntegerField()
    
    # System health
    system_status = serializers.CharField()
    last_health_check = serializers.DateTimeField()
    
    # Content moderation
    pending_moderations = serializers.IntegerField()
    resolved_today = serializers.IntegerField()
    
    # Security events
    security_events_today = serializers.IntegerField()
    unresolved_security_events = serializers.IntegerField()
    
    # System settings
    active_settings_count = serializers.IntegerField()
    
    # Recent activity summary
    recent_activities = serializers.ListField(child=serializers.DictField())


class BulkSettingsUpdateSerializer(serializers.Serializer):
    """Serializer for bulk settings updates"""
    
    updates = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )


class ContentModerationActionSerializer(serializers.Serializer):
    """Serializer for content moderation actions"""
    
    action = serializers.ChoiceField(choices=['approve', 'reject', 'escalate'])
    notes = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class SecurityEventResolutionSerializer(serializers.Serializer):
    """Serializer for resolving security events"""
    
    resolution_notes = serializers.CharField()
    action_taken = serializers.CharField(required=False, allow_blank=True)


class SystemHealthSummarySerializer(serializers.Serializer):
    """Serializer for system health summary"""
    
    overall_status = serializers.CharField()
    database_status = serializers.CharField()
    cache_status = serializers.CharField()
    api_status = serializers.CharField()
    external_services_status = serializers.CharField()
    last_check = serializers.DateTimeField()
    uptime_percentage = serializers.FloatField()
    response_time_avg = serializers.FloatField()


class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer for analytics dashboard data"""
    
    period = serializers.CharField()
    user_growth = serializers.DictField()
    revenue_trends = serializers.DictField()
    order_analytics = serializers.DictField()
    product_performance = serializers.DictField()
    geographic_distribution = serializers.DictField()
    conversion_rates = serializers.DictField()
