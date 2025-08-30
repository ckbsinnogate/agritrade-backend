"""
AgriConnect Processing Admin
Admin interface for processing management system
"""
from django.contrib import admin
from .models import (
    ProcessingEquipment, ProcessingSchedule, 
    ProcessingQualityCheck, ProcessingStats
)

@admin.register(ProcessingEquipment)
class ProcessingEquipmentAdmin(admin.ModelAdmin):
    """Admin interface for processing equipment"""
    list_display = [
        'name', 'equipment_type', 'status', 'processor', 
        'capacity', 'capacity_unit', 'last_maintenance'
    ]
    list_filter = ['equipment_type', 'status', 'processor']
    search_fields = ['name', 'model_number', 'manufacturer']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProcessingSchedule)
class ProcessingScheduleAdmin(admin.ModelAdmin):
    """Admin interface for processing schedules"""
    list_display = [
        'title', 'processor', 'scheduled_start', 'scheduled_end', 
        'status', 'priority'
    ]
    list_filter = ['status', 'priority', 'processor']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProcessingQualityCheck)
class ProcessingQualityCheckAdmin(admin.ModelAdmin):
    """Admin interface for quality checks"""
    list_display = [
        'check_type', 'processor', 'check_date', 'status', 
        'quality_score', 'inspector'
    ]
    list_filter = ['check_type', 'status', 'processor']
    search_fields = ['product_batch', 'issues_found']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProcessingStats)
class ProcessingStatsAdmin(admin.ModelAdmin):
    """Admin interface for processing statistics"""
    list_display = [
        'processor', 'date', 'total_orders_processed', 
        'total_volume_processed', 'quality_pass_rate', 'profit_margin'
    ]
    list_filter = ['processor', 'date']
    readonly_fields = ['created_at', 'updated_at']
