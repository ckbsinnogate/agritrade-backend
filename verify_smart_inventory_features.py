#!/usr/bin/env python3
"""
AgriConnect Smart Inventory Features Verification
This script verifies that all PRD Section 4.1.2 Smart Inventory Features requirements are implemented
"""

import os
import sys
import django

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

django.setup()

from warehouses.models import (
    WarehouseInventory, WarehouseZone, WarehouseStaff, Warehouse,
    WarehouseMovement, TemperatureLog, QualityInspection
)
from products.models import Product, TraceabilityRecord
from authentication.models import UserRole
from users.models import User

def print_section(title, color="36"):  # Cyan
    print(f"\n\033[{color}m{'='*80}\033[0m")
    print(f"\033[{color}m{title.center(80)}\033[0m")
    print(f"\033[{color}m{'='*80}\033[0m")

def print_requirement(req_num, title, status="", color="32"):
    status_icon = "✅" if status == "IMPLEMENTED" else "❌" if status == "MISSING" else "🔍"
    print(f"\n\033[{color}m{req_num}. {title} {status_icon}\033[0m")

def verify_realtime_tracking():
    """Verify Real-time Tracking: RFID/QR code-based inventory monitoring"""
    print_requirement("4.1.2.1", "Real-time Tracking: RFID/QR code-based inventory monitoring")
    
    # Check for RFID/QR tracking fields in inventory
    inventory_items = WarehouseInventory.objects.all()
    print(f"   📊 Total Inventory Items: {inventory_items.count()}")
    
    # Check for tracking codes
    rfid_items = inventory_items.exclude(rfid_tag='').exclude(rfid_tag__isnull=True)
    qr_items = inventory_items.exclude(qr_code='').exclude(qr_code__isnull=True)
    
    print(f"   📡 RFID Tagged Items: {rfid_items.count()}")
    print(f"   📱 QR Code Items: {qr_items.count()}")
    
    # Check for real-time tracking capabilities
    tracking_fields = []
    if hasattr(WarehouseInventory, 'rfid_tag'):
        tracking_fields.append('RFID')
    if hasattr(WarehouseInventory, 'qr_code'):
        tracking_fields.append('QR Code')
    if hasattr(WarehouseInventory, 'last_scanned'):
        tracking_fields.append('Last Scanned')
    if hasattr(WarehouseInventory, 'location_history'):
        tracking_fields.append('Location History')
    
    print(f"   🔍 Tracking Fields Available: {', '.join(tracking_fields) if tracking_fields else 'None'}")
    
    # Display sample tracking data
    if rfid_items.exists() or qr_items.exists():
        print("   📋 Sample Tracking Data:")
        for item in inventory_items[:3]:
            rfid = getattr(item, 'rfid_tag', 'N/A') or 'N/A'
            qr = getattr(item, 'qr_code', 'N/A') or 'N/A'
            print(f"      • {item.product.name}: RFID={rfid}, QR={qr}")
    
    is_implemented = len(tracking_fields) >= 2 and (rfid_items.exists() or qr_items.exists())
    return is_implemented

