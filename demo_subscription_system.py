"""
AgriConnect Subscription System Demo
Create sample subscription plans and demonstrate subscription functionality

This script demonstrates:
- Subscription plan creation for different user types
- User subscription management
- Loyalty program implementation
- Usage tracking and analytics
"""

import os
import sys
import django
from decimal import Decimal
from datetime import timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.utils import timezone
from django.db import models as django_models
from authentication.models import User
from subscriptions.models import (
    SubscriptionPlan, UserSubscription, SubscriptionUsageLog,
    LoyaltyProgram, UserLoyalty, LoyaltyTransaction,
    SubscriptionInvoice
)


def create_subscription_plans():
    """Create comprehensive subscription plans for all user types"""
    print("🎯 Creating Subscription Plans...")
    
    plans_data = [
        # FARMER PLANS
        {
            'name': 'Farmer Basic',
            'plan_type': 'farmer',
            'tier': 'basic',
            'description': 'Free plan for smallholder farmers to get started',
            'price': Decimal('0.00'),
            'currency': 'GHS',
            'billing_cycle': 'monthly',
            'trial_days': 0,
            'features': {
                'product_listings': 5,
                'marketplace_access': True,
                'basic_analytics': True,
                'community_access': True
            },
            'product_listing_limit': 5,
            'monthly_transactions': 10,
            'storage_limit_gb': 1,
            'sms_credits': 50,
            'transaction_fee_percentage': Decimal('3.5'),
            'priority_support': False,
            'analytics_access': True,
            'api_access': False,
            'blockchain_features': False,
            'marketing_tools': False
        },
        {
            'name': 'Farmer Professional',
            'plan_type': 'farmer',
            'tier': 'professional',
            'description': 'Enhanced features for growing agricultural businesses',
            'price': Decimal('25.00'),
            'currency': 'GHS',
            'billing_cycle': 'monthly',
            'trial_days': 14,
            'features': {
                'product_listings': 50,
                'marketplace_access': True,
                'advanced_analytics': True,
                'community_access': True,
                'warehouse_integration': True,
                'bulk_ordering': True
            },
            'product_listing_limit': 50,
            'monthly_transactions': 100,
            'storage_limit_gb': 10,
            'sms_credits': 500,
            'transaction_fee_percentage': Decimal('2.5'),
            'priority_support': True,
            'analytics_access': True,
            'api_access': True,
            'blockchain_features': True,
            'marketing_tools': True
        },
        {
            'name': 'Farmer Enterprise',
            'plan_type': 'farmer',
            'tier': 'enterprise',
            'description': 'Complete solution for large-scale farming operations',
            'price': Decimal('250.00'),
            'currency': 'GHS',
            'billing_cycle': 'yearly',
            'trial_days': 30,
            'features': {
                'product_listings': 'unlimited',
                'marketplace_access': True,
                'premium_analytics': True,
                'community_access': True,
                'warehouse_integration': True,
                'bulk_ordering': True,
                'contract_farming': True,
                'ai_insights': True
            },
            'product_listing_limit': None,
            'monthly_transactions': None,
            'storage_limit_gb': 100,
            'sms_credits': 5000,
            'transaction_fee_percentage': Decimal('1.5'),
            'priority_support': True,
            'analytics_access': True,
            'api_access': True,
            'blockchain_features': True,
            'marketing_tools': True
        },
        
        # CONSUMER PLANS
        {
            'name': 'Consumer Basic',
            'plan_type': 'consumer',
            'tier': 'basic',
            'description': 'Free access to marketplace and basic features',
            'price': Decimal('0.00'),
            'currency': 'GHS',
            'billing_cycle': 'monthly',
            'trial_days': 0,
            'features': {
                'marketplace_access': True,
                'order_tracking': True,
                'reviews': True,
                'basic_recommendations': True
            },
            'monthly_transactions': 5,
            'sms_credits': 20,
            'transaction_fee_percentage': Decimal('2.0'),
            'priority_support': False,
            'analytics_access': False,
            'api_access': False,
            'blockchain_features': False,
            'marketing_tools': False
        },
        {
            'name': 'Consumer Premium',
            'plan_type': 'consumer',
            'tier': 'premium',
            'description': 'Enhanced shopping experience with exclusive benefits',
            'price': Decimal('15.00'),
            'currency': 'GHS',
            'billing_cycle': 'monthly',
            'trial_days': 7,
            'features': {
                'marketplace_access': True,
                'order_tracking': True,
                'reviews': True,
                'ai_recommendations': True,
                'subscription_boxes': True,
                'priority_delivery': True,
                'exclusive_deals': True
            },
            'monthly_transactions': 50,
            'sms_credits': 200,
            'transaction_fee_percentage': Decimal('1.0'),
            'priority_support': True,
            'analytics_access': True,
            'api_access': False,
            'blockchain_features': True,
            'marketing_tools': False
        },
        
        # INSTITUTION PLANS
        {
            'name': 'Institution Standard',
            'plan_type': 'institution',
            'tier': 'professional',
            'description': 'Bulk purchasing and procurement management for institutions',
            'price': Decimal('100.00'),
            'currency': 'GHS',
            'billing_cycle': 'monthly',
            'trial_days': 14,
            'features': {
                'bulk_purchasing': True,
                'procurement_management': True,
                'vendor_management': True,
                'contract_management': True,
                'reporting': True
            },
            'monthly_transactions': 200,
            'storage_limit_gb': 50,
            'sms_credits': 1000,
            'transaction_fee_percentage': Decimal('1.5'),
            'priority_support': True,
            'analytics_access': True,
            'api_access': True,
            'blockchain_features': True,
            'marketing_tools': False
        }
    ]
    
    created_plans = []
    for i, plan_data in enumerate(plans_data):
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            plan_type=plan_data['plan_type'],
            tier=plan_data['tier'],
            defaults={
                **plan_data,
                'sort_order': i + 1,
                'is_active': True
            }
        )
        created_plans.append(plan)
        status = "✅ Created" if created else "📋 Exists"
        print(f"  {status}: {plan.name} - {plan.plan_type.title()} {plan.tier.title()} - {plan.currency} {plan.price}")
    
    return created_plans


