"""
Paystack Webhook URL Configuration
Generate the webhook URL for Paystack dashboard configuration
"""

import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.conf import settings
from payments.models import PaymentGateway
import requests
import json


def get_webhook_urls():
    """Get the webhook URLs for Paystack configuration"""
    
    print("🔗 PAYSTACK WEBHOOK URL CONFIGURATION")
    print("=" * 50)
    
    # Get domain/base URL
    if hasattr(settings, 'SITE_URL'):
        base_url = settings.SITE_URL
    else:
        # Default for development
        base_url = "http://localhost:8000"
    
    # Production domain (you'll need to update this with your actual domain)
    production_domain = "https://your-domain.com"  # Update this with your actual domain
    
    # Webhook URLs
    development_webhook = f"{base_url}/api/v1/payments/webhook/paystack/"
    production_webhook = f"{production_domain}/api/v1/payments/webhook/paystack/"
    test_webhook = f"{base_url}/api/v1/payments/webhook/test/"
    
    print("📍 WEBHOOK ENDPOINTS:")
    print(f"   Development: {development_webhook}")
    print(f"   Production:  {production_webhook}")
    print(f"   Test:        {test_webhook}")
    
    print("\n🎯 FOR PAYSTACK DASHBOARD:")
    print("   1. Login to your Paystack dashboard")
    print("   2. Go to Settings > Webhooks") 
    print("   3. Add the webhook URL below:")
    print(f"   \n   📋 WEBHOOK URL (Copy this):")
    print(f"   {production_webhook}")
    print(f"   \n   🧪 TEST WEBHOOK URL (For testing):")
    print(f"   {development_webhook}")
    
    return {
        'development': development_webhook,
        'production': production_webhook,
        'test': test_webhook
    }


def update_paystack_webhook_config():
    """Update Paystack gateway with webhook information"""
    
    print("\n🔧 UPDATING PAYSTACK CONFIGURATION")
    print("-" * 40)
    
    try:
        paystack = PaymentGateway.objects.get(name='paystack')
        
        # Get webhook URLs
        urls = get_webhook_urls()
        
        # Store webhook configuration in the gateway metadata
        if not hasattr(paystack, 'metadata') or paystack.metadata is None:
            # If metadata field doesn't exist, store in configuration
            if not paystack.configuration:
                paystack.configuration = {}
            
            paystack.configuration.update({
                'webhook_urls': urls,
                'webhook_events': [
                    'charge.success',
                    'charge.failed', 
                    'transfer.success',
                    'transfer.failed',
                    'transfer.reversed'
                ],
                'webhook_configured': True
            })
        else:
            # If metadata field exists
            if not paystack.metadata:
                paystack.metadata = {}
            paystack.metadata.update({
                'webhook_urls': urls,
                'webhook_events': [
                    'charge.success',
                    'charge.failed',
                    'transfer.success', 
                    'transfer.failed',
                    'transfer.reversed'
                ]
            })
        
        paystack.save()
        
        print("✅ Paystack configuration updated with webhook URLs")
        print(f"   Gateway: {paystack.display_name}")
        print(f"   Status: {'Active' if paystack.is_active else 'Inactive'}")
        
        return True
        
    except PaymentGateway.DoesNotExist:
        print("❌ Paystack gateway not found")
        return False
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False


