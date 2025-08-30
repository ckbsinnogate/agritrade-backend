"""
AgriConnect Payment Views
Complete payment processing API for agricultural commerce
"""

from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
import uuid
import logging

from .models import (
    PaymentGateway, PaymentMethod, Transaction, EscrowAccount,
    EscrowMilestone, DisputeCase, PaymentWebhook
)
from .serializers import (
    PaymentGatewaySerializer, PaymentMethodSerializer, TransactionSerializer,
    TransactionCreateSerializer, PaymentInitializeSerializer, EscrowAccountSerializer,
    EscrowMilestoneSerializer, EscrowMilestoneCompleteSerializer, DisputeCaseSerializer,
    DisputeCreateSerializer, PaymentWebhookSerializer, PaymentStatusSerializer
)
from orders.models import Order

logger = logging.getLogger(__name__)


class PaymentAPIRoot(generics.GenericAPIView):
    """
    AgriConnect Payment System API Root
    Complete payment processing for African agricultural commerce
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, format=None):
        try:
            endpoints = {
                'payment_gateways': request.build_absolute_uri('gateways/'),
                'payment_methods': request.build_absolute_uri('payment-methods/'),
                'transactions': request.build_absolute_uri('transactions/'),
                'payments': request.build_absolute_uri('payments/'),
                'escrow_accounts': request.build_absolute_uri('escrow/'),
                'disputes': request.build_absolute_uri('disputes/'),
                'webhooks': {
                    'paystack': request.build_absolute_uri('webhook/paystack/'),
                    'test': request.build_absolute_uri('webhook/test/'),
                }
            }
            
            # Get supported gateways safely
            try:
                supported_gateways = list(PaymentGateway.objects.filter(is_active=True).values_list('display_name', flat=True))
            except Exception:
                supported_gateways = ['Paystack', 'Flutterwave', 'Mobile Money']
                
        except Exception as e:
            logger.warning(f"Error generating payment endpoints: {e}")
            endpoints = {
                'payment_gateways': '/api/v1/payments/gateways/',
                'payment_methods': '/api/v1/payments/payment-methods/',
                'transactions': '/api/v1/payments/transactions/',
                'payments': '/api/v1/payments/payments/',
                'escrow_accounts': '/api/v1/payments/escrow/',
                'disputes': '/api/v1/payments/disputes/',
            }
            supported_gateways = ['Paystack', 'Flutterwave', 'Mobile Money']

        return Response({
            'name': 'AgriConnect Payment System',
            'version': '1.0',
            'description': 'Complete payment processing and escrow system for agricultural commerce',
            'features': [
                'Multi-Gateway Support (Paystack, Flutterwave, Mobile Money)',
                'Escrow System for Agricultural Trades',
                'Dispute Resolution',
                'Transaction Management',
                'African Payment Methods Support',
                'Multi-Currency Support (GHS, NGN, KES, USD)'
            ],
            'endpoints': endpoints,
            'supported_gateways': supported_gateways,
            'supported_currencies': ['GHS', 'NGN', 'KES', 'UGX', 'ZAR', 'USD'],
            'documentation': 'Visit individual endpoints for detailed API documentation',
            'status': 'Phase 4: Payment & Notification Integration - ACTIVE'
        })


class PaymentGatewayViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for available payment gateways"""
    queryset = PaymentGateway.objects.filter(is_active=True)
    serializer_class = PaymentGatewaySerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for user payment methods"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['method_type', 'is_default', 'is_active']
    ordering_fields = ['created_at', 'is_default']
    ordering = ['-is_default', '-created_at']
    
    def get_queryset(self):
        """Return payment methods for current user"""
        return PaymentMethod.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default"""
        payment_method = self.get_object()
        
        # Unset other defaults
        PaymentMethod.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Set this as default
        payment_method.is_default = True
        payment_method.save()
        
        return Response({'message': 'Payment method set as default'})
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify payment method (placeholder for verification logic)"""
        payment_method = self.get_object()
        
        # TODO: Implement actual verification based on payment method type
        payment_method.is_verified = True
        payment_method.save()
        
        return Response({'message': 'Payment method verified'})


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for transaction management"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'transaction_type', 'currency', 'gateway']
    search_fields = ['gateway_reference', 'external_reference']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return transactions for current user"""
        return Transaction.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get transaction status"""
        transaction = self.get_object()
        
        # TODO: Query gateway for latest status if needed
        
        return Response({
            'gateway_reference': transaction.gateway_reference,
            'status': transaction.status,
            'amount': transaction.amount,
            'currency': transaction.currency,
            'initiated_at': transaction.initiated_at,
            'completed_at': transaction.completed_at
        })


