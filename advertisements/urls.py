"""
Advertisement & Marketing System URLs
URL configuration for advertising platform APIs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'placements', views.AdvertisementPlacementViewSet, basename='advertisement-placements')
router.register(r'advertisements', views.AdvertisementViewSet, basename='advertisements')
router.register(r'campaigns', views.AdvertisementCampaignViewSet, basename='advertisement-campaigns')
router.register(r'stats', views.AdvertisementStatsViewSet, basename='advertisement-stats')

app_name = 'advertisements'

urlpatterns = [
    # API Root endpoint
    path('', views.advertisements_api_root, name='advertisements-api-root'),
    
    # Dashboard endpoint
    path('dashboard/', views.advertisement_dashboard, name='advertisement-dashboard'),
    
    # Audience segments endpoint
    path('audience-segments/', views.audience_segments, name='audience-segments'),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here
]

"""
API Endpoints Generated:

Advertisement Placements:
- GET /api/v1/advertisements/placements/ - List all placements
- POST /api/v1/advertisements/placements/ - Create new placement
- GET /api/v1/advertisements/placements/{id}/ - Get placement details
- PUT /api/v1/advertisements/placements/{id}/ - Update placement
- DELETE /api/v1/advertisements/placements/{id}/ - Delete placement

Advertisements:
- GET /api/v1/advertisements/advertisements/ - List advertisements
- POST /api/v1/advertisements/advertisements/ - Create advertisement
- GET /api/v1/advertisements/advertisements/{id}/ - Get advertisement details
- PUT /api/v1/advertisements/advertisements/{id}/ - Update advertisement
- DELETE /api/v1/advertisements/advertisements/{id}/ - Delete advertisement
- POST /api/v1/advertisements/advertisements/{id}/pause/ - Pause advertisement
- POST /api/v1/advertisements/advertisements/{id}/resume/ - Resume advertisement
- GET /api/v1/advertisements/advertisements/{id}/analytics/ - Get analytics

Advertisement Campaigns:
- GET /api/v1/advertisements/campaigns/ - List campaigns
- POST /api/v1/advertisements/campaigns/ - Create campaign
- GET /api/v1/advertisements/campaigns/{id}/ - Get campaign details
- PUT /api/v1/advertisements/campaigns/{id}/ - Update campaign
- DELETE /api/v1/advertisements/campaigns/{id}/ - Delete campaign
- GET /api/v1/advertisements/campaigns/{id}/performance/ - Get campaign performance

Advertisement Statistics:
- GET /api/v1/advertisements/stats/ - Get comprehensive statistics
- GET /api/v1/advertisements/stats/market_insights/ - Get market insights

Query Parameters Support:
- status: Filter by advertisement status
- ad_type: Filter by advertisement type
- campaign: Filter by campaign ID
- start_date/end_date: Filter by date range
- active_only: Show only active advertisements
- location: Filter placements by location
- is_active: Filter by active status
- days: Number of days for analytics (default: 30)
"""
