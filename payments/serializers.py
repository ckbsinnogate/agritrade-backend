"""
AgriConnect Payment Serializers
Serializers for payment processing, escrow management, and dispute resolution
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone

from .models import (
    PaymentGateway, PaymentMethod, Transaction, EscrowAccount,
    EscrowMilestone, DisputeCase, PaymentWebhook
)
from orders.models import Order

User = get_user_model()


class PaymentGatewaySerializer(serializers.ModelSerializer):
    """Serializer for payment gateway information (public data only)"""
    
    class Meta:
        model = PaymentGateway
        fields = [
            'name', 'display_name', 'is_active', 'supported_currencies',
            'supported_countries', 'supported_payment_methods',
            'minimum_amount', 'maximum_amount'
        ]
        read_only_fields = ['name']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for user payment methods"""
    gateway_name = serializers.CharField(source='gateway.display_name', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'method_type', 'gateway', 'gateway_name', 'account_details',
            'display_name', 'is_default', 'is_verified', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']
        extra_kwargs = {
            'account_details': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create payment method for authenticated user"""
        validated_data['user'] = self.context['request'].user
        
        # If this is set as default, unset other defaults
        if validated_data.get('is_default', False):
            PaymentMethod.objects.filter(
                user=validated_data['user'],
                is_default=True
            ).update(is_default=False)
        
        return super().create(validated_data)


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transactions"""
    
    class Meta:
        model = Transaction
        fields = [
            'order', 'gateway', 'payment_method', 'amount', 'currency',
            'transaction_type', 'metadata'
        ]
    
    def validate(self, data):
        """Validate transaction data"""
        gateway = data['gateway']
        amount = data['amount']
        currency = data['currency']
        
        # Check gateway supports currency
        if currency not in gateway.supported_currencies:
            raise serializers.ValidationError(
                f"Gateway {gateway.display_name} does not support {currency}"
            )
        
        # Check minimum amount
        if amount < gateway.minimum_amount:
            raise serializers.ValidationError(
                f"Amount below minimum {gateway.minimum_amount} {currency}"
            )
        
        # Check maximum amount
        if gateway.maximum_amount and amount > gateway.maximum_amount:
            raise serializers.ValidationError(
                f"Amount exceeds maximum {gateway.maximum_amount} {currency}"
            )
        
        return data
    
    def create(self, validated_data):
        """Create transaction with gateway reference"""
        import uuid
        validated_data['user'] = self.context['request'].user
        validated_data['gateway_reference'] = f"AG-{uuid.uuid4().hex[:12].upper()}"
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction display"""
    gateway_name = serializers.CharField(source='gateway.display_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'gateway_reference', 'external_reference', 'amount', 'currency',
            'status', 'transaction_type', 'gateway_name', 'user_name', 'order_number',
            'initiated_at', 'processed_at', 'completed_at', 'metadata'
        ]
        read_only_fields = ['id', 'gateway_reference', 'external_reference']


class PaymentInitializeSerializer(serializers.Serializer):
    """Serializer for payment initialization"""
    order_id = serializers.UUIDField()
    gateway = serializers.CharField()
    payment_method_id = serializers.UUIDField(required=False)
    return_url = serializers.URLField(required=False)
    metadata = serializers.DictField(required=False, default=dict)
    
    def validate_order_id(self, value):
        """Validate order exists and belongs to user"""
        try:
            order = Order.objects.get(id=value)
            user = self.context['request'].user
            
            # Check user has access to this order
            if order.buyer != user and order.seller != user:
                raise serializers.ValidationError("Order not found")
            
            # Check order is in payable state
            if order.status not in ['pending', 'confirmed']:
                raise serializers.ValidationError("Order is not in payable state")
            
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
    
    def validate_gateway(self, value):
        """Validate gateway exists and is active"""
        try:
            gateway = PaymentGateway.objects.get(name=value, is_active=True)
            return gateway.name
        except PaymentGateway.DoesNotExist:
            raise serializers.ValidationError("Payment gateway not available")


class EscrowAccountSerializer(serializers.ModelSerializer):
    """Serializer for escrow account management"""
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    milestones_count = serializers.IntegerField(source='milestones.count', read_only=True)
    pending_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = EscrowAccount
        fields = [
            'id', 'order_number', 'buyer_name', 'seller_name', 'total_amount',
            'currency', 'released_amount', 'pending_amount', 'status',
            'auto_release_days', 'requires_quality_confirmation',
            'milestones_count', 'funded_at', 'released_at', 'created_at'
        ]
        read_only_fields = ['id', 'funded_at', 'released_at', 'created_at']
    
    def get_pending_amount(self, obj):
        """Calculate pending release amount"""
        return obj.total_amount - obj.released_amount


class EscrowMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for escrow milestones"""
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    
    class Meta:
        model = EscrowMilestone
        fields = [
            'id', 'milestone_type', 'description', 'release_percentage',
            'release_amount', 'is_completed', 'is_released', 'completed_by_name',
            'evidence_data', 'verification_notes', 'completed_at', 'released_at'
        ]
        read_only_fields = ['id', 'release_amount', 'is_released', 'released_at']


class EscrowMilestoneCompleteSerializer(serializers.Serializer):
    """Serializer for completing escrow milestones"""
    evidence_data = serializers.DictField(required=False, default=dict)
    verification_notes = serializers.CharField(required=False, default='')
    
    def validate(self, data):
        """Validate milestone completion"""
        milestone = self.instance
        user = self.context['request'].user
        
        # Check if milestone is already completed
        if milestone.is_completed:
            raise serializers.ValidationError("Milestone already completed")
        
        # Check user has permission to complete this milestone
        escrow = milestone.escrow
        if user not in [escrow.buyer, escrow.seller]:
            raise serializers.ValidationError("No permission to complete this milestone")
        
        return data


class DisputeCaseSerializer(serializers.ModelSerializer):
    """Serializer for dispute cases"""
    raised_by_name = serializers.CharField(source='raised_by.get_full_name', read_only=True)
    respondent_name = serializers.CharField(source='respondent.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = DisputeCase
        fields = [
            'id', 'order_number', 'dispute_type', 'title', 'description',
            'raised_by_name', 'respondent_name', 'assigned_to_name',
            'status', 'resolution', 'resolution_notes', 'resolution_amount',
            'evidence', 'resolved_at', 'response_deadline', 'created_at'
        ]
        read_only_fields = [
            'id', 'raised_by_name', 'respondent_name', 'assigned_to_name',
            'resolved_at', 'created_at'
        ]


class DisputeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating dispute cases"""
    
    class Meta:
        model = DisputeCase
        fields = [
            'order', 'dispute_type', 'title', 'description', 'evidence'
        ]
    
    def validate_order(self, value):
        """Validate user can create dispute for this order"""
        user = self.context['request'].user
        
        if value.buyer != user and value.seller != user:
            raise serializers.ValidationError("Order not found")
        
        # Check if dispute already exists
        if value.disputes.filter(status__in=['open', 'investigating']).exists():
            raise serializers.ValidationError("Active dispute already exists for this order")
        
        return value
    
    def create(self, validated_data):
        """Create dispute case"""
        user = self.context['request'].user
        order = validated_data['order']
        
        validated_data['raised_by'] = user
        validated_data['respondent'] = order.seller if user == order.buyer else order.buyer
        
        # Set response deadline (7 days from now)
        validated_data['response_deadline'] = timezone.now() + timezone.timedelta(days=7)
        
        return super().create(validated_data)


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Serializer for payment webhooks"""
    gateway_name = serializers.CharField(source='gateway.display_name', read_only=True)
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'gateway_name', 'event_type', 'webhook_id', 'is_processed',
            'processing_error', 'retry_count', 'received_at', 'processed_at'
        ]
        read_only_fields = ['id', 'received_at', 'processed_at']


class PaymentStatusSerializer(serializers.Serializer):
    """Serializer for payment status checks"""
    gateway_reference = serializers.CharField()
    
    def validate_gateway_reference(self, value):
        """Validate transaction exists"""
        try:
            transaction = Transaction.objects.get(gateway_reference=value)
            user = self.context['request'].user
            
            # Check user has access to this transaction
            if transaction.user != user:
                raise serializers.ValidationError("Transaction not found")
            
            return value
        except Transaction.DoesNotExist:
            raise serializers.ValidationError("Transaction not found")
