"""
Advanced Product Management API Tests
Testing enhanced product creation and management features
"""

import json
import requests
from datetime import date
from decimal import Decimal

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_product_creation():
    """Test creating a new product via API"""
    
    # Sample product data
    product_data = {
        "name": "Premium Shea Butter",
        "description": "Pure, unrefined shea butter from northern Ghana. Rich in vitamins A and E, perfect for cosmetics and traditional medicine.",
        "category_id": 1,  # Grains & Cereals category (we'll update this)
        "product_type": "processed",
        "organic_status": "organic", 
        "price_per_unit": "15.75",
        "unit": "kg",
        "minimum_order_quantity": "5.00",
        "stock_quantity": "200.00",
        "processing_date": str(date.today()),
        "origin_country": "Ghana",
        "origin_region": "Upper West",
        "origin_city": "Wa",
        "quality_grade": "A",
        "processing_method": "Traditional extraction and filtering",
        "processing_facility": "Women's Cooperative Shea Processing Center",
        "nutritional_info": {
            "fat_content": "85%",
            "vitamin_e": "high",
            "vitamin_a": "moderate"
        },
        "search_keywords": ["shea", "butter", "organic", "cosmetic", "natural"]
    }
    
    print("Product creation test data:")
    print(json.dumps(product_data, indent=2))
    
    return product_data

def test_advanced_filtering():
    """Test various filtering combinations"""
    
    filters = [
        "?organic_status=organic",
        "?product_type=raw", 
        "?min_price=2.00&max_price=10.00",
        "?search=milk",
        "?in_stock=true",
        "?ordering=price_per_unit",
        "?ordering=-created_at"
    ]
    
    print("\nTesting advanced filtering:")
    for filter_query in filters:
        url = f"{BASE_URL}/products/api/products/{filter_query}"
        print(f"Filter: {filter_query}")
        print(f"URL: {url}")
    
    return filters

def test_api_endpoints():
    """Test all available API endpoints"""
    
    endpoints = [
        "/api/v1/",
        "/api/v1/auth/",
        "/api/v1/products/",
        "/api/v1/products/api/categories/",
        "/api/v1/products/api/products/",
        "/api/v1/products/api/products/featured/",
        "/api/v1/products/api/products/organic/",
        "/api/v1/products/api/products/statistics/"
    ]
    
    print("\nAvailable API endpoints:")
    for endpoint in endpoints:
        print(f"- {BASE_URL.replace('/api/v1', '')}{endpoint}")
    
    return endpoints

if __name__ == "__main__":
    print("=== AgriConnect API Advanced Testing ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Date: {date.today()}")
    
    # Test product creation data
    product_data = test_product_creation()
    
    # Test filtering options
    filters = test_advanced_filtering()
    
    # Test endpoints
    endpoints = test_api_endpoints()
    
    print("\n=== Test Complete ===")
    print("Use the above data and URLs to test the API manually with curl or a REST client.")
