"""
AgriConnect Communications Admin
Enhanced SMS & OTP Integration System (PRD Section 4.7)
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SMSProvider, SMSTemplate, SMSMessage, OTPCode,
    CommunicationPreference, CommunicationLog
)

@admin.register(SMSProvider)
class SMSProviderAdmin(admin.ModelAdmin):
    """Admin for SMS providers"""
    list_display = ['name', 'status_badge', 'cost_per_sms', 'priority', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">Active</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">Inactive</span>')
    status_badge.short_description = 'Status'

@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    """Admin for SMS templates"""
    list_display = ['name', 'template_type', 'language', 'is_active', 'created_at']
    list_filter = ['template_type', 'language', 'is_active', 'created_at']
    search_fields = ['name', 'content']
    readonly_fields = ['character_count', 'created_at', 'updated_at']

@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    """Admin for SMS messages"""
    list_display = ['recipient_phone', 'status', 'cost', 'sent_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['recipient_phone', 'content']
    readonly_fields = ['sent_at', 'delivered_at']
    date_hierarchy = 'sent_at'

@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """Admin for OTP codes"""
    list_display = ['phone_number', 'purpose', 'is_used', 'expires_at', 'created_at']
    list_filter = ['purpose', 'is_used', 'created_at']
    search_fields = ['phone_number', 'email']
    readonly_fields = ['code', 'used_at', 'created_at']
    date_hierarchy = 'created_at'

@admin.register(CommunicationPreference)
class CommunicationPreferenceAdmin(admin.ModelAdmin):
    """Admin for communication preferences"""
    list_display = ['user', 'preferred_language', 'sms_enabled', 'email_enabled', 'updated_at']
    list_filter = ['preferred_language', 'sms_enabled', 'email_enabled', 'created_at']
    search_fields = ['user__username']

@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    """Admin for communication logs"""
    list_display = ['recipient', 'communication_type', 'purpose', 'status', 'sent_at']
    list_filter = ['communication_type', 'status', 'sent_at']
    search_fields = ['recipient']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'
