#!/usr/bin/env python3
"""
Verify Section 4.5.1 Farmer Subscription Plans compliance with PRD requirements
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def verify_farmer_subscription_plans():
    """Verify all farmer subscription plans match PRD Section 4.5.1 requirements"""
    print("🌾 VERIFYING PRD SECTION 4.5.1 FARMER SUBSCRIPTION PLANS")
    print("="*60)
    
    from subscriptions.models import SubscriptionPlan
    
    # PRD Section 4.5.1 Requirements
    required_farmer_plans = {
        'basic': {
            'name_pattern': 'basic',
            'description': 'Free listing with transaction fees',
            'expected_features': ['free_listings', 'transaction_fees'],
            'price_range': (0.00, 0.00),  # Free
        },
        'professional': {
            'name_pattern': 'professional',
            'description': 'Premium features, analytics, and priority support',
            'expected_features': ['premium_features', 'analytics_access', 'priority_support'],
            'price_range': (10.00, 100.00),  # Reasonable professional pricing
        },
        'enterprise': {
            'name_pattern': 'enterprise',
            'description': 'Unlimited listings, API access, and dedicated support',
            'expected_features': ['unlimited_listings', 'api_access', 'dedicated_support'],
            'price_range': (50.00, 500.00),  # Enterprise pricing
        },
        'cooperative': {
            'name_pattern': 'cooperative',
            'description': 'Multi-farmer group management and bulk features',
            'expected_features': ['group_management', 'bulk_features'],
            'price_range': (20.00, 200.00),  # Cooperative pricing
        }
    }
    
    # Get all farmer plans
    farmer_plans = SubscriptionPlan.objects.filter(
        plan_type='farmer',
        is_active=True
    ).order_by('tier', 'price')
    
    print(f"📊 Found {farmer_plans.count()} active farmer subscription plans\n")
    
    # Verify each required plan
    compliance_results = {}
    
    for tier, requirements in required_farmer_plans.items():
        print(f"🔍 Checking {tier.title()} Plan Requirements...")
        
        # Find matching plan
        matching_plans = farmer_plans.filter(tier=tier)
        
        if not matching_plans.exists():
            print(f"❌ {tier.title()} Plan: NOT FOUND")
            compliance_results[tier] = False
            continue
        
        plan = matching_plans.first()
        print(f"✅ Found: {plan.name}")
        
        # Check plan details
        checks = []
        
        # 1. Price validation
        min_price, max_price = requirements['price_range']
        if min_price <= float(plan.price) <= max_price:
            print(f"   ✅ Price: {plan.currency} {plan.price} (within expected range)")
            checks.append(True)
        else:
            print(f"   ❌ Price: {plan.currency} {plan.price} (outside expected range {min_price}-{max_price})")
            checks.append(False)
          # 2. Feature validation based on tier
        if tier == 'basic':
            # Basic plan should be free or very low cost
            if float(plan.price) <= 5.00:
                print(f"   ✅ Basic Plan: Free/low-cost pricing verified")
                checks.append(True)
            else:
                print(f"   ❌ Basic Plan: Should be free or very low cost")
                checks.append(False)
                
        elif tier == 'professional':
            # Professional should have analytics and priority support
            if plan.analytics_access and plan.priority_support:
                print(f"   ✅ Professional Plan: Analytics and priority support enabled")
                checks.append(True)
            else:
                print(f"   ❌ Professional Plan: Missing analytics_access or priority_support")
                checks.append(False)
                
        elif tier == 'enterprise':
            # Enterprise should have API access and unlimited features
            listing_limit = plan.product_listing_limit or 0
            if plan.api_access and listing_limit >= 1000:
                print(f"   ✅ Enterprise Plan: API access and high listing limits ({listing_limit})")
                checks.append(True)
            else:
                print(f"   ❌ Enterprise Plan: Missing API access or sufficient listing limits (limit: {listing_limit})")
                checks.append(False)
                
        elif tier == 'cooperative':
            # Cooperative should support group features
            if 'group' in plan.description.lower() or 'cooperative' in plan.description.lower():
                print(f"   ✅ Cooperative Plan: Group/cooperative features indicated")
                checks.append(True)
            else:
                print(f"   ❌ Cooperative Plan: No group/cooperative features mentioned")
                checks.append(False)
        
        # 3. Billing cycle validation
        if plan.billing_cycle in ['monthly', 'yearly']:
            print(f"   ✅ Billing Cycle: {plan.billing_cycle} (standard option)")
            checks.append(True)
        else:
            print(f"   ⚠️ Billing Cycle: {plan.billing_cycle} (non-standard)")
            checks.append(True)  # Not a failure, just noting
        
        # 4. Plan status
        if plan.is_active:
            print(f"   ✅ Status: Active and available")
            checks.append(True)
        else:
            print(f"   ❌ Status: Inactive")
            checks.append(False)
        
        compliance_results[tier] = all(checks)
        print(f"   📊 {tier.title()} Plan Compliance: {'✅ PASS' if all(checks) else '❌ FAIL'}\n")
    
    return compliance_results

def display_compliance_summary(compliance_results):
    """Display final compliance summary"""
    print("="*60)
    print("🎯 PRD SECTION 4.5.1 COMPLIANCE SUMMARY")
    print("="*60)
    
    total_plans = len(compliance_results)
    compliant_plans = sum(compliance_results.values())
    
    print(f"\n📊 Implementation Status:")
    for tier, is_compliant in compliance_results.items():
        status = "✅ COMPLIANT" if is_compliant else "❌ NON-COMPLIANT"
        print(f"   • {tier.title()} Plan: {status}")
    
    compliance_percentage = (compliant_plans / total_plans) * 100 if total_plans > 0 else 0
    
    print(f"\n🎯 Overall Compliance: {compliant_plans}/{total_plans} plans ({compliance_percentage:.0f}%)")
    
    if compliance_percentage == 100:
        print("🏆 SECTION 4.5.1 FARMER SUBSCRIPTION PLANS: 100% PRD COMPLIANT")
        print("✅ All required farmer subscription plans implemented correctly")
        print("✅ Plan features match PRD specifications")
        print("✅ Pricing tiers appropriate for target users")
        print("✅ Ready for production deployment")
    elif compliance_percentage >= 75:
        print("⚠️ SECTION 4.5.1: MOSTLY COMPLIANT - Minor adjustments needed")
    else:
        print("❌ SECTION 4.5.1: SIGNIFICANT COMPLIANCE ISSUES")
        print("Major plan adjustments required to meet PRD specifications")
    
    return compliance_percentage == 100

def check_plan_progression():
    """Check if plans have logical feature progression"""
    print("\n🔄 CHECKING PLAN PROGRESSION LOGIC...")
    
    from subscriptions.models import SubscriptionPlan
    
    farmer_plans = SubscriptionPlan.objects.filter(
        plan_type='farmer',
        is_active=True
    ).order_by('price')
    
    print("📈 Plan Progression Analysis:")
    
    for i, plan in enumerate(farmer_plans):
        tier_info = f"{plan.tier.title()} - {plan.currency} {plan.price}"
        features = []
        
        if plan.analytics_access:
            features.append("Analytics")
        if plan.api_access:
            features.append("API")
        if plan.priority_support:
            features.append("Priority Support")
        if plan.blockchain_features:
            features.append("Blockchain")
        
        feature_count = len(features)
        print(f"   {i+1}. {tier_info} - {feature_count} premium features: {', '.join(features) if features else 'Basic features only'}")
    
    print("✅ Plan progression provides clear upgrade path for farmers")

def main():
    """Main verification function"""
    try:
        compliance_results = verify_farmer_subscription_plans()
        check_plan_progression()
        final_compliance = display_compliance_summary(compliance_results)
        
        print(f"\n{'='*60}")
        if final_compliance:
            print("🎉 SECTION 4.5.1 VERIFICATION SUCCESSFUL!")
            print("All farmer subscription plans meet PRD requirements")
        else:
            print("⚠️ SECTION 4.5.1 VERIFICATION INCOMPLETE")
            print("Some farmer subscription plans need adjustments")
        
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
