"""
AgriConnect Payment System URLs
Payment processing endpoints for African agricultural commerce platform
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .webhook_views import PaystackWebhookView, test_webhook

# Create router for ViewSets
router = DefaultRouter()
router.register(r'gateways', views.PaymentGatewayViewSet, basename='paymentgateway')
router.register(r'payment-methods', views.PaymentMethodViewSet, basename='paymentmethod')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'escrow', views.EscrowViewSet, basename='escrow')
router.register(r'disputes', views.DisputeViewSet, basename='dispute')

app_name = 'payments'

urlpatterns = [
    # API Root - Payment system overview
    path('', views.PaymentAPIRoot.as_view(), name='api-root'),
    
    # ViewSet URLs - Direct access (no nested api/v1/)
    path('', include(router.urls)),
      # Webhook endpoints
    path('webhook/paystack/', PaystackWebhookView.as_view(), name='paystack-webhook'),
    path('webhook/test/', test_webhook, name='test-webhook'),
]
