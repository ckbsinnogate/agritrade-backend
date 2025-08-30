#!/usr/bin/env python
"""
AgriConnect Order Management System - Live Demonstration
Showcases complete order workflow including cart management and order processing
"""

import os
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from orders.models import Order, OrderItem, ShippingMethod
from products.models import Product
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🌾 {title}")
    print("=" * 60)

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_order_system():
    """Demonstrate the complete order management system"""
    
    print_header("AGRICONNECT ORDER MANAGEMENT SYSTEM - LIVE DEMO")
    
    # System Overview
    print_section("SYSTEM OVERVIEW")
    total_orders = Order.objects.count()
    total_items = OrderItem.objects.count()
    total_products = Product.objects.filter(status='active').count()
    total_users = User.objects.count()
    
    print(f"🏪 Active Products: {total_products}")
    print(f"👥 Registered Users: {total_users}")
    print(f"📦 Total Orders: {total_orders}")
    print(f"📋 Order Items: {total_items}")
    
    # Order Statistics
    print_section("ORDER ANALYTICS")
    from django.db.models import Sum, Avg, Count
    
    stats = Order.objects.aggregate(
        total_value=Sum('total_amount'),
        avg_value=Avg('total_amount'),
        order_count=Count('id')
    )
    
    print(f"💰 Total Order Value: GHS {stats['total_value'] or 0}")
    print(f"📊 Average Order: GHS {stats['avg_value'] or 0:.2f}")
    
    # Status breakdown
    status_counts = Order.objects.values('status').annotate(count=Count('id'))
    print(f"\n📈 Order Status Distribution:")
    for item in status_counts:
        print(f"   {item['status'].upper()}: {item['count']} orders")
    
    # Recent Orders
    print_section("RECENT ORDERS")
    recent_orders = Order.objects.order_by('-created_at')[:3]
    
    for order in recent_orders:
        print(f"🛒 Order {order.order_number}")
        print(f"   Buyer: {order.buyer.first_name} {order.buyer.last_name}")
        print(f"   Status: {order.status.upper()}")
        print(f"   Value: GHS {order.total_amount}")
        print(f"   Items: {order.items.count()}")
        print(f"   Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()
    
    # Product Performance
    print_section("TOP SELLING PRODUCTS")
    from django.db.models import Sum as DBSum
    
    top_products = Product.objects.annotate(
        total_ordered=DBSum('orderitem__quantity')
    ).filter(total_ordered__isnull=False).order_by('-total_ordered')[:3]
    
    for i, product in enumerate(top_products, 1):
        print(f"{i}. {product.name}")
        print(f"   Category: {product.category.name}")
        print(f"   Price: GHS {product.price_per_unit}/{product.unit}")
        print(f"   Ordered: {product.total_ordered or 0} {product.unit}")
        print(f"   Stock: {product.stock_quantity} {product.unit}")
        print()
    
    # Shipping Methods
    print_section("SHIPPING OPTIONS")
    shipping_methods = ShippingMethod.objects.all()
    
    for method in shipping_methods:
        print(f"🚚 {method.name}")
        print(f"   Base Cost: GHS {method.base_cost}")
        print(f"   Per KG: GHS {method.cost_per_kg}")
        print(f"   Delivery: {method.estimated_days_min}-{method.estimated_days_max} days")
        print(f"   Regions: {', '.join(method.available_regions[:3])}...")
        print()
    
    # API Endpoints Summary
    print_section("API ENDPOINTS SUMMARY")
    endpoints = [
        ("GET /api/v1/orders/", "API information and features"),
        ("GET /api/v1/orders/orders/", "List all orders (paginated)"),
        ("POST /api/v1/orders/orders/", "Create new order"),
        ("GET /api/v1/orders/orders/{id}/", "Get order details"),
        ("PUT /api/v1/orders/orders/{id}/", "Update order"),
        ("DELETE /api/v1/orders/orders/{id}/", "Cancel order"),
        ("GET /api/v1/orders/cart/", "View shopping cart"),
        ("POST /api/v1/orders/cart/add_item/", "Add item to cart"),
        ("POST /api/v1/orders/cart/checkout/", "Convert cart to order"),
        ("GET /api/v1/orders/statistics/", "Order analytics"),
        ("GET /api/v1/orders/orders/my_purchases/", "User's purchase history"),
        ("GET /api/v1/orders/orders/my_sales/", "User's sales history"),
    ]
    
    for endpoint, description in endpoints:
        print(f"🔗 {endpoint:<35} - {description}")
    
    # System Features
    print_section("KEY FEATURES IMPLEMENTED")
    features = [
        "✅ Complete Order Lifecycle Management",
        "✅ Session-Based Shopping Cart",
        "✅ Real-Time Inventory Synchronization", 
        "✅ Order Status Tracking with History",
        "✅ User-Specific Purchase/Sales Views",
        "✅ Advanced Order Filtering and Search",
        "✅ Shipping Method Integration",
        "✅ Payment Status Tracking",
        "✅ Geographic Delivery Support",
        "✅ Bulk Order Support for Agriculture",
        "✅ Order Analytics and Statistics",
        "✅ Django Admin Integration",
        "✅ RESTful API with Authentication",
        "✅ Error Handling and Validation",
        "✅ Scalable Database Design"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    # Sample Order Workflow
    print_section("SAMPLE ORDER WORKFLOW")
    if recent_orders:
        sample_order = recent_orders[0]
        print(f"📦 Demonstrating Order: {sample_order.order_number}")
        print()
        print("🔄 Order Lifecycle:")
        print("   1. 🛒 Items added to cart")
        print("   2. ✅ Cart validated (stock, pricing)")
        print("   3. 📝 Order created from cart")
        print("   4. 💰 Payment processing initiated")
        print("   5. 📋 Inventory automatically updated")
        print("   6. 🚚 Shipping method assigned")
        print("   7. 📱 Status updates tracked")
        print("   8. 🎯 Delivery to customer")
        print()
        print(f"Current Status: {sample_order.status.upper()}")
        print(f"Payment Status: {sample_order.payment_status.upper()}")
        print(f"Delivery Address: {sample_order.delivery_address}")
        print(f"Expected Delivery: {sample_order.expected_delivery_date}")
    
    # Integration Points
    print_section("INTEGRATION READY")
    integrations = [
        "💳 Payment Gateways (Paystack, Flutterwave)",
        "📱 SMS Notifications (Twilio, local providers)",
        "📧 Email Alerts (SendGrid, SMTP)",
        "🚚 Logistics Partners (DHL, local couriers)",
        "📱 Mobile Applications (React Native, Flutter)",
        "🌐 Web Frontend (Next.js, React)",
        "📊 Analytics Platforms (Google Analytics)",
        "🔍 Search Services (Elasticsearch, Algolia)"
    ]
    
    for integration in integrations:
        print(f"  {integration}")
    
    print_header("AGRICONNECT PHASE 3: ORDER MANAGEMENT - FULLY OPERATIONAL! 🚀")
    print("🌍 Ready to revolutionize African agricultural commerce!")
    print("📞 Contact: AgriConnect Development Team")
    print("🌾 'Connecting Africa's Farmers to Global Markets'")

if __name__ == '__main__':
    demo_order_system()
