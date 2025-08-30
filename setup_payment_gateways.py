"""
AgriConnect Payment Gateway Sample Data Creator
Creates sample payment gateways and configurations for testing African payment methods
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from payments.models import PaymentGateway
from decimal import Decimal

def create_payment_gateways():
    """Create sample payment gateways for African market"""
    
    print("🌍 Creating African Payment Gateways...")
    
    # Paystack Gateway (Nigeria, Ghana, South Africa)
    paystack, created = PaymentGateway.objects.get_or_create(
        name='paystack',
        defaults={
            'display_name': 'Paystack',
            'is_active': True,
            'supported_currencies': ['NGN', 'GHS', 'ZAR', 'USD'],
            'supported_countries': ['NG', 'GH', 'ZA'],
            'gateway_config': {
                'api_url': 'https://api.paystack.co',
                'supported_methods': ['card', 'bank_transfer', 'ussd', 'qr_code'],
                'webhook_events': ['charge.success', 'transfer.success', 'transfer.failed'],
                'test_mode': True
            }
        }
    )
    print(f"✅ Paystack Gateway: {'Created' if created else 'Already exists'}")
    
    # Flutterwave Gateway (Pan-African)
    flutterwave, created = PaymentGateway.objects.get_or_create(
        name='flutterwave',
        defaults={
            'display_name': 'Flutterwave',
            'is_active': True,
            'supported_currencies': ['NGN', 'GHS', 'KES', 'UGX', 'ZAR', 'USD'],
            'supported_countries': ['NG', 'GH', 'KE', 'UG', 'ZA', 'RW', 'TZ'],
            'gateway_config': {
                'api_url': 'https://api.flutterwave.com/v3',
                'supported_methods': ['card', 'bank_transfer', 'mobile_money', 'ussd'],
                'webhook_events': ['charge.success', 'transfer.completed'],
                'test_mode': True
            }
        }
    )
    print(f"✅ Flutterwave Gateway: {'Created' if created else 'Already exists'}")
    
    # MTN Mobile Money Gateway
    mtn_momo, created = PaymentGateway.objects.get_or_create(
        name='mtn_mobile_money',
        defaults={
            'display_name': 'MTN Mobile Money',
            'is_active': True,
            'supported_currencies': ['GHS', 'UGX', 'ZMW', 'CDF'],
            'supported_countries': ['GH', 'UG', 'ZM', 'CD', 'CI', 'CM'],
            'gateway_config': {
                'api_url': 'https://sandbox.momodeveloper.mtn.com',
                'supported_methods': ['mobile_money'],
                'webhook_events': ['payment.success', 'payment.failed'],
                'test_mode': True
            }
        }
    )
    print(f"✅ MTN Mobile Money: {'Created' if created else 'Already exists'}")
    
    # Vodafone Cash Gateway (Ghana)
    vodafone_cash, created = PaymentGateway.objects.get_or_create(
        name='vodafone_cash',
        defaults={
            'display_name': 'Vodafone Cash',
            'is_active': True,
            'supported_currencies': ['GHS'],
            'supported_countries': ['GH'],
            'gateway_config': {
                'api_url': 'https://api.vodafone.com.gh/payment',
                'supported_methods': ['mobile_money'],
                'webhook_events': ['transaction.success', 'transaction.failed'],
                'test_mode': True
            }
        }
    )
    print(f"✅ Vodafone Cash: {'Created' if created else 'Already exists'}")
    
    # AirtelTigo Money Gateway (Ghana)
    airteltigo, created = PaymentGateway.objects.get_or_create(
        name='airteltigo_money',
        defaults={
            'display_name': 'AirtelTigo Money',
            'is_active': True,
            'supported_currencies': ['GHS'],
            'supported_countries': ['GH'],
            'gateway_config': {
                'api_url': 'https://api.airteltigo.com.gh/payment',
                'supported_methods': ['mobile_money'],
                'webhook_events': ['payment.completed', 'payment.failed'],
                'test_mode': True
            }
        }
    )
    print(f"✅ AirtelTigo Money: {'Created' if created else 'Already exists'}")
    
    # Bank Transfer Gateway (Generic)
    bank_transfer, created = PaymentGateway.objects.get_or_create(
        name='bank_transfer',
        defaults={
            'display_name': 'Bank Transfer',
            'is_active': True,
            'supported_currencies': ['GHS', 'NGN', 'KES', 'USD'],
            'supported_countries': ['GH', 'NG', 'KE', 'UG', 'ZA'],
            'gateway_config': {
                'supported_methods': ['bank_transfer'],
                'manual_verification': True,
                'webhook_events': [],
                'test_mode': True
            }
        }
    )
    print(f"✅ Bank Transfer: {'Created' if created else 'Already exists'}")

def display_gateways():
    """Display created payment gateways"""
    print("\n💳 AVAILABLE PAYMENT GATEWAYS:")
    print("=" * 60)
    
    gateways = PaymentGateway.objects.all()
    for gateway in gateways:
        status = "🟢 ACTIVE" if gateway.is_active else "🔴 INACTIVE"
        print(f"🏦 {gateway.display_name} ({gateway.name})")
        print(f"   Status: {status}")
        print(f"   Currencies: {', '.join(gateway.supported_currencies)}")
        print(f"   Countries: {', '.join(gateway.supported_countries)}")
        print(f"   Methods: {', '.join(gateway.gateway_config.get('supported_methods', []))}")
        print()

if __name__ == "__main__":
    print("🚀 AGRICONNECT PAYMENT GATEWAYS SETUP")
    print("=" * 50)
    
    try:
        create_payment_gateways()
        display_gateways()
        
        total_gateways = PaymentGateway.objects.count()
        active_gateways = PaymentGateway.objects.filter(is_active=True).count()
        
        print(f"📊 GATEWAY STATISTICS:")
        print(f"   Total Gateways: {total_gateways}")
        print(f"   Active Gateways: {active_gateways}")
        print(f"   Inactive Gateways: {total_gateways - active_gateways}")
        
        print("\n✅ Payment Gateway Setup Complete!")
        print("🔗 Access Admin: http://127.0.0.1:8000/admin/payments/")
        
    except Exception as e:
        print(f"❌ Error setting up payment gateways: {e}")
        import traceback
        traceback.print_exc()
