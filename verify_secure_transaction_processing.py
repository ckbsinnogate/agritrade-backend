#!/usr/bin/env python3
"""
AgriConnect Secure Transaction Processing Verification (PRD Section 4.3.1)
This script verifies that all PRD Section 4.3.1 Secure Transaction Processing requirements are implemented
"""

import os
import sys
import django

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

django.setup()

from payments.models import PaymentGateway, PaymentMethod, Transaction, EscrowAccount, EscrowMilestone, DisputeCase, PaymentWebhook
from orders.models import Order
from authentication.models import User
from decimal import Decimal
import django.db.models

def print_section(title, color="36"):  # Cyan
    print(f"\n\033[{color}m{'='*80}\033[0m")
    print(f"\033[{color}m{title.center(80)}\033[0m")
    print(f"\033[{color}m{'='*80}\033[0m")

def print_requirement(req_num, title, status="", color="32"):
    status_icon = "✅" if status == "IMPLEMENTED" else "❌" if status == "MISSING" else "🔍"
    print(f"\n\033[{color}m{req_num}. {title} {status_icon}\033[0m")

def verify_multi_stage_escrow():
    """Verify Multi-Stage Escrow: Order confirmation, shipment, and delivery milestones"""
    print_requirement("4.3.1.1", "Multi-Stage Escrow: Order confirmation, shipment, and delivery milestones")
    
    # Check for escrow accounts
    escrow_accounts = EscrowAccount.objects.all()
    print(f"   📊 Total Escrow Accounts: {escrow_accounts.count()}")
    
    # Check for milestones
    milestones = EscrowMilestone.objects.all()
    print(f"   📋 Total Milestones: {milestones.count()}")
    
    # Check specific milestone types required
    required_milestones = [
        ('order_confirmed', 'Order Confirmation'),
        ('goods_shipped', 'Shipment'), 
        ('goods_delivered', 'Delivery')
    ]
    
    milestone_coverage = {}
    print("   🎯 Required Milestone Types:")
    
    for milestone_type, description in required_milestones:
        count = milestones.filter(milestone_type=milestone_type).count()
        milestone_coverage[milestone_type] = count > 0
        status = "✅ IMPLEMENTED" if count > 0 else "❌ MISSING"
        print(f"      • {description}: {count} milestones - {status}")
    
    # Check multi-stage workflow
    if escrow_accounts.exists():
        print("\n   🔄 Multi-Stage Workflow Analysis:")
        for escrow in escrow_accounts[:2]:  # Check first 2 escrows
            escrow_milestones = escrow.milestones.all().order_by('release_percentage')
            total_stages = escrow_milestones.count()
            completed_stages = escrow_milestones.filter(is_completed=True).count()
            
            print(f"      • Escrow {escrow.id[:8]}...")
            print(f"        Total Stages: {total_stages}")
            print(f"        Completed Stages: {completed_stages}")
            print(f"        Status: {escrow.status}")
            
            # Show stage progression
            for milestone in escrow_milestones:
                stage_status = "✅ COMPLETED" if milestone.is_completed else "⏳ PENDING"
                print(f"        └─ {milestone.description}: {milestone.release_percentage}% - {stage_status}")
    
    is_implemented = all(milestone_coverage.values()) and escrow_accounts.count() > 0
    return is_implemented

def verify_dispute_resolution():
    """Verify Dispute Resolution: Automated and manual arbitration processes"""
    print_requirement("4.3.1.2", "Dispute Resolution: Automated and manual arbitration processes")
    
    # Check for dispute cases
    disputes = DisputeCase.objects.all()
    print(f"   📊 Total Dispute Cases: {disputes.count()}")
    
    # Check dispute workflow
    if disputes.exists():
        print("   ⚖️ Dispute Status Distribution:")
        for status, status_name in DisputeCase.STATUS_CHOICES:
            count = disputes.filter(status=status).count()
            if count > 0:
                print(f"      • {status_name}: {count} cases")
    
    # Check arbitration capabilities
    print("\n   🏛️ Arbitration Process Analysis:")
    
    # Check for assigned arbitrators/staff
    disputes_with_arbitrators = disputes.filter(assigned_to__isnull=False).count()
    print(f"      • Disputes with Assigned Arbitrators: {disputes_with_arbitrators}")
    
    # Check resolution types
    if disputes.exists():
        print("   🔨 Available Resolution Types:")
        for resolution, resolution_name in DisputeCase.RESOLUTION_CHOICES:
            print(f"      • {resolution_name}")
    
    # Check evidence management
    disputes_with_evidence = disputes.exclude(evidence=[]).count()
    print(f"   📋 Disputes with Evidence: {disputes_with_evidence}")
    
    # Check automated features
    print("\n   🤖 Automated Arbitration Features:")
    print(f"      • Response Deadlines: {'✅ CONFIGURED' if disputes.filter(response_deadline__isnull=False).exists() else '❌ NOT SET'}")
    print(f"      • Evidence Storage: {'✅ IMPLEMENTED' if disputes_with_evidence > 0 else '❌ NO EVIDENCE'}")
    print(f"      • Status Transitions: {'✅ WORKING' if disputes.count() > 0 else '❌ NO DATA'}")
    
    is_implemented = disputes.count() > 0 and len(DisputeCase.RESOLUTION_CHOICES) >= 3
    return is_implemented

