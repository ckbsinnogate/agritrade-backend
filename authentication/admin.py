"""
AgriConnect Authentication Admin Configuration
Admin interface for authentication models including User roles and OTP management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import UserRole, OTPCode

# Unregister the default Group admin to customize it
admin.site.unregister(Group)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for user roles"""
    
    list_display = ('name', 'get_role_display', 'get_user_count', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description')
        }),
    )
    
    def get_role_display(self, obj):
        """Display role with colored badge"""
        role_colors = {
            'FARMER': '#28a745',
            'PROCESSOR': '#17a2b8',
            'CONSUMER': '#ffc107',
            'INSTITUTION': '#6f42c1',
            'WAREHOUSE_MANAGER': '#fd7e14',
            'QUALITY_INSPECTOR': '#20c997',
            'AGENT': '#6c757d',
            'FINANCIAL_PARTNER': '#dc3545',
            'GOVERNMENT_OFFICIAL': '#007bff',
            'ADMIN': '#343a40',
        }
        
        color = role_colors.get(obj.name, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color, obj.get_name_display()
        )
    get_role_display.short_description = 'Role Badge'
    
    def get_user_count(self, obj):
        """Display number of users with this role"""
        count = obj.users.count()
        if count > 0:
            return format_html('<strong>{}</strong> users', count)
        return '0 users'
    get_user_count.short_description = 'User Count'


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """Admin interface for OTP codes"""
    
    list_display = (
        'user', 'get_contact_method', 'code', 'purpose', 
        'get_status', 'created_at', 'expires_at'
    )
    list_filter = ('purpose', 'is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'user__phone_number', 'code')
    readonly_fields = ('created_at', 'used_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('user', 'code', 'purpose')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone_number')
        }),
        ('Status & Timing', {
            'fields': ('is_used', 'used_at', 'created_at', 'expires_at')
        }),
    )
    
    def get_contact_method(self, obj):
        """Display contact method used for OTP"""
        if obj.email:
            return format_html('📧 {}', obj.email)
        elif obj.phone_number:
            return format_html('📱 {}', obj.phone_number)
        return '❌ No contact'
    get_contact_method.short_description = 'Contact Method'
    
    def get_status(self, obj):
        """Display OTP status with visual indicators"""
        from django.utils import timezone
        
        if obj.is_used:
            return format_html('<span style="color: green;">✅ Used</span>')
        elif obj.expires_at < timezone.now():
            return format_html('<span style="color: red;">❌ Expired</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    get_status.short_description = 'Status'
    
    # Custom actions
    actions = ['mark_as_expired', 'resend_otp']
    
    def mark_as_expired(self, request, queryset):
        """Mark selected OTP codes as expired"""
        from django.utils import timezone
        updated = queryset.update(expires_at=timezone.now())
        self.message_user(request, f'{updated} OTP codes were marked as expired.')
    mark_as_expired.short_description = "Mark selected OTP codes as expired"
    
    def resend_otp(self, request, queryset):
        """Resend OTP codes (placeholder for actual implementation)"""
        count = queryset.filter(is_used=False).count()
        self.message_user(request, f'{count} OTP codes would be resent (implementation needed).')
    resend_otp.short_description = "Resend OTP codes"


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    """Enhanced Group admin with better display"""
    
    list_display = ('name', 'get_permission_count', 'get_user_count')
    
    def get_permission_count(self, obj):
        """Display number of permissions"""
        count = obj.permissions.count()
        return format_html('<strong>{}</strong> permissions', count)
    get_permission_count.short_description = 'Permissions'
    
    def get_user_count(self, obj):
        """Display number of users in group"""
        count = obj.user_set.count()
        return format_html('<strong>{}</strong> users', count)
    get_user_count.short_description = 'Users'
