"""
SMS/USSD URL Configuration for AgriConnect
Routes for farmer onboarding via SMS and USSD
"""

from django.urls import path
import sms_views

app_name = 'sms'

urlpatterns = [
    # SMS Webhooks
    path('sms/webhook/', sms_views.sms_webhook, name='sms_webhook'),
    path('ussd/webhook/', sms_views.ussd_webhook, name='ussd_webhook'),
    
    # Test Endpoints
    path('sms/test/', sms_views.sms_test_endpoint, name='sms_test'),
    path('ussd/test/', sms_views.ussd_test_endpoint, name='ussd_test'),
    
    # Farmer Registration
    path('farmer/register/', sms_views.farmer_registration_sms, name='farmer_registration'),
    
    # Analytics & Management
    path('analytics/', sms_views.sms_analytics, name='sms_analytics'),
    path('broadcast/', sms_views.bulk_sms_broadcast, name='bulk_sms_broadcast'),
]
