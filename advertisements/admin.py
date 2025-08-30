"""
Advertisement & Marketing System Admin
Django admin interface for advertising platform
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Advertisement, AdvertisementPlacement, AdvertisementPlacementAssignment,
    AdvertisementPerformanceLog, AdvertisementCampaign, AdvertisementAnalytics
)

@admin.register(AdvertisementPlacement)
class AdvertisementPlacementAdmin(admin.ModelAdmin):
    """Admin interface for advertisement placements"""
    
    list_display = [
        'name', 'location', 'dimensions', 'price_per_impression', 
        'price_per_click', 'is_active', 'created_at'
    ]
    list_filter = ['location', 'is_active', 'created_at']
    search_fields = ['name', 'location']
    ordering = ['location', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'dimensions', 'max_file_size_mb')
        }),
        ('Pricing', {
            'fields': ('price_per_impression', 'price_per_click')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )

class AdvertisementPlacementAssignmentInline(admin.TabularInline):
    """Inline for advertisement placement assignments"""
    model = AdvertisementPlacementAssignment
    extra = 1
    fields = ['placement', 'priority', 'max_impressions']

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Admin interface for advertisements"""
    
    list_display = [
        'title', 'advertiser_name', 'ad_type', 'status', 'budget',
        'impressions', 'clicks', 'ctr_display', 'amount_spent', 'is_active_status'
    ]
    list_filter = [
        'status', 'ad_type', 'pricing_model', 'currency', 
        'created_at', 'start_date', 'end_date'
    ]
    search_fields = ['title', 'description', 'advertiser__email', 'advertiser__first_name', 'advertiser__last_name']
    readonly_fields = [
        'id', 'impressions', 'clicks', 'conversions', 'amount_spent',
        'click_through_rate', 'conversion_rate', 'cost_per_click', 'cost_per_acquisition',
        'is_active', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    
    inlines = [AdvertisementPlacementAssignmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'advertiser', 'title', 'description', 'ad_type', 'campaign')
        }),
        ('Targeting', {
            'fields': ('target_audience', 'geographic_targeting', 'demographic_targeting', 'product_categories'),
            'classes': ('collapse',)
        }),
        ('Creative Assets', {
            'fields': ('banner_image_url', 'banner_mobile_url', 'video_url', 'landing_page_url', 'call_to_action')
        }),
        ('Campaign Settings', {
            'fields': ('budget', 'daily_budget', 'bid_amount', 'pricing_model', 'currency')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approval_notes', 'approved_by', 'approved_at')
        }),
        ('Performance Metrics', {
            'fields': (
                'impressions', 'clicks', 'conversions', 'amount_spent',
                'click_through_rate', 'conversion_rate', 'cost_per_click', 'cost_per_acquisition'
            ),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_advertisements', 'pause_advertisements', 'resume_advertisements']
    
    def advertiser_name(self, obj):
        """Display advertiser name"""
        return obj.advertiser.get_full_name()
    advertiser_name.short_description = 'Advertiser'
    
    def ctr_display(self, obj):
        """Display click-through rate with formatting"""
        if obj.impressions > 0:
            ctr = obj.click_through_rate
            color = 'green' if ctr > 2.0 else 'orange' if ctr > 1.0 else 'red'
            return format_html(
                '<span style="color: {};">{:.2f}%</span>',
                color, ctr
            )
        return '-'
    ctr_display.short_description = 'CTR'
    
    def is_active_status(self, obj):
        """Display active status with visual indicator"""
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        else:
            return format_html('<span style="color: red;">●</span> Inactive')
    is_active_status.short_description = 'Status'
    
    def approve_advertisements(self, request, queryset):
        """Bulk approve advertisements"""
        updated = queryset.filter(status='pending_approval').update(
            status='active',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} advertisements approved successfully.')
    approve_advertisements.short_description = 'Approve selected advertisements'
    
    def pause_advertisements(self, request, queryset):
        """Bulk pause advertisements"""
        updated = queryset.filter(status='active').update(status='paused')
        self.message_user(request, f'{updated} advertisements paused successfully.')
    pause_advertisements.short_description = 'Pause selected advertisements'
    
    def resume_advertisements(self, request, queryset):
        """Bulk resume advertisements"""
        updated = queryset.filter(status='paused').update(status='active')
        self.message_user(request, f'{updated} advertisements resumed successfully.')
    resume_advertisements.short_description = 'Resume selected advertisements'

@admin.register(AdvertisementCampaign)
class AdvertisementCampaignAdmin(admin.ModelAdmin):
    """Admin interface for advertisement campaigns"""
    
    list_display = [
        'name', 'campaign_type', 'manager_name', 'total_budget',
        'advertisements_count', 'total_spent', 'is_active', 'created_at'
    ]
    list_filter = ['campaign_type', 'is_active', 'created_at', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'manager__email', 'manager__first_name', 'manager__last_name']
    readonly_fields = [
        'id', 'advertisements_count', 'total_spent', 'total_impressions', 'total_clicks',
        'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'campaign_type', 'manager')
        }),
        ('Budget & Timing', {
            'fields': ('total_budget', 'start_date', 'end_date')
        }),
        ('Goals & KPIs', {
            'fields': ('target_impressions', 'target_clicks', 'target_conversions', 'target_ctr'),
            'classes': ('collapse',)
        }),
        ('Performance Summary', {
            'fields': ('advertisements_count', 'total_spent', 'total_impressions', 'total_clicks'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def manager_name(self, obj):
        """Display manager name"""
        return obj.manager.get_full_name()
    manager_name.short_description = 'Manager'

@admin.register(AdvertisementPerformanceLog)
class AdvertisementPerformanceLogAdmin(admin.ModelAdmin):
    """Admin interface for performance logs"""
    
    list_display = [
        'advertisement_title', 'placement_name', 'event_type',
        'user_display', 'cost', 'created_at'
    ]
    list_filter = ['event_type', 'placement__location', 'created_at']
    search_fields = [
        'advertisement__title', 'placement__name', 'user__email',
        'ip_address', 'user_agent'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('advertisement', 'placement', 'event_type', 'cost')
        }),
        ('User Tracking', {
            'fields': ('user', 'session_id', 'ip_address', 'user_agent', 'referrer'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def advertisement_title(self, obj):
        """Display advertisement title"""
        return obj.advertisement.title
    advertisement_title.short_description = 'Advertisement'
    
    def placement_name(self, obj):
        """Display placement name"""
        return obj.placement.name
    placement_name.short_description = 'Placement'
    
    def user_display(self, obj):
        """Display user information"""
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return 'Anonymous'
    user_display.short_description = 'User'

@admin.register(AdvertisementAnalytics)
class AdvertisementAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for advertisement analytics"""
    
    list_display = [
        'advertisement_title', 'date', 'impressions', 'clicks',
        'conversions', 'ctr', 'cpc', 'amount_spent'
    ]
    list_filter = ['date', 'advertisement__ad_type', 'advertisement__status']
    search_fields = ['advertisement__title', 'advertisement__advertiser__email']
    readonly_fields = ['id', 'created_at']
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('advertisement', 'date')
        }),
        ('Performance Metrics', {
            'fields': ('impressions', 'clicks', 'conversions', 'amount_spent')
        }),
        ('Calculated Metrics', {
            'fields': ('ctr', 'cpc', 'cpa')
        }),
        ('Insights', {
            'fields': ('audience_demographics', 'geographic_performance'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def advertisement_title(self, obj):
        """Display advertisement title"""
        return obj.advertisement.title
    advertisement_title.short_description = 'Advertisement'
