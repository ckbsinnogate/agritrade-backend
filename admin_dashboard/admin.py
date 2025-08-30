"""
Administrator Dashboard Admin Interface
Django admin configuration for all admin dashboard backend models

This module provides Django admin interfaces for:
- Settings Section: System configuration and preferences management
- System Section: Platform health, monitoring, and maintenance
- Analytics Section: Comprehensive analytics and reporting
- Content Section: Content management and moderation
- Users Section: Advanced user management and administration

Built with 40+ years of web development experience.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.utils import timezone
import json

from .models import (
    SystemSettings, AdminPreferences, SystemHealthCheck, SystemMaintenanceLog,
    AnalyticsSnapshot, CustomAnalyticsReport, ContentModerationQueue, ContentPolicy,
    UserActivityLog, UserSecurityEvent, AdminActionLog
)


# ======================== SETTINGS SECTION ADMIN ========================

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin interface for system settings"""
    
    list_display = [
        'category', 'key', 'value_preview', 'is_active', 'is_public',
        'updated_by', 'updated_at'
    ]
    list_filter = ['category', 'is_active', 'is_public', 'created_at', 'updated_at']
    search_fields = ['key', 'description', 'value']
    readonly_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Setting Information', {
            'fields': ('category', 'key', 'value', 'description')
        }),
        ('Access Control', {
            'fields': ('is_active', 'is_public')
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def value_preview(self, obj):
        """Display truncated value"""
        if len(obj.value) > 50:
            return obj.value[:50] + "..."
        return obj.value
    value_preview.short_description = 'Value'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AdminPreferences)
class AdminPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for admin preferences"""
    
    list_display = ['admin_user', 'dashboard_layout', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['admin_user__username', 'admin_user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Admin Information', {
            'fields': ('admin_user',)
        }),
        ('Dashboard Settings', {
            'fields': ('dashboard_layout', 'theme_settings')
        }),
        ('Notifications', {
            'fields': ('notification_settings',)
        }),
        ('Preferences', {
            'fields': ('default_filters', 'timezone', 'language', 'items_per_page')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# ======================== SYSTEM SECTION ADMIN ========================

@admin.register(SystemHealthCheck)
class SystemHealthCheckAdmin(admin.ModelAdmin):
    """Admin interface for system health checks"""
    
    list_display = [
        'service_name', 'service_type', 'status_badge', 'response_time', 'checked_at'
    ]
    list_filter = ['service_type', 'status', 'checked_at']
    search_fields = ['service_name', 'error_message']
    readonly_fields = ['checked_at']
    
    fieldsets = (
        ('Check Information', {
            'fields': ('service_name', 'service_type', 'status', 'response_time')
        }),
        ('Results', {
            'fields': ('error_message', 'metadata')
        }),
        ('Metadata', {
            'fields': ('checked_at',)
        })
    )
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'HEALTHY': 'green',
            'WARNING': 'orange', 
            'CRITICAL': 'red',
            'DOWN': 'darkred'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(SystemMaintenanceLog)
class SystemMaintenanceLogAdmin(admin.ModelAdmin):
    """Admin interface for system maintenance logs"""
    
    list_display = [
        'title', 'maintenance_type', 'status_badge', 'started_at',
        'performed_by'
    ]
    list_filter = ['maintenance_type', 'was_successful', 'started_at']
    search_fields = ['title', 'description']
    readonly_fields = []
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': ('maintenance_type', 'title', 'description')
        }),
        ('Schedule', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Execution', {
            'fields': ('performed_by', 'was_successful', 'affected_services', 'downtime_minutes', 'notes')
        })
    )
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        if obj.was_successful:
            color = 'green'
            status = 'Success'
        else:
            color = 'red'
            status = 'Failed'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'


# ======================== ANALYTICS SECTION ADMIN ========================

@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    """Admin interface for analytics snapshots"""
    
    list_display = [
        'date', 'total_users', 'new_registrations', 'total_orders',
        'total_revenue', 'created_at'
    ]
    list_filter = ['date', 'created_at']
    search_fields = ['date']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Snapshot Date', {
            'fields': ('date',)
        }),
        ('User Metrics', {
            'fields': ('total_users', 'new_registrations', 'active_users')
        }),
        ('Order Metrics', {
            'fields': ('total_orders', 'total_revenue', 'total_transactions')
        }),
        ('Product Metrics', {
            'fields': ('total_products',)
        }),
        ('System Performance', {
            'fields': ('platform_usage_hours', 'api_requests', 'errors_count', 'conversion_rate', 'metadata')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )


@admin.register(CustomAnalyticsReport)
class CustomAnalyticsReportAdmin(admin.ModelAdmin):
    """Admin interface for custom analytics reports"""
    
    list_display = [
        'name', 'report_type', 'is_scheduled', 'last_generated',
        'created_by'
    ]
    list_filter = ['report_type', 'is_scheduled', 'last_generated', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['last_generated', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('name', 'description', 'report_type')
        }),
        ('Configuration', {
            'fields': ('query_config', 'is_scheduled', 'schedule_frequency')
        }),
        ('Sharing', {
            'fields': ('is_public',)
        }),
        ('Execution', {
            'fields': ('last_generated',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# ======================== CONTENT SECTION ADMIN ========================

@admin.register(ContentModerationQueue)
class ContentModerationQueueAdmin(admin.ModelAdmin):
    """Admin interface for content moderation queue"""
    
    list_display = [
        'content_type', 'priority_badge', 'status_badge', 'submitted_by',
        'moderated_by', 'submitted_at'
    ]
    list_filter = ['content_type', 'priority', 'status', 'submitted_at']
    search_fields = ['content_title', 'content_preview', 'moderation_notes']
    readonly_fields = ['submitted_at', 'moderated_at']
    
    fieldsets = (
        ('Content Information', {
            'fields': ('content_type', 'content_id', 'content_title', 'content_preview')
        }),
        ('Submission Details', {
            'fields': ('submitted_by', 'priority', 'auto_flagged', 'flag_reasons')
        }),
        ('Moderation', {
            'fields': ('status', 'moderated_by', 'moderation_notes')
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'moderated_at'),
            'classes': ('collapse',)
        })
    )
    
    def priority_badge(self, obj):
        """Display priority with colored badge"""
        if obj.priority >= 8:
            color = 'darkred'
            priority = 'URGENT'
        elif obj.priority >= 6:
            color = 'red'
            priority = 'HIGH'
        elif obj.priority >= 4:
            color = 'orange'
            priority = 'MEDIUM'
        else:
            color = 'green'
            priority = 'LOW'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, priority
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'PENDING': 'orange',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'FLAGGED': 'purple',
            'SPAM': 'darkred'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ContentPolicy)
class ContentPolicyAdmin(admin.ModelAdmin):
    """Admin interface for content policies"""
    
    list_display = [
        'policy_type', 'title', 'is_active', 'created_by',
        'updated_at'
    ]
    list_filter = ['policy_type', 'is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('policy_type', 'title', 'description')
        }),
        ('Rules & Enforcement', {
            'fields': ('rules', 'auto_enforcement')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ======================== USERS SECTION ADMIN ========================

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """Admin interface for user activity logs"""
    
    list_display = [
        'user', 'activity_type', 'description', 'ip_address', 'timestamp'
    ]
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'user__email', 'activity_type', 'description']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Activity Details', {
            'fields': ('activity_type', 'description', 'details')
        }),
        ('Session Information', {
            'fields': ('ip_address', 'user_agent', 'session_id')
        }),
        ('Metadata', {
            'fields': ('timestamp',)
        })
    )


@admin.register(UserSecurityEvent)
class UserSecurityEventAdmin(admin.ModelAdmin):
    """Admin interface for user security events"""
    
    list_display = [
        'user', 'event_type', 'severity_badge', 'status_badge',
        'resolved_by', 'occurred_at'
    ]
    list_filter = ['event_type', 'severity', 'is_resolved', 'occurred_at']
    search_fields = ['user__username', 'user__email', 'description']
    readonly_fields = ['occurred_at', 'resolved_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Event Details', {
            'fields': ('event_type', 'severity', 'description', 'details')
        }),
        ('Session Information', {
            'fields': ('ip_address',)
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('occurred_at', 'resolved_at'),
            'classes': ('collapse',)
        })
    )
    
    def severity_badge(self, obj):
        """Display severity with colored badge"""
        colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        if obj.is_resolved:
            color = 'green'
            status = 'Resolved'
        else:
            color = 'red'
            status = 'Open'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    """Admin interface for admin action logs"""
    
    list_display = [
        'admin_user', 'action_type', 'target_user', 'description',
        'timestamp'
    ]
    list_filter = ['action_type', 'timestamp']
    search_fields = [
        'admin_user__username', 'admin_user__email', 'action_type',
        'target_user__username', 'target_user__email', 'description'
    ]
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Admin Information', {
            'fields': ('admin_user',)
        }),
        ('Action Details', {
            'fields': ('action_type', 'description', 'details')
        }),
        ('Target Information', {
            'fields': ('target_user',)
        }),
        ('Session Information', {
            'fields': ('ip_address',)
        }),
        ('Metadata', {
            'fields': ('timestamp',)
        })
    )
