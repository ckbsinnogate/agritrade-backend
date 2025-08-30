"""
AgriConnect Product Views - Enhanced Version
Advanced product management system with filtering and search
"""

from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Min, Max
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer, ProductCreateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories with search
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing agricultural products with advanced filtering
    """
    queryset = Product.objects.filter(status='active').select_related('category', 'seller')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields
    search_fields = ['name', 'description', 'category__name', 'origin_region', 'origin_city']
    
    # Ordering fields
    ordering_fields = ['name', 'price_per_unit', 'created_at', 'views_count', 'orders_count']
    ordering = ['-created_at']
    
    # Filter fields
    filterset_fields = {
        'product_type': ['exact'],
        'organic_status': ['exact'],
        'category': ['exact'],
        'origin_country': ['exact'],
        'origin_region': ['icontains'],
        'price_per_unit': ['gte', 'lte'],
        'is_featured': ['exact'],
        'quality_grade': ['exact'],
        'unit': ['exact'],
        }
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Enhanced queryset with custom filtering"""
        queryset = super().get_queryset()
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(stock_quantity__gt=0)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(stock_quantity=0)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price is not None:
            queryset = queryset.filter(price_per_unit__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price_per_unit__lte=max_price)
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller', None)
        if seller_id is not None:
            queryset = queryset.filter(seller__id=seller_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the seller to the current user"""
        # The serializer's create method handles category_id conversion
        # We just need to set the seller
        serializer.save(seller=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment view count"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(featured_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def organic(self, request):
        """Get organic products"""
        organic_products = self.get_queryset().filter(organic_status='organic')
        page = self.paginate_queryset(organic_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(organic_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get products grouped by category"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            products = self.get_queryset().filter(category=category)
            page = self.paginate_queryset(products)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(products, many=True)
            return Response({
                'category': CategorySerializer(category).data,
                'products': serializer.data
            })
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def statistics(self, request):
        """Get product statistics and analytics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_products': queryset.count(),
            'organic_products': queryset.filter(organic_status='organic').count(),
            'featured_products': queryset.filter(is_featured=True).count(),
            'in_stock_products': queryset.filter(stock_quantity__gt=0).count(),
            'categories_count': Category.objects.filter(is_active=True).count(),
            'price_range': {
                'min': queryset.aggregate(Min('price_per_unit'))['price_per_unit__min'],
                'max': queryset.aggregate(Max('price_per_unit'))['price_per_unit__max'],
                'avg': queryset.aggregate(Avg('price_per_unit'))['price_per_unit__avg'],
            },
            'by_category': Category.objects.filter(is_active=True).annotate(
                product_count=Count('products', filter=Q(products__status='active'))
            ).values('id', 'name', 'product_count'),
            'by_organic_status': queryset.values('organic_status').annotate(
                count=Count('id')
            ),
            'by_product_type': queryset.values('product_type').annotate(
                count=Count('id')
            ),
            'top_viewed': queryset.order_by('-views_count')[:5].values(
                'id', 'name', 'views_count'
            ),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get current user's products"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        user_products = self.get_queryset().filter(seller=request.user)
        page = self.paginate_queryset(user_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(user_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock quantity"""
        product = self.get_object()
        
        if product.seller != request.user:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        new_stock = request.data.get('stock_quantity')
        action_type = request.data.get('action', 'set')  # 'set', 'add', 'subtract'
        
        if new_stock is None:
            return Response({'error': 'stock_quantity is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_stock = float(new_stock)
            if new_stock < 0:
                return Response({'error': 'Stock quantity cannot be negative'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            old_stock = float(product.stock_quantity)
            
            if action_type == 'add':
                product.stock_quantity = old_stock + new_stock
            elif action_type == 'subtract':
                if old_stock < new_stock:
                    return Response({'error': 'Insufficient stock'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                product.stock_quantity = old_stock - new_stock
            else:  # 'set'
                product.stock_quantity = new_stock
            
            product.save(update_fields=['stock_quantity', 'updated_at'])
            
            return Response({
                'message': 'Stock updated successfully',
                'old_stock': old_stock,
                'new_stock': float(product.stock_quantity),
                'action': action_type
            })
            
        except (ValueError, TypeError):
            return Response({'error': 'Invalid stock quantity'}, 
                          status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status of a product"""
        product = self.get_object()
        
        if product.seller != request.user:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        product.is_featured = not product.is_featured
        product.save(update_fields=['is_featured', 'updated_at'])
        
        return Response({
            'message': f'Product {"featured" if product.is_featured else "unfeatured"}',
            'is_featured': product.is_featured
        })

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change product status"""
        product = self.get_object()
        
        if product.seller != request.user:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        valid_statuses = ['draft', 'active', 'out_of_stock', 'discontinued']
        
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = product.status
        product.status = new_status
        product.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'message': f'Product status changed from {old_status} to {new_status}',
            'old_status': old_status,
            'new_status': new_status
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def products_api_root(request, format=None):
    """
    Products API Root - Enhanced with Inventory Management
    """
    return Response({
        'message': 'AgriConnect Products API',
        'version': '2.1',
        'endpoints': {
            'categories': '/api/v1/products/categories/',
            'products': '/api/v1/products/products/',
            'featured_products': '/api/v1/products/products/featured/',
            'organic_products': '/api/v1/products/products/organic/',
            'products_by_category': '/api/v1/products/products/by_category/?category_id={id}',
            'product_statistics': '/api/v1/products/products/statistics/',
            'my_products': '/api/v1/products/products/my_products/',
        },
        'inventory_management': {
            'update_stock': 'POST /api/v1/products/products/{id}/update_stock/',
            'toggle_featured': 'POST /api/v1/products/products/{id}/toggle_featured/',
            'change_status': 'POST /api/v1/products/products/{id}/change_status/',
        },
        'search_features': {
            'search': 'Use ?search={query} to search products',
            'filters': 'Available filters: product_type, organic_status, category, origin_region, price_per_unit, in_stock',
            'ordering': 'Use ?ordering={field} to sort. Available: name, price_per_unit, created_at, views_count',
            'pagination': 'Results are paginated. Use ?page={number} and ?page_size={size}'
        },
        'examples': {
            'search_rice': '/api/v1/products/products/?search=rice',
            'organic_products': '/api/v1/products/products/?organic_status=organic',
            'price_range': '/api/v1/products/products/?min_price=2.00&max_price=10.00',
            'in_stock_only': '/api/v1/products/products/?in_stock=true',
            'by_category': '/api/v1/products/products/?category=1',
            'sort_by_price': '/api/v1/products/products/?ordering=price_per_unit',
            'inventory_update': 'POST with {"stock_quantity": 50, "action": "add"}'
        },
        'status': 'Advanced product management with inventory control, filtering, search, and analytics'
    })