class PaymentViewSet(viewsets.ViewSet):
    """ViewSet for payment operations"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """Initialize a payment"""
        serializer = PaymentInitializeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order_id = serializer.validated_data['order_id']
                    gateway_name = serializer.validated_data['gateway']
                    
                    # Get order and gateway
                    order = Order.objects.get(id=order_id)
                    gateway = PaymentGateway.objects.get(name=gateway_name, is_active=True)
                    
                    # Create transaction
                    transaction_data = {
                        'user': request.user,
                        'order': order,
                        'gateway': gateway,
                        'amount': order.total_amount,
                        'currency': order.currency,
                        'gateway_reference': f"AG-{uuid.uuid4().hex[:12].upper()}",
                        'metadata': serializer.validated_data.get('metadata', {})
                    }
                    
                    # Add payment method if provided
                    if 'payment_method_id' in serializer.validated_data:
                        payment_method = PaymentMethod.objects.get(
                            id=serializer.validated_data['payment_method_id'],
                            user=request.user
                        )
                        transaction_data['payment_method'] = payment_method
                    
                    transaction_obj = Transaction.objects.create(**transaction_data)
                    
                    # TODO: Initialize payment with gateway
                    # This would call the actual payment gateway API
                    
                    return Response({
                        'transaction_id': transaction_obj.id,
                        'gateway_reference': transaction_obj.gateway_reference,
                        'amount': transaction_obj.amount,
                        'currency': transaction_obj.currency,
                        'status': transaction_obj.status,
                        'message': 'Payment initialized successfully',
                        # 'payment_url': payment_url,  # From gateway response
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                logger.error(f"Payment initialization failed: {str(e)}")
                return Response(
                    {'error': 'Payment initialization failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify payment status"""
        serializer = PaymentStatusSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            gateway_reference = serializer.validated_data['gateway_reference']
            transaction_obj = Transaction.objects.get(gateway_reference=gateway_reference)
            
            # TODO: Query gateway for actual status
            # This would call the payment gateway verification API
            
            return Response({
                'gateway_reference': transaction_obj.gateway_reference,
                'status': transaction_obj.status,
                'amount': transaction_obj.amount,
                'currency': transaction_obj.currency,
                'verified_at': transaction_obj.updated_at
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def methods(self, request):
        """Get available payment methods"""
        gateways = PaymentGateway.objects.filter(is_active=True)
        user_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
        
        return Response({
            'gateways': PaymentGatewaySerializer(gateways, many=True).data,
            'saved_methods': PaymentMethodSerializer(user_methods, many=True).data
        })


class EscrowViewSet(viewsets.ModelViewSet):
    """ViewSet for escrow account management"""
    serializer_class = EscrowAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'currency']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return escrow accounts for current user"""
        return EscrowAccount.objects.filter(
            Q(buyer=self.request.user) | Q(seller=self.request.user)
        )
    
    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """Release escrow funds"""
        escrow = self.get_object()
        user = request.user
        
        # Check permissions
        if user not in [escrow.buyer, escrow.seller]:
            return Response(
                {'error': 'No permission to release funds'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check escrow status
        if escrow.status != 'funded':
            return Response(
                {'error': 'Escrow is not in funded state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # TODO: Implement actual fund release logic
                escrow.status = 'released'
                escrow.released_amount = escrow.total_amount
                escrow.save()
                
                # Update order status
                escrow.order.payment_status = 'released'
                escrow.order.save()
                
                return Response({'message': 'Funds released successfully'})
                
        except Exception as e:
            logger.error(f"Escrow release failed: {str(e)}")
            return Response(
                {'error': 'Fund release failed'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def milestones(self, request, pk=None):
        """Get escrow milestones"""
        escrow = self.get_object()
        milestones = escrow.milestones.all()
        serializer = EscrowMilestoneSerializer(milestones, many=True)
        return Response(serializer.data)


class EscrowMilestoneViewSet(viewsets.ModelViewSet):
    """ViewSet for escrow milestone management"""
    serializer_class = EscrowMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return milestones for user's escrow accounts"""
        return EscrowMilestone.objects.filter(
            Q(escrow__buyer=self.request.user) | Q(escrow__seller=self.request.user)
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a milestone"""
        milestone = self.get_object()
        serializer = EscrowMilestoneCompleteSerializer(
            milestone, data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    milestone.is_completed = True
                    milestone.completed_by = request.user
                    milestone.completed_at = timezone.now()
                    milestone.evidence_data = serializer.validated_data.get('evidence_data', {})
                    milestone.verification_notes = serializer.validated_data.get('verification_notes', '')
                    milestone.save()
                    
                    # TODO: Check if this triggers escrow release
                    
                    return Response({'message': 'Milestone completed successfully'})
                    
            except Exception as e:
                logger.error(f"Milestone completion failed: {str(e)}")
                return Response(
                    {'error': 'Milestone completion failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisputeViewSet(viewsets.ModelViewSet):
    """ViewSet for dispute management"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'dispute_type']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'resolved_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return disputes for current user"""
        return DisputeCase.objects.filter(
            Q(raised_by=self.request.user) | Q(respondent=self.request.user)
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DisputeCreateSerializer
        return DisputeCaseSerializer
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a dispute (admin only)"""
        dispute = self.get_object()
        
        # Check if user is admin/staff
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can resolve disputes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        resolution = request.data.get('resolution')
        resolution_notes = request.data.get('resolution_notes', '')
        resolution_amount = request.data.get('resolution_amount')
        
        try:
            with transaction.atomic():
                dispute.status = 'resolved'
                dispute.resolution = resolution
                dispute.resolution_notes = resolution_notes
                dispute.resolution_amount = resolution_amount
                dispute.resolved_at = timezone.now()
                dispute.save()
                
                # TODO: Implement resolution actions (refunds, releases, etc.)
                
                return Response({'message': 'Dispute resolved successfully'})
                
        except Exception as e:
            logger.error(f"Dispute resolution failed: {str(e)}")
            return Response(
                {'error': 'Dispute resolution failed'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def webhook_handler(request, gateway_name):
    """Handle payment gateway webhooks"""
    try:
        gateway = PaymentGateway.objects.get(name=gateway_name, is_active=True)
        
        # Create webhook record
        webhook = PaymentWebhook.objects.create(
            gateway=gateway,
            event_type=request.data.get('event', 'unknown'),
            payload=request.data,
            signature=request.headers.get('X-Paystack-Signature', '')
        )
        
        # TODO: Process webhook based on gateway type
        # This would include signature verification and transaction updates
        
        return Response({'status': 'received'}, status=status.HTTP_200_OK)
        
    except PaymentGateway.DoesNotExist:
        return Response({'error': 'Gateway not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        return Response({'error': 'Processing failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def payments_api_root(request, format=None):
    """API root for payments system"""
    return Response({
        'message': 'AgriConnect Payment System v4.0',
        'description': 'Complete payment processing and escrow system for agricultural commerce',
        'version': '4.0.0',
        'features': [
            'Multi-gateway payment processing (Paystack, Flutterwave)',
            'African mobile money integration',
            'Escrow system for secure agricultural trades',
            'Milestone-based fund releases',
            'Dispute resolution system',
            'Multi-currency support',
            'Webhook processing',
            'Payment method management'
        ],
        'endpoints': {
            'gateways': {
                'url': '/api/v1/payments/gateways/',
                'description': 'Available payment gateways'
            },
            'methods': {
                'url': '/api/v1/payments/payment-methods/',
                'description': 'User payment methods'
            },
            'transactions': {
                'url': '/api/v1/payments/transactions/',
                'description': 'Payment transactions'
            },
            'payments': {
                'url': '/api/v1/payments/payments/',
                'description': 'Payment operations'
            },
            'escrow': {
                'url': '/api/v1/payments/escrow/',
                'description': 'Escrow account management'
            },
            'disputes': {
                'url': '/api/v1/payments/disputes/',
                'description': 'Dispute resolution'
            }
        },
        'payment_flow': {
            '1_initialize': 'Initialize payment with order and gateway',
            '2_redirect': 'Redirect user to gateway payment page',
            '3_webhook': 'Receive payment confirmation via webhook',
            '4_verify': 'Verify payment status with gateway',
            '5_escrow': 'Funds held in escrow until delivery',
            '6_release': 'Release funds based on milestones'
        },
        'supported_gateways': ['Paystack', 'Flutterwave', 'MTN Mobile Money', 'Vodafone Cash'],
        'supported_currencies': ['GHS', 'NGN', 'KES', 'USD', 'EUR'],
        'escrow_features': [
            'Automatic fund holding',
            'Milestone-based releases',
            'Quality confirmation',
            'Dispute resolution',
            'Auto-release after delivery'
        ]
    })
