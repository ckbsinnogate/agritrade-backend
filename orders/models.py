"""
AgriConnect Orders Models
Complete order management system for agricultural commerce

Supports:
- Individual and bulk orders
- Escrow payment integration
- Order tracking and status updates
- Institutional bulk ordering
- Processing orders for value addition
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

User = get_user_model()


class Order(models.Model):
    """Main order model for all agricultural transactions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('regular', 'Regular Order'),
        ('bulk', 'Bulk Order'),
        ('subscription', 'Subscription Order'),
        ('processing', 'Processing Order'),
        ('contract', 'Contract Farming Order'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('escrow', 'In Escrow'),
        ('released', 'Payment Released'),
        ('refunded', 'Refunded'),
        ('disputed', 'Under Dispute'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='regular')
    
    # Parties
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    
    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Financial Information
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default='GHS')
    
    # Delivery Information
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_region = models.CharField(max_length=100)
    delivery_country = models.CharField(max_length=100, default='Ghana')
    delivery_phone = models.CharField(max_length=20)
    
    # Timing
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Special Instructions
    buyer_notes = models.TextField(blank=True)
    seller_notes = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    logistics_partner = models.CharField(max_length=200, blank=True)
    
    # Contract Information (for contract farming)
    contract_details = models.JSONField(default=dict, blank=True)
    delivery_schedule = models.JSONField(default=list, blank=True)
    
    # Quality Requirements
    quality_requirements = models.JSONField(default=dict, blank=True)
    quality_inspection_passed = models.BooleanField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['order_date']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.buyer.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number"""
        import datetime
        now = datetime.datetime.now()
        return f"AG{now.strftime('%Y%m%d')}{now.strftime('%H%M%S')}{str(uuid.uuid4())[:4].upper()}"
    
    def calculate_total(self):
        """Calculate total order amount"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        return self.total_amount


class OrderItem(models.Model):
    """Individual items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    product_variation = models.ForeignKey('products.ProductVariation', on_delete=models.CASCADE, null=True, blank=True)
    
    # Quantity and Pricing
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Product snapshot (in case product details change)
    product_name = models.CharField(max_length=200)
    product_description = models.TextField(blank=True)
    unit = models.CharField(max_length=20)
    
    # Quality and specifications
    quality_specifications = models.JSONField(default=dict, blank=True)
    
    # Processing requirements (for processing orders)
    processing_requirements = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity} {self.unit}"
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Track order status changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Location tracking
    location = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'order_status_history'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Order {self.order.order_number} - {self.get_status_display()}"


class ShippingMethod(models.Model):
    """Available shipping methods"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_days_min = models.PositiveIntegerField()
    estimated_days_max = models.PositiveIntegerField()
    
    # Geographic coverage
    available_countries = models.JSONField(default=list, blank=True)
    available_regions = models.JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'shipping_methods'
    
    def __str__(self):
        return self.name


class OrderShipping(models.Model):
    """Shipping details for orders"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    
    # Tracking information
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    shipped_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    
    # Package details
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)  # length, width, height
    
    class Meta:
        db_table = 'order_shipping'
    
    def __str__(self):
        return f"Shipping for Order {self.order.order_number}"


class ProcessingOrder(models.Model):
    """Special orders for value-addition processing"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('materials_received', 'Raw Materials Received'),
        ('processing', 'In Processing'),
        ('quality_check', 'Quality Check'),
        ('packaging', 'Packaging'),
        ('ready', 'Ready for Delivery'),
        ('completed', 'Completed'),
        ('rejected', 'Quality Rejected'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='processing_order')
    processor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processing_orders')
    
    # Processing details
    processing_type = models.CharField(max_length=100)  # e.g., "Milling", "Oil Extraction"
    processing_facility = models.CharField(max_length=200)
    
    # Raw materials
    raw_materials_received = models.BooleanField(default=False)
    raw_materials_quality_score = models.PositiveIntegerField(null=True, blank=True)
    
    # Processing status
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Quality control
    quality_check_passed = models.BooleanField(null=True, blank=True)
    quality_notes = models.TextField(blank=True)
    
    # Output details
    expected_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    waste_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processing_orders'
    
    def __str__(self):
        return f"Processing Order {self.order.order_number} - {self.processing_type}"


class OrderPayment(models.Model):
    """Payment records for orders"""
    PAYMENT_METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('crypto', 'Cryptocurrency'),
        ('cash', 'Cash'),
        ('escrow', 'Escrow'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default='GHS')
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Gateway information
    payment_gateway = models.CharField(max_length=50, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'order_payments'
        ordering = ['-initiated_at']
    
    def __str__(self):
        return f"Payment {self.amount} {self.currency} for Order {self.order.order_number}"
