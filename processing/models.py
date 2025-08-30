"""
AgriConnect Processing Models
Complete processing management system for processors
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()

class ProcessingEquipment(models.Model):
    """Equipment used in processing operations"""
    EQUIPMENT_STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('broken', 'Broken'),
        ('reserved', 'Reserved'),
    ]
    
    EQUIPMENT_TYPE_CHOICES = [
        ('milling', 'Milling Equipment'),
        ('processing', 'Processing Equipment'),
        ('packaging', 'Packaging Equipment'),
        ('cleaning', 'Cleaning Equipment'),
        ('storage', 'Storage Equipment'),
        ('transport', 'Transport Equipment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity_unit = models.CharField(max_length=20, default='kg')
    status = models.CharField(max_length=20, choices=EQUIPMENT_STATUS_CHOICES, default='available')
    processor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processing_equipment')
    purchase_date = models.DateField(null=True, blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    next_maintenance = models.DateTimeField(null=True, blank=True)
    operating_hours = models.PositiveIntegerField(default=0)
    specifications = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processing_equipment'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.equipment_type})"

class ProcessingSchedule(models.Model):
    """Production scheduling for processing operations"""
    SCHEDULE_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processing_schedules')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SCHEDULE_STATUS_CHOICES, default='scheduled')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    equipment_required = models.ManyToManyField(ProcessingEquipment, blank=True)
    raw_materials = models.JSONField(default=list, blank=True)
    expected_output = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processing_schedule'
        ordering = ['scheduled_start']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_start.date()}"

class ProcessingQualityCheck(models.Model):
    """Quality control checks during processing"""
    CHECK_TYPE_CHOICES = [
        ('incoming', 'Incoming Materials'),
        ('in_process', 'In-Process'),
        ('final', 'Final Product'),
        ('packaging', 'Packaging'),
        ('storage', 'Storage'),
    ]
    
    CHECK_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('requires_recheck', 'Requires Recheck'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quality_checks')
    schedule = models.ForeignKey(ProcessingSchedule, on_delete=models.CASCADE, null=True, blank=True)
    check_type = models.CharField(max_length=20, choices=CHECK_TYPE_CHOICES)
    check_date = models.DateTimeField(default=timezone.now)
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='conducted_checks')
    product_batch = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=CHECK_STATUS_CHOICES, default='pending')
    quality_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    parameters_checked = models.JSONField(default=list, blank=True)
    test_results = models.JSONField(default=dict, blank=True)
    issues_found = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    compliance_standards = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processing_quality_checks'
        ordering = ['-check_date']
    
    def __str__(self):
        return f"{self.check_type} - {self.check_date.date()}"

class ProcessingStats(models.Model):
    """Processing statistics and metrics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processing_stats')
    date = models.DateField(default=timezone.now)
    total_orders_processed = models.PositiveIntegerField(default=0)
    total_volume_processed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    volume_unit = models.CharField(max_length=20, default='kg')
    equipment_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quality_pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    production_efficiency = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costs_incurred = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    energy_consumption = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waste_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    downtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    metrics_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processing_stats'
        ordering = ['-date']
        unique_together = ['processor', 'date']
    
    def __str__(self):
        return f"Stats for {self.processor.username} - {self.date}"
