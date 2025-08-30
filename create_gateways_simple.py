"""
Simple Payment Gateway Creator for AgriConnect
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway

# Create Paystack Gateway
paystack = PaymentGateway.objects.create(
    name='paystack',
    display_name='Paystack',
    is_active=True,
    supported_currencies=['NGN', 'GHS', 'ZAR', 'USD'],
    supported_countries=['NG', 'GH', 'ZA'],
    gateway_config={
        'api_url': 'https://api.paystack.co',
        'supported_methods': ['card', 'bank_transfer', 'ussd'],
        'test_mode': True
    }
)

# Create Flutterwave Gateway
flutterwave = PaymentGateway.objects.create(
    name='flutterwave',
    display_name='Flutterwave',
    is_active=True,
    supported_currencies=['NGN', 'GHS', 'KES', 'USD'],
    supported_countries=['NG', 'GH', 'KE', 'UG'],
    gateway_config={
        'api_url': 'https://api.flutterwave.com/v3',
        'supported_methods': ['card', 'mobile_money', 'bank_transfer'],
        'test_mode': True
    }
)

# Create MTN Mobile Money
mtn = PaymentGateway.objects.create(
    name='mtn_mobile_money',
    display_name='MTN Mobile Money',
    is_active=True,
    supported_currencies=['GHS', 'UGX'],
    supported_countries=['GH', 'UG'],
    gateway_config={
        'supported_methods': ['mobile_money'],
        'test_mode': True
    }
)

print("✅ Payment gateways created successfully!")
print(f"Total gateways: {PaymentGateway.objects.count()}")

for gateway in PaymentGateway.objects.all():
    print(f"- {gateway.display_name} ({gateway.name})")
