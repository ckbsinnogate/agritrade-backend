"""
AgriConnect Subscription & Membership System Models
Complete subscription management for farmers, consumers, and institutions

Features:
- Multi-tier subscription plans for different user types
- Flexible billing cycles (monthly, quarterly, yearly)
- Usage tracking and limits
- Trial periods and auto-renewal
- Feature-based access control
- Loyalty programs and rewards
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Subscription plans for different user types and tiers"""
    
    PLAN_TYPE_CHOICES = [
        ('farmer', 'Farmer'),
        ('consumer', 'Consumer'),
        ('institution', 'Institution'),
        ('processor', 'Processor'),
        ('logistics', 'Logistics'),
    ]
    
    TIER_CHOICES = [
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
        ('premium', 'Premium'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    CURRENCY_CHOICES = [
        ('GHS', 'Ghana Cedi'),
        ('NGN', 'Nigerian Naira'),
        ('KES', 'Kenyan Shilling'),
        ('USD', 'US Dollar'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GHS')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES)
    trial_days = models.IntegerField(default=0)
    
    # Features (stored as JSON)
    features = models.JSONField(default=dict)
    
    # Limits
    product_listing_limit = models.IntegerField(null=True, blank=True)
    warehouse_access = models.IntegerField(null=True, blank=True)
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    monthly_transactions = models.IntegerField(null=True, blank=True)
    storage_limit_gb = models.IntegerField(null=True, blank=True)
    sms_credits = models.IntegerField(null=True, blank=True)
    
    # Access Controls
    priority_support = models.BooleanField(default=False)
    analytics_access = models.BooleanField(default=False)
    api_access = models.BooleanField(default=False)
    blockchain_features = models.BooleanField(default=False)
    marketing_tools = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['plan_type', 'sort_order', 'price']
        indexes = [
            models.Index(fields=['plan_type', 'tier']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.plan_type.title()} - {self.tier.title()})"
    
    def get_monthly_price(self):
        """Convert price to monthly equivalent for comparison"""
        if self.billing_cycle == 'monthly':
            return self.price
        elif self.billing_cycle == 'quarterly':
            return self.price / 3
        elif self.billing_cycle == 'yearly':
            return self.price / 12
        return self.price


class UserSubscription(models.Model):
    """User subscription records with payment and usage tracking"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    payment_method = models.CharField(max_length=50, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking for current period
    current_period_transactions = models.IntegerField(default=0)
    current_period_storage_gb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    current_period_sms_sent = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return (
            self.status == 'active' and 
            self.expires_at > timezone.now()
        )
    
    @property
    def is_trial(self):
        """Check if subscription is in trial period"""
        return (
            self.status == 'trial' and 
            self.trial_ends_at and 
            self.trial_ends_at > timezone.now()
        )
    
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        if self.expires_at > timezone.now():
            return (self.expires_at - timezone.now()).days
        return 0
    
    def usage_percentage(self, usage_type):
        """Calculate usage percentage for a specific type"""
        if usage_type == 'transactions' and self.plan.monthly_transactions:
            return (self.current_period_transactions / self.plan.monthly_transactions) * 100
        elif usage_type == 'storage' and self.plan.storage_limit_gb:
            return (float(self.current_period_storage_gb) / self.plan.storage_limit_gb) * 100
        elif usage_type == 'sms' and self.plan.sms_credits:
            return (self.current_period_sms_sent / self.plan.sms_credits) * 100
        return 0
    
    def can_use_feature(self, feature_name):
        """Check if user can access a specific feature"""
        return getattr(self.plan, feature_name, False) if self.is_active else False


class SubscriptionUsageLog(models.Model):
    """Track subscription usage for billing and analytics"""
    
    USAGE_TYPE_CHOICES = [
        ('transaction', 'Transaction'),
        ('storage', 'Storage'),
        ('sms', 'SMS'),
        ('api_call', 'API Call'),
        ('listing', 'Product Listing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='usage_logs')
    usage_type = models.CharField(max_length=30, choices=USAGE_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscription_usage_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'usage_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.subscription.user.get_full_name()} - {self.usage_type}: {self.quantity}"


class LoyaltyProgram(models.Model):
    """Loyalty programs for frequent users"""
    
    PROGRAM_TYPE_CHOICES = [
        ('points', 'Points Based'),
        ('tier', 'Tier Based'),
        ('cashback', 'Cashback'),
        ('discount', 'Discount'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    
    # Program settings
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Rules and rewards
    rules = models.JSONField(default=dict, help_text="Program rules and earning criteria")
    rewards = models.JSONField(default=dict, help_text="Available rewards and redemption options")
    
    # Target audience
    target_user_types = models.JSONField(default=list, help_text="User types eligible for this program")
    minimum_transactions = models.IntegerField(default=0)
    minimum_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loyalty_programs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.program_type})"


class UserLoyalty(models.Model):
    """User participation in loyalty programs"""
    
    STATUS_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loyalty_memberships')
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='members')
    
    # Loyalty status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='bronze')
    points_balance = models.IntegerField(default=0)
    points_earned_total = models.IntegerField(default=0)
    points_redeemed_total = models.IntegerField(default=0)
    
    # Tier information
    tier_level = models.IntegerField(default=1)
    tier_progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Statistics
    total_transactions = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Dates
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_loyalty'
        unique_together = ['user', 'program']
        ordering = ['-points_balance']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['program', 'tier_level']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.program.name} ({self.status})"
    
    def add_points(self, points, description=""):
        """Add points to user's balance"""
        self.points_balance += points
        self.points_earned_total += points
        self.save()
        
        # Log the transaction
        LoyaltyTransaction.objects.create(
            loyalty_membership=self,
            transaction_type='earned',
            points=points,
            description=description
        )
    
    def redeem_points(self, points, description=""):
        """Redeem points from user's balance"""
        if self.points_balance >= points:
            self.points_balance -= points
            self.points_redeemed_total += points
            self.save()
            
            # Log the transaction
            LoyaltyTransaction.objects.create(
                loyalty_membership=self,
                transaction_type='redeemed',
                points=-points,
                description=description
            )
            return True
        return False


class LoyaltyTransaction(models.Model):
    """Track loyalty points transactions"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('earned', 'Points Earned'),
        ('redeemed', 'Points Redeemed'),
        ('expired', 'Points Expired'),
        ('bonus', 'Bonus Points'),
        ('adjustment', 'Manual Adjustment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loyalty_membership = models.ForeignKey(UserLoyalty, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    description = models.TextField(blank=True)
    
    # Related objects
    order_id = models.UUIDField(null=True, blank=True, help_text="Related order if applicable")
    reference_id = models.CharField(max_length=100, blank=True, help_text="External reference ID")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'loyalty_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['loyalty_membership', 'transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.loyalty_membership.user.get_full_name()} - {self.transaction_type}: {self.points} points"


class SubscriptionInvoice(models.Model):
    """Invoices for subscription payments"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # Invoice details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Dates
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid_date = models.DateTimeField(null=True, blank=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_gateway = models.CharField(max_length=50, blank=True)
    
    # Period covered
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Additional details
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_invoices'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.subscription.user.get_full_name()}"
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.status == 'sent' and self.due_date < timezone.now()
    
    def mark_as_paid(self, payment_method=None, transaction_id=None):
        """Mark invoice as paid"""
        self.status = 'paid'
        self.paid_date = timezone.now()
        if payment_method:
            self.payment_method = payment_method
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()
