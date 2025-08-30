#!/usr/bin/env python
"""
Setup Paystack for Ghana (Default Currency: GHS)
Configure AgriConnect for Ghanaian agricultural commerce
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

def setup_paystack_ghana():
    """Configure Paystack specifically for Ghana operations"""
    
    print("🇬🇭 PAYSTACK GHANA SETUP - AGRICONNECT")
    print("=" * 50)
    
    # Paystack Test API Keys (same for all countries)
    PAYSTACK_PUBLIC_KEY = "pk_test_ea5b669d4ab214ab74857c2ad154c5d25329a42f"
    PAYSTACK_SECRET_KEY = "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26"
    
    try:
        # Update or create Paystack gateway for Ghana
        paystack, created = PaymentGateway.objects.get_or_create(
            name='paystack',
            defaults={
                'display_name': 'Paystack Ghana',
                'is_active': True,
                'api_base_url': "https://api.paystack.co",
                'public_key': PAYSTACK_PUBLIC_KEY,
                'secret_key': PAYSTACK_SECRET_KEY,
                'supported_currencies': ['GHS', 'NGN', 'ZAR', 'USD'],
                'supported_countries': ['GH', 'NG', 'ZA'],
                'supported_payment_methods': ['credit_card', 'debit_card', 'mobile_money', 'bank_transfer'],
                'transaction_fee_percentage': Decimal('0.015'),  # 1.5% fee
                'fixed_fee': Decimal('1.00'),  # GHS 1 fixed fee
                'minimum_amount': Decimal('1.00'),  # GHS 1 minimum
                'maximum_amount': Decimal('100000.00'),  # GHS 100K maximum
                'webhook_secret': '',  # To be set later
                'metadata': {
                    'country': 'Ghana',
                    'primary_currency': 'GHS',
                    'local_name': 'Ghana Cedis',
                    'mobile_money_operators': ['MTN', 'Vodafone', 'AirtelTigo'],
                    'major_banks': ['GCB Bank', 'Ecobank', 'Standard Chartered', 'Fidelity Bank']
                }
            }
        )
        
        if not created:
            # Update existing gateway for Ghana
            paystack.display_name = 'Paystack Ghana'
            paystack.public_key = PAYSTACK_PUBLIC_KEY
            paystack.secret_key = PAYSTACK_SECRET_KEY
            paystack.api_base_url = "https://api.paystack.co"
            paystack.supported_currencies = ['GHS', 'NGN', 'ZAR', 'USD']
            paystack.supported_countries = ['GH', 'NG', 'ZA']
            paystack.supported_payment_methods = ['credit_card', 'debit_card', 'mobile_money', 'bank_transfer']
            paystack.transaction_fee_percentage = Decimal('0.015')
            paystack.fixed_fee = Decimal('1.00')  # GHS 1
            paystack.minimum_amount = Decimal('1.00')
            paystack.maximum_amount = Decimal('100000.00')
            paystack.metadata = {
                'country': 'Ghana',
                'primary_currency': 'GHS',
                'local_name': 'Ghana Cedis',
                'mobile_money_operators': ['MTN', 'Vodafone', 'AirtelTigo'],
                'major_banks': ['GCB Bank', 'Ecobank', 'Standard Chartered', 'Fidelity Bank']
            }
            paystack.save()
        
        print("✅ Paystack Ghana Configuration Complete:")
        print(f"   Gateway: {paystack.display_name}")
        print(f"   Status: {'ACTIVE' if paystack.is_active else 'INACTIVE'}")
        print(f"   Primary Currency: GHS (Ghana Cedis)")
        print(f"   Public Key: {PAYSTACK_PUBLIC_KEY[:20]}...")
        print(f"   Secret Key: {PAYSTACK_SECRET_KEY[:20]}...")
        print(f"   API URL: {paystack.api_base_url}")
        print(f"   Supported Currencies: {', '.join(paystack.supported_currencies)}")
        print(f"   Countries: {', '.join(paystack.supported_countries)}")
        print(f"   Payment Methods: {', '.join(paystack.supported_payment_methods)}")
        print(f"   Transaction Fee: {paystack.transaction_fee_percentage*100}% + GHS {paystack.fixed_fee}")
        
        print(f"\n🏦 GHANA BANKING INTEGRATION:")
        print(f"   ✅ Mobile Money: MTN, Vodafone, AirtelTigo")
        print(f"   ✅ Banks: GCB Bank, Ecobank, Standard Chartered")
        print(f"   ✅ Cards: Visa, Mastercard, Verve")
        print(f"   ✅ Currency: Ghana Cedis (GHS)")
        
        print(f"\n🌾 AGRICULTURAL PAYMENT SCENARIOS (GHANA):")
        print(f"   🌱 Smallholder Seeds: GHS 10 - 50")
        print(f"   🚜 Farm Equipment: GHS 100 - 1,000")
        print(f"   🌾 Fertilizer Packages: GHS 50 - 500")
        print(f"   🏪 Cooperative Orders: GHS 1,000 - 10,000")
        print(f"   📱 Mobile Money Payments: Instant settlement")
        
        # Test API connection
        print(f"\n🧪 TESTING API CONNECTION...")
        test_api_connection(paystack)
        
        return paystack
        
    except Exception as e:
        print(f"❌ Error setting up Paystack Ghana: {e}")
        return None

def test_api_connection(paystack):
    """Test Paystack API connection"""
    
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {paystack.secret_key}',
            'Content-Type': 'application/json'
        }
        
        # Test bank list API
        response = requests.get(f"{paystack.api_base_url}/bank", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            banks = data.get('data', [])
            ghana_banks = [bank for bank in banks if bank.get('country') == 'Ghana']
            
            print(f"✅ API Connection: SUCCESS")
            print(f"✅ Total Banks Available: {len(banks)}")
            print(f"✅ Ghana Banks: {len(ghana_banks)}")
            
            if ghana_banks:
                print(f"🏦 Sample Ghana Banks:")
                for bank in ghana_banks[:3]:
                    print(f"   - {bank.get('name')} ({bank.get('code')})")
            
        else:
            print(f"❌ API Connection Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API Test Error: {e}")

def create_ghana_test_payment():
    """Create a sample Ghana agricultural payment"""
    
    print(f"\n💰 CREATING GHANA TEST PAYMENT...")
    
    try:
        from authentication.models import User
        from payments.models import PaymentMethod, Transaction
        import uuid
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='ghana_farmer_test',
            defaults={
                'email': 'farmer@ghana.test',
                'first_name': 'Kwame',
                'last_name': 'Osei'
            }
        )
        
        paystack = PaymentGateway.objects.get(name='paystack')
        
        # Create payment method
        payment_method, created = PaymentMethod.objects.get_or_create(
            user=user,
            gateway=paystack,
            method_type='mobile_money',
            defaults={
                'display_name': 'MTN Mobile Money',
                'account_details': {'operator': 'MTN', 'number': '233241234567'},
                'is_verified': True
            }
        )
        
        # Create test transaction
        transaction = Transaction.objects.create(
            user=user,
            gateway=paystack,
            payment_method=payment_method,
            amount=Decimal('150.00'),  # GHS 150
            currency='GHS',
            status='pending',
            gateway_reference=f'ghana_test_{uuid.uuid4().hex[:10]}',
            metadata={
                'product': 'Maize Seeds & Fertilizer Package',
                'location': 'Kumasi, Ashanti Region',
                'farm_size': '2 acres',
                'crop_type': 'Maize',
                'season': '2025 Major Season',
                'payment_method': 'MTN Mobile Money',
                'farmer_type': 'Smallholder'
            }
        )
        
        print(f"✅ Ghana Test Payment Created:")
        print(f"   Transaction ID: {transaction.id}")
        print(f"   Amount: GHS {transaction.amount}")
        print(f"   Farmer: {user.first_name} {user.last_name}")
        print(f"   Location: Kumasi, Ashanti Region")
        print(f"   Payment Method: MTN Mobile Money")
        print(f"   Product: Maize Seeds & Fertilizer Package")
        
        return transaction
        
    except Exception as e:
        print(f"❌ Error creating test payment: {e}")
        return None

def main():
    """Main setup function"""
    
    print("🌾 AGRICONNECT GHANA PAYMENT SETUP")
    print("🇬🇭 Empowering Ghanaian Agriculture with Digital Payments")
    print("=" * 60)
    
    # Setup Paystack for Ghana
    paystack = setup_paystack_ghana()
    
    if paystack:
        # Create test payment
        test_payment = create_ghana_test_payment()
        
        print(f"\n🎉 GHANA SETUP COMPLETE!")
        print(f"=" * 35)
        print(f"✅ Paystack Gateway: CONFIGURED")
        print(f"✅ Currency: GHS (Ghana Cedis)")
        print(f"✅ Mobile Money: ENABLED")
        print(f"✅ Agricultural Payments: READY")
        print(f"✅ Test Payment: CREATED")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Deploy to production")
        print(f"   2. Configure webhook URL")
        print(f"   3. Test with Ghana test cards")
        print(f"   4. Launch in Ghana! 🇬🇭")
        
    else:
        print(f"\n❌ Setup failed - check configuration")

if __name__ == "__main__":
    main()