"""Quick Paystack Setup"""

import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

# Setup Django
django.setup()

# Now import models
from payments.models import PaymentGateway

# Create Paystack gateway
paystack, created = PaymentGateway.objects.get_or_create(
    name="Paystack",
    defaults={
        "display_name": "Paystack",
        "status": "ACTIVE",
        "api_base_url": "https://api.paystack.co",
        "public_key": "pk_test_ea5b669d4ab214ab74857c2ad154c5d25329a42f",
        "secret_key": "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26",
        "supported_currencies": ["NGN"],
        "transaction_fee_percent": 1.5
    }
)

print(f"Paystack gateway {'created' if created else 'updated'}: {paystack.id}")

# Test basic API
import requests

headers = {
    "Authorization": f"Bearer {paystack.secret_key}",
    "Content-Type": "application/json"
}

# Quick payment test
data = {"email": "test@example.com", "amount": 10000}
response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    if result.get("status"):
        print(f"API Test: SUCCESS - Reference: {result['data']['reference']}")
    else:
        print(f"API Test: FAILED - {result.get('message')}")
else:
    print(f"API Test: HTTP Error {response.status_code}")

print("Setup complete!")
