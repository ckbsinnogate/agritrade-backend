from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_simple as views

app_name = 'products'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    # API Root
    path('', views.products_api_root, name='products-root'),
    
    # ViewSet routes - removed 'api/' prefix to fix duplicate URL issue
    path('', include(router.urls)),
]
