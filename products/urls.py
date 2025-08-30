from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Custom endpoints
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('by-category/<int:category_id>/', views.ProductsByCategoryView.as_view(), name='products-by-category'),
    
    # Product variations
    path('<uuid:product_id>/variations/', views.ProductVariationListView.as_view(), name='product-variations'),
    path('variations/<uuid:variation_id>/', views.ProductVariationDetailView.as_view(), name='variation-detail'),
    
    # Product images
    path('<uuid:product_id>/images/', views.ProductImageListView.as_view(), name='product-images'),
    path('images/<uuid:image_id>/', views.ProductImageDetailView.as_view(), name='image-detail'),
    
    # Certifications
    path('certifications/', views.CertificationListView.as_view(), name='certifications'),
    path('<uuid:product_id>/certifications/', views.ProductCertificationView.as_view(), name='product-certifications'),
]
