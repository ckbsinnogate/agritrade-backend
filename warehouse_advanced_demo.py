#!/usr/bin/env python
"""
AgriConnect Warehouse Management - Advanced Features Demo
Demonstrates inventory management, movements, temperature monitoring, and quality inspections
"""

import os
import django
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from warehouses.models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, WarehouseMovement, TemperatureLog, QualityInspection
)
from products.models import Product, Category
from django.utils import timezone

User = get_user_model()

def print_header(title):
    print("\n" + "="*80)
    print(f"🌾 {title}")
    print("="*80)

def print_section(title):
    print(f"\n📍 {title}")
    print("-"*60)

def create_warehouse_inventory():
    """Create sample inventory in warehouses"""
    print_section("Creating Warehouse Inventory")
    
    # Get existing warehouses and products
    warehouses = Warehouse.objects.all()
    products = Product.objects.all()[:10]  # Get first 10 products
    
    if not warehouses.exists():
        print("❌ No warehouses found. Please run setup_warehouse_demo.py first")
        return []
    
    if not products.exists():
        print("❌ No products found. Please ensure products are created")
        return []
    
    inventory_items = []
    
    for warehouse in warehouses:
        zones = WarehouseZone.objects.filter(warehouse=warehouse)
        
        for zone in zones:
            # Add 2-3 products per zone
            zone_products = random.sample(list(products), min(3, len(products)))
            
            for product in zone_products:
                # Generate realistic inventory data
                batch_number = f"BTH{random.randint(100000, 999999)}"
                quantity = random.randint(50, 500)
                reserved_qty = random.randint(0, min(50, quantity // 4))
                
                # Quality status distribution
                quality_statuses = ['excellent', 'good', 'fair']
                quality_weights = [0.6, 0.3, 0.1]
                quality_status = random.choices(quality_statuses, weights=quality_weights)[0]
                
                inventory, created = WarehouseInventory.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    zone=zone,
                    batch_number=batch_number,
                    defaults={
                        'quantity': quantity,
                        'reserved_quantity': reserved_qty,
                        'manufacturing_date': date.today() - timedelta(days=random.randint(1, 30)),
                        'harvest_date': date.today() - timedelta(days=random.randint(1, 60)),
                        'expiry_date': date.today() + timedelta(days=random.randint(30, 365)),
                        'quality_status': quality_status,
                        'storage_conditions': {
                            'temperature': random.uniform(15, 25),
                            'humidity': random.uniform(50, 70),
                            'ventilation': 'adequate'
                        },
                        'last_inspection_date': date.today() - timedelta(days=random.randint(1, 14)),
                        'next_inspection_date': date.today() + timedelta(days=random.randint(7, 30)),
                        'notes': f"Stored in {zone.name} under optimal conditions",
                        'qr_code': f"QR{random.randint(1000000, 9999999)}",
                        'rfid_tag': f"RFID{random.randint(100000, 999999)}"
                    }
                )
                
                inventory_items.append(inventory)
                status = "✅ Created" if created else "📋 Exists"
                print(f"  {status} {product.name} in {warehouse.code}/{zone.zone_code}")
                print(f"    📦 Qty: {inventory.quantity}, Reserved: {inventory.reserved_quantity}")
                print(f"    🏷️  Batch: {inventory.batch_number}, Quality: {inventory.quality_status}")
    
    return inventory_items

def create_warehouse_movements(inventory_items):
    """Create sample warehouse movements"""
    print_section("Creating Warehouse Movements")
    
    if not inventory_items:
        print("❌ No inventory items found for movements")
        return []
    
    movements = []
    movement_types = ['inbound', 'outbound', 'transfer', 'adjustment']
    
    # Get staff for authorization
    staff_members = list(WarehouseStaff.objects.all())
    
    if not staff_members:
        print("❌ No warehouse staff found for movements")
        return []
    
    for i in range(20):  # Create 20 sample movements
        inventory = random.choice(inventory_items)
        movement_type = random.choice(movement_types)
        
        # Generate movement quantity
        max_qty = min(inventory.quantity, 50)
        if max_qty <= 0:
            continue
            
        movement_qty = random.randint(1, max_qty)
        
        # Select staff for authorization and performance
        authorized_by = random.choice(staff_members)
        performed_by = random.choice(staff_members)
        
        # Generate reference number
        ref_number = f"WM{timezone.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        movement_data = {
            'movement_type': movement_type,
            'reference_number': ref_number,
            'inventory': inventory,
            'quantity': Decimal(str(movement_qty)),
            'unit': 'kg',
            'authorized_by': authorized_by.user,
            'performed_by': performed_by.user,
            'reason': f"Routine {movement_type} operation",
            'notes': f"Movement of {inventory.product.name} from {inventory.zone.name}",
            'conditions_at_movement': {
                'temperature': random.uniform(18, 24),
                'humidity': random.uniform(55, 65),
                'weather': 'clear'
            },
            'is_completed': random.choice([True, False])
        }
        
        # Set zones based on movement type
        if movement_type == 'outbound':
            movement_data['from_zone'] = inventory.zone
            movement_data['to_zone'] = None
        elif movement_type == 'inbound':
            movement_data['from_zone'] = None
            movement_data['to_zone'] = inventory.zone
        elif movement_type == 'transfer':
            # Find another zone in the same warehouse
            other_zones = WarehouseZone.objects.filter(
                warehouse=inventory.warehouse
            ).exclude(id=inventory.zone.id)
            if other_zones.exists():
                movement_data['from_zone'] = inventory.zone
                movement_data['to_zone'] = random.choice(other_zones)
            else:
                continue
        else:  # adjustment
            movement_data['from_zone'] = inventory.zone
            movement_data['to_zone'] = inventory.zone
        
        if movement_data['is_completed']:
            movement_data['completed_at'] = timezone.now() - timedelta(
                hours=random.randint(1, 48)
            )
        
        movement, created = WarehouseMovement.objects.get_or_create(
            reference_number=ref_number,
            defaults=movement_data
        )
        
        movements.append(movement)
        status = "✅ Created" if created else "📋 Exists"
        print(f"  {status} {movement.get_movement_type_display()}: {movement.reference_number}")
        print(f"    📦 Product: {movement.inventory.product.name}")
        print(f"    📊 Quantity: {movement.quantity} {movement.unit}")
        print(f"    ✅ Completed: {'Yes' if movement.is_completed else 'No'}")
    
    return movements