def create_loyalty_programs():
    """Create loyalty programs for user engagement"""
    print("\n🏆 Creating Loyalty Programs...")
    
    programs_data = [
        {
            'name': 'AgriConnect Rewards',
            'description': 'Earn points for every transaction and activity on the platform',
            'program_type': 'points',
            'start_date': timezone.now(),
            'end_date': None,
            'target_user_types': ['farmer', 'consumer', 'institution'],
            'minimum_transactions': 0,
            'minimum_spend': Decimal('0.00'),
            'rules': {
                'points_per_transaction': 10,
                'points_per_ghs_spent': 1,
                'welcome_bonus': 100,
                'review_bonus': 25,
                'referral_bonus': 500,
                'tier_multipliers': {
                    'bronze': 1.0,
                    'silver': 1.2,
                    'gold': 1.5,
                    'platinum': 2.0,
                    'diamond': 3.0
                }
            },
            'rewards': {
                'discount_vouchers': {
                    '5_percent': 500,
                    '10_percent': 1000,
                    '15_percent': 2000
                },
                'free_shipping': 750,
                'exclusive_products': 1500,
                'consultation_session': 2500
            }
        },
        {
            'name': 'Farmer Excellence Program',
            'description': 'Exclusive program for committed farmers to achieve excellence',
            'program_type': 'tier',
            'start_date': timezone.now(),
            'end_date': None,
            'target_user_types': ['farmer'],
            'minimum_transactions': 5,
            'minimum_spend': Decimal('100.00'),
            'rules': {
                'tier_requirements': {
                    'bronze': {'transactions': 5, 'spend': 100},
                    'silver': {'transactions': 20, 'spend': 500},
                    'gold': {'transactions': 50, 'spend': 2000},
                    'platinum': {'transactions': 100, 'spend': 5000},
                    'diamond': {'transactions': 200, 'spend': 10000}
                },
                'seasonal_bonuses': True,
                'certification_support': True
            },
            'rewards': {
                'reduced_fees': {
                    'bronze': 0.1,
                    'silver': 0.3,
                    'gold': 0.5,
                    'platinum': 0.8,
                    'diamond': 1.0
                },
                'priority_support': ['silver', 'gold', 'platinum', 'diamond'],
                'exclusive_training': ['gold', 'platinum', 'diamond'],
                'ai_insights': ['platinum', 'diamond']
            }
        }
    ]
    
    created_programs = []
    for program_data in programs_data:
        program, created = LoyaltyProgram.objects.get_or_create(
            name=program_data['name'],
            defaults={
                **program_data,
                'is_active': True
            }
        )
        created_programs.append(program)
        status = "✅ Created" if created else "📋 Exists"
        print(f"  {status}: {program.name} ({program.program_type})")
    
    return created_programs


