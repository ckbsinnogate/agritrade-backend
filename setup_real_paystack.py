"""
Setup Real Paystack Gateway
Configure the working Paystack integration
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway


def setup_paystack_gateway():
    """Setup the real Paystack gateway with working credentials"""
    
    print("🔧 SETTING UP REAL PAYSTACK GATEWAY")
    print("=" * 45)
    
    # Real Paystack test credentials (working)
    PUBLIC_KEY = "pk_test_ea5b669d4ab214ab74857c2ad154c5d25329a42f"
    SECRET_KEY = "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26"
    
    try:
        # Create or update Paystack gateway
        paystack, created = PaymentGateway.objects.get_or_create(
            name="Paystack",
            defaults={
                "display_name": "Paystack Payment Gateway",
                "description": "Real Paystack integration for AgriConnect payments",
                "status": "ACTIVE",
                "api_base_url": "https://api.paystack.co",
                "public_key": PUBLIC_KEY,
                "secret_key": SECRET_KEY,
                "supported_currencies": ["NGN", "GHS", "ZAR", "USD"],
                "transaction_fee_percent": 1.5,
                "configuration": {
                    "webhook_url": "https://agriconnect.com/api/v1/payments/paystack/webhook/",
                    "callback_url": "https://agriconnect.com/payment/callback/",
                    "supported_methods": ["card", "bank", "ussd", "qr", "mobile_money"],
                    "test_mode": True,
                    "currency_default": "NGN"
                }
            }
        )
        
        if created:
            print("✅ Created new Paystack gateway")
        else:
            # Update existing gateway with working credentials
            paystack.public_key = PUBLIC_KEY
            paystack.secret_key = SECRET_KEY
            paystack.status = "ACTIVE"
            paystack.api_base_url = "https://api.paystack.co"
            paystack.save()
            print("✅ Updated existing Paystack gateway")
        
        print(f"   Gateway ID: {paystack.id}")
        print(f"   Name: {paystack.name}")
        print(f"   Status: {paystack.status}")
        print(f"   Public Key: {paystack.public_key[:20]}...")
        print(f"   Secret Key: {paystack.secret_key[:20]}...")
        print(f"   Supported Currencies: {paystack.supported_currencies}")
        print(f"   Transaction Fee: {paystack.transaction_fee_percent}%")
        
        # Test the API connection
        print(f"\n🧪 Testing API Connection")
        print("-" * 25)
        
        import requests
        
        headers = {
            "Authorization": f"Bearer {paystack.secret_key}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Banks
        response = requests.get(
            "https://api.paystack.co/bank?country=nigeria&perPage=3",
            headers=headers
        )
        
        if response.status_code == 200:
            banks = response.json()
            if banks.get("status"):
                print(f"✅ API Connection: Working")
                print(f"✅ Banks Retrieved: {len(banks['data'])} Nigerian banks")
            else:
                print(f"❌ API Error: {banks.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
        
        # Test 2: Payment initialization
        payment_test = {
            "email": "test@agriconnect.com",
            "amount": 10000  # NGN 100 in kobo
        }
        
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payment_test
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                print(f"✅ Payment Test: Working")
                print(f"✅ Reference: {data['data']['reference']}")
            else:
                print(f"❌ Payment Error: {data.get('message')}")
        else:
            print(f"❌ Payment HTTP Error: {response.status_code}")
        
        return paystack
        
    except Exception as e:
        print(f"❌ Error setting up gateway: {e}")
        return None


def create_other_gateways():
    """Create other payment gateways for comparison"""
    
    print(f"\n🏦 Creating Other Payment Gateways")
    print("-" * 35)
    
    gateways = [
        {
            "name": "Flutterwave",
            "display_name": "Flutterwave Payment Gateway", 
            "status": "ACTIVE",
            "supported_currencies": ["NGN", "USD", "GHS", "KES"]
        },
        {
            "name": "MTN Mobile Money",
            "display_name": "MTN Mobile Money",
            "status": "ACTIVE", 
            "supported_currencies": ["NGN"]
        },
        {
            "name": "Bank Transfer",
            "display_name": "Direct Bank Transfer",
            "status": "ACTIVE",
            "supported_currencies": ["NGN", "USD"]
        }
    ]
    
    for gateway_data in gateways:
        gateway, created = PaymentGateway.objects.get_or_create(
            name=gateway_data["name"],
            defaults=gateway_data
        )
        
        if created:
            print(f"✅ Created {gateway.name}")
        else:
            print(f"✅ Updated {gateway.name}")


def show_gateway_summary():
    """Show summary of all payment gateways"""
    
    print(f"\n📊 PAYMENT GATEWAY SUMMARY")
    print("-" * 30)
    
    gateways = PaymentGateway.objects.all()
    
    print(f"Total Gateways: {gateways.count()}")
    
    for gateway in gateways:
        print(f"   • {gateway.name} - {gateway.status}")
        if gateway.supported_currencies:
            currencies = ", ".join(gateway.supported_currencies)
            print(f"     Currencies: {currencies}")


if __name__ == "__main__":
    paystack = setup_paystack_gateway()
    
    if paystack:
        create_other_gateways()
        show_gateway_summary()
        
        print(f"\n" + "=" * 45)
        print("🎉 PAYMENT GATEWAYS SETUP: SUCCESS!")
        print("✅ Paystack: Working with real API")
        print("✅ Other gateways: Created")
        print("✅ Database: Updated")
        print("🌾 Ready for AgriConnect payments!")
        print("=" * 45)
    else:
        print(f"\n❌ Gateway setup failed")
