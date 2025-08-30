"""
AgriConnect Processing URLs
URL configuration for processing management API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'equipment', views.ProcessingEquipmentViewSet, basename='processing-equipment')
router.register(r'schedule', views.ProcessingScheduleViewSet, basename='processing-schedule')
router.register(r'quality-checks', views.ProcessingQualityCheckViewSet, basename='processing-quality-checks')
router.register(r'stats', views.ProcessingStatsViewSet, basename='processing-stats')

app_name = 'processing'

urlpatterns = [
    # API Root
    path('', views.processing_api_root, name='processing-api-root'),
    
    # Processing orders endpoint (for frontend compatibility)
    path('orders/', views.processing_orders, name='processing-orders'),
    
    # Include router URLs
    path('', include(router.urls)),
]