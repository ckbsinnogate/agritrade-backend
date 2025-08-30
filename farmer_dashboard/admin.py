"""
Farmer Dashboard Admin Configuration
Django admin interface for farmer dashboard management
"""

from django.contrib import admin
from .models import FarmerDashboardPreferences, FarmerAlert, FarmerDashboardMetrics, FarmerGoal


@admin.register(FarmerDashboardPreferences)
class FarmerDashboardPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for farmer dashboard preferences"""
    list_display = [
        'farmer', 'default_currency', 'preferred_language', 
        'dashboard_theme', 'created_at', 'updated_at'
    ]
    list_filter = [
        'default_currency', 'preferred_language', 'dashboard_theme',
        'weather_alerts', 'market_price_alerts', 'order_notifications'
    ]
    search_fields = ['farmer__username', 'farmer__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Farmer Information', {
            'fields': ('farmer',)
        }),
        ('Dashboard Settings', {
            'fields': ('default_currency', 'preferred_language', 'dashboard_theme')
        }),
        ('Notification Preferences', {
            'fields': (
                'weather_alerts', 'market_price_alerts', 
                'order_notifications', 'payment_reminders'
            )
        }),
        ('Analytics Preferences', {
            'fields': (
                'show_revenue_trends', 'show_crop_analytics', 'show_market_insights'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FarmerAlert)
class FarmerAlertAdmin(admin.ModelAdmin):
    """Admin interface for farmer alerts"""
    list_display = [
        'title', 'farmer', 'alert_type', 'priority', 
        'is_read', 'is_archived', 'created_at'
    ]
    list_filter = [
        'alert_type', 'priority', 'is_read', 'is_archived', 
        'created_at', 'expires_at'
    ]
    search_fields = ['title', 'message', 'farmer__username']
    readonly_fields = ['created_at', 'updated_at', 'is_expired']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('farmer', 'title', 'message', 'alert_type', 'priority')
        }),
        ('Status', {
            'fields': ('is_read', 'is_archived', 'expires_at')
        }),
        ('Related Objects', {
            'fields': ('related_product_id', 'related_order_id', 'related_farm_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'is_expired'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'archive_alerts']
    
    def mark_as_read(self, request, queryset):
        """Mark selected alerts as read"""
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} alerts marked as read.')
    mark_as_read.short_description = "Mark selected alerts as read"
    
    def mark_as_unread(self, request, queryset):
        """Mark selected alerts as unread"""
        count = queryset.update(is_read=False)
        self.message_user(request, f'{count} alerts marked as unread.')
    mark_as_unread.short_description = "Mark selected alerts as unread"
    
    def archive_alerts(self, request, queryset):
        """Archive selected alerts"""
        count = queryset.update(is_archived=True)
        self.message_user(request, f'{count} alerts archived.')
    archive_alerts.short_description = "Archive selected alerts"


@admin.register(FarmerDashboardMetrics)
class FarmerDashboardMetricsAdmin(admin.ModelAdmin):
    """Admin interface for farmer dashboard metrics"""
    list_display = [
        'farmer', 'date', 'total_revenue', 'orders_count', 
        'total_products', 'total_customers'
    ]
    list_filter = ['date', 'created_at']
    search_fields = ['farmer__username']
    readonly_fields = [
        'created_at', 'updated_at', 'total_revenue', 'orders_count',
        'products_sold', 'average_order_value', 'total_products',
        'active_products', 'total_customers'
    ]
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farmer', 'date')
        }),
        ('Revenue Metrics', {
            'fields': (
                'total_revenue', 'orders_count', 'products_sold', 'average_order_value'
            )
        }),
        ('Product Metrics', {
            'fields': (
                'total_products', 'active_products', 
                'low_stock_products', 'out_of_stock_products'
            )
        }),
        ('Customer Metrics', {
            'fields': ('new_customers', 'returning_customers', 'total_customers')
        }),
        ('Farm Metrics', {
            'fields': ('farms_registered', 'total_farm_area')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FarmerGoal)
class FarmerGoalAdmin(admin.ModelAdmin):
    """Admin interface for farmer goals"""
    list_display = [
        'title', 'farmer', 'goal_type', 'progress_percentage', 
        'status', 'target_date', 'days_remaining'
    ]
    list_filter = ['goal_type', 'status', 'start_date', 'target_date']
    search_fields = ['title', 'description', 'farmer__username']
    readonly_fields = [
        'created_at', 'updated_at', 'progress_percentage', 
        'days_remaining', 'completed_at'
    ]
    date_hierarchy = 'target_date'
    
    fieldsets = (
        ('Goal Information', {
            'fields': ('farmer', 'title', 'description', 'goal_type')
        }),
        ('Target & Progress', {
            'fields': (
                'target_value', 'current_value', 'unit', 
                'progress_percentage'
            )
        }),
        ('Timeline', {
            'fields': (
                'start_date', 'target_date', 'days_remaining', 'status'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_completed', 'mark_active']
    
    def mark_completed(self, request, queryset):
        """Mark selected goals as completed"""
        count = queryset.update(status='completed')
        self.message_user(request, f'{count} goals marked as completed.')
    mark_completed.short_description = "Mark selected goals as completed"
    
    def mark_active(self, request, queryset):
        """Mark selected goals as active"""
        count = queryset.update(status='active')
        self.message_user(request, f'{count} goals marked as active.')
    mark_active.short_description = "Mark selected goals as active"