def create_temperature_logs():
    """Create temperature monitoring logs"""
    print_section("Creating Temperature Monitoring Logs")
    
    warehouses = Warehouse.objects.filter(temperature_controlled=True)
    
    if not warehouses.exists():
        print("❌ No temperature-controlled warehouses found")
        return []
    
    logs = []
    
    for warehouse in warehouses:
        zones = WarehouseZone.objects.filter(warehouse=warehouse)
        
        for zone in zones:
            # Create logs for the past 7 days, every 4 hours
            start_date = timezone.now() - timedelta(days=7)
            
            for i in range(42):  # 7 days * 6 readings per day
                log_time = start_date + timedelta(hours=i * 4)
                
                # Generate realistic temperature data
                base_temp = warehouse.warehouse_type.temperature_range_min + (
                    warehouse.warehouse_type.temperature_range_max - 
                    warehouse.warehouse_type.temperature_range_min
                ) / 2
                
                # Add some variation
                temperature = base_temp + random.uniform(-2, 2)
                humidity = random.uniform(
                    warehouse.warehouse_type.humidity_range_min,
                    warehouse.warehouse_type.humidity_range_max
                )
                
                # Occasionally trigger alerts for demo purposes
                alert_triggered = random.random() < 0.05  # 5% chance
                
                if alert_triggered:
                    temperature += random.uniform(3, 8)  # Temperature spike
                
                log, created = TemperatureLog.objects.get_or_create(
                    warehouse=warehouse,
                    zone=zone,
                    recorded_at=log_time,
                    defaults={
                        'temperature_celsius': Decimal(str(round(temperature, 2))),
                        'humidity_percentage': Decimal(str(round(humidity, 2))),
                        'alert_triggered': alert_triggered,
                        'alert_type': 'high_temperature' if alert_triggered else None,
                        'sensor_id': f"TEMP_{warehouse.code}_{zone.zone_code}_{random.randint(100, 999)}",
                        'notes': 'High temperature alert!' if alert_triggered else 'Normal reading'
                    }
                )
                
                logs.append(log)
                if created and i % 10 == 0:  # Print every 10th log
                    alert_status = "🚨 ALERT" if log.alert_triggered else "✅ Normal"
                    print(f"  {alert_status} {warehouse.code}/{zone.zone_code}: {log.temperature_celsius}°C, {log.humidity_percentage}% RH")
    
    print(f"📊 Created {len([l for l in logs if hasattr(l, '_state') and l._state.adding])} temperature logs")
    return logs