def verify_automated_alerts():
    """Verify Automated Alerts: Low stock, expiry date, and quality warnings"""
    print_requirement("4.1.2.2", "Automated Alerts: Low stock, expiry date, and quality warnings")
    
    # Check for alert-related fields
    alert_fields = []
    if hasattr(WarehouseInventory, 'low_stock_threshold'):
        alert_fields.append('Low Stock Threshold')
    if hasattr(WarehouseInventory, 'expiry_date'):
        alert_fields.append('Expiry Date')
    if hasattr(WarehouseInventory, 'expiry_alert_days'):
        alert_fields.append('Expiry Alert Days')
    if hasattr(WarehouseInventory, 'quality_status'):
        alert_fields.append('Quality Status')
    
    print(f"   🚨 Alert Fields Available: {', '.join(alert_fields) if alert_fields else 'None'}")
    
    # Check for items with alert thresholds
    inventory_items = WarehouseInventory.objects.all()
    
    # Low stock alerts
    try:
        low_stock_items = inventory_items.filter(quantity__lte=10)  # Assuming threshold logic
        print(f"   📉 Items Below Stock Threshold: {low_stock_items.count()}")
    except:
        print(f"   📉 Low Stock Tracking: Field not available")
    
    # Expiry alerts
    try:
        from django.utils import timezone
        from datetime import timedelta
        soon_expiry = inventory_items.filter(
            expiry_date__lte=timezone.now() + timedelta(days=7)
        ).exclude(expiry_date__isnull=True)
        print(f"   ⏰ Items Expiring Soon: {soon_expiry.count()}")
    except:
        print(f"   ⏰ Expiry Tracking: Field not available")
    
    # Quality alerts
    try:
        quality_issues = inventory_items.exclude(quality_status='good')
        print(f"   ⚠️ Items with Quality Issues: {quality_issues.count()}")
    except:
        print(f"   ⚠️ Quality Tracking: Field not available")
    
    is_implemented = len(alert_fields) >= 3
    return is_implemented

def verify_batch_management():
    """Verify Batch Management: Complete traceability from farm to consumer"""
    print_requirement("4.1.2.3", "Batch Management: Complete traceability from farm to consumer")
    
    # Check for batch tracking in warehouse inventory
    inventory_with_batches = WarehouseInventory.objects.exclude(batch_number='').count()
    inventory_with_lots = WarehouseInventory.objects.exclude(lot_number='').count()
    total_inventory = WarehouseInventory.objects.count()
    
    print(f"   📦 Items with Batch Numbers: {inventory_with_batches}")
    print(f"   🏷️  Items with Lot Numbers: {inventory_with_lots}")
    print(f"   📊 Total Inventory Items: {total_inventory}")
    
    # Check for traceability records
    traceability_records = TraceabilityRecord.objects.count()
    blockchain_verified = TraceabilityRecord.objects.filter(blockchain_verified=True).count()
    print(f"   🔗 Traceability Records: {traceability_records}")
    print(f"   ⛓️  Blockchain Verified: {blockchain_verified}")
    
    # Check traceability stages coverage
    if traceability_records > 0:
        stages = TraceabilityRecord.objects.values_list('stage', flat=True).distinct()
        print(f"   📋 Traceability Stages: {list(stages)}")
    
    # Sample batch data
    sample_batches = WarehouseInventory.objects.exclude(batch_number='')[:3]    if sample_batches:
        print("   📋 Sample Batch Data:")
        for item in sample_batches:
            batch_info = f"Batch: {item.batch_number}"
            if item.lot_number:
                batch_info += f", Lot: {item.lot_number}"
            if item.manufacturing_date:
                batch_info += f", Mfg: {item.manufacturing_date}"
            print(f"      • {item.product.name} - {batch_info}")
    
    is_implemented = inventory_with_batches > 0 and traceability_records > 0
    return is_implemented

def verify_temperature_monitoring():
    """Verify Temperature Monitoring: IoT sensors for cold chain compliance"""
    print_requirement("4.1.2.4", "Temperature Monitoring: IoT sensors for cold chain compliance")
    
    # Check for temperature monitoring fields
    temp_fields = []
    if hasattr(WarehouseZone, 'temperature_range'):
        temp_fields.append('Temperature Range')
    if hasattr(WarehouseZone, 'current_temperature'):
        temp_fields.append('Current Temperature')
    if hasattr(WarehouseZone, 'humidity_level'):
        temp_fields.append('Humidity Level')
    if hasattr(WarehouseInventory, 'temperature_log'):
        temp_fields.append('Temperature Log')
    
    print(f"   🌡️ Temperature Fields Available: {', '.join(temp_fields) if temp_fields else 'None'}")
    
    # Check cold storage zones
    cold_zones = WarehouseZone.objects.filter(zone_type='cold_storage')
    print(f"   ❄️ Cold Storage Zones: {cold_zones.count()}")
    
    # Check temperature monitoring
    if cold_zones.exists():
        print("   📊 Cold Storage Temperature Monitoring:")
        for zone in cold_zones[:3]:
            temp_range = getattr(zone, 'temperature_range', {})
            if temp_range:
                min_temp = temp_range.get('min', 'N/A')
                max_temp = temp_range.get('max', 'N/A')
                print(f"      • {zone.name}: {min_temp}°C to {max_temp}°C")
            else:
                print(f"      • {zone.name}: Temperature range not configured")
    
    # Check for IoT sensor integration
    sensor_features = []
    if hasattr(WarehouseZone, 'sensor_data'):
        sensor_features.append('Sensor Data')
    if hasattr(WarehouseZone, 'last_sensor_reading'):
        sensor_features.append('Last Reading')
    if hasattr(WarehouseZone, 'alert_thresholds'):
        sensor_features.append('Alert Thresholds')
    
    print(f"   📡 IoT Sensor Features: {', '.join(sensor_features) if sensor_features else 'None'}")
    
    is_implemented = cold_zones.exists() and len(temp_fields) >= 2
    return is_implemented

