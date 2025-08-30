"""
AgriConnect Traceability API Serializers
REST API serializers for blockchain traceability system
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    BlockchainNetwork, SmartContract, BlockchainTransaction,
    Farm, FarmCertification, ProductTrace, SupplyChainEvent,
    ConsumerScan
)
from products.models import Product

User = get_user_model()

class BlockchainNetworkSerializer(serializers.ModelSerializer):
    """Serializer for blockchain networks"""
    
    class Meta:
        model = BlockchainNetwork
        fields = [
            'id', 'name', 'network_id', 'rpc_url', 'explorer_url',
            'native_currency', 'is_testnet', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class SmartContractSerializer(serializers.ModelSerializer):
    """Serializer for smart contracts"""
    network_name = serializers.CharField(source='network.name', read_only=True)
    
    class Meta:
        model = SmartContract
        fields = [
            'id', 'name', 'contract_address', 'abi', 'bytecode',
            'network', 'network_name', 'version', 'is_deployed',
            'deployment_transaction', 'deployed_at', 'created_at'
        ]
        read_only_fields = ['id', 'deployed_at', 'created_at']

class BlockchainTransactionSerializer(serializers.ModelSerializer):
    """Serializer for blockchain transactions"""
    contract_name = serializers.CharField(source='contract.name', read_only=True)
    network_name = serializers.CharField(source='contract.network.name', read_only=True)
    
    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'transaction_hash', 'contract', 'contract_name', 'network_name',
            'function_name', 'parameters', 'from_address', 'to_address',
            'gas_limit', 'gas_used', 'gas_price', 'value', 'status',
            'block_number', 'block_hash', 'confirmation_count',
            'created_at', 'confirmed_at'
        ]
        read_only_fields = ['id', 'created_at', 'confirmed_at']

class FarmerBasicSerializer(serializers.ModelSerializer):
    """Basic farmer information for farm listings"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'email']