def create_sample_subscriptions():
    """Create sample subscriptions for demonstration"""
    print("\n👥 Creating Sample Subscriptions...")
    
    # Get sample users
    farmer_users = User.objects.filter(roles__name='FARMER')[:3]
    consumer_users = User.objects.filter(roles__name='CONSUMER')[:2]
    
    # Get subscription plans
    farmer_pro = SubscriptionPlan.objects.filter(plan_type='farmer', tier='professional').first()
    consumer_premium = SubscriptionPlan.objects.filter(plan_type='consumer', tier='premium').first()
    
    created_subscriptions = []
    
    # Create farmer subscriptions
    for i, user in enumerate(farmer_users):
        if farmer_pro:
            subscription, created = UserSubscription.objects.get_or_create(
                user=user,
                plan=farmer_pro,
                defaults={
                    'status': 'active' if i == 0 else 'trial',
                    'started_at': timezone.now() - timedelta(days=i*10),
                    'expires_at': timezone.now() + timedelta(days=30-i*10),
                    'trial_ends_at': timezone.now() + timedelta(days=14) if i > 0 else None,
                    'auto_renew': True,
                    'amount_paid': farmer_pro.price if i == 0 else Decimal('0.00'),
                    'currency': farmer_pro.currency,
                    'payment_method': 'paystack' if i == 0 else None,
                    'last_payment_date': timezone.now() - timedelta(days=i*10) if i == 0 else None,
                    'next_payment_date': timezone.now() + timedelta(days=30-i*10),
                    'current_period_transactions': i * 5,
                    'current_period_sms_sent': i * 20
                }
            )
            if created:
                created_subscriptions.append(subscription)
                print(f"  ✅ Created: {user.get_full_name()} - {farmer_pro.name} ({subscription.status})")
    
    # Create consumer subscriptions
    for i, user in enumerate(consumer_users):
        if consumer_premium:
            subscription, created = UserSubscription.objects.get_or_create(
                user=user,
                plan=consumer_premium,
                defaults={
                    'status': 'active',
                    'started_at': timezone.now() - timedelta(days=i*5),
                    'expires_at': timezone.now() + timedelta(days=30-i*5),
                    'auto_renew': True,
                    'amount_paid': consumer_premium.price,
                    'currency': consumer_premium.currency,
                    'payment_method': 'paystack',
                    'last_payment_date': timezone.now() - timedelta(days=i*5),
                    'next_payment_date': timezone.now() + timedelta(days=30-i*5),
                    'current_period_transactions': i * 3,
                    'current_period_sms_sent': i * 10
                }
            )
            if created:
                created_subscriptions.append(subscription)
                print(f"  ✅ Created: {user.get_full_name()} - {consumer_premium.name}")
    
    return created_subscriptions