def verify_staff_management():
    """Verify Staff Management: Role-based access and activity tracking"""
    print_requirement("4.1.2.5", "Staff Management: Role-based access and activity tracking")
    
    # Check warehouse staff
    warehouse_staff = WarehouseStaff.objects.all()
    print(f"   👥 Total Warehouse Staff: {warehouse_staff.count()}")
    
    # Check user roles
    user_roles = UserRole.objects.all()
    print(f"   🎭 User Roles: {user_roles.count()}")
    
    # Check role types
    if user_roles.exists():
        role_types = user_roles.values_list('name', flat=True).distinct()
        print(f"   📋 Available Roles: {', '.join(role_types)}")
    
    # Check staff roles and permissions
    if warehouse_staff.exists():
        print("   👨‍💼 Staff Role Distribution:")
        for staff in warehouse_staff[:5]:
            role = getattr(staff, 'role', 'N/A') or 'N/A'
            warehouse = getattr(staff, 'warehouse', 'N/A')
            print(f"      • {staff.user.get_full_name() or staff.user.username}: {role} at {warehouse}")
    
    # Check activity tracking fields
    activity_fields = []
    if hasattr(WarehouseStaff, 'last_activity'):
        activity_fields.append('Last Activity')
    if hasattr(WarehouseStaff, 'shift_schedule'):
        activity_fields.append('Shift Schedule')
    if hasattr(WarehouseStaff, 'access_level'):
        activity_fields.append('Access Level')
    
    print(f"   📊 Activity Tracking Fields: {', '.join(activity_fields) if activity_fields else 'None'}")
    
    is_implemented = warehouse_staff.exists() and user_roles.exists() and len(activity_fields) >= 1
    return is_implemented

