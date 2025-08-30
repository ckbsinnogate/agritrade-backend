"""
AgriConnect Warehouse Management Models
Complete multi-zone warehouse system for agricultural products

Features:
- Multi-zone warehouse architecture (cold storage, dry storage, organic zones)
- Real-time inventory tracking across zones
- Temperature and humidity monitoring
- Staff management with role-based access
- Quality control zones and inspection tracking
- RFID/QR code integration for traceability
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

User = get_user_model()


class WarehouseType(models.Model):
    """Different types of agricultural warehouses"""
    
    TYPE_CHOICES = [
        ('cold_storage', 'Cold Storage'),
        ('dry_storage', 'Dry Storage'),
        ('processing', 'Processing Facility'),
        ('multi_purpose', 'Multi-Purpose'),
        ('organic_only', 'Organic Only'),
        ('conventional', 'Conventional'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    warehouse_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Environmental specifications
    temperature_range_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Minimum temperature in Celsius")
    temperature_range_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Maximum temperature in Celsius")
    humidity_range_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Minimum humidity percentage")
    humidity_range_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Maximum humidity percentage")
    
    # Special requirements
    special_requirements = models.JSONField(default=dict, blank=True, help_text="Additional requirements (organic certification, etc.)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warehouse_types'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Warehouse(models.Model):
    """Main warehouse model"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('construction', 'Under Construction'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, help_text="Warehouse identification code")
    name = models.CharField(max_length=200)
    warehouse_type = models.ForeignKey(WarehouseType, on_delete=models.CASCADE, related_name='warehouses')
    
    # Location Information
    country = models.CharField(max_length=100, default='Ghana')
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.JSONField(help_text="Complete address information")
    gps_coordinates = models.CharField(max_length=50, blank=True, help_text="GPS coordinates (lat,lng)")
    
    # Capacity and Specifications
    capacity_cubic_meters = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total storage capacity")
    current_utilization_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))])
    
    # Environmental Controls
    temperature_controlled = models.BooleanField(default=False)
    humidity_controlled = models.BooleanField(default=False)
    organic_certified = models.BooleanField(default=False)
    has_loading_dock = models.BooleanField(default=True)
    
    # Management
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_warehouses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Contact Information
    contact_info = models.JSONField(default=dict, blank=True)
    
    # Operational Information
    operating_hours = models.JSONField(default=dict, blank=True, help_text="Weekly operating schedule")
    security_features = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'warehouses'
        ordering = ['name']
        indexes = [
            models.Index(fields=['country', 'region']),
            models.Index(fields=['status']),
            models.Index(fields=['organic_certified']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_utilization_percentage(self):
        """Calculate current utilization percentage"""
        return float(self.current_utilization_percent)
    
    def is_organic_certified(self):
        """Check if warehouse is organic certified"""
        return self.organic_certified


class WarehouseZone(models.Model):
    """Zones within warehouses for different product types"""
    
    ZONE_TYPE_CHOICES = [
        ('cold_storage', 'Cold Storage'),
        ('dry_storage', 'Dry Storage'),
        ('organic', 'Organic Only'),
        ('processing', 'Processing Area'),
        ('loading', 'Loading/Unloading'),
        ('quality_control', 'Quality Control'),
        ('quarantine', 'Quarantine'),
        ('packaging', 'Packaging'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='zones')
    zone_code = models.CharField(max_length=10, help_text="Zone identifier within warehouse")
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    
    # Capacity
    capacity_cubic_meters = models.DecimalField(max_digits=8, decimal_places=2)
    current_stock_level = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Environmental Controls
    temperature_range = models.JSONField(default=dict, blank=True, help_text="Min/max temperature settings")
    humidity_range = models.JSONField(default=dict, blank=True, help_text="Min/max humidity settings")
    special_conditions = models.JSONField(default=dict, blank=True, help_text="Special storage conditions")
    
    # Status
    is_active = models.BooleanField(default=True)
    requires_certification = models.BooleanField(default=False, help_text="Zone requires special certifications")
    access_restrictions = models.JSONField(default=list, blank=True, help_text="Access control requirements")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warehouse_zones'
        unique_together = ['warehouse', 'zone_code']
        ordering = ['warehouse', 'zone_code']
    
    def __str__(self):
        return f"{self.warehouse.code}-{self.zone_code}: {self.name}"
    
    def get_occupancy_percentage(self):
        """Calculate zone occupancy percentage"""
        if self.capacity_cubic_meters > 0:
            return (float(self.current_stock_level) / float(self.capacity_cubic_meters)) * 100
        return 0


class WarehouseStaff(models.Model):
    """Staff members working in warehouses"""
    
    ROLE_CHOICES = [
        ('manager', 'Warehouse Manager'),
        ('supervisor', 'Zone Supervisor'),
        ('worker', 'Warehouse Worker'),
        ('security', 'Security Personnel'),
        ('quality_inspector', 'Quality Inspector'),
        ('forklift_operator', 'Forklift Operator'),
        ('admin', 'Administrative Staff'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='staff')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warehouse_positions')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Access Control
    access_zones = models.JSONField(default=list, blank=True, help_text="List of zone IDs this staff can access")
    permissions = models.JSONField(default=dict, blank=True, help_text="Specific permissions within warehouse")
    
    # Employment Information
    is_active = models.BooleanField(default=True)
    hired_date = models.DateField()
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    # Performance
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('1')), MaxValueValidator(Decimal('5'))])
    certifications = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'warehouse_staff'
        unique_together = ['warehouse', 'user']
        ordering = ['warehouse', 'role', 'hired_date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} at {self.warehouse.name}"


class WarehouseInventory(models.Model):
    """Product inventory within warehouse zones"""
    
    QUALITY_STATUS_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('expired', 'Expired'),
        ('quarantine', 'Under Quarantine'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='warehouse_inventory')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory')
    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, related_name='inventory')
    
    # Quantity and Batch Information    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    reserved_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    available_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    
    batch_number = models.CharField(max_length=100, blank=True)
    lot_number = models.CharField(max_length=100, blank=True)
    
    # Dates
    manufacturing_date = models.DateField(null=True, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(auto_now_add=True)
    
    # Quality and Condition
    quality_status = models.CharField(max_length=20, choices=QUALITY_STATUS_CHOICES, default='good')
    storage_conditions = models.JSONField(default=dict, blank=True)
    
    # Inspection Information
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspected_inventory')
    inspection_notes = models.TextField(blank=True)
    
    # Location within zone
    location_details = models.JSONField(default=dict, blank=True, help_text="Specific location within zone (aisle, shelf, etc.)")
    
    # Tracking
    qr_code = models.CharField(max_length=100, blank=True, unique=True)
    rfid_tag = models.CharField(max_length=100, blank=True)
      # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'warehouse_inventory'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['batch_number']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['quality_status']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.code}/{self.zone.zone_code} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Calculate available quantity
        self.available_quantity = self.quantity - self.reserved_quantity
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if inventory item is expired"""
        if self.expiry_date:
            try:
                from django.utils import timezone
                return timezone.now().date() > self.expiry_date
            except (AttributeError, TypeError, ValueError):
                return False
        return False
    
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            try:
                from django.utils import timezone
                delta = self.expiry_date - timezone.now().date()
                return delta.days
            except (AttributeError, TypeError, ValueError):
                return None
        return None


class WarehouseMovement(models.Model):
    """Track all inventory movements within and between warehouses"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('inbound', 'Inbound Receipt'),
        ('outbound', 'Outbound Shipment'),
        ('transfer', 'Internal Transfer'),
        ('adjustment', 'Inventory Adjustment'),
        ('loss', 'Inventory Loss'),
        ('return', 'Product Return'),
        ('quarantine', 'Move to Quarantine'),
        ('release', 'Release from Quarantine'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    reference_number = models.CharField(max_length=100, unique=True)
    
    # Product and Location
    inventory = models.ForeignKey(WarehouseInventory, on_delete=models.CASCADE, related_name='movements')
    from_zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, null=True, blank=True, related_name='outbound_movements')
    to_zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, null=True, blank=True, related_name='inbound_movements')
    
    # Quantity Information
    quantity = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal('0'))])
    unit = models.CharField(max_length=20)
    
    # Personnel and Authorization
    authorized_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authorized_movements')
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performed_movements')
    
    # Related Documents
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='warehouse_movements')
    
    # Additional Information
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    conditions_at_movement = models.JSONField(default=dict, blank=True, help_text="Temperature, humidity, etc. at time of movement")
    
    # Status
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'warehouse_movements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['movement_type', 'created_at']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.get_movement_type_display()}"


