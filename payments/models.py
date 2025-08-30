"""
AgriConnect Payment System Models
Complete payment processing and escrow system for agricultural commerce

Supports:
- African payment methods (Mobile Money, Bank Transfer, Cards)
- Multi-gateway integration (Paystack, Flutterwave)
- Escrow system for agricultural trades
- Dispute resolution and refund management
- Multi-currency support across Africa
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class PaymentGateway(models.Model):
    """Payment gateway configuration and management"""
    
    GATEWAY_CHOICES = [
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('mtn_momo', 'MTN Mobile Money'),
        ('vodafone_cash', 'Vodafone Cash'),
        ('airteltigo_money', 'AirtelTigo Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('stripe', 'Stripe'),
        # Cryptocurrency Gateways
        ('bitcoin_core', 'Bitcoin Core'),
        ('usdc_polygon', 'USDC on Polygon'),
        ('ethereum_mainnet', 'Ethereum Mainnet'),
        # Credit/Financing Gateways
        ('agri_credit_bank', 'Agricultural Credit Bank'),
        ('farmer_finance_coop', 'Farmer Finance Cooperative'),
        ('digital_agri_lending', 'Digital Agricultural Lending'),
    ]
    
    name = models.CharField(max_length=50, choices=GATEWAY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    # Gateway configuration
    api_base_url = models.URLField()
    public_key = models.CharField(max_length=200, blank=True)
    secret_key = models.CharField(max_length=200, blank=True)  # Should be encrypted
    webhook_secret = models.CharField(max_length=200, blank=True)
    
    # Supported features
    supported_currencies = models.JSONField(default=list)
    supported_countries = models.JSONField(default=list)
    supported_payment_methods = models.JSONField(default=list)
      # Business configuration
    transaction_fee_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_gateways'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.display_name} ({'Active' if self.is_active else 'Inactive'})"


class PaymentMethod(models.Model):
    """Available payment methods for users"""
    METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('crypto', 'Cryptocurrency'),
        ('cash', 'Cash on Delivery'),
        ('bank_account', 'Bank Account'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_CHOICES)
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Payment method details (encrypted storage)
    account_details = models.JSONField(default=dict)  # phone_number, account_number, etc.
    display_name = models.CharField(max_length=100)  # "MTN *****1234"
    
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.display_name}"


class Transaction(models.Model):
    """Core transaction model for all payments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    
    TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('transfer', 'Transfer'),
        ('escrow_fund', 'Escrow Funding'),
        ('escrow_release', 'Escrow Release'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Transaction details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, null=True, blank=True)
    
    # Financial details
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=10, default='GHS')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1)
    
    # Gateway details
    gateway_reference = models.CharField(max_length=200, unique=True)
    external_reference = models.CharField(max_length=200, blank=True)  # Gateway transaction ID
    
    # Status and type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='payment')
    
    # Metadata and responses
    gateway_request = models.JSONField(default=dict, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gateway_reference']),
            models.Index(fields=['external_reference']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.gateway_reference} - {self.amount} {self.currency} ({self.status})"


class EscrowAccount(models.Model):
    """Escrow accounts for secure agricultural transactions"""
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('funded', 'Funded'),
        ('partial_release', 'Partial Release'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='escrow')
    
    # Parties
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_escrows')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_escrows')
    
    # Financial details
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=10, default='GHS')
    released_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Escrow configuration
    auto_release_days = models.PositiveIntegerField(default=7)  # Auto-release after delivery confirmation
    requires_quality_confirmation = models.BooleanField(default=True)
    
    # Status and management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    
    # Timestamps
    funded_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    auto_release_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'escrow_accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Escrow {self.id} - Order {self.order.order_number} ({self.status})"


class EscrowMilestone(models.Model):
    """Milestone-based escrow releases for agricultural transactions"""
    MILESTONE_CHOICES = [
        ('order_confirmed', 'Order Confirmed'),
        ('goods_prepared', 'Goods Prepared'),
        ('goods_shipped', 'Goods Shipped'),
        ('goods_delivered', 'Goods Delivered'),
        ('quality_confirmed', 'Quality Confirmed'),
        ('completion', 'Transaction Completed'),
    ]
    
    escrow = models.ForeignKey(EscrowAccount, on_delete=models.CASCADE, related_name='milestones')
    milestone_type = models.CharField(max_length=20, choices=MILESTONE_CHOICES)
    description = models.CharField(max_length=200)
    
    # Release configuration
    release_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    release_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Status tracking
    is_completed = models.BooleanField(default=False)
    is_released = models.BooleanField(default=False)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Evidence and verification
    evidence_data = models.JSONField(default=dict, blank=True)  # photos, GPS, signatures
    verification_notes = models.TextField(blank=True)
    
    # Timestamps
    completed_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'escrow_milestones'
        ordering = ['release_percentage']
        unique_together = ['escrow', 'milestone_type']
    
    def __str__(self):
        return f"{self.escrow.id} - {self.milestone_type} ({self.release_percentage}%)"


class DisputeCase(models.Model):
    """Dispute resolution for payment and escrow issues"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('awaiting_response', 'Awaiting Response'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    DISPUTE_TYPE_CHOICES = [
        ('payment_failed', 'Payment Failed'),
        ('product_quality', 'Product Quality Issue'),
        ('delivery_issue', 'Delivery Problem'),
        ('wrong_product', 'Wrong Product Received'),
        ('fraud', 'Fraudulent Activity'),
        ('other', 'Other'),
    ]
    
    RESOLUTION_CHOICES = [
        ('refund_buyer', 'Refund to Buyer'),
        ('release_seller', 'Release to Seller'),
        ('partial_refund', 'Partial Refund'),
        ('replacement', 'Product Replacement'),
        ('no_action', 'No Action Required'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Dispute details
    escrow = models.ForeignKey(EscrowAccount, on_delete=models.CASCADE, related_name='disputes', null=True, blank=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='disputes', null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='disputes')
    
    # Parties
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='raised_disputes')
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispute_responses')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_disputes')
    
    # Dispute information
    dispute_type = models.CharField(max_length=20, choices=DISPUTE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Evidence and attachments
    evidence = models.JSONField(default=list, blank=True)  # URLs to uploaded files
    
    # Resolution
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution = models.CharField(max_length=20, choices=RESOLUTION_CHOICES, blank=True)
    resolution_notes = models.TextField(blank=True)
    resolution_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    resolved_at = models.DateTimeField(null=True, blank=True)
    response_deadline = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dispute_cases'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute {self.id} - {self.title} ({self.status})"


class PaymentWebhook(models.Model):
    """Webhook events from payment gateways"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Webhook details
    event_type = models.CharField(max_length=100)
    webhook_id = models.CharField(max_length=200, blank=True)  # Gateway webhook ID
    
    # Data and processing
    payload = models.JSONField(default=dict)
    signature = models.CharField(max_length=500, blank=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Related transaction
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_webhooks'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['gateway', 'event_type']),
            models.Index(fields=['is_processed', 'received_at']),
        ]
    
    def __str__(self):
        return f"Webhook {self.event_type} from {self.gateway.name} ({'Processed' if self.is_processed else 'Pending'})"