def verify_capacity_planning():
    """Verify Capacity Planning: AI-driven demand forecasting"""
    print_requirement("4.1.2.6", "Capacity Planning: AI-driven demand forecasting")
    
    # Check for capacity planning fields
    capacity_fields = []
    if hasattr(WarehouseZone, 'capacity_cubic_meters'):
        capacity_fields.append('Cubic Capacity')
    if hasattr(WarehouseZone, 'current_utilization'):
        capacity_fields.append('Current Utilization')
    if hasattr(WarehouseZone, 'max_capacity'):
        capacity_fields.append('Maximum Capacity')
    if hasattr(Warehouse, 'total_capacity'):
        capacity_fields.append('Total Warehouse Capacity')
    
    print(f"   📊 Capacity Fields Available: {', '.join(capacity_fields) if capacity_fields else 'None'}")
    
    # Check warehouse capacity utilization
    warehouses = Warehouse.objects.all()
    total_zones = WarehouseZone.objects.all()
    
    print(f"   🏢 Total Warehouses: {warehouses.count()}")
    print(f"   🏗️ Total Zones: {total_zones.count()}")
    
    # Check capacity utilization
    if total_zones.exists():
        print("   📈 Zone Capacity Analysis:")
        for zone in total_zones[:3]:
            capacity = getattr(zone, 'capacity_cubic_meters', 0) or 0
            if capacity > 0:
                print(f"      • {zone.name}: {capacity}m³ capacity")
            else:
                print(f"      • {zone.name}: Capacity not defined")
    
    # Check for AI/forecasting features
    ai_features = []
    try:
        # Check if there are any AI-related apps or modules
        import importlib
        if importlib.util.find_spec('ai_analytics'):
            ai_features.append('AI Analytics Module')
    except:
        pass
    
    # Check for demand forecasting data
    forecasting_fields = []
    if hasattr(WarehouseInventory, 'demand_forecast'):
        forecasting_fields.append('Demand Forecast')
    if hasattr(WarehouseInventory, 'reorder_point'):
        forecasting_fields.append('Reorder Point')
    if hasattr(WarehouseInventory, 'optimal_stock_level'):
        forecasting_fields.append('Optimal Stock Level')
    
    print(f"   🤖 AI Features: {', '.join(ai_features) if ai_features else 'None'}")
    print(f"   📈 Forecasting Fields: {', '.join(forecasting_fields) if forecasting_fields else 'None'}")
    
    is_implemented = len(capacity_fields) >= 2 and (len(forecasting_fields) >= 1 or len(ai_features) >= 1)
    return is_implemented

def main():
    """Main verification function"""
    print_section("AGRICONNECT SMART INVENTORY FEATURES VERIFICATION", "33")
    print("\033[33mPRD Section 4.1.2 Requirements Verification\033[0m")
    
    # Track implementation status
    results = {}
    
    print_section("REQUIREMENT VERIFICATION", "36")
    
    # Verify each requirement
    results["realtime_tracking"] = verify_realtime_tracking()
    results["automated_alerts"] = verify_automated_alerts()
    results["batch_management"] = verify_batch_management()
    results["temperature_monitoring"] = verify_temperature_monitoring()
    results["staff_management"] = verify_staff_management()
    results["capacity_planning"] = verify_capacity_planning()
    
    # Summary
    print_section("IMPLEMENTATION SUMMARY", "32")
    
    implemented_count = sum(1 for status in results.values() if status)
    total_count = len(results)
    
    print(f"\n📊 \033[32mImplementation Status: {implemented_count}/{total_count} Requirements Met\033[0m")
    
    requirement_names = {
        "realtime_tracking": "Real-time Tracking",
        "automated_alerts": "Automated Alerts", 
        "batch_management": "Batch Management",
        "temperature_monitoring": "Temperature Monitoring",
        "staff_management": "Staff Management",
        "capacity_planning": "Capacity Planning"
    }
    
    for requirement, status in results.items():
        status_text = "✅ IMPLEMENTED" if status else "❌ MISSING"
        color = "32" if status else "31"
        req_name = requirement_names.get(requirement, requirement.replace('_', ' ').title())
        print(f"   \033[{color}m{req_name}: {status_text}\033[0m")
    
    # Overall status
    if implemented_count == total_count:
        print(f"\n🎉 \033[32mALL SMART INVENTORY FEATURES IMPLEMENTED!\033[0m")
        print(f"\033[32m🌟 PRD Section 4.1.2 - 100% Compliant\033[0m")
    else:
        print(f"\n⚠️  \033[33m{total_count - implemented_count} FEATURES NEED ATTENTION\033[0m")
    
    # Database statistics
    print_section("DATABASE STATISTICS", "34")
    print(f"📦 Total Inventory Items: {WarehouseInventory.objects.count()}")
    print(f"🏭 Total Product Batches: {ProductBatch.objects.count()}")
    print(f"🔗 Total Traceability Records: {TraceabilityRecord.objects.count()}")
    print(f"👥 Total Warehouse Staff: {WarehouseStaff.objects.count()}")
    print(f"🎭 Total User Roles: {UserRole.objects.count()}")
    print(f"🏢 Total Warehouses: {Warehouse.objects.count()}")

if __name__ == "__main__":
    main()
