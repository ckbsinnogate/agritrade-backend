"""
Simple Webhook URL Generator for Paystack
"""

def generate_webhook_urls():
    """Generate webhook URLs for Paystack dashboard"""
    
    print("🔗 PAYSTACK WEBHOOK URL FOR DASHBOARD")
    print("=" * 50)
    
    # Your domain URLs
    local_url = "http://localhost:8000/api/v1/payments/webhook/paystack/"
    production_url = "https://your-agriconnect-domain.com/api/v1/payments/webhook/paystack/"
    
    print("📍 WEBHOOK ENDPOINTS:")
    print(f"Local Development: {local_url}")
    print(f"Production:        {production_url}")
    
    print("\n🎯 FOR PAYSTACK DASHBOARD CONFIGURATION:")
    print("=" * 50)
    print("1. Login to: https://dashboard.paystack.com/")
    print("2. Go to: Settings > Webhooks")
    print("3. Click: 'Add Endpoint'")
    print("4. Enter this URL:")
    print()
    print("   📋 WEBHOOK URL (Copy this exactly):")
    print(f"   {production_url}")
    print()
    print("5. Select these events:")
    print("   ✅ charge.success")
    print("   ✅ charge.failed")
    print("   ✅ transfer.success")
    print("   ✅ transfer.failed")
    print()
    print("6. Save the webhook configuration")
    
    print("\n🧪 FOR TESTING (Development):")
    print("=" * 35)
    print("Use this URL for local testing:")
    print(f"{local_url}")
    print("(Make sure Django server is running: python manage.py runserver)")
    
    print("\n🔐 SECURITY NOTES:")
    print("=" * 20)
    print("- Paystack will provide a webhook secret")
    print("- Store this secret in your PaymentGateway model")
    print("- The webhook endpoint verifies signatures for security")
    print("- HTTPS is required for production webhooks")
    
    return {
        'local': local_url,
        'production': production_url
    }

if __name__ == "__main__":
    urls = generate_webhook_urls()
    
    print("\n" + "=" * 50)
    print("🎉 WEBHOOK URLs GENERATED!")
    print("✅ Copy the production URL to Paystack dashboard")
    print("✅ Configure webhook events as listed above")
    print("✅ Your AgriConnect payment system will receive real-time notifications")
    print("=" * 50)
