"""
AgriConnect Enhanced Admin Configuration
Comprehensive admin interface for user management and profile models
Enables administrators to create accounts for end users who cannot self-register
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django.forms import widgets
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Import models
from .models import (
    ExtendedUserProfile,
    FarmerProfile,
    ConsumerProfile,
    InstitutionProfile,
    AgentProfile,
    FinancialPartnerProfile,
    GovernmentOfficialProfile
)
from authentication.models import UserRole

User = get_user_model()

# Unregister the default User admin to avoid conflicts
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


# ======================== CUSTOM FORMS ========================

class AdminUserCreationForm(UserCreationForm):
    """Custom user creation form for admin interface"""
    identifier = forms.CharField(
        max_length=150,
        help_text="Email address or phone number (international format: +233...)"
    )
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    roles = forms.ModelMultipleChoiceField(
        queryset=UserRole.objects.all(),
        required=True,
        help_text="Select user roles",
        widget=widgets.CheckboxSelectMultiple
    )
    country = forms.CharField(max_length=100, initial='Ghana')
    region = forms.CharField(max_length=100, required=False)
    language = forms.ChoiceField(
        choices=[
            ('en', 'English'),
            ('fr', 'French'),
            ('tw', 'Twi'),
            ('ee', 'Ewe'),
            ('ha', 'Hausa'),
            ('yo', 'Yoruba'),
            ('sw', 'Swahili'),
        ],
        initial='en'
    )
    is_verified = forms.BooleanField(
        initial=True,
        required=False,
        help_text="Check to mark account as verified (skips OTP verification)"
    )

    class Meta:
        model = User
        fields = ('identifier', 'first_name', 'last_name', 'roles', 'country', 'region', 'language')

    def clean_identifier(self):
        identifier = self.cleaned_data['identifier']
        if '@' in identifier:
            # Email validation
            if User.objects.filter(email=identifier).exists():
                raise ValidationError("A user with this email already exists.")
        else:
            # Phone number validation
            import re
            if not re.match(r'^\+?[1-9]\d{1,14}$', identifier):
                raise ValidationError("Please enter a valid phone number in international format (+233...)")
            if User.objects.filter(phone_number=identifier).exists():
                raise ValidationError("A user with this phone number already exists.")
        return identifier

    def save(self, commit=True):
        user = super().save(commit=False)
        identifier = self.cleaned_data['identifier']
        
        # Set email or phone based on identifier
        if '@' in identifier:
            user.email = identifier
            user.username = identifier
            user.email_verified = self.cleaned_data.get('is_verified', False)
        else:
            user.phone_number = identifier
            user.username = identifier
            user.phone_verified = self.cleaned_data.get('is_verified', False)
        
        user.is_verified = self.cleaned_data.get('is_verified', False)
        user.country = self.cleaned_data['country']
        user.region = self.cleaned_data.get('region', '')
        user.language = self.cleaned_data['language']
        
        if commit:
            user.save()
            # Add roles
            user.roles.set(self.cleaned_data['roles'])
        return user


class AdminUserChangeForm(UserChangeForm):
    """Custom user change form for admin interface"""
    
    class Meta:
        model = User
        fields = '__all__'


# ======================== CUSTOM FILTERS ========================

class UserTypeFilter(SimpleListFilter):
    """Filter users by their primary role"""
    title = 'User Type'
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        return [
            ('FARMER', 'Farmer'),
            ('PROCESSOR', 'Processor'), 
            ('CONSUMER', 'Consumer'),
            ('INSTITUTION', 'Institution'),
            ('WAREHOUSE_MANAGER', 'Warehouse Manager'),
            ('QUALITY_INSPECTOR', 'Quality Inspector'),
            ('AGENT', 'Sales Agent'),
            ('FINANCIAL_PARTNER', 'Financial Partner'),
            ('GOVERNMENT_OFFICIAL', 'Government Official'),
            ('ADMIN', 'Administrator'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(roles__name=self.value())
        return queryset


class VerificationStatusFilter(SimpleListFilter):
    """Filter users by verification status"""
    title = 'Verification Status'
    parameter_name = 'verification'

    def lookups(self, request, model_admin):
        return [
            ('verified', 'Verified'),
            ('unverified', 'Unverified'),
            ('email_verified', 'Email Verified'),
            ('phone_verified', 'Phone Verified'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'verified':
            return queryset.filter(is_verified=True)
        elif self.value() == 'unverified':
            return queryset.filter(is_verified=False)
        elif self.value() == 'email_verified':
            return queryset.filter(email_verified=True)
        elif self.value() == 'phone_verified':
            return queryset.filter(phone_verified=True)
        return queryset


# ======================== ENHANCED USER ADMIN ========================

@admin.register(User)
class EnhancedUserAdmin(BaseUserAdmin):
    """Enhanced User admin with comprehensive user management features"""
    
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    
    # Display configuration
    list_display = (
        'username', 'get_full_name', 'get_contact_info', 'get_user_roles',
        'get_verification_status', 'is_active', 'date_joined', 'last_login'
    )
    list_filter = (
        UserTypeFilter, VerificationStatusFilter, 'is_active', 'is_staff', 
        'is_superuser', 'date_joined', 'country', 'language'
    )
    search_fields = (
        'username', 'email', 'phone_number', 'first_name', 'last_name'
    )
    ordering = ('-date_joined',)
    
    # Fieldsets for detailed view
    fieldsets = (
        ('Authentication Info', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'email_verified', 'phone_verified')
        }),        ('Location & Preferences', {
            'fields': ('country', 'region', 'language')
        }),
        ('Business Info', {
            'fields': ('business_name', 'business_registration_number', 'tax_identification_number'),
            'classes': ('collapse',)
        }),
        ('Roles & Permissions', {
            'fields': ('roles', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Security & Tracking', {
            'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    # Fieldsets for add user form
    add_fieldsets = (
        ('Create User Account', {
            'classes': ('wide',),
            'fields': (
                'identifier', 'password1', 'password2', 'first_name', 'last_name',
                'roles', 'country', 'region', 'language', 'is_verified'
            ),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'username')
    filter_horizontal = ('roles', 'groups', 'user_permissions')
    
    # Custom display methods
    def get_full_name(self, obj):
        """Display user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    get_full_name.short_description = 'Full Name'
    
    def get_contact_info(self, obj):
        """Display primary contact method"""
        if obj.email:
            icon = '📧' if obj.email_verified else '📧❓'
            return format_html(f'{icon} {obj.email}')
        elif obj.phone_number:
            icon = '📱' if obj.phone_verified else '📱❓'
            return format_html(f'{icon} {obj.phone_number}')
        return '❌ No contact info'
    get_contact_info.short_description = 'Contact Info'
    
    def get_user_roles(self, obj):
        """Display user roles as colored badges"""
        roles = obj.roles.all()
        if not roles:
            return '❌ No roles'
        
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
        
        badges = []
        for role in roles[:3]:  # Limit to 3 roles for display
            color = role_colors.get(role.name, '#6c757d')
            badges.append(f'<span style="background: {color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin: 1px;">{role.name}</span>')
        
        if roles.count() > 3:
            badges.append(f'<span style="color: #6c757d;">+{roles.count() - 3} more</span>')
        
        return format_html(' '.join(badges))
    get_user_roles.short_description = 'Roles'
    
    def get_verification_status(self, obj):
        """Display verification status with icons"""
        if obj.is_verified:
            return format_html('<span style="color: green;">✅ Verified</span>')
        else:
            status = []
            if obj.email_verified:
                status.append('📧✅')
            if obj.phone_verified:
                status.append('📱✅')
            if not status:
                return format_html('<span style="color: red;">❌ Unverified</span>')
            return format_html(' '.join(status))
    get_verification_status.short_description = 'Verification'
    
    # Custom actions
    actions = ['verify_users', 'deactivate_users', 'send_verification_email']
    
    def verify_users(self, request, queryset):
        """Mark selected users as verified"""
        updated = queryset.update(is_verified=True, email_verified=True, phone_verified=True)
        self.message_user(request, f'{updated} users were successfully verified.')
    verify_users.short_description = "Mark selected users as verified"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def send_verification_email(self, request, queryset):
        """Send verification email to selected users"""
        count = 0
        for user in queryset:
            if user.email and not user.email_verified:
                # TODO: Implement email sending logic
                count += 1
        self.message_user(request, f'Verification emails sent to {count} users.')
    send_verification_email.short_description = "Send verification emails"


