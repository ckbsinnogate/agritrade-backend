from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .views import (
    ReviewViewSet, ExpertReviewViewSet, ReviewRecipeViewSet, SeasonalInsightViewSet,
    PeerRecommendationViewSet, FarmerNetworkViewSet
)

app_name = 'reviews'

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'expert-reviews', ExpertReviewViewSet, basename='expert-review')
router.register(r'recipes', ReviewRecipeViewSet, basename='recipe')
router.register(r'seasonal-insights', SeasonalInsightViewSet, basename='seasonal-insight')
router.register(r'peer-recommendations', PeerRecommendationViewSet, basename='peer-recommendation')
router.register(r'farmer-network', FarmerNetworkViewSet, basename='farmer-network')

@api_view(['GET'])
@permission_classes([AllowAny])
def reviews_api_root(request, format=None):
    """Reviews API Root - Community review and recommendation system"""
    return Response({
        'name': 'AgriConnect Reviews API',
        'description': 'Community-driven review and recommendation system',
        'endpoints': {
            'reviews': request.build_absolute_uri('reviews/'),
            'expert_reviews': request.build_absolute_uri('expert-reviews/'),
            'recipes': request.build_absolute_uri('recipes/'),
            'seasonal_insights': request.build_absolute_uri('seasonal-insights/'),
            'peer_recommendations': request.build_absolute_uri('peer-recommendations/'),
            'farmer_network': request.build_absolute_uri('farmer-network/'),
        },
        'status': 'operational'
    })

urlpatterns = [
    path('', reviews_api_root, name='api-root'),
    path('', include(router.urls)),
]
