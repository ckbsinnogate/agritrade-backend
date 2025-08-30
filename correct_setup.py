"""Correct Paystack Setup with proper field names"""

import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway

print("Setting up Paystack gateway...")

# Create Paystack gateway with correct field names
paystack, created = PaymentGateway.objects.get_or_create(
    name="paystack",  # Use the choice value, not display name
    defaults={
        "display_name": "Paystack Payment Gateway",
        "is_active": True,  # Use is_active, not status
        "api_base_url": "https://api.paystack.co",
        "public_key": "pk_test_ea5b669d4ab214ab74857c2ad154c5d25329a42f",
        "secret_key": "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26",
        "supported_currencies": ["NGN", "USD", "GHS"],
        "supported_countries": ["NG", "GH"],
        "supported_payment_methods": ["card", "bank_transfer", "ussd"],
        "transaction_fee_percentage": 1.5000,
        "minimum_amount": 100.00  # NGN 1.00 minimum
    }
)

print(f"Paystack gateway {'created' if created else 'found'}: ID {paystack.id}")
print(f"Name: {paystack.name}")
print(f"Display: {paystack.display_name}")
print(f"Active: {paystack.is_active}")
print(f"API URL: {paystack.api_base_url}")

# Test API connection
import requests

headers = {
    "Authorization": f"Bearer {paystack.secret_key}",
    "Content-Type": "application/json"
}

print("\nTesting API connection...")

# Test payment initialization
data = {
    "email": "farmer@agriconnect.com", 
    "amount": 25000,  # NGN 250
    "metadata": {
        "product": "Maize Seeds",
        "farmer": "John Doe"
    }
}

response = requests.post(
    "https://api.paystack.co/transaction/initialize",
    headers=headers,
    json=data
)

if response.status_code == 200:
    result = response.json()
    if result.get("status"):
        print(f"✅ API Test SUCCESS!")
        print(f"   Reference: {result['data']['reference']}")
        print(f"   Amount: NGN 250.00")
        print(f"   URL: {result['data']['authorization_url'][:50]}...")
    else:
        print(f"❌ API Error: {result.get('message')}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
    print(f"Response: {response.text}")

print("\nSetup complete!")
