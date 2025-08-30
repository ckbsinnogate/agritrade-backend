"""
AgriConnect Order URLs
URL patterns for complete order management system
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'shipping-methods', views.ShippingMethodViewSet, basename='shipping-method')

app_name = 'orders'

urlpatterns = [
    # API root for orders
    path('', views.orders_api_root, name='orders-api-root'),
    
    # Statistics endpoint (frontend compatibility)
    path('statistics/', views.order_statistics, name='order-statistics'),
    
    # Purchases API endpoints (for institution dashboard)
    path('purchases/', views.purchases_api_root, name='purchases-api-root'),
    path('purchases/list/', views.get_purchases, name='get-purchases'),
    
    # Include router URLs
    path('', include(router.urls)),
]
