"""
Farmer Dashboard URLs
URL patterns for farmer dashboard backend APIs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'preferences', views.FarmerDashboardPreferencesViewSet, basename='farmer-preferences')
router.register(r'alerts', views.FarmerAlertViewSet, basename='farmer-alerts')
router.register(r'goals', views.FarmerGoalViewSet, basename='farmer-goals')
router.register(r'metrics', views.FarmerDashboardMetricsViewSet, basename='farmer-metrics')

app_name = 'farmer_dashboard'

urlpatterns = [
    # ======================== MAIN DASHBOARD ENDPOINT ========================
    path('', views.farmer_dashboard_api_root, name='farmer-dashboard-root'),
    
    # ======================== CORE DASHBOARD SECTIONS ========================
    # Dashboard Overview - Main dashboard with all statistics
    path('overview/', views.FarmerDashboardOverviewView.as_view(), name='farmer-dashboard-overview'),
    
    # Add Product - Redirect to existing products API (documented for frontend)
    # POST /api/v1/products/api/products/ with farmer authentication
    
    # My Products - Farmer-specific product management
    path('products/', views.FarmerProductsView.as_view(), name='farmer-dashboard-products'),
    
    # Orders - Order management for farmers (sales)
    path('orders/', views.FarmerOrdersView.as_view(), name='farmer-dashboard-orders'),
    
    # Weather - Weather insights and forecasting
    path('weather/', views.FarmerWeatherView.as_view(), name='farmer-dashboard-weather'),
    
    # Market Insights - AI-powered market analysis
    path('market-insights/', views.FarmerMarketInsightsView.as_view(), name='farmer-dashboard-market-insights'),
    
    # My Farms - Farm registration and management
    path('farms/', views.FarmerFarmsView.as_view(), name='farmer-dashboard-farms'),
    
    # ======================== ROUTER URLS ========================
    # Include all ViewSet URLs (preferences, alerts, goals, metrics)
    path('', include(router.urls)),
]

"""
Farmer Dashboard URL Pattern Summary:

MAIN DASHBOARD:
- GET /farmer-dashboard/ - Main dashboard API root with endpoint documentation

CORE SECTIONS (Required by Frontend):
- GET /farmer-dashboard/overview/ - Complete farmer dashboard overview with all metrics
- GET /farmer-dashboard/products/ - Farmer's products with sales analytics
- GET /farmer-dashboard/orders/ - Farmer's orders (sales) management
- GET /farmer-dashboard/weather/ - Weather insights and alerts
- GET /farmer-dashboard/market-insights/ - AI-powered market analysis
- GET /farmer-dashboard/farms/ - Farmer's registered farms

ADD PRODUCT SECTION:
- Use existing: POST /api/v1/products/api/products/ (with farmer authentication)
- Update stock: POST /api/v1/products/api/products/{id}/update_stock/
- Toggle featured: POST /api/v1/products/api/products/{id}/toggle_featured/
- Change status: POST /api/v1/products/api/products/{id}/change_status/

DASHBOARD MANAGEMENT:
- CRUD /farmer-dashboard/preferences/ - Dashboard preferences and settings
- CRUD /farmer-dashboard/alerts/ - Farmer alerts and notifications
- CRUD /farmer-dashboard/goals/ - Farmer goals and targets
- READ /farmer-dashboard/metrics/ - Dashboard metrics (auto-generated)

ADDITIONAL ENDPOINTS:
- POST /farmer-dashboard/alerts/{id}/mark_read/ - Mark alert as read
- POST /farmer-dashboard/alerts/mark_all_read/ - Mark all alerts as read
- POST /farmer-dashboard/goals/{id}/update_progress/ - Update goal progress

INTEGRATION WITH EXISTING APIS:
- Products API: /api/v1/products/api/products/ (for Add Product functionality)
- Orders API: /api/v1/orders/orders/my_sales/ (alternative endpoint)
- Farms API: /api/v1/traceability/farms/ (for farm management)
- AI API: /api/v1/ai/ (for market insights and crop advice)
- Weather API: Integration with external weather services
"""
