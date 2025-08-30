"""
AgriConnect Subscription System URLs
URL configuration for subscription and loyalty management APIs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanViewSet,
    UserSubscriptionViewSet,
    LoyaltyProgramViewSet,
    UserLoyaltyViewSet,
    SubscriptionAnalyticsViewSet,
    current_subscription,
    usage_stats,
    subscriptions_api_root
)

# Create router for subscription API endpoints
router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plans')
router.register(r'user-subscriptions', UserSubscriptionViewSet, basename='user-subscriptions')
router.register(r'loyalty-programs', LoyaltyProgramViewSet, basename='loyalty-programs')
router.register(r'user-loyalty', UserLoyaltyViewSet, basename='user-loyalty')
router.register(r'analytics', SubscriptionAnalyticsViewSet, basename='subscription-analytics')

app_name = 'subscriptions'

urlpatterns = [
    # API Root endpoint
    path('', subscriptions_api_root, name='subscriptions-api-root'),
    
    # Frontend-specific endpoints (must come before router)
    path('current/', current_subscription, name='current-subscription-frontend'),
    path('usage-stats/', usage_stats, name='usage-stats-frontend'),
    
    # Legacy endpoints for backward compatibility
    path('current-subscription/', current_subscription, name='current-subscription-legacy'),
    
    # Additional subscription endpoints
    path('plans/compare/', SubscriptionPlanViewSet.as_view({'get': 'compare'}), name='plans-compare'),
    path('subscriptions/create/', UserSubscriptionViewSet.as_view({'post': 'create_subscription'}), name='subscription-create'),
    path('loyalty/leaderboard/', UserLoyaltyViewSet.as_view({'get': 'leaderboard'}), name='loyalty-leaderboard'),
    path('analytics/dashboard/', SubscriptionAnalyticsViewSet.as_view({'get': 'dashboard'}), name='analytics-dashboard'),
    path('analytics/recommendations/', SubscriptionAnalyticsViewSet.as_view({'get': 'recommendations'}), name='analytics-recommendations'),
    
    # Include router URLs (must come last)
    path('', include(router.urls)),
]