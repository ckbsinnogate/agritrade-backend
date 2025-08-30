"""
Farmer Dashboard Views
Comprehensive farmer dashboard backend API endpoints
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging

from .models import FarmerDashboardPreferences, FarmerAlert, FarmerDashboardMetrics, FarmerGoal
from .serializers import (
    FarmerDashboardPreferencesSerializer, FarmerAlertSerializer,
    FarmerDashboardMetricsSerializer, FarmerGoalSerializer,
    FarmerOverviewSerializer, FarmerProductSummarySerializer,
    FarmerOrderSummarySerializer, FarmerFarmSummarySerializer,
    WeatherInsightSerializer, MarketInsightSerializer
)

# Import existing models from other apps
try:
    from products.models import Product
    from orders.models import Order, OrderItem
    from traceability.models import Farm
    from authentication.models import User
    from users.models import FarmerProfile
except ImportError as e:
    logging.warning(f"Could not import some models: {e}")

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def farmer_dashboard_api_root(request, format=None):
    """Farmer Dashboard API Root"""
    return Response({
        'message': 'AgriConnect Farmer Dashboard API',
        'version': '1.0',
        'description': 'Comprehensive farmer dashboard backend APIs',
        'endpoints': {
            'overview': '/api/v1/farmer-dashboard/overview/',
            'products': '/api/v1/farmer-dashboard/products/',
            'orders': '/api/v1/farmer-dashboard/orders/',
            'farms': '/api/v1/farmer-dashboard/farms/',
            'weather': '/api/v1/farmer-dashboard/weather/',
            'market_insights': '/api/v1/farmer-dashboard/market-insights/',
            'alerts': '/api/v1/farmer-dashboard/alerts/',
            'preferences': '/api/v1/farmer-dashboard/preferences/',
            'metrics': '/api/v1/farmer-dashboard/metrics/',
            'goals': '/api/v1/farmer-dashboard/goals/',
        },
        'sections': {
            'Add Product': 'Use existing products API with farmer dashboard integration',
            'Overview': 'Complete farmer metrics and analytics',
            'My Products': 'Farmer-specific product management',
            'Orders': 'Order management and tracking',
            'Weather': 'Weather insights and alerts',
            'Market Insights': 'AI-powered market analysis',
            'My Farms': 'Farm registration and management'
        }
    })


class FarmerDashboardOverviewView(APIView):
    """Farmer Dashboard Overview - Main dashboard view"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive farmer dashboard overview"""
        try:
            farmer = request.user
            today = timezone.now().date()
            week_start = today - timedelta(days=7)
            month_start = today - timedelta(days=30)
            year_start = today - timedelta(days=365)
            
            # Revenue calculations
            try:
                orders = Order.objects.filter(seller=farmer)
                today_revenue = orders.filter(order_date__date=today).aggregate(
                    total=Sum('total_amount'))['total'] or Decimal('0')
                week_revenue = orders.filter(order_date__date__gte=week_start).aggregate(
                    total=Sum('total_amount'))['total'] or Decimal('0')
                month_revenue = orders.filter(order_date__date__gte=month_start).aggregate(
                    total=Sum('total_amount'))['total'] or Decimal('0')
                year_revenue = orders.filter(order_date__date__gte=year_start).aggregate(
                    total=Sum('total_amount'))['total'] or Decimal('0')
            except Exception as e:
                logger.warning(f"Could not calculate revenue: {e}")
                today_revenue = week_revenue = month_revenue = year_revenue = Decimal('0')
            
            # Order statistics
            try:
                pending_orders = Order.objects.filter(seller=farmer, status='pending').count()
                completed_orders = Order.objects.filter(seller=farmer, status='completed').count()
                cancelled_orders = Order.objects.filter(seller=farmer, status='cancelled').count()
                total_orders = Order.objects.filter(seller=farmer).count()
            except Exception as e:
                logger.warning(f"Could not calculate orders: {e}")
                pending_orders = completed_orders = cancelled_orders = total_orders = 0
              # Product statistics
            try:
                products = Product.objects.filter(seller=farmer)
                total_products = products.count()
                active_products = products.filter(status='active').count()
                low_stock_products = products.filter(stock_quantity__lte=5, stock_quantity__gt=0).count()
                out_of_stock_products = products.filter(stock_quantity=0).count()
            except Exception as e:
                logger.warning(f"Could not calculate products: {e}")
                total_products = active_products = low_stock_products = out_of_stock_products = 0
            
            # Farm statistics
            try:
                farms = Farm.objects.filter(farmer=farmer)
                total_farms = farms.count()
                verified_farms = farms.filter(is_verified=True).count()
                total_farm_area = farms.aggregate(total=Sum('farm_size_hectares'))['total'] or Decimal('0')
            except Exception as e:
                logger.warning(f"Could not calculate farms: {e}")
                total_farms = verified_farms = 0
                total_farm_area = Decimal('0')
            
            # Customer statistics
            try:
                customers = Order.objects.filter(seller=farmer).values('buyer').distinct().count()
                repeat_customers = Order.objects.filter(seller=farmer).values('buyer').annotate(
                    order_count=Count('id')).filter(order_count__gt=1).count()
            except Exception as e:
                logger.warning(f"Could not calculate customers: {e}")
                customers = repeat_customers = 0
            
            # Recent activity
            recent_orders = []
            recent_products = []
            low_stock_alerts = []
            
            try:
                # Recent orders
                latest_orders = Order.objects.filter(seller=farmer).order_by('-order_date')[:5]
                for order in latest_orders:
                    recent_orders.append({
                        'id': str(order.id),
                        'order_number': order.order_number,
                        'buyer': order.buyer.username if order.buyer else 'Unknown',
                        'total_amount': float(order.total_amount),
                        'status': order.status,
                        'order_date': order.order_date.isoformat() if order.order_date else None
                    })
                  # Recent products
                latest_products = Product.objects.filter(seller=farmer).order_by('-created_at')[:5]
                for product in latest_products:
                    recent_products.append({
                        'id': str(product.id),
                        'name': product.name,
                        'price': float(product.price_per_unit),
                        'stock': product.stock_quantity,
                        'status': product.status
                    })
                
                # Low stock alerts
                low_stock = Product.objects.filter(seller=farmer, stock_quantity__lte=5)
                for product in low_stock:
                    low_stock_alerts.append({
                        'id': str(product.id),
                        'name': product.name,
                        'current_stock': product.stock_quantity,
                        'status': 'low_stock' if product.stock_quantity > 0 else 'out_of_stock'
                    })
                    
            except Exception as e:
                logger.warning(f"Could not fetch recent activity: {e}")
            
            # Goals progress
            active_goals = []
            try:
                goals = FarmerGoal.objects.filter(farmer=farmer, status='active')[:3]
                for goal in goals:
                    active_goals.append({
                        'id': str(goal.id),
                        'title': goal.title,
                        'progress': float(goal.progress_percentage),
                        'target_value': float(goal.target_value),
                        'current_value': float(goal.current_value),
                        'days_remaining': goal.days_remaining
                    })
            except Exception as e:
                logger.warning(f"Could not fetch goals: {e}")
            
            # Market insights
            trending_crops = [
                {'name': 'Tomatoes', 'growth': 15.2, 'demand': 'high'},
                {'name': 'Maize', 'growth': 8.7, 'demand': 'medium'},
                {'name': 'Rice', 'growth': 12.1, 'demand': 'high'}
            ]
            
            price_trends = [
                {'crop': 'Tomatoes', 'current_price': 4.50, 'change': 12.5},
                {'crop': 'Maize', 'current_price': 2.80, 'change': -3.2},
                {'crop': 'Rice', 'current_price': 6.20, 'change': 8.1}
            ]
            
            # Weather alerts
            weather_alerts = [
                {'type': 'rainfall', 'message': 'Heavy rainfall expected this week', 'severity': 'medium'},
                {'type': 'temperature', 'message': 'Optimal growing temperature', 'severity': 'low'}
            ]
            
            # Performance metrics
            avg_order_value = Decimal('0')
            try:
                avg_order_value = Order.objects.filter(seller=farmer).aggregate(
                    avg=Avg('total_amount'))['avg'] or Decimal('0')
            except Exception:
                pass
            
            overview_data = {
                'today_revenue': today_revenue,
                'week_revenue': week_revenue,
                'month_revenue': month_revenue,
                'year_revenue': year_revenue,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'total_orders': total_orders,
                'total_products': total_products,
                'active_products': active_products,
                'low_stock_products': low_stock_products,
                'out_of_stock_products': out_of_stock_products,
                'total_farms': total_farms,
                'verified_farms': verified_farms,
                'total_farm_area': total_farm_area,
                'total_customers': customers,
                'repeat_customers': repeat_customers,
                'recent_orders': recent_orders,
                'recent_products': recent_products,
                'low_stock_alerts': low_stock_alerts,
                'active_goals': active_goals,
                'trending_crops': trending_crops,
                'price_trends': price_trends,
                'weather_alerts': weather_alerts,
                'average_order_value': avg_order_value,
                'customer_satisfaction': Decimal('4.5'),
                'revenue_growth': Decimal('15.8')
            }
            
            serializer = FarmerOverviewSerializer(overview_data)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Farmer dashboard overview retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in farmer dashboard overview: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve dashboard overview',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FarmerProductsView(APIView):
    """Farmer Products Management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get farmer's products with analytics"""
        try:
            farmer = request.user
            products_data = []
            
            try:
                products = Product.objects.filter(seller=farmer).order_by('-created_at')
                
                for product in products:
                    # Calculate sales data
                    try:
                        order_items = OrderItem.objects.filter(product=product)
                        total_sales = order_items.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
                        orders_count = order_items.count()
                        avg_rating = Decimal('4.2')  # Placeholder for rating calculation
                    except Exception:
                        total_sales = Decimal('0')
                        orders_count = 0
                        avg_rating = Decimal('0')
                    
                    products_data.append({
                        'id': str(product.id),
                        'name': product.name,
                        'category': product.category.name if product.category else 'Uncategorized',
                        'price_per_unit': product.price_per_unit,
                        'quantity_available': product.stock_quantity,
                        'unit': product.unit,
                        'status': product.status,
                        'total_sales': total_sales,
                        'orders_count': orders_count,
                        'average_rating': avg_rating,
                        'created_at': product.created_at,
                        'updated_at': product.updated_at
                    })
                    
            except Exception as e:
                logger.warning(f"Could not fetch products: {e}")
            
            return Response({
                'success': True,
                'count': len(products_data),
                'data': products_data,
                'message': 'Products retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in farmer products view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve products',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FarmerOrdersView(APIView):
    """Farmer Orders Management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get farmer's orders (sales)"""
        try:
            farmer = request.user
            orders_data = []
            
            try:
                orders = Order.objects.filter(seller=farmer).order_by('-order_date')
                
                for order in orders:
                    orders_data.append({
                        'id': str(order.id),
                        'order_number': order.order_number,
                        'buyer': order.buyer.username if order.buyer else 'Unknown',
                        'total_amount': order.total_amount,
                        'status': order.status,
                        'payment_status': order.payment_status,
                        'order_date': order.order_date,
                        'expected_delivery_date': order.expected_delivery_date,
                        'items_count': order.items.count(),
                        'delivery_city': order.delivery_city,
                        'delivery_region': order.delivery_region
                    })
                    
            except Exception as e:
                logger.warning(f"Could not fetch orders: {e}")
            
            return Response({
                'success': True,
                'count': len(orders_data),
                'data': orders_data,
                'message': 'Orders retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in farmer orders view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve orders',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FarmerFarmsView(APIView):
    """Farmer Farms Management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get farmer's farms"""
        try:
            farmer = request.user
            farms_data = []
            
            try:
                farms = Farm.objects.filter(farmer=farmer).order_by('-created_at')
                
                for farm in farms:
                    farms_data.append({
                        'id': str(farm.id),
                        'name': farm.name,
                        'location': farm.location,
                        'farm_size_hectares': farm.farm_size_hectares,
                        'organic_certified': farm.organic_certified,
                        'is_verified': farm.is_verified,
                        'primary_crops': farm.primary_crops or [],
                        'registration_number': farm.registration_number,
                        'created_at': farm.created_at
                    })
                    
            except Exception as e:
                logger.warning(f"Could not fetch farms: {e}")
            
            return Response({
                'success': True,
                'count': len(farms_data),
                'data': farms_data,
                'message': 'Farms retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in farmer farms view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve farms',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FarmerWeatherView(APIView):
    """Farmer Weather Insights"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get weather insights for farmer's location"""
        try:
            farmer = request.user
            
            # Get farmer's location (try different sources)
            location = "Ghana"  # Default
            try:
                if hasattr(farmer, 'farmerprofile'):
                    profile = farmer.farmerprofile
                    if hasattr(profile, 'location') and profile.location:
                        location = profile.location
                elif hasattr(farmer, 'farms') and farmer.farms.exists():
                    farm = farmer.farms.first()
                    if farm.location:
                        location = farm.location
            except Exception:
                pass
            
            # Mock weather data (integrate with real weather API)
            weather_data = {
                'location': location,
                'current_temperature': Decimal('28.5'),
                'humidity': Decimal('75.2'),
                'weather_condition': 'Partly Cloudy',
                'rainfall_prediction': Decimal('15.5'),
                'alerts': [
                    {
                        'type': 'rainfall',
                        'severity': 'medium',
                        'message': 'Moderate rainfall expected in the next 3 days',
                        'recommendations': ['Prepare irrigation systems', 'Monitor soil moisture']
                    }
                ],
                'recommendations': [
                    'Optimal time for planting tomatoes',
                    'Consider pest management for current weather',
                    'Monitor crop moisture levels'
                ],
                'forecast': [
                    {'day': 'Today', 'temp_high': 30, 'temp_low': 22, 'condition': 'Sunny'},
                    {'day': 'Tomorrow', 'temp_high': 28, 'temp_low': 20, 'condition': 'Cloudy'},
                    {'day': 'Day 3', 'temp_high': 26, 'temp_low': 19, 'condition': 'Rainy'}
                ]
            }
            
            serializer = WeatherInsightSerializer(weather_data)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Weather insights retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in farmer weather view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve weather insights',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FarmerMarketInsightsView(APIView):
    """Farmer Market Insights"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get AI-powered market insights"""
        try:
            # Mock market insights data (integrate with AI services)
            market_data = {
                'trending_products': [
                    {'name': 'Tomatoes', 'demand_score': 85, 'price_trend': 'increasing'},
                    {'name': 'Maize', 'demand_score': 72, 'price_trend': 'stable'},
                    {'name': 'Rice', 'demand_score': 68, 'price_trend': 'increasing'}
                ],
                'price_changes': [
                    {'product': 'Tomatoes', 'current_price': 4.50, 'change_percentage': 12.5, 'trend': 'up'},
                    {'product': 'Maize', 'current_price': 2.80, 'change_percentage': -3.2, 'trend': 'down'},
                    {'product': 'Rice', 'current_price': 6.20, 'change_percentage': 8.1, 'trend': 'up'}
                ],
                'demand_forecast': [
                    {'period': 'Next Week', 'demand_level': 'high', 'confidence': 89},
                    {'period': 'Next Month', 'demand_level': 'medium', 'confidence': 76},
                    {'period': 'Next Season', 'demand_level': 'high', 'confidence': 82}
                ],
                'competitor_analysis': [
                    {'competitor': 'Local Farm A', 'price_comparison': 'higher', 'market_share': 15},
                    {'competitor': 'Local Farm B', 'price_comparison': 'lower', 'market_share': 12}
                ],
                'opportunities': [
                    'High demand for organic tomatoes in urban areas',
                    'Export opportunities for premium rice varieties',
                    'Local processing facilities seeking maize suppliers'
                ],
                'recommendations': [
                    'Consider increasing tomato production by 20%',
                    'Focus on organic certification for premium pricing',
                    'Diversify into high-value vegetable crops'
                ]
            }
            
            serializer = MarketInsightSerializer(market_data)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Market insights retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in farmer market insights view: {e}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve market insights',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FarmerDashboardPreferencesViewSet(viewsets.ModelViewSet):
    """Farmer Dashboard Preferences Management"""
    serializer_class = FarmerDashboardPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FarmerDashboardPreferences.objects.filter(farmer=self.request.user)
    
    def perform_create(self, serializer):
        # Check if preferences already exist for this farmer
        existing_prefs = FarmerDashboardPreferences.objects.filter(farmer=self.request.user).first()
        if existing_prefs:
            # Update existing preferences instead of creating new ones
            for attr, value in serializer.validated_data.items():
                setattr(existing_prefs, attr, value)
            existing_prefs.save()
            return existing_prefs
        else:
            return serializer.save(farmer=self.request.user)


class FarmerAlertViewSet(viewsets.ModelViewSet):
    """Farmer Alerts Management"""
    serializer_class = FarmerAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = FarmerAlert.objects.filter(farmer=self.request.user)
        
        # Filter by status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        alert_type = self.request.query_params.get('type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        return Response({'message': 'Alert marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all alerts as read"""
        count = FarmerAlert.objects.filter(farmer=request.user, is_read=False).update(is_read=True)
        return Response({'message': f'{count} alerts marked as read'})


class FarmerGoalViewSet(viewsets.ModelViewSet):
    """Farmer Goals Management"""
    serializer_class = FarmerGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'target_date', 'progress_percentage']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = FarmerGoal.objects.filter(farmer=self.request.user)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update goal progress"""
        goal = self.get_object()
        current_value = request.data.get('current_value')
        
        if current_value is not None:
            goal.current_value = Decimal(str(current_value))
            
            # Check if goal is completed
            if goal.current_value >= goal.target_value and goal.status == 'active':
                goal.status = 'completed'
                goal.completed_at = timezone.now()
            
            goal.save()
            
            serializer = self.get_serializer(goal)
            return Response(serializer.data)
        
        return Response(
            {'error': 'current_value is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class FarmerDashboardMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """Farmer Dashboard Metrics (Read-only)"""
    serializer_class = FarmerDashboardMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FarmerDashboardMetrics.objects.filter(farmer=self.request.user)
