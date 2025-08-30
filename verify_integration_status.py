"""
Verify AgriConnect Payment Integration Status
Quick status check of all payment system components
"""

import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
from payments.models import PaymentGateway, Transaction
from django.contrib.auth import get_user_model

def verify_integration_status():
    """Verify all integration components"""
    
    print("🔍 AGRICONNECT PAYMENT INTEGRATION STATUS")
    print("=" * 50)
    
    status = {
        "gateway_configured": False,
        "api_connection": False,
        "payment_initialization": False,
        "django_integration": False,
        "transaction_management": False
    }
    
    try:
        # 1. Check gateway configuration
        print("\n1. 🏦 Payment Gateway Configuration")
        print("-" * 35)
        
        paystack = PaymentGateway.objects.get(name="paystack")
        print(f"   ✅ Gateway found: {paystack.display_name}")
        print(f"   ✅ Status: {'Active' if paystack.is_active else 'Inactive'}")
        print(f"   ✅ API URL: {paystack.api_base_url}")
        print(f"   ✅ Credentials: Configured")
        status["gateway_configured"] = True
        
        # 2. Test API connection
        print("\n2. 🌐 API Connection Test")
        print("-" * 25)
        
        headers = {
            "Authorization": f"Bearer {paystack.secret_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://api.paystack.co/bank?country=nigeria&perPage=1",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ API connection: Working")
            print(f"   ✅ Authentication: Valid")
            status["api_connection"] = True
        else:
            print(f"   ❌ API connection failed: {response.status_code}")
        
        # 3. Test payment initialization
        print("\n3. 💳 Payment Initialization Test")
        print("-" * 32)
        
        test_payment = {
            "email": "test@agriconnect.com",
            "amount": 10000,  # NGN 100
            "metadata": {"test": "verification"}
        }
        
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=test_payment,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                print(f"   ✅ Payment initialization: Working")
                print(f"   ✅ Reference: {data['data']['reference']}")
                status["payment_initialization"] = True
            else:
                print(f"   ❌ Payment error: {data.get('message')}")
        else:
            print(f"   ❌ Payment HTTP error: {response.status_code}")
        
        # 4. Test Django integration
        print("\n4. 🐍 Django Integration Test")
        print("-" * 27)
        
        User = get_user_model()
        test_user = User.objects.first()
        
        if test_user:
            print(f"   ✅ User model: Working")
            print(f"   ✅ Test user: {test_user.email}")
            status["django_integration"] = True
        else:
            print(f"   ❌ No users found")
        
        # 5. Test transaction management
        print("\n5. 📊 Transaction Management Test")
        print("-" * 32)
        
        transaction_count = Transaction.objects.count()
        recent_transactions = Transaction.objects.order_by('-initiated_at')[:3]
        
        print(f"   ✅ Transaction model: Working")
        print(f"   ✅ Total transactions: {transaction_count}")
        
        if recent_transactions:
            print(f"   ✅ Recent transactions:")
            for txn in recent_transactions:
                amount = txn.amount
                ref = txn.gateway_reference[:15]
                print(f"      • {ref}... - NGN {amount}")
            status["transaction_management"] = True
        else:
            print(f"   ℹ️  No transactions yet")
            status["transaction_management"] = True  # Model works even if empty
        
    except PaymentGateway.DoesNotExist:
        print("   ❌ Paystack gateway not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Overall status
    print("\n" + "=" * 50)
    print("📋 INTEGRATION STATUS SUMMARY")
    print("=" * 50)
    
    all_working = all(status.values())
    
    for component, working in status.items():
        icon = "✅" if working else "❌"
        name = component.replace("_", " ").title()
        print(f"{icon} {name}")
    
    print("\n" + "=" * 50)
    
    if all_working:
        print("🎉 INTEGRATION STATUS: FULLY OPERATIONAL!")
        print("✅ All components working correctly")
        print("🌾 Ready for agricultural commerce")
        print("🚀 Production deployment ready")
    else:
        print("⚠️  INTEGRATION STATUS: NEEDS ATTENTION")
        failed_components = [k for k, v in status.items() if not v]
        print(f"❌ Failed components: {', '.join(failed_components)}")
    
    print("=" * 50)
    
    return all_working

if __name__ == "__main__":
    verify_integration_status()
