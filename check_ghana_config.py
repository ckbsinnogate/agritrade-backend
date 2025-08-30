#!/usr/bin/env python
"""
Check Ghana Configuration Status
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway

def check_ghana_config():
    """Check if Ghana configuration is applied"""
    
    print("🇬🇭 CHECKING GHANA CONFIGURATION")
    print("=" * 40)
    
    try:
        paystack = PaymentGateway.objects.get(name='paystack')
        
        print(f"✅ Gateway Found: {paystack.display_name}")
        print(f"✅ Status: {'ACTIVE' if paystack.is_active else 'INACTIVE'}")
        print(f"✅ Supported Currencies: {paystack.supported_currencies}")
        print(f"✅ Primary Currency: {paystack.supported_currencies[0] if paystack.supported_currencies else 'None'}")
        print(f"✅ Countries: {paystack.supported_countries}")
        print(f"✅ Payment Methods: {paystack.supported_payment_methods}")
        print(f"✅ Fixed Fee: {paystack.fixed_fee}")
        
        if paystack.supported_currencies and paystack.supported_currencies[0] == 'GHS':
            print(f"\n🎉 GHANA CONFIGURATION: SUCCESS!")
            print(f"   Primary Currency: Ghana Cedis (GHS)")
            print(f"   System Ready for Ghana operations")
        else:
            print(f"\n⚠️  GHANA CONFIGURATION: NEEDS UPDATE")
            print(f"   Current Primary: {paystack.supported_currencies[0] if paystack.supported_currencies else 'None'}")
            print(f"   Expected: GHS")
            
    except PaymentGateway.DoesNotExist:
        print("❌ Paystack gateway not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_ghana_config()
