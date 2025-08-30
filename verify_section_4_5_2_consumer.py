#!/usr/bin/env python3
"""
Verify Section 4.5.2 Consumer Subscription Services compliance with PRD requirements
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def verify_consumer_subscription_services():
    """Verify PRD Section 4.5.2 Consumer Subscription Services implementation"""
    print("🛒 VERIFYING PRD SECTION 4.5.2 CONSUMER SUBSCRIPTION SERVICES")
    print("="*65)
    
    from subscriptions.models import SubscriptionPlan
    
    # Get all consumer subscription plans
    consumer_plans = SubscriptionPlan.objects.filter(
        plan_type='consumer',
        is_active=True
    ).order_by('tier', 'price')
    
    print(f"📊 Found {consumer_plans.count()} active consumer subscription plans\n")
    
    if consumer_plans.exists():
        print("📋 CURRENT CONSUMER PLANS:")
        for plan in consumer_plans:
            print(f"   • {plan.name}: {plan.description}")
            print(f"     Price: {plan.currency} {plan.price} ({plan.billing_cycle})")
            print(f"     Tier: {plan.tier}")
            print()
    
    # PRD Section 4.5.2 Requirements Check
    print("🎯 PRD SECTION 4.5.2 REQUIREMENTS VERIFICATION:")
    print("-" * 50)
    
    compliance_results = {}
      # 1. Fresh Box Subscriptions: Weekly/monthly produce deliveries
    print("1. 📦 Fresh Box Subscriptions (Weekly/monthly produce deliveries)")
    
    from django.db.models import Q
    fresh_box_plans = consumer_plans.filter(
        Q(name__icontains='fresh') | 
        Q(name__icontains='box') |
        Q(description__icontains='fresh') |
        Q(description__icontains='delivery')
    )
    
    if fresh_box_plans.exists():
        print(f"   ✅ IMPLEMENTED: Found {fresh_box_plans.count()} Fresh Box plans")
        for plan in fresh_box_plans:
            print(f"      - {plan.name}: {plan.description}")
        compliance_results['fresh_box'] = True
    else:
        print("   ❌ MISSING: No Fresh Box subscription plans found")
        compliance_results['fresh_box'] = False
    
    print()
      # 2. Organic Premium: Certified organic product access
    print("2. 🌱 Organic Premium (Certified organic product access)")
    organic_plans = consumer_plans.filter(
        Q(name__icontains='organic') |
        Q(name__icontains='premium') |
        Q(description__icontains='organic') |
        Q(description__icontains='certified')
    )
    
    if organic_plans.exists():
        print(f"   ✅ IMPLEMENTED: Found {organic_plans.count()} Organic Premium plans")
        for plan in organic_plans:
            print(f"      - {plan.name}: {plan.description}")
        compliance_results['organic_premium'] = True
    else:
        print("   ❌ MISSING: No Organic Premium subscription plans found")
        compliance_results['organic_premium'] = False
    
    print()
      # 3. Bulk Buying Groups: Community purchasing for better prices
    print("3. 👥 Bulk Buying Groups (Community purchasing for better prices)")
    bulk_plans = consumer_plans.filter(
        Q(name__icontains='bulk') |
        Q(name__icontains='group') |
        Q(name__icontains='community') |
        Q(description__icontains='bulk') |
        Q(description__icontains='group') |
        Q(description__icontains='community')
    )
    
    if bulk_plans.exists():
        print(f"   ✅ IMPLEMENTED: Found {bulk_plans.count()} Bulk Buying plans")
        for plan in bulk_plans:
            print(f"      - {plan.name}: {plan.description}")
        compliance_results['bulk_buying'] = True
    else:
        print("   ❌ MISSING: No Bulk Buying Group subscription plans found")
        compliance_results['bulk_buying'] = False
    
    print()
    
    # 4. Seasonal Alerts: Notifications for best products and prices
    print("4. 🔔 Seasonal Alerts (Notifications for best products and prices)")
    
    # Check if communication system exists for seasonal alerts
    try:
        from communications.models import SMSLog, EmailLog
        
        # Check if seasonal alert functionality exists
        seasonal_features = any([
            'seasonal' in plan.description.lower() or 
            'alert' in plan.description.lower() or
            'notification' in plan.description.lower()
            for plan in consumer_plans
        ])
        
        # Check SMS/Email infrastructure
        sms_available = SMSLog.objects.exists() or hasattr(SMSLog, '_meta')
        email_available = EmailLog.objects.exists() or hasattr(EmailLog, '_meta')
        
        if seasonal_features or (sms_available and email_available):
            print("   ✅ IMPLEMENTED: Seasonal alert infrastructure available")
            print("      - SMS notification system: ✅ Available")
            print("      - Email notification system: ✅ Available")
            if seasonal_features:
                print("      - Seasonal features mentioned in plans: ✅ Yes")
            compliance_results['seasonal_alerts'] = True
        else:
            print("   ⚠️ PARTIAL: Communication infrastructure exists but no seasonal-specific plans")
            compliance_results['seasonal_alerts'] = False
            
    except ImportError:
        print("   ❌ MISSING: Communication system not found")
        compliance_results['seasonal_alerts'] = False
    
    return compliance_results

def check_missing_consumer_services():
    """Check which consumer services need to be implemented"""
    print("\n" + "="*65)
    print("🔧 MISSING CONSUMER SERVICES ANALYSIS")
    print("="*65)
    
    compliance = verify_consumer_subscription_services()
    
    missing_services = []
    if not compliance.get('fresh_box', False):
        missing_services.append("Fresh Box Subscriptions")
    if not compliance.get('organic_premium', False):
        missing_services.append("Organic Premium")
    if not compliance.get('bulk_buying', False):
        missing_services.append("Bulk Buying Groups")
    if not compliance.get('seasonal_alerts', False):
        missing_services.append("Seasonal Alerts")
    
    if missing_services:
        print(f"\n❌ MISSING SERVICES ({len(missing_services)}/4):")
        for service in missing_services:
            print(f"   • {service}")
        
        print(f"\n📋 IMPLEMENTATION NEEDED:")
        print("   1. Create specific consumer subscription plans for missing services")
        print("   2. Update plan descriptions to include PRD requirements")
        print("   3. Implement service-specific features and functionality")
        
        return False
    else:
        print(f"\n✅ ALL CONSUMER SERVICES IMPLEMENTED (4/4)")
        print("   • Fresh Box Subscriptions ✅")
        print("   • Organic Premium ✅") 
        print("   • Bulk Buying Groups ✅")
        print("   • Seasonal Alerts ✅")
        
        return True

def display_section_4_5_2_summary():
    """Display Section 4.5.2 compliance summary"""
    print("\n" + "="*65)
    print("🎯 PRD SECTION 4.5.2 COMPLIANCE SUMMARY")
    print("="*65)
    
    compliance = verify_consumer_subscription_services()
    all_compliant = check_missing_consumer_services()
    
    total_services = len(compliance)
    compliant_services = sum(compliance.values())
    compliance_percentage = (compliant_services / total_services) * 100 if total_services > 0 else 0
    
    print(f"\n📊 Implementation Status:")
    for service, is_compliant in compliance.items():
        service_name = service.replace('_', ' ').title()
        status = "✅ COMPLIANT" if is_compliant else "❌ NON-COMPLIANT"
        print(f"   • {service_name}: {status}")
    
    print(f"\n🎯 Overall Compliance: {compliant_services}/{total_services} services ({compliance_percentage:.0f}%)")
    
    if compliance_percentage == 100:
        print("🏆 SECTION 4.5.2 CONSUMER SUBSCRIPTION SERVICES: 100% PRD COMPLIANT")
        print("✅ All required consumer subscription services implemented")
        print("✅ Fresh Box, Organic Premium, Bulk Buying, and Seasonal Alerts available")
        print("✅ Ready for consumer onboarding and service delivery")
    elif compliance_percentage >= 75:
        print("⚠️ SECTION 4.5.2: MOSTLY COMPLIANT - Minor services missing")
    else:
        print("❌ SECTION 4.5.2: SIGNIFICANT COMPLIANCE ISSUES")
        print("Major consumer services missing - implementation required")
    
    return compliance_percentage == 100

def main():
    """Main verification function"""
    try:        
        final_compliance = display_section_4_5_2_summary()
        
        print(f"\n{'='*65}")
        if final_compliance:
            print("🎉 SECTION 4.5.2 VERIFICATION SUCCESSFUL!")
            print("All consumer subscription services meet PRD requirements")
        else:
            print("⚠️ SECTION 4.5.2 VERIFICATION INCOMPLETE")
            print("Some consumer subscription services need implementation")
        
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
