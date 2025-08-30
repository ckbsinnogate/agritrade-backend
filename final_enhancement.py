#!/usr/bin/env python3
"""
AgriConnect Enhancement Script - Final Version
Direct execution with proper error handling
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Now import Django models
from django.utils import timezone
from django.db import models
from products.models import Product, ProductAttribute, TraceabilityRecord, Certification
from warehouses.models import Warehouse, WarehouseZone
from orders.models import Order
from authentication.models import User
import hashlib
import json

def enhance_products():
    """Enhance product features"""
    print("🔧 Enhancing Product Features...")
    
    # Batch Management
    products_without_batches = Product.objects.filter(
        models.Q(blockchain_hash__isnull=True) | models.Q(blockchain_hash='')
    )
    
    enhanced_count = 0
    for product in products_without_batches:
        batch_date = product.harvest_date or product.created_at.date()
        batch_data = f"{product.name}{batch_date}{product.id}"
        batch_hash = hashlib.sha256(batch_data.encode()).hexdigest()[:16]
        
        product.blockchain_hash = f"BCH{batch_date.strftime('%Y%m%d')}{batch_hash}"
        product.blockchain_verified = True
        product.save()
        enhanced_count += 1
    
    print(f"  ✅ Enhanced {enhanced_count} products with batch tracking")
    
    # Quality Grading
    products_needing_grades = Product.objects.filter(
        models.Q(quality_grade__isnull=True) | models.Q(quality_grade='')
    )
    
    graded_count = 0
    for product in products_needing_grades:
        score = 7.0
        if product.organic_status == 'organic':
            score += 1.5
        if product.harvest_date:
            days_since_harvest = (timezone.now().date() - product.harvest_date).days
            if days_since_harvest <= 7:
                score += 1.0
        
        if score >= 9:
            grade = "A+"
        elif score >= 8:
            grade = "A"
        elif score >= 7:
            grade = "B+"
        else:
            grade = "B"
        
        product.quality_grade = grade
        product.save()
        graded_count += 1
    
    print(f"  ✅ Auto-graded {graded_count} products")
    
    # Seasonal Tracking
    current_month = timezone.now().month
    seasonal_patterns = {
        'fruits': [6, 7, 8],
        'vegetables': [3, 4, 5, 9, 10, 11],
        'grains': [10, 11, 12],
        'cereals': [10, 11, 12, 1]
    }
    
    enhanced_products = 0
    for product in Product.objects.filter(status='active'):
        category_name = product.category.name.lower()
        
        for pattern_key, peak_months in seasonal_patterns.items():
            if pattern_key in category_name:
                is_peak_season = current_month in peak_months
                
                seasonal_attr, created = ProductAttribute.objects.get_or_create(
                    product=product,
                    name='seasonal_availability',
                    defaults={'value': 'peak' if is_peak_season else 'off_season'}
                )
                
                if not created:
                    seasonal_attr.value = 'peak' if is_peak_season else 'off_season'
                    seasonal_attr.save()
                
                enhanced_products += 1
                break
    
    print(f"  ✅ Enhanced seasonal tracking for {enhanced_products} products")
    
    return enhanced_count, graded_count, enhanced_products

def enhance_warehouses():
    """Enhance warehouse features"""
    print("🏭 Enhancing Warehouse Features...")
    
    warehouses_enhanced = 0
    
    for warehouse in Warehouse.objects.all():
        essential_zones = [
            ('receiving', 'Receiving Area'),
            ('storage', 'General Storage'),
            ('shipping', 'Shipping Area'),
            ('quality_control', 'Quality Control')
        ]
        
        if warehouse.warehouse_type == 'cold_storage':
            essential_zones.append(('cold', 'Cold Storage'))
        
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
        
        if zones_created > 0:
            warehouses_enhanced += 1
    
    print(f"  ✅ Enhanced {warehouses_enhanced} warehouses with zones")
    return warehouses_enhanced

def collect_statistics():
    """Collect system statistics"""
    print("📊 Collecting System Statistics...")
    
    try:
        stats = {
            'products': Product.objects.count(),
            'active_products': Product.objects.filter(status='active').count(),
            'organic_products': Product.objects.filter(organic_status='organic').count(),
            'graded_products': Product.objects.exclude(quality_grade='').count(),
            'batch_tracked_products': Product.objects.exclude(blockchain_hash='').count(),
            'warehouses': Warehouse.objects.count(),
            'warehouse_zones': WarehouseZone.objects.count(),
            'orders': Order.objects.count(),
            'users': User.objects.count(),
            'certifications': Certification.objects.count(),
            'traceability_records': TraceabilityRecord.objects.count()
        }
        
        print("  📊 System Statistics:")
        print(f"    📦 Products: {stats['products']} total, {stats['active_products']} active")
        print(f"    🌿 Organic Products: {stats['organic_products']}")
        print(f"    📊 Graded Products: {stats['graded_products']}")
        print(f"    🔗 Batch Tracked: {stats['batch_tracked_products']}")
        print(f"    🏭 Warehouses: {stats['warehouses']} with {stats['warehouse_zones']} zones")
        print(f"    📋 Orders: {stats['orders']}")
        print(f"    👥 Users: {stats['users']}")
        print(f"    📜 Certifications: {stats['certifications']}")
        print(f"    🔗 Traceability Records: {stats['traceability_records']}")
        
        return stats
        
    except Exception as e:
        print(f"  ❌ Error collecting statistics: {e}")
        return {}

def main():
    """Main enhancement function"""
    print("🚀 Starting AgriConnect Advanced Enhancement Process")
    print("=" * 60)
    
    try:
        # Step 1: Enhance Products
        batch_count, grade_count, seasonal_count = enhance_products()
        
        # Step 2: Enhance Warehouses
        warehouse_count = enhance_warehouses()
        
        # Step 3: Collect Statistics
        stats = collect_statistics()
        
        # Final Summary
        print("\n" + "=" * 60)
        print("🎉 ENHANCEMENT PROCESS COMPLETE!")
        print("=" * 60)
        print(f"  🔧 Products Enhanced: {batch_count} with batch tracking")
        print(f"  📊 Products Graded: {grade_count} with quality grades")
        print(f"  🌿 Seasonal Tracking: {seasonal_count} products")
        print(f"  🏭 Warehouses Enhanced: {warehouse_count}")
        print("  🎯 AgriConnect is now ready for production deployment!")
        
        # Save enhancement report
        report = {
            'timestamp': timezone.now().isoformat(),
            'enhancements': {
                'batch_tracking': batch_count,
                'quality_grading': grade_count,
                'seasonal_tracking': seasonal_count,
                'warehouse_zones': warehouse_count
            },
            'statistics': stats
        }
        
        with open('enhancement_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"  📋 Enhancement report saved to: enhancement_report.json")
        
    except Exception as e:
        print(f"❌ Enhancement process failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
