#!/usr/bin/env python
"""
AgriConnect Warehouse Management System - Demo Setup
Creates sample warehouse data to demonstrate the complete warehouse system
"""

import os
import django
from decimal import Decimal
from datetime import date, timedelta
import django.utils.timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from warehouses.models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, WarehouseMovement, TemperatureLog, QualityInspection
)
from products.models import Product
from django.contrib.gis.geos import Point

User = get_user_model()

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 40)

def create_warehouse_demo_data():
    """Create comprehensive warehouse demo data"""
    
    print_header("AGRICONNECT WAREHOUSE MANAGEMENT DEMO SETUP")
    
    # Create Warehouse Types
    print_section("CREATING WAREHOUSE TYPES")
    
    cold_storage_type = WarehouseType.objects.create(
        name="Cold Storage Facility",
        warehouse_type="cold_storage",
        description="Temperature-controlled storage for perishable agricultural products",
        temperature_range_min=Decimal('2.0'),
        temperature_range_max=Decimal('8.0'),
        humidity_range_min=Decimal('80.0'),
        humidity_range_max=Decimal('95.0'),
        special_requirements={
            "backup_power": True,
            "temperature_monitoring": True,
            "humidity_control": True,
            "emergency_alerts": True
        }
    )
    
    dry_storage_type = WarehouseType.objects.create(
        name="Dry Storage Facility",
        warehouse_type="dry_storage",
        description="Climate-controlled storage for grains, cereals, and dried products",
        temperature_range_min=Decimal('15.0'),
        temperature_range_max=Decimal('25.0'),
        humidity_range_min=Decimal('40.0'),
        humidity_range_max=Decimal('60.0'),
        special_requirements={
            "pest_control": True,
            "moisture_control": True,
            "ventilation": True,
            "fire_suppression": True
        }
    )
    
    organic_type = WarehouseType.objects.create(
        name="Organic Certified Facility",
        warehouse_type="organic",
        description="Certified organic storage with strict contamination controls",
        temperature_range_min=Decimal('10.0'),
        temperature_range_max=Decimal('20.0'),
        humidity_range_min=Decimal('50.0'),
        humidity_range_max=Decimal('70.0'),
        special_requirements={
            "organic_certification": True,
            "contamination_prevention": True,
            "dedicated_equipment": True,
            "traceability_systems": True
        }
    )
    
    print(f"✅ Created {WarehouseType.objects.count()} warehouse types")
    
    # Create Users for Warehouse Management
    print_section("CREATING WAREHOUSE MANAGERS AND STAFF")
    
    warehouse_manager = User.objects.create_user(
        username='warehouse_manager_accra',
        email='manager@accra-warehouse.com',
        phone_number='+233244567890',
        first_name='Kwame',
        last_name='Asante',
        country='GH',
        region='Greater Accra',
        is_verified=True,
        email_verified=True,
        phone_verified=True
    )
    
    zone_supervisor = User.objects.create_user(
        username='zone_supervisor_1',
        email='supervisor@accra-warehouse.com',
        phone_number='+233244567891',
        first_name='Ama',
        last_name='Osei',
        country='GH',
        region='Greater Accra',
        is_verified=True,
        email_verified=True,
        phone_verified=True
    )
    
    quality_inspector = User.objects.create_user(
        username='quality_inspector_1',
        email='inspector@accra-warehouse.com',
        phone_number='+233244567892',
        first_name='Kofi',
        last_name='Mensah',
        country='GH',
        region='Greater Accra',
        is_verified=True,
        email_verified=True,
        phone_verified=True
    )
    
    # Create Warehouses
    print_section("CREATING WAREHOUSES")
    
    accra_warehouse = Warehouse.objects.create(
        code="ACC-WH-001",
        name="AgriConnect Accra Central Warehouse",
        warehouse_type=cold_storage_type,
        country="Ghana",
        region="Greater Accra",
        city="Accra",
        address={
            "street": "Industrial Area Road",
            "district": "Tema",
            "postal_code": "GA-456-7890",
            "landmarks": ["Near Tema Port", "Close to Industrial Area"]
        },
        gps_coordinates="5.6037,-0.1870",
        capacity_cubic_meters=Decimal('5000.00'),
        current_utilization_percent=Decimal('65.5'),
        temperature_controlled=True,
        humidity_controlled=True,
        organic_certified=True,
        has_loading_dock=True,
        manager=warehouse_manager,
        status="active",
        contact_info={
            "phone": "+233302123456",
            "email": "accra@agriconnect.com",
            "emergency": "+233244567890"
        },
        operating_hours={
            "monday": "06:00-18:00",
            "tuesday": "06:00-18:00",
            "wednesday": "06:00-18:00",
            "thursday": "06:00-18:00",
            "friday": "06:00-18:00",
            "saturday": "08:00-16:00",
            "sunday": "08:00-12:00"
        },
        security_features=[
            "24/7 Security Guards",
            "CCTV Surveillance",
            "Access Control System",
            "Fire Suppression",
            "Intrusion Detection"
        ]
    )
    
    kumasi_warehouse = Warehouse.objects.create(
        code="KUM-WH-002",
        name="AgriConnect Kumasi Regional Hub",
        warehouse_type=dry_storage_type,
        country="Ghana",
        region="Ashanti",
        city="Kumasi",
        address={
            "street": "Suame Industrial Area",
            "district": "Suame",
            "postal_code": "AK-123-4567",
            "landmarks": ["Suame Magazine", "Near Kumasi Airport"]
        },
        gps_coordinates="6.6885,-1.6244",
        capacity_cubic_meters=Decimal('8000.00'),
        current_utilization_percent=Decimal('72.3'),
        temperature_controlled=True,
        humidity_controlled=True,
        organic_certified=False,
        has_loading_dock=True,
        manager=warehouse_manager,
        status="active",
        contact_info={
            "phone": "+233322123456",
            "email": "kumasi@agriconnect.com",
            "emergency": "+233244567891"
        }
    )
    
    print(f"✅ Created {Warehouse.objects.count()} warehouses")
    
    # Create Warehouse Zones
    print_section("CREATING WAREHOUSE ZONES")
    
    # Accra Warehouse Zones
    cold_zone = WarehouseZone.objects.create(
        warehouse=accra_warehouse,
        zone_code="COLD-A",
        name="Cold Storage Zone A",
        zone_type="cold_storage",
        capacity_cubic_meters=Decimal('1500.00'),
        current_stock_level=Decimal('980.50'),
        temperature_range={"min": 2, "max": 8},
        special_conditions={
            "backup_cooling": True,
            "temperature_alarms": True,
            "humidity_control": True
        },
        is_active=True
    )
    
    organic_zone = WarehouseZone.objects.create(
        warehouse=accra_warehouse,
        zone_code="ORG-A",
        name="Organic Products Zone",
        zone_type="organic_zone",
        capacity_cubic_meters=Decimal('1200.00'),
        current_stock_level=Decimal('750.25'),
        temperature_range={"min": 10, "max": 20},
        special_conditions={
            "organic_certified": True,
            "contamination_barriers": True,
            "dedicated_equipment": True
        },
        is_active=True
    )
    
    dry_zone = WarehouseZone.objects.create(
        warehouse=accra_warehouse,
        zone_code="DRY-A",
        name="Dry Storage Zone A",
        zone_type="dry_storage",
        capacity_cubic_meters=Decimal('2000.00'),
        current_stock_level=Decimal('1320.75'),
        temperature_range={"min": 15, "max": 25},
        special_conditions={
            "pest_control": True,
            "moisture_barriers": True,
            "ventilation": True
        },
        is_active=True
    )
    
    # Kumasi Warehouse Zones
    grain_zone = WarehouseZone.objects.create(
        warehouse=kumasi_warehouse,
        zone_code="GRAIN-A",
        name="Grain Storage Zone A",
        zone_type="dry_storage",
        capacity_cubic_meters=Decimal('3000.00'),
        current_stock_level=Decimal('2150.80'),
        temperature_range={"min": 18, "max": 22},
        special_conditions={
            "grain_silos": True,
            "aeration_system": True,
            "quality_monitoring": True
        },
        is_active=True
    )
    
    processing_zone = WarehouseZone.objects.create(
        warehouse=kumasi_warehouse,
        zone_code="PROC-A",
        name="Processing Area A",
        zone_type="processing_area",
        capacity_cubic_meters=Decimal('1500.00'),
        current_stock_level=Decimal('890.40'),
        temperature_range={"min": 20, "max": 25},
        special_conditions={
            "processing_equipment": True,
            "packaging_area": True,
            "quality_control": True
        },
        is_active=True
    )
    
    print(f"✅ Created {WarehouseZone.objects.count()} warehouse zones")
    
    # Create Warehouse Staff
    print_section("CREATING WAREHOUSE STAFF")
    
    WarehouseStaff.objects.create(
        warehouse=accra_warehouse,
        user=warehouse_manager,
        role="manager",
        access_zones=[str(cold_zone.id), str(organic_zone.id), str(dry_zone.id)],
        permissions={
            "inventory_management": True,
            "staff_management": True,
            "quality_control": True,
            "reporting": True
        },
        is_active=True,
        hired_date=date.today() - timedelta(days=365),
        performance_rating=Decimal('4.8'),
        certifications=["Warehouse Management", "Cold Chain", "Organic Handling"]
    )
    
    WarehouseStaff.objects.create(
        warehouse=accra_warehouse,
        user=zone_supervisor,
        role="supervisor",
        access_zones=[str(cold_zone.id), str(organic_zone.id)],
        permissions={
            "inventory_management": True,
            "quality_control": True,
            "staff_coordination": True
        },
        is_active=True,
        hired_date=date.today() - timedelta(days=180),
        performance_rating=Decimal('4.5'),
        certifications=["Food Safety", "Cold Chain Management"]
    )
    
    WarehouseStaff.objects.create(
        warehouse=accra_warehouse,
        user=quality_inspector,
        role="quality_inspector",
        access_zones=[str(organic_zone.id), str(dry_zone.id)],
        permissions={
            "quality_inspections": True,
            "certification": True,
            "compliance_monitoring": True
        },
        is_active=True,
        hired_date=date.today() - timedelta(days=90),
        performance_rating=Decimal('4.9'),
        certifications=["Quality Assurance", "Organic Certification", "HACCP"]
    )
    
    print(f"✅ Created {WarehouseStaff.objects.count()} warehouse staff members")
    
    # Create Sample Inventory (if products exist)
    print_section("CREATING WAREHOUSE INVENTORY")
    
    products = Product.objects.all()[:5]  # Get first 5 products if any exist
    
    if products.exists():
        for i, product in enumerate(products):
            # Choose appropriate zone based on product type
            zone = cold_zone if i % 2 == 0 else organic_zone if product.is_organic else dry_zone
            
            WarehouseInventory.objects.create(
                product=product,
                warehouse=accra_warehouse,
                zone=zone,
                quantity=Decimal(str(100 + i * 25)),
                reserved_quantity=Decimal(str(10 + i * 2)),
                batch_number=f"BATCH-{date.today().strftime('%Y%m%d')}-{i+1:03d}",
                lot_number=f"LOT-{date.today().year}-{i+1:04d}",
                manufacturing_date=date.today() - timedelta(days=30),
                harvest_date=date.today() - timedelta(days=35),
                expiry_date=date.today() + timedelta(days=180),
                received_date=date.today() - timedelta(days=25),
                quality_status="good",
                storage_conditions={
                    "temperature": zone.temperature_range,
                    "humidity": "controlled",
                    "lighting": "minimal"
                },
                last_inspection_date=date.today() - timedelta(days=7),
                next_inspection_date=date.today() + timedelta(days=23),
                inspector=quality_inspector,
                inspection_notes=f"Product quality excellent. Proper storage conditions maintained.",
                location_details={
                    "aisle": f"A{i+1}",
                    "shelf": f"S{i+1}",
                    "position": f"P{i+1}"
                },
                qr_code=f"QR-{accra_warehouse.code}-{zone.zone_code}-{i+1:04d}",
                rfid_tag=f"RFID-{i+1:08d}",
                notes=f"High-quality {product.name} from verified supplier"
            )
        
        print(f"✅ Created {WarehouseInventory.objects.count()} inventory items")
    else:
        print("⚠️  No products found. Inventory creation skipped.")
    
    # Create Temperature Logs
    print_section("CREATING TEMPERATURE MONITORING LOGS")
    
    for warehouse in [accra_warehouse, kumasi_warehouse]:
        for zone in warehouse.zones.all():
            # Create temperature logs for the last 7 days
            for day_offset in range(7):
                log_date = date.today() - timedelta(days=day_offset)
                
                # Create multiple readings per day
                for hour in [6, 12, 18, 23]:
                    temp_range = zone.temperature_range if zone.temperature_range else {"min": 15, "max": 25}
                    temp = (temp_range["min"] + temp_range["max"]) / 2 + (day_offset % 3) - 1  # Small variation
                    
                    TemperatureLog.objects.create(
                        warehouse=warehouse,
                        zone=zone,
                        temperature_celsius=Decimal(str(temp)),
                        humidity_percentage=Decimal('65.5'),
                        recorded_at=django.utils.timezone.make_aware(
                            django.utils.timezone.datetime.combine(log_date, django.utils.timezone.time(hour, 0))
                        ),
                        recorded_by=warehouse_manager,
                        sensor_id=f"TEMP-{zone.zone_code}-001",
                        alert_triggered=temp < temp_range["min"] or temp > temp_range["max"],
                        notes=f"Automated temperature reading - Zone {zone.zone_code}"
                    )
    
    print(f"✅ Created {TemperatureLog.objects.count()} temperature monitoring logs")
    
    # Create Quality Inspections
    print_section("CREATING QUALITY INSPECTION RECORDS")
    
    inventory_items = WarehouseInventory.objects.all()
    
    for i, inventory in enumerate(inventory_items):
        QualityInspection.objects.create(
            inspection_number=f"QI-{date.today().strftime('%Y%m%d')}-{i+1:04d}",
            inspection_type="routine",
            inventory=inventory,
            inspector=quality_inspector,
            inspection_date=date.today() - timedelta(days=i+1),
            visual_inspection={
                "appearance": "excellent",
                "color": "normal",
                "texture": "good",
                "contamination": "none"
            },
            physical_tests={
                "weight": "within_specs",
                "moisture_content": "acceptable",
                "firmness": "good"
            },
            chemical_tests={
                "ph_level": "normal",
                "pesticide_residue": "within_limits" if not inventory.product.is_organic else "none_detected"
            },
            microbiological_tests={
                "bacterial_count": "acceptable",
                "yeast_mold": "within_limits",
                "pathogens": "none_detected"
            },
            overall_result="pass",
            quality_score=85 + (i % 15),  # Score between 85-99
            findings=f"Product meets all quality standards. Storage conditions optimal.",
            recommendations="Continue current storage conditions. Next inspection in 30 days.",
            corrective_actions="None required",
            requires_follow_up=False,
            photos=[],
            documents=[]
        )
    
    print(f"✅ Created {QualityInspection.objects.count()} quality inspection records")
    
    # Display Summary
    print_section("WAREHOUSE SYSTEM SUMMARY")
    
    print(f"🏢 Warehouses: {Warehouse.objects.count()}")
    print(f"📦 Warehouse Types: {WarehouseType.objects.count()}")
    print(f"🏗️  Zones: {WarehouseZone.objects.count()}")
    print(f"👥 Staff Members: {WarehouseStaff.objects.count()}")
    print(f"📋 Inventory Items: {WarehouseInventory.objects.count()}")
    print(f"🌡️  Temperature Logs: {TemperatureLog.objects.count()}")
    print(f"✅ Quality Inspections: {QualityInspection.objects.count()}")
    
    print_section("WAREHOUSE ENDPOINTS READY")
    
    endpoints = [
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/dashboard/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/types/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/warehouses/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/zones/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/staff/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/inventory/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/movements/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/temperature-logs/",
        "🔗 http://127.0.0.1:8000/api/v1/warehouses/quality-inspections/"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")
    
    print_header("WAREHOUSE MANAGEMENT SYSTEM READY!")
    print("🎉 Complete warehouse management system with sample data created successfully!")
    print("🚀 All API endpoints are now functional and ready for testing.")

if __name__ == '__main__':
    create_warehouse_demo_data()
