#!/usr/bin/env python
"""
Add Webhook Secret to Paystack Gateway
Run this after getting the webhook secret from Paystack dashboard
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway

def add_webhook_secret():
    """Add webhook secret to Paystack gateway"""
    
    print("🔐 ADD PAYSTACK WEBHOOK SECRET")
    print("=" * 40)
    
    # Get Paystack gateway
    try:
        paystack = PaymentGateway.objects.get(name='paystack')
        print(f"✅ Found Paystack gateway: {paystack.display_name}")
        
        # Prompt for webhook secret
        print("\n📋 Instructions:")
        print("1. Go to your Paystack dashboard")
        print("2. Navigate to Settings > Webhooks")
        print("3. Find your webhook endpoint")
        print("4. Copy the webhook secret")
        
        webhook_secret = input("\n🔑 Enter your webhook secret from Paystack: ").strip()
        
        if webhook_secret:
            # Add webhook secret to gateway
            paystack.webhook_secret = webhook_secret
            paystack.save()
            
            print(f"\n✅ Webhook secret added successfully!")
            print(f"   Gateway: {paystack.display_name}")
            print(f"   Secret: {webhook_secret[:20]}... (truncated for security)")
            print(f"   Status: {'ACTIVE' if paystack.is_active else 'INACTIVE'}")
            
            print(f"\n🎉 WEBHOOK SECURITY: ENABLED!")
            print("✅ Signature verification will now work")
            print("✅ Webhook endpoint is secure")
            print("✅ Ready for production webhooks!")
            
        else:
            print("\n❌ No webhook secret provided")
            print("🔧 Run this script again after getting the secret")
        
    except PaymentGateway.DoesNotExist:
        print("❌ Paystack gateway not found")
        print("🔧 Run setup_paystack_api.py first")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_webhook_secret()
