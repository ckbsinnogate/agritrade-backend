"""
AgriConnect Order Views
Complete order management system for agricultural commerce
"""

from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

from .models import (
    Order, OrderItem, OrderStatusHistory, ShippingMethod,
    OrderShipping, ProcessingOrder, OrderPayment
)
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderListSerializer,
    OrderItemSerializer, OrderStatusHistorySerializer,
    ShippingMethodSerializer, OrderShippingSerializer,
    CartSerializer, CartItemSerializer, OrderPaymentSerializer
)
from products.models import Product
from products.serializers import ProductListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders with advanced filtering and actions
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields
    search_fields = ['order_number', 'buyer__username', 'seller__username', 'delivery_city']
    
    # Ordering fields
    ordering_fields = ['order_date', 'total_amount', 'status', 'expected_delivery_date']
    ordering = ['-order_date']
    
    # Filter fields
    filterset_fields = {
        'status': ['exact'],
        'payment_status': ['exact'],
        'order_type': ['exact'],
        'delivery_country': ['exact'],
        'delivery_region': ['icontains'],
        'total_amount': ['gte', 'lte'],
        'order_date': ['gte', 'lte'],
        'expected_delivery_date': ['gte', 'lte'],
    }
    
    def get_queryset(self):
        """Filter orders based on user role"""
        user = self.request.user
        
        # Admin can see all orders
        if user.is_staff:
            return Order.objects.all().select_related('buyer', 'seller').prefetch_related('items__product')
        
        # Users can see their own orders (as buyer or seller)
        return Order.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('buyer', 'seller').prefetch_related('items__product')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        """Create order and handle inventory updates"""
        with transaction.atomic():
            order = serializer.save()
              # Create initial status history
            OrderStatusHistory.objects.create(
                order=order,
                status='pending',
                notes='Order created',
                updated_by=self.request.user
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        
        # Check permissions
        if order.seller != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        # Validate status
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status
        old_status = order.status
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
          # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes,
            updated_by=request.user
        )
        
        return Response({
            'message': f'Order status updated from {old_status} to {new_status}',
            'old_status': old_status,
            'new_status': new_status,
            'order_number': order.order_number
        })
    
    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        """Cancel order and restore inventory"""
        order = self.get_object()
        
        # Check permissions
        if order.buyer != request.user and order.seller != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Check if order can be cancelled
        if order.status in ['shipped', 'delivered', 'completed', 'cancelled']:
            return Response({
                'error': f'Cannot cancel order with status: {order.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cancellation_reason = request.data.get('reason', 'No reason provided')
        
        with transaction.atomic():
            # Restore inventory
            for item in order.items.all():
                product = item.product
                product.stock_quantity += item.quantity
                product.orders_count -= 1
                product.save(update_fields=['stock_quantity', 'orders_count'])
            
            # Update order status
            order.status = 'cancelled'
            order.save(update_fields=['status', 'updated_at'])
              # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                notes=f'Order cancelled. Reason: {cancellation_reason}',
                updated_by=request.user
            )
        
        return Response({
            'message': 'Order cancelled successfully',
            'order_number': order.order_number,
            'reason': cancellation_reason
        })
    
    @action(detail=False, methods=['get'])
    def my_purchases(self, request):
        """Get current user's purchase orders"""
        orders = self.get_queryset().filter(buyer=request.user)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_sales(self, request):
        """Get current user's sales orders"""
        orders = self.get_queryset().filter(seller=request.user)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get order statistics"""
        queryset = self.get_queryset()
        
        # Overall statistics
        stats = {
            'total_orders': queryset.count(),
            'total_value': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
            'average_order_value': queryset.aggregate(avg=Avg('total_amount'))['avg'] or 0,
        }
        
        # Status breakdown
        status_counts = queryset.values('status').annotate(count=Count('id'))
        stats['status_breakdown'] = {item['status']: item['count'] for item in status_counts}
        
        # Payment status breakdown
        payment_counts = queryset.values('payment_status').annotate(count=Count('id'))
        stats['payment_breakdown'] = {item['payment_status']: item['count'] for item in payment_counts}
        
        # Order type breakdown
        type_counts = queryset.values('order_type').annotate(count=Count('id'))
        stats['type_breakdown'] = {item['order_type']: item['count'] for item in type_counts}
        
        return Response(stats)


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for session-based cart management
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get current cart contents"""
        cart = request.session.get('cart', [])
        
        # Get product details for cart items
        cart_with_products = []
        total_amount = Decimal('0.00')
        
        for item in cart:
            try:
                product = Product.objects.get(id=item['product_id'], status='active')
                product_data = ProductListSerializer(product).data
                
                item_total = Decimal(str(item['quantity'])) * product.price_per_unit
                total_amount += item_total
                
                cart_with_products.append({
                    'product': product_data,
                    'quantity': item['quantity'],
                    'unit_price': product.price_per_unit,
                    'total_price': item_total,
                    'quality_specifications': item.get('quality_specifications', {}),
                    'processing_requirements': item.get('processing_requirements', {})
                })
            except Product.DoesNotExist:
                # Remove invalid products from cart
                cart.remove(item)
                request.session['cart'] = cart
        
        return Response({
            'items': cart_with_products,
            'total_items': len(cart_with_products),
            'total_amount': total_amount
        })
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart = request.session.get('cart', [])
            
            # Check if product already in cart
            product_id = str(serializer.validated_data['product_id'])
            existing_item = None
            for item in cart:
                if item['product_id'] == product_id:
                    existing_item = item
                    break
            
            if existing_item:
                # Update quantity
                existing_item['quantity'] = float(serializer.validated_data['quantity'])
                existing_item['quality_specifications'] = serializer.validated_data.get('quality_specifications', {})
                existing_item['processing_requirements'] = serializer.validated_data.get('processing_requirements', {})
            else:
                # Add new item
                cart.append({
                    'product_id': product_id,
                    'quantity': float(serializer.validated_data['quantity']),
                    'quality_specifications': serializer.validated_data.get('quality_specifications', {}),
                    'processing_requirements': serializer.validated_data.get('processing_requirements', {})
                })
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return Response({'message': 'Item added to cart'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['product_id'] != str(product_id)]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return Response({'message': 'Item removed from cart'})
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear cart"""
        request.session['cart'] = []
        request.session.modified = True
        
        return Response({'message': 'Cart cleared'})
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Convert cart to order"""
        cart = request.session.get('cart', [])
        if not cart:
            return Response({'error': 'Cart is empty'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare order data
        order_data = request.data.copy()
        order_data['items'] = []
        
        # Convert cart items to order items
        for item in cart:
            order_data['items'].append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'quality_specifications': item.get('quality_specifications', {}),
                'processing_requirements': item.get('processing_requirements', {})
            })
        
        # Create order
        serializer = OrderCreateSerializer(data=order_data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            
            # Clear cart after successful order
            request.session['cart'] = []
            request.session.modified = True
            
            return Response({
                'message': 'Order created successfully',
                'order_id': order.id,
                'order_number': order.order_number
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing shipping methods
    """
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def orders_api_root(request, format=None):
    """
    Orders API Root - Complete Order Management System
    
    AgriConnect Order Management API provides comprehensive order processing
    capabilities for Africa's premier agricultural commerce platform.
    """
    return Response({
        'message': 'AgriConnect Orders API v3.0 - Complete Order Management',
        'description': 'Africa\'s premier agricultural commerce platform - Order Management System',
        'version': '3.0.0',
        'features': [
            'Complete order lifecycle management',
            'Session-based cart system',
            'Inventory synchronization',
            'Order status tracking',
            'Payment integration ready',
            'Shipping management',
            'Bulk order support'
        ],
        'endpoints': {
            'orders': {
                'url': '/api/v1/orders/',
                'methods': ['GET', 'POST'],
                'description': 'Manage orders - create, view, update',
                'features': [
                    'Advanced filtering and search',
                    'Order status management', 
                    'Inventory auto-update',
                    'Cancellation with stock restoration'
                ]
            },
            'cart': {
                'url': '/api/v1/orders/cart/',
                'methods': ['GET', 'POST'],
                'description': 'Session-based shopping cart',
                'actions': [
                    'add_item/', 'remove_item/', 
                    'clear/', 'checkout/'
                ]
            },
            'my_orders': {
                'purchases': '/api/v1/orders/my_purchases/',
                'sales': '/api/v1/orders/my_sales/',
                'description': 'User-specific order views'
            },
            'order_actions': {
                'update_status': '/api/v1/orders/{id}/update_status/',
                'cancel_order': '/api/v1/orders/{id}/cancel_order/',
                'description': 'Order management actions'
            },
            'statistics': {
                'url': '/api/v1/orders/statistics/',
                'description': 'Order analytics and metrics'
            },
            'shipping': {
                'url': '/api/v1/orders/shipping-methods/',
                'description': 'Available shipping options'
            }
        },
        'order_workflow': {
            '1_cart_management': 'Add products to session-based cart',
            '2_checkout': 'Convert cart to order with validation',
            '3_payment': 'Process payment (Paystack/Flutterwave ready)',
            '4_fulfillment': 'Seller processes and ships order',
            '5_tracking': 'Real-time status updates',
            '6_completion': 'Delivery confirmation and payment release'
        },
        'sample_requests': {
            'add_to_cart': {
                'url': 'POST /api/v1/orders/cart/add_item/',
                'data': {
                    'product_id': 'product-uuid',
                    'quantity': 10.5,
                    'quality_specifications': {'grade': 'A'},
                    'processing_requirements': {'method': 'organic'}
                }
            },
            'create_order': {
                'url': 'POST /api/v1/orders/cart/checkout/',
                'data': {
                    'order_type': 'regular',
                    'delivery_address': '123 Farm Road',
                    'delivery_city': 'Accra',
                    'delivery_region': 'Greater Accra',
                    'delivery_country': 'Ghana',
                    'delivery_phone': '+233123456789'
                }
            },
            'update_status': {
                'url': 'POST /api/v1/orders/{order_id}/update_status/',
                'data': {
                    'status': 'shipped',
                    'notes': 'Order shipped via DHL'
                }
            }
        },
        'integration_ready': {
            'payment_gateways': ['Paystack', 'Flutterwave', 'Mobile Money'],
            'inventory_sync': 'Real-time stock updates',
            'notifications': 'SMS/Email alerts ready',
            'logistics': 'Shipping partner integration'
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def purchases_api_root(request, format=None):
    """
    Purchases API Root - Institution Purchase Management
    """
    return Response({
        'name': 'AgriConnect Purchases API',
        'version': '1.0',
        'description': 'Institution purchase management and analytics',
        'endpoints': {
            'purchases': '/api/v1/purchases/',
            'purchase_analytics': '/api/v1/purchases/analytics/',
            'bulk_purchases': '/api/v1/purchases/bulk/',
            'recurring_purchases': '/api/v1/purchases/recurring/',
        },
        'status': 'Purchases system operational for institutions'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_statistics(request):
    """Get order statistics - frontend compatibility endpoint"""
    try:
        # Use the same logic as OrderViewSet.statistics action
        orders = Order.objects.all()
        
        # Filter by user if not admin
        if not (request.user.is_staff or request.user.is_superuser):
            # Allow farmers to see stats for their products' orders
            if hasattr(request.user, 'roles') and 'FARMER' in request.user.roles:
                orders = orders.filter(
                    Q(buyer=request.user) |
                    Q(orderitem__product__seller=request.user)
                ).distinct()
            else:
                orders = orders.filter(buyer=request.user)
        
        # Overall statistics
        stats = {
            'total_orders': orders.count(),
            'total_value': orders.aggregate(total=Sum('total_amount'))['total'] or 0,
            'average_order_value': orders.aggregate(avg=Avg('total_amount'))['avg'] or 0,
        }
        
        # Status breakdown
        status_counts = orders.values('status').annotate(count=Count('id'))
        stats['status_breakdown'] = {item['status']: item['count'] for item in status_counts}
        
        # Payment status breakdown
        payment_counts = orders.values('payment_status').annotate(count=Count('id'))
        stats['payment_breakdown'] = {item['payment_status']: item['count'] for item in payment_counts}
        
        # Order type breakdown
        type_counts = orders.values('order_type').annotate(count=Count('id'))
        stats['type_breakdown'] = {item['order_type']: item['count'] for item in type_counts}
        
        # Recent orders (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_orders = orders.filter(created_at__gte=thirty_days_ago)
        stats['recent_orders_count'] = recent_orders.count()
        
        return Response({
            'status': 'success',
            'data': stats,
            'message': 'Order statistics retrieved successfully'
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch order statistics',
            'message': str(e),
            'data': {},
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_purchases(request):
    """Get institution purchases - compatible with frontend expectations"""
    try:
        # Get user's orders (purchases from their perspective)
        user_orders = Order.objects.filter(user=request.user)
        
        # Filter by order type if needed
        order_type = request.GET.get('order_type')
        if order_type:
            user_orders = user_orders.filter(order_type=order_type)
        
        # Calculate summary statistics
        total_purchases = user_orders.count()
        total_amount = user_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Recent purchases (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_purchases = user_orders.filter(created_at__gte=thirty_days_ago).count()
        recent_amount = user_orders.filter(created_at__gte=thirty_days_ago).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Status breakdown
        status_breakdown = {}
        for status_choice in Order.STATUS_CHOICES:
            status_code = status_choice[0]
            count = user_orders.filter(status=status_code).count()
            status_breakdown[status_code] = count
        
        # Recent purchase items
        recent_orders = user_orders.order_by('-created_at')[:10]
        serializer = OrderSerializer(recent_orders, many=True)
        
        return Response({
            'success': True,
            'summary': {
                'total_purchases': total_purchases,
                'total_amount': float(total_amount),
                'recent_purchases_30d': recent_purchases,
                'recent_amount_30d': float(recent_amount),
                'status_breakdown': status_breakdown
            },
            'recent_purchases': serializer.data,
            'pagination': {
                'count': total_purchases,
                'page': 1,
                'page_size': 10
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