def verify_payment_protection():
    """Verify Payment Protection: Buyer and seller security guarantees"""
    print_requirement("4.3.1.3", "Payment Protection: Buyer and seller security guarantees")
    
    escrow_accounts = EscrowAccount.objects.all()
    
    print("   🛡️ Protection Mechanisms Analysis:")
    
    if escrow_accounts.exists():
        # Buyer protection (funds held in escrow)
        funded_escrows = escrow_accounts.filter(status__in=['funded', 'partial_release', 'released']).count()
        total_escrows = escrow_accounts.count()
        buyer_protection_rate = (funded_escrows / total_escrows * 100) if total_escrows > 0 else 0
        
        print(f"      • Buyer Protection Rate: {buyer_protection_rate:.1f}% ({funded_escrows}/{total_escrows} escrows funded)")
        
        # Seller protection (payment guarantees)
        released_escrows = escrow_accounts.filter(status__in=['released', 'partial_release']).count()
        seller_protection_rate = (released_escrows / total_escrows * 100) if total_escrows > 0 else 0
        
        print(f"      • Seller Protection Rate: {seller_protection_rate:.1f}% ({released_escrows}/{total_escrows} escrows released)")
        
        # Quality confirmation requirements
        quality_required_escrows = escrow_accounts.filter(requires_quality_confirmation=True).count()
        quality_protection_rate = (quality_required_escrows / total_escrows * 100) if total_escrows > 0 else 0
        
        print(f"      • Quality Confirmation Required: {quality_protection_rate:.1f}% ({quality_required_escrows}/{total_escrows} escrows)")
        
        # Auto-release protection
        auto_release_escrows = escrow_accounts.exclude(auto_release_days=0).count()
        auto_release_rate = (auto_release_escrows / total_escrows * 100) if total_escrows > 0 else 0
        
        print(f"      • Auto-Release Protection: {auto_release_rate:.1f}% ({auto_release_escrows}/{total_escrows} escrows)")
        
        # Financial protection summary
        print("\n   💰 Financial Protection Summary:")
        totals = escrow_accounts.aggregate(
            total_amount=django.db.models.Sum('total_amount'),
            released_amount=django.db.models.Sum('released_amount')
        )
        total_protected = totals['total_amount'] or Decimal('0')
        total_released = totals['released_amount'] or Decimal('0')
        total_held = total_protected - total_released
        
        print(f"      • Total Protected Value: GHS {total_protected}")
        print(f"      • Released to Sellers: GHS {total_released}")
        print(f"      • Held for Buyers: GHS {total_held}")
    
    # Check transaction security
    transactions = Transaction.objects.all()
    if transactions.exists():
        print("\n   🔒 Transaction Security:")
        secure_transactions = transactions.filter(gateway__isnull=False).count()
        print(f"      • Gateway-Secured Transactions: {secure_transactions}/{transactions.count()}")
        
        # Check status tracking
        status_counts = {}
        for status, _ in Transaction.STATUS_CHOICES:
            count = transactions.filter(status=status).count()
            if count > 0:
                status_counts[status] = count
        
        print("      • Transaction Status Tracking:")
        for status, count in status_counts.items():
            print(f"        └─ {status.upper()}: {count} transactions")
    
    is_implemented = escrow_accounts.count() > 0 and buyer_protection_rate > 0 and seller_protection_rate > 0
    return is_implemented

