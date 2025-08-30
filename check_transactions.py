#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import Transaction, PaymentGateway

def check_transaction_status():
    print("🔍 CHECKING TRANSACTION DATABASE STATUS")
    print("=" * 50)
    
    # Check all transactions
    all_transactions = Transaction.objects.all()
    print(f"📊 Total Transactions: {all_transactions.count()}")
    
    # Check transactions with empty gateway_reference
    empty_refs = Transaction.objects.filter(gateway_reference__isnull=True) | Transaction.objects.filter(gateway_reference__exact='')
    print(f"⚠️  Empty Gateway References: {empty_refs.count()}")
    
    if empty_refs.exists():
        print("\n🔧 Transactions with empty gateway_reference:")
        for i, transaction in enumerate(empty_refs[:5]):
            print(f"   {i+1}. ID: {transaction.id}")
            print(f"      Status: {transaction.status}")
            print(f"      Amount: {transaction.amount} {transaction.currency}")
            print(f"      Created: {transaction.created_at}")
            print()
    
    # Check payment gateways
    gateways = PaymentGateway.objects.all()
    print(f"💳 Payment Gateways: {gateways.count()}")
    for gateway in gateways:
        print(f"   - {gateway.name}: {gateway.status}")
    
    return empty_refs.count() > 0

if __name__ == "__main__":
    has_empty_refs = check_transaction_status()
    if has_empty_refs:
        print("\n❌ Database cleanup needed before running tests")
    else:
        print("\n✅ Database is ready for testing")
