"""
AgriConnect User Profiles Admin Interface
Admin configuration for all user profile types
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model

# Import User model from authentication app
User = get_user_model()

# Admin configurations will be added after migrations are complete
# All admin registrations are temporarily commented out to resolve import conflicts
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles"""
    list_display = ['user', 'bio_short', 'gender', 'created_at']
    list_filter = ['gender', 'newsletter_subscription', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    
    def bio_short(self, obj):
        return obj.bio[:50] + "..." if obj.bio and len(obj.bio) > 50 else obj.bio or "-"
    bio_short.short_description = "Bio"


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    """Admin interface for farmer profiles"""
    list_display = [
        'user', 'farm_name', 'farm_size', 'organic_certified', 
        'years_of_experience', 'production_capacity'
    ]
    list_filter = ['organic_certified', 'farm_type', 'created_at']
    search_fields = ['user__username', 'farm_name', 'primary_crops']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'farm_name', 'farm_size', 'farm_type')
        }),
        ('Certifications', {
            'fields': ('organic_certified', 'certifications', 'certification_files')
        }),
        ('Experience & Capacity', {
            'fields': ('years_of_experience', 'production_capacity', 'primary_crops')
        }),
        ('Location', {
            'fields': ('geo_location',)
        })
    )


@admin.register(ConsumerProfile)
class ConsumerProfileAdmin(admin.ModelAdmin):
    """Admin interface for consumer profiles"""
    list_display = ['user', 'budget_range', 'delivery_address', 'created_at']
    list_filter = ['budget_range', 'created_at']
    search_fields = ['user__username', 'delivery_address']


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(admin.ModelAdmin):
    """Admin interface for institution profiles"""
    list_display = [
        'organization_name', 'user', 'organization_type', 
        'annual_volume', 'created_at'
    ]
    list_filter = ['organization_type', 'created_at']
    search_fields = ['organization_name', 'user__username', 'tax_id']


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    """Admin interface for agent profiles"""
    list_display = [
        'user', 'employee_id', 'agent_type', 'performance_rating',
        'farmers_registered', 'is_active', 'hire_date'
    ]
    list_filter = ['agent_type', 'is_active', 'hire_date', 'assigned_regions']
    search_fields = ['user__username', 'employee_id', 'assigned_regions']
    readonly_fields = ['employee_id', 'farmers_registered', 'total_sales_volume']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'employee_id', 'agent_type', 'supervisor')
        }),
        ('Territory & Targets', {
            'fields': ('assigned_regions', 'territory_size_km', 'target_farmers')
        }),
        ('Performance', {
            'fields': (
                'farmers_registered', 'total_sales_volume', 'commission_rate',
                'performance_rating'
            )
        }),
        ('Professional Details', {
            'fields': (
                'training_certifications', 'languages_spoken', 'vehicle_type'
            ),
            'classes': ('collapse',)
        }),
        ('Employment', {
            'fields': ('hire_date', 'is_active', 'last_field_visit')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'supervisor')


@admin.register(FinancialPartnerProfile)
class FinancialPartnerProfileAdmin(admin.ModelAdmin):
    """Admin interface for financial partner profiles"""
    list_display = [
        'institution_name', 'user', 'institution_type', 'integration_status',
        'success_rate', 'is_verified', 'partnership_start_date'
    ]
    list_filter = [
        'institution_type', 'integration_status', 'is_verified',
        'partnership_start_date'
    ]
    search_fields = [
        'institution_name', 'user__username', 'registration_number'
    ]
    readonly_fields = [
        'total_transactions_processed', 'total_volume_processed',
        'success_rate', 'average_processing_time'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'institution_name', 'institution_type')
        }),
        ('Registration & Compliance', {
            'fields': (
                'registration_number', 'central_bank_license', 
                'regulatory_authority'
            )
        }),
        ('Services & Limits', {
            'fields': (
                'services_offered', 'supported_currencies',
                'minimum_transaction', 'maximum_transaction',
                'transaction_fee_percentage'
            )
        }),
        ('Geographic Coverage', {
            'fields': ('countries_served', 'regions_served', 'branch_locations'),
            'classes': ('collapse',)
        }),
        ('API Integration', {
            'fields': (
                'api_endpoint', 'webhook_url', 'api_key_active',
                'integration_status'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'total_transactions_processed', 'total_volume_processed',
                'success_rate', 'average_processing_time'
            ),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': (
                'primary_contact_name', 'primary_contact_email',
                'primary_contact_phone', 'technical_support_email'
            ),
            'classes': ('collapse',)
        }),
        ('Partnership Status', {
            'fields': ('is_verified', 'verified_at', 'partnership_start_date')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(GovernmentOfficialProfile)
class GovernmentOfficialProfileAdmin(admin.ModelAdmin):
    """Admin interface for government official profiles"""
    list_display = [
        'user', 'employee_id', 'official_title', 'department',
        'position_level', 'jurisdiction_level', 'employment_status'
    ]
    list_filter = [
        'position_level', 'jurisdiction_level', 'employment_status',
        'ministry', 'appointment_date'
    ]
    search_fields = [
        'user__username', 'employee_id', 'official_title', 
        'department', 'ministry'
    ]
    readonly_fields = [
        'employee_id', 'farmers_supervised', 'inspections_conducted',
        'policies_implemented'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'employee_id', 'official_title', 'department', 'ministry')
        }),
        ('Position & Authority', {
            'fields': ('position_level', 'jurisdiction_level', 'superior_officer')
        }),
        ('Jurisdiction & Responsibilities', {
            'fields': (
                'assigned_regions', 'policy_areas', 'agricultural_specializations'
            )
        }),
        ('Authority & Permissions', {
            'fields': (
                'can_approve_certifications', 'can_issue_permits',
                'can_conduct_inspections', 'can_authorize_subsidies',
                'approval_limit_amount'
            ),
            'classes': ('collapse',)
        }),
        ('Contact & Office', {
            'fields': (
                'office_address', 'office_phone', 'office_email'
            ),
            'classes': ('collapse',)
        }),
        ('Professional Details', {
            'fields': (
                'certifications_held', 'years_in_service', 'security_clearance'
            ),
            'classes': ('collapse',)
        }),
        ('Performance & Activity', {
            'fields': (
                'farmers_supervised', 'inspections_conducted',
                'policies_implemented', 'last_field_activity'
            ),
            'classes': ('collapse',)
        }),
        ('Employment Status', {
            'fields': ('employment_status', 'appointment_date')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'superior_officer')


# Admin site customization
admin.site.site_header = "AgriConnect User Management"
admin.site.site_title = "AgriConnect Users"
admin.site.index_title = "User Administration Dashboard"