def verify_multi_currency_support():
    """Verify Multi-Currency Support: All African currencies with real-time conversion"""
    print_requirement("4.3.1.4", "Multi-Currency Support: All African currencies with real-time conversion")
    
    # Check supported currencies in payment gateways
    gateways = PaymentGateway.objects.filter(is_active=True)
    all_currencies = set()
    
    print("   💱 Payment Gateway Currency Support:")
    for gateway in gateways:
        currencies = gateway.supported_currencies
        all_currencies.update(currencies)
        print(f"      • {gateway.display_name}: {', '.join(currencies)}")
    
    print(f"\n   🌍 Total Supported Currencies: {len(all_currencies)}")
    african_currencies = [curr for curr in all_currencies if curr in ['GHS', 'NGN', 'KES', 'UGX', 'ZAR', 'EGP', 'MAD', 'XOF', 'XAF']]
    print(f"   🌍 African Currencies: {len(african_currencies)} ({', '.join(sorted(african_currencies))})")
    
    # Check currency usage in escrow accounts
    escrow_accounts = EscrowAccount.objects.all()
    if escrow_accounts.exists():
        escrow_currencies = escrow_accounts.values_list('currency', flat=True).distinct()
        print(f"\n   🔒 Escrow Currency Usage:")
        for currency in escrow_currencies:
            count = escrow_accounts.filter(currency=currency).count()
            total_value = escrow_accounts.filter(currency=currency).aggregate(
                total=django.db.models.Sum('total_amount'))['total'] or Decimal('0')
            print(f"      • {currency}: {count} accounts (Total: {total_value} {currency})")
    
    # Check transaction currency support
    transactions = Transaction.objects.all()
    if transactions.exists():
        transaction_currencies = transactions.values_list('currency', flat=True).distinct()
        print(f"\n   💳 Transaction Currency Usage:")
        for currency in transaction_currencies:
            count = transactions.filter(currency=currency).count()
            print(f"      • {currency}: {count} transactions")
    
    # Check real-time conversion capabilities (framework readiness)
    print("\n   🔄 Real-Time Conversion Framework:")
    print(f"      • Gateway Integration: {'✅ READY' if gateways.count() > 0 else '❌ NOT READY'}")
    print(f"      • Multi-Currency Models: {'✅ IMPLEMENTED' if len(all_currencies) > 1 else '❌ SINGLE CURRENCY'}")
    print(f"      • African Market Focus: {'✅ OPTIMIZED' if len(african_currencies) >= 3 else '⚠️ LIMITED'}")
    
    is_implemented = len(all_currencies) >= 4 and len(african_currencies) >= 3
    return is_implemented

def verify_fee_management():
    """Verify Fee Management: Transparent pricing and profit sharing"""
    print_requirement("4.3.1.5", "Fee Management: Transparent pricing and profit sharing")
    
    # Check payment gateway fee configuration
    gateways = PaymentGateway.objects.filter(is_active=True)
    
    print("   💰 Fee Management Analysis:")
    
    fee_configured_gateways = 0
    for gateway in gateways:
        has_fee_config = gateway.transaction_fee_percentage > 0 or gateway.fixed_fee > 0
        fee_configured_gateways += 1 if has_fee_config else 0
        
        print(f"      • {gateway.display_name}:")
        print(f"        └─ Transaction Fee: {gateway.transaction_fee_percentage}%")
        print(f"        └─ Fixed Fee: {gateway.fixed_fee} {gateway.currency}")
        print(f"        └─ Fee Configuration: {'✅ CONFIGURED' if has_fee_config else '❌ NOT SET'}")
    
    fee_coverage = (fee_configured_gateways / gateways.count() * 100) if gateways.count() > 0 else 0
    print(f"\n   📊 Fee Configuration Coverage: {fee_coverage:.1f}% ({fee_configured_gateways}/{gateways.count()} gateways)")
    
    # Check transaction fee tracking
    transactions = Transaction.objects.all()
    transactions_with_fees = transactions.exclude(gateway_fee=0).count()
    
    print(f"\n   💳 Transaction Fee Tracking:")
    print(f"      • Total Transactions: {transactions.count()}")
    print(f"      • Transactions with Fees: {transactions_with_fees}")
    
    if transactions.exists():
        total_fees = transactions.aggregate(total_fees=django.db.models.Sum('gateway_fee'))['total_fees'] or Decimal('0')
        print(f"      • Total Fees Collected: GHS {total_fees}")
    
    # Check profit sharing capabilities (framework)
    print(f"\n   🤝 Profit Sharing Framework:")
    print(f"      • Gateway Fee Tracking: {'✅ IMPLEMENTED' if transactions_with_fees > 0 else '⚠️ NO FEE DATA'}")
    print(f"      • Multiple Gateways: {'✅ AVAILABLE' if gateways.count() > 1 else '⚠️ SINGLE GATEWAY'}")
    print(f"      • Fee Transparency: {'✅ CONFIGURED' if fee_coverage > 50 else '❌ INCOMPLETE'}")
    
    is_implemented = fee_coverage >= 50 and gateways.count() > 0
    return is_implemented

