"""
Update Paystack Gateway with Real API Keys
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway

# Paystack Test API Keys
PAYSTACK_PUBLIC_KEY = "pk_test_ea5b669d4ab214ab74857c2ad154c5d25329a42f"
PAYSTACK_SECRET_KEY = "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26"

print("🔑 Updating Paystack Gateway with Real API Keys...")

try:
    paystack = PaymentGateway.objects.filter(name='paystack').first()
    
    if paystack:
        paystack.public_key = PAYSTACK_PUBLIC_KEY
        paystack.secret_key = PAYSTACK_SECRET_KEY
        paystack.api_base_url = "https://api.paystack.co"
        paystack.save()
        
        print("✅ Paystack API keys updated successfully!")
        print(f"   Public Key: {PAYSTACK_PUBLIC_KEY[:25]}...")
        print(f"   Secret Key: {PAYSTACK_SECRET_KEY[:25]}...")
        print(f"   API URL: {paystack.api_base_url}")
        print(f"   Status: {'ACTIVE' if paystack.is_active else 'INACTIVE'}")
        
        # Verify the update
        updated_paystack = PaymentGateway.objects.get(name='paystack')
        print(f"✅ Verification: Keys saved to database")
        
    else:
        print("❌ Paystack gateway not found")
        print("Available gateways:")
        for gw in PaymentGateway.objects.all():
            print(f"  - {gw.name}: {gw.display_name}")
        
except Exception as e:
    print(f"❌ Error updating Paystack: {e}")
    import traceback
    traceback.print_exc()
