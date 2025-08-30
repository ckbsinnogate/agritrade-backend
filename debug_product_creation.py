#!/usr/bin/env python
"""
Product Creation Debug Tool
Investigates the 405 Method Not Allowed issue
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

import requests
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from products.views_simple import ProductViewSet
from products.models import Category

User = get_user_model()

def test_viewset_directly():
    """Test the ViewSet directly without going through URLs"""
    print("\n🔍 TESTING VIEWSET DIRECTLY")
    print("-" * 50)
    
    try:
        # Create test user
        user = User.objects.filter(phone_number="+233548577399").first()
        if not user:
            print("❌ Test user not found")
            return
            
        print(f"✅ Test user found: {user.username}")
        
        # Create API request factory
        factory = APIRequestFactory()
        
        # Test data
        product_data = {
            'name': 'Direct Test Product',
            'description': 'Test Description',
            'price_per_unit': 10.00,
            'category_id': 1,
            'stock_quantity': 100,
            'unit': 'kg',
            'product_type': 'raw',
            'organic_status': 'non_organic',
            'origin_country': 'Ghana'
        }
        
        # Create POST request
        request = factory.post('/api/v1/products/products/', product_data, format='json')
        force_authenticate(request, user=user)
        
        # Test ViewSet
        viewset = ProductViewSet()
        viewset.action = 'create'
        viewset.request = request
        viewset.format_kwarg = None
        
        print(f"ViewSet class: {ProductViewSet.__name__}")
        print(f"Base classes: {[cls.__name__ for cls in ProductViewSet.__mro__]}")
        print(f"Has create method: {hasattr(viewset, 'create')}")
        
        # Check allowed methods
        if hasattr(viewset, 'allowed_methods'):
            print(f"Allowed methods: {viewset.allowed_methods}")
        
        # Check HTTP method names
        print(f"HTTP method names: {viewset.http_method_names}")
        
        # Try to call create method directly
        if hasattr(viewset, 'create'):
            print("\n📝 Attempting direct create call...")
            try:
                response = viewset.create(request)
                print(f"✅ Direct create successful: Status {response.status_code}")
                if hasattr(response, 'data'):
                    print(f"Response data: {response.data}")
            except Exception as e:
                print(f"❌ Direct create failed: {e}")
        else:
            print("❌ Create method not found")
            
    except Exception as e:
        print(f"❌ ViewSet test failed: {e}")

def test_router_configuration():
    """Test the router configuration"""
    print("\n🔍 TESTING ROUTER CONFIGURATION")
    print("-" * 50)
    
    try:
        from products.urls_simple import router
        
        print("Router registry:")
        for prefix, viewset_class, basename in router.registry:
            print(f"  {prefix}: {viewset_class.__name__} (basename: {basename})")
            
            # Check if this is the products ViewSet
            if 'product' in prefix.lower():
                print(f"    Base classes: {[cls.__name__ for cls in viewset_class.__mro__]}")
                
                # Check methods
                instance = viewset_class()
                print(f"    HTTP methods: {instance.http_method_names}")
                print(f"    Has create: {hasattr(instance, 'create')}")
                print(f"    Has list: {hasattr(instance, 'list')}")
                print(f"    Has retrieve: {hasattr(instance, 'retrieve')}")
                print(f"    Has update: {hasattr(instance, 'update')}")
                print(f"    Has destroy: {hasattr(instance, 'destroy')}")
                
    except Exception as e:
        print(f"❌ Router test failed: {e}")

def test_url_resolution():
    """Test URL resolution"""
    print("\n🔍 TESTING URL RESOLUTION")
    print("-" * 50)
    
    try:
        from django.urls import resolve, reverse
        
        # Test different URL patterns
        urls_to_test = [
            '/api/v1/products/products/',
            '/api/v1/products/categories/',
        ]
        
        for url in urls_to_test:
            try:
                resolver_match = resolve(url)
                print(f"✅ {url}")
                print(f"    View: {resolver_match.func}")
                print(f"    View class: {getattr(resolver_match.func, 'view_class', 'N/A')}")
                print(f"    Actions: {getattr(resolver_match.func, 'actions', 'N/A')}")
                print(f"    Kwargs: {resolver_match.kwargs}")
            except Exception as e:
                print(f"❌ {url}: {e}")
                
    except Exception as e:
        print(f"❌ URL resolution test failed: {e}")

def test_http_methods_live():
    """Test HTTP methods on live endpoint"""
    print("\n🔍 TESTING LIVE HTTP METHODS")
    print("-" * 50)
    
    # Get authentication token
    login_resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json={
        'identifier': '+233548577399',
        'password': 'Kingsco45@1'
    })
    
    if login_resp.status_code != 200:
        print("❌ Login failed")
        return
        
    token = login_resp.json().get('access')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test different endpoints and methods
    endpoints = [
        'http://127.0.0.1:8000/api/v1/products/products/',
        'http://127.0.0.1:8000/api/v1/products/categories/',
    ]
    
    methods = ['GET', 'POST', 'OPTIONS']
    
    for endpoint in endpoints:
        print(f"\nTesting {endpoint}:")
        for method in methods:
            try:
                if method == 'POST':
                    if 'products/' in endpoint and 'categories' not in endpoint:
                        data = {
                            'name': 'HTTP Test Product',
                            'description': 'Test',
                            'price_per_unit': 10.00,
                            'category_id': 1,
                            'stock_quantity': 100,
                            'unit': 'kg',
                            'product_type': 'raw',
                            'organic_status': 'non_organic',
                            'origin_country': 'Ghana'
                        }
                    else:
                        data = {'name': 'Test Category', 'description': 'Test'}
                    
                    resp = requests.post(endpoint, json=data, headers=headers, timeout=5)
                else:
                    resp = requests.request(method, endpoint, headers=headers, timeout=5)
                    
                print(f"  {method}: {resp.status_code}")
                if resp.status_code == 405:
                    allowed = resp.headers.get('Allow', 'Not specified')
                    print(f"    Allowed: {allowed}")
                elif resp.status_code in [200, 201]:
                    print(f"    ✅ Success")
                elif resp.status_code >= 400:
                    print(f"    Error: {resp.text[:100]}...")
                    
            except Exception as e:
                print(f"  {method}: Error - {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("  PRODUCT CREATION DEBUG TOOL")
    print("=" * 60)
    
    test_viewset_directly()
    test_router_configuration()
    test_url_resolution()
    test_http_methods_live()
    
    print("\n" + "=" * 60)
    print("  DEBUG COMPLETE")
    print("=" * 60)
