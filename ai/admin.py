"""
Django Admin Configuration for AI Models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    AIConversation, CropAdvisory, DiseaseDetection, 
    MarketIntelligence, AIUsageAnalytics, AIFeedback
)


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    """Admin interface for AI conversations"""
    list_display = ['id', 'user_link', 'conversation_type', 'language', 'created_at']
    list_filter = ['conversation_type', 'language', 'created_at']
    search_fields = ['user__username', 'user__email', 'farmer_question']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
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
    list_display = ['id', 'user_link', 'farmer_location', 'target_season', 'created_at']
    list_filter = ['target_season', 'region', 'created_at']
    search_fields = ['conversation__user__username', 'farmer_location', 'region']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.conversation and obj.conversation.user:
            url = reverse('admin:auth_user_change', args=[obj.conversation.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.conversation.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'conversation__user__username'


@admin.register(DiseaseDetection)
class DiseaseDetectionAdmin(admin.ModelAdmin):
    """Admin interface for disease detection"""
    list_display = ['id', 'user_link', 'crop_type', 'primary_diagnosis', 'created_at']
    list_filter = ['crop_type', 'severity_level', 'created_at']
    search_fields = ['conversation__user__username', 'crop_type', 'farmer_description', 'primary_diagnosis']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.conversation and obj.conversation.user:
            url = reverse('admin:auth_user_change', args=[obj.conversation.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.conversation.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'conversation__user__username'


@admin.register(MarketIntelligence)
class MarketIntelligenceAdmin(admin.ModelAdmin):
    """Admin interface for market intelligence"""
    list_display = ['id', 'user_link', 'crop_name', 'target_region', 'created_at']
    list_filter = ['crop_name', 'target_region', 'created_at']
    search_fields = ['conversation__user__username', 'crop_name', 'target_region']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.conversation and obj.conversation.user:
            url = reverse('admin:auth_user_change', args=[obj.conversation.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.conversation.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'conversation__user__username'


@admin.register(AIUsageAnalytics)
class AIUsageAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for AI usage analytics"""
    list_display = ['id', 'user_link', 'daily_queries', 'total_tokens_used', 'date']
    list_filter = ['date']
    search_fields = ['user__username']
    readonly_fields = ['id', 'date']
    date_hierarchy = 'date'
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'


@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    """Admin interface for AI feedback"""
    list_display = ['id', 'user_link', 'feedback_type', 'rating', 'created_at']
    list_filter = ['feedback_type', 'rating', 'created_at']
    search_fields = ['conversation__user__username', 'feedback_type', 'comments']
    readonly_fields = ['id', 'created_at']
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.conversation and obj.conversation.user:
            url = reverse('admin:auth_user_change', args=[obj.conversation.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.conversation.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'conversation__user__username'