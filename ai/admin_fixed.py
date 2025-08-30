"""
Django Admin Configuration for AI Models
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
    list_display = ['id', 'user_link', 'conversation_type', 'language', 'created_at']
    list_filter = ['conversation_type', 'language', 'created_at']
    search_fields = ['user__username', 'user__email', 'last_message']
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CropAdvisory)
class CropAdvisoryAdmin(admin.ModelAdmin):
    """Admin interface for crop advisories"""
    list_display = ['id', 'user_link', 'crop_type', 'farming_stage', 'location', 'created_at']
    list_filter = ['crop_type', 'farming_stage', 'location', 'created_at']
    search_fields = ['user__username', 'crop_type', 'location', 'question']
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(DiseaseDetection)
class DiseaseDetectionAdmin(admin.ModelAdmin):
    """Admin interface for disease detection"""
    list_display = ['id', 'user_link', 'crop_type', 'location', 'created_at']
    list_filter = ['crop_type', 'location', 'created_at']
    search_fields = ['user__username', 'crop_type', 'symptoms', 'diagnosis']
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(MarketIntelligence)
class MarketIntelligenceAdmin(admin.ModelAdmin):
    """Admin interface for market intelligence"""
    list_display = ['id', 'user_link', 'crop_type', 'location', 'market_type', 'created_at']
    list_filter = ['crop_type', 'market_type', 'location', 'created_at']
    search_fields = ['user__username', 'crop_type', 'location', 'analysis']
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AIUsageAnalytics)
class AIUsageAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for AI usage analytics"""
    list_display = ['id', 'user_link', 'service_type', 'tokens_used', 'success', 'created_at']
    list_filter = ['service_type', 'success', 'created_at']
    search_fields = ['user__username', 'service_type']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    """Admin interface for AI feedback"""
    list_display = ['id', 'user_link', 'service_type', 'rating', 'created_at']
    list_filter = ['service_type', 'rating', 'created_at']
    search_fields = ['user__username', 'service_type', 'feedback_text']
    readonly_fields = ['id', 'created_at']
    
    def user_link(self, obj):
        """Create clickable link to user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
