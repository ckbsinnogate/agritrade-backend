"""
Serializers for AI models
"""

from rest_framework import serializers
from .models import (
    AIConversation, CropAdvisory, DiseaseDetection, 
    MarketIntelligence, AIUsageAnalytics, AIFeedback
)


class AIConversationSerializer(serializers.ModelSerializer):
    """Serializer for AI conversations"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = AIConversation
        fields = [
            'id', 'user', 'conversation_type', 'language', 
            'last_message', 'message_count', 'satisfaction_rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CropAdvisorySerializer(serializers.ModelSerializer):
    """Serializer for crop advisories"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = CropAdvisory
        fields = [
            'id', 'user', 'crop_type', 'farming_stage', 'location',
            'season', 'question', 'advice', 'confidence_score',
            'implementation_status', 'results', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class DiseaseDetectionSerializer(serializers.ModelSerializer):
    """Serializer for disease detection"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = DiseaseDetection
        fields = [
            'id', 'user', 'crop_type', 'symptoms', 'image_url',
            'location', 'diagnosis', 'treatment_plan', 'confidence_score',
            'treatment_status', 'outcome', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class MarketIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for market intelligence"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = MarketIntelligence
        fields = [
            'id', 'user', 'crop_type', 'location', 'market_type',
            'price_prediction', 'analysis', 'confidence_score',
            'validity_period', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class AIUsageAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for AI usage analytics"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = AIUsageAnalytics
        fields = [
            'id', 'user', 'service_type', 'tokens_used',
            'response_time', 'success', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class AIFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for AI feedback"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = AIFeedback
        fields = [
            'id', 'user', 'service_type', 'service_id',
            'rating', 'feedback_text', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class AIAnalyticsSerializer(serializers.Serializer):
    """Serializer for AI analytics dashboard"""
    total_requests = serializers.IntegerField()
    total_tokens_used = serializers.IntegerField()
    service_breakdown = serializers.DictField()
    average_rating = serializers.FloatField()
    feedback_count = serializers.IntegerField()
    period_days = serializers.IntegerField()


class AIHealthCheckSerializer(serializers.Serializer):
    """Serializer for AI health check"""
    success = serializers.BooleanField()
    status = serializers.CharField()
    model = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()
