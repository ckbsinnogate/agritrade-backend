#!/usr/bin/env python
"""
Production Webhook Setup for Paystack
This script helps configure webhooks for production deployment
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway

def setup_production_webhook():
    """Setup webhook configuration for production deployment"""
    
    print("🌐 PAYSTACK WEBHOOK PRODUCTION SETUP")
    print("=" * 50)
    
    try:
        paystack = PaymentGateway.objects.get(name='paystack')
        print(f"✅ Found Paystack gateway: {paystack.display_name}")
        
        print(f"\n📊 Current Configuration:")
        print(f"   Status: {'ACTIVE' if paystack.is_active else 'INACTIVE'}")
        print(f"   API URL: {paystack.api_url}")
        print(f"   Public Key: {paystack.public_key[:20]}...")
        print(f"   Secret Key: {paystack.secret_key[:20]}...")
        print(f"   Webhook Secret: {'SET' if paystack.webhook_secret else 'NOT SET'}")
        
        print(f"\n🔧 PRODUCTION DEPLOYMENT STEPS:")
        print("=" * 40)
        
        print("\n1️⃣ DEPLOY YOUR APPLICATION")
        print("   - Deploy to a hosting service (Heroku, Railway, DigitalOcean, etc.)")
        print("   - Ensure your domain is accessible over HTTPS")
        print("   - Example: https://your-agriconnect-app.herokuapp.com")
        
        print("\n2️⃣ CONFIGURE PAYSTACK WEBHOOK")
        print("   - Login to https://dashboard.paystack.com/")
        print("   - Go to Settings > Webhooks")
        print("   - Click 'Add Endpoint'")
        print("   - Webhook URL: https://your-domain.com/api/v1/payments/webhook/paystack/")
        print("   - Select Events:")
        print("     ✓ charge.success")
        print("     ✓ charge.failed")
        print("     ✓ transfer.success")
        print("     ✓ transfer.failed")
        print("     ✓ transfer.reversed")
        
        print("\n3️⃣ GET WEBHOOK SECRET")
        print("   - After creating the webhook, copy the webhook secret")
        print("   - Add it to your production environment variables")
        print("   - Or run this script in production to add it to the database")
        
        print("\n4️⃣ LOCAL TESTING ALTERNATIVES")
        print("   Since Paystack doesn't accept localhost:")
        print("   a) Use ngrok to expose your local server:")
        print("      - Install ngrok: https://ngrok.com/")
        print("      - Run: ngrok http 8000")
        print("      - Use the https URL for webhook testing")
        print("   b) Use Paystack's webhook simulator in dashboard")
        print("   c) Test webhook logic with manual API calls")
        
        # Offer to set webhook secret if provided
        choice = input("\n❓ Do you have a webhook secret to add now? (y/n): ").lower().strip()
        
        if choice == 'y':
            webhook_secret = input("🔑 Enter webhook secret: ").strip()
            if webhook_secret:
                paystack.webhook_secret = webhook_secret
                paystack.save()
                print(f"\n✅ Webhook secret added!")
                print(f"   Secret: {webhook_secret[:20]}... (truncated)")
            else:
                print("❌ No secret provided")
        
        print(f"\n🎯 WEBHOOK ENDPOINT READY:")
        print(f"   Development: http://localhost:8000/api/v1/payments/webhook/paystack/")
        print(f"   Production:  https://your-domain.com/api/v1/payments/webhook/paystack/")
        print(f"   Test URL:    http://localhost:8000/api/v1/payments/webhook/test/")
        
        print(f"\n✅ Your webhook handler is fully implemented and ready!")
        
    except PaymentGateway.DoesNotExist:
        print("❌ Paystack gateway not found")
        print("🔧 Run setup_paystack_api.py first")
    except Exception as e:
        print(f"❌ Error: {e}")

def create_ngrok_instructions():
    """Create instructions for using ngrok for local testing"""
    
    instructions = """
# NGROK SETUP FOR LOCAL WEBHOOK TESTING

## Install ngrok
1. Go to https://ngrok.com/
2. Sign up for free account
3. Download ngrok for Windows
4. Extract to a folder in your PATH

## Use ngrok for webhook testing
1. Start your Django server:
   ```
   python manage.py runserver 8000
   ```

2. In another terminal, start ngrok:
   ```
   ngrok http 8000
   ```

3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

4. Use this URL in Paystack dashboard:
   ```
   Webhook URL: https://abc123.ngrok.io/api/v1/payments/webhook/paystack/
   ```

## Alternative: Test webhook locally
You can test the webhook logic without external calls by using our test endpoint:
```
POST http://localhost:8000/api/v1/payments/webhook/test/
```

This simulates webhook events for testing purposes.
"""
    
    with open('NGROK_WEBHOOK_SETUP.md', 'w') as f:
        f.write(instructions)
    
    print("📝 Created NGROK_WEBHOOK_SETUP.md with detailed instructions")

if __name__ == "__main__":
    setup_production_webhook()
    create_ngrok_instructions()