def create_loyalty_memberships():
    """Create loyalty program memberships"""
    print("\n🎖️ Creating Loyalty Memberships...")
    
    # Get loyalty programs
    general_program = LoyaltyProgram.objects.filter(name='AgriConnect Rewards').first()
    farmer_program = LoyaltyProgram.objects.filter(name='Farmer Excellence Program').first()
    
    # Get users with subscriptions
    users_with_subscriptions = User.objects.filter(subscriptions__isnull=False).distinct()
    
    created_memberships = []
    
    for i, user in enumerate(users_with_subscriptions[:5]):
        # Add to general program
        if general_program:
            membership, created = UserLoyalty.objects.get_or_create(
                user=user,
                program=general_program,
                defaults={
                    'status': ['bronze', 'silver', 'gold'][min(i, 2)],
                    'points_balance': 100 + (i * 250),
                    'points_earned_total': 200 + (i * 500),
                    'points_redeemed_total': 100 + (i * 100),
                    'tier_level': min(i + 1, 3),
                    'total_transactions': i * 5 + 3,
                    'total_spent': Decimal(str(100 + i * 300))
                }
            )
            if created:
                created_memberships.append(membership)
                print(f"  ✅ Created: {user.get_full_name()} - {general_program.name} ({membership.status})")
                
                # Add some loyalty transactions
                LoyaltyTransaction.objects.create(
                    loyalty_membership=membership,
                    transaction_type='earned',
                    points=100,
                    description='Welcome bonus'
                )
                LoyaltyTransaction.objects.create(
                    loyalty_membership=membership,
                    transaction_type='earned',
                    points=50,
                    description='First purchase bonus'
                )
        
        # Add farmers to farmer program
        if farmer_program and user.roles.filter(name='FARMER').exists():
            farmer_membership, created = UserLoyalty.objects.get_or_create(
                user=user,
                program=farmer_program,
                defaults={
                    'status': ['bronze', 'silver'][min(i, 1)],
                    'points_balance': 50 + (i * 100),
                    'points_earned_total': 100 + (i * 200),
                    'tier_level': min(i + 1, 2),
                    'total_transactions': i * 3 + 2,
                    'total_spent': Decimal(str(200 + i * 400))
                }
            )
            if created:
                created_memberships.append(farmer_membership)
                print(f"  ✅ Created: {user.get_full_name()} - {farmer_program.name} ({farmer_membership.status})")
    
    return created_memberships


def create_usage_logs():
    """Create sample usage logs for analytics"""
    print("\n📊 Creating Usage Logs...")
    
    subscriptions = UserSubscription.objects.filter(status__in=['active', 'trial'])
    
    created_logs = []
    for subscription in subscriptions:
        # Create various usage log entries
        usage_types = ['transaction', 'storage', 'sms', 'api_call', 'listing']
        
        for usage_type in usage_types:
            for day in range(1, 8):  # Last 7 days
                log_date = timezone.now() - timedelta(days=day)
                
                # Random usage amounts based on type
                if usage_type == 'transaction':
                    quantity = min(day * 2, 10)
                elif usage_type == 'storage':
                    quantity = min(day * 0.5, 5)
                elif usage_type == 'sms':
                    quantity = min(day * 5, 30)
                elif usage_type == 'api_call':
                    quantity = min(day * 20, 100)
                else:  # listing
                    quantity = min(day, 5)
                
                log = SubscriptionUsageLog.objects.create(
                    subscription=subscription,
                    usage_type=usage_type,
                    quantity=Decimal(str(quantity)),
                    description=f"Daily {usage_type} usage",
                    metadata={'date': log_date.date().isoformat()}
                )
                log.created_at = log_date
                log.save(update_fields=['created_at'])
                created_logs.append(log)
    
    print(f"  ✅ Created {len(created_logs)} usage log entries")
    return created_logs


