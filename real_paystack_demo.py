"""
Real Paystack Payment Integration for AgriConnect
Complete payment processing with real API integration within Django framework
"""

import os
import django
from decimal import Decimal
import requests
import json
from datetime import datetime
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway, Transaction, PaymentMethod
from orders.models import Order
from authentication.models import User


class AgriConnectPaystackService:
    """Enhanced Paystack service for AgriConnect"""
    
    def __init__(self):
        self.gateway = PaymentGateway.objects.filter(
            name='paystack', 
            is_active=True
        ).first()
        
        if not self.gateway or not self.gateway.secret_key:
            raise Exception("Paystack gateway not configured")
            
        self.secret_key = self.gateway.secret_key
        self.public_key = self.gateway.public_key
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
    
    def create_agricultural_payment(self, user, order, amount, currency="NGN"):
        """Create agricultural commerce payment with real Paystack API"""
        
        print(f"🌾 Creating agricultural payment for order {order.order_number}")
        print(f"   Amount: {amount} {currency}")
        print(f"   User: {user.email}")
        
        # Create local transaction record first
        transaction = Transaction.objects.create(
            user=user,
            order=order,
            gateway=self.gateway,
            amount=amount,
            currency=currency,
            gateway_reference=f"AG_{order.order_number}_{uuid.uuid4().hex[:8].upper()}",
            status='pending',
            transaction_type='payment',
            metadata={
                "order_number": order.order_number,
                "customer_name": f"{user.first_name} {user.last_name}".strip() or user.email,
                "purpose": "Agricultural Product Purchase",
                "platform": "AgriConnect",
                "initiated_at": datetime.now().isoformat()
            }
        )
        
        print(f"   Transaction ID: {transaction.id}")
        print(f"   Reference: {transaction.gateway_reference}")
        
        # Prepare Paystack payment initialization
        amount_in_kobo = int(amount * 100)  # Convert to smallest currency unit
        
        payload = {
            "email": user.email,
            "amount": amount_in_kobo,
            "currency": currency,
            "reference": transaction.gateway_reference,
            "callback_url": "https://agriconnect.com/payment/callback",
            "metadata": {
                "order_id": str(order.id),
                "order_number": order.order_number,
                "transaction_id": str(transaction.id),
                "customer_id": str(user.id),
                "customer_name": f"{user.first_name} {user.last_name}".strip() or user.email,
                "purpose": "Agricultural Product Purchase - AgriConnect Platform",
                "platform": "AgriConnect",
                "cancel_action": "https://agriconnect.com/payment/cancelled"
            },
            "channels": ["card", "bank", "ussd", "qr", "mobile_money"],
            "split_code": None,  # For marketplace transactions
            "subaccount": None   # For vendor payments
        }
        
        try:
            print("   📡 Calling Paystack API...")
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status"):
                    payment_info = data["data"]
                    
                    # Update transaction with Paystack response
                    transaction.external_reference = payment_info["reference"]
                    transaction.gateway_response = {
                        "authorization_url": payment_info["authorization_url"],
                        "access_code": payment_info["access_code"],
                        "reference": payment_info["reference"],
                        "paystack_response": data
                    }
                    transaction.save()
                    
                    print("   ✅ Payment initialized successfully!")
                    print(f"   Authorization URL: {payment_info['authorization_url']}")
                    
                    return {
                        "success": True,
                        "transaction": transaction,
                        "payment_url": payment_info["authorization_url"],
                        "reference": payment_info["reference"],
                        "access_code": payment_info["access_code"]
                    }
                else:
                    error_msg = data.get("message", "Unknown error")
                    print(f"   ❌ Paystack Error: {error_msg}")
                    
                    transaction.status = 'failed'
                    transaction.gateway_response = {"error": error_msg, "raw_response": data}
                    transaction.save()
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "transaction": transaction
                    }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"   ❌ HTTP Error: {error_msg}")
                
                transaction.status = 'failed'
                transaction.gateway_response = {"error": error_msg}
                transaction.save()
                
                return {
                    "success": False,
                    "error": error_msg,
                    "transaction": transaction
                }
                
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"   ❌ Network Error: {error_msg}")
            
            transaction.status = 'failed'
            transaction.gateway_response = {"error": error_msg}
            transaction.save()
            
            return {
                "success": False,
                "error": error_msg,
                "transaction": transaction
            }
    
    def verify_agricultural_payment(self, reference):
        """Verify payment with enhanced agricultural commerce handling"""
        
        print(f"🔍 Verifying payment: {reference}")
        
        try:
            transaction = Transaction.objects.get(
                gateway_reference=reference
            )
            print(f"   Found transaction: {transaction.id}")
            
        except Transaction.DoesNotExist:
            print(f"   ❌ Transaction not found for reference: {reference}")
            return {"success": False, "error": "Transaction not found"}
        
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status"):
                    payment_data = data["data"]
                    
                    # Update transaction based on Paystack response
                    if payment_data["status"] == "success":
                        transaction.status = 'completed'
                        transaction.processed_at = datetime.now()
                        
                        # Update order status
                        order = transaction.order
                        order.status = 'paid'
                        order.save()
                        
                        print(f"   ✅ Payment verified successfully!")
                        print(f"   Amount: {payment_data['amount']/100} {payment_data['currency']}")
                        print(f"   Order status updated to: {order.status}")
                        
                    elif payment_data["status"] == "failed":
                        transaction.status = 'failed'
                        print(f"   ❌ Payment failed")
                    else:
                        transaction.status = 'processing'
                        print(f"   ⏳ Payment still processing")
                    
                    transaction.gateway_response.update({
                        "verification_data": payment_data,
                        "verified_at": datetime.now().isoformat()
                    })
                    transaction.save()
                    
                    return {
                        "success": True,
                        "status": payment_data["status"],
                        "amount": Decimal(str(payment_data["amount"])) / 100,
                        "currency": payment_data["currency"],
                        "transaction": transaction
                    }
                else:
                    error_msg = data.get("message", "Verification failed")
                    print(f"   ❌ Verification Error: {error_msg}")
                    return {"success": False, "error": error_msg}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"   ❌ HTTP Error: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"   ❌ Network Error: {error_msg}")
            return {"success": False, "error": error_msg}


