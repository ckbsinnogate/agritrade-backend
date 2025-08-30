"""
AgriConnect API - Main URL Configuration
Africa's Premier Agricultural Commerce Platform

This URL configuration includes routes for:
- Dual Authentication (Phone/Email + OTP)
- Product Management with Blockchain Traceability
- Warehouse Management
- Escrow Payment System
- Orders and Reviews
- SMS/Communication Integration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from myapiproject.health import health_check

# Create main router for API endpoints
router = DefaultRouter()

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    AgriConnect API Root
    Africa's Premier Agricultural Commerce Platform
    """
    base_url = f"{request.scheme}://{request.get_host()}"
    
    return Response({
        'name': 'AgriConnect API',
        'version': '1.0',
        'description': 'Africa\'s Premier Agricultural Commerce Platform',
        'features': [
            'Dual Authentication (Phone/Email + OTP)',
            'Product Management with Blockchain Traceability', 
            'Warehouse Management',
            'Blockchain Traceability System',
            'Escrow Payment System',
            'Order Processing',
            'Review System',
            'Subscription & Membership System',
            'Advertisement & Marketing System',
            'SMS/Communication Integration',        'AI-Powered Agricultural Intelligence (OpenRouter Integration)'
        ],        'endpoints': {
            'authentication': f'{base_url}/api/v1/auth/',
            'users': f'{base_url}/api/v1/users/',
            'products': f'{base_url}/api/v1/products/',
            'orders': f'{base_url}/api/v1/orders/',
            'payments': f'{base_url}/api/v1/payments/',
            'financial': f'{base_url}/api/v1/financial/',
            'warehouses': f'{base_url}/api/v1/warehouses/',
            'reviews': f'{base_url}/api/v1/reviews/',
            'subscriptions': f'{base_url}/api/v1/subscriptions/',
            'advertisements': f'{base_url}/api/v1/advertisements/',
            'traceability': f'{base_url}/api/v1/traceability/',
            'ai_services': f'{base_url}/api/v1/ai/',
            'communications': f'{base_url}/api/v1/communications/',
            'processors': f'{base_url}/api/v1/processors/',
            'analytics': f'{base_url}/api/v1/analytics/',
        },
        'documentation': 'Visit individual endpoint roots for detailed API documentation',
        'status': 'Production Ready - All 12 modules operational',
        'health_check': f'{base_url}/api/v1/ai/health/',
        'admin_panel': f'{base_url}/admin/'
    })

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Health Check for DigitalOcean App Platform
    path('api/health/', health_check, name='health-check'),
    
    # API Root
    path('api/v1/', api_root, name='api-root'),
    
    # Legacy API Endpoints (without v1 prefix for backward compatibility)
    path('api/auth/', include(('authentication.urls', 'authentication'), namespace='api-auth')),
    path('api/products/', include(('products.urls_simple', 'products'), namespace='api-products')),
    path('api/orders/', include(('orders.urls', 'orders'), namespace='api-orders')),
    path('api/payments/', include(('payments.urls', 'payments'), namespace='api-payments')),
    path('api/ai/', include(('ai.urls', 'ai'), namespace='api-ai')),
    path('api/warehouses/', include(('warehouses.urls', 'warehouses'), namespace='api-warehouses')),
    path('api/traceability/', include(('traceability.urls', 'traceability'), namespace='api-traceability')),
    path('api/reviews/', include(('reviews.urls', 'reviews'), namespace='api-reviews')),
    path('api/subscriptions/', include(('subscriptions.urls', 'subscriptions'), namespace='api-subscriptions')),
    path('api/advertisements/', include(('advertisements.urls', 'advertisements'), namespace='api-advertisements')),
    path('api/communications/', include(('communications.urls', 'communications'), namespace='api-communications')),
    path('api/processors/', include(('processors.urls', 'processors'), namespace='api-processors')),    # API v1 Endpoints (preferred for new integrations)
    path('api/v1/auth/', include(('authentication.urls', 'authentication'), namespace='api-v1-auth')),
    path('api/v1/users/', include('users.urls', namespace='api-v1-users')),
    path('api/v1/products/', include(('products.urls_simple', 'products'), namespace='api-v1-products')),    path('api/v1/orders/', include(('orders.urls', 'orders'), namespace='api-v1-orders')),    path('api/v1/purchases/', include(('orders.urls', 'orders'), namespace='api-v1-purchases')),  # Institution purchases
    # path('api/v1/contracts/', include(('contracts.urls', 'contracts'), namespace='api-v1-contracts')),  # Contract management - temporarily disabled    path('api/v1/payments/', include(('payments.urls', 'payments'), namespace='api-v1-payments')),
    path('api/v1/financial/', include(('financial.urls', 'financial'), namespace='api-v1-financial')),  # Financial services API
    path('api/v1/processing/', include(('processing.urls', 'processing'), namespace='api-v1-processing')),  # Processing management API
    path('api/v1/ai/', include(('ai.urls', 'ai'), namespace='api-v1-ai')),
    path('api/v1/weather/', include(('weather.urls', 'weather'), namespace='api-v1-weather')),  # Weather services API
    # path('api/v1/sms/', include(('sms_urls', 'sms'), namespace='api-v1-sms')),  # Temporarily disabled
    path('api/v1/warehouses/', include(('warehouses.urls', 'warehouses'), namespace='api-v1-warehouses')),
    path('api/v1/traceability/', include(('traceability.urls', 'traceability'), namespace='api-v1-traceability')),
    # path('api/v1/blockchain/', include('blockchain.urls')),
    path('api/v1/reviews/', include(('reviews.urls', 'reviews'), namespace='api-v1-reviews')),
    path('api/v1/subscriptions/', include(('subscriptions.urls', 'subscriptions'), namespace='api-v1-subscriptions')),    path('api/v1/advertisements/', include(('advertisements.urls', 'advertisements'), namespace='api-v1-advertisements')),
    path('api/v1/communications/', include(('communications.urls', 'communications'), namespace='api-v1-communications')),    path('api/v1/processors/', include(('processors.urls', 'processors'), namespace='api-v1-processors')),  # Recipe sharing API
    path('api/v1/analytics/', include(('analytics.urls', 'analytics'), namespace='api-v1-analytics')),  # Analytics and Dashboard API
    path('api/v1/admin-dashboard/', include(('admin_dashboard.urls', 'admin_dashboard'), namespace='api-v1-admin-dashboard')),  # Administrator Dashboard Platform Overview & Management    path('api/v1/farmer-dashboard/', include(('farmer_dashboard.urls', 'farmer_dashboard'), namespace='api-v1-farmer-dashboard')),  # Farmer Dashboard comprehensive management system
    
    # Direct AI endpoints for frontend compatibility (no /api/ prefix)
    path('ai/', include(('ai.urls', 'ai'), namespace='direct-ai')),
    
    # DRF Router URLs (for ViewSet-based APIs)
    path('api/v1/router/', include(router.urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