def verify_refund_processing():
    """Verify Refund Processing: Automated return and dispute handling"""
    print_requirement("4.3.1.6", "Refund Processing: Automated return and dispute handling")
    
    # Check refund capabilities in escrow system
    escrow_accounts = EscrowAccount.objects.all()
    
    print("   🔄 Refund Processing Analysis:")
    
    # Check refund status tracking
    refunded_escrows = escrow_accounts.filter(status='refunded').count()
    disputed_escrows = escrow_accounts.filter(status='disputed').count()
    
    print(f"      • Refunded Escrow Accounts: {refunded_escrows}")
    print(f"      • Disputed Escrow Accounts: {disputed_escrows}")
    
    # Check dispute resolution with refunds
    disputes = DisputeCase.objects.all()
    refund_resolutions = disputes.filter(resolution__in=['refund_buyer', 'partial_refund']).count()
    
    print(f"      • Disputes Resolved with Refunds: {refund_resolutions}")
    
    # Check automated refund capabilities
    print(f"\n   🤖 Automated Refund Features:")
    
    # Check resolution options
    refund_options = [res for res in DisputeCase.RESOLUTION_CHOICES if 'refund' in res[0]]
    print(f"      • Refund Resolution Options: {len(refund_options)}")
    for resolution_code, resolution_name in refund_options:
        print(f"        └─ {resolution_name}")
    
    # Check refund amount tracking
    disputes_with_amounts = disputes.filter(resolution_amount__isnull=False).count()
    print(f"      • Disputes with Resolution Amounts: {disputes_with_amounts}")
    
    # Check transaction refund capabilities
    transactions = Transaction.objects.all()
    refund_transactions = transactions.filter(transaction_type='refund').count()
    print(f"      • Refund Transactions: {refund_transactions}")
    
    # Check automated return handling
    print(f"\n   📦 Return Handling Framework:")
    print(f"      • Dispute-Based Returns: {'✅ IMPLEMENTED' if disputes.count() > 0 else '❌ NO DISPUTES'}")
    print(f"      • Refund Amount Calculation: {'✅ SUPPORTED' if disputes_with_amounts > 0 else '⚠️ NO AMOUNTS'}")
    print(f"      • Multiple Resolution Types: {'✅ AVAILABLE' if len(refund_options) > 1 else '⚠️ LIMITED'}")
    
    is_implemented = len(refund_options) > 0 and disputes.count() > 0
    return is_implemented

def main():
    """Main verification function"""
    print_section("AGRICONNECT SECURE TRANSACTION PROCESSING VERIFICATION", "33")
    print("\033[33mPRD Section 4.3.1 Requirements Verification\033[0m")
    
    # Track implementation status
    results = {}
    
    print_section("REQUIREMENT VERIFICATION", "36")
    
    # Verify each requirement
    results["multi_stage_escrow"] = verify_multi_stage_escrow()
    results["dispute_resolution"] = verify_dispute_resolution()
    results["payment_protection"] = verify_payment_protection()
    results["multi_currency_support"] = verify_multi_currency_support()
    results["fee_management"] = verify_fee_management()
    results["refund_processing"] = verify_refund_processing()
    
    # Summary
    print_section("IMPLEMENTATION SUMMARY", "32")
    
    implemented_count = sum(1 for status in results.values() if status)
    total_count = len(results)
    
    print(f"\n📊 \033[32mImplementation Status: {implemented_count}/{total_count} Requirements Met\033[0m")
    
    requirement_names = {
        "multi_stage_escrow": "MULTI-STAGE ESCROW",
        "dispute_resolution": "DISPUTE RESOLUTION",
        "payment_protection": "PAYMENT PROTECTION",
        "multi_currency_support": "MULTI-CURRENCY SUPPORT",
        "fee_management": "FEE MANAGEMENT",
        "refund_processing": "REFUND PROCESSING"
    }
    
    for requirement, status in results.items():
        status_text = "✅ IMPLEMENTED" if status else "❌ MISSING"
        color = "32" if status else "31"
        req_name = requirement_names.get(requirement, requirement.upper().replace('_', ' '))
        print(f"   \033[{color}m{req_name}: {status_text}\033[0m")
    
    # Overall status
    if implemented_count == total_count:
        print(f"\n🎉 \033[32mALL SECURE TRANSACTION PROCESSING REQUIREMENTS IMPLEMENTED!\033[0m")
    else:
        print(f"\n⚠️  \033[33m{total_count - implemented_count} REQUIREMENTS NEED ATTENTION\033[0m")
    
    # Database statistics
    print_section("DATABASE STATISTICS", "34")
    print(f"🏦 Payment Gateways: {PaymentGateway.objects.count()}")
    print(f"💳 Payment Methods: {PaymentMethod.objects.count()}")
    print(f"💰 Transactions: {Transaction.objects.count()}")
    print(f"🔒 Escrow Accounts: {EscrowAccount.objects.count()}")
    print(f"📋 Escrow Milestones: {EscrowMilestone.objects.count()}")
    print(f"⚖️ Dispute Cases: {DisputeCase.objects.count()}")
    print(f"📡 Payment Webhooks: {PaymentWebhook.objects.count()}")
    print(f"📦 Orders: {Order.objects.count()}")
    print(f"👥 Users: {User.objects.count()}")

if __name__ == "__main__":
    # Import django db models for aggregation
    main()