def demo_real_payment_integration():
    """Demonstrate real Paystack integration with AgriConnect"""
    
    print("🚀 AGRICONNECT - REAL PAYSTACK PAYMENT INTEGRATION DEMO")
    print("=" * 70)
    print("Testing live payment processing for agricultural commerce")
    print(f"Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print()
    
    try:
        # Initialize Paystack service
        paystack_service = AgriConnectPaystackService()
        print("✅ Paystack service initialized successfully")
        print(f"   Gateway: {paystack_service.gateway.display_name}")
        print(f"   API URL: {paystack_service.base_url}")
        print(f"   Public Key: {paystack_service.public_key[:25]}...")
        
        # Get or create demo user
        user, created = User.objects.get_or_create(
            email='farmer@agriconnect.com',
            defaults={
                'phone_number': '+233555123456',
                'first_name': 'Kwame',
                'last_name': 'Asante',
                'is_active': True
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            print(f"✅ Created demo user: {user.email}")
        else:
            print(f"✅ Using existing user: {user.email}")
        
        # Get or create demo order
        order = Order.objects.filter(user=user).first()
        if not order:
            order = Order.objects.create(
                user=user,
                order_number=f"AG{datetime.now().strftime('%Y%m%d%H%M%S')}DEMO",
                status='pending',
                total_amount=Decimal('150.00'),
                currency='NGN',
                shipping_address='Lagos, Nigeria',
                metadata={
                    'demo': True,
                    'products': ['Premium Maize Seeds - 10kg', 'Organic Fertilizer - 5kg'],
                    'delivery_method': 'Standard Shipping'
                }
            )
            print(f"✅ Created demo order: {order.order_number}")
        else:
            print(f"✅ Using existing order: {order.order_number}")
        
        print(f"   Order Amount: {order.total_amount} {order.currency}")
        print(f"   Order Status: {order.status}")
        
        # Create real payment with Paystack
        print(f"\n💳 CREATING REAL PAYMENT WITH PAYSTACK")
        print("-" * 50)
        
        payment_result = paystack_service.create_agricultural_payment(
            user=user,
            order=order,
            amount=order.total_amount,
            currency=order.currency
        )
        
        if payment_result["success"]:
            transaction = payment_result["transaction"]
            
            print(f"\n🎉 PAYMENT CREATED SUCCESSFULLY!")
            print(f"   Transaction ID: {transaction.id}")
            print(f"   Reference: {transaction.gateway_reference}")
            print(f"   Payment URL: {payment_result['payment_url']}")
            print(f"   Status: {transaction.status}")
            
            # Display payment statistics
            print(f"\n📊 PAYMENT STATISTICS")
            print("-" * 30)
            
            total_transactions = Transaction.objects.count()
            pending_transactions = Transaction.objects.filter(status='pending').count()
            completed_transactions = Transaction.objects.filter(status='completed').count()
            total_amount = Transaction.objects.aggregate(
                total=django.db.models.Sum('amount')
            )['total'] or Decimal('0')
            
            print(f"Total Transactions: {total_transactions}")
            print(f"Pending: {pending_transactions}")
            print(f"Completed: {completed_transactions}")
            print(f"Total Value: {total_amount} NGN")
            
            print(f"\n🔗 PAYMENT URL FOR TESTING:")
            print(f"{payment_result['payment_url']}")
            print(f"\n📋 To complete this demo:")
            print(f"1. Open the payment URL in a browser")
            print(f"2. Use Paystack test card: 4084084084084081")
            print(f"3. Any future date and CVV: 123")
            print(f"4. Verify payment using reference: {transaction.gateway_reference}")
            
        else:
            print(f"❌ Payment creation failed: {payment_result['error']}")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Import Django models
    import django.db.models
    
    demo_real_payment_integration()
