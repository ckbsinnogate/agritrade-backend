import requests
import json

# Test the disease detection endpoint with different scenarios
base_url = 'http://127.0.0.1:8000/api/v1/ai/disease-detection/'
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer invalid_token'}

# Test scenarios that might cause 400 errors
test_cases = [
    {'name': 'Empty body', 'data': {}},
    {'name': 'Empty crop_type', 'data': {'crop_type': ''}},
    {'name': 'No symptoms or image', 'data': {'crop_type': 'tomatoes'}},
    {'name': 'Valid minimal', 'data': {'crop_type': 'tomatoes', 'symptoms': 'yellow leaves'}},
    {'name': 'Empty symptoms and image', 'data': {'crop_type': 'tomatoes', 'symptoms': '', 'image_url': ''}},
]

print("Testing disease detection endpoint...")
print("=" * 50)

for test in test_cases:
    try:
        response = requests.post(base_url, json=test['data'], headers=headers)
        print(f"{test['name']}: Status {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        print("-" * 30)
    except Exception as e:
        print(f"{test['name']}: Error - {e}")
        print("-" * 30)

print("Test complete!")
