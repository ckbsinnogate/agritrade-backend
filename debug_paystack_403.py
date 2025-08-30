"""
Debug Paystack 403 Error
Detailed investigation of payment initialization issue
"""

import requests
import json

# Paystack Test API Keys
PUBLIC_KEY = "pk_test_ea5b669d4ab214ab74857c2ad154c5d25329a42f"
SECRET_KEY = "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26"

def debug_paystack_403():
    """Debug the 403 error in payment initialization"""
    
    print("🔍 DEBUGGING PAYSTACK 403 ERROR")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Verify API Key with a simple endpoint
    print("\n🔐 Test 1: Verify API Key Authentication")
    print("-" * 40)
    
    try:
        response = requests.get(
            "https://api.paystack.co/bank?country=nigeria&perPage=1",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API Key authentication is working")
        else:
            print(f"❌ Authentication failed: {response.text}")
            return
            
    except requests.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return
    
    # Test 2: Try different payment initialization formats
    print("\n💳 Test 2: Payment Initialization - Basic Format")
    print("-" * 50)
    
    # Format 1: Minimal required fields
    payment_data_1 = {
        "email": "test@agriconnect.com",
        "amount": 10000,  # NGN 100.00 in kobo
    }
    
    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payment_data_1,
            timeout=10
        )
        
        print(f"Format 1 - Status Code: {response.status_code}")
        print(f"Format 1 - Response: {response.text}")
        
        if response.status_code != 200:
            print(f"❌ Error Details: {response.text}")
        else:
            print("✅ Basic format worked!")
            
    except requests.RequestException as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 3: Try with explicit currency
    print("\n💳 Test 3: Payment Initialization - With Currency")
    print("-" * 50)
    
    payment_data_2 = {
        "email": "test@agriconnect.com",
        "amount": 10000,
        "currency": "NGN"
    }
    
    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payment_data_2,
            timeout=10
        )
        
        print(f"Format 2 - Status Code: {response.status_code}")
        print(f"Format 2 - Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                print("✅ Currency format worked!")
                payment_ref = data["data"]["reference"]
                print(f"   Reference: {payment_ref}")
                print(f"   Auth URL: {data['data']['authorization_url']}")
                return payment_ref
        else:
            print(f"❌ Error Details: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 4: Check if it's a rate limiting issue
    print("\n⏱️ Test 4: Rate Limiting Check")
    print("-" * 30)
    
    try:
        # Make multiple quick requests to see if it's rate limiting
        for i in range(3):
            response = requests.get(
                "https://api.paystack.co/bank?country=nigeria&perPage=1",
                headers=headers,
                timeout=5
            )
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 429:
                print("❌ Rate limiting detected!")
                return
                
    except requests.RequestException as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 5: Check account status
    print("\n👤 Test 5: Account Information")
    print("-" * 30)
    
    try:
        # This endpoint might give us account info
        response = requests.get(
            "https://api.paystack.co/integration",
            headers=headers,
            timeout=10
        )
        
        print(f"Account Status Code: {response.status_code}")
        if response.status_code == 200:
            account_data = response.json()
            if account_data.get("status"):
                integration = account_data["data"]
                print(f"✅ Account Active: {integration.get('name', 'Unknown')}")
                print(f"   Domain: {integration.get('domain', 'N/A')}")
                print(f"   Live Mode: {integration.get('live', False)}")
            else:
                print(f"❌ Account Issue: {account_data.get('message')}")
        else:
            print(f"❌ Account Check Failed: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    debug_paystack_403()
