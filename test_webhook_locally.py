#!/usr/bin/env python
"""
Local Webhook Testing - Simulate Paystack Webhook Events
Test webhook functionality without external Paystack calls
"""

import os
import sys
import django
import json
import hashlib
import hmac
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway, Transaction
from authentication.models import User
import requests

def simulate_webhook_event(event_type='charge.success', transaction_id=None):
    """Simulate a Paystack webhook event"""
    
    print(f"🔔 SIMULATING WEBHOOK EVENT: {event_type}")
    print("=" * 50)
    
    try:
        # Get or create a test transaction
        if transaction_id:
            try:
                transaction = Transaction.objects.get(id=transaction_id)
                print(f"✅ Using existing transaction: {transaction.id}")
            except Transaction.DoesNotExist:
                print(f"❌ Transaction {transaction_id} not found")
                return
        else:
            # Create a test transaction
            user = User.objects.first()
            if not user:
                print("❌ No users found. Create a user first.")
                return
                
            paystack = PaymentGateway.objects.get(name='paystack')
            
            transaction = Transaction.objects.create(
                user=user,
                gateway=paystack,
                amount=Decimal('500.00'),
                currency='NGN',
                status='pending',
                gateway_reference=f'test_webhook_{event_type}_{len(Transaction.objects.all())}',
                metadata={
                    'product': 'Webhook Test Transaction',
                    'test': True
                }
            )
            print(f"✅ Created test transaction: {transaction.id}")
        
        # Create webhook payload
        webhook_data = {
            "event": event_type,
            "data": {
                "id": int(transaction.gateway_reference.split('_')[-1]) if transaction.gateway_reference else 12345,
                "domain": "test",
                "status": "success" if "success" in event_type else "failed",
                "reference": transaction.gateway_reference or f"test_ref_{transaction.id}",
                "amount": int(float(transaction.amount) * 100),  # Convert to kobo
                "message": "Approved" if "success" in event_type else "Declined",
                "gateway_response": "Successful" if "success" in event_type else "Declined",
                "paid_at": "2025-07-04T10:30:00.000Z",
                "created_at": "2025-07-04T10:25:00.000Z",
                "channel": "card",
                "currency": transaction.currency,
                "ip_address": "127.0.0.1",
                "metadata": transaction.metadata or {},
                "customer": {
                    "id": transaction.user.id,
                    "first_name": getattr(transaction.user, 'first_name', 'Test'),
                    "last_name": getattr(transaction.user, 'last_name', 'User'),
                    "email": transaction.user.email
                },
                "authorization": {
                    "authorization_code": "AUTH_test123",
                    "bin": "408408",
                    "last4": "4081",
                    "exp_month": "12",
                    "exp_year": "2030",
                    "channel": "card",
                    "card_type": "visa DEBIT",
                    "bank": "Test Bank",
                    "country_code": "NG",
                    "brand": "visa",
                    "reusable": True,
                    "signature": "SIG_test123"
                }
            }
        }
        
        # Convert to JSON
        payload_json = json.dumps(webhook_data)
        print(f"\n📦 Webhook Payload:")
        print(json.dumps(webhook_data, indent=2))
        
        # Generate signature (if webhook secret exists)
        paystack = PaymentGateway.objects.get(name='paystack')
        if paystack.webhook_secret:
            signature = hmac.new(
                paystack.webhook_secret.encode('utf-8'),
                payload_json.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            print(f"\n🔐 Generated Signature: {signature[:40]}...")
        else:
            signature = "test_signature_no_secret_set"
            print(f"\n⚠️  No webhook secret set - using test signature")
        
        # Send to local webhook endpoint
        webhook_url = "http://localhost:8000/api/v1/payments/webhook/paystack/"
        headers = {
            'Content-Type': 'application/json',
            'X-Paystack-Signature': signature
        }
        
        print(f"\n🚀 Sending webhook to: {webhook_url}")
        
        try:
            response = requests.post(
                webhook_url,
                data=payload_json,
                headers=headers,
                timeout=30
            )
            
            print(f"\n📨 Webhook Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Check transaction status after webhook
            transaction.refresh_from_db()
            print(f"\n📊 Transaction Status After Webhook:")
            print(f"   ID: {transaction.id}")
            print(f"   Status: {transaction.status}")
            print(f"   Gateway Ref: {transaction.gateway_reference}")
            print(f"   Amount: {transaction.amount} {transaction.currency}")
            
            if response.status_code == 200:
                print(f"\n✅ Webhook simulation successful!")
                if "success" in event_type and transaction.status == 'completed':
                    print("✅ Transaction status updated correctly!")
                elif "failed" in event_type and transaction.status == 'failed':
                    print("✅ Transaction status updated correctly!")
                else:
                    print("⚠️  Transaction status may not have updated as expected")
            else:
                print(f"\n❌ Webhook simulation failed!")
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Could not connect to webhook endpoint")
            print("🔧 Make sure Django server is running: python manage.py runserver")
        except Exception as e:
            print(f"\n❌ Error sending webhook: {e}")
            
    except Exception as e:
        print(f"❌ Error in webhook simulation: {e}")

def test_all_webhook_events():
    """Test all major webhook events"""
    
    events = [
        'charge.success',
        'charge.failed',
        'transfer.success',
        'transfer.failed'
    ]
    
    print("🧪 TESTING ALL WEBHOOK EVENTS")
    print("=" * 40)
    
    for event in events:
        print(f"\n🔔 Testing {event}...")
        simulate_webhook_event(event)
        print(f"✅ {event} test completed")
        print("-" * 30)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Paystack webhooks locally')
    parser.add_argument('--event', default='charge.success', 
                       help='Webhook event type (charge.success, charge.failed, etc.)')
    parser.add_argument('--transaction', type=str, 
                       help='Transaction ID to use (optional)')
    parser.add_argument('--all', action='store_true', 
                       help='Test all webhook events')
    
    args = parser.parse_args()
    
    if args.all:
        test_all_webhook_events()
    else:
        simulate_webhook_event(args.event, args.transaction)
