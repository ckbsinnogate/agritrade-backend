"""
AgriConnect Processing Views
Complete API endpoints for processing management system
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from .models import (
    ProcessingEquipment, ProcessingSchedule, 
    ProcessingQualityCheck, ProcessingStats
)
from .serializers import (
    ProcessingEquipmentSerializer, ProcessingEquipmentCreateSerializer,
    ProcessingScheduleSerializer, ProcessingQualityCheckSerializer,
    ProcessingStatsSerializer, ProcessingDashboardStatsSerializer
)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def processing_api_root(request, format=None):
    """Processing API Root - Processing Management System"""
    return Response({
        'name': 'AgriConnect Processing API',
        'description': 'Complete processing management system for processors',
        'endpoints': {
            'equipment': request.build_absolute_uri('equipment/'),
            'schedule': request.build_absolute_uri('schedule/'),
            'quality_checks': request.build_absolute_uri('quality-checks/'),
            'stats': request.build_absolute_uri('stats/'),
            'orders': request.build_absolute_uri('orders/'),
        },
        'features': [
            'Equipment management and tracking',
            'Production scheduling and planning',
            'Quality control and inspections',
            'Performance analytics and reporting',
            'Order processing management'
        ],
        'status': 'operational'
    })

class ProcessingEquipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for processing equipment management"""
    serializer_class = ProcessingEquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter equipment by processor"""
        if hasattr(self.request.user, 'user_role') and self.request.user.user_role.role == 'PROCESSOR':
            return ProcessingEquipment.objects.filter(processor=self.request.user)
        return ProcessingEquipment.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProcessingEquipmentCreateSerializer
        return ProcessingEquipmentSerializer
    
    def perform_create(self, serializer):
        serializer.save(processor=self.request.user)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available equipment"""
        equipment = self.get_queryset().filter(status='available')
        serializer = self.get_serializer(equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_maintenance(self, request, pk=None):
        """Start maintenance on equipment"""
        equipment = self.get_object()
        equipment.status = 'maintenance'
        equipment.last_maintenance = timezone.now()
        equipment.save()
        return Response({'status': 'Maintenance started'})

class ProcessingScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for processing schedule management"""
    serializer_class = ProcessingScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter schedules by processor"""
        if hasattr(self.request.user, 'user_role') and self.request.user.user_role.role == 'PROCESSOR':
            return ProcessingSchedule.objects.filter(processor=self.request.user)
        return ProcessingSchedule.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(processor=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's schedule"""
        today = timezone.now().date()
        schedules = self.get_queryset().filter(
            scheduled_start__date=today
        )
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active schedules"""
        schedules = self.get_queryset().filter(
            status__in=['scheduled', 'in_progress']
        )
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_processing(self, request, pk=None):
        """Start processing for a schedule"""
        schedule = self.get_object()
        schedule.status = 'in_progress'
        schedule.actual_start = timezone.now()
        schedule.save()
        return Response({'status': 'Processing started'})

class ProcessingQualityCheckViewSet(viewsets.ModelViewSet):
    """ViewSet for quality checks management"""
    serializer_class = ProcessingQualityCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter quality checks by processor"""
        if hasattr(self.request.user, 'user_role') and self.request.user.user_role.role == 'PROCESSOR':
            return ProcessingQualityCheck.objects.filter(processor=self.request.user)
        return ProcessingQualityCheck.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(processor=self.request.user, inspector=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending quality checks"""
        checks = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(checks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's quality checks"""
        today = timezone.now().date()
        checks = self.get_queryset().filter(check_date__date=today)
        serializer = self.get_serializer(checks, many=True)
        return Response(serializer.data)

class ProcessingStatsViewSet(viewsets.ModelViewSet):
    """ViewSet for processing statistics"""
    serializer_class = ProcessingStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter stats by processor"""
        if hasattr(self.request.user, 'user_role') and self.request.user.user_role.role == 'PROCESSOR':
            return ProcessingStats.objects.filter(processor=self.request.user)
        return ProcessingStats.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(processor=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        user = request.user
        today = timezone.now().date()
        
        # Calculate dashboard stats
        total_equipment = ProcessingEquipment.objects.filter(processor=user).count()
        active_schedules = ProcessingSchedule.objects.filter(
            processor=user, 
            status__in=['scheduled', 'in_progress']
        ).count()
        pending_quality_checks = ProcessingQualityCheck.objects.filter(
            processor=user, 
            status='pending'
        ).count()
        
        # Get today's production stats
        today_stats = ProcessingStats.objects.filter(
            processor=user, 
            date=today
        ).first()
        
        if today_stats:
            today_production = today_stats.total_volume_processed
            equipment_utilization = today_stats.equipment_utilization
            quality_pass_rate = today_stats.quality_pass_rate
        else:
            today_production = 0
            equipment_utilization = 0
            quality_pass_rate = 0
        
        # Recent orders (last 7 days)
        week_ago = today - timedelta(days=7)
        recent_orders = ProcessingSchedule.objects.filter(
            processor=user,
            created_at__date__gte=week_ago
        ).count()
        
        # Monthly revenue
        month_start = today.replace(day=1)
        monthly_revenue = ProcessingStats.objects.filter(
            processor=user,
            date__gte=month_start
        ).aggregate(total=Sum('revenue_generated'))['total'] or 0
        
        stats = {
            'total_equipment': total_equipment,
            'active_schedules': active_schedules,
            'pending_quality_checks': pending_quality_checks,
            'today_production': today_production,
            'equipment_utilization': equipment_utilization,
            'quality_pass_rate': quality_pass_rate,
            'recent_orders': recent_orders,
            'monthly_revenue': monthly_revenue,
        }
        
        serializer = ProcessingDashboardStatsSerializer(stats)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def processing_orders(request):
    """Get processing orders - compatible with frontend expectations"""
    try:
        # Import here to avoid circular imports
        from orders.models import Order
        
        user = request.user
        
        # Get orders related to processing
        orders = Order.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('buyer', 'seller').prefetch_related('items')
        
        # Filter based on query parameters
        status_filter = request.GET.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Convert to frontend-compatible format
        orders_data = []
        for order in orders[:20]:  # Limit to 20 for performance
            orders_data.append({
                'id': str(order.id),
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': float(order.total_amount),
                'order_date': order.order_date.isoformat() if order.order_date else None,
                'buyer': order.buyer.username if order.buyer else None,
                'seller': order.seller.username if order.seller else None,
                'items_count': order.items.count(),
                'processing_status': getattr(order, 'processing_status', 'pending'),
                'created_at': order.created_at.isoformat(),
            })
        
        return Response({
            'count': len(orders_data),
            'results': orders_data,
            'status': 'success'
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch processing orders',
            'message': str(e),
            'results': [],
            'count': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
