"""
Admin interface for AI models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    AIConversation, CropAdvisory, DiseaseDetection, 
    MarketIntelligence, AIUsageAnalytics, AIFeedback
)


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    """Admin interface for AI conversations"""
    list_display = [
        'id', 'user_link', 'conversation_type', 'language', 'created_at'
    ]
    list_filter = [
        'conversation_type', 'language', 'created_at', 'updated_at'
    ]
    search_fields = ['user__username', 'user__email', 'last_message']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'conversation_type', 'language')
        }),
        ('Conversation Details', {
            'fields': ('last_message', 'context')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'


@admin.register(CropAdvisory)
class CropAdvisoryAdmin(admin.ModelAdmin):
    """Admin interface for crop advisories"""
    list_display = [
        'id', 'user_link', 'crop_type', 'farming_stage', 'location', 'created_at'
    ]
    list_filter = [
        'crop_type', 'farming_stage', 'location', 'created_at'
    ]
    search_fields = [
        'user__username', 'crop_type', 'location', 'question', 'advice'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'crop_type', 'farming_stage', 'location', 'season')
        }),
        ('Question & Advice', {
            'fields': ('question', 'advice')
        }),
        ('Metadata', {
            'fields': ('context', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'


@admin.register(DiseaseDetection)
class DiseaseDetectionAdmin(admin.ModelAdmin):
    """Admin interface for disease detection"""
    list_display = [
        'id', 'user_link', 'crop_type', 'location', 'created_at'
    ]
    list_filter = [
        'crop_type', 'location', 'created_at'
    ]
    search_fields = [
        'user__username', 'crop_type', 'symptoms', 'diagnosis'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Detection Request', {
            'fields': ('user', 'crop_type', 'symptoms', 'image_url', 'location')
        }),
        ('Diagnosis', {
            'fields': ('diagnosis', 'treatment_plan')
        }),
        ('Metadata', {
            'fields': ('context', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    ]
    search_fields = [
        'user__username', 'crop_type', 'symptoms', 'diagnosis'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Detection Request', {
            'fields': ('user', 'crop_type', 'symptoms', 'image_url', 'location')
        }),
        ('Diagnosis', {
            'fields': ('diagnosis', 'treatment_plan', 'confidence_score')
        }),
        ('Treatment Progress', {
            'fields': ('treatment_status', 'outcome')
        }),
        ('Metadata', {
            'fields': ('context', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def symptoms_short(self, obj):
        """Show shortened symptoms"""
        return obj.symptoms[:50] + '...' if len(obj.symptoms) > 50 else obj.symptoms
    symptoms_short.short_description = 'Symptoms'


@admin.register(MarketIntelligence)
class MarketIntelligenceAdmin(admin.ModelAdmin):
    """Admin interface for market intelligence"""
    list_display = [
        'id', 'user_link', 'crop_type', 'location', 'market_type', 'created_at'
    ]
    list_filter = [
        'crop_type', 'market_type', 'location', 'created_at'
    ]
    search_fields = [
        'user__username', 'crop_type', 'location', 'analysis'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'crop_type', 'location', 'market_type')
        }),
        ('Intelligence', {
            'fields': ('price_prediction', 'analysis')
        }),
        ('Validity', {
            'fields': ('validity_period',)
        }),
        ('Metadata', {
            'fields': ('context', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'


@admin.register(AIUsageAnalytics)
class AIUsageAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for AI usage analytics"""
    list_display = [
        'id', 'user_link', 'service_type', 'tokens_used', 'success', 'created_at'
    ]
    list_filter = [
        'service_type', 'success', 'created_at'
    ]
    search_fields = ['user__username', 'service_type']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('user', 'service_type', 'tokens_used', 'response_time')
        }),
        ('Request/Response', {
            'fields': ('request_data', 'response_data', 'success')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    """Admin interface for AI feedback"""
    list_display = [
        'id', 'user_link', 'service_type', 'rating', 'created_at'
    ]
    list_filter = [
        'service_type', 'rating', 'created_at'
    ]
    search_fields = [
        'user__username', 'service_type', 'feedback_text'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'service_type', 'service_id', 'rating')
        }),
        ('Feedback Content', {
            'fields': ('feedback_text',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'service_type', 'service_id', 'rating')
        }),
        ('Feedback Text', {
            'fields': ('feedback_text',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def feedback_short(self, obj):
        """Show shortened feedback"""
        return obj.feedback_text[:50] + '...' if len(obj.feedback_text) > 50 else obj.feedback_text
    feedback_short.short_description = 'Feedback'


# Custom admin site configuration
admin.site.site_header = "AgriConnect AI Administration"
admin.site.site_title = "AgriConnect AI Admin"
admin.site.index_title = "Welcome to AgriConnect AI Administration"
