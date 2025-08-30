"""
Advertisement & Marketing System Serializers
Comprehensive API serializers for advertising platform
"""

from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Advertisement, AdvertisementPlacement, AdvertisementPlacementAssignment,
    AdvertisementPerformanceLog, AdvertisementCampaign, AdvertisementAnalytics
)

User = get_user_model()

class AdvertisementPlacementSerializer(serializers.ModelSerializer):
    """Serializer for advertisement placements"""
    
    class Meta:
        model = AdvertisementPlacement
        fields = [
            'id', 'name', 'location', 'dimensions', 'max_file_size_mb',
            'price_per_impression', 'price_per_click', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AdvertisementPlacementAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for placement assignments"""
    
    placement_name = serializers.CharField(source='placement.name', read_only=True)
    placement_location = serializers.CharField(source='placement.location', read_only=True)
    
    class Meta:
        model = AdvertisementPlacementAssignment
        fields = [
            'id', 'placement', 'placement_name', 'placement_location',
            'priority', 'max_impressions', 'assigned_at'
        ]
        read_only_fields = ['id', 'assigned_at']

class AdvertisementPerformanceLogSerializer(serializers.ModelSerializer):
    """Serializer for performance tracking"""
    
    class Meta:
        model = AdvertisementPerformanceLog
        fields = [
            'id', 'advertisement', 'placement', 'event_type', 'user',
            'session_id', 'ip_address', 'user_agent', 'referrer',
            'cost', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AdvertisementAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for daily analytics"""
    
    class Meta:
        model = AdvertisementAnalytics
        fields = [
            'id', 'advertisement', 'date', 'impressions', 'clicks',
            'conversions', 'amount_spent', 'ctr', 'cpc', 'cpa',
            'audience_demographics', 'geographic_performance', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AdvertisementSerializer(serializers.ModelSerializer):
    """Main advertisement serializer with comprehensive features"""
    
    # Calculated fields
    click_through_rate = serializers.ReadOnlyField()
    conversion_rate = serializers.ReadOnlyField()
    cost_per_click = serializers.ReadOnlyField()
    cost_per_acquisition = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    # Related data
    advertiser_name = serializers.CharField(source='advertiser.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    
    # Placement assignments
    placement_assignments = AdvertisementPlacementAssignmentSerializer(
        source='advertisementplacementassignment_set', many=True, read_only=True
    )
    
    class Meta:
        model = Advertisement
        fields = [
            # Basic info
            'id', 'advertiser', 'advertiser_name', 'title', 'description', 'ad_type',
            
            # Targeting
            'target_audience', 'geographic_targeting', 'demographic_targeting', 'product_categories',
            
            # Creative assets
            'banner_image_url', 'banner_mobile_url', 'video_url', 'landing_page_url', 'call_to_action',
            
            # Campaign settings
            'budget', 'daily_budget', 'bid_amount', 'pricing_model', 'currency',
            
            # Schedule
            'start_date', 'end_date',
            
            # Status
            'status', 'approval_notes', 'approved_by', 'approved_at',
            
            # Performance metrics
            'impressions', 'clicks', 'conversions', 'amount_spent',
            
            # Calculated metrics
            'click_through_rate', 'conversion_rate', 'cost_per_click', 'cost_per_acquisition', 'is_active',
            
            # Campaign
            'campaign', 'campaign_name',
            
            # Placements
            'placement_assignments',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'advertiser', 'advertiser_name', 'impressions', 'clicks', 'conversions',
            'amount_spent', 'click_through_rate', 'conversion_rate', 'cost_per_click',
            'cost_per_acquisition', 'is_active', 'approved_by', 'approved_at',
            'campaign_name', 'placement_assignments', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Comprehensive validation for advertisements"""
        
        # Validate date range
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
            
            if data['start_date'] < timezone.now():
                raise serializers.ValidationError("Start date cannot be in the past")
        
        # Validate budget constraints
        budget = data.get('budget', Decimal('0'))
        daily_budget = data.get('daily_budget')
        
        if budget <= Decimal('0'):
            raise serializers.ValidationError("Budget must be greater than 0")
        
        if daily_budget and daily_budget > budget:
            raise serializers.ValidationError("Daily budget cannot exceed total budget")
        
        # Validate targeting configuration
        target_audience = data.get('target_audience', {})
        if target_audience:
            required_fields = ['age_range', 'interests']
            for field in required_fields:
                if field not in target_audience:
                    raise serializers.ValidationError(f"Target audience must include {field}")
        
        # Validate creative assets
        banner_image = data.get('banner_image_url')
        if not banner_image:
            raise serializers.ValidationError("Banner image is required")
        
        return data
    
    def create(self, validated_data):
        """Create advertisement with proper user assignment"""
        validated_data['advertiser'] = self.context['request'].user
        return super().create(validated_data)

class AdvertisementCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating advertisements"""
    
    placement_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of placement IDs for this advertisement"
    )
    
    class Meta:
        model = Advertisement
        fields = [
            'title', 'description', 'ad_type', 'target_audience',
            'geographic_targeting', 'demographic_targeting', 'product_categories',
            'banner_image_url', 'banner_mobile_url', 'video_url',
            'landing_page_url', 'call_to_action', 'budget', 'daily_budget',
            'bid_amount', 'pricing_model', 'currency', 'start_date', 'end_date',
            'campaign', 'placement_ids'
        ]
    
    def create(self, validated_data):
        """Create advertisement with placements"""
        placement_ids = validated_data.pop('placement_ids', [])
        validated_data['advertiser'] = self.context['request'].user
        
        advertisement = Advertisement.objects.create(**validated_data)
        
        # Create placement assignments
        for placement_id in placement_ids:
            try:
                placement = AdvertisementPlacement.objects.get(id=placement_id, is_active=True)
                AdvertisementPlacementAssignment.objects.create(
                    advertisement=advertisement,
                    placement=placement,
                    priority=1
                )
            except AdvertisementPlacement.DoesNotExist:
                continue
        
        return advertisement

class AdvertisementCampaignSerializer(serializers.ModelSerializer):
    """Serializer for advertisement campaigns"""
    
    # Calculated fields
    advertisements_count = serializers.ReadOnlyField()
    total_spent = serializers.ReadOnlyField()
    total_impressions = serializers.ReadOnlyField()
    total_clicks = serializers.ReadOnlyField()
    
    # Manager info
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    
    # Nested advertisements (optional)
    advertisements = AdvertisementSerializer(many=True, read_only=True)
    
    class Meta:
        model = AdvertisementCampaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'manager', 'manager_name',
            'total_budget', 'start_date', 'end_date', 'target_impressions',
            'target_clicks', 'target_conversions', 'target_ctr', 'is_active',
            'advertisements_count', 'total_spent', 'total_impressions', 'total_clicks',
            'advertisements', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'manager', 'manager_name', 'advertisements_count', 'total_spent',
            'total_impressions', 'total_clicks', 'advertisements', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create campaign with proper user assignment"""
        validated_data['manager'] = self.context['request'].user
        return super().create(validated_data)

class AdvertisementStatsSerializer(serializers.Serializer):
    """Serializer for advertisement statistics"""
    
    total_advertisements = serializers.IntegerField()
    active_advertisements = serializers.IntegerField()
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    
    # Performance metrics
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_conversions = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Calculated metrics
    overall_ctr = serializers.DecimalField(max_digits=5, decimal_places=2)
    overall_conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_cpc = serializers.DecimalField(max_digits=8, decimal_places=4)
    
    # Top performing ads
    top_ads_by_ctr = AdvertisementSerializer(many=True, read_only=True)
    top_ads_by_conversions = AdvertisementSerializer(many=True, read_only=True)

class AdvertisementPerformanceSerializer(serializers.Serializer):
    """Serializer for detailed performance analytics"""
    
    advertisement_id = serializers.UUIDField()
    date_range = serializers.CharField()
    
    # Time series data
    daily_metrics = serializers.ListField(
        child=serializers.DictField(),
        help_text="Daily performance metrics"
    )
    
    # Aggregated metrics
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_conversions = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Performance indicators
    ctr = serializers.DecimalField(max_digits=5, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    cpc = serializers.DecimalField(max_digits=8, decimal_places=4)
    cpa = serializers.DecimalField(max_digits=8, decimal_places=4)
    roi = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Audience insights
    top_demographics = serializers.DictField()
    geographic_breakdown = serializers.DictField()
    device_breakdown = serializers.DictField()
    
    # Recommendations
    optimization_recommendations = serializers.ListField(
        child=serializers.CharField(),
        help_text="AI-powered optimization suggestions"
    )
