"""
AgriConnect Order Serializers
Complete order management system for agricultural commerce
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import (
    Order, OrderItem, OrderStatusHistory, ShippingMethod, 
    OrderShipping, ProcessingOrder, OrderPayment
)
from products.models import Product
from products.serializers import ProductListSerializer

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_id', 'product_variation',
            'quantity', 'unit_price', 'total_price',
            'product_name', 'product_description', 'unit',
            'quality_specifications', 'processing_requirements',
            'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']

    def validate_product_id(self, value):
        """Validate that product exists and is available"""
        try:
            product = Product.objects.get(id=value, status='active')
            if product.stock_quantity <= 0:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")

    def validate_quantity(self, value):
        """Validate quantity against minimum order and stock"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order items"""
    product_id = serializers.UUIDField()
    
    class Meta:
        model = OrderItem
        fields = [
            'product_id', 'quantity', 'quality_specifications', 
            'processing_requirements'
        ]

    def validate(self, attrs):
        """Validate order item data"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        
        try:
            product = Product.objects.get(id=product_id, status='active')
            
            # Check minimum order quantity
            if quantity < product.minimum_order_quantity:
                raise serializers.ValidationError(
                    f"Minimum order quantity is {product.minimum_order_quantity} {product.unit}"
                )
            
            # Check stock availability
            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Only {product.stock_quantity} {product.unit} available in stock"
                )
            
            # Store product data for order item creation
            attrs['product'] = product
            attrs['unit_price'] = product.price_per_unit
            attrs['total_price'] = quantity * product.price_per_unit
            attrs['product_name'] = product.name
            attrs['product_description'] = product.description
            attrs['unit'] = product.unit
            
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        return attrs


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history"""
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'timestamp', 'updated_by']
        read_only_fields = ['id', 'timestamp', 'updated_by']


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods"""
    
    class Meta:
        model = ShippingMethod
        fields = [
            'id', 'name', 'description', 'base_cost', 'cost_per_kg',
            'estimated_days_min', 'estimated_days_max', 'is_active', 
            'available_countries', 'available_regions'
        ]


class OrderShippingSerializer(serializers.ModelSerializer):
    """Serializer for order shipping details"""
    shipping_method = ShippingMethodSerializer(read_only=True)
    
    class Meta:
        model = OrderShipping
        fields = [
            'id', 'shipping_method', 'tracking_number', 'carrier',
            'shipped_at', 'estimated_delivery', 'actual_delivery',
            'weight', 'dimensions'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Simplified order serializer for list views"""
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_type', 'status', 'payment_status',
            'buyer_name', 'seller_name', 'total_amount', 'currency',
            'items_count', 'order_date', 'expected_delivery_date'
        ]
    
    def get_items_count(self, obj):
        """Get number of items in order"""
        return obj.items.count()


class OrderSerializer(serializers.ModelSerializer):
    """Detailed order serializer"""
    buyer = serializers.StringRelatedField(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    shipping = OrderShippingSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_type', 'buyer', 'seller',
            'status', 'payment_status', 'subtotal', 'tax_amount',
            'shipping_cost', 'discount_amount', 'total_amount', 'currency',
            'delivery_address', 'delivery_city', 'delivery_region',
            'delivery_country', 'delivery_phone', 'order_date',
            'expected_delivery_date', 'actual_delivery_date',
            'buyer_notes', 'seller_notes', 'special_instructions',
            'tracking_number', 'logistics_partner', 'contract_details',
            'delivery_schedule', 'quality_requirements',
            'quality_inspection_passed', 'items', 'status_history',
            'shipping', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'buyer', 'seller', 'items',
            'status_history', 'shipping', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = OrderItemCreateSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'order_type', 'seller_id', 'delivery_address', 'delivery_city',
            'delivery_region', 'delivery_country', 'delivery_phone',
            'expected_delivery_date', 'buyer_notes', 'special_instructions',
            'quality_requirements', 'items'
        ]
    
    def validate_seller_id(self, value):
        """Validate seller exists"""
        try:
            seller = User.objects.get(id=value)
            return seller
        except User.DoesNotExist:
            raise serializers.ValidationError("Seller not found")
    
    def validate_items(self, value):
        """Validate order items"""
        if not value:
            raise serializers.ValidationError("At least one item is required")
        
        # Check if all items are from the same seller
        sellers = set()
        for item_data in value:
            try:
                product = Product.objects.get(id=item_data['product_id'])
                sellers.add(product.seller_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError("One or more products not found")
        
        if len(sellers) > 1:
            raise serializers.ValidationError("All items must be from the same seller")
        
        return value
    
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop('items')
        seller_id = validated_data.pop('seller_id')
        
        # Create the order
        order = Order.objects.create(
            buyer=self.context['request'].user,
            seller_id=seller_id,
            **validated_data
        )
        
        # Create order items and calculate totals
        subtotal = 0
        for item_data in items_data:
            product = item_data.pop('product')
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                **item_data
            )
            subtotal += order_item.total_price
            
            # Update product stock
            product.stock_quantity -= order_item.quantity
            product.orders_count += 1
            product.save(update_fields=['stock_quantity', 'orders_count'])
        
        # Update order totals
        order.subtotal = subtotal
        order.total_amount = subtotal + order.tax_amount + order.shipping_cost - order.discount_amount
        order.save(update_fields=['subtotal', 'total_amount'])
        
        return order


class CartItemSerializer(serializers.Serializer):
    """Serializer for cart items (session-based)"""
    product_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    quality_specifications = serializers.JSONField(required=False, default=dict)
    processing_requirements = serializers.JSONField(required=False, default=dict)
    
    def validate_product_id(self, value):
        """Validate product exists and is available"""
        try:
            product = Product.objects.get(id=value, status='active')
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")
    
    def validate(self, attrs):
        """Validate cart item"""
        try:
            product = Product.objects.get(id=attrs['product_id'])
            quantity = attrs['quantity']
            
            # Check minimum order quantity
            if quantity < product.minimum_order_quantity:
                raise serializers.ValidationError(
                    f"Minimum order quantity is {product.minimum_order_quantity} {product.unit}"
                )
            
            # Check stock availability
            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Only {product.stock_quantity} {product.unit} available in stock"
                )
            
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        return attrs


class CartSerializer(serializers.Serializer):
    """Serializer for cart management"""
    items = CartItemSerializer(many=True)
    
    def validate_items(self, value):
        """Validate cart items"""
        if not value:
            raise serializers.ValidationError("Cart cannot be empty")
        
        # Check for duplicate products
        product_ids = [item['product_id'] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products in cart")
        
        return value


class OrderPaymentSerializer(serializers.ModelSerializer):
    """Serializer for order payments"""
    
    class Meta:
        model = OrderPayment
        fields = [
            'id', 'payment_method', 'transaction_id', 'amount',
            'currency', 'status', 'gateway_response', 'initiated_at',
            'completed_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'gateway_response', 'initiated_at']
