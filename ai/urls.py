"""
URL patterns for AI app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import views

app_name = 'ai'

@api_view(['GET'])
@permission_classes([AllowAny])
def ai_api_root(request, format=None):
    """AI Services API Root - Agricultural Intelligence System"""
    return Response({
        'name': 'AgriConnect AI Services',
        'description': 'AI-powered agricultural intelligence and advisory system',
        'endpoints': {
            'chat': request.build_absolute_uri('chat/'),
            'crop_advisory': request.build_absolute_uri('crop-advisory/'),
            'disease_detection': request.build_absolute_uri('disease-detection/'),
            'market_intelligence': request.build_absolute_uri('market-intelligence/'),
            'feedback': request.build_absolute_uri('feedback/'),
            'analytics': request.build_absolute_uri('analytics/'),
            'health': request.build_absolute_uri('health/'),
        },
        'status': 'operational'
    })

# API URL patterns
api_urlpatterns = [
    # API Root
    path('', ai_api_root, name='api-root'),
    
    # Conversational AI
    path('chat/', views.AIConversationView.as_view(), name='chat'),
    
    # Crop Advisory
    path('crop-advisory/', views.CropAdvisoryView.as_view(), name='crop-advisory'),
    
    # Disease Detection
    path('disease-detection/', views.DiseaseDetectionView.as_view(), name='disease-detection'),
      # Market Intelligence
    path('market-intelligence/', views.MarketIntelligenceView.as_view(), name='market-intelligence'),
    path('market-insights/', views.MarketIntelligenceView.as_view(), name='market-insights'),  # Alternative endpoint
    
    # Feedback
    path('feedback/', views.AIFeedbackView.as_view(), name='feedback'),
    
    # Analytics
    path('analytics/', views.AIAnalyticsView.as_view(), name='analytics'),
    
    # Health Check
    path('health/', views.AIHealthCheckView.as_view(), name='health-check'),
]

# Web interface URL patterns
web_urlpatterns = [
    # Admin Dashboard
    path('admin/', views.AIAdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Conversation Management
    path('conversations/', views.AIConversationListView.as_view(), name='conversation-list'),
    
    # Crop Advisory Management
    path('crop-advisories/', views.CropAdvisoryListView.as_view(), name='crop-advisory-list'),
]

# Main URL patterns - Direct endpoints for frontend compatibility
urlpatterns = [
    # Direct API endpoints for frontend compatibility (original structure)
    path('', ai_api_root, name='api-root'),
    path('chat/', views.AIConversationView.as_view(), name='chat'),
    path('crop-advisory/', views.CropAdvisoryView.as_view(), name='crop-advisory'),
    path('disease-detection/', views.DiseaseDetectionView.as_view(), name='disease-detection'),
    path('market-intelligence/', views.MarketIntelligenceView.as_view(), name='market-intelligence'),
    path('market-insights/', views.MarketIntelligenceView.as_view(), name='market-insights'),  # Alternative endpoint
    path('feedback/', views.AIFeedbackView.as_view(), name='feedback'),
    path('analytics/', views.AIAnalyticsView.as_view(), name='analytics'),
    path('health/', views.AIHealthCheckView.as_view(), name='health-check'),
    
    # Nested API structure for new integrations (with /api/ prefix)
    path('api/', include(api_urlpatterns)),
    # Web interface endpoints
    path('web/', include(web_urlpatterns)),
]
