#!/usr/bin/env python3
"""
Create comprehensive traceability records for batch management
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from products.models import TraceabilityRecord
from warehouses.models import WarehouseInventory
from users.models import User
from django.utils import timezone
import random

def main():
    print('🔗 Creating comprehensive traceability records...')

    # Get sample data
    items = list(WarehouseInventory.objects.exclude(batch_number='')[:6])
    user = User.objects.first()
    
    stages = [
        'planting', 'growing', 'harvesting', 'post_harvest', 
        'processing', 'packaging', 'storage', 'transport'
    ]

    if items and user:
        created = 0
        for item in items:
            for stage in stages[:5]:  # 5 stages per item
                record, created_new = TraceabilityRecord.objects.get_or_create(
                    product=item.product,
                    stage=stage,
                    actor=user,
                    defaults={
                        'location': f'{item.warehouse.region}, {item.warehouse.country}',
                        'timestamp': timezone.now(),
                        'description': f'{stage.title()} of {item.product.name} batch {item.batch_number}',
                        'quality_score': random.randint(7, 10),
                        'blockchain_verified': True,
                        'blockchain_hash': f'hash_{random.randint(100000, 999999)}'
                    }
                )
                if created_new:
                    created += 1
                    print(f'   ✅ Created: {item.product.name} - {stage.title()}')

        print(f'\n📊 Summary:')
        print(f'   ✅ Created {created} new traceability records')
        print(f'   📊 Total traceability records: {TraceabilityRecord.objects.count()}')
        print(f'   📦 Products with traceability: {TraceabilityRecord.objects.values("product").distinct().count()}')
        print(f'   🔗 Average stages per product: {TraceabilityRecord.objects.count() / max(1, TraceabilityRecord.objects.values("product").distinct().count()):.1f}')
        
        # Show some examples
        print(f'\n📋 Sample Traceability Chain:')
        sample_product = TraceabilityRecord.objects.first().product
        records = TraceabilityRecord.objects.filter(product=sample_product).order_by('timestamp')
        for record in records[:4]:
            print(f'   • {record.get_stage_display()}: {record.description}')
            
        print(f'\n🎉 Batch Management with Complete Traceability: IMPLEMENTED!')
    else:
        print('❌ No data available for traceability creation')

if __name__ == "__main__":
    main()
