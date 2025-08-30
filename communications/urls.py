"""
AgriConnect Communications URLs
Enhanced SMS & OTP Integration System (PRD Section 4.7)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import views

app_name = 'communications'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'providers', views.SMSProviderViewSet, basename='sms-providers')
router.register(r'templates', views.SMSTemplateViewSet, basename='sms-templates')
router.register(r'messages', views.SMSMessageViewSet, basename='sms-messages')
router.register(r'otp', views.OTPCodeViewSet, basename='otp')
router.register(r'preferences', views.CommunicationPreferenceViewSet, basename='preferences')
router.register(r'logs', views.CommunicationLogViewSet, basename='logs')

@api_view(['GET'])
@permission_classes([AllowAny])
def communications_api_root(request, format=None):
    """Communications API Root - SMS and messaging system"""
    return Response({
        'name': 'AgriConnect Communications API',
        'description': 'SMS, OTP, and messaging system integration',
        'endpoints': {
            'providers': request.build_absolute_uri('providers/'),
            'templates': request.build_absolute_uri('templates/'),
            'messages': request.build_absolute_uri('messages/'),
            'otp': request.build_absolute_uri('otp/'),
            'preferences': request.build_absolute_uri('preferences/'),
            'logs': request.build_absolute_uri('logs/'),
            'conversations': request.build_absolute_uri('conversations/'),
            'notifications': request.build_absolute_uri('notifications/'),
            'notification_settings': request.build_absolute_uri('notification-settings/'),
        },
        'status': 'operational'
    })

urlpatterns = [
    # API root
    path('', communications_api_root, name='api-root'),
    
    # Missing frontend endpoints
    path('conversations/', views.conversations_list, name='conversations'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notification-settings/', views.notification_settings, name='notification-settings'),
    
    # Router endpoints
    path('', include(router.urls)),
]