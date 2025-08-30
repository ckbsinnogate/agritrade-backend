#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix Paystack Currency Issue
Test with different currencies and check account settings
"""

import requests
import json

def fix_paystack_currency():
    """Fix the currency issue and test payment initialization"""
    
    SECRET_KEY = "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26"
    
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🔧 FIXING PAYSTACK CURRENCY ISSUE")
    print("=" * 50)
    
    # Test 1: Check account integration settings
    print("\n📋 Test 1: Check Account Integration Settings")
    print("-" * 45)
    
    try:
        response = requests.get(
            "https://api.paystack.co/integration",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                integration = data["data"]
                print(f"✅ Account Name: {integration.get('name', 'N/A')}")
                print(f"✅ Domain: {integration.get('domain', 'N/A')}")
                print(f"✅ Live Mode: {integration.get('live', False)}")
                
                # Check supported currencies
                currencies = integration.get('allowed_currencies', [])
                if currencies:
                    print(f"✅ Supported Currencies: {', '.join(currencies)}")
                else:
                    print("❌ No currencies listed - checking default NGN")
                    currencies = ['NGN']  # Default for Nigerian accounts
            else:
                print(f"❌ Account Error: {data.get('message')}")
                return
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            # Assume NGN as default
            currencies = ['NGN']
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        # Assume NGN as default
        currencies = ['NGN']
    
    # Test 2: Try payment without specifying currency (use default)
    print("\n💳 Test 2: Payment Without Currency (Use Default)")
    print("-" * 50)
    
    payment_data_1 = {
        "email": "test@agriconnect.com",
        "amount": 10000,  # 100 NGN in kobo
    }
    
    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payment_data_1
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                payment_info = data["data"]
                print("✅ Payment initialization successful!")
                print(f"   Reference: {payment_info['reference']}")
                print(f"   Amount: {payment_info.get('amount', 'N/A')}")
                print(f"   Currency: {payment_info.get('currency', 'NGN')}")
                print(f"   Auth URL: {payment_info['authorization_url'][:60]}...")
                return payment_info['reference']
            else:
                print(f"❌ Payment Error: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            error_data = response.json() if response.text else {}
            print(f"Error: {error_data.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 3: Try with explicit NGN currency
    print("\n💳 Test 3: Payment With NGN Currency")
    print("-" * 40)
    
    payment_data_2 = {
        "email": "test@agriconnect.com",
        "amount": 10000,
        "currency": "NGN"
    }
    
    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payment_data_2
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                payment_info = data["data"]
                print("✅ NGN Payment initialization successful!")
                print(f"   Reference: {payment_info['reference']}")
                print(f"   Amount: NGN {payment_info.get('amount', 0) / 100}")
                print(f"   Auth URL: {payment_info['authorization_url'][:60]}...")
                return payment_info['reference']
            else:
                print(f"❌ NGN Payment Error: {data.get('message')}")
        else:
            print(f"❌ NGN HTTP Error: {response.status_code}")
            error_data = response.json() if response.text else {}
            print(f"Error: {error_data.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ NGN Connection Error: {e}")
    
    # Test 4: Check supported currencies endpoint
    print("\n🌍 Test 4: Available Countries and Currencies")
    print("-" * 45)
    
    try:
        response = requests.get(
            "https://api.paystack.co/country",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                countries = data["data"]
                print("✅ Supported Countries and Currencies:")
                for country in countries[:5]:  # Show first 5
                    print(f"   • {country['name']} ({country['iso_code']}) - {country['default_currency_code']}")
                
                if len(countries) > 5:
                    print(f"   ... and {len(countries) - 5} more countries")
            else:
                print(f"❌ Countries Error: {data.get('message')}")
        else:
            print(f"❌ Countries HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Countries Connection Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATION:")
    print("1. Use NGN currency for Nigerian Paystack accounts")
    print("2. Don't specify currency to use account default")
    print("3. Enable additional currencies in Paystack dashboard if needed")
    print("=" * 50)

if __name__ == "__main__":
    fix_paystack_currency()
