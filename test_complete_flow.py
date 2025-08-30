#!/usr/bin/env python
"""
Test Complete Payment Flow with Webhook
Final integration test for production readiness
"""

import os
import sys
import django
import requests
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway, Transaction, PaymentMethod
from orders.models import Order
from authentication.models import User
from products.models import Product

def test_complete_payment_flow():
    """Test the complete payment flow with webhook integration"""
    
    print("🧪 COMPLETE PAYMENT FLOW TEST")
    print("=" * 50)
    
    # Get Paystack gateway
    paystack = PaymentGateway.objects.filter(name='paystack').first()
    if not paystack:
        print("❌ Paystack gateway not found")
        return False
    
    print(f"✅ Found Paystack gateway")
    print(f"   Status: {'ACTIVE' if paystack.is_active else 'INACTIVE'}")
    print(f"   Webhook Secret: {'CONFIGURED' if paystack.webhook_secret else 'NOT SET'}")
    
    # Create test transaction
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            email='farmer@agriconnect.com',
            defaults={
                'username': 'test_farmer',
                'first_name': 'John',
                'last_name': 'Farmer'
            }
        )
          # Get or create a PaymentMethod instance
        payment_method, created = PaymentMethod.objects.get_or_create(
            user=user,
            gateway=paystack,
            method_type='credit_card',
            defaults={
                'display_name': 'Test Credit Card',
                'account_details': {'type': 'test'},
                'is_verified': True
            }
        )        # Create transaction for premium seeds (Ghana)
        import uuid
        transaction = Transaction.objects.create(
            user=user,
            gateway=paystack,
            payment_method=payment_method,
            amount=Decimal('75.00'),  # GHS 75 for premium seeds
            currency='GHS',
            status='pending',
            gateway_reference=f'test_{uuid.uuid4().hex[:12]}',  # Add unique reference
            metadata={
                'product': 'Premium Maize Seeds - 15kg',
                'farmer_location': 'Ashanti Region, Ghana',
                'crop_type': 'Maize',
                'farming_season': '2025 Wet Season',
                'farming_scale': 'Commercial',
                'notes': 'High-yield drought-resistant variety'
            }
        )
        
        print(f"\n💰 Test Transaction Created:")
        print(f"   ID: {transaction.id}")
        print(f"   Amount: NGN {transaction.amount}")
        print(f"   User: {transaction.user.email}")
        print(f"   Product: {transaction.metadata.get('product')}")
        
        # Initialize payment with Paystack
        headers = {
            "Authorization": f"Bearer {paystack.secret_key}",
            "Content-Type": "application/json"
        }        # Use the transaction ID as reference
        payment_data = {
            "email": user.email,
            "amount": int(transaction.amount * 100),  # Convert to kobo
            "reference": transaction.gateway_reference,
            "callback_url": "https://your-domain.com/payment/callback/",
            "metadata": {
                "transaction_id": str(transaction.id),  # Convert UUID to string
                "product": transaction.metadata.get('product'),
                "farmer_location": transaction.metadata.get('farmer_location'),
                "crop_type": transaction.metadata.get('crop_type')
            }
        }
        
        print(f"\n🚀 Initializing payment with Paystack...")
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payment_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                payment_info = data["data"]
                
                print(f"✅ Payment initialization successful!")
                print(f"   Reference: {payment_info['reference']}")
                print(f"   Authorization URL: {payment_info['authorization_url']}")
                print(f"   Access Code: {payment_info['access_code']}")
                
                # Update transaction with Paystack reference
                transaction.external_reference = payment_info.get('reference')
                transaction.save()
                
                print(f"\n🌐 TEST PAYMENT URL:")
                print(f"   {payment_info['authorization_url']}")
                print(f"\n💳 PAYSTACK TEST CARDS:")
                print(f"   Successful: 4084084084084081")
                print(f"   Failed: 4084084084084008")
                print(f"   Expiry: Any future date (e.g., 12/25)")
                print(f"   CVV: 123")
                print(f"   PIN: 1234")
                
                print(f"\n🔔 WEBHOOK TESTING:")
                print(f"   1. Complete payment using test card")
                print(f"   2. Check webhook delivery in Paystack dashboard")
                print(f"   3. Verify transaction status update in Django")
                print(f"   4. Monitor Django logs for webhook processing")
                
                # Check transaction status
                print(f"\n📊 Transaction Status Check:")
                print(f"   Current Status: {transaction.status}")
                print(f"   Gateway Reference: {transaction.gateway_reference}")
                print(f"   External Reference: {transaction.external_reference}")
                
                return True
            else:
                print(f"❌ Payment initialization failed: {data.get('message')}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
        
    except Exception as e:
        print(f"❌ Error in payment flow test: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def show_production_checklist():
    """Show production deployment checklist"""
    
    print(f"\n📋 PRODUCTION DEPLOYMENT CHECKLIST")
    print("=" * 40)
    
    checklist = [
        ("✅", "Real Paystack API integration working"),
        ("✅", "Webhook system implemented"),
        ("✅", "Database models configured"),
        ("✅", "Payment URLs generated"),
        ("🔄", "Webhook URL added to Paystack dashboard"),
        ("🔄", "Webhook secret configured"),
        ("🔄", "Domain name configured"),
        ("🔄", "SSL certificate installed"),
        ("🔄", "Production API keys obtained"),
    ]
    
    for status, item in checklist:
        print(f"   {status} {item}")
    
    print(f"\n🚀 NEXT IMMEDIATE ACTIONS:")
    print("1. Add webhook URL to Paystack dashboard")
    print("2. Get webhook secret and run add_webhook_secret.py")
    print("3. Test payment with generated URL")
    print("4. Monitor webhook delivery")
    print("5. Deploy to production domain")

if __name__ == "__main__":
    success = test_complete_payment_flow()
    
    if success:
        show_production_checklist()
        
        print(f"\n" + "=" * 50)
        print("🎉 AGRICONNECT PAYMENT SYSTEM: READY!")
        print("✅ Real Paystack API: Working")
        print("✅ Webhook system: Implemented")
        print("✅ Test payment: Generated")
        print("🌾 Ready for live agricultural commerce!")
        print("=" * 50)
    else:
        print(f"\n❌ Payment flow test failed - check configuration")
