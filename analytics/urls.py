"""
Analytics URLs
URL patterns for analytics and dashboard endpoints
"""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Analytics API Root
    path('', views.analytics_api_root, name='analytics-root'),
    
    # Core Analytics Endpoints (Original)
    path('platform/', views.platform_stats, name='platform-stats'),
    path('farmer-stats/', views.farmer_stats, name='farmer-stats'),
    path('dashboard/', views.dashboard_summary, name='dashboard-summary'),
    path('market-insights/', views.market_insights, name='market-insights'),
    path('user-growth/', views.user_growth, name='user-growth'),
    path('revenue/', views.revenue_analytics, name='revenue-analytics'),
    path('products/', views.product_analytics, name='product-analytics'),
    path('orders/', views.order_analytics, name='order-analytics'),
    
    # Institution-specific endpoints
    path('institution/members/', views.institution_members, name='institution-members'),
    path('institution/budget-analytics/', views.institution_budget_analytics, name='institution-budget-analytics'),
    path('institution/stats/', views.institution_stats, name='institution-stats'),
    
    # Frontend-Expected Endpoints (Aliases for compatibility)
    path('dashboard-stats/', views.platform_stats, name='dashboard-stats'),
    path('revenue-overview/', views.revenue_analytics, name='revenue-overview'),
    path('user-analytics/', views.user_growth, name='user-analytics'),
]
