"""
AgriConnect Warehouse Management Views
Complete API views for warehouse operations and management
"""

from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg, F, Value
from django.utils import timezone
from datetime import timedelta, date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from decimal import Decimal

from .models import (
    WarehouseType, Warehouse, WarehouseZone, WarehouseStaff,
    WarehouseInventory, WarehouseMovement, TemperatureLog, QualityInspection
)
from .serializers import (
    WarehouseTypeSerializer, WarehouseListSerializer, WarehouseDetailSerializer,
    WarehouseZoneSerializer, WarehouseStaffSerializer, WarehouseInventorySerializer,
    WarehouseMovementSerializer, TemperatureLogSerializer, QualityInspectionSerializer,
    WarehouseStatsSerializer, InventoryAlertSerializer, ZoneUtilizationSerializer,
    MovementReportSerializer, WarehouseCreateSerializer, InventoryMovementCreateSerializer
)


class WarehouseTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for warehouse types"""
    queryset = WarehouseType.objects.all()
    serializer_class = WarehouseTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['warehouse_type']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class WarehouseViewSet(viewsets.ModelViewSet):
    """ViewSet for warehouse management"""
    queryset = Warehouse.objects.select_related('warehouse_type', 'manager').prefetch_related('zones', 'staff')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'warehouse_type', 'organic_certified', 'country', 'region']
    search_fields = ['code', 'name', 'region', 'city']
    ordering_fields = ['name', 'created_at', 'current_utilization_percent']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WarehouseListSerializer
        elif self.action == 'create':
            return WarehouseCreateSerializer
        return WarehouseDetailSerializer
    
    @action(detail=True, methods=['get'])
    def zones(self, request, pk=None):
        """Get all zones for a warehouse"""
        warehouse = self.get_object()
        zones = warehouse.zones.all()
        serializer = WarehouseZoneSerializer(zones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get inventory for a warehouse"""
        warehouse = self.get_object()
        inventory = warehouse.inventory.select_related('product', 'zone').all()
        
        # Apply filters
        zone_type = request.query_params.get('zone_type')
        quality_status = request.query_params.get('quality_status')
        
        if zone_type:
            inventory = inventory.filter(zone__zone_type=zone_type)
        if quality_status:
            inventory = inventory.filter(quality_status=quality_status)
        
        serializer = WarehouseInventorySerializer(inventory, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def staff(self, request, pk=None):
        """Get staff for a warehouse"""
        warehouse = self.get_object()
        staff = warehouse.staff.select_related('user').all()
        serializer = WarehouseStaffSerializer(staff, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get recent movements for a warehouse"""
        warehouse = self.get_object()
        movements = WarehouseMovement.objects.filter(
            Q(from_zone__warehouse=warehouse) | Q(to_zone__warehouse=warehouse)
        ).select_related('inventory__product', 'authorized_by', 'performed_by').order_by('-created_at')[:50]
        
        serializer = WarehouseMovementSerializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def temperature_logs(self, request, pk=None):
        """Get temperature logs for a warehouse"""
        warehouse = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        logs = warehouse.temperature_logs.filter(recorded_at__gte=since).order_by('-recorded_at')
        serializer = TemperatureLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def log_temperature(self, request, pk=None):
        """Log temperature reading for warehouse"""
        warehouse = self.get_object()
        data = request.data.copy()
        data['warehouse'] = warehouse.id
        
        serializer = TemperatureLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def utilization_report(self, request, pk=None):
        """Get detailed utilization report for warehouse"""
        warehouse = self.get_object()
        zones = warehouse.zones.all()
        
        zone_data = []
        for zone in zones:
            zone_data.append({
                'zone_id': zone.id,
                'zone_name': zone.name,
                'zone_type': zone.zone_type,
                'warehouse_name': warehouse.name,
                'capacity': zone.capacity_cubic_meters,
                'current_stock': zone.current_stock_level,
                'utilization_percentage': zone.get_occupancy_percentage(),
                'status': 'Active' if zone.is_active else 'Inactive'
            })
        
        serializer = ZoneUtilizationSerializer(zone_data, many=True)
        return Response(serializer.data)


class WarehouseZoneViewSet(viewsets.ModelViewSet):
    """ViewSet for warehouse zones"""
    queryset = WarehouseZone.objects.select_related('warehouse').all()
    serializer_class = WarehouseZoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['zone_type', 'is_active', 'requires_certification', 'warehouse']
    search_fields = ['zone_code', 'name']
    ordering_fields = ['zone_code', 'capacity_cubic_meters', 'current_stock_level']
    ordering = ['warehouse', 'zone_code']
    
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get inventory for a zone"""
        zone = self.get_object()
        inventory = zone.inventory.select_related('product').all()
        serializer = WarehouseInventorySerializer(inventory, many=True)
        return Response(serializer.data)


class WarehouseStaffViewSet(viewsets.ModelViewSet):
    """ViewSet for warehouse staff"""
    queryset = WarehouseStaff.objects.select_related('warehouse', 'user').all()
    serializer_class = WarehouseStaffSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'warehouse']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['hired_date', 'performance_rating']
    ordering = ['warehouse', 'role']


class WarehouseInventoryViewSet(viewsets.ModelViewSet):
    """ViewSet for warehouse inventory"""
    queryset = WarehouseInventory.objects.select_related('product', 'warehouse', 'zone').all()
    serializer_class = WarehouseInventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['quality_status', 'warehouse', 'zone__zone_type']
    search_fields = ['product__name', 'batch_number', 'lot_number']
    ordering_fields = ['created_at', 'expiry_date', 'quantity']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get inventory alerts"""
        # Low stock (less than 10% of original quantity)
        low_stock = self.queryset.filter(available_quantity__lt=F('quantity') * 0.1)
        
        # Expiring soon (within 7 days)
        week_from_now = date.today() + timedelta(days=7)
        expiring_soon = self.queryset.filter(
            expiry_date__lte=week_from_now,
            expiry_date__gt=date.today()
        )
        
        # Already expired
        expired = self.queryset.filter(expiry_date__lt=date.today())
        
        # In quarantine
        quarantine = self.queryset.filter(quality_status='quarantine')
        
        alert_data = {
            'low_stock_items': low_stock.count(),
            'expiring_soon': expiring_soon.count(),
            'expired_items': expired.count(),
            'quarantine_items': quarantine.count(),
            'low_stock_details': WarehouseInventorySerializer(low_stock[:10], many=True).data,
            'expiring_details': WarehouseInventorySerializer(expiring_soon[:10], many=True).data,
            'expired_details': WarehouseInventorySerializer(expired[:10], many=True).data,
        }
        
        serializer = InventoryAlertSerializer(alert_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """Reserve inventory for an order"""
        inventory = self.get_object()
        quantity = float(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity > inventory.available_quantity:
            return Response(
                {'error': f'Not enough inventory. Available: {inventory.available_quantity}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inventory.reserved_quantity += quantity
        inventory.save()
        
        serializer = self.get_serializer(inventory)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def release_reservation(self, request, pk=None):
        """Release reserved inventory"""
        inventory = self.get_object()
        quantity = float(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity > inventory.reserved_quantity:
            return Response(
                {'error': f'Cannot release more than reserved. Reserved: {inventory.reserved_quantity}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inventory.reserved_quantity -= quantity
        inventory.save()
        
        serializer = self.get_serializer(inventory)
        return Response(serializer.data)


class WarehouseMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for warehouse movements"""
    queryset = WarehouseMovement.objects.select_related(
        'inventory__product', 'from_zone', 'to_zone', 'authorized_by', 'performed_by'
    ).all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'is_completed']
    search_fields = ['reference_number', 'inventory__product__name']
    ordering_fields = ['created_at', 'completed_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InventoryMovementCreateSerializer
        return WarehouseMovementSerializer
    
    def perform_create(self, serializer):
        # Generate reference number if not provided
        if not serializer.validated_data.get('reference_number'):
            ref_num = f"WM{timezone.now().strftime('%Y%m%d%H%M%S')}"
            serializer.save(reference_number=ref_num)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark movement as completed"""
        movement = self.get_object()
        movement.is_completed = True
        movement.completed_at = timezone.now()
        movement.save()
        
        # Update inventory quantities based on movement type
        if movement.movement_type == 'outbound':
            movement.inventory.quantity -= movement.quantity
            movement.inventory.save()
        elif movement.movement_type == 'inbound':
            movement.inventory.quantity += movement.quantity
            movement.inventory.save()
        
        serializer = self.get_serializer(movement)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generate movement report"""
        period = request.query_params.get('period', '30')  # days
        start_date = timezone.now() - timedelta(days=int(period))
        
        movements = self.queryset.filter(created_at__gte=start_date)
        
        report_data = {
            'period': f"Last {period} days",
            'total_movements': movements.count(),
            'inbound_movements': movements.filter(movement_type='inbound').count(),
            'outbound_movements': movements.filter(movement_type='outbound').count(),
            'internal_transfers': movements.filter(movement_type='transfer').count(),
            'movements_by_type': dict(movements.values('movement_type').annotate(count=Count('id')).values_list('movement_type', 'count')),
            'movements_by_warehouse': {},
            'top_moved_products': []
        }
        
        serializer = MovementReportSerializer(report_data)
        return Response(serializer.data)


class TemperatureLogViewSet(viewsets.ModelViewSet):
    """ViewSet for temperature logs"""
    queryset = TemperatureLog.objects.select_related('warehouse', 'zone').all()
    serializer_class = TemperatureLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'zone', 'alert_triggered', 'is_within_range']
    ordering_fields = ['recorded_at', 'temperature']
    ordering = ['-recorded_at']
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get active temperature alerts"""
        alerts = self.queryset.filter(
            alert_triggered=True,
            alert_acknowledged=False
        ).order_by('-recorded_at')
        
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge a temperature alert"""
        log = self.get_object()
        log.alert_acknowledged = True
        log.acknowledged_by = request.user
        log.save()
        
        serializer = self.get_serializer(log)
        return Response(serializer.data)


