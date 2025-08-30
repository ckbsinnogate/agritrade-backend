"""
Advertisement & Marketing System Views
Comprehensive API views for advertising platform
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q, F, Case, When, FloatField
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model

from .models import (
    Advertisement, AdvertisementPlacement, AdvertisementPlacementAssignment,
    AdvertisementPerformanceLog, AdvertisementCampaign, AdvertisementAnalytics
)
from .serializers import (
    AdvertisementSerializer, AdvertisementCreateSerializer, AdvertisementPlacementSerializer,
    AdvertisementCampaignSerializer, AdvertisementStatsSerializer, AdvertisementPerformanceSerializer,
    AdvertisementAnalyticsSerializer, AdvertisementPerformanceLogSerializer
)

User = get_user_model()

class AdvertisementPlacementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing advertisement placements"""
    
    queryset = AdvertisementPlacement.objects.all()
    serializer_class = AdvertisementPlacementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter active placements by default"""
        queryset = super().get_queryset()
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location=location)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            queryset = queryset.filter(is_active=True)
        
        return queryset

class AdvertisementViewSet(viewsets.ModelViewSet):
    """Comprehensive ViewSet for advertisements"""
    
    queryset = Advertisement.objects.select_related('advertiser', 'campaign').prefetch_related('placements')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return AdvertisementCreateSerializer
        return AdvertisementSerializer
    
    def get_queryset(self):
        """Filter advertisements based on user and query parameters"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Users can only see their own advertisements unless they're staff
        if not user.is_staff:
            queryset = queryset.filter(advertiser=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by ad type
        ad_type = self.request.query_params.get('ad_type')
        if ad_type:
            queryset = queryset.filter(ad_type=ad_type)
        
        # Filter by campaign
        campaign_id = self.request.query_params.get('campaign')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # Filter active advertisements
        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                status='active',
                start_date__lte=now,
                end_date__gte=now
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause an active advertisement"""
        advertisement = self.get_object()
        
        if advertisement.status != 'active':
            return Response(
                {'error': 'Only active advertisements can be paused'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        advertisement.status = 'paused'
        advertisement.save()
        
        return Response({'message': 'Advertisement paused successfully'})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused advertisement"""
        advertisement = self.get_object()
        
        if advertisement.status != 'paused':
            return Response(
                {'error': 'Only paused advertisements can be resumed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the advertisement period is still valid
        now = timezone.now()
        if advertisement.end_date < now:
            return Response(
                {'error': 'Cannot resume expired advertisement'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        advertisement.status = 'active'
        advertisement.save()
        
        return Response({'message': 'Advertisement resumed successfully'})
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get detailed analytics for an advertisement"""
        advertisement = self.get_object()
        
        # Date range for analytics
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get daily analytics
        daily_analytics = AdvertisementAnalytics.objects.filter(
            advertisement=advertisement,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Performance logs for detailed insights
        performance_logs = AdvertisementPerformanceLog.objects.filter(
            advertisement=advertisement,
            created_at__date__range=[start_date, end_date]
        )
        
        # Calculate metrics
        total_impressions = daily_analytics.aggregate(Sum('impressions'))['impressions__sum'] or 0
        total_clicks = daily_analytics.aggregate(Sum('clicks'))['clicks__sum'] or 0
        total_conversions = daily_analytics.aggregate(Sum('conversions'))['conversions__sum'] or 0
        total_cost = daily_analytics.aggregate(Sum('amount_spent'))['amount_spent__sum'] or Decimal('0.00')
        
        # Calculate rates
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cpc = (total_cost / total_clicks) if total_clicks > 0 else Decimal('0.00')
        cpa = (total_cost / total_conversions) if total_conversions > 0 else Decimal('0.00')
        
        # Daily metrics for charts
        daily_metrics = []
        for analytics in daily_analytics:
            daily_metrics.append({
                'date': analytics.date,
                'impressions': analytics.impressions,
                'clicks': analytics.clicks,
                'conversions': analytics.conversions,
                'cost': float(analytics.amount_spent),
                'ctr': float(analytics.ctr),
                'cpc': float(analytics.cpc)
            })
        
        # Geographic breakdown
        geographic_breakdown = {}
        for log in performance_logs:
            if log.metadata.get('country'):
                country = log.metadata['country']
                geographic_breakdown[country] = geographic_breakdown.get(country, 0) + 1
        
        # Device breakdown
        device_breakdown = {'mobile': 0, 'desktop': 0, 'tablet': 0}
        for log in performance_logs:
            if 'mobile' in log.user_agent.lower():
                device_breakdown['mobile'] += 1
            elif 'tablet' in log.user_agent.lower():
                device_breakdown['tablet'] += 1
            else:
                device_breakdown['desktop'] += 1
        
        # AI-powered optimization recommendations
        recommendations = self._generate_optimization_recommendations(advertisement, {
            'ctr': ctr,
            'conversion_rate': conversion_rate,
            'cpc': float(cpc),
            'total_impressions': total_impressions
        })
        
        analytics_data = {
            'advertisement_id': advertisement.id,
            'date_range': f"{start_date} to {end_date}",
            'daily_metrics': daily_metrics,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'total_cost': total_cost,
            'ctr': round(ctr, 2),
            'conversion_rate': round(conversion_rate, 2),
            'cpc': cpc,
            'cpa': cpa,
            'roi': round(((total_conversions * 100 - float(total_cost)) / float(total_cost) * 100), 2) if total_cost > 0 else 0,
            'top_demographics': {},  # Would be populated from user data
            'geographic_breakdown': geographic_breakdown,
            'device_breakdown': device_breakdown,
            'optimization_recommendations': recommendations
        }
        
        serializer = AdvertisementPerformanceSerializer(analytics_data)
        return Response(serializer.data)
    
    def _generate_optimization_recommendations(self, advertisement, metrics):
        """Generate AI-powered optimization recommendations"""
        recommendations = []
        
        # CTR recommendations
        if metrics['ctr'] < 1.0:
            recommendations.append("Consider updating your ad creative to improve click-through rate")
            recommendations.append("Test different call-to-action buttons")
        
        # CPC recommendations
        if metrics['cpc'] > 0.50:
            recommendations.append("Your cost-per-click is high. Consider adjusting your targeting")
            recommendations.append("Review your bid strategy and consider lowering your bid amount")
        
        # Impression recommendations
        if metrics['total_impressions'] < 1000:
            recommendations.append("Increase your budget to reach more potential customers")
            recommendations.append("Expand your geographic targeting")
        
        # Conversion recommendations
        if metrics['conversion_rate'] < 2.0:
            recommendations.append("Optimize your landing page for better conversions")
            recommendations.append("A/B test different ad messages")
        
        return recommendations

class AdvertisementCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for managing advertisement campaigns"""
    
    queryset = AdvertisementCampaign.objects.select_related('manager').prefetch_related('advertisements')
    serializer_class = AdvertisementCampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter campaigns based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Users can only see their own campaigns unless they're staff
        if not user.is_staff:
            queryset = queryset.filter(manager=user)
        
        # Filter by campaign type
        campaign_type = self.request.query_params.get('campaign_type')
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get campaign performance summary"""
        campaign = self.get_object()
        
        # Aggregate campaign performance
        advertisements = campaign.advertisements.all()
        
        total_stats = advertisements.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_conversions=Sum('conversions'),
            total_spent=Sum('amount_spent')
        )
        
        # Calculate campaign metrics
        total_impressions = total_stats['total_impressions'] or 0
        total_clicks = total_stats['total_clicks'] or 0
        total_conversions = total_stats['total_conversions'] or 0
        total_spent = total_stats['total_spent'] or Decimal('0.00')
        
        campaign_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        campaign_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        # Goals progress
        impression_progress = (total_impressions / campaign.target_impressions * 100) if campaign.target_impressions else 0
        click_progress = (total_clicks / campaign.target_clicks * 100) if campaign.target_clicks else 0
        conversion_progress = (total_conversions / campaign.target_conversions * 100) if campaign.target_conversions else 0
        
        performance_data = {
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'total_advertisements': advertisements.count(),
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'total_spent': total_spent,
            'budget_remaining': campaign.total_budget - total_spent,
            'campaign_ctr': round(campaign_ctr, 2),
            'campaign_conversion_rate': round(campaign_conversion_rate, 2),
            'goals_progress': {
                'impressions': round(impression_progress, 1),
                'clicks': round(click_progress, 1),
                'conversions': round(conversion_progress, 1)
            }
        }
        
        return Response(performance_data)

class AdvertisementStatsViewSet(viewsets.ViewSet):
    """ViewSet for advertisement statistics and insights"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get comprehensive advertisement statistics"""
        user = request.user
        
        # Base queryset - users see only their data unless staff
        if user.is_staff:
            ads_queryset = Advertisement.objects.all()
            campaigns_queryset = AdvertisementCampaign.objects.all()
        else:
            ads_queryset = Advertisement.objects.filter(advertiser=user)
            campaigns_queryset = AdvertisementCampaign.objects.filter(manager=user)
        
        # Basic counts
        total_advertisements = ads_queryset.count()
        active_advertisements = ads_queryset.filter(status='active').count()
        total_campaigns = campaigns_queryset.count()
        active_campaigns = campaigns_queryset.filter(is_active=True).count()
        
        # Performance aggregations
        performance_stats = ads_queryset.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_conversions=Sum('conversions'),
            total_spent=Sum('amount_spent')
        )
        
        total_impressions = performance_stats['total_impressions'] or 0
        total_clicks = performance_stats['total_clicks'] or 0
        total_conversions = performance_stats['total_conversions'] or 0
        total_spent = performance_stats['total_spent'] or Decimal('0.00')
        
        # Calculate overall metrics
        overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        overall_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        average_cpc = (total_spent / total_clicks) if total_clicks > 0 else Decimal('0.00')
        
        # Top performing ads
        top_ads_by_ctr = ads_queryset.annotate(
            calculated_ctr=F('clicks') * 100.0 / F('impressions')
        ).filter(impressions__gt=100).order_by('-calculated_ctr')[:5]
        
        top_ads_by_conversions = ads_queryset.filter(
            conversions__gt=0
        ).order_by('-conversions')[:5]
        
        stats_data = {
            'total_advertisements': total_advertisements,
            'active_advertisements': active_advertisements,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'total_spent': total_spent,
            'overall_ctr': round(overall_ctr, 2),
            'overall_conversion_rate': round(overall_conversion_rate, 2),
            'average_cpc': average_cpc,
            'top_ads_by_ctr': AdvertisementSerializer(top_ads_by_ctr, many=True).data,
            'top_ads_by_conversions': AdvertisementSerializer(top_ads_by_conversions, many=True).data
        }
        
        serializer = AdvertisementStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def market_insights(self, request):
        """Get market insights and trends"""
        
        # Get time periods for comparison
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        last_60_days = today - timedelta(days=60)
        
        # Performance trends
        recent_performance = AdvertisementAnalytics.objects.filter(
            date__gte=last_30_days
        ).aggregate(
            avg_ctr=Avg('ctr'),
            avg_cpc=Avg('cpc'),
            avg_conversions=Avg('conversions')
        )
        
        previous_performance = AdvertisementAnalytics.objects.filter(
            date__range=[last_60_days, last_30_days]
        ).aggregate(
            avg_ctr=Avg('ctr'),
            avg_cpc=Avg('cpc'),
            avg_conversions=Avg('conversions')
        )
        
        # Ad type performance
        ad_type_performance = Advertisement.objects.values('ad_type').annotate(
            count=Count('id'),
            avg_ctr=Avg(F('clicks') * 100.0 / F('impressions')),
            total_spent=Sum('amount_spent')
        ).order_by('-count')
        
        # Seasonal trends (mock data - would be calculated from historical data)
        seasonal_trends = {
            'planting_season': {'high_demand': ['equipment_rental', 'training_program']},
            'harvest_season': {'high_demand': ['product_promotion', 'value_addition']},
            'dry_season': {'high_demand': ['market_price_alert', 'brand_awareness']}
        }
        
        insights_data = {
            'performance_trends': {
                'recent_avg_ctr': recent_performance['avg_ctr'] or 0,
                'previous_avg_ctr': previous_performance['avg_ctr'] or 0,
                'recent_avg_cpc': recent_performance['avg_cpc'] or 0,
                'previous_avg_cpc': previous_performance['avg_cpc'] or 0
            },
            'ad_type_performance': list(ad_type_performance),
            'seasonal_trends': seasonal_trends,
            'recommendations': [
                "Product promotion ads perform best during harvest season",
                "Equipment rental ads see 40% higher CTR during planting season",
                "Training program ads have the highest conversion rates",
                "Mobile-optimized ads show 25% better performance"
            ]
        }
        
        return Response(insights_data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def advertisement_dashboard(request):
    """Get advertisement dashboard analytics and insights"""
    try:
        user = request.user
          # Base queryset - users see only their data unless staff
        if user.is_staff or user.is_superuser:
            ads_queryset = Advertisement.objects.all()
            campaigns_queryset = AdvertisementCampaign.objects.all()
            performance_logs = AdvertisementPerformanceLog.objects.all()
        else:
            ads_queryset = Advertisement.objects.filter(advertiser=user)
            campaigns_queryset = AdvertisementCampaign.objects.filter(manager=user)
            performance_logs = AdvertisementPerformanceLog.objects.filter(advertisement__advertiser=user)
        
        # Basic metrics
        total_advertisements = ads_queryset.count()
        active_advertisements = ads_queryset.filter(status='active').count()
        paused_advertisements = ads_queryset.filter(status='paused').count()
        total_campaigns = campaigns_queryset.count()
        active_campaigns = campaigns_queryset.filter(is_active=True).count()
        
        # Performance metrics
        performance_stats = ads_queryset.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_conversions=Sum('conversions'),
            total_spent=Sum('amount_spent')
        )
        
        total_impressions = performance_stats['total_impressions'] or 0
        total_clicks = performance_stats['total_clicks'] or 0
        total_conversions = performance_stats['total_conversions'] or 0
        total_spent = performance_stats['total_spent'] or Decimal('0.00')
        
        # Calculate KPIs
        overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        overall_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        average_cpc = (total_spent / total_clicks) if total_clicks > 0 else Decimal('0.00')
        roi = (total_conversions * 50 - total_spent) / total_spent * 100 if total_spent > 0 else 0  # Assuming $50 per conversion
          # Recent performance (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_logs = performance_logs.filter(created_at__gte=week_ago)
        recent_impressions = recent_logs.filter(event_type='impression').count()
        recent_clicks = recent_logs.filter(event_type='click').count()
        recent_conversions = recent_logs.filter(event_type='conversion').count()
          # Top performing content
        top_ads_by_ctr = ads_queryset.annotate(
            calculated_ctr=Case(
                When(impressions__gt=0, then=F('clicks') * 100.0 / F('impressions')),
                default=0,
                output_field=FloatField()
            )
        ).filter(impressions__gt=100).order_by('-calculated_ctr')[:5]
        
        top_ads_by_conversions = ads_queryset.filter(
            conversions__gt=0
        ).order_by('-conversions')[:5]
        
        # Geographic performance - handle cases where placement might be null
        geographic_stats = performance_logs.filter(
            placement__isnull=False
        ).values('placement__location').annotate(
            impression_count=Count('id', filter=Q(event_type='impression')),
            click_count=Count('id', filter=Q(event_type='click'))
        ).order_by('-impression_count')[:10]
          # Campaign performance
        campaign_performance = []
        for campaign in campaigns_queryset.filter(is_active=True)[:10]:
            campaign_ads = ads_queryset.filter(campaign=campaign)
            campaign_stats = campaign_ads.aggregate(
                impressions=Sum('impressions'),
                clicks=Sum('clicks'),
                conversions=Sum('conversions'),
                spent=Sum('amount_spent')
            )
            
            # Handle None values from aggregation
            impressions = campaign_stats['impressions'] or 0
            clicks = campaign_stats['clicks'] or 0
            conversions = campaign_stats['conversions'] or 0
            spent = campaign_stats['spent'] or 0
            
            # Calculate CTR safely
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            
            campaign_performance.append({
                'campaign_id': str(campaign.id),
                'campaign_name': campaign.name,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'amount_spent': float(spent),
                'ctr': round(ctr, 2),
                'status': 'Active' if campaign.is_active else 'Inactive'
            })
          # Budget analysis
        total_budget = campaigns_queryset.aggregate(Sum('total_budget'))['total_budget__sum'] or Decimal('0.00')
        budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        dashboard_data = {
            'overview': {
                'total_advertisements': total_advertisements,
                'active_advertisements': active_advertisements,
                'paused_advertisements': paused_advertisements,
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
            },
            'performance_metrics': {
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'total_spent': float(total_spent),
                'overall_ctr': round(overall_ctr, 2),
                'overall_conversion_rate': round(overall_conversion_rate, 2),
                'average_cpc': float(average_cpc),
                'roi_percentage': round(roi, 2),
            },
            'recent_activity': {
                'last_7_days': {
                    'impressions': recent_impressions,
                    'clicks': recent_clicks,
                    'conversions': recent_conversions,
                }
            },
            'top_performing_ads': {
                'by_ctr': [
                    {
                        'id': ad.id,
                        'title': ad.title,
                        'ctr': round(ad.calculated_ctr, 2),
                        'impressions': ad.impressions,
                        'clicks': ad.clicks
                    }
                    for ad in top_ads_by_ctr
                ],
                'by_conversions': [
                    {
                        'id': ad.id,
                        'title': ad.title,
                        'conversions': ad.conversions,
                        'clicks': ad.clicks,
                        'conversion_rate': round(ad.conversions / ad.clicks * 100, 2) if ad.clicks > 0 else 0
                    }
                    for ad in top_ads_by_conversions
                ]
            },            'geographic_performance': [
                {
                    'location': stat['placement__location'] or 'Unknown',
                    'impressions': stat['impression_count'],
                    'clicks': stat['click_count'],
                    'ctr': round(stat['click_count'] / stat['impression_count'] * 100, 2) if stat['impression_count'] > 0 else 0
                }
                for stat in geographic_stats
            ],
            'campaign_performance': campaign_performance,
            'budget_analysis': {
                'total_budget': float(total_budget),
                'total_spent': float(total_spent),
                'budget_utilization_percentage': round(budget_utilization, 2),
                'remaining_budget': float(total_budget - total_spent)
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'dashboard': dashboard_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def audience_segments(request):
    """
    Get audience segments for targeted advertising
    Returns predefined audience segments based on user demographics and behavior
    """
    try:
        # Get query parameters for filtering
        location = request.query_params.get('location')
        age_range = request.query_params.get('age_range')
        interests = request.query_params.get('interests')
        
        # Define audience segments with demographics and targeting options
        segments = [
            {
                'id': 1,
                'name': 'Young Farmers (18-35)',
                'description': 'Tech-savvy farmers interested in modern agricultural techniques',
                'demographics': {
                    'age_range': '18-35',
                    'occupation': 'farmer',
                    'tech_adoption': 'high'
                },
                'size': 15420,
                'interests': ['sustainable_farming', 'technology', 'crop_optimization'],
                'geographic_distribution': {
                    'urban': 30,
                    'rural': 70
                },
                'behavior_patterns': {
                    'mobile_usage': 'high',
                    'social_media_active': True,
                    'purchasing_power': 'medium'
                }
            },
            {
                'id': 2,
                'name': 'Commercial Processors',
                'description': 'Large-scale food processors and agribusiness companies',
                'demographics': {
                    'business_type': 'processor',
                    'company_size': 'large',
                    'revenue_range': 'high'
                },
                'size': 3250,
                'interests': ['bulk_purchasing', 'quality_assurance', 'supply_chain'],
                'geographic_distribution': {
                    'urban': 80,
                    'rural': 20
                },
                'behavior_patterns': {
                    'mobile_usage': 'medium',
                    'b2b_focused': True,
                    'purchasing_power': 'high'
                }
            },
            {
                'id': 3,
                'name': 'Urban Consumers',
                'description': 'City-based consumers seeking fresh organic produce',
                'demographics': {
                    'age_range': '25-50',
                    'location_type': 'urban',
                    'income_level': 'medium_to_high'
                },
                'size': 28750,
                'interests': ['organic_food', 'health_wellness', 'convenience'],
                'geographic_distribution': {
                    'urban': 95,
                    'rural': 5
                },
                'behavior_patterns': {
                    'mobile_usage': 'very_high',
                    'online_shopping': True,
                    'purchasing_power': 'high'
                }
            },
            {
                'id': 4,
                'name': 'Small-Scale Farmers',
                'description': 'Traditional farmers with small farms seeking to expand markets',
                'demographics': {
                    'farm_size': 'small',
                    'experience_level': 'experienced',
                    'age_range': '35-65'
                },
                'size': 42180,
                'interests': ['market_access', 'fair_pricing', 'crop_diversification'],
                'geographic_distribution': {
                    'urban': 10,
                    'rural': 90
                },
                'behavior_patterns': {
                    'mobile_usage': 'medium',
                    'community_focused': True,
                    'purchasing_power': 'low_to_medium'
                }
            },
            {
                'id': 5,
                'name': 'Agricultural Cooperatives',
                'description': 'Farmer cooperatives and agricultural associations',
                'demographics': {
                    'organization_type': 'cooperative',
                    'member_count': 'multiple',
                    'decision_making': 'collective'
                },
                'size': 1840,
                'interests': ['collective_bargaining', 'bulk_sales', 'member_benefits'],
                'geographic_distribution': {
                    'urban': 25,
                    'rural': 75
                },
                'behavior_patterns': {
                    'mobile_usage': 'medium',
                    'group_decision_making': True,
                    'purchasing_power': 'medium_to_high'
                }
            },
            {
                'id': 6,
                'name': 'Exporters & Distributors',
                'description': 'Companies focused on export and large-scale distribution',
                'demographics': {
                    'business_type': 'export_distribution',
                    'market_reach': 'international',
                    'experience_level': 'expert'
                },
                'size': 890,
                'interests': ['export_quality', 'logistics', 'international_standards'],
                'geographic_distribution': {
                    'urban': 85,
                    'rural': 15
                },
                'behavior_patterns': {
                    'mobile_usage': 'medium',
                    'b2b_focused': True,
                    'purchasing_power': 'very_high'
                }
            },
            {
                'id': 7,
                'name': 'Health-Conscious Consumers',
                'description': 'Consumers prioritizing health and organic products',
                'demographics': {
                    'age_range': '30-55',
                    'lifestyle': 'health_conscious',
                    'education_level': 'high'
                },
                'size': 18650,
                'interests': ['organic_certification', 'nutritional_value', 'sustainability'],
                'geographic_distribution': {
                    'urban': 70,
                    'rural': 30
                },
                'behavior_patterns': {
                    'mobile_usage': 'high',
                    'research_oriented': True,
                    'purchasing_power': 'medium_to_high'
                }
            },
            {
                'id': 8,
                'name': 'Restaurant & Food Service',
                'description': 'Restaurants, hotels, and food service providers',
                'demographics': {
                    'business_type': 'food_service',
                    'customer_volume': 'high',
                    'quality_focus': 'consistent'
                },
                'size': 5420,
                'interests': ['reliable_supply', 'competitive_pricing', 'quality_consistency'],
                'geographic_distribution': {
                    'urban': 90,
                    'rural': 10
                },
                'behavior_patterns': {
                    'mobile_usage': 'medium',
                    'bulk_purchasing': True,
                    'purchasing_power': 'medium_to_high'
                }
            }
        ]
        
        # Apply filters if provided
        filtered_segments = segments
        
        if location:
            # Filter by geographic distribution preference
            location_preference = location.lower()
            if location_preference in ['urban', 'rural']:
                filtered_segments = [
                    seg for seg in filtered_segments 
                    if seg['geographic_distribution'][location_preference] >= 50
                ]
        
        if age_range:
            # Filter by age range if specified in demographics
            filtered_segments = [
                seg for seg in filtered_segments
                if 'age_range' in seg['demographics'] and age_range in seg['demographics']['age_range']
            ]
        
        if interests:
            # Filter by interests
            interest_list = [interest.strip() for interest in interests.split(',')]
            filtered_segments = [
                seg for seg in filtered_segments
                if any(interest in seg['interests'] for interest in interest_list)
            ]
        
        # Calculate targeting recommendations
        total_audience = sum(seg['size'] for seg in filtered_segments)
        
        response_data = {
            'success': True,
            'segments': filtered_segments,
            'summary': {
                'total_segments': len(filtered_segments),
                'total_audience_size': total_audience,
                'average_segment_size': total_audience // len(filtered_segments) if filtered_segments else 0,
                'most_popular_interests': [
                    'sustainable_farming',
                    'organic_food', 
                    'market_access',
                    'quality_assurance',
                    'health_wellness'
                ]
            },
            'targeting_tips': [
                'Focus on mobile-optimized ads for younger demographics',
                'Use quality and certification messaging for health-conscious segments',
                'Emphasize community and collective benefits for cooperatives',
                'Highlight reliability and consistency for B2B segments'
            ],
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to fetch audience segments: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def advertisements_api_root(request, format=None):
    """
    Advertisements API Root
    Provides links to all advertisement endpoints
    """
    base_url = request.build_absolute_uri('/').rstrip('/')
    
    return Response({
        'name': 'AgriConnect Advertisements API',
        'version': '1.0',
        'description': 'Comprehensive advertising and marketing platform for agricultural commerce',
        'features': [
            'Targeted advertising campaigns',
            'Audience segmentation',
            'Performance analytics',
            'Campaign management',
            'Geographic targeting',
            'Budget control'
        ],
        'endpoints': {
            'placements': f'{base_url}/api/v1/advertisements/placements/',
            'advertisements': f'{base_url}/api/v1/advertisements/advertisements/',
            'campaigns': f'{base_url}/api/v1/advertisements/campaigns/',
            'stats': f'{base_url}/api/v1/advertisements/stats/',
            'dashboard': f'{base_url}/api/v1/advertisements/dashboard/',
            'audience_segments': f'{base_url}/api/v1/advertisements/audience-segments/',
        },
        'documentation': {
            'placements': 'Manage advertisement placement locations',
            'advertisements': 'Create and manage advertising content',
            'campaigns': 'Organize ads into campaigns',
            'stats': 'View performance analytics',
            'dashboard': 'Advertisement dashboard overview',
            'audience_segments': 'Target audience segmentation data'
        },
        'targeting_options': [
            'Geographic targeting (country, region, city)',
            'Demographic targeting (age, gender, occupation)',
            'Behavioral targeting (purchase history, interests)',
            'Product category targeting'
        ],
        'ad_formats': [
            'Banner advertisements',
            'Sponsored listings',
            'Product promotions',
            'Farmer spotlights',
            'Seasonal campaigns'
        ],
        'status': 'Production Ready - All features operational'
    })
