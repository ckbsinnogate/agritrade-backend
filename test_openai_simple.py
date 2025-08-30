#!/usr/bin/env python
"""
Simple OpenAI API Test for AgriConnect
"""

import os
from openai import OpenAI

def test_openai_connection():
    """Test OpenAI API connection"""
    print("🔧 Testing OpenAI API Connection...")
    
    # Initialize OpenAI client
    client = OpenAI(
        api_key='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',
        base_url='https://openrouter.ai/api/v1'
    )
    
    try:
        # Test basic chat completion
        response = client.chat.completions.create(
            model='anthropic/claude-3-haiku-20241022',
            messages=[
                {"role": "system", "content": "You are an agricultural AI assistant."},
                {"role": "user", "content": "Hello! Can you help me with maize farming in Ghana?"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print("✅ OpenAI API Connection Successful!")
        print(f"Model: {response.model}")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Connection Failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()
