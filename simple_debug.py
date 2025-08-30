"""
Simple Paystack Debug Test
"""

import requests
import json

# Paystack Test API Keys
SECRET_KEY = "sk_test_de0ad358ec07284b50832638f5d7248a757a6b26"

def main():
    print("Starting Paystack Debug...")
    
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test payment initialization
    payment_data = {
        "email": "test@example.com",
        "amount": 10000
    }
    
    try:
        print("Making payment request...")
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payment_data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
