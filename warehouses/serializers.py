"""
AgriConnect Warehouse Management Serializers
RESTful API serializers for warehouse operations
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, WarehouseMovement, TemperatureLog, QualityInspection
)

User = get_user_model()


class WarehouseTypeSerializer(serializers.ModelSerializer):
    """Serializer for warehouse types"""
    
    class Meta:
        model = WarehouseType
        fields = '__all__'
        read_only_fields = ['created_at']


class WarehouseZoneSerializer(serializers.ModelSerializer):
    """Serializer for warehouse zones"""
    occupancy_percentage = serializers.ReadOnlyField(source='get_occupancy_percentage')
    
    class Meta:
        model = WarehouseZone
        fields = '__all__'
        read_only_fields = ['created_at']


class WarehouseStaffSerializer(serializers.ModelSerializer):
    """Serializer for warehouse staff"""
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    role_display = serializers.ReadOnlyField(source='get_role_display')
    
    class Meta:
        model = WarehouseStaff
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class WarehouseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for warehouse listings"""
    warehouse_type_name = serializers.ReadOnlyField(source='warehouse_type.name')
    manager_name = serializers.ReadOnlyField(source='manager.get_full_name')
    utilization_percentage = serializers.ReadOnlyField(source='get_utilization_percentage')
    zones_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name', 'warehouse_type_name', 'country', 'region', 'city',
            'status', 'utilization_percentage', 'organic_certified', 'manager_name',
            'zones_count', 'created_at'
        ]
    
    def get_zones_count(self, obj):
        return obj.zones.count()


class WarehouseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual warehouse"""
    warehouse_type = WarehouseTypeSerializer(read_only=True)
    zones = WarehouseZoneSerializer(many=True, read_only=True)
    staff = WarehouseStaffSerializer(many=True, read_only=True)
    manager_name = serializers.ReadOnlyField(source='manager.get_full_name')
    utilization_percentage = serializers.ReadOnlyField(source='get_utilization_percentage')
    
    # Statistics
    total_inventory_items = serializers.SerializerMethodField()
    total_inventory_value = serializers.SerializerMethodField()
    active_zones_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_inventory_items(self, obj):
        return obj.inventory.count()
    
    def get_total_inventory_value(self, obj):
        total = 0
        for item in obj.inventory.all():
            total += float(item.quantity) * float(item.product.price_per_unit)
        return total
    
    def get_active_zones_count(self, obj):
        return obj.zones.filter(is_active=True).count()
    
    def get_staff_count(self, obj):
        return obj.staff.filter(is_active=True).count()


class WarehouseInventorySerializer(serializers.ModelSerializer):
    """Serializer for warehouse inventory"""
    product_name = serializers.ReadOnlyField(source='product.name')
    product_category = serializers.ReadOnlyField(source='product.category.name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    zone_name = serializers.ReadOnlyField(source='zone.name')
    zone_type = serializers.ReadOnlyField(source='zone.zone_type')
    quality_status_display = serializers.ReadOnlyField(source='get_quality_status_display')
    
    # Calculated fields
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    # Safe date fields to handle null values properly
    manufacturing_date = serializers.DateField(allow_null=True, required=False)
    harvest_date = serializers.DateField(allow_null=True, required=False)
    expiry_date = serializers.DateField(allow_null=True, required=False)
    
    class Meta:
        model = WarehouseInventory
        fields = '__all__'
        read_only_fields = ['available_quantity', 'created_at', 'updated_at']
    
    def get_total_value(self, obj):
        try:
            return float(obj.quantity) * float(obj.product.price_per_unit)
        except (ValueError, AttributeError):
            return 0.0
    
    def get_days_until_expiry(self, obj):
        """Safely calculate days until expiry"""
        try:
            return obj.days_until_expiry()
        except (AttributeError, TypeError):
            return None
    
    def to_representation(self, instance):
        """Override to ensure safe date handling"""
        data = super().to_representation(instance)
        
        # Ensure date fields are properly formatted or null
        date_fields = ['manufacturing_date', 'harvest_date', 'expiry_date']
        for field in date_fields:
            if field in data and data[field] == '':
                data[field] = None
                
        return data


class WarehouseMovementSerializer(serializers.ModelSerializer):
    """Serializer for warehouse movements"""
    inventory_product = serializers.ReadOnlyField(source='inventory.product.name')
    authorized_by_name = serializers.ReadOnlyField(source='authorized_by.get_full_name')
    performed_by_name = serializers.ReadOnlyField(source='performed_by.get_full_name')
    movement_type_display = serializers.ReadOnlyField(source='get_movement_type_display')
    
    from_zone_name = serializers.ReadOnlyField(source='from_zone.name')
    to_zone_name = serializers.ReadOnlyField(source='to_zone.name')
    
    class Meta:
        model = WarehouseMovement
        fields = '__all__'
        read_only_fields = ['created_at']


class TemperatureLogSerializer(serializers.ModelSerializer):
    """Serializer for temperature logs"""
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    zone_name = serializers.ReadOnlyField(source='zone.name')
    acknowledged_by_name = serializers.ReadOnlyField(source='acknowledged_by.get_full_name')
    
    class Meta:
        model = TemperatureLog
        fields = '__all__'
        read_only_fields = ['recorded_at']


class QualityInspectionSerializer(serializers.ModelSerializer):
    """Serializer for quality inspections"""
    inventory_product = serializers.ReadOnlyField(source='inventory.product.name')
    inspector_name = serializers.ReadOnlyField(source='inspector.get_full_name')
    inspection_type_display = serializers.ReadOnlyField(source='get_inspection_type_display')
    overall_result_display = serializers.ReadOnlyField(source='get_overall_result_display')
    
    class Meta:
        model = QualityInspection
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# Specialized serializers for specific use cases

class WarehouseStatsSerializer(serializers.Serializer):
    """Serializer for warehouse statistics"""
    total_warehouses = serializers.IntegerField()
    active_warehouses = serializers.IntegerField()
    total_zones = serializers.IntegerField()
    total_inventory_items = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_utilization = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # By type
    warehouses_by_type = serializers.DictField()
    zones_by_type = serializers.DictField()
    
    # Quality metrics
    inventory_by_quality = serializers.DictField()
    recent_movements = serializers.IntegerField()
    pending_inspections = serializers.IntegerField()


class InventoryAlertSerializer(serializers.Serializer):
    """Serializer for inventory alerts"""
    low_stock_items = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    expired_items = serializers.IntegerField()
    quarantine_items = serializers.IntegerField()
    
    # Alert details
    low_stock_details = WarehouseInventorySerializer(many=True, read_only=True)
    expiring_details = WarehouseInventorySerializer(many=True, read_only=True)
    expired_details = WarehouseInventorySerializer(many=True, read_only=True)


class ZoneUtilizationSerializer(serializers.Serializer):
    """Serializer for zone utilization data"""
    zone_id = serializers.UUIDField()
    zone_name = serializers.CharField()
    zone_type = serializers.CharField()
    warehouse_name = serializers.CharField()
    capacity = serializers.DecimalField(max_digits=8, decimal_places=2)
    current_stock = serializers.DecimalField(max_digits=8, decimal_places=2)
    utilization_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    status = serializers.CharField()


class MovementReportSerializer(serializers.Serializer):
    """Serializer for movement reports"""
    period = serializers.CharField()
    total_movements = serializers.IntegerField()
    inbound_movements = serializers.IntegerField()
    outbound_movements = serializers.IntegerField()
    internal_transfers = serializers.IntegerField()
    
    # Movement details
    movements_by_type = serializers.DictField()
    movements_by_warehouse = serializers.DictField()
    top_moved_products = serializers.ListField()


class WarehouseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new warehouses"""
    
    class Meta:
        model = Warehouse
        fields = [
            'code', 'name', 'warehouse_type', 'country', 'region', 'city',
            'address', 'gps_coordinates', 'capacity_cubic_meters',
            'temperature_controlled', 'humidity_controlled', 'organic_certified',
            'has_loading_dock', 'manager', 'contact_info', 'operating_hours'
        ]
    
    def validate_code(self, value):
        """Validate warehouse code is unique"""
        if Warehouse.objects.filter(code=value).exists():
            raise serializers.ValidationError("Warehouse code must be unique")
        return value


class InventoryMovementCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating inventory movements"""
    
    class Meta:
        model = WarehouseMovement
        fields = [
            'movement_type', 'inventory', 'from_zone', 'to_zone',
            'quantity', 'unit', 'authorized_by', 'performed_by',
            'order', 'reason', 'notes', 'conditions_at_movement'
        ]
    
    def validate(self, data):
        """Validate movement data"""
        # Check if there's enough inventory for outbound movements
        if data['movement_type'] in ['outbound', 'transfer'] and data.get('inventory'):
            available = data['inventory'].available_quantity
            if data['quantity'] > available:
                raise serializers.ValidationError(
                    f"Not enough inventory available. Available: {available}, Requested: {data['quantity']}"
                )
        
        return data
