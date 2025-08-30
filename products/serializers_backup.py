"""
AgriConnect Product Serializers
Handles product catalog, categories, and traceability
"""

from rest_framework import serializers
from .models import Category, Product, ProductVariation, ProductImage, Certification, TraceabilityRecord


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with hierarchy support"""
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'parent',
            'is_active', 'children', 'product_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_children(self, obj):
        if hasattr(obj, 'children'):
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_primary', 'sort_order']


class ProductVariationSerializer(serializers.ModelSerializer):
    """Product variation serializer"""
    
    class Meta:
        model = ProductVariation
        fields = [
            'id', 'variation_name', 'variation_type', 'price',
            'stock_quantity', 'unit', 'weight_kg', 'dimensions',
            'is_available', 'created_at'
        ]


class CertificationSerializer(serializers.ModelSerializer):
    """Certification serializer"""
    
    class Meta:
        model = Certification
        fields = [
            'id', 'certification_name', 'certification_type',
            'issuing_body', 'certificate_number', 'issue_date',
            'expiry_date', 'certificate_url', 'is_verified'
        ]


class TraceabilityRecordSerializer(serializers.ModelSerializer):
    """Traceability record serializer for blockchain integration"""
    
    class Meta:
        model = TraceabilityRecord
        fields = [
            'id', 'stage', 'location', 'timestamp', 'processor',
            'notes', 'quality_metrics', 'environmental_data',
            'blockchain_hash', 'verification_status', 'images'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified product serializer for list views"""
    category = CategorySerializer(read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    image_url = serializers.ImageField(source='featured_image', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'seller_name', 'seller_username', 'product_type', 'organic_status',
            'price_per_unit', 'unit', 'minimum_order_quantity', 'stock_quantity',
            'origin_country', 'origin_region', 'quality_grade',
            'image_url', 'is_featured', 'status', 'views_count', 'orders_count',
            'created_at', 'updated_at'
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Detailed product serializer with all relationships"""
    category = CategorySerializer(read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    seller_country = serializers.CharField(source='seller.country', read_only=True)
    # images = ProductImageSerializer(many=True, read_only=True)
    # variations = ProductVariationSerializer(many=True, read_only=True)
    # certifications = CertificationSerializer(many=True, read_only=True)
    # traceability_records = TraceabilityRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'seller_name', 'seller_username', 'seller_country',
            'product_type', 'organic_status', 'price_per_unit', 'unit',
            'minimum_order_quantity', 'stock_quantity', 'harvest_date',
            'expiry_date', 'processing_date', 'origin_country', 'origin_region',
            'origin_city', 'quality_grade', 'certifications', 'featured_image',
            'additional_images', 'raw_materials', 'processing_method',
            'processing_facility', 'nutritional_info', 'status', 'is_featured',
            'search_keywords', 'views_count', 'orders_count', 'blockchain_hash',
            'blockchain_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'seller_name', 'seller_username', 'seller_country',
            'views_count', 'orders_count', 'created_at', 'updated_at'
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    """Product creation serializer with validation"""
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category_id', 'product_type', 'organic_status',
            'price_per_unit', 'unit', 'minimum_order_quantity', 'stock_quantity',
            'harvest_date', 'expiry_date', 'processing_date', 'origin_country',
            'origin_region', 'origin_city', 'quality_grade', 'featured_image',
            'raw_materials', 'processing_method', 'processing_facility',
            'nutritional_info', 'search_keywords'
        ]
    
    def validate_category_id(self, value):
        """Validate that category exists and is active"""
        try:
            category = Category.objects.get(id=value, is_active=True)
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category ID")
    
    def validate_price_per_unit(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock_quantity(self, value):
        """Validate stock quantity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value
    
    def validate(self, attrs):
        """Additional validation for product data"""
        # Check expiry date is after harvest date
        if attrs.get('harvest_date') and attrs.get('expiry_date'):
            if attrs['expiry_date'] <= attrs['harvest_date']:
                raise serializers.ValidationError("Expiry date must be after harvest date")
        
        # Check processing date for processed products
        if attrs.get('product_type') == 'processed':
            if not attrs.get('processing_date'):
                raise serializers.ValidationError("Processing date is required for processed products")
            if not attrs.get('processing_method'):
                raise serializers.ValidationError("Processing method is required for processed products")
        
        return attrs
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        validated_data['category'] = category
        return super().create(validated_data)
    
    class Meta:
        model = Certification
        fields = [
            'id', 'certification_name', 'certification_type',
            'issuing_body', 'certificate_number', 'issue_date',
            'expiry_date', 'certificate_url', 'is_verified'
        ]


class TraceabilityRecordSerializer(serializers.ModelSerializer):
    """Traceability record serializer for blockchain integration"""
    
    class Meta:
        model = TraceabilityRecord
        fields = [
            'id', 'stage', 'location', 'timestamp', 'processor',
            'notes', 'quality_metrics', 'environmental_data',
            'blockchain_hash', 'verification_status', 'images'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer with all relationships"""
    category = CategorySerializer(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    traceability_records = TraceabilityRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'seller',
            'sku', 'product_type', 'is_organic', 'base_price', 'currency',
            'stock_quantity', 'unit', 'weight_kg', 'origin_country',
            'origin_region', 'harvest_date', 'shelf_life_days',
            'storage_requirements', 'nutritional_info', 'tags',
            'is_available', 'is_featured', 'total_sales', 'average_rating',
            'images', 'variations', 'certifications', 'traceability_records',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'seller', 'total_sales', 'average_rating',
            'created_at', 'updated_at'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified product serializer for list views"""
    category = serializers.StringRelatedField(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'seller', 'product_type',
            'is_organic', 'base_price', 'currency', 'stock_quantity',
            'unit', 'origin_region', 'average_rating', 'primary_image',
            'is_available', 'is_featured'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image_url
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Product serializer for create/update operations"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'sku', 'product_type',
            'is_organic', 'base_price', 'currency', 'stock_quantity',
            'unit', 'weight_kg', 'origin_country', 'origin_region',
            'harvest_date', 'shelf_life_days', 'storage_requirements',
            'nutritional_info', 'tags', 'is_available', 'is_featured'
        ]
    
    def validate_sku(self, value):
        """Ensure SKU is unique"""
        if self.instance:
            # For updates, exclude current instance
            if Product.objects.exclude(id=self.instance.id).filter(sku=value).exists():
                raise serializers.ValidationError("Product with this SKU already exists.")
        else:
            # For new products
            if Product.objects.filter(sku=value).exists():
                raise serializers.ValidationError("Product with this SKU already exists.")
        return value
    
    def validate_base_price(self, value):
        """Ensure price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate_stock_quantity(self, value):
        """Ensure stock quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search parameters"""
    query = serializers.CharField(max_length=200, required=False)
    category = serializers.IntegerField(required=False)
    product_type = serializers.ChoiceField(
        choices=['raw', 'processed'], required=False
    )
    is_organic = serializers.BooleanField(required=False)
    origin_country = serializers.CharField(max_length=100, required=False)
    origin_region = serializers.CharField(max_length=100, required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    in_stock = serializers.BooleanField(required=False)
    is_featured = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['name', 'price', 'created_at', 'rating', 'sales'],
        required=False,
        default='created_at'
    )
    sort_order = serializers.ChoiceField(
        choices=['asc', 'desc'],
        required=False,
        default='desc'
    )