def generate_subscription_analytics():
    """Generate subscription analytics summary"""
    print("\n📈 Subscription System Analytics...")
    
    # Subscription statistics
    total_plans = SubscriptionPlan.objects.filter(is_active=True).count()
    total_subscriptions = UserSubscription.objects.count()
    active_subscriptions = UserSubscription.objects.filter(
        status__in=['active', 'trial'],
        expires_at__gt=timezone.now()
    ).count()
      # Revenue analytics
    total_revenue = UserSubscription.objects.filter(
        status__in=['active', 'cancelled', 'expired']
    ).aggregate(
        total=django_models.Sum('amount_paid')
    )['total'] or Decimal('0.00')
      # Loyalty program statistics
    total_programs = LoyaltyProgram.objects.filter(is_active=True).count()
    total_loyalty_members = UserLoyalty.objects.count()
    total_points_earned = UserLoyalty.objects.aggregate(
        total=django_models.Sum('points_earned_total')
    )['total'] or 0
    
    # Usage analytics
    total_usage_logs = SubscriptionUsageLog.objects.count()
    recent_usage = SubscriptionUsageLog.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    print(f"""
🎯 SUBSCRIPTION SYSTEM SUMMARY:
   📋 Subscription Plans: {total_plans}
   👥 Total Subscriptions: {total_subscriptions}
   ✅ Active Subscriptions: {active_subscriptions}
   💰 Total Revenue: GHS {total_revenue}
   
🏆 LOYALTY PROGRAM SUMMARY:
   📊 Active Programs: {total_programs}
   👥 Total Members: {total_loyalty_members}
   🎖️ Points Earned: {total_points_earned:,}
   
📈 USAGE ANALYTICS:
   📝 Total Usage Logs: {total_usage_logs}
   📅 Recent Usage (7d): {recent_usage}
""")


def test_subscription_features():
    """Test subscription system features"""
    print("\n🧪 Testing Subscription Features...")
    
    # Test subscription creation
    user = User.objects.filter(roles__name='FARMER').first()
    plan = SubscriptionPlan.objects.filter(
        plan_type='farmer', 
        tier='professional'
    ).first()
    
    if user and plan:
        print(f"✅ Test User: {user.get_full_name()}")
        print(f"✅ Test Plan: {plan.name}")
        
        # Check if user can access features
        subscription = UserSubscription.objects.filter(
            user=user, 
            plan=plan
        ).first()
        
        if subscription:
            print(f"✅ Subscription Status: {subscription.status}")
            print(f"✅ Is Active: {subscription.is_active}")
            print(f"✅ Days Remaining: {subscription.days_remaining()}")
            print(f"✅ Usage - Transactions: {subscription.usage_percentage('transactions'):.1f}%")
            print(f"✅ Can Use Analytics: {subscription.can_use_feature('analytics_access')}")
            print(f"✅ Can Use API: {subscription.can_use_feature('api_access')}")
    
    # Test loyalty program
    loyalty_membership = UserLoyalty.objects.first()
    if loyalty_membership:
        print(f"\n🏆 Loyalty Test:")
        print(f"✅ User: {loyalty_membership.user.get_full_name()}")
        print(f"✅ Program: {loyalty_membership.program.name}")
        print(f"✅ Status: {loyalty_membership.status}")
        print(f"✅ Points Balance: {loyalty_membership.points_balance}")
        
        # Test point redemption
        if loyalty_membership.points_balance >= 100:
            success = loyalty_membership.redeem_points(50, "Test redemption")
            print(f"✅ Point Redemption: {'Success' if success else 'Failed'}")
            print(f"✅ New Balance: {loyalty_membership.points_balance}")


def main():
    """Run the complete subscription system demo"""
    print("🌾 AGRICONNECT SUBSCRIPTION SYSTEM DEMO")
    print("=" * 60)
    
    try:
        # Create subscription plans
        plans = create_subscription_plans()
        
        # Create loyalty programs
        programs = create_loyalty_programs()
        
        # Create sample subscriptions
        subscriptions = create_sample_subscriptions()
        
        # Create loyalty memberships
        memberships = create_loyalty_memberships()
        
        # Create usage logs
        usage_logs = create_usage_logs()
        
        # Generate analytics
        generate_subscription_analytics()
        
        # Test features
        test_subscription_features()
        
        print("\n🎉 SUBSCRIPTION SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Subscription plans created and configured")
        print("✅ Loyalty programs implemented")
        print("✅ Sample subscriptions active")
        print("✅ Usage tracking functional")
        print("✅ Analytics system operational")
        print("\n📊 Ready for API testing at: http://127.0.0.1:8000/api/v1/subscriptions/")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