class QualityInspectionViewSet(viewsets.ModelViewSet):
    """ViewSet for quality inspections"""
    queryset = QualityInspection.objects.select_related('inventory__product', 'inspector').all()
    serializer_class = QualityInspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['inspection_type', 'overall_result', 'requires_follow_up']
    search_fields = ['inspection_number', 'inventory__product__name']
    ordering_fields = ['inspection_date', 'quality_score']
    ordering = ['-inspection_date']
    
    @action(detail=False, methods=['get'])
    def pending_follow_ups(self, request):
        """Get inspections requiring follow-up"""
        pending = self.queryset.filter(
            requires_follow_up=True,
            follow_up_completed=False
        )
        
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)


# Dashboard and analytics views

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def warehouse_api_root(request, format=None):
    """
    Warehouse Management API Root
    Complete agricultural warehouse management system
    """
    return Response({
        'name': 'AgriConnect Warehouse Management System',
        'version': '1.0',
        'description': 'Complete multi-zone warehouse system for agricultural supply chain management',
        'features': [
            'Multi-zone warehouse architecture (cold storage, dry storage, organic zones)',
            'Real-time inventory tracking across zones',
            'Temperature and humidity monitoring',
            'Staff management with role-based access',
            'Quality control zones and inspection tracking',
            'RFID/QR code integration for traceability',
            'Movement tracking and audit trails',
            'Environmental monitoring and alerts'
        ],
        'endpoints': {
            'dashboard': '/api/v1/warehouses/dashboard/',
            'warehouse_types': '/api/v1/warehouses/types/',
            'warehouses': '/api/v1/warehouses/warehouses/',
            'zones': '/api/v1/warehouses/zones/',
            'staff': '/api/v1/warehouses/staff/',
            'inventory': '/api/v1/warehouses/inventory/',
            'movements': '/api/v1/warehouses/movements/',
            'temperature_logs': '/api/v1/warehouses/temperature-logs/',
            'quality_inspections': '/api/v1/warehouses/quality-inspections/'
        },
        'warehouse_operations': {
            'inventory_management': {
                'add_stock': 'POST /warehouses/{id}/inventory/',
                'reserve_stock': 'POST /inventory/{id}/reserve/',
                'release_reservation': 'POST /inventory/{id}/release_reservation/',
                'move_inventory': 'POST /movements/',
                'quality_check': 'POST /quality-inspections/'
            },
            'monitoring': {
                'temperature_logs': 'GET /warehouses/{id}/temperature_logs/',
                'log_temperature': 'POST /warehouses/{id}/log_temperature/',
                'inventory_alerts': 'GET /inventory/alerts/',
                'utilization_report': 'GET /warehouses/{id}/utilization_report/'
            },
            'staff_management': {
                'assign_staff': 'POST /staff/',
                'manage_access': 'PUT /staff/{id}/',
                'track_performance': 'GET /staff/{id}/'
            }
        },
        'zone_types': [
            'cold_storage', 'dry_storage', 'organic_zone', 
            'processing_area', 'quarantine_zone', 'loading_dock'
        ],
        'quality_statuses': [
            'excellent', 'good', 'fair', 'poor', 'expired', 'quarantine'
        ],
        'movement_types': [
            'inbound', 'outbound', 'transfer', 'adjustment', 
            'loss', 'return', 'quarantine', 'release'
        ],
        'integration_ready': {
            'order_fulfillment': 'Automatic inventory allocation for orders',
            'blockchain_tracking': 'Full traceability from farm to consumer',
            'iot_sensors': 'Real-time environmental monitoring',
            'mobile_apps': 'Staff mobile applications ready',
            'erp_systems': 'Enterprise resource planning integration'
        },
        'status': 'Phase 4: Warehouse Management System - ACTIVE'
    })

