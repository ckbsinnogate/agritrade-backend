"""
AgriConnect Warehouse Management URLs
Complete warehouse system API endpoints for agricultural supply chain management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'types', views.WarehouseTypeViewSet, basename='warehouse-type')
router.register(r'warehouses', views.WarehouseViewSet, basename='warehouse')
router.register(r'zones', views.WarehouseZoneViewSet, basename='warehouse-zone')
router.register(r'staff', views.WarehouseStaffViewSet, basename='warehouse-staff')
router.register(r'inventory', views.WarehouseInventoryViewSet, basename='warehouse-inventory')
router.register(r'movements', views.WarehouseMovementViewSet, basename='warehouse-movement')
router.register(r'temperature-logs', views.TemperatureLogViewSet, basename='temperature-log')
router.register(r'quality-inspections', views.QualityInspectionViewSet, basename='quality-inspection')
router.register(r'bookings', views.WarehouseBookingViewSet, basename='warehouse-booking')

app_name = 'warehouses'

urlpatterns = [
    # API root for warehouse management
    path('', views.warehouse_api_root, name='warehouse-api-root'),
    
    # Dashboard and analytics
    path('dashboard/', views.WarehouseDashboardView.as_view(), name='warehouse-dashboard'),
      # Inventory optimization
    path('inventory/optimize/', views.inventory_optimization, name='inventory-optimization'),
    path('optimization/', views.inventory_optimization, name='warehouse-optimization'),  # Alias for compatibility
    
    # Include router URLs
    path('', include(router.urls)),
]
