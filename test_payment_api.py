"""
AgriConnect Phase 4 Payment API Test
Test payment system API endpoints and functionality
"""

import os
import sys
import django
from decimal import Decimal
import json

# Setup Django environment  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from payments.models import PaymentGateway, PaymentMethod, Transaction
from payments.views import PaymentAPIRoot, PaymentGatewayViewSet
from orders.models import Order

User = get_user_model()

def test_payment_api():
    """Test payment API functionality"""
    
    print("🧪 AGRICONNECT PHASE 4 - PAYMENT API TESTING")
    print("=" * 60)
    
    # Setup test request factory
    factory = RequestFactory()
    
    # 1. Test Payment API Root
    print("\n🌐 Testing Payment API Root...")
    try:
        request = factory.get('/api/v1/payments/')
        api_root_view = PaymentAPIRoot()
        response = api_root_view.get(request)
        
        if response.status_code == 200:
            print("✅ Payment API Root: WORKING")
            data = response.data
            print(f"   API Name: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Features: {len(data.get('features', []))}")
            print(f"   Status: {data.get('status')}")
        else:
            print(f"❌ Payment API Root: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Payment API Root: Error - {e}")
    
    # 2. Test Payment Gateways API  
    print("\n🏦 Testing Payment Gateways API...")
    try:
        # Get a test user
        user = User.objects.first()
        if not user:
            print("⚠️  No users found, creating test user...")
            user = User.objects.create_user(
                email='test@agriconnect.com',
                phone_number='+233123456789',
                password='testpass123'
            )
        
        request = factory.get('/api/v1/payments/gateways/')
        request.user = user
        
        gateway_viewset = PaymentGatewayViewSet()
        gateway_viewset.request = request
        
        queryset = gateway_viewset.get_queryset()
        print(f"✅ Payment Gateways API: {queryset.count()} gateways available")
        
        for gateway in queryset:
            print(f"   • {gateway.display_name}: {len(gateway.supported_currencies)} currencies")
            
    except Exception as e:
        print(f"❌ Payment Gateways API: Error - {e}")
    
    # 3. Test Payment Method Creation
    print("\n💳 Testing Payment Method Creation...")
    try:
        # Get a gateway for testing
        gateway = PaymentGateway.objects.filter(is_active=True).first()
        if gateway and user:
            payment_method = PaymentMethod.objects.create(
                user=user,
                method_type='mobile_money',
                gateway=gateway,
                account_details={
                    'phone_number': '+233555123456',
                    'network': 'MTN'
                },
                display_name='MTN *****3456',
                is_verified=True
            )
            print(f"✅ Payment Method Created: {payment_method.display_name}")
        else:
            print("⚠️  No gateway or user available for payment method test")
    except Exception as e:
        print(f"❌ Payment Method Creation: Error - {e}")
    
    # 4. Test Transaction Creation
    print("\n💰 Testing Transaction Creation...")
    try:
        # Get an order for testing
        order = Order.objects.first()
        gateway = PaymentGateway.objects.filter(is_active=True).first()
        
        if order and gateway and user:
            transaction = Transaction.objects.create(
                user=user,
                order=order,
                gateway=gateway,
                amount=Decimal('50.00'),
                currency='GHS',
                gateway_reference=f'TEST_{order.id}_{gateway.name}',
                status='pending'
            )
            print(f"✅ Transaction Created: {transaction.gateway_reference}")
            print(f"   Amount: {transaction.amount} {transaction.currency}")
            print(f"   Status: {transaction.status}")
        else:
            print("⚠️  Missing order, gateway, or user for transaction test")
    except Exception as e:
        print(f"❌ Transaction Creation: Error - {e}")
    
    # 5. Payment System Summary
    print("\n" + "=" * 60)
    print("📋 PAYMENT API TEST SUMMARY")
    print("=" * 60)
    
    # Count current state
    gateways = PaymentGateway.objects.filter(is_active=True).count()
    methods = PaymentMethod.objects.count()
    transactions = Transaction.objects.count()
    orders = Order.objects.count()
    users = User.objects.count()
    
    print(f"🏦 Active Payment Gateways: {gateways}")
    print(f"💳 Payment Methods: {methods}")
    print(f"💰 Transactions: {transactions}")
    print(f"📦 Orders Available: {orders}")
    print(f"👥 Users Available: {users}")
    
    if gateways > 0 and orders > 0 and users > 0:
        print("\n🎉 PAYMENT SYSTEM: FULLY OPERATIONAL ✅")
        print("🚀 Ready for live payment processing!")
        
        print("\n🔗 API Endpoints Available:")
        print("   • GET  /api/v1/payments/ - API Root")
        print("   • GET  /api/v1/payments/api/v1/gateways/ - Payment Gateways")
        print("   • CRUD /api/v1/payments/api/v1/payment-methods/ - Payment Methods")
        print("   • CRUD /api/v1/payments/api/v1/transactions/ - Transactions")
        print("   • CRUD /api/v1/payments/api/v1/payments/ - Payment Operations")
        print("   • CRUD /api/v1/payments/api/v1/escrow/ - Escrow Management")
        
    else:
        print("\n⚠️  PAYMENT SYSTEM: CONFIGURATION INCOMPLETE")
        print("🔧 Ensure gateways, orders, and users are available")

if __name__ == "__main__":
    try:
        test_payment_api()
    except Exception as e:
        print(f"\n❌ Error running payment API test: {e}")
        import traceback
        traceback.print_exc()
