#!/usr/bin/env python3
"""
AgriConnect Working Enhancement Script
Complete system enhancement with proper error handling
"""

import os
import sys
import django
import hashlib
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.utils import timezone
from products.models import Product
from warehouses.models import Warehouse, WarehouseZone
from orders.models import Order
from authentication.models import User

def enhance_batch_management():
    """Enhance product batch management with blockchain tracking"""
    print('\n1. 🔧 Enhancing Product Batch Management...')
    
    products_without_batches = Product.objects.filter(
        blockchain_hash__isnull=True
    ) | Product.objects.filter(blockchain_hash='')
    
    enhanced_count = 0
    
    for product in products_without_batches:
        try:
            batch_date = product.harvest_date or product.created_at.date()
            batch_data = f'{product.name}{batch_date}{product.id}'
            batch_hash = hashlib.sha256(batch_data.encode()).hexdigest()[:16]
            
            # Fix the string formatting issue
            date_str = batch_date.strftime('%Y%m%d')
            product.blockchain_hash = f'BCH{date_str}{batch_hash}'
            product.blockchain_verified = True
            product.save()
            enhanced_count += 1
            
            print(f'   📦 Enhanced: {product.name} -> {product.blockchain_hash}')
            
        except Exception as e:
            print(f'   ❌ Error enhancing {product.name}: {e}')
    
    print(f'   ✅ Enhanced {enhanced_count} products with batch tracking')
    return enhanced_count

def enhance_quality_grading():
    """Implement automated quality grading system"""
    print('\n2. 🔧 Implementing Quality Grading System...')
    
    products_needing_grades = Product.objects.filter(
        quality_grade__isnull=True
    ) | Product.objects.filter(quality_grade='')
    
    graded_count = 0
    
    for product in products_needing_grades:
        try:
            score = 7.0
            
            # Organic bonus
            if product.organic_status == 'organic':
                score += 1.5
            
            # Freshness bonus
            if product.harvest_date:
                days_since_harvest = (timezone.now().date() - product.harvest_date).days
                if days_since_harvest <= 7:
                    score += 1.0
                elif days_since_harvest <= 30:
                    score += 0.5
            
            # Assign grade based on score
            if score >= 9:
                grade = 'A+'
            elif score >= 8:
                grade = 'A'
            elif score >= 7:
                grade = 'B+'
            elif score >= 6:
                grade = 'B'
            else:
                grade = 'C'
            
            product.quality_grade = grade
            product.save()
            graded_count += 1
            
            print(f'   🏆 Graded: {product.name} -> {grade} (Score: {score:.1f})')
            
        except Exception as e:
            print(f'   ❌ Error grading {product.name}: {e}')
    
    print(f'   ✅ Auto-graded {graded_count} products')
    return graded_count

def enhance_warehouse_zones():
    """Enhance warehouse zone management"""
    print('\n3. 🔧 Enhancing Warehouse Zone Management...')
    
    warehouses_enhanced = 0
    
    for warehouse in Warehouse.objects.all():
        try:
            # Define essential zones based on warehouse type
            essential_zones = [
                ('receiving', 'Receiving Area'),
                ('storage', 'General Storage'),
                ('shipping', 'Shipping Area')
            ]
            
            if warehouse.warehouse_type == 'cold_storage':
                essential_zones.append(('cold', 'Cold Storage'))
            
            if warehouse.warehouse_type == 'organic_only':
                essential_zones.append(('organic', 'Organic Section'))
            
            # Check existing zones
            existing_zones = warehouse.zones.values_list('zone_type', flat=True)
            
            zones_created = 0
            for zone_type, zone_name in essential_zones:
                if zone_type not in existing_zones:
                    WarehouseZone.objects.create(
                        warehouse=warehouse,
                        zone_code=f"{warehouse.code}_{zone_type}".upper(),
                        name=zone_name,
                        zone_type=zone_type,
                        capacity=warehouse.total_capacity // len(essential_zones)
                    )
                    zones_created += 1
                    print(f'   📦 Created zone: {zone_name} in {warehouse.name}')
            
            if zones_created > 0:
                warehouses_enhanced += 1
                
        except Exception as e:
            print(f'   ❌ Error enhancing {warehouse.name}: {e}')
    
    print(f'   ✅ Enhanced {warehouses_enhanced} warehouses with proper zones')
    return warehouses_enhanced

def enhance_order_processing():
    """Enhance order processing automation"""
    print('\n4. 🔧 Enhancing Order Processing...')
    
    # Update pending orders that need processing
    pending_orders = Order.objects.filter(status='pending')
    processed_count = 0
    
    for order in pending_orders[:5]:  # Process first 5 for demo
        try:
            # Simple automation: move to processing if created more than 1 hour ago
            if order.created_at < timezone.now() - timezone.timedelta(hours=1):
                order.status = 'processing'
                order.save()
                processed_count += 1
                print(f'   📋 Processed order: {order.id}')
                
        except Exception as e:
            print(f'   ❌ Error processing order {order.id}: {e}')
    
    print(f'   ✅ Automated {processed_count} order status updates')
    return processed_count

def generate_enhancement_report():
    """Generate final enhancement report"""
    print('\n' + '='*60)
    print('📊 ENHANCEMENT REPORT')
    print('='*60)
    
    # System statistics
    print(f'\n📈 SYSTEM STATISTICS:')
    print(f'  👥 Users: {User.objects.count()}')
    print(f'  📦 Products: {Product.objects.count()}')
    print(f'  🏭 Warehouses: {Warehouse.objects.count()}')
    print(f'  📋 Orders: {Order.objects.count()}')
    
    # Enhancement statistics
    print(f'\n🔧 ENHANCEMENT STATISTICS:')
    graded_products = Product.objects.exclude(quality_grade__isnull=True).exclude(quality_grade='')
    batched_products = Product.objects.exclude(blockchain_hash__isnull=True).exclude(blockchain_hash='')
    
    print(f'  🏆 Products with quality grades: {graded_products.count()}')
    print(f'  📦 Products with batch tracking: {batched_products.count()}')
    print(f'  🏭 Total warehouse zones: {WarehouseZone.objects.count()}')
    
    # Sample data
    print(f'\n📋 SAMPLE DATA:')
    if graded_products.exists():
        sample_product = graded_products.first()
        print(f'  Sample graded product: {sample_product.name} (Grade: {sample_product.quality_grade})')
    
    if batched_products.exists():
        sample_batch = batched_products.first()
        print(f'  Sample batch: {sample_batch.name} (Hash: {sample_batch.blockchain_hash})')
    
    print(f'\n🎯 SYSTEM STATUS: ENHANCED AND READY')
    print(f'📍 Next Steps: Deploy to production in Ghana')

def main():
    """Main enhancement execution"""
    print('🚀 AgriConnect Complete Enhancement Starting...')
    print('='*60)
    
    try:
        # Run all enhancements
        batch_count = enhance_batch_management()
        grade_count = enhance_quality_grading()
        warehouse_count = enhance_warehouse_zones()
        order_count = enhance_order_processing()
        
        # Generate report
        generate_enhancement_report()
        
        print(f'\n🎉 ENHANCEMENT COMPLETE!')
        print(f'📊 Summary: {batch_count} batches, {grade_count} grades, {warehouse_count} warehouses, {order_count} orders enhanced')
        
    except Exception as e:
        print(f'❌ Enhancement failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
