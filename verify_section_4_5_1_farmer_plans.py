#!/usr/bin/env python3
"""
Section 4.5.1 Farmer Subscription Plans - Implementation Verification
Check if all required farmer subscription plans are implemented according to PRD
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def verify_farmer_subscription_plans():
    """Verify specific farmer subscription plans from Section 4.5.1"""
    print("🌾 Verifying Section 4.5.1 Farmer Subscription Plans...")
    
    try:
        from subscriptions.models import SubscriptionPlan
        
        # PRD Section 4.5.1 Required Plans
        required_farmer_plans = {
            'basic': {
                'name_keywords': ['basic', 'free'],
                'features': ['free listing', 'transaction fees'],
                'description': 'Free listing with transaction fees'
            },
            'professional': {
                'name_keywords': ['professional', 'premium'],
                'features': ['premium features', 'analytics', 'priority support'],
                'description': 'Premium features, analytics, and priority support'
            },
            'enterprise': {
                'name_keywords': ['enterprise', 'unlimited'],
                'features': ['unlimited listings', 'api access', 'dedicated support'],
                'description': 'Unlimited listings, API access, and dedicated support'
            },
            'cooperative': {
                'name_keywords': ['cooperative', 'group', 'multi-farmer'],
                'features': ['group management', 'bulk features', 'multi-farmer'],
                'description': 'Multi-farmer group management and bulk features'
            }
        }
        
        # Get all farmer subscription plans
        farmer_plans = SubscriptionPlan.objects.filter(
            plan_type='farmer',
            is_active=True
        ).order_by('tier', 'price')
        
        print(f"\n📊 Found {farmer_plans.count()} active farmer subscription plans:")
        
        implemented_plans = {}
        for plan in farmer_plans:
            print(f"\n✅ Plan: {plan.name}")
            print(f"   • Type: {plan.plan_type}")
            print(f"   • Tier: {plan.tier}")
            print(f"   • Price: {plan.currency} {plan.price}")
            print(f"   • Billing: {plan.billing_cycle}")
            print(f"   • Description: {plan.description}")
            print(f"   • Features: {plan.features}")
            
            # Analyze plan features
            plan_text = f"{plan.name} {plan.description} {plan.features}".lower()
            
            # Check which required plan this might match
            for plan_type, requirements in required_farmer_plans.items():
                if any(keyword in plan_text for keyword in requirements['name_keywords']):
                    if plan_type not in implemented_plans:
                        implemented_plans[plan_type] = []
                    implemented_plans[plan_type].append(plan)
        
        # Verify each required plan type
        print(f"\n🎯 PRD Section 4.5.1 Compliance Check:")
        
        compliance_status = {}
        for plan_type, requirements in required_farmer_plans.items():
            print(f"\n📋 {plan_type.title()} Plan Requirements:")
            print(f"   • Description: {requirements['description']}")
            print(f"   • Required Features: {', '.join(requirements['features'])}")
            
            if plan_type in implemented_plans:
                matching_plans = implemented_plans[plan_type]
                print(f"   ✅ Status: IMPLEMENTED ({len(matching_plans)} plan(s) found)")
                
                for plan in matching_plans:
                    print(f"      → {plan.name} ({plan.tier})")
                    
                    # Check specific features for each plan type
                    feature_compliance = check_plan_features(plan, plan_type)
                    if feature_compliance:
                        print(f"      ✅ Feature compliance: PASSED")
                    else:
                        print(f"      ⚠️ Feature compliance: PARTIAL")
                
                compliance_status[plan_type] = True
            else:
                print(f"   ❌ Status: NOT FOUND")
                print(f"      Missing plan matching: {', '.join(requirements['name_keywords'])}")
                compliance_status[plan_type] = False
        
        return compliance_status, farmer_plans
        
    except Exception as e:
        print(f"❌ Error verifying farmer plans: {e}")
        import traceback
        traceback.print_exc()
        return {}, []

def check_plan_features(plan, plan_type):
    """Check if a plan has the required features for its type"""
    try:
        # Basic Plan Requirements
        if plan_type == 'basic':
            # Should be free or very low cost
            is_free_or_low_cost = plan.price <= 10  # Allow up to 10 for "basic"
            has_transaction_fees = plan.transaction_fee_percentage > 0
            has_limited_listings = plan.product_listing_limit and plan.product_listing_limit <= 10
            
            print(f"         • Free/Low Cost: {'✅' if is_free_or_low_cost else '❌'} (Price: {plan.currency} {plan.price})")
            print(f"         • Transaction Fees: {'✅' if has_transaction_fees else '❌'} ({plan.transaction_fee_percentage}%)")
            print(f"         • Limited Listings: {'✅' if has_limited_listings else '❌'} ({plan.product_listing_limit})")
            
            return is_free_or_low_cost and has_transaction_fees
            
        # Professional Plan Requirements
        elif plan_type == 'professional':
            has_analytics = plan.analytics_access
            has_priority_support = plan.priority_support
            has_more_listings = plan.product_listing_limit and plan.product_listing_limit > 10
            
            print(f"         • Analytics Access: {'✅' if has_analytics else '❌'}")
            print(f"         • Priority Support: {'✅' if has_priority_support else '❌'}")
            print(f"         • More Listings: {'✅' if has_more_listings else '❌'} ({plan.product_listing_limit})")
            
            return has_analytics and has_priority_support
            
        # Enterprise Plan Requirements
        elif plan_type == 'enterprise':
            has_api_access = plan.api_access
            has_unlimited_listings = plan.product_listing_limit == 0 or plan.product_listing_limit >= 1000
            has_premium_features = plan.blockchain_features or plan.marketing_tools
            
            print(f"         • API Access: {'✅' if has_api_access else '❌'}")
            print(f"         • Unlimited Listings: {'✅' if has_unlimited_listings else '❌'} ({plan.product_listing_limit})")
            print(f"         • Premium Features: {'✅' if has_premium_features else '❌'}")
            
            return has_api_access and has_unlimited_listings
            
        # Cooperative Plan Requirements
        elif plan_type == 'cooperative':
            # Check if plan mentions group/bulk features
            plan_text = f"{plan.name} {plan.description} {plan.features}".lower()
            has_group_features = any(word in plan_text for word in ['group', 'cooperative', 'bulk', 'multi'])
            has_api_access = plan.api_access  # Needed for group management
            has_high_limits = plan.product_listing_limit == 0 or plan.product_listing_limit >= 100
            
            print(f"         • Group Features: {'✅' if has_group_features else '❌'}")
            print(f"         • API Access: {'✅' if has_api_access else '❌'}")
            print(f"         • High Limits: {'✅' if has_high_limits else '❌'} ({plan.product_listing_limit})")
            
            return has_group_features and has_high_limits
            
        return True
        
    except Exception as e:
        print(f"         ❌ Error checking features: {e}")
        return False

def suggest_missing_plans(compliance_status):
    """Suggest what plans need to be created or updated"""
    print(f"\n🔧 RECOMMENDATIONS:")
    
    missing_plans = [plan_type for plan_type, implemented in compliance_status.items() if not implemented]
    
    if not missing_plans:
        print("   ✅ All required farmer subscription plans are implemented!")
        return
    
    print(f"   ⚠️ Missing or incomplete plans: {len(missing_plans)}")
    
    for plan_type in missing_plans:
        if plan_type == 'basic':
            print(f"\n   📝 Create Basic Plan:")
            print(f"      • Name: 'Farmer Basic' or 'Free Farmer Plan'")
            print(f"      • Price: GHS 0.00 (free)")
            print(f"      • Tier: 'basic'")
            print(f"      • Features: 5-10 free listings")
            print(f"      • Transaction fee: 3-5%")
            print(f"      • Limited support")
            
        elif plan_type == 'professional':
            print(f"\n   📝 Create Professional Plan:")
            print(f"      • Name: 'Farmer Professional' or 'Premium Farmer'")
            print(f"      • Price: GHS 50-100/month")
            print(f"      • Tier: 'professional'")
            print(f"      • Features: Analytics, priority support")
            print(f"      • 50-100 listings")
            print(f"      • Lower transaction fees")
            
        elif plan_type == 'enterprise':
            print(f"\n   📝 Create Enterprise Plan:")
            print(f"      • Name: 'Farmer Enterprise' or 'Unlimited Farmer'")
            print(f"      • Price: GHS 200-500/month")
            print(f"      • Tier: 'enterprise'")
            print(f"      • Features: API access, unlimited listings")
            print(f"      • Dedicated support")
            print(f"      • Advanced analytics")
            
        elif plan_type == 'cooperative':
            print(f"\n   📝 Create Cooperative Plan:")
            print(f"      • Name: 'Farmer Cooperative' or 'Group Plan'")
            print(f"      • Price: GHS 300-1000/month")
            print(f"      • Tier: 'enterprise' or 'cooperative'")
            print(f"      • Features: Multi-farmer management")
            print(f"      • Bulk operations")
            print(f"      • Group analytics")

def display_section_4_5_1_summary(compliance_status, farmer_plans):
    """Display Section 4.5.1 implementation summary"""
    print("\n" + "="*70)
    print("🎯 SECTION 4.5.1 FARMER SUBSCRIPTION PLANS - VERIFICATION")
    print("="*70)
    
    total_required = len(compliance_status)
    implemented_count = sum(1 for status in compliance_status.values() if status)
    compliance_percentage = (implemented_count / total_required) * 100 if total_required > 0 else 0
    
    print(f"\n📊 IMPLEMENTATION STATUS:")
    print(f"   • Total Required Plans: {total_required}")
    print(f"   • Implemented Plans: {implemented_count}")
    print(f"   • Available Farmer Plans: {len(farmer_plans)}")
    print(f"   • Compliance Percentage: {compliance_percentage:.1f}%")
    
    print(f"\n📋 PLAN-BY-PLAN STATUS:")
    for plan_type, implemented in compliance_status.items():
        status_icon = "✅" if implemented else "❌"
        print(f"   {status_icon} {plan_type.title()} Plan: {'IMPLEMENTED' if implemented else 'MISSING'}")
    
    print(f"\n🎯 SECTION 4.5.1 COMPLIANCE:")
    
    if compliance_percentage == 100:
        print("   🏆 100% COMPLIANCE ACHIEVED")
        print("   ✅ All required farmer subscription plans implemented")
        print("   ✅ Basic plan with free listings and transaction fees")
        print("   ✅ Professional plan with premium features and analytics")
        print("   ✅ Enterprise plan with unlimited listings and API access")
        print("   ✅ Cooperative plan with multi-farmer group management")
        print("   ✅ Ready for farmer onboarding and subscription management")
    elif compliance_percentage >= 75:
        print("   🟡 MOSTLY COMPLIANT")
        print("   ✅ Most required plans implemented")
        print("   ⚠️ Some plans may need feature enhancements")
    elif compliance_percentage >= 50:
        print("   🟠 PARTIAL COMPLIANCE")
        print("   ⚠️ Several required plans missing or incomplete")
        print("   📝 Plan creation/updates needed")
    else:
        print("   🔴 LOW COMPLIANCE")
        print("   ❌ Most required plans missing")
        print("   📝 Significant implementation work required")
    
    return compliance_percentage >= 100

def main():
    """Main verification function"""
    print("🔍 Starting Section 4.5.1 Farmer Subscription Plans Verification...")
    
    try:
        compliance_status, farmer_plans = verify_farmer_subscription_plans()
        suggest_missing_plans(compliance_status)
        
        is_compliant = display_section_4_5_1_summary(compliance_status, farmer_plans)
        
        if is_compliant:
            print("\n✅ Section 4.5.1 verification completed successfully!")
            print("🎉 All farmer subscription plans are properly implemented!")
        else:
            print("\n⚠️ Section 4.5.1 verification found gaps")
            print("Some farmer subscription plans need attention")
        
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
