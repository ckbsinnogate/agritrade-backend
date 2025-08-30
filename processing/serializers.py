"""
AgriConnect Processing Serializers
REST API serializers for processing management system
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ProcessingEquipment, ProcessingSchedule, 
    ProcessingQualityCheck, ProcessingStats
)

User = get_user_model()

class ProcessingEquipmentSerializer(serializers.ModelSerializer):
    """Serializer for processing equipment"""
    processor_name = serializers.CharField(source='processor.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_type_display = serializers.CharField(source='get_equipment_type_display', read_only=True)
    
    class Meta:
        model = ProcessingEquipment
        fields = [
            'id', 'name', 'equipment_type', 'equipment_type_display',
            'description', 'model_number', 'manufacturer', 'capacity',
            'capacity_unit', 'status', 'status_display', 'processor',
            'processor_name', 'purchase_date', 'last_maintenance',
            'next_maintenance', 'operating_hours', 'specifications',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProcessingEquipmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating processing equipment"""
    
    class Meta:
        model = ProcessingEquipment
        fields = [
            'name', 'equipment_type', 'description', 'model_number',
            'manufacturer', 'capacity', 'capacity_unit', 'status',
            'purchase_date', 'specifications'
        ]

class ProcessingScheduleSerializer(serializers.ModelSerializer):
    """Serializer for processing schedules"""
    processor_name = serializers.CharField(source='processor.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    equipment_required = ProcessingEquipmentSerializer(many=True, read_only=True)
    equipment_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessingSchedule
        fields = [
            'id', 'processor', 'processor_name', 'order', 'title',
            'description', 'scheduled_start', 'scheduled_end',
            'actual_start', 'actual_end', 'status', 'status_display',
            'priority', 'priority_display', 'equipment_required',
            'equipment_ids', 'raw_materials', 'expected_output',
            'notes', 'duration_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_duration_hours(self, obj):
        """Calculate duration in hours"""
        if obj.scheduled_start and obj.scheduled_end:
            delta = obj.scheduled_end - obj.scheduled_start
            return round(delta.total_seconds() / 3600, 2)
        return 0
    
    def create(self, validated_data):
        equipment_ids = validated_data.pop('equipment_ids', [])
        schedule = ProcessingSchedule.objects.create(**validated_data)
        if equipment_ids:
            equipment = ProcessingEquipment.objects.filter(id__in=equipment_ids)
            schedule.equipment_required.set(equipment)
        return schedule

class ProcessingQualityCheckSerializer(serializers.ModelSerializer):
    """Serializer for quality checks"""
    processor_name = serializers.CharField(source='processor.username', read_only=True)
    inspector_name = serializers.CharField(source='inspector.username', read_only=True)
    check_type_display = serializers.CharField(source='get_check_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    schedule_title = serializers.CharField(source='schedule.title', read_only=True)
    
    class Meta:
        model = ProcessingQualityCheck
        fields = [
            'id', 'processor', 'processor_name', 'schedule', 'schedule_title',
            'check_type', 'check_type_display', 'check_date', 'inspector',
            'inspector_name', 'product_batch', 'status', 'status_display',
            'quality_score', 'parameters_checked', 'test_results',
            'issues_found', 'corrective_actions', 'compliance_standards',
            'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProcessingStatsSerializer(serializers.ModelSerializer):
    """Serializer for processing statistics"""
    processor_name = serializers.CharField(source='processor.username', read_only=True)
    
    class Meta:
        model = ProcessingStats
        fields = [
            'id', 'processor', 'processor_name', 'date',
            'total_orders_processed', 'total_volume_processed',
            'volume_unit', 'equipment_utilization', 'quality_pass_rate',
            'production_efficiency', 'revenue_generated', 'costs_incurred',
            'profit_margin', 'energy_consumption', 'waste_generated',
            'downtime_hours', 'metrics_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProcessingDashboardStatsSerializer(serializers.Serializer):
    """Serializer for processing dashboard statistics"""
    total_equipment = serializers.IntegerField()
    active_schedules = serializers.IntegerField()
    pending_quality_checks = serializers.IntegerField()
    today_production = serializers.DecimalField(max_digits=12, decimal_places=2)
    equipment_utilization = serializers.DecimalField(max_digits=5, decimal_places=2)
    quality_pass_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    recent_orders = serializers.IntegerField()
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)