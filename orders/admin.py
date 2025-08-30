"""
AgriConnect Order Admin
Admin interface for order management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Order, OrderItem, OrderStatusHistory, ShippingMethod,
    OrderShipping, ProcessingOrder, OrderPayment
)


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'created_at']
    fields = [
        'product', 'product_variation', 'quantity', 'unit_price', 
        'total_price', 'quality_specifications'
    ]


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline admin for order status history"""
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['timestamp', 'updated_by']
    fields = ['status', 'notes', 'updated_by', 'timestamp']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders"""
    list_display = [
        'order_number', 'buyer', 'seller', 'status', 'payment_status',
        'total_amount', 'currency', 'order_date', 'expected_delivery_date'
    ]
    list_filter = [
        'status', 'payment_status', 'order_type', 'delivery_country',
        'order_date', 'expected_delivery_date'
    ]
    search_fields = [
        'order_number', 'buyer__username', 'buyer__email',
        'seller__username', 'seller__email', 'delivery_city'
    ]
    readonly_fields = [
        'id', 'order_number', 'subtotal', 'total_amount',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Order Information', {
            'fields': (
                'id', 'order_number', 'order_type', 'status', 'payment_status'
            )
        }),
        ('Parties', {
            'fields': ('buyer', 'seller')
        }),
        ('Financial Details', {
            'fields': (
                'subtotal', 'tax_amount', 'shipping_cost', 
                'discount_amount', 'total_amount', 'currency'
            )
        }),
        ('Delivery Information', {
            'fields': (
                'delivery_address', 'delivery_city', 'delivery_region',
                'delivery_country', 'delivery_phone'
            )
        }),
        ('Timing', {
            'fields': (
                'order_date', 'expected_delivery_date', 'actual_delivery_date'
            )
        }),
        ('Notes and Instructions', {
            'fields': (
                'buyer_notes', 'seller_notes', 'special_instructions'
            ),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'logistics_partner'),
            'classes': ('collapse',)
        }),
        ('Quality and Contract', {
            'fields': (
                'quality_requirements', 'quality_inspection_passed',
                'contract_details', 'delivery_schedule'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    date_hierarchy = 'order_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('buyer', 'seller')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for order items"""
    list_display = [
        'order', 'product_name', 'quantity', 'unit_price', 
        'total_price', 'unit', 'created_at'
    ]
    list_filter = ['unit', 'created_at']
    search_fields = [
        'order__order_number', 'product__name', 'product_name'
    ]
    readonly_fields = ['total_price', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Admin interface for order status history"""
    list_display = ['order', 'status', 'updated_by', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['order__order_number', 'notes']
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'updated_by')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """Admin interface for shipping methods"""
    list_display = [
        'name', 'base_cost', 'cost_per_kg', 'estimated_days_min', 'estimated_days_max', 'is_active'
    ]
    list_filter = ['is_active', 'estimated_days_min']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('base_cost', 'cost_per_kg')
        }),
        ('Delivery', {
            'fields': ('estimated_days_min', 'estimated_days_max', 'available_countries', 'available_regions')
        })
    )


@admin.register(OrderShipping)
class OrderShippingAdmin(admin.ModelAdmin):
    """Admin interface for order shipping"""
    list_display = [
        'order', 'shipping_method', 'tracking_number', 
        'shipped_at', 'estimated_delivery', 'actual_delivery'
    ]
    list_filter = ['shipping_method', 'shipped_at', 'estimated_delivery']
    search_fields = ['order__order_number', 'tracking_number', 'carrier']
    readonly_fields = ['shipped_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'shipping_method')


@admin.register(ProcessingOrder)
class ProcessingOrderAdmin(admin.ModelAdmin):
    """Admin interface for processing orders"""
    list_display = [
        'order', 'processor', 'processing_type', 'processing_status',
        'raw_materials_received', 'quality_check_passed'
    ]
    list_filter = [
        'processing_status', 'raw_materials_received', 
        'quality_check_passed', 'processing_started_at'
    ]
    search_fields = [
        'order__order_number', 'processor__username', 
        'processing_type', 'processing_facility'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'processor')
        }),
        ('Processing Details', {
            'fields': (
                'processing_type', 'processing_facility', 'processing_status'
            )
        }),
        ('Raw Materials', {
            'fields': (
                'raw_materials_received', 'raw_materials_quality_score'
            )
        }),
        ('Processing Timeline', {
            'fields': (
                'processing_started_at', 'processing_completed_at'
            )
        }),
        ('Quality Control', {
            'fields': (
                'quality_check_passed', 'quality_notes'
            )
        }),
        ('Output Details', {
            'fields': (
                'expected_yield', 'actual_yield', 'waste_percentage'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'processor')


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    """Admin interface for order payments"""
    list_display = [
        'order', 'payment_method', 'amount', 'currency', 
        'status', 'initiated_at', 'completed_at'
    ]
    list_filter = ['payment_method', 'status', 'currency', 'initiated_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['transaction_id', 'gateway_response', 'initiated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')
