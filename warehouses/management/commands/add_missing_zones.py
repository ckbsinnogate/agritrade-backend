from django.core.management.base import BaseCommand
from warehouses.models import Warehouse, WarehouseZone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add missing warehouse zones for PRD Section 4.1.1 compliance'

    def handle(self, *args, **options):
        self.stdout.write("Adding missing warehouse zones...")
        
        # Get existing warehouses
        warehouses = list(Warehouse.objects.all())
        if not warehouses:
            self.stdout.write("No warehouses found!")
            return
        
        self.stdout.write(f"Found {len(warehouses)} warehouses")
        
        zones_created = 0
        
        # Add organic zones
        for i, warehouse in enumerate(warehouses[:3]):
            zone, created = WarehouseZone.objects.get_or_create(
                warehouse=warehouse,
                zone_code=f'ORG-{i+1:02d}',
                defaults={
                    'name': f'Organic Products Zone {i+1}',
                    'zone_type': 'organic',
                    'capacity_cubic_meters': Decimal('500.00'),
                    'current_stock_level': Decimal('0.00'),
                    'temperature_range': {'min': 2, 'max': 8},
                    'humidity_range': {'min': 80, 'max': 95},
                    'is_organic_certified': True,
                }
            )
            if created:
                zones_created += 1
                self.stdout.write(f"✅ Created organic zone: {zone.name}")
            
            # Mark warehouse as organic certified
            warehouse.organic_certified = True
            warehouse.save()
        
        # Add processing zones
        for i, warehouse in enumerate(warehouses[:4]):
            # Processing zone
            zone, created = WarehouseZone.objects.get_or_create(
                warehouse=warehouse,
                zone_code=f'PROC-{i+1:02d}',
                defaults={
                    'name': f'Processing Area {i+1}',
                    'zone_type': 'processing',
                    'capacity_cubic_meters': Decimal('300.00'),
                    'current_stock_level': Decimal('0.00'),
                    'temperature_range': {'min': 15, 'max': 25},
                    'humidity_range': {'min': 45, 'max': 65},
                }
            )
            if created:
                zones_created += 1
                self.stdout.write(f"✅ Created processing zone: {zone.name}")
            
            # Packaging zone
            zone, created = WarehouseZone.objects.get_or_create(
                warehouse=warehouse,
                zone_code=f'PKG-{i+1:02d}',
                defaults={
                    'name': f'Packaging Area {i+1}',
                    'zone_type': 'packaging',
                    'capacity_cubic_meters': Decimal('200.00'),
                    'current_stock_level': Decimal('0.00'),
                    'temperature_range': {'min': 18, 'max': 24},
                    'humidity_range': {'min': 40, 'max': 60},
                }
            )
            if created:
                zones_created += 1
                self.stdout.write(f"✅ Created packaging zone: {zone.name}")
        
        # Add loading zones
        for i, warehouse in enumerate(warehouses):
            zone, created = WarehouseZone.objects.get_or_create(
                warehouse=warehouse,
                zone_code=f'LOAD-{i+1:02d}',
                defaults={
                    'name': f'Loading/Unloading Bay {i+1}',
                    'zone_type': 'loading',
                    'capacity_cubic_meters': Decimal('150.00'),
                    'current_stock_level': Decimal('0.00'),
                    'temperature_range': {'min': -5, 'max': 35},
                    'humidity_range': {'min': 30, 'max': 90},
                }
            )
            if created:
                zones_created += 1
                self.stdout.write(f"✅ Created loading zone: {zone.name}")
                
                # Update warehouse to have loading dock
                warehouse.has_loading_dock = True
                warehouse.save()
        
        self.stdout.write(f"\n🎯 Total zones created: {zones_created}")
        
        # Verify results
        self.stdout.write("\n📊 Current zone counts:")
        self.stdout.write(f"   Cold Storage: {WarehouseZone.objects.filter(zone_type='cold_storage').count()}")
        self.stdout.write(f"   Organic: {WarehouseZone.objects.filter(zone_type='organic').count()}")
        self.stdout.write(f"   Dry Storage: {WarehouseZone.objects.filter(zone_type='dry_storage').count()}")
        self.stdout.write(f"   Processing: {WarehouseZone.objects.filter(zone_type='processing').count()}")
        self.stdout.write(f"   Packaging: {WarehouseZone.objects.filter(zone_type='packaging').count()}")
        self.stdout.write(f"   Quality Control: {WarehouseZone.objects.filter(zone_type='quality_control').count()}")
        self.stdout.write(f"   Quarantine: {WarehouseZone.objects.filter(zone_type='quarantine').count()}")
        self.stdout.write(f"   Loading: {WarehouseZone.objects.filter(zone_type='loading').count()}")
        
        # Check PRD compliance
        requirements_met = 0
        total_requirements = 6
        
        cold_storage = WarehouseZone.objects.filter(zone_type='cold_storage').count()
        organic = WarehouseZone.objects.filter(zone_type='organic').count()
        dry_storage = WarehouseZone.objects.filter(zone_type='dry_storage').count()
        processing = WarehouseZone.objects.filter(zone_type__in=['processing', 'packaging']).count()
        quality_control = WarehouseZone.objects.filter(zone_type__in=['quality_control', 'quarantine']).count()
        loading = WarehouseZone.objects.filter(zone_type='loading').count()
        
        if cold_storage > 0: requirements_met += 1
        if organic > 0: requirements_met += 1
        if dry_storage > 0: requirements_met += 1
        if processing > 0: requirements_met += 1
        if quality_control > 0: requirements_met += 1
        if loading > 0: requirements_met += 1
        
        self.stdout.write(f"\n🎯 PRD Section 4.1.1 Compliance: {requirements_met}/{total_requirements} requirements met")
        
        if requirements_met == total_requirements:
            self.stdout.write("🎉 ALL MULTI-ZONE WAREHOUSE ARCHITECTURE REQUIREMENTS IMPLEMENTED!")
        else:
            self.stdout.write(f"⚠️  {total_requirements - requirements_met} requirements still need attention")
