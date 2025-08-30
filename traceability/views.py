"""
AgriConnect Traceability API Views
REST API views for blockchain traceability system
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import qrcode
import base64
import io
import json

from .models import (
    BlockchainNetwork, SmartContract, BlockchainTransaction,
    Farm, FarmCertification, ProductTrace, SupplyChainEvent,
    ConsumerScan
)
from .serializers import (
    BlockchainNetworkSerializer, SmartContractSerializer, BlockchainTransactionSerializer,
    FarmSerializer, FarmCertificationSerializer, ProductTraceSerializer,
    SupplyChainEventSerializer, ConsumerScanSerializer, ConsumerTraceabilitySerializer,
    QRCodeDataSerializer, BlockchainVerificationSerializer, TraceabilityAnalyticsSerializer,
    FarmRegistrationSerializer
)

class ProductTraceViewSet(viewsets.ModelViewSet):
    """ViewSet for product traceability"""
    queryset = ProductTrace.objects.select_related(
        'product', 'farm__farmer'
    ).prefetch_related('events').all()
    serializer_class = ProductTraceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['quality_grade', 'is_active', 'farm', 'product']
    search_fields = ['product__name', 'batch_number', 'blockchain_id', 'farm__name']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def consumer_view(self, request, pk=None):
        """Consumer-facing traceability information"""
        product_trace = self.get_object()
        
        # Record the scan
        ConsumerScan.objects.create(
            product_trace=product_trace,
            consumer_id=request.GET.get('consumer_id', ''),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_type=self.get_device_type(request),
            location=request.GET.get('location', '')
        )
        
        # Update view count
        product_trace.consumer_view_count += 1
        product_trace.last_viewed_at = timezone.now()
        product_trace.save()
        
        serializer = ConsumerTraceabilitySerializer(product_trace)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Generate QR code for product"""
        product_trace = self.get_object()
        
        # QR code data
        qr_data = {
            'product_id': product_trace.product.id,
            'product_name': product_trace.product.name,
            'batch_number': product_trace.batch_number,
            'blockchain_id': product_trace.blockchain_id,
            'farm_name': product_trace.farm.name,
            'farmer_name': product_trace.farm.farmer.get_full_name(),
            'harvest_date': product_trace.harvest_date.isoformat(),
            'organic_certified': product_trace.farm.organic_certified,
            'verification_url': f"{request.build_absolute_uri('/api/v1/traceability/products/')}{product_trace.id}/consumer_view/"
        }
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Update product trace with QR code data
        product_trace.qr_code_data = json.dumps(qr_data)
        product_trace.qr_code_image = qr_image_base64
        product_trace.save()
        
        return Response({
            'qr_data': qr_data,
            'qr_image': qr_image_base64,
            'qr_text': json.dumps(qr_data)
        })

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_device_type(self, request):
        """Determine device type from user agent"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent:
            return 'tablet'
        else:
            return 'desktop'

class BlockchainNetworkViewSet(viewsets.ModelViewSet):
    """ViewSet for blockchain networks"""
    queryset = BlockchainNetwork.objects.all()
    serializer_class = BlockchainNetworkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_testnet', 'is_active', 'native_currency']
    search_fields = ['name', 'network_id']
    ordering = ['name']

class SmartContractViewSet(viewsets.ModelViewSet):
    """ViewSet for smart contracts"""
    queryset = SmartContract.objects.select_related('network').all()
    serializer_class = SmartContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['network', 'is_deployed', 'version']
    search_fields = ['name', 'contract_address']
    ordering = ['-created_at']

class BlockchainTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blockchain transactions (read-only)"""
    queryset = BlockchainTransaction.objects.select_related('contract__network').all()
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'contract', 'function_name']
    search_fields = ['transaction_hash', 'from_address', 'to_address']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify transaction status on blockchain"""
        transaction = self.get_object()
        # TODO: Implement actual blockchain verification
        return Response({
            'verified': True,
            'transaction_hash': transaction.transaction_hash,
            'status': transaction.status,
            'confirmation_count': transaction.confirmation_count
        })

class FarmViewSet(viewsets.ModelViewSet):
    """ViewSet for farms"""
    queryset = Farm.objects.select_related('farmer').prefetch_related('certifications').all()
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['organic_certified', 'is_verified', 'farmer']
    search_fields = ['name', 'location', 'registration_number', 'farmer__username']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Farmers can only see their own farms
        if not self.request.user.is_staff:
            queryset = queryset.filter(farmer=self.request.user)
        return queryset

    @action(detail=False, methods=['post'], serializer_class=FarmRegistrationSerializer)
    def register(self, request):
        """Register a new farm"""
        serializer = FarmRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            farm = serializer.save()
            return Response(FarmSerializer(farm).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify farm (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        farm = self.get_object()
        farm.is_verified = True
        farm.verification_date = timezone.now()
        farm.save()
        
        return Response({'message': 'Farm verified successfully'})

class FarmCertificationViewSet(viewsets.ModelViewSet):
    """ViewSet for farm certifications"""
    queryset = FarmCertification.objects.select_related('farm__farmer').all()
    serializer_class = FarmCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['certification_type', 'blockchain_verified', 'farm']
    search_fields = ['certificate_number', 'issuing_authority', 'farm__name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Farmers can only see their own farm certifications
        if not self.request.user.is_staff:
            queryset = queryset.filter(farm__farmer=self.request.user)
        return queryset

class SupplyChainEventViewSet(viewsets.ModelViewSet):
    """ViewSet for supply chain events"""
    queryset = SupplyChainEvent.objects.select_related(
        'product_trace__product', 'actor'
    ).all()
    serializer_class = SupplyChainEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['event_type', 'status', 'verification_required', 'product_trace']
    search_fields = ['product_trace__product__name', 'actor__username', 'location', 'description']
    ordering = ['-timestamp']

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify supply chain event"""
        event = self.get_object()
        event.status = 'verified'
        event.verified_at = timezone.now()
        event.save()
        
        # TODO: Record on blockchain
        
        return Response({'message': 'Event verified successfully'})

class ConsumerScanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for consumer scans (read-only)"""
    queryset = ConsumerScan.objects.select_related('product_trace__product').all()
    serializer_class = ConsumerScanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['device_type', 'feedback_rating', 'product_trace']
    search_fields = ['product_trace__product__name', 'consumer_id']
    ordering = ['-scanned_at']

class TraceabilityDashboardViewSet(viewsets.ViewSet):
    """Dashboard views for traceability analytics"""
    permission_classes = [permissions.AllowAny]  # Temporarily allow for testing

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Traceability system overview"""
        # Get counts
        total_products = ProductTrace.objects.filter(is_active=True).count()
        total_farms = Farm.objects.filter(is_verified=True).count()
        total_scans = ConsumerScan.objects.count()
        total_transactions = BlockchainTransaction.objects.filter(status='confirmed').count()
        
        # Calculate percentages
        organic_products = ProductTrace.objects.filter(farm__organic_certified=True).count()
        organic_percentage = (organic_products / total_products * 100) if total_products > 0 else 0
        
        verified_farms = Farm.objects.filter(is_verified=True).count()
        total_farms_count = Farm.objects.count()
        verified_percentage = (verified_farms / total_farms_count * 100) if total_farms_count > 0 else 0
        
        # Average supply chain events per product
        avg_events = SupplyChainEvent.objects.values('product_trace').annotate(
            event_count=Count('id')
        ).aggregate(Avg('event_count'))['event_count__avg'] or 0
        
        # Top scanned products
        top_products = ProductTrace.objects.order_by('-consumer_view_count')[:5]
        top_products_data = [{
            'product_name': pt.product.name,
            'batch_number': pt.batch_number,
            'scan_count': pt.consumer_view_count,
            'farm_name': pt.farm.name
        } for pt in top_products]
        
        # Recent activities
        recent_events = SupplyChainEvent.objects.select_related(
            'product_trace__product', 'actor'
        ).order_by('-created_at')[:5]
        
        recent_activities = [{
            'event_type': event.get_event_type_display(),
            'product_name': event.product_trace.product.name,
            'actor_name': event.actor.get_full_name(),
            'location': event.location,
            'timestamp': event.timestamp.isoformat()
        } for event in recent_events]
        
        data = {
            'total_products_traced': total_products,
            'total_farms_registered': total_farms,
            'total_consumer_scans': total_scans,
            'blockchain_transactions': total_transactions,
            'organic_products_percentage': round(organic_percentage, 2),
            'verified_farms_percentage': round(verified_percentage, 2),
            'average_supply_chain_events': round(avg_events, 2),
            'top_scanned_products': top_products_data,
            'recent_activities': recent_activities
        }
        
        serializer = TraceabilityAnalyticsSerializer(data)
        return Response(serializer.data)
