"""
AgriConnect Analytics Views
Comprehensive analytics and dashboard API endpoints with enhanced protection
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.cache import cache
import logging

# Import custom throttling for Institution Dashboard protection
try:
    from institution_dashboard.throttling import (
        InstitutionDashboardAnonThrottle, 
        InstitutionDashboardUserThrottle,
        InstitutionDashboardErrorHandler
    )
except ImportError:
    # Fallback if institution_dashboard not available
    InstitutionDashboardAnonThrottle = AnonRateThrottle
    InstitutionDashboardUserThrottle = UserRateThrottle
    InstitutionDashboardErrorHandler = None

# Import models from different apps
from products.models import Product, Category
from orders.models import Order, OrderItem
from payments.models import Transaction
from authentication.models import User, UserRole
from warehouses.models import Warehouse, WarehouseInventory
from ai.models import AIConversation, CropAdvisory, MarketIntelligence

# Set up logging
logger = logging.getLogger('analytics')

User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def analytics_api_root(request, format=None):
    """Analytics API Root - Comprehensive Dashboard Analytics"""
    return Response({
        'name': 'AgriConnect Analytics API',
        'version': '1.0',
        'description': 'Comprehensive analytics and dashboard data for all user roles',
        'endpoints': {
            'platform_stats': '/api/v1/analytics/platform/',
            'farmer_stats': '/api/v1/analytics/farmer-stats/',
            'dashboard_summary': '/api/v1/analytics/dashboard/',
            'market_insights': '/api/v1/analytics/market-insights/',
            'user_growth': '/api/v1/analytics/user-growth/',
            'revenue_analytics': '/api/v1/analytics/revenue/',
            'product_analytics': '/api/v1/analytics/products/',
            'order_analytics': '/api/v1/analytics/orders/',
        },
        'status': 'Analytics system operational with real-time data'
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def platform_stats(request):
    """Get comprehensive platform statistics"""
    try:
        # Calculate basic metrics
        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Transaction.objects.filter(
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
          # User breakdown by role
        user_roles = {}
        for role_choice in UserRole.ROLE_CHOICES:
            role_code = role_choice[0]
            role_name = role_choice[1]
            count = User.objects.filter(roles__name=role_code).count()
            user_roles[role_name] = count
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        recent_products = Product.objects.filter(created_at__gte=thirty_days_ago).count()
        recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # Product categories
        categories = Category.objects.annotate(
            product_count=Count('products')
        ).values('name', 'product_count')
        
        return Response({
            'success': True,
            'data': {
                'totals': {
                    'users': total_users,
                    'products': total_products,
                    'orders': total_orders,
                    'revenue': float(total_revenue)
                },
                'user_roles': user_roles,
                'recent_activity': {
                    'new_users_30_days': recent_users,
                    'new_products_30_days': recent_products,
                    'new_orders_30_days': recent_orders
                },
                'categories': list(categories),
                'generated_at': timezone.now().isoformat()
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def farmer_stats(request):
    """Get farmer-specific statistics and analytics"""
    try:
        user = request.user
        
        # Check if user has farmer role through many-to-many relationship
        user_roles = user.roles.values_list('name', flat=True)
        is_farmer = 'FARMER' in user_roles
        is_admin = 'ADMIN' in user_roles or user.is_staff or user.is_superuser
        
        # Only allow farmers or admins to access farmer stats
        if not (is_farmer or is_admin):
            return Response({
                'error': 'Access denied. This endpoint is for farmers and administrators only.',
                'user_roles': list(user_roles)
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get farmer's products
        if is_farmer and not is_admin:
            farmer_products = Product.objects.filter(seller=user)
        else:
            # Admin or staff can see all farmer stats
            farmer_id = request.GET.get('farmer_id')
            if farmer_id:
                try:
                    farmer_products = Product.objects.filter(seller_id=farmer_id)
                except Exception:
                    # Get products from users with farmer role
                    farmer_products = Product.objects.filter(seller__roles__name='FARMER')
            else:
                # Get products from users with farmer role
                farmer_products = Product.objects.filter(seller__roles__name='FARMER')
        
        # Calculate farmer metrics
        total_products = farmer_products.count()
        active_products = farmer_products.filter(status='active').count()
        total_views = farmer_products.aggregate(Sum('views_count'))['views_count__sum'] or 0
          # Sales data
        farmer_orders = OrderItem.objects.filter(product__in=farmer_products)
        total_sales = farmer_orders.count()
        total_revenue = farmer_orders.aggregate(
            total_revenue=Sum(F('quantity') * F('unit_price'))
        )['total_revenue'] or 0
        
        # Recent performance (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_sales = farmer_orders.filter(
            order__created_at__gte=thirty_days_ago
        ).count()
        recent_revenue = farmer_orders.filter(
            order__created_at__gte=thirty_days_ago
        ).aggregate(recent_revenue=Sum(F('quantity') * F('unit_price')))['recent_revenue'] or 0
        
        # Product performance
        top_products = farmer_products.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:5].values(
            'id', 'name', 'order_count', 'views_count', 'price_per_unit'
        )
        
        return Response({
            'success': True,
            'data': {
                'overview': {
                    'total_products': total_products,
                    'active_products': active_products,
                    'total_views': total_views,
                    'total_sales': total_sales,
                    'total_revenue': float(total_revenue)
                },
                'recent_performance': {
                    'sales_30_days': recent_sales,
                    'revenue_30_days': float(recent_revenue)
                },
                'top_products': list(top_products),
                'generated_at': timezone.now().isoformat()
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    """Get role-specific dashboard summary data"""
    try:
        user = request.user
        
        # Get user roles - handle different role structures
        user_roles = []
        primary_role = None
        
        try:
            if hasattr(user, 'roles') and user.roles.exists():
                user_roles = [role.name for role in user.roles.all()]
                primary_role = user_roles[0] if user_roles else None
            elif hasattr(user, 'role') and user.role:
                primary_role = user.role
                user_roles = [user.role]
        except Exception:
            # Fallback for any role-related errors
            primary_role = 'user'
            user_roles = ['user']
        
        # Base data for all users
        dashboard_data = {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'roles': user_roles,
                'primary_role': primary_role or 'user',
                'joined_date': user.date_joined.isoformat()
            },
            'notifications': [],
            'quick_stats': {},
            'recent_activity': []
        }
        
        # Role-specific data
        if primary_role == 'farmer' or 'farmer' in user_roles:
            # Farmer dashboard data
            try:
                my_products = Product.objects.filter(seller=user)
                my_orders = OrderItem.objects.filter(product__seller=user)
                
                dashboard_data['quick_stats'] = {
                    'total_products': my_products.count(),
                    'active_products': my_products.filter(status='active').count(),
                    'total_sales': my_orders.count(),
                    'pending_orders': my_orders.filter(order__status='pending').count()
                }
                
                # Recent activity for farmers
                recent_orders = my_orders.order_by('-order__created_at')[:5]
                dashboard_data['recent_activity'] = [
                    {
                        'type': 'order',
                        'description': f'Order for {item.product.name}',
                        'amount': float(item.quantity * item.unit_price),
                        'date': item.order.created_at.isoformat()
                    }
                    for item in recent_orders
                ]
            except Exception as e:
                # Handle any product/order related errors
                dashboard_data['quick_stats'] = {
                    'total_products': 0,
                    'active_products': 0,
                    'total_sales': 0,
                    'pending_orders': 0
                }
            
        elif primary_role == 'consumer' or 'consumer' in user_roles:
            # Consumer dashboard data
            try:
                my_orders = Order.objects.filter(buyer=user)
                
                dashboard_data['quick_stats'] = {
                    'total_orders': my_orders.count(),
                    'pending_orders': my_orders.filter(status='pending').count(),
                    'completed_orders': my_orders.filter(status='completed').count(),
                    'total_spent': float(my_orders.filter(
                        status='completed'
                    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
                }
            except Exception:
                dashboard_data['quick_stats'] = {
                    'total_orders': 0,
                    'pending_orders': 0,
                    'completed_orders': 0,
                    'total_spent': 0.0
                }
            
        elif primary_role == 'administrator' or 'administrator' in user_roles or user.is_staff:
            # Admin dashboard data
            try:
                dashboard_data['quick_stats'] = {
                    'total_users': User.objects.count(),
                    'total_products': Product.objects.count(),
                    'total_orders': Order.objects.count(),
                    'pending_orders': Order.objects.filter(status='pending').count()
                }
            except Exception:
                dashboard_data['quick_stats'] = {
                    'total_users': 0,
                    'total_products': 0,
                    'total_orders': 0,
                    'pending_orders': 0
                }
        else:
            # Default stats for other roles
            dashboard_data['quick_stats'] = {
                'user_type': primary_role or 'user',
                'account_status': 'active',
                'joined_days_ago': (timezone.now() - user.date_joined).days
            }
        
        return Response({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Dashboard error: {str(e)}',
            'fallback_data': {
                'user_info': {
                    'id': request.user.id if request.user.is_authenticated else None,
                    'username': request.user.username if request.user.is_authenticated else None,
                    'roles': [],
                    'primary_role': 'user'
                },
                'quick_stats': {},
                'recent_activity': [],
                'notifications': []
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def market_insights(request):
    """Get market insights and trends"""
    try:
        # Price trends by category
        category_stats = Category.objects.annotate(
            avg_price=Avg('products__price_per_unit'),
            product_count=Count('products'),
            total_sales=Count('products__orderitem')
        ).values('name', 'avg_price', 'product_count', 'total_sales')
        
        # Top selling products
        top_products = Product.objects.annotate(
            sales_count=Count('orderitem')
        ).order_by('-sales_count')[:10].values(
            'name', 'sales_count', 'price_per_unit', 'category__name'
        )
        
        # Recent market activity
        recent_orders = Order.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # AI insights count
        ai_insights = MarketIntelligence.objects.count()
        
        return Response({
            'success': True,
            'data': {
                'category_insights': list(category_stats),
                'top_products': list(top_products),
                'market_activity': {
                    'orders_last_7_days': recent_orders,
                    'ai_insights_generated': ai_insights
                },
                'generated_at': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_growth(request):
    """Get user growth analytics"""
    try:
        # User growth over the last 12 months
        twelve_months_ago = timezone.now() - timedelta(days=365)
        
        monthly_growth = []
        for i in range(12):
            month_start = twelve_months_ago + timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            new_users = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count()
            
            monthly_growth.append({
                'month': month_start.strftime('%Y-%m'),
                'new_users': new_users
            })
          # Role distribution over time
        role_distribution = {}
        for role_choice in UserRole.ROLE_CHOICES:
            role_code = role_choice[0]
            role_name = role_choice[1]
            count = User.objects.filter(roles__name=role_code).count()
            role_distribution[role_name] = count
        
        return Response({
            'success': True,
            'data': {
                'monthly_growth': monthly_growth,
                'role_distribution': role_distribution,
                'total_users': User.objects.count(),
                'generated_at': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def revenue_analytics(request):
    """Get revenue analytics and financial insights"""
    try:
        # Total revenue
        total_revenue = Transaction.objects.filter(
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Revenue by month (last 12 months)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        
        monthly_revenue = []
        for i in range(12):
            month_start = twelve_months_ago + timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_revenue = Transaction.objects.filter(
                status='completed',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            monthly_revenue.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': float(month_revenue)
            })
        
        # Revenue by category
        category_revenue = Category.objects.annotate(
            revenue=Sum('products__orderitem__quantity') * Sum('products__orderitem__unit_price')
        ).values('name', 'revenue')
        
        return Response({
            'success': True,
            'data': {
                'total_revenue': float(total_revenue),
                'monthly_revenue': monthly_revenue,
                'category_revenue': list(category_revenue),
                'generated_at': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_analytics(request):
    """Get product analytics and insights"""
    try:
        # Product performance metrics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(status='active').count()
        featured_products = Product.objects.filter(is_featured=True).count()
        
        # Category distribution
        category_distribution = Category.objects.annotate(
            product_count=Count('products')
        ).values('name', 'product_count')
        
        # Top viewed products
        top_viewed = Product.objects.order_by('-views_count')[:10].values(
            'name', 'views_count', 'category__name', 'seller__username'
        )
        
        # Price range analysis
        price_stats = Product.objects.aggregate(
            min_price=Count('price_per_unit'),
            max_price=Count('price_per_unit'),
            avg_price=Avg('price_per_unit')
        )
        
        return Response({
            'success': True,
            'data': {
                'overview': {
                    'total_products': total_products,
                    'active_products': active_products,
                    'featured_products': featured_products
                },
                'category_distribution': list(category_distribution),
                'top_viewed': list(top_viewed),
                'price_analysis': price_stats,
                'generated_at': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def order_analytics(request):
    """Get order analytics and insights"""
    try:
        # Order statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='completed').count()
        
        # Order trends (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # Daily order trends (last 7 days)
        daily_trends = []
        for i in range(7):
            day = timezone.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_orders = Order.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            daily_trends.append({
                'date': day.strftime('%Y-%m-%d'),
                'orders': day_orders
            })
        
        # Order value analysis
        order_values = Order.objects.filter(
            status='completed'
        ).aggregate(
            avg_order_value=Avg('total_amount'),
            total_order_value=Sum('total_amount')
        )
        
        return Response({
            'success': True,
            'data': {
                'overview': {
                    'total_orders': total_orders,
                    'pending_orders': pending_orders,
                    'completed_orders': completed_orders,
                    'recent_orders_30_days': recent_orders
                },
                'daily_trends': daily_trends,
                'value_analysis': {
                    'average_order_value': float(order_values['avg_order_value'] or 0),
                    'total_order_value': float(order_values['total_order_value'] or 0)
                },
                'generated_at': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([InstitutionDashboardUserThrottle])
def institution_members(request):
    """
    Get institution members and analytics with enhanced error handling
    """
    try:
        logger.info(f"Institution members request from user {request.user.username}")
        
        # Get user's institution
        institution_profile = getattr(request.user, 'institutionprofile', None)
        if not institution_profile:
            logger.warning(f"User {request.user.username} has no institution profile")
            if InstitutionDashboardErrorHandler:
                return InstitutionDashboardErrorHandler.handle_permission_error(request)
            return Response({
                'error': 'User is not associated with an institution',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all members of the institution
        members = User.objects.filter(
            Q(institutionprofile=institution_profile) |
            Q(institution_members=institution_profile)
        ).select_related('profile').prefetch_related('roles')

        # Member statistics
        member_stats = {
            'total_members': members.count(),
            'active_members': members.filter(is_active=True).count(),
            'recently_joined': members.filter(
                date_joined__gte=timezone.now() - timedelta(days=30)
            ).count()
        }

        # Role breakdown
        role_breakdown = {}
        for role_choice in UserRole.ROLE_CHOICES:
            role_code = role_choice[0]
            role_name = role_choice[1]
            count = members.filter(roles__name=role_code).count()
            if count > 0:
                role_breakdown[role_name] = count

        # Member activity (orders, purchases)
        member_activity = []
        for member in members[:10]:  # Top 10 most active
            try:
                orders_count = Order.objects.filter(buyer=member).count()
                total_spent = Order.objects.filter(
                    buyer=member, status='completed'
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                member_activity.append({
                    'id': member.id,
                    'username': member.username,
                    'full_name': member.get_full_name(),
                    'email': member.email,
                    'date_joined': member.date_joined.isoformat(),
                    'is_active': member.is_active,
                    'orders_count': orders_count,
                    'total_spent': float(total_spent),
                    'roles': [role.name for role in member.roles.all()]
                })
            except Exception:
                member_activity.append({
                    'id': member.id,
                    'username': member.username,
                    'full_name': member.get_full_name(),
                    'email': member.email,
                    'date_joined': member.date_joined.isoformat(),
                    'is_active': member.is_active,                    'orders_count': 0,
                    'total_spent': 0.0,
                    'roles': []
                })

        return Response({
            'data': {
                'institution': {
                    'id': institution_profile.id,
                    'name': institution_profile.name,
                    'type': getattr(institution_profile, 'institution_type', 'Unknown'),
                },
                'summary': member_stats,
                'role_breakdown': role_breakdown,
                'members': member_activity,
                'pagination': {
                    'total_count': members.count(),
                    'showing': len(member_activity)
                }
            },
            'generated_at': timezone.now().isoformat(),
            'success': True  # Add success flag for frontend
        })

    except Exception as e:
        logger.error(f"Institution members error for user {request.user.username}: {str(e)}")
        return InstitutionDashboardErrorHandler.handle_server_error(request, e)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([InstitutionDashboardUserThrottle])
def institution_budget_analytics(request):
    """
    Get institution budget analytics and spending patterns
    """
    try:
        # Enhanced logging for Institution Dashboard debugging
        logger.info(f"Institution budget analytics request from user {request.user.username}")
        
        # Get user's institution
        institution_profile = getattr(request.user, 'institutionprofile', None)
        if not institution_profile:
            logger.warning(f"User {request.user.username} has no institution profile")
            return InstitutionDashboardErrorHandler.handle_permission_error(request)

        # Get time period from query params
        period = request.query_params.get('period', '30')  # days
        try:
            days = int(period)
        except ValueError:
            days = 30

        start_date = timezone.now() - timedelta(days=days)

        # Get institution members for filtering
        institution_members = User.objects.filter(
            Q(institutionprofile=institution_profile) |
            Q(institution_members=institution_profile)
        )

        # Budget analytics from orders
        orders = Order.objects.filter(
            buyer__in=institution_members,
            created_at__gte=start_date
        )

        # Spending summary
        spending_summary = orders.aggregate(
            total_spent=Sum('total_amount'),
            completed_spent=Sum('total_amount', filter=Q(status='completed')),
            pending_amount=Sum('total_amount', filter=Q(status='pending')),
            average_order_value=Avg('total_amount')
        )

        # Monthly spending trends
        monthly_spending = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_orders = Order.objects.filter(
                buyer__in=institution_members,
                created_at__gte=month_start,
                created_at__lt=month_end,
                status='completed'
            )
            
            month_total = month_orders.aggregate(
                total=Sum('total_amount')
            )['total'] or 0

            monthly_spending.append({
                'month': month_start.strftime('%Y-%m'),
                'total_spent': float(month_total),
                'order_count': month_orders.count()
            })

        # Category breakdown
        category_spending = []
        try:
            from products.models import Category
            categories = Category.objects.all()
            
            for category in categories:
                category_orders = OrderItem.objects.filter(
                    order__buyer__in=institution_members,
                    order__created_at__gte=start_date,
                    order__status='completed',
                    product__category=category
                )
                
                category_total = category_orders.aggregate(
                    total=Sum(F('quantity') * F('unit_price'))
                )['total'] or 0

                if category_total > 0:
                    category_spending.append({
                        'category': category.name,
                        'total_spent': float(category_total),
                        'order_count': category_orders.values('order').distinct().count()
                    })
        except Exception:
            category_spending = []

        # Supplier analysis
        supplier_spending = []
        supplier_orders = orders.filter(status='completed').values('seller').annotate(
            total_spent=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_spent')[:10]

        for supplier_data in supplier_orders:
            try:
                supplier = User.objects.get(id=supplier_data['seller'])
                supplier_spending.append({
                    'supplier_id': supplier.id,
                    'supplier_name': supplier.get_full_name(),
                    'total_spent': float(supplier_data['total_spent']),
                    'order_count': supplier_data['order_count']
                })
            except User.DoesNotExist:
                continue

        # Budget utilization (if budget data exists)
        budget_utilization = {
            'allocated_budget': 0,  # This would come from institution budget model
            'spent_budget': float(spending_summary['completed_spent'] or 0),
            'remaining_budget': 0,
            'utilization_percentage': 0
        }

        return Response({
            'data': {
                'institution': {
                    'id': institution_profile.id,
                    'name': institution_profile.name,
                },
                'period': f'{days} days',
                'spending_summary': {
                    'total_spent': float(spending_summary['total_spent'] or 0),
                    'completed_spent': float(spending_summary['completed_spent'] or 0),
                    'pending_amount': float(spending_summary['pending_amount'] or 0),
                    'average_order_value': float(spending_summary['average_order_value'] or 0),
                    'total_orders': orders.count(),
                    'completed_orders': orders.filter(status='completed').count()
                },
                'monthly_trends': monthly_spending[:6],  # Last 6 months
                'category_breakdown': category_spending,
                'supplier_analysis': supplier_spending,                'budget_utilization': budget_utilization
            },
            'generated_at': timezone.now().isoformat(),
            'success': True  # Add success flag for frontend
        })

    except Exception as e:
        logger.error(f"Institution budget analytics error for user {request.user.username}: {str(e)}")
        return InstitutionDashboardErrorHandler.handle_server_error(request, e)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([InstitutionDashboardUserThrottle])
def institution_stats(request):
    """
    Get comprehensive institution statistics and KPIs
    """
    try:
        # Enhanced logging for Institution Dashboard debugging
        logger.info(f"Institution stats request from user {request.user.username}")
        
        # Get user's institution
        institution_profile = getattr(request.user, 'institutionprofile', None)
        if not institution_profile:
            logger.warning(f"User {request.user.username} has no institution profile")
            return InstitutionDashboardErrorHandler.handle_permission_error(request)

        # Get institution members
        institution_members = User.objects.filter(
            Q(institutionprofile=institution_profile) |
            Q(institution_members=institution_profile)
        )

        # Overall statistics
        total_members = institution_members.count()
        active_members = institution_members.filter(is_active=True).count()
        
        # Order statistics
        all_orders = Order.objects.filter(buyer__in=institution_members)
        recent_orders = all_orders.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )

        order_stats = {
            'total_orders': all_orders.count(),
            'completed_orders': all_orders.filter(status='completed').count(),
            'pending_orders': all_orders.filter(status='pending').count(),
            'recent_orders_30_days': recent_orders.count(),
            'total_order_value': float(all_orders.filter(
                status='completed'
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
        }

        # Performance metrics
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago = timezone.now() - timedelta(days=60)

        current_month_orders = recent_orders.count()
        previous_month_orders = Order.objects.filter(
            buyer__in=institution_members,
            created_at__gte=sixty_days_ago,
            created_at__lt=thirty_days_ago
        ).count()

        order_growth = 0
        if previous_month_orders > 0:
            order_growth = ((current_month_orders - previous_month_orders) / previous_month_orders) * 100

        # Top products/categories
        top_products = []
        try:
            popular_items = OrderItem.objects.filter(
                order__buyer__in=institution_members,
                order__status='completed'
            ).values('product__name').annotate(
                total_quantity=Sum('quantity'),
                total_value=Sum(F('quantity') * F('unit_price'))
            ).order_by('-total_quantity')[:5]

            for item in popular_items:
                top_products.append({
                    'product_name': item['product__name'],
                    'total_quantity': item['total_quantity'],
                    'total_value': float(item['total_value'] or 0)
                })
        except Exception:
            top_products = []

        # Supplier relationships
        unique_suppliers = all_orders.filter(
            status='completed'
        ).values('seller').distinct().count()

        # Activity trends (last 7 days)
        daily_activity = []
        for i in range(7):
            day = timezone.now().date() - timedelta(days=i)
            day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            
            day_orders = Order.objects.filter(
                buyer__in=institution_members,
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            daily_activity.append({
                'date': day.isoformat(),
                'orders': day_orders
            })

        # Key performance indicators
        kpis = {
            'member_engagement': {
                'total_members': total_members,
                'active_members': active_members,
                'engagement_rate': round((active_members / total_members * 100), 2) if total_members > 0 else 0
            },
            'procurement_efficiency': {
                'orders_per_month': round(current_month_orders, 2),
                'average_order_value': round(order_stats['total_order_value'] / order_stats['total_orders'], 2) if order_stats['total_orders'] > 0 else 0,
                'order_completion_rate': round((order_stats['completed_orders'] / order_stats['total_orders'] * 100), 2) if order_stats['total_orders'] > 0 else 0
            },
            'supplier_diversity': {
                'unique_suppliers': unique_suppliers,
                'supplier_relationship_score': min(100, unique_suppliers * 10)  # Simple scoring
            },
            'growth_metrics': {
                'order_growth_rate': round(order_growth, 2),
                'recent_activity_trend': 'increasing' if order_growth > 0 else 'decreasing' if order_growth < 0 else 'stable'
            }
        }

        return Response({
            'data': {
                'institution': {
                    'id': institution_profile.id,
                    'name': institution_profile.name,
                    'type': getattr(institution_profile, 'institution_type', 'Unknown'),
                    'member_count': total_members
                },
                'overview': order_stats,
                'performance_metrics': kpis,
                'top_products': top_products,
                'daily_activity': daily_activity[:7],  # Last 7 days
                'insights': {
                    'most_active_period': 'weekdays',  # This could be calculated
                    'preferred_suppliers': unique_suppliers,
                    'procurement_pattern': 'bulk_orders' if order_stats.get('total_order_value', 0) / max(order_stats.get('total_orders', 1), 1) > 1000 else 'regular_orders'
                }
            },
            'generated_at': timezone.now().isoformat()
        })

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
