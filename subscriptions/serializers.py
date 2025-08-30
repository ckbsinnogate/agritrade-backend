"""
AgriConnect Subscription System Serializers
REST API serializers for subscription and loyalty management

Features:
- Subscription plan comparison and selection
- User subscription management
- Usage tracking and analytics
- Loyalty program participation
- Invoice and billing management
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import (
    SubscriptionPlan, UserSubscription, SubscriptionUsageLog,
    LoyaltyProgram, UserLoyalty, LoyaltyTransaction,
    SubscriptionInvoice
)

User = get_user_model()


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    
    monthly_equivalent = serializers.SerializerMethodField()
    is_popular = serializers.SerializerMethodField()
    savings_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'tier', 'description',
            'price', 'currency', 'billing_cycle', 'trial_days',
            'features', 'product_listing_limit', 'warehouse_access',
            'transaction_fee_percentage', 'monthly_transactions',
            'storage_limit_gb', 'sms_credits',
            'priority_support', 'analytics_access', 'api_access',
            'blockchain_features', 'marketing_tools',
            'is_active', 'sort_order',
            'monthly_equivalent', 'is_popular', 'savings_percentage'
        ]
        read_only_fields = ['id', 'monthly_equivalent', 'is_popular', 'savings_percentage']
    
    def get_monthly_equivalent(self, obj):
        """Calculate monthly equivalent price"""
        return float(obj.get_monthly_price())
    
    def get_is_popular(self, obj):
        """Mark popular plans (typically professional tier)"""
        return obj.tier == 'professional'
    
    def get_savings_percentage(self, obj):
        """Calculate savings for yearly vs monthly billing"""
        from decimal import Decimal
        if obj.billing_cycle == 'yearly':
            # Assume monthly would be 10% more expensive
            monthly_price = obj.price / Decimal('12')
            implied_monthly = monthly_price * Decimal('1.1')
            savings = ((implied_monthly * Decimal('12')) - obj.price) / (implied_monthly * Decimal('12')) * Decimal('100')
            return round(float(savings), 1)
        return 0


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_trial = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    usage_summary = serializers.SerializerMethodField()
    next_billing_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_details', 'user_name',
            'status', 'started_at', 'expires_at', 'auto_renew',
            'trial_ends_at', 'amount_paid', 'currency',
            'payment_method', 'last_payment_date', 'next_payment_date',
            'current_period_transactions', 'current_period_storage_gb',
            'current_period_sms_sent', 'is_active', 'is_trial',
            'days_remaining', 'usage_summary', 'next_billing_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'plan_details', 'user_name', 'is_active', 'is_trial',
            'days_remaining', 'usage_summary', 'next_billing_amount',
            'created_at', 'updated_at'
        ]
    
    def get_usage_summary(self, obj):
        """Get usage summary for current period"""
        return {
            'transactions': {
                'used': obj.current_period_transactions,
                'limit': obj.plan.monthly_transactions,
                'percentage': obj.usage_percentage('transactions')
            },
            'storage': {
                'used': float(obj.current_period_storage_gb),
                'limit': obj.plan.storage_limit_gb,
                'percentage': obj.usage_percentage('storage')
            },
            'sms': {
                'used': obj.current_period_sms_sent,
                'limit': obj.plan.sms_credits,
                'percentage': obj.usage_percentage('sms')
            }
        }
    
    def get_next_billing_amount(self, obj):
        """Calculate next billing amount"""
        if obj.auto_renew and obj.next_payment_date:
            return float(obj.plan.price)
        return 0


class LoyaltyProgramSerializer(serializers.ModelSerializer):
    """Serializer for loyalty programs"""
    
    total_members = serializers.SerializerMethodField()
    is_eligible = serializers.SerializerMethodField()
    
    class Meta:
        model = LoyaltyProgram
        fields = [
            'id', 'name', 'description', 'program_type',
            'is_active', 'start_date', 'end_date',
            'rules', 'rewards', 'target_user_types',
            'minimum_transactions', 'minimum_spend',
            'total_members', 'is_eligible',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_members', 'is_eligible', 'created_at', 'updated_at']
    
    def get_total_members(self, obj):
        """Get total number of program members"""
        return obj.members.count()
    
    def get_is_eligible(self, obj):
        """Check if current user is eligible for this program"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        # Check user type eligibility
        user_roles = [role.name for role in user.roles.all()]
        user_types = [role.lower() for role in user_roles]
        
        return any(user_type in obj.target_user_types for user_type in user_types)


class UserLoyaltySerializer(serializers.ModelSerializer):
    """Serializer for user loyalty memberships"""
    
    program_details = LoyaltyProgramSerializer(source='program', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    next_tier = serializers.SerializerMethodField()
    points_to_next_tier = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLoyalty
        fields = [
            'id', 'user', 'program', 'program_details', 'user_name',
            'status', 'points_balance', 'points_earned_total',
            'points_redeemed_total', 'tier_level', 'tier_progress',
            'total_transactions', 'total_spent', 'last_activity',
            'next_tier', 'points_to_next_tier', 'joined_at'
        ]
        read_only_fields = [
            'id', 'program_details', 'user_name', 'next_tier',
            'points_to_next_tier', 'joined_at'
        ]
    
    def get_next_tier(self, obj):
        """Get next tier information"""
        tier_mapping = {
            'bronze': 'silver',
            'silver': 'gold',
            'gold': 'platinum',
            'platinum': 'diamond',
            'diamond': None
        }
        return tier_mapping.get(obj.status)
    
    def get_points_to_next_tier(self, obj):
        """Calculate points needed for next tier"""
        tier_thresholds = {
            'bronze': 1000,
            'silver': 2500,
            'gold': 5000,
            'platinum': 10000,
            'diamond': float('inf')
        }
        
        next_tier = self.get_next_tier(obj)
        if next_tier:
            next_threshold = tier_thresholds.get(next_tier, 0)
            return max(0, next_threshold - obj.points_earned_total)
        return 0


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating new subscriptions"""
    
    plan_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=50)
    auto_renew = serializers.BooleanField(default=True)
    use_trial = serializers.BooleanField(default=False)
    
    def validate_plan_id(self, value):
        """Validate that plan exists and is active"""
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive subscription plan")
    
    def validate(self, data):
        """Validate subscription creation"""
        user = self.context['request'].user
        
        # Check if user already has an active subscription of this type
        plan = SubscriptionPlan.objects.get(id=data['plan_id'])
        existing = UserSubscription.objects.filter(
            user=user,
            plan__plan_type=plan.plan_type,
            status__in=['active', 'trial'],
            expires_at__gt=timezone.now()
        ).exists()
        
        if existing:
            raise serializers.ValidationError(
                f"You already have an active {plan.plan_type} subscription"
            )
        
        return data