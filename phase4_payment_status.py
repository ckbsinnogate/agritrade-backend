"""
AgriConnect Phase 4 Payment System Status Check
Comprehensive verification of payment integration implementation
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway, PaymentMethod, Transaction, EscrowAccount
from orders.models import Order
from authentication.models import User
from django.db import models

def check_payment_system():
    """Comprehensive payment system status check"""
    
    print("🚀 AGRICONNECT PHASE 4 - PAYMENT SYSTEM STATUS CHECK")
    print("=" * 70)
    
    # 1. Payment Gateways
    print("\n💳 PAYMENT GATEWAYS:")
    print("-" * 50)
    gateways = PaymentGateway.objects.all()
    print(f"📊 Total Payment Gateways: {gateways.count()}")
    
    if gateways.exists():
        active_gateways = gateways.filter(is_active=True)
        print(f"🟢 Active Gateways: {active_gateways.count()}")
        print(f"🔴 Inactive Gateways: {gateways.count() - active_gateways.count()}")
        
        print("\n🏦 Available Gateways:")
        for gateway in gateways:
            status = "🟢 ACTIVE" if gateway.is_active else "🔴 INACTIVE"
            currencies = ", ".join(gateway.supported_currencies[:3])
            if len(gateway.supported_currencies) > 3:
                currencies += f" (+{len(gateway.supported_currencies) - 3} more)"
            print(f"  • {gateway.display_name} ({gateway.name}) - {status}")
            print(f"    Currencies: {currencies}")
            print(f"    Countries: {', '.join(gateway.supported_countries[:3])}")
    else:
        print("❌ No payment gateways configured")
    
    # 2. Payment Methods
    print("\n🔧 PAYMENT METHODS:")
    print("-" * 50)
    payment_methods = PaymentMethod.objects.all()
    print(f"📊 Total Payment Methods: {payment_methods.count()}")
    
    if payment_methods.exists():
        for method_type, _ in PaymentMethod.METHOD_CHOICES:
            count = payment_methods.filter(method_type=method_type).count()
            if count > 0:
                print(f"  • {method_type.replace('_', ' ').title()}: {count}")
    
    # 3. Transactions
    print("\n💰 TRANSACTIONS:")
    print("-" * 50)
    transactions = Transaction.objects.all()
    print(f"📊 Total Transactions: {transactions.count()}")
    
    if transactions.exists():
        total_amount = transactions.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        print(f"💵 Total Transaction Value: GHS {total_amount}")
        
        print("\n📈 Transaction Status Distribution:")
        for status, _ in Transaction.STATUS_CHOICES:
            count = transactions.filter(status=status).count()
            if count > 0:
                print(f"  • {status.upper()}: {count} transactions")
    
    # 4. Escrow Accounts
    print("\n🔒 ESCROW SYSTEM:")
    print("-" * 50)
    escrow_accounts = EscrowAccount.objects.all()
    print(f"📊 Total Escrow Accounts: {escrow_accounts.count()}")
    
    if escrow_accounts.exists():
        total_escrow = escrow_accounts.aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0')
        released_escrow = escrow_accounts.aggregate(
            released=models.Sum('released_amount')
        )['released'] or Decimal('0')
        
        print(f"💰 Total Escrow Value: GHS {total_escrow}")
        print(f"✅ Released Amount: GHS {released_escrow}")
        print(f"🔒 Held Amount: GHS {total_escrow - released_escrow}")
        
        print("\n📊 Escrow Status Distribution:")
        for status, _ in EscrowAccount.STATUS_CHOICES:
            count = escrow_accounts.filter(status=status).count()
            if count > 0:
                print(f"  • {status.upper()}: {count} accounts")
    
    # 5. System Integration
    print("\n🔗 SYSTEM INTEGRATION:")
    print("-" * 50)
    orders = Order.objects.all()
    users = User.objects.all()
    
    print(f"📦 Total Orders: {orders.count()}")
    print(f"👥 Total Users: {users.count()}")
    
    # Check integration health
    orders_with_transactions = orders.filter(transactions__isnull=False).distinct().count()
    orders_with_escrow = orders.filter(escrow__isnull=False).count()
    
    print(f"💳 Orders with Transactions: {orders_with_transactions}")
    print(f"🔒 Orders with Escrow: {orders_with_escrow}")
    
    # 6. API Endpoints Check
    print("\n🌐 API ENDPOINTS:")
    print("-" * 50)
    try:
        from payments.urls import urlpatterns
        endpoint_count = len(urlpatterns)
        print(f"📍 Payment API Endpoints: {endpoint_count}")
        print("✅ Payment URLs configured")
    except Exception as e:
        print(f"❌ Payment URL configuration error: {e}")
    
    # 7. Database Models Health
    print("\n🗄️ DATABASE MODELS:")
    print("-" * 50)
    model_checks = [
        ('PaymentGateway', PaymentGateway),
        ('PaymentMethod', PaymentMethod), 
        ('Transaction', Transaction),
        ('EscrowAccount', EscrowAccount),
    ]
    
    all_models_healthy = True
    for model_name, model_class in model_checks:
        try:
            count = model_class.objects.count()
            print(f"✅ {model_name}: {count} records")
        except Exception as e:
            print(f"❌ {model_name}: Database error - {e}")
            all_models_healthy = False
    
    # 8. System Status Summary
    print("\n" + "=" * 70)
    print("📋 PHASE 4 SYSTEM STATUS SUMMARY")
    print("=" * 70)
    
    if gateways.filter(is_active=True).exists():
        print("✅ Payment Gateways: CONFIGURED")
    else:
        print("⚠️  Payment Gateways: NEED CONFIGURATION")
    
    if all_models_healthy:
        print("✅ Database Models: HEALTHY")
    else:
        print("❌ Database Models: ERRORS DETECTED")
    
    try:
        from payments.views import PaymentAPIRoot
        print("✅ Payment API Views: AVAILABLE")
    except Exception:
        print("❌ Payment API Views: IMPORT ERROR")
    
    # Overall Phase 4 Status
    if gateways.filter(is_active=True).exists() and all_models_healthy:
        print("\n🎉 PHASE 4 STATUS: PAYMENT SYSTEM ACTIVE ✅")
        print("🚀 Ready for payment processing integration!")
    else:
        print("\n⚠️  PHASE 4 STATUS: CONFIGURATION NEEDED")
        print("🔧 Review issues above and continue setup")
    
    print("\n🔗 Next Steps:")
    print("  1. Test API endpoints: http://127.0.0.1:8000/api/v1/payments/")
    print("  2. Configure real payment gateway credentials")
    print("  3. Implement webhook handling")
    print("  4. Add notification system")
    print("  5. Create payment tests")

if __name__ == "__main__":
    try:
        check_payment_system()
    except Exception as e:
        print(f"\n❌ Error running payment system check: {e}")
        import traceback
        traceback.print_exc()
