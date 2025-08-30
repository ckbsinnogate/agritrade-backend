"""
Paystack API Integration Setup
Configure real Paystack API keys for AgriConnect payment processing
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway

def setup_paystack_api():
    """Configure Paystack with real API credentials"""
    
    print("🔑 PAYSTACK API INTEGRATION SETUP")
    print("=" * 50)
      # Paystack Test API Keys
    PAYSTACK_PUBLIC_KEY = "pk_test_ea5b669d4ab214ab74857c2ad154c5d25329a42f"
    PAYSTACK_SECRET_KEY = "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26"
    
    try:
        # Update Paystack gateway with real API keys
        paystack = PaymentGateway.objects.filter(name='paystack').first()
        
        if paystack:
            paystack.public_key = PAYSTACK_PUBLIC_KEY
            paystack.secret_key = PAYSTACK_SECRET_KEY
            paystack.api_base_url = "https://api.paystack.co"
            paystack.webhook_secret = ""  # Will be set when configuring webhooks
            
            # Update supported features for Paystack (Ghana primary)
            paystack.supported_currencies = ['GHS', 'NGN', 'ZAR', 'USD']
            paystack.supported_countries = ['GH', 'NG', 'ZA']
            paystack.supported_payment_methods = ['credit_card', 'debit_card', 'mobile_money', 'bank_transfer']
            
            # Set Paystack specific fees and limits (Ghana Cedis)
            paystack.transaction_fee_percentage = Decimal('0.015')  # 1.5% fee
            paystack.fixed_fee = Decimal('5.00')  # GHS 5 fixed fee
            paystack.minimum_amount = Decimal('1.00')  # GHS 1 minimum
            paystack.maximum_amount = Decimal('500000.00')  # GHS 500K maximum
            
            paystack.save()
            
            print("✅ Paystack API Configuration Updated:")
            print(f"   Gateway: {paystack.display_name}")
            print(f"   Public Key: {PAYSTACK_PUBLIC_KEY[:20]}...")
            print(f"   Secret Key: {PAYSTACK_SECRET_KEY[:20]}...")
            print(f"   API URL: {paystack.api_base_url}")
            print(f"   Currencies: {', '.join(paystack.supported_currencies)}")
            print(f"   Countries: {', '.join(paystack.supported_countries)}")
            print(f"   Fee: {paystack.transaction_fee_percentage*100}% + GHS {paystack.fixed_fee}")
            
        else:
            print("❌ Paystack gateway not found in database")
            print("Creating new Paystack gateway...")
            
            paystack = PaymentGateway.objects.create(
                name='paystack',
                display_name='Paystack',
                is_active=True,
                api_base_url="https://api.paystack.co",
                public_key=PAYSTACK_PUBLIC_KEY,
                secret_key=PAYSTACK_SECRET_KEY,
                supported_currencies=['GHS', 'NGN', 'ZAR', 'USD'],
                supported_countries=['GH', 'NG', 'ZA'],
                supported_payment_methods=['credit_card', 'debit_card', 'mobile_money', 'bank_transfer'],
                transaction_fee_percentage=Decimal('0.015'),
                fixed_fee=Decimal('5.00'),
                minimum_amount=Decimal('1.00'),
                maximum_amount=Decimal('500000.00')
            )
            print("✅ Created new Paystack gateway with API keys")
            
    except Exception as e:
        print(f"❌ Error configuring Paystack: {e}")
        return False
    
    return True

def verify_paystack_config():
    """Verify Paystack configuration"""
    
    print("\n🔍 PAYSTACK CONFIGURATION VERIFICATION")
    print("-" * 50)
    
    try:
        paystack = PaymentGateway.objects.filter(name='paystack').first()
        
        if paystack and paystack.public_key and paystack.secret_key:
            print("✅ API Keys: Configured")
            print("✅ Gateway: Active" if paystack.is_active else "❌ Gateway: Inactive")
            print(f"✅ Supported Currencies: {len(paystack.supported_currencies)}")
            print(f"✅ Supported Countries: {len(paystack.supported_countries)}")
            print(f"✅ Payment Methods: {len(paystack.supported_payment_methods)}")
            
            # Verify key format
            if paystack.public_key.startswith('pk_test_'):
                print("✅ Public Key: Valid test key format")
            elif paystack.public_key.startswith('pk_live_'):
                print("🔴 Public Key: Live key detected")
            else:
                print("⚠️  Public Key: Unknown format")
                
            if paystack.secret_key.startswith('sk_test_'):
                print("✅ Secret Key: Valid test key format")
            elif paystack.secret_key.startswith('sk_live_'):
                print("🔴 Secret Key: Live key detected")
            else:
                print("⚠️  Secret Key: Unknown format")
                
            return True
        else:
            print("❌ Paystack configuration incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying Paystack: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PAYSTACK REAL API INTEGRATION")
    print("=" * 60)
    
    # Setup Paystack API
    if setup_paystack_api():
        # Verify configuration
        if verify_paystack_config():
            print("\n🎉 PAYSTACK API INTEGRATION COMPLETE!")
            print("🔑 Real API keys configured successfully")
            print("🚀 Ready for live payment processing tests")
        else:
            print("\n⚠️  Configuration verification failed")
    else:
        print("\n❌ Failed to setup Paystack API")
        
    print("\n🔗 Next Steps:")
    print("  1. Test payment initialization with real API")
    print("  2. Configure webhook endpoints")
    print("  3. Test transaction verification")
    print("  4. Implement payment flows")
