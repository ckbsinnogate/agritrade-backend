#!/usr/bin/env python
"""
Quick Status Check for AgriConnect Ghana
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway, Transaction
from authentication.models import User

def check_status():
    """Quick status check"""
    
    print("🇬🇭 AGRICONNECT GHANA - QUICK STATUS CHECK")
    print("=" * 55)
    
    try:
        # Check Paystack gateway
        paystack = PaymentGateway.objects.get(name='paystack')
        primary_currency = paystack.supported_currencies[0] if paystack.supported_currencies else 'None'
        
        print(f"✅ Gateway: {paystack.display_name}")
        print(f"✅ Primary Currency: {primary_currency}")
        print(f"✅ Status: {'ACTIVE' if paystack.is_active else 'INACTIVE'}")
        print(f"✅ Mobile Money: {'mobile_money' in paystack.supported_payment_methods}")
        
        # Check transactions
        total_transactions = Transaction.objects.count()
        ghana_transactions = Transaction.objects.filter(currency='GHS').count()
        
        print(f"✅ Total Transactions: {total_transactions}")
        print(f"✅ Ghana Transactions: {ghana_transactions}")
        
        # Check users
        total_users = User.objects.count()
        print(f"✅ Total Users: {total_users}")
        
        print(f"\n🎯 SYSTEM STATUS:")
        if primary_currency == 'GHS':
            print("✅ GHANA CONFIGURATION: COMPLETE")
            print("🚀 READY FOR NEXT DEVELOPMENT PHASE")
        else:
            print("⚠️  Need to set GHS as primary currency")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_status()
