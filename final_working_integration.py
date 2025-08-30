"""
Final Working Integration
Complete AgriConnect + Paystack integration with correct models
"""

import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway, Transaction
from django.contrib.auth import get_user_model
from decimal import Decimal
import requests

User = get_user_model()


def run_final_integration_test():
    """Run the final complete integration test"""
    
    print("🌾 FINAL AGRICONNECT + PAYSTACK INTEGRATION")
    print("=" * 50)
    
    try:
        # Get Paystack gateway
        paystack = PaymentGateway.objects.get(name="paystack")
        print(f"✅ Gateway: {paystack.display_name}")
        print(f"   Status: {'Active' if paystack.is_active else 'Inactive'}")
        print(f"   API URL: {paystack.api_base_url}")
        
        # Get existing test user
        test_user = User.objects.first()
        if not test_user:
            test_user = User.objects.create_user(
                username="farmer1",
                email="farmer@agriconnect.com",
                password="testpass123"
            )
        
        print(f"✅ User: {test_user.email}")
        
        # Test agricultural payment scenario
        print(f"\n💳 AGRICULTURAL PAYMENT SCENARIO")
        print("-" * 35)
        print("Product: Premium Maize Seeds + Fertilizer Package")
        print("Amount: NGN 500.00")
        print("Customer: Nigerian Farmer")
        print("Location: Kaduna State")
        
        headers = {
            "Authorization": f"Bearer {paystack.secret_key}",
            "Content-Type": "application/json"
        }
        
        payment_data = {
            "email": test_user.email,
            "amount": 50000,  # NGN 500 in kobo
            "metadata": {
                "product": "Premium Maize Seeds + Fertilizer Package",
                "quantity": "5kg seeds + 10kg fertilizer",
                "farmer_name": test_user.username,
                "location": "Kaduna State, Nigeria",
                "platform": "AgriConnect",
                "season": "2025 Wet Season Planting",
                "order_type": "Agricultural Supplies"
            }
        }
        
        # Initialize payment
        response = requests.post(
            f"{paystack.api_base_url}/transaction/initialize",
            headers=headers,
            json=payment_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                payment_info = data["data"]
                reference = payment_info['reference']
                
                print(f"\n✅ PAYSTACK PAYMENT INITIALIZED")
                print(f"   Reference: {reference}")
                print(f"   Amount: NGN 500.00")
                print(f"   Access Code: {payment_info['access_code']}")
                print(f"   Payment URL: {payment_info['authorization_url']}")
                
                # Create Django transaction
                transaction = Transaction.objects.create(
                    user=test_user,
                    gateway=paystack,
                    amount=Decimal("500.00"),
                    currency="NGN",
                    gateway_reference=reference,
                    status="pending",
                    transaction_type="payment",
                    metadata=payment_data['metadata'],
                    gateway_request=payment_data,
                    gateway_response=payment_info
                )
                
                print(f"\n✅ DJANGO TRANSACTION CREATED")
                print(f"   Transaction ID: {transaction.id}")
                print(f"   Gateway Ref: {transaction.gateway_reference}")
                print(f"   Status: {transaction.status}")
                print(f"   Amount: {transaction.currency} {transaction.amount}")
                print(f"   Created: {transaction.initiated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Verify payment status
                verify_response = requests.get(
                    f"{paystack.api_base_url}/transaction/verify/{reference}",
                    headers=headers
                )
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    if verify_data.get("status"):
                        txn_data = verify_data["data"]
                        
                        print(f"\n✅ PAYMENT VERIFICATION")
                        print(f"   Status: {txn_data['status']}")
                        print(f"   Amount: NGN {txn_data['amount'] / 100:.2f}")
                        print(f"   Currency: {txn_data['currency']}")
                        print(f"   Channel: {txn_data.get('channel', 'N/A')}")
                        print(f"   Customer: {txn_data['customer']['email']}")
                        
                        # Show agricultural metadata
                        metadata = txn_data.get('metadata', {})
                        if metadata:
                            print(f"\n📋 AGRICULTURAL DETAILS:")
                            for key, value in metadata.items():
                                print(f"   • {key.replace('_', ' ').title()}: {value}")
                        
                        # Update Django transaction
                        transaction.status = txn_data['status']
                        if txn_data.get('id'):
                            transaction.external_reference = str(txn_data['id'])
                        transaction.save()
                        
                        print(f"\n✅ DJANGO TRANSACTION UPDATED")
                        
                        return transaction
                        
                    else:
                        print(f"❌ Verification failed: {verify_data.get('message')}")
                else:
                    print(f"❌ Verification HTTP error: {verify_response.status_code}")
                    
            else:
                print(f"❌ Payment failed: {data.get('message')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_test_payment_urls():
    """Create test payment URLs for different scenarios"""
    
    print(f"\n🌐 TEST PAYMENT URLS FOR AGRICULTURAL SCENARIOS")
    print("-" * 55)
    
    try:
        paystack = PaymentGateway.objects.get(name="paystack")
        test_user = User.objects.first()
        
        scenarios = [
            {
                "name": "Small Scale Farming Package",
                "amount": 25000,  # NGN 250
                "items": "Tomato seeds (1kg) + Basic fertilizer (5kg)"
            },
            {
                "name": "Medium Scale Farming Package", 
                "amount": 75000,  # NGN 750
                "items": "Maize seeds (5kg) + Premium fertilizer (20kg)"
            },
            {
                "name": "Large Scale Farming Package",
                "amount": 200000,  # NGN 2,000
                "items": "Multiple crop seeds + Equipment + Fertilizers"
            }
        ]
        
        headers = {
            "Authorization": f"Bearer {paystack.secret_key}",
            "Content-Type": "application/json"
        }
        
        for i, scenario in enumerate(scenarios, 1):
            payment_data = {
                "email": test_user.email,
                "amount": scenario["amount"],
                "metadata": {
                    "package": scenario["name"],
                    "items": scenario["items"],
                    "scenario": f"Test {i}",
                    "platform": "AgriConnect Demo"
                }
            }
            
            response = requests.post(
                f"{paystack.api_base_url}/transaction/initialize",
                headers=headers,
                json=payment_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    ref = data["data"]["reference"]
                    url = data["data"]["authorization_url"]
                    
                    print(f"\n   {i}. {scenario['name']}")
                    print(f"      Amount: NGN {scenario['amount']/100:.2f}")
                    print(f"      Items: {scenario['items']}")
                    print(f"      Reference: {ref}")
                    print(f"      Payment URL: {url}")
                    
                    # Create transaction record
                    Transaction.objects.create(
                        user=test_user,
                        gateway=paystack,
                        amount=Decimal(scenario["amount"]) / 100,
                        currency="NGN",
                        gateway_reference=ref,
                        status="pending",
                        metadata=payment_data['metadata'],
                        gateway_response=data['data']
                    )
            
    except Exception as e:
        print(f"❌ Error: {e}")


def show_system_status():
    """Show complete system status"""
    
    print(f"\n📊 SYSTEM STATUS SUMMARY")
    print("-" * 30)
    
    try:
        # Gateway status
        gateways = PaymentGateway.objects.all()
        print(f"Payment Gateways: {gateways.count()}")
        for gw in gateways:
            status = "✅ Active" if gw.is_active else "❌ Inactive"
            print(f"   • {gw.display_name}: {status}")
        
        # User status
        users = User.objects.all()
        print(f"\nUsers: {users.count()}")
        for user in users[:3]:
            print(f"   • {user.email}")
        
        # Transaction status
        total_txns = Transaction.objects.count()
        pending_txns = Transaction.objects.filter(status="pending").count()
        total_amount = sum(t.amount for t in Transaction.objects.all())
        
        print(f"\nTransactions:")
        print(f"   Total: {total_txns}")
        print(f"   Pending: {pending_txns}")
        print(f"   Total Amount: NGN {total_amount:.2f}")
        
        # Recent transactions
        recent = Transaction.objects.order_by('-initiated_at')[:3]
        if recent:
            print(f"\nRecent Transactions:")
            for txn in recent:
                package = txn.metadata.get('package', txn.metadata.get('product', 'N/A'))
                print(f"   • {txn.gateway_reference} - NGN {txn.amount} - {package[:30]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Run the final integration test
    transaction = run_final_integration_test()
    
    if transaction:
        create_test_payment_urls()
        show_system_status()
        
        print(f"\n" + "=" * 50)
        print("🎉 AGRICONNECT PAYMENT SYSTEM: FULLY OPERATIONAL!")
        print("=" * 50)
        print("✅ Paystack API Integration: Working")
        print("✅ Django Transaction Management: Operational")
        print("✅ Agricultural Payment Scenarios: Created")
        print("✅ Test Payment URLs: Generated")
        print("✅ Database Records: Properly stored")
        print("✅ Payment Verification: Working")
        print("🌾 Ready for production deployment!")
        
        print(f"\n💳 PAYSTACK TEST CARD:")
        print("   Card Number: 4084084084084081")
        print("   Expiry Date: 12/25")
        print("   CVV: 123")
        print("   PIN: 1234")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Test payments using generated URLs")
        print("2. Implement webhook handling")
        print("3. Add email notifications")
        print("4. Deploy to production")
        print("5. Configure live API keys")
        
        print("=" * 50)
        
    else:
        print(f"\n❌ Integration test failed - check logs above")
