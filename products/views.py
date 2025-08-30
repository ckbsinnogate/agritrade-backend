"""
AgriConnect Product Views
Complete product management system for Africa's agricultural commerce platform
"""

from rest_framework import viewsets, generics, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Avg
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product, ProductVariation, ProductImage, Certification, TraceabilityRecord
from .serializers import (
    CategorySerializer, ProductSerializer, ProductCreateSerializer, ProductListSerializer,
    ProductVariationSerializer, ProductImageSerializer, CertificationSerializer,
    TraceabilityRecordSerializer
)

import logging
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for product lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories
    Supports hierarchical categories for agricultural products
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter categories based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by parent category
        parent_id = self.request.query_params.get('parent', None)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif self.request.query_params.get('root_only', None):
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in this category"""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            status='active'
        ).select_related('seller', 'category')
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing agricultural products
    Supports both raw and processed agricultural goods
    """
    queryset = Product.objects.filter(status='active')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'search_keywords']
    ordering_fields = ['price_per_unit', 'created_at', 'views_count', 'orders_count']
    filterset_fields = ['category', 'product_type', 'organic_status', 'origin_country', 'seller']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Filter products based on query parameters"""
        queryset = super().get_queryset().select_related('seller', 'category')
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price:
            queryset = queryset.filter(price_per_unit__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_unit__lte=max_price)
        
        # Location filtering
        region = self.request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(origin_region__icontains=region)
        
        # Featured products
        if self.request.query_params.get('featured', None):
            queryset = queryset.filter(is_featured=True)
        
        # Only show seller's own products for certain actions
        if self.action in ['update', 'partial_update', 'destroy']:
            if not self.request.user.is_staff:
                queryset = queryset.filter(seller=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the seller to the current user and generate slug"""
        slug = slugify(serializer.validated_data['name'])
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        serializer.save(seller=self.request.user, slug=slug)
        logger.info(f"Product created: {serializer.instance.name} by {self.request.user.username}")
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when product is retrieved"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def variations(self, request, pk=None):
        """Get all variations for this product"""
        product = self.get_object()
        variations = ProductVariation.objects.filter(product=product, is_available=True)
        serializer = ProductVariationSerializer(variations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """Get all images for this product"""
        product = self.get_object()
        images = ProductImage.objects.filter(product=product).order_by('sort_order')
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def traceability(self, request, pk=None):
        """Get traceability records for this product"""
        product = self.get_object()
        records = TraceabilityRecord.objects.filter(product=product).order_by('-created_at')
        serializer = TraceabilityRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin users can feature products'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        product = self.get_object()
        product.is_featured = not product.is_featured
        product.save(update_fields=['is_featured'])
        
        return Response({
            'message': f'Product {"featured" if product.is_featured else "unfeatured"} successfully',
            'is_featured': product.is_featured
        })


class ProductSearchView(generics.ListAPIView):
    """
    Advanced product search with filtering and sorting
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Custom search functionality"""
        queryset = Product.objects.filter(status='active').select_related('seller', 'category')
        
        # Search query
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(search_keywords__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Apply additional filters
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        product_type = self.request.query_params.get('type', None)
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        organic_status = self.request.query_params.get('organic', None)
        if organic_status:
            queryset = queryset.filter(organic_status=organic_status)
        
        # Sorting
        sort_by = self.request.query_params.get('sort', 'created_at')
        if sort_by in ['price_per_unit', 'created_at', 'views_count', 'orders_count', 'name']:
            order = '-' + sort_by if self.request.query_params.get('order', 'desc') == 'desc' else sort_by
            queryset = queryset.order_by(order)
        
        return queryset


class FeaturedProductsView(generics.ListAPIView):
    """
    Get featured products for homepage display
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Product.objects.filter(
            status='active',
            is_featured=True
        ).select_related('seller', 'category').order_by('-created_at')[:10]


class ProductsByCategoryView(generics.ListAPIView):
    """
    Get products by category with pagination
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(
            category_id=category_id,
            status='active'
        ).select_related('seller', 'category').order_by('-created_at')


class ProductVariationListView(generics.ListCreateAPIView):
    """
    List and create product variations
    """
    serializer_class = ProductVariationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductVariation.objects.filter(
            product_id=product_id,
            is_available=True
        ).order_by('sort_order')
    
    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user owns the product
        if product.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only add variations to your own products")
        
        serializer.save(product=product)


class ProductVariationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a product variation
    """
    serializer_class = ProductVariationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'
    lookup_url_kwarg = 'variation_id'
    
    def get_queryset(self):
        return ProductVariation.objects.all()
    
    def perform_update(self, serializer):
        # Check ownership
        variation = self.get_object()
        if variation.product.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only update your own product variations")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        # Check ownership
        if instance.product.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only delete your own product variations")
        
        # Soft delete
        instance.is_available = False
        instance.save()


class ProductImageListView(generics.ListCreateAPIView):
    """
    List and upload product images
    """
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductImage.objects.filter(product_id=product_id).order_by('sort_order')
    
    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        
        # Check ownership
        if product.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only add images to your own products")
        
        serializer.save(product=product)


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a product image
    """
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'
    lookup_url_kwarg = 'image_id'
    
    def get_queryset(self):
        return ProductImage.objects.all()
    
    def perform_update(self, serializer):
        # Check ownership
        image = self.get_object()
        if image.product.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only update your own product images")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        # Check ownership
        if instance.product.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only delete your own product images")
        
        instance.delete()


class CertificationListView(generics.ListCreateAPIView):
    """
    List and create certifications
    """
    queryset = Certification.objects.filter(is_active=True)
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductCertificationView(generics.ListCreateAPIView):
    """
    Manage product certifications
    """
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        return product.certifications.filter(is_active=True)


# API Root for products
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def products_api_root(request, format=None):
    """
    Products API Root
    Provides links to all product endpoints
    """
    return Response({
        'message': 'AgriConnect Products API',
        'version': '1.0',
        'endpoints': {
            'categories': '/api/v1/products/categories/',
            'products': '/api/v1/products/products/',
            'search': '/api/v1/products/search/',
            'featured': '/api/v1/products/featured/',
        },
        'documentation': {
            'categories': 'GET /categories/ to list all categories, POST to create (auth required)',
            'products': 'GET /products/ to list all products, POST to create (auth required)',
            'search': 'GET /search/?q=query to search products',
            'featured': 'GET /featured/ to get featured products',
        },
        'filtering': {
            'by_category': 'GET /products/?category=<id>',
            'by_type': 'GET /products/?product_type=raw|processed',
            'by_organic': 'GET /products/?organic_status=organic|non_organic',
            'by_price': 'GET /products/?min_price=<amount>&max_price=<amount>',
            'by_location': 'GET /products/?region=<region_name>',
        },
        'sorting': {
            'by_price': 'GET /products/?ordering=price_per_unit|-price_per_unit',
            'by_date': 'GET /products/?ordering=created_at|-created_at',
            'by_popularity': 'GET /products/?ordering=views_count|-views_count',
        }
    })
