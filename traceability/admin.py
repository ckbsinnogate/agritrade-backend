"""
AgriConnect Traceability Admin Interface
Admin configuration for blockchain traceability system
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    BlockchainNetwork, SmartContract, BlockchainTransaction,
    Farm, FarmCertification, ProductTrace, SupplyChainEvent,
    ConsumerScan
)

@admin.register(BlockchainNetwork)
class BlockchainNetworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'network_id', 'native_currency', 'is_testnet', 'is_active', 'created_at']
    list_filter = ['is_testnet', 'is_active', 'native_currency']
    search_fields = ['name', 'network_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'network_id', 'native_currency')
        }),
        ('Network Configuration', {
            'fields': ('rpc_url', 'explorer_url', 'is_testnet', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'network', 'is_deployed', 'deployed_at']
    list_filter = ['network', 'is_deployed', 'version']
    search_fields = ['name', 'contract_address']
    readonly_fields = ['deployed_at', 'created_at']
    
    fieldsets = (
        ('Contract Information', {
            'fields': ('name', 'version', 'network', 'contract_address')
        }),
        ('Deployment', {
            'fields': ('is_deployed', 'deployment_transaction', 'deployed_at')
        }),
        ('Contract Code', {
            'fields': ('abi', 'bytecode'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_hash_short', 'function_name', 'contract', 'status', 'gas_used', 'created_at']
    list_filter = ['status', 'contract', 'created_at']
    search_fields = ['transaction_hash', 'function_name', 'from_address', 'to_address']
    readonly_fields = ['created_at', 'confirmed_at']
    
    def transaction_hash_short(self, obj):
        return f"{obj.transaction_hash[:10]}...{obj.transaction_hash[-8:]}"
    transaction_hash_short.short_description = 'Transaction Hash'

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer', 'location', 'farm_size_hectares', 'organic_certified', 'is_verified', 'created_at']
    list_filter = ['organic_certified', 'is_verified', 'certification_body']
    search_fields = ['name', 'farmer__username', 'farmer__email', 'location', 'registration_number']
    readonly_fields = ['farm_id', 'created_at', 'updated_at']

@admin.register(FarmCertification)
class FarmCertificationAdmin(admin.ModelAdmin):
    list_display = ['farm', 'certification_type', 'certificate_number', 'issuing_authority', 'is_valid', 'blockchain_verified']
    list_filter = ['certification_type', 'blockchain_verified', 'issuing_authority']
    search_fields = ['farm__name', 'certificate_number', 'issuing_authority']
    readonly_fields = ['created_at']
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Valid'

@admin.register(ProductTrace)
class ProductTraceAdmin(admin.ModelAdmin):
    list_display = ['product', 'batch_number', 'farm', 'harvest_date', 'quality_grade', 'consumer_view_count', 'is_active']
    list_filter = ['quality_grade', 'is_active', 'harvest_date', 'farm']
    search_fields = ['product__name', 'batch_number', 'blockchain_id', 'farm__name']
    readonly_fields = ['blockchain_id', 'consumer_view_count', 'last_viewed_at', 'created_at']

@admin.register(SupplyChainEvent)
class SupplyChainEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'product_trace', 'actor', 'location', 'timestamp', 'status', 'verified_at']
    list_filter = ['event_type', 'status', 'verification_required', 'timestamp']
    search_fields = ['product_trace__product__name', 'actor__username', 'location', 'description']
    readonly_fields = ['event_id', 'created_at', 'verified_at']

@admin.register(ConsumerScan)
class ConsumerScanAdmin(admin.ModelAdmin):
    list_display = ['product_trace', 'consumer_id', 'device_type', 'feedback_rating', 'scan_duration', 'scanned_at']
    list_filter = ['device_type', 'feedback_rating', 'scanned_at']
    search_fields = ['product_trace__product__name', 'consumer_id', 'ip_address']
    readonly_fields = ['scan_id', 'scanned_at']
