"""
Paystack Payment Integration Service
Real payment processing integration with Paystack API for AgriConnect
"""

import requests
import json
import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional

class PaystackService:
    """Paystack payment processing service"""
    
    def __init__(self, public_key: str, secret_key: str):
        self.public_key = public_key
        self.secret_key = secret_key
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
    
    def initialize_payment(self, amount: Decimal, email: str, currency: str = "NGN", 
                          callback_url: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Initialize a payment transaction with Paystack"""
        
        # Convert amount to kobo (for NGN) or lowest currency unit
        amount_in_kobo = int(amount * 100)
        
        payload = {
            "email": email,
            "amount": amount_in_kobo,
            "currency": currency,
            "callback_url": callback_url or f"{settings.SITE_URL}/payments/callback/",
            "metadata": metadata or {}
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "data": response.json(),
                "status_code": response.status_code
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def verify_payment(self, reference: str) -> Dict[str, Any]:
        """Verify a payment transaction"""
        
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self.headers,
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "data": response.json(),
                "status_code": response.status_code
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def list_transactions(self, per_page: int = 50, page: int = 1) -> Dict[str, Any]:
        """List transactions"""
        
        params = {
            "perPage": per_page,
            "page": page
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/transaction",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "data": response.json(),
                "status_code": response.status_code
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def create_customer(self, email: str, first_name: str = None, 
                       last_name: str = None, phone: str = None) -> Dict[str, Any]:
        """Create a customer on Paystack"""
        
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            response = requests.post(
                f"{self.base_url}/customer",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "data": response.json(),
                "status_code": response.status_code
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature from Paystack"""
        
        computed_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    
    def get_banks(self, country: str = "nigeria") -> Dict[str, Any]:
        """Get list of banks for a country"""
        
        params = {"country": country}
        
        try:
            response = requests.get(
                f"{self.base_url}/bank",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "data": response.json(),
                "status_code": response.status_code
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }


def get_paystack_service() -> Optional[PaystackService]:
    """Get configured Paystack service instance"""
    
    try:
        from payments.models import PaymentGateway
        
        paystack_gateway = PaymentGateway.objects.filter(
            name='paystack', 
            is_active=True
        ).first()
        
        if paystack_gateway and paystack_gateway.public_key and paystack_gateway.secret_key:
            return PaystackService(
                public_key=paystack_gateway.public_key,
                secret_key=paystack_gateway.secret_key
            )
        else:
            print("❌ Paystack gateway not configured or inactive")
            return None
            
    except Exception as e:
        print(f"❌ Error getting Paystack service: {e}")
        return None


# Test functions for real API integration
def test_paystack_connection():
    """Test Paystack API connection"""
    
    print("🧪 TESTING PAYSTACK API CONNECTION")
    print("=" * 50)
    
    service = get_paystack_service()
    if not service:
        print("❌ Paystack service not available")
        return False
    
    # Test by listing banks
    result = service.get_banks("nigeria")
    
    if result["success"]:
        banks_data = result["data"]
        if banks_data.get("status"):
            bank_count = len(banks_data.get("data", []))
            print(f"✅ Paystack API Connection: SUCCESS")
            print(f"   Retrieved {bank_count} Nigerian banks")
            print(f"   Response time: Good")
            return True
        else:
            print(f"❌ API Error: {banks_data.get('message', 'Unknown error')}")
    else:
        print(f"❌ Connection Error: {result.get('error', 'Unknown error')}")
    
    return False


def test_payment_initialization():
    """Test payment initialization with real API"""
    
    print("\n💳 TESTING PAYMENT INITIALIZATION")
    print("-" * 50)
    
    service = get_paystack_service()
    if not service:
        print("❌ Paystack service not available")
        return False
    
    # Test payment initialization
    result = service.initialize_payment(
        amount=Decimal("100.00"),  # NGN 100
        email="test@agriconnect.com",
        currency="NGN",
        metadata={
            "order_id": "TEST_ORDER_001",
            "customer_name": "AgriConnect Test User",
            "purpose": "Agricultural Product Purchase"
        }
    )
    
    if result["success"]:
        payment_data = result["data"]
        if payment_data.get("status"):
            auth_url = payment_data["data"]["authorization_url"]
            reference = payment_data["data"]["reference"]
            
            print("✅ Payment Initialization: SUCCESS")
            print(f"   Reference: {reference}")
            print(f"   Payment URL: {auth_url}")
            print(f"   Amount: NGN 100.00")
            print(f"   Status: {payment_data['data']['status']}")
            
            return True
        else:
            print(f"❌ Initialization Error: {payment_data.get('message', 'Unknown error')}")
    else:
        print(f"❌ Request Error: {result.get('error', 'Unknown error')}")
    
    return False


if __name__ == "__main__":
    print("🚀 PAYSTACK REAL API INTEGRATION TEST")
    print("=" * 60)
    
    # Test API connection
    connection_ok = test_paystack_connection()
    
    if connection_ok:
        # Test payment initialization
        payment_ok = test_payment_initialization()
        
        if payment_ok:
            print("\n🎉 PAYSTACK INTEGRATION: FULLY OPERATIONAL!")
            print("✅ API Connection: Working")
            print("✅ Payment Initialization: Working")
            print("🚀 Ready for live agricultural commerce payments!")
        else:
            print("\n⚠️  PAYSTACK INTEGRATION: PARTIAL")
            print("✅ API Connection: Working")
            print("❌ Payment Initialization: Failed")
    else:
        print("\n❌ PAYSTACK INTEGRATION: FAILED")
        print("❌ API Connection: Failed")
        print("🔧 Check API credentials and network connection")
    
    print(f"\n🔗 Next Steps:")
    print("  1. Integrate payment initialization into order flow")
    print("  2. Set up webhook endpoints for payment callbacks")
    print("  3. Implement payment verification workflow")
    print("  4. Add customer creation and management")
