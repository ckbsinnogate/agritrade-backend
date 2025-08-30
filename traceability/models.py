"""
AgriConnect Traceability Models
Blockchain-powered supply chain traceability system
"""

from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid
import json

User = get_user_model()

class BlockchainNetwork(models.Model):
    """Blockchain network configuration"""
    name = models.CharField(max_length=100, unique=True)
    network_id = models.IntegerField()
    rpc_url = models.URLField()
    explorer_url = models.URLField(blank=True)
    native_currency = models.CharField(max_length=10, default='ETH')
    is_testnet = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'traceability_blockchain_network'
    
    def __str__(self):
        return f"{self.name} ({'Testnet' if self.is_testnet else 'Mainnet'})"

class SmartContract(models.Model):
    """Smart contract registry"""
    name = models.CharField(max_length=100)
    contract_address = models.CharField(max_length=42, unique=True)
    abi = models.JSONField()  # Contract ABI
    bytecode = models.TextField(blank=True)
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE)
    version = models.CharField(max_length=20, default='1.0.0')
    is_deployed = models.BooleanField(default=False)
    deployment_transaction = models.CharField(max_length=66, blank=True)
    deployed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'traceability_smart_contract'
        unique_together = ['name', 'network']
    
    def __str__(self):
        return f"{self.name} v{self.version} on {self.network.name}"

class BlockchainTransaction(models.Model):
    """Blockchain transaction tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('reverted', 'Reverted'),
    ]
    
    transaction_hash = models.CharField(max_length=66, unique=True)
    contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE)
    function_name = models.CharField(max_length=100)
    parameters = models.JSONField(default=dict)
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    gas_limit = models.BigIntegerField()
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.BigIntegerField()
    value = models.CharField(max_length=78, default='0')  # Wei amount
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    block_number = models.BigIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=66, blank=True)
    confirmation_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'traceability_blockchain_transaction'
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.function_name} - {self.transaction_hash[:10]}..."

class Farm(models.Model):
    """Farm registration for traceability"""
    farm_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    farm_size_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    organic_certified = models.BooleanField(default=False)
    certification_body = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=100, unique=True)
    blockchain_address = models.CharField(max_length=42, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'traceability_farm'
        indexes = [
            models.Index(fields=['farmer']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['organic_certified']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.farmer.get_full_name()}"

class FarmCertification(models.Model):
    """Farm certifications stored on blockchain"""
    CERTIFICATION_TYPES = [
        ('organic', 'Organic Certification'),
        ('fair_trade', 'Fair Trade Certification'),
        ('rainforest', 'Rainforest Alliance'),
        ('global_gap', 'GlobalGAP'),
        ('iso_22000', 'ISO 22000 Food Safety'),
        ('haccp', 'HACCP Certification'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='certifications')
    certification_type = models.CharField(max_length=50, choices=CERTIFICATION_TYPES)
    certificate_number = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    certificate_file_hash = models.CharField(max_length=64, blank=True)  # IPFS hash
    blockchain_hash = models.CharField(max_length=66, blank=True)
    blockchain_verified = models.BooleanField(default=False)
    verification_transaction = models.ForeignKey(
        BlockchainTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'traceability_farm_certification'
        unique_together = ['farm', 'certification_type', 'certificate_number']
    
    def __str__(self):
        return f"{self.farm.name} - {self.get_certification_type_display()}"
    
    @property
    def is_valid(self):
        from django.utils import timezone
        return self.expiry_date > timezone.now().date()

class ProductTrace(models.Model):
    """Blockchain traceability for products"""
    from products.models import Product
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='trace')
    blockchain_id = models.CharField(max_length=66, unique=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    harvest_date = models.DateTimeField()
    harvest_location = models.CharField(max_length=300)
    batch_number = models.CharField(max_length=100)
    quantity_harvested = models.DecimalField(max_digits=10, decimal_places=2)
    quality_grade = models.CharField(max_length=20, default='good')
    qr_code_data = models.TextField()  # QR code content
    qr_code_image = models.TextField(blank=True)  # Base64 encoded image
    ipfs_hash = models.CharField(max_length=64, blank=True)  # IPFS metadata hash
    consumer_view_count = models.IntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'traceability_product_trace'
        indexes = [
            models.Index(fields=['blockchain_id']),
            models.Index(fields=['batch_number']),
            models.Index(fields=['harvest_date']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.batch_number}"

class SupplyChainEvent(models.Model):
    """Supply chain events recorded on blockchain"""
    EVENT_TYPES = [
        ('harvest', 'Harvest'),
        ('process', 'Processing'),
        ('package', 'Packaging'),
        ('store', 'Storage'),
        ('transport', 'Transportation'),
        ('inspect', 'Quality Inspection'),
        ('certify', 'Certification'),
        ('deliver', 'Delivery'),
        ('purchase', 'Consumer Purchase'),
    ]
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Blockchain Verified'),
    ]
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    product_trace = models.ForeignKey(ProductTrace, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    timestamp = models.DateTimeField()
    description = models.TextField()
    metadata = models.JSONField(default=dict)  # Additional event data
    blockchain_hash = models.CharField(max_length=66, blank=True)
    blockchain_transaction = models.ForeignKey(
        BlockchainTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    verification_required = models.BooleanField(default=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'traceability_supply_chain_event'
        indexes = [
            models.Index(fields=['product_trace', 'timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['status']),
        ]
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.product_trace.product.name}"

class ConsumerScan(models.Model):
    """Track consumer QR code scans"""
    scan_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    product_trace = models.ForeignKey(ProductTrace, on_delete=models.CASCADE, related_name='scans')
    consumer_id = models.CharField(max_length=100, blank=True)  # Anonymous or registered
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=300, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=20, blank=True)
    scan_duration = models.IntegerField(default=0)  # Seconds spent viewing
    feedback_rating = models.IntegerField(null=True, blank=True)  # 1-5 rating
    feedback_comment = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'traceability_consumer_scan'
        indexes = [
            models.Index(fields=['product_trace']),
            models.Index(fields=['scanned_at']),
            models.Index(fields=['consumer_id']),
        ]
    
    def __str__(self):
        return f"Scan {self.scan_id} - {self.product_trace.product.name}"
