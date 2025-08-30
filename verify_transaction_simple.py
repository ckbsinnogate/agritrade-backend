#!/usr/bin/env python3
"""
AgriConnect Secure Transaction Processing Verification - Simplified
Section 4.3.1 Detailed Requirements Check
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db.models import Sum, Count, Avg, Q
from payments.models import (
    EscrowAccount, EscrowMilestone, DisputeCase, 
    PaymentGateway, Transaction, PaymentMethod, PaymentWebhook
)

def main():
    print("🚀 AgriConnect Secure Transaction Processing Verification")
    print("📋 Section 4.3.1 - Detailed Requirements Analysis")
    print("="*70)
    
    # 4.3.1.1 Multi-Stage Escrow
    print("\n1️⃣ MULTI-STAGE ESCROW SYSTEM")
    try:
        escrow_accounts = EscrowAccount.objects.all()
        milestones = EscrowMilestone.objects.all()
        
        print(f"   📊 Escrow Accounts: {escrow_accounts.count()}")
        print(f"   📊 Total Milestones: {milestones.count()}")
        
        if milestones.exists():
            milestone_types = milestones.values('milestone_type').annotate(count=Count('id'))
            print("   🔄 Milestone Types:")
            for mt in milestone_types:
                print(f"      • {mt['milestone_type']}: {mt['count']} milestones")
        
        result_1 = milestones.count() > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_1 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_1 = False
    
    # 4.3.1.2 Dispute Resolution
    print("\n2️⃣ DISPUTE RESOLUTION SYSTEM")
    try:
        disputes = DisputeCase.objects.all()
        print(f"   📊 Total Disputes: {disputes.count()}")
        
        if disputes.exists():
            dispute_statuses = disputes.values('status').annotate(count=Count('id'))
            print("   ⚖️ Dispute Statuses:")
            for ds in dispute_statuses:
                print(f"      • {ds['status']}: {ds['count']} disputes")
        
        result_2 = disputes.count() > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_2 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_2 = False
      # 4.3.1.3 Payment Protection
    print("\n3️⃣ PAYMENT PROTECTION SYSTEM")
    try:
        total_escrow = escrow_accounts.aggregate(total=Sum('total_amount'))['total'] or 0
        released_amount = escrow_accounts.aggregate(released=Sum('released_amount'))['released'] or 0
        protected_amount = total_escrow - released_amount
        
        print(f"   💰 Total Escrow: {total_escrow}")
        print(f"   💸 Released: {released_amount}")
        print(f"   🛡️ Protected: {protected_amount}")
        
        result_3 = total_escrow > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_3 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_3 = False
      # 4.3.1.4 Multi-Currency Support
    print("\n4️⃣ MULTI-CURRENCY SUPPORT")
    try:
        gateways = PaymentGateway.objects.all()
        transactions = Transaction.objects.all()
        
        print(f"   💳 Payment Gateways: {gateways.count()}")
        print(f"   💱 Multi-Currency Transactions: {transactions.count()}")
        
        if gateways.exists():
            # Check supported currencies across gateways
            all_currencies = set()
            for gateway in gateways:
                if gateway.supported_currencies:
                    all_currencies.update(gateway.supported_currencies)
            
            print(f"   🌍 Supported Currencies: {len(all_currencies)}")
            for currency in sorted(all_currencies):
                print(f"      • {currency}")
            
            # Check African currencies
            african_currencies = {'GHS', 'NGN', 'KES', 'UGX', 'ZAR'}.intersection(all_currencies)
            print(f"   🌍 African Currencies: {len(african_currencies)} - {list(african_currencies)}")
            
            # Check transaction currencies
            if transactions.exists():
                transaction_currencies = transactions.values('currency').distinct()
                print(f"   📊 Currencies in Use: {transaction_currencies.count()}")
                for tc in transaction_currencies:
                    count = transactions.filter(currency=tc['currency']).count()
                    print(f"      • {tc['currency']}: {count} transactions")
        
        result_4 = len(all_currencies) >= 3 and gateways.count() > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_4 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_4 = False
      # 4.3.1.5 Fee Management
    print("\n5️⃣ FEE MANAGEMENT SYSTEM")
    try:
        gateways = PaymentGateway.objects.all()
        transactions = Transaction.objects.all()
        
        print(f"   💼 Payment Gateways: {gateways.count()}")
        
        if gateways.exists():
            # Check gateway fee configuration
            fee_configured = 0
            for gateway in gateways:
                has_fee = (
                    hasattr(gateway, 'transaction_fee_percentage') and gateway.transaction_fee_percentage > 0
                ) or (
                    hasattr(gateway, 'fixed_fee') and gateway.fixed_fee > 0
                )
                if has_fee:
                    fee_configured += 1
                print(f"      • {gateway.display_name}: Fee config available")
            
            print(f"   🔍 Gateways with Fee Config: {fee_configured}")
            
            # Check transaction metadata for fee tracking
            if transactions.exists():
                transactions_with_metadata = transactions.exclude(metadata={}).count()
                print(f"   📊 Transactions with Metadata: {transactions_with_metadata}")
                
                # Check for gateway fees in transactions
                total_transactions = transactions.count()
                print(f"   💳 Total Transactions: {total_transactions}")
        
        result_5 = gateways.count() > 0 and fee_configured > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_5 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_5 = False
      # 4.3.1.6 Refund Processing
    print("\n6️⃣ REFUND PROCESSING SYSTEM")
    try:
        transactions = Transaction.objects.all()
        refund_transactions = transactions.filter(
            Q(transaction_type='refund') | Q(status='refunded')
        )
        disputes = DisputeCase.objects.all()
        
        print(f"   💸 Total Transactions: {transactions.count()}")
        print(f"   💸 Refund Transactions: {refund_transactions.count()}")
        print(f"   ⚖️ Dispute Cases: {disputes.count()}")
        
        if refund_transactions.exists():
            total_refund_amount = refund_transactions.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            successful_refunds = refund_transactions.filter(status='success').count()
            processing_rate = (successful_refunds / refund_transactions.count() * 100) if refund_transactions.count() > 0 else 0
            
            print(f"   ✅ Successful Refunds: {successful_refunds}")
            print(f"   💰 Total Refund Amount: {total_refund_amount}")
            print(f"   📈 Processing Rate: {processing_rate:.1f}%")
        
        # Check dispute-based refunds
        if disputes.exists():
            resolved_disputes = disputes.filter(status='resolved').count()
            print(f"   ⚖️ Resolved Disputes: {resolved_disputes}")
        
        result_6 = refund_transactions.count() > 0 or disputes.count() > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_6 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_6 = False
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    results = [result_1, result_2, result_3, result_4, result_5, result_6]
    implemented = sum(results)
    total = len(results)
    percentage = (implemented / total * 100) if total > 0 else 0
    
    print(f"📈 Implementation Rate: {implemented}/{total} ({percentage:.1f}%)")
    
    requirement_names = [
        "Multi-Stage Escrow",
        "Dispute Resolution", 
        "Payment Protection",
        "Multi-Currency Support",
        "Fee Management",
        "Refund Processing"
    ]
    
    for i, (name, status) in enumerate(zip(requirement_names, results)):
        icon = "✅" if status else "❌"
        print(f"   {i+1}. {name}: {icon}")
    
    if percentage >= 80:
        print("\n🌟 EXCELLENT: Secure Transaction Processing is well implemented!")
    elif percentage >= 60:
        print("\n👍 GOOD: Most requirements implemented, minor gaps exist")
    elif percentage >= 40:
        print("\n⚠️ FAIR: Significant gaps need attention")
    else:
        print("\n🔴 CRITICAL: Major implementation work required")

if __name__ == "__main__":
    main()