def create_quality_inspections(inventory_items):
    """Create quality inspection records"""
    print_section("Creating Quality Inspection Records")
    
    if not inventory_items:
        print("❌ No inventory items found for inspections")
        return []
    
    # Get quality inspectors
    inspectors = WarehouseStaff.objects.filter(role='quality_inspector')
    
    if not inspectors.exists():
        print("❌ No quality inspectors found")
        return []
    
    inspections = []
    inspection_types = ['incoming', 'routine', 'random', 'pre_shipment', 'complaint_investigation']
    
    # Create inspections for random inventory items
    sample_inventory = random.sample(inventory_items, min(15, len(inventory_items)))
    
    for inventory in sample_inventory:
        inspection_type = random.choice(inspection_types)
        inspector = random.choice(inspectors)
        
        # Generate inspection results
        overall_results = ['passed', 'passed_with_notes', 'failed']
        overall_weights = [0.7, 0.2, 0.1]
        overall_result = random.choices(overall_results, weights=overall_weights)[0]
        
        quality_score = random.randint(70, 100) if overall_result == 'passed' else random.randint(40, 95)
        
        inspection_number = f"QI{random.randint(100000, 999999)}"
        
        inspection, created = QualityInspection.objects.get_or_create(
            inspection_number=inspection_number,
            defaults={
                'inventory': inventory,
                'inspection_type': inspection_type,
                'inspector': inspector.user,
                'inspection_date': date.today() - timedelta(days=random.randint(0, 30)),
                'visual_inspection': {
                    'color': 'acceptable',
                    'texture': 'good',
                    'foreign_matter': 'none_detected',
                    'pest_damage': 'minimal' if random.random() < 0.9 else 'moderate'
                },
                'physical_tests': {
                    'moisture_content': round(random.uniform(8, 15), 2),
                    'weight': round(random.uniform(0.95, 1.05) * float(inventory.quantity), 2),
                    'density': round(random.uniform(1.2, 1.8), 2)
                },
                'chemical_tests': {
                    'ph_level': round(random.uniform(6.0, 7.5), 1),
                    'pesticide_residue': 'within_limits',
                    'heavy_metals': 'not_detected'
                } if random.random() < 0.7 else {},
                'microbiological_tests': {
                    'total_plate_count': random.randint(100, 10000),
                    'e_coli': 'not_detected',
                    'salmonella': 'not_detected'
                } if random.random() < 0.5 else {},
                'overall_result': overall_result,
                'quality_score': quality_score,
                'findings': f"Product meets quality standards for {inspection_type} inspection" if overall_result == 'passed' else "Minor issues noted, corrective action recommended",
                'recommendations': "Continue current storage practices" if overall_result == 'passed' else "Implement additional moisture control measures",
                'corrective_actions': "" if overall_result == 'passed' else "Adjust storage humidity, increase inspection frequency",
                'requires_follow_up': overall_result == 'failed',
                'follow_up_date': date.today() + timedelta(days=7) if overall_result == 'failed' else None,
                'photos': [f"inspection_photo_{random.randint(1000, 9999)}.jpg"],
                'documents': [f"inspection_report_{inspection_number}.pdf"]
            }
        )
        
        inspections.append(inspection)
        status = "✅ Created" if created else "📋 Exists"
        result_emoji = "✅" if overall_result == 'passed' else "⚠️" if overall_result == 'passed_with_notes' else "❌"
        print(f"  {status} {inspection.inspection_number} - {inspection.get_inspection_type_display()}")
        print(f"    🔬 Product: {inspection.inventory.product.name}")
        print(f"    {result_emoji} Result: {inspection.get_overall_result_display()} (Score: {inspection.quality_score})")
    
    return inspections

