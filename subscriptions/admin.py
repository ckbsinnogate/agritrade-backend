"""
AgriConnect Subscription System Admin
Django admin interface for subscription and loyalty management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    SubscriptionPlan, UserSubscription, SubscriptionUsageLog,
    LoyaltyProgram, UserLoyalty, LoyaltyTransaction,
    SubscriptionInvoice
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Admin interface for subscription plans"""
    
    list_display = [
        'name', 'plan_type', 'tier', 'price', 'currency',
        'billing_cycle', 'is_active', 'subscriber_count'
    ]
    list_filter = ['plan_type', 'tier', 'billing_cycle', 'is_active', 'currency']
    search_fields = ['name', 'description']
    ordering = ['plan_type', 'sort_order', 'price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'tier', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'currency', 'billing_cycle', 'trial_days')
        }),
        ('Features & Limits', {
            'fields': (
                'features', 'product_listing_limit', 'warehouse_access',
                'transaction_fee_percentage', 'monthly_transactions',
                'storage_limit_gb', 'sms_credits'
            )
        }),
        ('Access Controls', {
            'fields': (
                'priority_support', 'analytics_access', 'api_access',
                'blockchain_features', 'marketing_tools'
            )
        }),
        ('Status & Ordering', {
            'fields': ('is_active', 'sort_order')
        })
    )
    
    def subscriber_count(self, obj):
        """Count active subscribers"""
        count = obj.subscriptions.filter(
            status__in=['active', 'trial'],
            expires_at__gt=timezone.now()
        ).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    subscriber_count.short_description = 'Active Subscribers'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for user subscriptions"""
    
    list_display = [
        'user_link', 'plan_link', 'status', 'started_at',
        'expires_at', 'amount_paid', 'currency', 'auto_renew',
        'days_remaining_display'
    ]
    list_filter = [
        'status', 'plan__plan_type', 'plan__tier',
        'currency', 'auto_renew', 'started_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name',
        'user__last_name', 'plan__name'
    ]
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'is_active',
        'is_trial', 'days_remaining'
    ]
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'plan', 'status', 'auto_renew')
        }),
        ('Dates', {
            'fields': (
                'started_at', 'expires_at', 'trial_ends_at',
                'next_payment_date'
            )
        }),
        ('Payment Information', {
            'fields': (
                'amount_paid', 'currency', 'payment_method',
                'last_payment_date'
            )
        }),
        ('Usage Tracking', {
            'fields': (
                'current_period_transactions', 'current_period_storage_gb',
                'current_period_sms_sent'
            )
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:authentication_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'User'
    
    def plan_link(self, obj):
        """Link to plan admin page"""
        url = reverse('admin:subscriptions_subscriptionplan_change', args=[obj.plan.pk])
        return format_html('<a href="{}">{}</a>', url, obj.plan.name)
    plan_link.short_description = 'Plan'
    
    def days_remaining_display(self, obj):
        """Display days remaining with color coding"""
        days = obj.days_remaining()
        if days <= 0:
            color = 'red'
            text = 'Expired'
        elif days <= 7:
            color = 'orange'
            text = f'{days} days'
        else:
            color = 'green'
            text = f'{days} days'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    days_remaining_display.short_description = 'Days Remaining'


@admin.register(SubscriptionUsageLog)
class SubscriptionUsageLogAdmin(admin.ModelAdmin):
    """Admin interface for subscription usage logs"""
    
    list_display = [
        'subscription_user', 'usage_type', 'quantity',
        'description', 'created_at'
    ]
    list_filter = ['usage_type', 'created_at']
    search_fields = [
        'subscription__user__username', 'subscription__user__email',
        'description'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    readonly_fields = ['id', 'created_at']
    
    def subscription_user(self, obj):
        """Display subscription user"""
        return obj.subscription.user.get_full_name()
    subscription_user.short_description = 'User'


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    """Admin interface for loyalty programs"""
    
    list_display = [
        'name', 'program_type', 'is_active', 'start_date',
        'end_date', 'member_count', 'created_at'
    ]
    list_filter = ['program_type', 'is_active', 'start_date']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Program Details', {
            'fields': ('name', 'description', 'program_type')
        }),
        ('Schedule', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
        ('Rules & Rewards', {
            'fields': ('rules', 'rewards')
        }),
        ('Eligibility', {
            'fields': (
                'target_user_types', 'minimum_transactions',
                'minimum_spend'
            )
        })
    )
    
    def member_count(self, obj):
        """Count program members"""
        count = obj.members.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    member_count.short_description = 'Members'


@admin.register(UserLoyalty)
class UserLoyaltyAdmin(admin.ModelAdmin):
    """Admin interface for user loyalty memberships"""
    
    list_display = [
        'user_link', 'program_link', 'status', 'points_balance',
        'tier_level', 'total_transactions', 'last_activity'
    ]
    list_filter = ['status', 'tier_level', 'program', 'joined_at']
    search_fields = [
        'user__username', 'user__email', 'user__first_name',
        'user__last_name', 'program__name'
    ]
    ordering = ['-points_balance']
    
    readonly_fields = ['joined_at']
    
    fieldsets = (
        ('Membership Details', {
            'fields': ('user', 'program', 'status', 'tier_level')
        }),
        ('Points Information', {
            'fields': (
                'points_balance', 'points_earned_total',
                'points_redeemed_total', 'tier_progress'
            )
        }),
        ('Statistics', {
            'fields': (
                'total_transactions', 'total_spent', 'last_activity'
            )
        }),
        ('Dates', {
            'fields': ('joined_at',)
        })
    )
    
    def user_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:authentication_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'User'
    
    def program_link(self, obj):
        """Link to program admin page"""
        url = reverse('admin:subscriptions_loyaltyprogram_change', args=[obj.program.pk])
        return format_html('<a href="{}">{}</a>', url, obj.program.name)
    program_link.short_description = 'Program'


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    """Admin interface for loyalty transactions"""
    
    list_display = [
        'user_name', 'program_name', 'transaction_type',
        'points', 'description', 'created_at'
    ]
    list_filter = ['transaction_type', 'created_at']
    search_fields = [
        'loyalty_membership__user__username',
        'loyalty_membership__user__email',
        'description'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    readonly_fields = ['id', 'created_at']
    
    def user_name(self, obj):
        """Display user name"""
        return obj.loyalty_membership.user.get_full_name()
    user_name.short_description = 'User'
    
    def program_name(self, obj):
        """Display program name"""
        return obj.loyalty_membership.program.name
    program_name.short_description = 'Program'


@admin.register(SubscriptionInvoice)
class SubscriptionInvoiceAdmin(admin.ModelAdmin):
    """Admin interface for subscription invoices"""
    
    list_display = [
        'invoice_number', 'subscription_user', 'status',
        'total_amount', 'currency', 'issue_date',
        'due_date', 'paid_date', 'is_overdue_display'
    ]
    list_filter = ['status', 'currency', 'issue_date', 'due_date']
    search_fields = [
        'invoice_number', 'subscription__user__username',
        'subscription__user__email'
    ]
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']
    
    readonly_fields = [
        'id', 'is_overdue', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Invoice Details', {
            'fields': (
                'subscription', 'invoice_number', 'status'
            )
        }),
        ('Amounts', {
            'fields': (
                'amount', 'tax_amount', 'total_amount', 'currency'
            )
        }),
        ('Dates', {
            'fields': (
                'issue_date', 'due_date', 'paid_date'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method', 'transaction_id', 'payment_gateway'
            )
        }),
        ('Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Additional Information', {
            'fields': ('notes', 'metadata')
        }),
        ('System Information', {
            'fields': ('id', 'is_overdue', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def subscription_user(self, obj):
        """Display subscription user"""
        return obj.subscription.user.get_full_name()
    subscription_user.short_description = 'User'
    
    def is_overdue_display(self, obj):
        """Display overdue status with color"""
        if obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">Overdue</span>')
        elif obj.status == 'paid':
            return format_html('<span style="color: green;">Paid</span>')
        else:
            return format_html('<span style="color: blue;">Current</span>')
    is_overdue_display.short_description = 'Status'
