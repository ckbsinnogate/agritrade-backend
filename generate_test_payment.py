"""
Generate Test Payment URL
Create a real Paystack payment URL for immediate testing
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

def generate_live_payment_url():
    """Generate a live payment URL for testing"""
    
    print("💳 GENERATE LIVE AGRICONNECT PAYMENT URL")
    print("=" * 50)
    
    try:
        # Get Paystack gateway
        paystack = PaymentGateway.objects.get(name='paystack')
        print(f"✅ Using gateway: {paystack.display_name}")
        
        # Get or create test user
        User = get_user_model()
        test_user = User.objects.first()
        if not test_user:
            print("❌ No users found. Create a user first.")
            return None
        
        print(f"✅ Customer: {test_user.email}")
          # Agricultural payment scenarios (Ghana)
        scenarios = [
            {
                "name": "Premium Maize Seeds Package",
                "amount": 50,  # GHS 50
                "description": "5kg premium maize seeds + starter fertilizer",
                "farmer_type": "Small-scale farmer",
                "location": "Ashanti Region"
            },
            {
                "name": "Commercial Fertilizer Package", 
                "amount": 125,  # GHS 125
                "description": "25kg NPK fertilizer + organic compost",
                "farmer_type": "Commercial farmer",
                "location": "Northern Region"
            },
            {
                "name": "Irrigation Starter Kit",
                "amount": 250,  # GHS 250
                "description": "Drip irrigation system for 1 acre",
                "farmer_type": "Progressive farmer",
                "location": "Greater Accra Region"
            }
        ]
        
        print(f"\n📦 AVAILABLE AGRICULTURAL PACKAGES (GHANA):")
        print("-" * 45)
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['name']}")
            print(f"   Amount: GHS {scenario['amount']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Target: {scenario['farmer_type']}")
            print(f"   Location: {scenario['location']}\n")
        
        # Let's create payment URLs for all scenarios
        payment_urls = []
        
        headers = {
            "Authorization": f"Bearer {paystack.secret_key}",
            "Content-Type": "application/json"
        }
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"Creating payment for scenario {i}...")
            
            payment_data = {
                "email": test_user.email,
                "amount": scenario["amount"] * 100,  # Convert to kobo
                "metadata": {
                    "package_name": scenario["name"],
                    "description": scenario["description"],
                    "farmer_type": scenario["farmer_type"],
                    "location": scenario["location"],
                    "platform": "AgriConnect",
                    "season": "2025 Wet Season",
                    "order_type": "Agricultural Package"
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
                    payment_info = data["data"]
                    reference = payment_info['reference']
                    auth_url = payment_info['authorization_url']
                      # Create Django transaction (Ghana Cedis)
                    transaction = Transaction.objects.create(
                        user=test_user,
                        gateway=paystack,
                        amount=Decimal(str(scenario["amount"])),
                        currency="GHS",
                        gateway_reference=reference,
                        status="pending",
                        metadata=payment_data['metadata'],
                        gateway_response=payment_info
                    )
                    
                    payment_urls.append({
                        'scenario': scenario,
                        'reference': reference,
                        'url': auth_url,
                        'transaction_id': transaction.id
                    })
                    
                    print(f"   ✅ Created: {reference}")
                else:
                    print(f"   ❌ Failed: {data.get('message')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        
        # Display payment URLs
        print(f"\n🌐 LIVE PAYMENT URLS FOR TESTING")
        print("=" * 45)
        
        for payment in payment_urls:
            scenario = payment['scenario']
            print(f"\n📦 {scenario['name']}")
            print(f"💰 Amount: NGN {scenario['amount']}")
            print(f"📍 Location: {scenario['location']}")
            print(f"🔗 Payment URL:")
            print(f"   {payment['url']}")
            print(f"📋 Reference: {payment['reference']}")
            print(f"🆔 Transaction ID: {payment['transaction_id']}")
            print("-" * 45)
        
        # Test card information
        print(f"\n💳 PAYSTACK TEST CARD DETAILS")
        print("-" * 35)
        print("Card Number: 4084084084084081")
        print("Expiry Date: 12/25")
        print("CVV: 123")
        print("PIN: 1234")
        
        print(f"\n📱 PAYMENT TESTING INSTRUCTIONS")
        print("-" * 40)
        print("1. Click any payment URL above")
        print("2. Enter the test card details")
        print("3. Complete the payment flow")
        print("4. Check Django admin for transaction updates")
        print("5. Monitor webhook notifications (if configured)")
        
        return payment_urls
        
    except PaymentGateway.DoesNotExist:
        print("❌ Paystack gateway not found")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    payment_urls = generate_live_payment_url()
    
    if payment_urls:
        print(f"\n" + "=" * 50)
        print("🎉 LIVE PAYMENT URLS GENERATED!")
        print(f"✅ Created {len(payment_urls)} agricultural payment scenarios")
        print("✅ Django transactions recorded")
        print("✅ Ready for immediate testing")
        print("🌾 Test AgriConnect payments now!")
        print("=" * 50)
    else:
        print(f"\n❌ Failed to generate payment URLs")