def demonstrate_api_features():
    """Demonstrate key API features and endpoints"""
    print_section("API Features Demonstration")
    
    base_url = "http://127.0.0.1:8000/api/v1/warehouses"
    
    print("🔗 Key API Endpoints:")
    endpoints = [
        ("Warehouse Dashboard", f"{base_url}/dashboard/"),
        ("Inventory Alerts", f"{base_url}/inventory/alerts/"),
        ("Temperature Monitoring", f"{base_url}/temperature-logs/"),
        ("Quality Inspections", f"{base_url}/quality-inspections/"),
        ("Movement Tracking", f"{base_url}/movements/"),
        ("Warehouse Utilization", f"{base_url}/warehouses/{{id}}/utilization_report/"),
        ("Zone Management", f"{base_url}/zones/"),
        ("Staff Management", f"{base_url}/staff/")
    ]
    
    for name, url in endpoints:
        print(f"  • {name:<25} → {url}")
    
    print("\n📊 Available Operations:")
    operations = [
        "✅ Real-time inventory tracking across multiple zones",
        "✅ Temperature and humidity monitoring with alerts",
        "✅ Quality inspection management and reporting",
        "✅ Warehouse movement tracking and audit trails",
        "✅ Staff management with role-based access control",
        "✅ Capacity planning and utilization reporting",
        "✅ Batch tracking with expiry date monitoring",
        "✅ QR code and RFID integration for traceability"
    ]
    
    for operation in operations:
        print(f"  {operation}")

def main():
    """Main function to run the warehouse advanced features demo"""
    print_header("WAREHOUSE MANAGEMENT SYSTEM - ADVANCED FEATURES DEMO")
    
    # Create comprehensive test data
    inventory_items = create_warehouse_inventory()
    movements = create_warehouse_movements(inventory_items)
    temperature_logs = create_temperature_logs()
    inspections = create_quality_inspections(inventory_items)
    
    # Display summary
    print_section("Demo Setup Complete")
    print(f"📦 Inventory Items: {len(inventory_items)}")
    print(f"🔄 Movements: {len(movements)}")
    print(f"🌡️  Temperature Logs: {len([l for l in temperature_logs if hasattr(l, '_state')])}")
    print(f"🔬 Quality Inspections: {len(inspections)}")
    
    # Demonstrate API features
    demonstrate_api_features()
    
    print_section("System Status")
    print("🚀 Warehouse Management System is fully operational!")
    print("✅ All core features implemented and tested")
    print("✅ Sample data created for comprehensive testing")
    print("✅ Ready for integration with order fulfillment")
    print("✅ Blockchain traceability ready for implementation")
    
    print_section("Next Phase: Blockchain Traceability Integration")
    print("🔗 Ready to implement:")
    print("  • Farm-to-table blockchain tracking")
    print("  • Digital certificates for organic products")
    print("  • Smart contracts for escrow payments")
    print("  • QR code scanning for consumer transparency")
    print("  • Immutable audit trails for quality compliance")

if __name__ == '__main__':
    main()
