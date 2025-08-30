"""
AgriConnect Warehouse Management Admin Interface
Complete admin interface for warehouse operations
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, WarehouseMovement, TemperatureLog, QualityInspection
)


@admin.register(WarehouseType)
class WarehouseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'warehouse_type', 'temperature_range', 'humidity_range', 'created_at']
    list_filter = ['warehouse_type', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def temperature_range(self, obj):
        if obj.temperature_range_min and obj.temperature_range_max:
            return f"{obj.temperature_range_min}°C to {obj.temperature_range_max}°C"
        return "-"
    temperature_range.short_description = "Temperature Range"
    
    def humidity_range(self, obj):
        if obj.humidity_range_min and obj.humidity_range_max:
            return f"{obj.humidity_range_min}% to {obj.humidity_range_max}%"
        return "-"
    humidity_range.short_description = "Humidity Range"


class WarehouseZoneInline(admin.TabularInline):
    model = WarehouseZone
    extra = 1
    fields = ['zone_code', 'name', 'zone_type', 'capacity_cubic_meters', 'current_stock_level', 'is_active']
    readonly_fields = ['current_stock_level']


class WarehouseStaffInline(admin.TabularInline):
    model = WarehouseStaff
    extra = 1
    fields = ['user', 'role', 'hired_date', 'is_active']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'warehouse_type', 'region', 'status', 'utilization_badge', 'organic_certified', 'manager']
    list_filter = ['status', 'warehouse_type', 'organic_certified', 'country', 'region', 'temperature_controlled']
    search_fields = ['code', 'name', 'region', 'city']
    ordering = ['name']
    inlines = [WarehouseZoneInline, WarehouseStaffInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'warehouse_type', 'manager')
        }),
        ('Location', {
            'fields': ('country', 'region', 'city', 'address', 'gps_coordinates')
        }),
        ('Capacity & Specifications', {
            'fields': ('capacity_cubic_meters', 'current_utilization_percent', 'status')
        }),
        ('Features', {
            'fields': ('temperature_controlled', 'humidity_controlled', 'organic_certified', 'has_loading_dock')
        }),
        ('Operations', {
            'fields': ('operating_hours', 'security_features', 'contact_info'),
            'classes': ['collapse']
        }),
    )
    
    def utilization_badge(self, obj):
        percentage = obj.get_utilization_percentage()
        if percentage < 50:
            color = 'green'
        elif percentage < 80:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percentage
        )
    utilization_badge.short_description = "Utilization"


@admin.register(WarehouseZone)
class WarehouseZoneAdmin(admin.ModelAdmin):
    list_display = ['zone_identifier', 'warehouse', 'zone_type', 'occupancy_badge', 'is_active', 'requires_certification']
    list_filter = ['zone_type', 'is_active', 'requires_certification', 'warehouse__country']
    search_fields = ['zone_code', 'name', 'warehouse__name', 'warehouse__code']
    ordering = ['warehouse', 'zone_code']
    
    def zone_identifier(self, obj):
        return f"{obj.warehouse.code}-{obj.zone_code}"
    zone_identifier.short_description = "Zone ID"
    
    def occupancy_badge(self, obj):
        percentage = obj.get_occupancy_percentage()
        if percentage < 60:
            color = 'green'
        elif percentage < 85:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percentage
        )
    occupancy_badge.short_description = "Occupancy"


@admin.register(WarehouseStaff)
class WarehouseStaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'warehouse', 'role', 'hired_date', 'is_active', 'performance_rating']
    list_filter = ['role', 'is_active', 'warehouse', 'hired_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'warehouse__name']
    ordering = ['warehouse', 'role', 'hired_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('warehouse', 'user', 'role', 'supervisor')
        }),
        ('Employment', {
            'fields': ('hired_date', 'is_active', 'performance_rating')
        }),
        ('Access & Permissions', {
            'fields': ('access_zones', 'permissions', 'certifications'),
            'classes': ['collapse']
        }),
    )


@admin.register(WarehouseInventory)
class WarehouseInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse_zone', 'get_quantity', 'available_quantity', 'quality_status', 'expiry_status', 'batch_number']
    list_filter = ['quality_status', 'warehouse', 'zone__zone_type', 'expiry_date']
    search_fields = ['product__name', 'batch_number', 'lot_number', 'warehouse__name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Product & Location', {
            'fields': ('product', 'warehouse', 'zone')
        }),
        ('Quantities', {
            'fields': ('quantity', 'reserved_quantity', 'available_quantity')
        }),
        ('Batch Information', {
            'fields': ('batch_number', 'lot_number', 'manufacturing_date', 'harvest_date', 'expiry_date')
        }),
        ('Quality & Condition', {
            'fields': ('quality_status', 'storage_conditions', 'inspection_notes')
        }),
        ('Location & Tracking', {
            'fields': ('location_details', 'qr_code', 'rfid_tag'),
            'classes': ['collapse']
        }),    )
    
    readonly_fields = ['available_quantity']
    
    def warehouse_zone(self, obj):
        return f"{obj.warehouse.code}/{obj.zone.zone_code}"
    warehouse_zone.short_description = "Location"
    
    def get_quantity(self, obj):
        return obj.quantity
    get_quantity.short_description = "Quantity"
    
    def expiry_status(self, obj):
        if obj.expiry_date:
            days = obj.days_until_expiry()
            if days is None:
                return "-"
            elif days < 0:
                return format_html('<span style="color: red; font-weight: bold;">EXPIRED</span>')
            elif days <= 7:
                return format_html('<span style="color: orange; font-weight: bold;">{} days</span>', days)
            elif days <= 30:
                return format_html('<span style="color: blue;">{} days</span>', days)
            else:
                return format_html('<span style="color: green;">{} days</span>', days)
        return "-"
    expiry_status.short_description = "Expires In"


@admin.register(WarehouseMovement)
class WarehouseMovementAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'movement_type', 'inventory_product', 'quantity', 'from_to_zones', 'authorized_by', 'is_completed', 'created_at']
    list_filter = ['movement_type', 'is_completed', 'created_at', 'inventory__warehouse']
    search_fields = ['reference_number', 'inventory__product__name', 'authorized_by__first_name', 'authorized_by__last_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('movement_type', 'reference_number', 'inventory')
        }),
        ('Locations', {
            'fields': ('from_zone', 'to_zone')
        }),
        ('Quantity & Unit', {
            'fields': ('quantity', 'unit')
        }),
        ('Authorization', {
            'fields': ('authorized_by', 'performed_by')
        }),
        ('Additional Information', {
            'fields': ('reason', 'notes', 'conditions_at_movement', 'order'),
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ('is_completed', 'completed_at')
        }),
    )
    
    def inventory_product(self, obj):
        return obj.inventory.product.name
    inventory_product.short_description = "Product"
    
    def from_to_zones(self, obj):
        from_zone = f"{obj.from_zone.warehouse.code}/{obj.from_zone.zone_code}" if obj.from_zone else "External"
        to_zone = f"{obj.to_zone.warehouse.code}/{obj.to_zone.zone_code}" if obj.to_zone else "External"
        return f"{from_zone} → {to_zone}"
    from_to_zones.short_description = "Route"


@admin.register(TemperatureLog)
class TemperatureLogAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'zone', 'temperature', 'humidity', 'is_within_range', 'alert_status', 'recorded_at']
    list_filter = ['warehouse', 'is_within_range', 'alert_triggered', 'recorded_at']
    search_fields = ['warehouse__name', 'zone__name', 'sensor_id']
    ordering = ['-recorded_at']
    date_hierarchy = 'recorded_at'
    
    fieldsets = (
        ('Location', {
            'fields': ('warehouse', 'zone')
        }),
        ('Environmental Data', {
            'fields': ('temperature', 'humidity', 'additional_data')
        }),
        ('Sensor Information', {
            'fields': ('sensor_id', 'sensor_location')
        }),
        ('Alert Status', {
            'fields': ('is_within_range', 'alert_triggered', 'alert_acknowledged', 'acknowledged_by')
        }),
    )
    
    def alert_status(self, obj):
        if obj.alert_triggered and not obj.alert_acknowledged:
            return format_html('<span style="color: red; font-weight: bold;">🚨 ALERT</span>')
        elif obj.alert_triggered and obj.alert_acknowledged:
            return format_html('<span style="color: orange;">✓ Acknowledged</span>')
        elif not obj.is_within_range:
            return format_html('<span style="color: orange;">⚠ Out of Range</span>')
        else:
            return format_html('<span style="color: green;">✓ Normal</span>')
    alert_status.short_description = "Status"


@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = ['inspection_number', 'inventory_product', 'inspection_type', 'overall_result', 'quality_score', 'inspector', 'inspection_date']
    list_filter = ['inspection_type', 'overall_result', 'inspection_date', 'requires_follow_up']
    search_fields = ['inspection_number', 'inventory__product__name', 'inspector__first_name', 'inspector__last_name']
    ordering = ['-inspection_date']
    date_hierarchy = 'inspection_date'
    
    fieldsets = (
        ('Inspection Information', {
            'fields': ('inspection_number', 'inspection_type', 'inventory', 'inspector', 'inspection_date')
        }),
        ('Test Results', {
            'fields': ('visual_inspection', 'physical_tests', 'chemical_tests', 'microbiological_tests'),
            'classes': ['collapse']
        }),
        ('Assessment', {
            'fields': ('overall_result', 'quality_score', 'findings')
        }),
        ('Recommendations & Actions', {
            'fields': ('recommendations', 'corrective_actions')
        }),
        ('Follow-up', {
            'fields': ('requires_follow_up', 'follow_up_date', 'follow_up_completed')
        }),
        ('Documentation', {
            'fields': ('photos', 'documents'),
            'classes': ['collapse']
        }),
    )
    
    def inventory_product(self, obj):
        return obj.inventory.product.name
    inventory_product.short_description = "Product"


# Custom admin site configuration
admin.site.site_header = "AgriConnect Warehouse Management"
admin.site.site_title = "AgriConnect Warehouses"
admin.site.index_title = "Warehouse Operations Dashboard"
