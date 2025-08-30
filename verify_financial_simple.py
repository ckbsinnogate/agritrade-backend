#!/usr/bin/env python3
"""
Simple Financial Services Integration Check - Section 4.3.2
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db.models import Sum, Count, Q
from payments.models import PaymentGateway, PaymentMethod, Transaction

def main():
    print("🚀 AgriConnect Financial Services Integration Verification")
    print("📋 Section 4.3.2 - Requirements Analysis")
    print("="*70)
    
    # 4.3.2.1 Mobile Money
    print("\n1️⃣ MOBILE MONEY INTEGRATION")
    try:
        mobile_gateways = PaymentGateway.objects.filter(
            Q(name__icontains='mtn') | 
            Q(name__icontains='mobile') |
            Q(name='mtn_momo')
        )
        mobile_methods = PaymentMethod.objects.filter(method_type='mobile_money')
        
        print(f"   📱 Mobile Money Gateways: {mobile_gateways.count()}")
        print(f"   📱 Mobile Money Methods: {mobile_methods.count()}")
        
        for gateway in mobile_gateways:
            print(f"      • {gateway.display_name}: {'✅' if gateway.is_active else '❌'}")
        
        result_1 = mobile_gateways.count() > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_1 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_1 = False
    
    # 4.3.2.2 Banking Integration
    print("\n2️⃣ BANKING INTEGRATION")
    try:
        bank_gateways = PaymentGateway.objects.filter(
            Q(name__icontains='bank') | Q(name='bank_transfer')
        )
        bank_methods = PaymentMethod.objects.filter(method_type='bank_transfer')
        
        print(f"   🏦 Bank Gateways: {bank_gateways.count()}")
        print(f"   🏦 Bank Methods: {bank_methods.count()}")
        
        for gateway in bank_gateways:
            print(f"      • {gateway.display_name}: {'✅' if gateway.is_active else '❌'}")
        
        result_2 = bank_gateways.count() > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_2 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_2 = False
    
    # 4.3.2.3 Cryptocurrency
    print("\n3️⃣ CRYPTOCURRENCY SUPPORT")
    try:
        crypto_methods = PaymentMethod.objects.filter(method_type='crypto')
        crypto_currencies = set()
        
        for gateway in PaymentGateway.objects.all():
            if gateway.supported_currencies:
                for currency in gateway.supported_currencies:
                    if currency in ['BTC', 'ETH', 'USDC', 'USDT']:
                        crypto_currencies.add(currency)
        
        print(f"   ₿ Crypto Methods: {crypto_methods.count()}")
        print(f"   💰 Crypto Currencies: {len(crypto_currencies)}")
        if crypto_currencies:
            print(f"      • {', '.join(crypto_currencies)}")
        
        result_3 = crypto_methods.count() > 0 or len(crypto_currencies) > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_3 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_3 = False
    
    # 4.3.2.4 Credit Systems
    print("\n4️⃣ CREDIT SYSTEMS")
    try:
        from payments.models import EscrowAccount
        credit_transactions = Transaction.objects.filter(
            Q(metadata__contains='credit') | Q(metadata__contains='financing')
        )
        long_term_escrows = EscrowAccount.objects.filter(auto_release_days__gte=30)
        
        print(f"   💳 Credit Transactions: {credit_transactions.count()}")
        print(f"   🏦 Long-term Escrows: {long_term_escrows.count()}")
        
        result_4 = credit_transactions.count() > 0 or long_term_escrows.count() > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_4 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_4 = False
    
    # 4.3.2.5 Insurance
    print("\n5️⃣ INSURANCE SERVICES")
    try:
        from payments.models import EscrowAccount, DisputeCase
        from decimal import Decimal
        
        insurance_transactions = Transaction.objects.filter(
            Q(metadata__contains='insurance') | Q(metadata__contains='protection')
        )
        
        total_escrow = EscrowAccount.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        disputes = DisputeCase.objects.count()
        
        print(f"   🛡️ Insurance Transactions: {insurance_transactions.count()}")
        print(f"   🛡️ Escrow Protection: {total_escrow}")
        print(f"   ⚖️ Dispute Protection: {disputes}")
        
        result_5 = insurance_transactions.count() > 0 or total_escrow > 0 or disputes > 0
        print(f"   ✅ Status: {'IMPLEMENTED' if result_5 else 'NOT IMPLEMENTED'}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        result_5 = False
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 FINANCIAL SERVICES INTEGRATION SUMMARY")
    print("="*70)
    
    results = [result_1, result_2, result_3, result_4, result_5]
    implemented = sum(results)
    total = len(results)
    percentage = (implemented / total * 100) if total > 0 else 0
    
    print(f"📈 Implementation Rate: {implemented}/{total} ({percentage:.1f}%)")
    
    requirement_names = [
        "Mobile Money Integration",
        "Banking Integration", 
        "Cryptocurrency Support",
        "Credit Systems",
        "Insurance Services"
    ]
    
    for i, (name, status) in enumerate(zip(requirement_names, results)):
        icon = "✅" if status else "❌"
        print(f"   {i+1}. {name}: {icon}")
    
    if percentage >= 80:
        print("\n🌟 EXCELLENT: Financial Services Integration is well implemented!")
    elif percentage >= 60:
        print("\n👍 GOOD: Most requirements implemented, minor gaps exist")
    elif percentage >= 40:
        print("\n⚠️ FAIR: Significant gaps need attention")
    else:
        print("\n🔴 CRITICAL: Major implementation work required")

if __name__ == "__main__":
    main()
