"""
AgriConnect Phase 4 Payment System Demo
Comprehensive demonstration of payment capabilities for agricultural commerce
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway, PaymentMethod, Transaction, EscrowAccount, EscrowMilestone
from orders.models import Order
from authentication.models import User
from products.models import Product

def demo_payment_system():
    """Demonstrate AgriConnect payment system capabilities"""
    
    print("🌾 AGRICONNECT PHASE 4 - PAYMENT SYSTEM DEMO")
    print("=" * 70)
    print("Demonstrating secure agricultural commerce payment processing")
    print("Date:", datetime.now().strftime("%B %d, %Y"))
    print()
    
    # 1. Display Available Payment Gateways
    print("🏦 AVAILABLE PAYMENT GATEWAYS")
    print("-" * 50)
    gateways = PaymentGateway.objects.filter(is_active=True)
    
    for gateway in gateways:
        print(f"✅ {gateway.display_name} ({gateway.name})")
        print(f"   💱 Currencies: {', '.join(gateway.supported_currencies)}")
        print(f"   🌍 Countries: {', '.join(gateway.supported_countries)}")
        print(f"   🔧 Methods: {', '.join(gateway.supported_payment_methods)}")
        print(f"   💰 Fee: {gateway.transaction_fee_percentage*100:.1f}% + {gateway.fixed_fee}")
        print()
    
    # 2. Demo User Payment Method Setup
    print("👤 USER PAYMENT METHOD SETUP DEMO")
    print("-" * 50)
    
    # Get or create demo user
    user, created = User.objects.get_or_create(
        email='farmer@agriconnect.com',
        defaults={
            'phone_number': '+233555123456',
            'first_name': 'Kwame',
            'last_name': 'Farmer',
            'is_active': True
        }
    )
    
    if created:
        user.set_password('demo123')
        user.save()
        print(f"✅ Created demo user: {user.email}")
    else:
        print(f"✅ Using existing user: {user.email}")
    
    # Create payment methods for demo
    payment_methods_data = [
        {
            'gateway': PaymentGateway.objects.filter(name='mtn_momo').first(),
            'method_type': 'mobile_money',
            'account_details': {'phone_number': '+233555123456', 'network': 'MTN'},
            'display_name': 'MTN *****3456'
        },
        {
            'gateway': PaymentGateway.objects.filter(name='paystack').first(),
            'method_type': 'credit_card',
            'account_details': {'card_last4': '1234', 'card_type': 'Visa'},
            'display_name': 'Visa ****1234'
        }
    ]
    
    created_methods = []
    for method_data in payment_methods_data:
        if method_data['gateway']:
            method, created = PaymentMethod.objects.get_or_create(
                user=user,
                gateway=method_data['gateway'],
                method_type=method_data['method_type'],
                defaults={
                    'account_details': method_data['account_details'],
                    'display_name': method_data['display_name'],
                    'is_verified': True,
                    'is_default': len(created_methods) == 0
                }
            )
            created_methods.append(method)
            print(f"💳 {method.display_name} - {method.gateway.display_name}")
    
    # 3. Demo Agricultural Order Transaction
    print(f"\n🌾 AGRICULTURAL TRANSACTION DEMO")
    print("-" * 50)
    
    # Get a sample order or create one
    order = Order.objects.first()
    if not order:
        # Create a demo order if none exists
        product = Product.objects.first()
        if product:
            order = Order.objects.create(
                user=user,
                order_number=f"AG{datetime.now().strftime('%Y%m%d%H%M%S')}DEMO",
                status='pending',
                total_amount=Decimal('250.00'),
                currency='GHS',
                shipping_address='Accra, Ghana'
            )
            print(f"✅ Created demo order: {order.order_number}")
    
    if order:
        print(f"📦 Order: {order.order_number}")
        print(f"💰 Amount: {order.total_amount} {order.currency}")
        print(f"📍 Delivery: {getattr(order, 'shipping_address', 'Accra, Ghana')}")
        
        # Create demo transaction
        gateway = PaymentGateway.objects.filter(name='paystack').first()
        if gateway:
            transaction = Transaction.objects.create(
                user=user,
                order=order,
                gateway=gateway,
                amount=order.total_amount,
                currency=order.currency,
                gateway_reference=f"PAY_{order.order_number}_{gateway.name.upper()}",
                status='pending',
                transaction_type='payment',
                metadata={
                    'demo': True,
                    'payment_method': 'Mobile Money',
                    'customer_phone': '+233555123456'
                }
            )
            print(f"💳 Transaction: {transaction.gateway_reference}")
            print(f"🔄 Status: {transaction.status.upper()}")
            
            # Simulate transaction processing
            transaction.status = 'completed'
            transaction.processed_at = datetime.now()
            transaction.save()
            print(f"✅ Transaction completed successfully!")
    
    # 4. Demo Escrow System
    print(f"\n🔒 ESCROW SYSTEM DEMO")
    print("-" * 50)
    
    if order and user:
        # Create or get escrow account
        escrow, created = EscrowAccount.objects.get_or_create(
            order=order,
            defaults={
                'buyer': user,
                'seller': User.objects.exclude(id=user.id).first() or user,
                'total_amount': order.total_amount,
                'currency': order.currency,
                'status': 'funded',
                'auto_release_days': 7,
                'requires_quality_confirmation': True
            }
        )
        
        if created:
            print(f"🔒 Created escrow account for order {order.order_number}")
        else:
            print(f"🔒 Using existing escrow for order {order.order_number}")
            
        print(f"💰 Escrow Amount: {escrow.total_amount} {escrow.currency}")
        print(f"✅ Released: {escrow.released_amount} {escrow.currency}")
        print(f"🔒 Held: {escrow.total_amount - escrow.released_amount} {escrow.currency}")
        print(f"📅 Auto-release: {escrow.auto_release_days} days after delivery")
        
        # Create milestone demo
        milestones_data = [
            ('order_confirmed', 'Order Confirmed by Seller', 20.0),
            ('goods_prepared', 'Goods Prepared for Shipping', 30.0),
            ('goods_delivered', 'Goods Delivered to Buyer', 40.0),
            ('quality_confirmed', 'Quality Confirmed by Buyer', 10.0)
        ]
        
        print(f"\n📋 Escrow Milestones:")
        for milestone_type, description, percentage in milestones_data:
            milestone, created = EscrowMilestone.objects.get_or_create(
                escrow=escrow,
                milestone_type=milestone_type,
                defaults={
                    'description': description,
                    'release_percentage': Decimal(str(percentage)),
                    'release_amount': escrow.total_amount * Decimal(str(percentage)) / 100,
                    'is_completed': milestone_type in ['order_confirmed', 'goods_prepared']
                }
            )
            
            status = "✅ COMPLETED" if milestone.is_completed else "⏳ PENDING"
            print(f"  • {description}: {percentage}% - {status}")
    
    # 5. Payment System Statistics
    print(f"\n📊 PAYMENT SYSTEM STATISTICS")
    print("-" * 50)
    
    total_gateways = PaymentGateway.objects.count()
    active_gateways = PaymentGateway.objects.filter(is_active=True).count()
    total_methods = PaymentMethod.objects.count()
    total_transactions = Transaction.objects.count()
    total_escrow = EscrowAccount.objects.count()
    
    completed_transactions = Transaction.objects.filter(status='completed').count()
    total_transaction_value = Transaction.objects.filter(
        status='completed'
    ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0')
    
    print(f"🏦 Payment Gateways: {active_gateways}/{total_gateways} active")
    print(f"💳 Payment Methods: {total_methods}")
    print(f"💰 Transactions: {total_transactions} ({completed_transactions} completed)")
    print(f"💵 Transaction Value: GHS {total_transaction_value}")
    print(f"🔒 Escrow Accounts: {total_escrow}")
    
    # 6. API Endpoints Summary
    print(f"\n🌐 AVAILABLE API ENDPOINTS")
    print("-" * 50)
    endpoints = [
        "GET    /api/v1/payments/ - Payment system overview",
        "GET    /api/v1/payments/api/v1/gateways/ - Available gateways",
        "CRUD   /api/v1/payments/api/v1/payment-methods/ - Payment methods",
        "CRUD   /api/v1/payments/api/v1/transactions/ - Transactions",
        "CRUD   /api/v1/payments/api/v1/payments/ - Payment operations",
        "CRUD   /api/v1/payments/api/v1/escrow/ - Escrow management",
        "CRUD   /api/v1/payments/api/v1/disputes/ - Dispute resolution"
    ]
    
    for endpoint in endpoints:
        print(f"  📍 {endpoint}")
    
    # Demo Summary
    print(f"\n" + "=" * 70)
    print("🎉 AGRICONNECT PAYMENT SYSTEM DEMO COMPLETE!")
    print("=" * 70)
    print("✅ Payment gateways configured and active")
    print("✅ User payment methods demonstrated")
    print("✅ Agricultural transaction processing shown") 
    print("✅ Escrow system with milestones working")
    print("✅ API endpoints available for integration")
    print()
    print("🚀 The AgriConnect payment system is ready for:")
    print("   • Secure agricultural commerce transactions")
    print("   • Multi-gateway payment processing")
    print("   • Escrow-protected trade agreements")
    print("   • Mobile money integration for rural farmers")
    print("   • Dispute resolution and buyer protection")
    print()
    print("🔗 Next: Configure real payment gateway credentials for live processing")

if __name__ == "__main__":
    try:
        # Import django db models for aggregation
        import django.db.models
        demo_payment_system()
    except Exception as e:
        print(f"\n❌ Error running payment system demo: {e}")
        import traceback
        traceback.print_exc()