class TemperatureLog(models.Model):
    """Temperature monitoring logs for warehouses and zones"""
    
    # Location
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='temperature_logs')
    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, null=True, blank=True, related_name='temperature_logs')
    
    # Environmental Data
    temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temperature in Celsius")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Humidity percentage")
    
    # Sensor Information
    sensor_id = models.CharField(max_length=100, blank=True)
    sensor_location = models.CharField(max_length=200, blank=True)
    
    # Alert Information
    is_within_range = models.BooleanField(default=True)
    alert_triggered = models.BooleanField(default=False)
    alert_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    
    # Additional Measurements
    additional_data = models.JSONField(default=dict, blank=True, help_text="Additional sensor data")
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'temperature_logs'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['warehouse', 'recorded_at']),
            models.Index(fields=['zone', 'recorded_at']),
            models.Index(fields=['alert_triggered']),
        ]
    
    def __str__(self):
        location = f"{self.warehouse.code}"
        if self.zone:
            location += f"/{self.zone.zone_code}"
        return f"{location} - {self.temperature}°C at {self.recorded_at}"


class QualityInspection(models.Model):
    """Quality inspection records for warehouse inventory"""
    
    INSPECTION_TYPE_CHOICES = [
        ('routine', 'Routine Inspection'),
        ('incoming', 'Incoming Goods Inspection'),
        ('complaint', 'Complaint Investigation'),
        ('pre_shipment', 'Pre-Shipment Inspection'),
        ('compliance', 'Compliance Audit'),
        ('damage', 'Damage Assessment'),
    ]
    
    RESULT_CHOICES = [
        ('pass', 'Pass'),
        ('pass_conditional', 'Pass with Conditions'),
        ('fail', 'Fail'),
        ('quarantine', 'Quarantine Required'),
        ('retest', 'Retest Required'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection_number = models.CharField(max_length=100, unique=True)
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPE_CHOICES)
    
    # Subject of Inspection
    inventory = models.ForeignKey(WarehouseInventory, on_delete=models.CASCADE, related_name='quality_inspections')
    
    # Inspection Details
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_inspections')
    inspection_date = models.DateTimeField()
    
    # Quality Parameters
    visual_inspection = models.JSONField(default=dict, blank=True, help_text="Visual inspection results")
    physical_tests = models.JSONField(default=dict, blank=True, help_text="Physical test results")
    chemical_tests = models.JSONField(default=dict, blank=True, help_text="Chemical test results")
    microbiological_tests = models.JSONField(default=dict, blank=True, help_text="Microbiological test results")
    
    # Overall Assessment
    overall_result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    quality_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))])
    
    # Documentation
    findings = models.TextField()
    recommendations = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    
    # Follow-up
    requires_follow_up = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    
    # Attachments
    photos = models.JSONField(default=list, blank=True, help_text="Photo URLs")
    documents = models.JSONField(default=list, blank=True, help_text="Document URLs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quality_inspections'
        ordering = ['-inspection_date']
        indexes = [
            models.Index(fields=['inspection_type', 'inspection_date']),
            models.Index(fields=['overall_result']),
        ]
    
    def __str__(self):
        return f"{self.inspection_number} - {self.inventory} ({self.get_overall_result_display()})"
