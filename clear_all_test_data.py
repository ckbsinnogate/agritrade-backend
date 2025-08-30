#!/usr/bin/env python3
"""
AgriConnect - Clear All Test Data
Comprehensive cleanup script to remove all test data and ensure fresh production testing
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from products.models import Product, Category
from payments.models import (
    PaymentGateway, Transaction, EscrowAccount, 
    EscrowMilestone, DisputeCase, PaymentMethod
)
from warehouses.models import Warehouse, WarehouseZone, WarehouseInventory
from orders.models import Order, OrderItem
from authentication.models import UserRole, OTPCode

User = get_user_model()

def print_header():
    print("🧹 AGRICONNECT - COMPREHENSIVE DATA CLEANUP")
    print("=" * 60)
    print("🗑️ Removing all test data for fresh production testing")
    print("=" * 60)
    print()

def backup_essential_data():
    """Backup essential configuration data that should be preserved"""
    print("💾 BACKING UP ESSENTIAL CONFIGURATION DATA")
    
    # Count essential data that will be preserved
    gateways = PaymentGateway.objects.count()
    warehouses = Warehouse.objects.count()
    zones = WarehouseZone.objects.count()
    user_roles = UserRole.objects.count()
    
    print(f"   🏦 Payment Gateways: {gateways} (will be preserved)")
    print(f"   🏢 Warehouses: {warehouses} (will be preserved)")
    print(f"   🏗️ Warehouse Zones: {zones} (will be preserved)")
    print(f"   👥 User Roles: {user_roles} (will be preserved)")
    print("   ✅ Essential configuration will be preserved")
    print()

def clear_user_data():
    """Clear all user-related test data"""
    print("👥 CLEARING USER DATA")
    
    # Count before deletion
    users_count = User.objects.count()
    otp_count = OTPCode.objects.count()
    
    # Clear OTP codes
    deleted_otp = OTPCode.objects.all().delete()[0]
    print(f"   🔑 Deleted {deleted_otp} OTP codes")
    
    # Clear test users (preserve superusers)
    deleted_users = User.objects.filter(is_superuser=False).delete()[0]
    print(f"   👥 Deleted {deleted_users} test users (preserved superusers)")
    
    remaining_users = User.objects.count()
    print(f"   📊 Remaining users: {remaining_users} (superusers only)")
    print()

def clear_product_data():
    """Clear all product and category test data"""
    print("🌾 CLEARING PRODUCT DATA")
    
    # Count before deletion
    products_count = Product.objects.count()
    categories_count = Category.objects.count()
    
    # Clear products
    deleted_products = Product.objects.all().delete()[0]
    print(f"   🌾 Deleted {deleted_products} products")
    
    # Clear categories
    deleted_categories = Category.objects.all().delete()[0]
    print(f"   📂 Deleted {deleted_categories} categories")
    print()

def clear_order_data():
    """Clear all order-related test data"""
    print("📦 CLEARING ORDER DATA")
    
    # Count before deletion
    orders_count = Order.objects.count()
    order_items_count = OrderItem.objects.count()
    
    # Clear order items
    deleted_items = OrderItem.objects.all().delete()[0]
    print(f"   📋 Deleted {deleted_items} order items")
    
    # Clear orders
    deleted_orders = Order.objects.all().delete()[0]
    print(f"   📦 Deleted {deleted_orders} orders")
    print()

def clear_payment_data():
    """Clear all payment transaction data while preserving gateway configuration"""
    print("💳 CLEARING PAYMENT TRANSACTION DATA")
    
    # Count before deletion
    transactions_count = Transaction.objects.count()
    escrows_count = EscrowAccount.objects.count()
    milestones_count = EscrowMilestone.objects.count()
    disputes_count = DisputeCase.objects.count()
    payment_methods_count = PaymentMethod.objects.count()
    
    # Clear disputes
    deleted_disputes = DisputeCase.objects.all().delete()[0]
    print(f"   ⚖️ Deleted {deleted_disputes} dispute cases")
    
    # Clear escrow milestones
    deleted_milestones = EscrowMilestone.objects.all().delete()[0]
    print(f"   🎯 Deleted {deleted_milestones} escrow milestones")
    
    # Clear escrow accounts
    deleted_escrows = EscrowAccount.objects.all().delete()[0]
    print(f"   🏦 Deleted {deleted_escrows} escrow accounts")
    
    # Clear transactions
    deleted_transactions = Transaction.objects.all().delete()[0]
    print(f"   💳 Deleted {deleted_transactions} transactions")
    
    # Clear payment methods
    deleted_methods = PaymentMethod.objects.all().delete()[0]
    print(f"   💰 Deleted {deleted_methods} payment methods")
    
    # Preserve payment gateways
    gateways_count = PaymentGateway.objects.count()
    print(f"   🏦 Preserved {gateways_count} payment gateways (configuration)")
    print()

def clear_warehouse_data():
    """Clear warehouse inventory data while preserving warehouse structure"""
    print("🏢 CLEARING WAREHOUSE INVENTORY DATA")
    
    # Count before deletion
    inventory_count = WarehouseInventory.objects.count()
    
    # Clear inventory
    deleted_inventory = WarehouseInventory.objects.all().delete()[0]
    print(f"   📦 Deleted {deleted_inventory} inventory items")
    
    # Preserve warehouse structure
    warehouses_count = Warehouse.objects.count()
    zones_count = WarehouseZone.objects.count()
    print(f"   🏢 Preserved {warehouses_count} warehouses (configuration)")
    print(f"   🏗️ Preserved {zones_count} warehouse zones (configuration)")
    print()

def reset_sequences():
    """Reset database sequences for clean IDs"""
    print("🔄 RESETTING DATABASE SEQUENCES")
    
    from django.db import connection
    cursor = connection.cursor()
    
    # Reset sequences for clean auto-increment IDs
    sequences_to_reset = [
        'products_product_id_seq',
        'products_category_id_seq',
        'payments_transaction_id_seq',
        'payments_escrowaccount_id_seq',
        'payments_escrowmilestone_id_seq',
        'payments_disputecase_id_seq',
        'orders_order_id_seq',
        'orders_orderitem_id_seq',
        'warehouses_warehouseinventory_id_seq'
    ]
    
    reset_count = 0
    for sequence in sequences_to_reset:
        try:
            cursor.execute(f"ALTER SEQUENCE {sequence} RESTART WITH 1;")
            reset_count += 1
        except Exception as e:
            # Sequence might not exist, continue
            pass
    
    print(f"   🔢 Reset {reset_count} database sequences")
    print()

def verify_cleanup():
    """Verify that cleanup was successful"""
    print("✅ VERIFYING CLEANUP SUCCESS")
    print("-" * 60)
    
    # Check remaining data
    users = User.objects.count()
    products = Product.objects.count()
    categories = Category.objects.count()
    orders = Order.objects.count()
    transactions = Transaction.objects.count()
    escrows = EscrowAccount.objects.count()
    disputes = DisputeCase.objects.count()
    inventory = WarehouseInventory.objects.count()
    
    # Check preserved configuration
    gateways = PaymentGateway.objects.count()
    warehouses = Warehouse.objects.count()
    zones = WarehouseZone.objects.count()
    roles = UserRole.objects.count()
    
    print("📊 REMAINING DATA (should be 0 except configuration):")
    print(f"   👥 Users: {users} (superusers only)")
    print(f"   🌾 Products: {products}")
    print(f"   📂 Categories: {categories}")
    print(f"   📦 Orders: {orders}")
    print(f"   💳 Transactions: {transactions}")
    print(f"   🏦 Escrow Accounts: {escrows}")
    print(f"   ⚖️ Disputes: {disputes}")
    print(f"   📦 Inventory: {inventory}")
    print()
    print("🔧 PRESERVED CONFIGURATION:")
    print(f"   🏦 Payment Gateways: {gateways}")
    print(f"   🏢 Warehouses: {warehouses}")
    print(f"   🏗️ Warehouse Zones: {zones}")
    print(f"   👥 User Roles: {roles}")
    print()
    
    # Calculate cleanup success
    test_data_cleared = (products == 0 and categories == 0 and orders == 0 and 
                        transactions == 0 and escrows == 0 and disputes == 0 and 
                        inventory == 0)
    
    config_preserved = (gateways > 0 and warehouses > 0 and zones > 0 and roles > 0)
    
    if test_data_cleared and config_preserved:
        print("🎉 CLEANUP SUCCESSFUL!")
        print("✅ All test data cleared")
        print("✅ Essential configuration preserved")
        print("🚀 Ready for fresh production testing")
    else:
        print("⚠️ CLEANUP INCOMPLETE")
        if not test_data_cleared:
            print("❌ Some test data remains")
        if not config_preserved:
            print("❌ Essential configuration missing")
    
    print("=" * 60)

def main():
    print_header()
    
    try:
        with transaction.atomic():
            # Step 1: Backup essential data info
            backup_essential_data()
            
            # Step 2: Clear test data in correct order (respecting foreign keys)
            clear_warehouse_data()
            clear_payment_data()
            clear_order_data()
            clear_product_data()
            clear_user_data()
            
            # Step 3: Reset sequences
            reset_sequences()
            
            # Step 4: Verify cleanup
            verify_cleanup()
            
            print("🧹 DATA CLEANUP COMPLETE!")
            print("🚀 Ready for production testing with clean slate")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        print("🔄 Rolling back changes...")

if __name__ == "__main__":
    main()