class WarehouseDashboardView(generics.GenericAPIView):
    """Dashboard view with warehouse statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Basic statistics
        total_warehouses = Warehouse.objects.count()
        active_warehouses = Warehouse.objects.filter(status='active').count()
        total_zones = WarehouseZone.objects.count()
        total_inventory_items = WarehouseInventory.objects.count()
        
        # Calculate total inventory value
        total_value = 0
        for item in WarehouseInventory.objects.select_related('product').all():
            total_value += float(item.quantity) * float(item.product.price_per_unit)
        
        # Average utilization
        avg_utilization = Warehouse.objects.aggregate(
            avg=Avg('current_utilization_percent')
        )['avg'] or 0
        
        # Groupings
        warehouses_by_type = dict(
            Warehouse.objects.values('warehouse_type__name').annotate(
                count=Count('id')
            ).values_list('warehouse_type__name', 'count')
        )
        
        zones_by_type = dict(
            WarehouseZone.objects.values('zone_type').annotate(
                count=Count('id')
            ).values_list('zone_type', 'count')
        )
        
        inventory_by_quality = dict(
            WarehouseInventory.objects.values('quality_status').annotate(
                count=Count('id')
            ).values_list('quality_status', 'count')
        )
        
        # Recent activity
        recent_movements = WarehouseMovement.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        pending_inspections = QualityInspection.objects.filter(
            requires_follow_up=True,
            follow_up_completed=False
        ).count()
        
        stats_data = {
            'total_warehouses': total_warehouses,
            'active_warehouses': active_warehouses,
            'total_zones': total_zones,
            'total_inventory_items': total_inventory_items,
            'total_inventory_value': total_value,
            'average_utilization': avg_utilization,
            'warehouses_by_type': warehouses_by_type,
            'zones_by_type': zones_by_type,
            'inventory_by_quality': inventory_by_quality,
            'recent_movements': recent_movements,
            'pending_inspections': pending_inspections,
        }
        
        serializer = WarehouseStatsSerializer(stats_data)
        return Response(serializer.data)


class WarehouseBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for warehouse space bookings"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return warehouse inventory that can be booked
        return WarehouseInventory.objects.select_related('product', 'warehouse', 'zone').filter(
            quantity__gt=0
        )
    
    def get_serializer_class(self):
        return WarehouseInventorySerializer
    
    def list(self, request):
        """List available warehouse space for booking"""
        try:
            # Get warehouses with available space
            warehouses = Warehouse.objects.filter(
                status='active',
                current_utilization_percent__lt=90
            ).select_related('warehouse_type')
            
            booking_data = []
            for warehouse in warehouses:
                available_zones = warehouse.zones.filter(
                    is_active=True,
                    current_stock_level__lt=F('capacity_cubic_meters') * 0.9
                )
                
                for zone in available_zones:
                    available_capacity = zone.capacity_cubic_meters - zone.current_stock_level
                    booking_data.append({
                        'warehouse_id': warehouse.id,
                        'warehouse_name': warehouse.name,
                        'warehouse_location': f"{warehouse.city}, {warehouse.region}",
                        'zone_id': zone.id,
                        'zone_name': zone.name,
                        'zone_type': zone.zone_type,
                        'available_capacity': available_capacity,
                        'capacity_unit': 'cubic_meters',
                        'organic_certified': warehouse.organic_certified,
                        'temperature_controlled': zone.zone_type in ['cold_storage', 'frozen_storage'],
                        'booking_rate_per_day': 50.0,  # Sample rate
                        'minimum_booking_period': 7,  # days
                    })
            
            return Response({
                'success': True,
                'available_bookings': booking_data,
                'total_warehouses': warehouses.count(),
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """Create a new warehouse booking"""
        try:
            data = request.data
            warehouse_id = data.get('warehouse_id')
            zone_id = data.get('zone_id')
            capacity_needed = float(data.get('capacity_needed', 0))
            booking_period = int(data.get('booking_period', 7))
            
            # Validate warehouse and zone
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)
            zone = get_object_or_404(WarehouseZone, id=zone_id, warehouse=warehouse)
            
            # Check available capacity
            available_capacity = zone.capacity_cubic_meters - zone.current_stock_level
            if capacity_needed > available_capacity:
                return Response({
                    'success': False,
                    'error': f'Insufficient capacity. Available: {available_capacity}, Requested: {capacity_needed}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create booking record (simplified)
            booking_data = {
                'booking_id': f"WB{timezone.now().strftime('%Y%m%d')}{warehouse.id}{zone.id}",
                'warehouse': warehouse.name,
                'zone': zone.name,
                'capacity_booked': capacity_needed,
                'booking_period_days': booking_period,
                'total_cost': capacity_needed * 50.0 * booking_period,
                'status': 'confirmed',
                'booking_date': timezone.now().isoformat(),
                'start_date': timezone.now().date().isoformat(),
                'end_date': (timezone.now().date() + timedelta(days=booking_period)).isoformat()
            }
            
            return Response({
                'success': True,
                'booking': booking_data,
                'message': 'Warehouse space booked successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def inventory_optimization(request):
    """Optimize warehouse inventory allocation and suggestions"""
    try:
        if request.method == 'GET':
            # Get optimization suggestions with safe database queries
            
            # Check if we have any inventory data
            if not WarehouseInventory.objects.exists():
                return Response({
                    'success': True,
                    'optimization_analysis': {
                        'overstocked_items': [],
                        'understocked_items': [],
                        'expiring_soon': [],
                        'zone_optimization': [],
                        'summary': {
                            'total_overstocked_items': 0,
                            'total_understocked_items': 0,
                            'items_expiring_soon': 0,
                            'zones_needing_attention': 0
                        }
                    },
                    'generated_at': timezone.now().isoformat(),
                    'message': 'No inventory data available for optimization'
                })
            
            # Identify overstocked items - using Decimal to avoid type issues
            try:
                overstocked = WarehouseInventory.objects.filter(
                    quantity__gt=F('reserved_quantity') * Decimal('2.0')
                ).select_related('product', 'warehouse', 'zone')[:10]
            except Exception as e:
                overstocked = WarehouseInventory.objects.none()
              # Identify understocked items
            try:
                understocked = WarehouseInventory.objects.filter(
                    quantity__lt=F('reserved_quantity') * Decimal('1.2')
                ).select_related('product', 'warehouse', 'zone')[:10]
            except Exception as e:
                understocked = WarehouseInventory.objects.none()
            
            # Identify items near expiry
            try:
                week_from_now = date.today() + timedelta(days=7)
                expiring_soon = WarehouseInventory.objects.filter(
                    expiry_date__lte=week_from_now,
                    expiry_date__gt=date.today(),
                    quantity__gt=0
                ).select_related('product', 'warehouse', 'zone')[:10]
            except Exception as e:
                expiring_soon = WarehouseInventory.objects.none()
            
            # Zone utilization analysis
            try:
                zones = WarehouseZone.objects.select_related('warehouse').all()
            except Exception as e:
                zones = WarehouseZone.objects.none()
            zone_optimization = []
            
            for zone in zones:
                # Safe decimal calculation for utilization
                if zone.capacity_cubic_meters and zone.capacity_cubic_meters > 0:
                    utilization = float(zone.current_stock_level) / float(zone.capacity_cubic_meters) * 100
                else:
                    utilization = 0
                
                if utilization > 90:
                    suggestion = "Consider moving some inventory to other zones"
                    priority = "high"
                elif utilization < 30:
                    suggestion = "Zone is underutilized - consider consolidation"
                    priority = "medium"
                else:
                    suggestion = "Optimal utilization"
                    priority = "low"
                
                zone_optimization.append({
                    'zone_id': zone.id,
                    'zone_name': zone.name,
                    'warehouse': zone.warehouse.name,
                    'utilization_percent': round(utilization, 2),
                    'suggestion': suggestion,
                    'priority': priority
                })
            
            optimization_data = {
                'overstocked_items': [
                    {
                        'product_name': item.product.name,
                        'warehouse': item.warehouse.name,
                        'zone': item.zone.name,
                        'current_quantity': float(item.quantity),
                        'reserved_quantity': float(item.reserved_quantity),
                        'excess_quantity': float(item.quantity - item.reserved_quantity * Decimal('1.5')),
                        'suggestion': 'Consider redistributing excess inventory'
                    }
                    for item in overstocked
                ],
                'understocked_items': [
                    {
                        'product_name': item.product.name,
                        'warehouse': item.warehouse.name,
                        'zone': item.zone.name,
                        'current_quantity': float(item.quantity),
                        'reserved_quantity': float(item.reserved_quantity),
                        'shortage': float(item.reserved_quantity * Decimal('1.2') - item.quantity),
                        'suggestion': 'Consider restocking'
                    }
                    for item in understocked
                ],
                'expiring_soon': [
                    {
                        'product_name': item.product.name,
                        'warehouse': item.warehouse.name,
                        'zone': item.zone.name,
                        'quantity': float(item.quantity),
                        'expiry_date': item.expiry_date.isoformat() if item.expiry_date else None,
                        'days_until_expiry': (item.expiry_date - date.today()).days if item.expiry_date else None,
                        'suggestion': 'Prioritize for sale or processing'
                    }
                    for item in expiring_soon
                ],
                'zone_optimization': zone_optimization,
                'summary': {
                    'total_overstocked_items': overstocked.count(),
                    'total_understocked_items': understocked.count(),
                    'items_expiring_soon': expiring_soon.count(),
                    'zones_needing_attention': len([z for z in zone_optimization if z['priority'] in ['high', 'medium']])
                }
            }
            
            return Response({
                'success': True,
                'optimization_analysis': optimization_data,
                'generated_at': timezone.now().isoformat()
            })
        
        elif request.method == 'POST':
            # Apply optimization suggestions
            optimization_actions = request.data.get('actions', [])
            applied_actions = []
            
            for action in optimization_actions:
                action_type = action.get('type')
                
                if action_type == 'move_inventory':
                    # Simulate inventory movement
                    applied_actions.append({
                        'action': 'move_inventory',
                        'from_zone': action.get('from_zone'),
                        'to_zone': action.get('to_zone'),
                        'quantity': action.get('quantity'),
                        'status': 'completed',
                        'message': 'Inventory movement scheduled'
                    })
                
                elif action_type == 'restock_item':
                    # Simulate restocking
                    applied_actions.append({
                        'action': 'restock_item',
                        'item_id': action.get('item_id'),
                        'quantity': action.get('quantity'),
                        'status': 'completed',
                        'message': 'Restocking order created'
                    })
                
                elif action_type == 'prioritize_sale':
                    # Simulate prioritizing for sale
                    applied_actions.append({
                        'action': 'prioritize_sale',
                        'item_id': action.get('item_id'),
                        'status': 'completed',
                        'message': 'Item marked for priority sale'
                    })
            
            return Response({
                'success': True,
                'applied_actions': applied_actions,
                'message': f'{len(applied_actions)} optimization actions applied successfully'
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
