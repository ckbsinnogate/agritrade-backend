"""
AgriConnect Traceability URLs
URL configuration for blockchain traceability API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'networks', views.BlockchainNetworkViewSet, basename='network')
router.register(r'contracts', views.SmartContractViewSet, basename='contract')
router.register(r'transactions', views.BlockchainTransactionViewSet, basename='transaction')
router.register(r'farms', views.FarmViewSet, basename='farm')
router.register(r'certifications', views.FarmCertificationViewSet, basename='certification')
router.register(r'products', views.ProductTraceViewSet, basename='product-trace')
router.register(r'events', views.SupplyChainEventViewSet, basename='event')
router.register(r'scans', views.ConsumerScanViewSet, basename='scan')
router.register(r'dashboard', views.TraceabilityDashboardViewSet, basename='dashboard')

@api_view(['GET'])
@permission_classes([AllowAny])
def traceability_root(request):
    """
    AgriConnect Blockchain Traceability System API Root
    Complete farm-to-table transparency with blockchain verification
    """
    return Response({
        "name": "AgriConnect Blockchain Traceability System",
        "version": "1.0",
        "description": "Complete farm-to-table transparency with blockchain verification",
        "features": [
            "Farm registration and verification",
            "Digital certification management", 
            "Product journey tracking from farm to consumer",
            "QR code generation for consumer scanning",
            "Blockchain-verified supply chain events",
            "Consumer engagement analytics",
            "Smart contract integration",
            "IPFS metadata storage",
            "Real-time verification system"
        ],
        "endpoints": {
            "farms": "/api/v1/traceability/farms/",
            "farm_certifications": "/api/v1/traceability/certifications/",
            "product_traces": "/api/v1/traceability/products/",
            "supply_chain_events": "/api/v1/traceability/events/",
            "consumer_scans": "/api/v1/traceability/scans/",
            "blockchain_networks": "/api/v1/traceability/networks/",
            "smart_contracts": "/api/v1/traceability/contracts/",
            "blockchain_transactions": "/api/v1/traceability/transactions/",
            "analytics_dashboard": "/api/v1/traceability/dashboard/"
        },
        "farm_operations": {
            "register_farm": "POST /farms/register/",
            "verify_farm": "POST /farms/{id}/verify/",
            "add_certification": "POST /certifications/",
            "view_certifications": "GET /farms/{id}/certifications/"
        },
        "product_operations": {
            "create_trace": "POST /products/",
            "generate_qr_code": "GET /products/{id}/qr_code/",
            "add_supply_chain_event": "POST /products/{id}/add_event/",
            "consumer_view": "GET /products/{id}/consumer_view/"
        },
        "blockchain_operations": {
            "record_on_blockchain": "POST /events/{id}/verify/",
            "verify_transaction": "POST /transactions/{id}/verify/",
            "deploy_contract": "POST /contracts/",
            "network_status": "GET /dashboard/blockchain_status/"
        },
        "consumer_features": {
            "scan_qr_code": "Consumer mobile app QR code scanning",
            "view_product_journey": "Complete farm-to-table journey visualization",
            "verify_certifications": "Blockchain-verified organic and quality certifications",
            "farmer_stories": "Direct connection with farmers and their stories",
            "leave_feedback": "Rate and review products and farmers"
        },
        "certification_types": [
            "organic",
            "fair_trade", 
            "rainforest",
            "global_gap",
            "iso_22000",
            "haccp"
        ],
        "supply_chain_events": [
            "harvest",
            "process",
            "package", 
            "store",
            "transport",
            "inspect",
            "certify",
            "deliver",
            "purchase"
        ],
        "blockchain_integration": {
            "supported_networks": "Ethereum, Polygon, Binance Smart Chain",
            "smart_contracts": "Product traceability, certification verification, supply chain events",
            "ipfs_storage": "Metadata, certificates, and farmer profiles",
            "gas_optimization": "Batch transactions and layer 2 scaling"
        },
        "security_features": {
            "data_integrity": "Blockchain immutable records",
            "authentication": "Multi-factor authentication for farmers and verifiers",
            "encryption": "End-to-end encryption for sensitive data",
            "privacy": "GDPR compliant with selective data disclosure"
        },
        "integration_ready": {
            "warehouse_system": "Automatic traceability event recording from warehouse operations",
            "order_fulfillment": "Product trace linking with customer orders",
            "payment_system": "Escrow contracts for verified delivery",
            "iot_sensors": "Real-time data from field and storage sensors",
            "mobile_apps": "Consumer and farmer mobile applications"
        },
        "status": "Phase 5: Blockchain Traceability System - ACTIVE"
    })

urlpatterns = [
    path('', traceability_root, name='traceability-root'),
    path('', include(router.urls)),
]