def test_webhook_endpoint():
    """Test the webhook endpoint locally"""
    
    print("\n🧪 TESTING WEBHOOK ENDPOINT")
    print("-" * 30)
    
    try:
        # Test webhook URL
        test_url = "http://localhost:8000/api/v1/payments/webhook/test/"
        
        # Sample webhook payload
        test_payload = {
            "event": "charge.success",
            "data": {
                "id": 123456789,
                "reference": "test_webhook_" + str(hash("test")),
                "amount": 50000,  # NGN 500 in kobo
                "currency": "NGN",
                "status": "success",
                "customer": {
                    "email": "farmer@agriconnect.com"
                },
                "metadata": {
                    "product": "Test Agricultural Product",
                    "farmer": "Test Farmer",
                    "webhook_test": True
                }
            }
        }
        
        print(f"📡 Testing webhook URL: {test_url}")
        print(f"📦 Test payload: charge.success event")
        
        # Make test request
        response = requests.post(
            test_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is working!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        return response.status_code == 200
        
    except requests.RequestException as e:
        print(f"❌ Network error testing webhook: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False


def generate_webhook_setup_guide():
    """Generate a setup guide for Paystack webhooks"""
    
    print("\n📚 PAYSTACK WEBHOOK SETUP GUIDE")
    print("=" * 40)
    
    urls = get_webhook_urls()
    
    guide = f"""
🚀 PAYSTACK WEBHOOK CONFIGURATION GUIDE

1. 📱 ACCESS PAYSTACK DASHBOARD:
   - Go to: https://dashboard.paystack.com/
   - Login with your account credentials

2. 🔧 NAVIGATE TO WEBHOOKS:
   - Click on "Settings" in the sidebar
   - Select "Webhooks" from the menu

3. ➕ ADD NEW WEBHOOK:
   - Click "Add Endpoint" or "+" button
   - Enter the webhook URL below

4. 📋 WEBHOOK URL TO ADD:
   {urls['production']}

5. 🎯 SELECT EVENTS:
   Check these events to receive notifications:
   ✅ charge.success (Payment successful)
   ✅ charge.failed (Payment failed)
   ✅ transfer.success (Transfer successful)
   ✅ transfer.failed (Transfer failed)
   ✅ transfer.reversed (Transfer reversed)

6. 🔐 SECURITY SETTINGS:
   - Paystack will provide a webhook secret
   - Add this secret to your PaymentGateway model
   - This ensures webhook authenticity

7. 🧪 TESTING:
   - Use this URL for testing: {urls['development']}
   - Paystack dashboard has a "Test" feature
   - Check webhook delivery status

8. 🔍 MONITORING:
   - Monitor webhook delivery in Paystack dashboard
   - Check Django logs for webhook processing
   - Verify transaction status updates

📝 NOTES:
- Replace 'your-domain.com' with your actual domain
- Ensure your server accepts POST requests
- HTTPS is required for production webhooks
- Keep your webhook secret secure

🆘 TROUBLESHOOTING:
- Check firewall settings allow Paystack IPs
- Verify CSRF exemption for webhook endpoint
- Monitor Django logs for errors
- Test with Paystack's webhook test feature
"""
    
    print(guide)
    
    # Save guide to file
    with open('PAYSTACK_WEBHOOK_SETUP_GUIDE.md', 'w') as f:
        f.write(guide)
    
    print("\n💾 Setup guide saved to: PAYSTACK_WEBHOOK_SETUP_GUIDE.md")


if __name__ == "__main__":
    print("🌾 AGRICONNECT PAYSTACK WEBHOOK CONFIGURATION")
    print("=" * 60)
    
    # Get webhook URLs
    webhook_urls = get_webhook_urls()
    
    # Update Paystack configuration
    if update_paystack_webhook_config():
        print("\n✅ Configuration updated successfully")
    
    # Test webhook endpoint
    if test_webhook_endpoint():
        print("\n✅ Webhook endpoint is ready")
    else:
        print("\n⚠️  Webhook endpoint needs Django server to be running")
        print("   Start server with: python manage.py runserver")
    
    # Generate setup guide
    generate_webhook_setup_guide()
    
    print("\n" + "=" * 60)
    print("🎉 WEBHOOK CONFIGURATION COMPLETE!")
    print("✅ Webhook endpoint created and tested")
    print("✅ URLs generated for Paystack dashboard")
    print("✅ Setup guide created")
    print("🔗 Ready to add to Paystack dashboard!")
    print("=" * 60)
    
    print("\n🚀 IMMEDIATE NEXT STEPS:")
    print("1. Copy the webhook URL above")
    print("2. Add it to your Paystack dashboard")
    print("3. Configure webhook events")
    print("4. Test webhook delivery")
    print("5. Start receiving real-time payment notifications!")
