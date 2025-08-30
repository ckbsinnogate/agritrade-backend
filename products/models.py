"""
AgriConnect Product Models
Support for both raw agricultural products and processed goods

Based on comprehensive PRD supporting complete agricultural value chain:
- Raw crops and livestock from farmers
- Processed products from value-addition businesses  
- Organic and non-organic classification
- Blockchain traceability integration
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Category(models.Model):
    """Product categories for agricultural products"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        db_table = 'product_categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Core product model supporting both raw and processed agricultural goods"""
    
    PRODUCT_TYPE_CHOICES = [
        ('raw', 'Raw Agricultural Product'),
        ('processed', 'Processed Product'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]
    
    ORGANIC_STATUS_CHOICES = [
        ('organic', 'Organic Certified'),
        ('non_organic', 'Non-Organic'),
        ('transitional', 'Transitional to Organic'),
    ]
    
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('tons', 'Metric Tons'),
        ('pieces', 'Pieces'),
        ('bunches', 'Bunches'),
        ('bags', 'Bags'),
        ('liters', 'Liters'),
        ('ml', 'Milliliters'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Product Classification
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    organic_status = models.CharField(max_length=20, choices=ORGANIC_STATUS_CHOICES, default='non_organic')
    
    # Seller Information
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    
    # Pricing and Inventory
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    minimum_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Product Details
    harvest_date = models.DateField(null=True, blank=True)  # For raw products
    expiry_date = models.DateField(null=True, blank=True)
    processing_date = models.DateField(null=True, blank=True)  # For processed products
    
    # Location
    origin_country = models.CharField(max_length=100, default='Ghana')
    origin_region = models.CharField(max_length=100, blank=True)
    origin_city = models.CharField(max_length=100, blank=True)
    
    # Quality and Certifications
    quality_grade = models.CharField(max_length=10, blank=True)  # A, B, C grades
    certifications = models.JSONField(default=list, blank=True)  # List of certification IDs
    
    # Images and Media
    featured_image = models.ImageField(upload_to='products/', blank=True, null=True)
    additional_images = models.JSONField(default=list, blank=True)
    
    # Processing Information (for processed products)
    raw_materials = models.JSONField(default=list, blank=True)  # List of raw material product IDs
    processing_method = models.TextField(blank=True)
    processing_facility = models.CharField(max_length=200, blank=True)
    
    # Nutritional Information
    nutritional_info = models.JSONField(default=dict, blank=True)
    
    # Status and Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # SEO and Search
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    search_keywords = models.JSONField(default=list, blank=True)
    
    # Statistics
    views_count = models.PositiveIntegerField(default=0)
    orders_count = models.PositiveIntegerField(default=0)
    
    # Blockchain Integration
    blockchain_hash = models.CharField(max_length=100, blank=True)
    blockchain_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['category', 'product_type', 'organic_status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['origin_country', 'origin_region']),
            models.Index(fields=['price_per_unit']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_product_type_display()}"
    
    def get_absolute_url(self):
        return f"/products/{self.slug}/"
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0
    
    def get_availability_status(self):
        """Get product availability status"""
        if self.status != 'active':
            return self.get_status_display()
        elif not self.is_in_stock():
            return 'Out of Stock'
        else:
            return 'Available'


class ProductVariation(models.Model):
    """Product variations (size, weight, packaging options)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    name = models.CharField(max_length=100)  # e.g., "Small Pack", "Bulk Order"
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=Product.UNIT_CHOICES)
    minimum_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_variations'
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductImage(models.Model):
    """Additional product images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductAttribute(models.Model):
    """Flexible product attributes (color, size, variety, etc.)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)  # e.g., "Variety", "Color", "Size"
    value = models.CharField(max_length=200)  # e.g., "Red", "Large", "Hybrid"
    
    class Meta:
        db_table = 'product_attributes'
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.name}: {self.name} = {self.value}"


class TraceabilityRecord(models.Model):
    """Blockchain traceability records for products"""
    STAGE_CHOICES = [
        ('planting', 'Planting'),
        ('growing', 'Growing'),
        ('harvesting', 'Harvesting'),
        ('post_harvest', 'Post-Harvest Handling'),
        ('processing', 'Processing'),
        ('packaging', 'Packaging'),
        ('storage', 'Storage'),
        ('transport', 'Transportation'),
        ('retail', 'Retail'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='traceability_records')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    location = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    actor = models.ForeignKey(User, on_delete=models.CASCADE)  # Who performed this action
    
    # Detailed information
    description = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # Flexible data storage
    
    # Quality metrics
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    quality_score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    
    # Blockchain integration
    blockchain_hash = models.CharField(max_length=100, blank=True)
    blockchain_verified = models.BooleanField(default=False)
    
    # Evidence
    images = models.JSONField(default=list, blank=True)
    documents = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'traceability_records'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_stage_display()} at {self.location}"


class Certification(models.Model):
    """Product certifications (organic, quality, safety, etc.)"""
    CERTIFICATION_TYPES = [
        ('organic', 'Organic Certification'),
        ('quality', 'Quality Assurance'),
        ('safety', 'Food Safety'),
        ('fair_trade', 'Fair Trade'),
        ('rainforest', 'Rainforest Alliance'),
        ('global_gap', 'GlobalGAP'),
        ('halal', 'Halal Certification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_certifications')
    certification_type = models.CharField(max_length=20, choices=CERTIFICATION_TYPES)
    
    # Certification Details
    certificate_number = models.CharField(max_length=100, unique=True)
    issuing_body = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    
    # Status and Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_documents = models.JSONField(default=list, blank=True)
    
    # Blockchain Integration
    blockchain_hash = models.CharField(max_length=100, blank=True)
    blockchain_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_certifications'
        unique_together = ['product', 'certification_type', 'certificate_number']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_certification_type_display()}"
    
    def is_valid(self):
        """Check if certification is currently valid"""
        from django.utils import timezone
        return (
            self.status == 'approved' and
            self.expiry_date > timezone.now().date()
        )