class FarmCertificationSerializer(serializers.ModelSerializer):
    """Serializer for farm certifications"""
    certification_type_display = serializers.CharField(source='get_certification_type_display', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = FarmCertification
        fields = [
            'id', 'certification_type', 'certification_type_display',
            'certificate_number', 'issuing_authority', 'issue_date',
            'expiry_date', 'is_valid', 'certificate_file_hash',
            'blockchain_hash', 'blockchain_verified', 'created_at'
        ]
        read_only_fields = ['id', 'blockchain_hash', 'blockchain_verified', 'created_at']

class FarmSerializer(serializers.ModelSerializer):
    """Serializer for farms"""
    farmer_info = FarmerBasicSerializer(source='farmer', read_only=True)
    certifications = FarmCertificationSerializer(many=True, read_only=True)
    certifications_count = serializers.IntegerField(source='certifications.count', read_only=True)
    
    class Meta:
        model = Farm
        fields = [
            'id', 'farm_id', 'name', 'farmer', 'farmer_info', 'location',
            'latitude', 'longitude', 'farm_size_hectares', 'organic_certified',
            'certification_body', 'registration_number', 'blockchain_address',
            'is_verified', 'verification_date', 'certifications',
            'certifications_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'farm_id', 'blockchain_address', 'created_at', 'updated_at']

class FarmBasicSerializer(serializers.ModelSerializer):
    """Basic farm information for product listings"""
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    
    class Meta:
        model = Farm
        fields = [
            'id', 'farm_id', 'name', 'farmer_name', 'location',
            'organic_certified', 'is_verified'
        ]
        read_only_fields = fields

class ProductBasicSerializer(serializers.ModelSerializer):
    """Basic product information for traceability"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_name', 'unit']
        read_only_fields = fields

class SupplyChainEventSerializer(serializers.ModelSerializer):
    """Serializer for supply chain events"""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    
    class Meta:
        model = SupplyChainEvent
        fields = [
            'id', 'event_id', 'event_type', 'event_type_display',
            'actor', 'actor_name', 'location', 'latitude', 'longitude',
            'timestamp', 'description', 'metadata', 'blockchain_hash',
            'status', 'status_display', 'verification_required',
            'verified_at', 'created_at'
        ]
        read_only_fields = ['id', 'event_id', 'blockchain_hash', 'verified_at', 'created_at']

class ProductTraceSerializer(serializers.ModelSerializer):
    """Serializer for product traceability"""
    product_info = ProductBasicSerializer(source='product', read_only=True)
    farm_info = FarmBasicSerializer(source='farm', read_only=True)
    events = SupplyChainEventSerializer(many=True, read_only=True)
    events_count = serializers.IntegerField(source='events.count', read_only=True)
    
    class Meta:
        model = ProductTrace
        fields = [
            'id', 'blockchain_id', 'product', 'product_info', 'farm',
            'farm_info', 'harvest_date', 'harvest_location', 'batch_number',
            'quantity_harvested', 'quality_grade', 'qr_code_data',
            'qr_code_image', 'ipfs_hash', 'consumer_view_count',
            'last_viewed_at', 'events', 'events_count', 'is_active', 'created_at'
        ]
        read_only_fields = [
            'id', 'blockchain_id', 'consumer_view_count', 'last_viewed_at', 'created_at'
        ]

class ConsumerScanSerializer(serializers.ModelSerializer):
    """Serializer for consumer scans"""
    product_name = serializers.CharField(source='product_trace.product.name', read_only=True)
    batch_number = serializers.CharField(source='product_trace.batch_number', read_only=True)
    
    class Meta:
        model = ConsumerScan
        fields = [
            'id', 'scan_id', 'product_trace', 'product_name', 'batch_number',
            'consumer_id', 'ip_address', 'user_agent', 'location',
            'latitude', 'longitude', 'device_type', 'app_version',
            'scan_duration', 'feedback_rating', 'feedback_comment', 'scanned_at'
        ]
        read_only_fields = ['id', 'scan_id', 'scanned_at']

class ConsumerTraceabilitySerializer(serializers.ModelSerializer):
    """Simplified serializer for consumer-facing traceability information"""
    product = ProductBasicSerializer(read_only=True)
    farm = FarmBasicSerializer(read_only=True)
    supply_chain_journey = SupplyChainEventSerializer(source='events', many=True, read_only=True)
    farm_certifications = FarmCertificationSerializer(source='farm.certifications', many=True, read_only=True)
    
    class Meta:
        model = ProductTrace
        fields = [
            'blockchain_id', 'product', 'farm', 'harvest_date',
            'harvest_location', 'batch_number', 'quality_grade',
            'supply_chain_journey', 'farm_certifications', 'consumer_view_count'
        ]
        read_only_fields = fields

class QRCodeDataSerializer(serializers.Serializer):
    """Serializer for QR code data structure"""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    batch_number = serializers.CharField()
    blockchain_id = serializers.CharField()
    farm_name = serializers.CharField()
    farmer_name = serializers.CharField()
    harvest_date = serializers.DateTimeField()
    organic_certified = serializers.BooleanField()
    verification_url = serializers.URLField()
    scan_timestamp = serializers.DateTimeField(read_only=True)

class BlockchainVerificationSerializer(serializers.Serializer):
    """Serializer for blockchain verification responses"""
    verified = serializers.BooleanField()
    transaction_hash = serializers.CharField(required=False)
    block_number = serializers.IntegerField(required=False)
    confirmation_count = serializers.IntegerField(required=False)
    verification_timestamp = serializers.DateTimeField(required=False)
    error_message = serializers.CharField(required=False)

class TraceabilityAnalyticsSerializer(serializers.Serializer):
    """Serializer for traceability analytics"""
    total_products_traced = serializers.IntegerField()
    total_farms_registered = serializers.IntegerField()
    total_consumer_scans = serializers.IntegerField()
    blockchain_transactions = serializers.IntegerField()
    organic_products_percentage = serializers.FloatField()
    verified_farms_percentage = serializers.FloatField()
    average_supply_chain_events = serializers.FloatField()
    top_scanned_products = serializers.ListField(child=serializers.DictField())
    recent_activities = serializers.ListField(child=serializers.DictField())

class FarmRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for farm registration process"""
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    
    class Meta:
        model = Farm
        fields = [
            'name', 'location', 'latitude', 'longitude', 'farm_size_hectares',
            'organic_certified', 'certification_body', 'registration_number',
            'farmer_name'
        ]
        
    def create(self, validated_data):
        # Set the farmer to the current user
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)