# ======================== PROFILE ADMIN CLASSES ========================

@admin.register(ExtendedUserProfile)
class ExtendedUserProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for extended user profiles"""
    
    list_display = ('user', 'get_user_contact', 'gender', 'city', 'newsletter_subscription', 'created_at')
    list_filter = ('gender', 'newsletter_subscription', 'created_at', 'user__is_verified')
    search_fields = (
        'user__username', 'user__email', 'user__first_name', 'user__last_name', 
        'city', 'address'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('gender', 'date_of_birth', 'bio')
        }),
        ('Location', {
            'fields': ('address', 'city', 'postal_code', 'latitude', 'longitude')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscription', 'marketing_consent', 'data_processing_consent')
        }),
        ('Media', {
            'fields': ('profile_picture', 'cover_photo'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_contact(self, obj):
        """Display user contact information"""
        if obj.user.email:
            return f"📧 {obj.user.email}"
        elif obj.user.phone_number:
            return f"📱 {obj.user.phone_number}"
        return "❌ No contact"
    get_user_contact.short_description = 'Contact'


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for farmer profiles"""
    
    list_display = (
        'user', 'farm_name', 'farm_size', 'organic_certified', 
        'years_of_experience', 'farm_type', 'get_verification_status'
    )
    list_filter = (
        'organic_certified', 'farm_type', 'created_at', 
        'user__is_verified'
    )
    search_fields = (
        'user__username', 'user__email', 'farm_name', 
        'user__first_name', 'user__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Farmer Information', {
            'fields': ('user',)
        }),
        ('Farm Details', {
            'fields': (
                'farm_name', 'farm_size', 'farm_type', 
                'years_of_experience', 'farming_methods'
            )
        }),
        ('Location & Contact', {
            'fields': ('farm_location', 'farm_address')
        }),
        ('Certifications', {
            'fields': ('organic_certified', 'certifications')
        }),
        ('Production', {
            'fields': ('main_crops', 'secondary_crops', 'livestock'),
            'classes': ('collapse',)
        }),
        ('Equipment & Technology', {
            'fields': ('equipment_owned', 'technology_adoption_level'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_verification_status(self, obj):
        """Display verification status"""
        if obj.user.is_verified:
            return format_html('<span style="color: green;">✅ Verified</span>')
        return format_html('<span style="color: red;">❌ Unverified</span>')
    get_verification_status.short_description = 'Status'


@admin.register(ConsumerProfile)
class ConsumerProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for consumer profiles"""
    
    list_display = (
        'user', 'budget_range', 'delivery_address', 'get_preferences', 'created_at'
    )
    list_filter = ('budget_range', 'created_at', 'user__is_verified')
    search_fields = (
        'user__username', 'user__email', 'user__first_name', 
        'user__last_name', 'delivery_address'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Consumer Information', {
            'fields': ('user',)
        }),
        ('Shopping Preferences', {
            'fields': ('budget_range', 'preferred_categories', 'dietary_preferences')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_instructions')
        }),
        ('Additional Preferences', {
            'fields': ('organic_preference', 'local_preference'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_preferences(self, obj):
        """Display key preferences"""
        prefs = []
        if obj.organic_preference:
            prefs.append('🌱 Organic')
        if obj.local_preference:
            prefs.append('📍 Local')
        return ' '.join(prefs) if prefs else '➖'
    get_preferences.short_description = 'Preferences'


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for institution profiles"""
    
    list_display = (
        'organization_name', 'organization_type', 'user', 
        'annual_volume', 'get_verification', 'created_at'
    )
    list_filter = ('organization_type', 'created_at', 'user__is_verified')
    search_fields = (
        'organization_name', 'tax_id', 'user__username', 
        'user__email', 'contact_person'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Institution Information', {
            'fields': ('user', 'organization_name', 'organization_type')
        }),
        ('Business Details', {
            'fields': ('tax_id', 'registration_number', 'annual_volume')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'business_address', 'business_phone')
        }),
        ('Requirements', {
            'fields': ('procurement_requirements', 'quality_standards'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_verification(self, obj):
        """Display verification status"""
        if obj.user.is_verified:
            return format_html('<span style="color: green;">✅ Verified</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    get_verification.short_description = 'Status'


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for agent profiles"""
    
    list_display = (
        'user', 'employee_id', 'agent_type', 'performance_rating', 
        'farmers_registered', 'is_active', 'hire_date'
    )
    list_filter = (
        'agent_type', 'is_active', 'hire_date', 'created_at',
        'performance_rating', 'user__is_verified'
    )
    search_fields = (
        'user__username', 'user__email', 'employee_id', 
        'user__first_name', 'user__last_name'
    )
    readonly_fields = ('created_at', 'updated_at', 'employee_id')
    
    fieldsets = (
        ('Agent Information', {
            'fields': ('user', 'employee_id', 'agent_type')
        }),
        ('Employment Details', {
            'fields': ('hire_date', 'is_active', 'supervisor')
        }),
        ('Performance', {
            'fields': ('performance_rating', 'farmers_registered', 'sales_target')
        }),
        ('Territory & Responsibilities', {
            'fields': ('assigned_territory', 'responsibilities'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-generate employee ID if not provided"""
        if not obj.employee_id:
            # Generate employee ID based on agent type and user ID
            prefix = obj.agent_type[:2].upper() if obj.agent_type else 'AG'
            obj.employee_id = f"{prefix}{obj.user.id:06d}"
        super().save_model(request, obj, form, change)


@admin.register(FinancialPartnerProfile)
class FinancialPartnerProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for financial partner profiles"""
    
    list_display = (
        'institution_name', 'institution_type', 'integration_status', 
        'is_verified', 'user', 'created_at'
    )
    list_filter = (
        'institution_type', 'integration_status', 'is_verified', 
        'created_at', 'user__is_verified'
    )
    search_fields = (
        'institution_name', 'registration_number', 'user__username', 
        'user__email', 'contact_person'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Financial Partner Information', {
            'fields': ('user', 'institution_name', 'institution_type')
        }),
        ('Business Registration', {
            'fields': ('registration_number', 'license_number', 'is_verified')
        }),
        ('Integration Details', {
            'fields': ('integration_status', 'api_endpoints', 'supported_services')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'business_address', 'business_phone')
        }),
        ('Compliance & Documentation', {
            'fields': ('compliance_documents', 'terms_and_conditions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GovernmentOfficialProfile)
class GovernmentOfficialProfileAdmin(admin.ModelAdmin):
    """Enhanced admin for government official profiles"""
    
    list_display = (
        'user', 'official_title', 'department', 'position_level', 
        'jurisdiction_level', 'employment_status', 'created_at'
    )
    list_filter = (
        'position_level', 'jurisdiction_level', 'employment_status', 
        'ministry', 'created_at', 'user__is_verified'
    )
    search_fields = (
        'user__username', 'user__email', 'official_title', 
        'department', 'employee_id', 'user__first_name', 'user__last_name'
    )
    readonly_fields = ('created_at', 'updated_at', 'employee_id')
    
    fieldsets = (
        ('Official Information', {
            'fields': ('user', 'employee_id', 'official_title')
        }),
        ('Department & Ministry', {
            'fields': ('department', 'ministry', 'position_level')
        }),
        ('Jurisdiction & Status', {
            'fields': ('jurisdiction_level', 'employment_status')
        }),
        ('Responsibilities', {
            'fields': ('area_of_responsibility', 'authority_level'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('office_address', 'office_phone'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-generate employee ID if not provided"""
        if not obj.employee_id:
            # Generate employee ID for government officials
            obj.employee_id = f"GOV{obj.user.id:06d}"
        super().save_model(request, obj, form, change)


# ======================== ADMIN SITE CUSTOMIZATION ========================

# Customize admin site headers
admin.site.site_header = "AgriConnect Administration"
admin.site.site_title = "AgriConnect Admin"
admin.site.index_title = "Welcome to AgriConnect Administration Portal"