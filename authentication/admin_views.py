"""
Admin-specific views for user management
Provides admin endpoints for user management that frontend admin dashboards expect
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta

from .models import UserRole, OTPCode
from .serializers import UserRegistrationSerializer
from users.serializers import ComprehensiveUserProfileSerializer

User = get_user_model()


class AdminUserManagementViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for user management
    Provides CRUD operations for user accounts by administrators
    """
    queryset = User.objects.all().select_related().prefetch_related('roles')
    serializer_class = ComprehensiveUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields
    search_fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']
    
    # Ordering fields  
    ordering_fields = ['date_joined', 'last_login', 'username', 'email']
    ordering = ['-date_joined']
    
    # Filter fields
    filterset_fields = {
        'is_active': ['exact'],
        'is_verified': ['exact'],
        'email_verified': ['exact'],
        'phone_verified': ['exact'],
        'country': ['exact', 'icontains'],
        'language': ['exact'],
        'date_joined': ['gte', 'lte'],
        'last_login': ['gte', 'lte'],
    }

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions required for this view.
        """
        permission_classes = [permissions.IsAuthenticated]
        
        # For sensitive operations, require admin or staff permissions
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes.append(permissions.IsAdminUser)
        elif self.action in ['list', 'retrieve']:
            # Allow staff to view users
            permission_classes.append(permissions.IsAdminUser)
            
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on user permissions and query parameters
        """
        queryset = super().get_queryset()
        
        # Filter by role if specified
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(roles__name=role)
        
        # Filter by verification status
        verification_status = self.request.query_params.get('verification_status')
        if verification_status == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif verification_status == 'unverified':
            queryset = queryset.filter(is_verified=False)
        elif verification_status == 'email_verified':
            queryset = queryset.filter(email_verified=True)
        elif verification_status == 'phone_verified':
            queryset = queryset.filter(phone_verified=True)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date_joined__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_joined__lte=date_to)
            
        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        """
        Create a new user account (admin only)
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Set as verified if admin is creating the account
            user.is_verified = True
            user.email_verified = bool(user.email)
            user.phone_verified = bool(user.phone_number)
            user.save()
            
            # Add roles if specified
            roles_data = request.data.get('roles', [])
            if roles_data:
                for role_name in roles_data:
                    try:
                        role = UserRole.objects.get(name=role_name)
                        user.roles.add(role)
                    except UserRole.DoesNotExist:
                        pass
            
            # Return comprehensive user data
            response_serializer = ComprehensiveUserProfileSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify_user(self, request, pk=None):
        """
        Manually verify a user (admin only)
        """
        user = self.get_object()
        user.is_verified = True
        user.email_verified = bool(user.email)
        user.phone_verified = bool(user.phone_number)
        user.save()
        
        return Response({
            'message': f'User {user.username} has been verified',
            'verified': True
        })

    @action(detail=True, methods=['post'])
    def deactivate_user(self, request, pk=None):
        """
        Deactivate a user account (admin only)
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response({
            'message': f'User {user.username} has been deactivated',
            'active': False
        })

    @action(detail=True, methods=['post'])
    def activate_user(self, request, pk=None):
        """
        Activate a user account (admin only)
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'message': f'User {user.username} has been activated',
            'active': True
        })

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Reset user password (admin only)
        """
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({
                'error': 'new_password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': f'Password reset for user {user.username}',
            'success': True
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get user statistics for admin dashboard
        """
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_registrations = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        
        # Users by role
        role_stats = {}
        for role in UserRole.objects.all():
            role_stats[role.name] = User.objects.filter(roles=role).count()
        
        # Users by country
        country_stats = User.objects.values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'recent_registrations': recent_registrations,
            'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0,
            'role_distribution': role_stats,
            'top_countries': list(country_stats),
            'generated_at': datetime.now().isoformat()
        })

    @action(detail=False, methods=['post'])
    def bulk_verify(self, request):
        """
        Bulk verify multiple users (admin only)
        """
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({
                'error': 'user_ids list is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(id__in=user_ids)
        updated_count = users.update(
            is_verified=True,
            email_verified=True,
            phone_verified=True
        )
        
        return Response({
            'message': f'{updated_count} users verified successfully',
            'verified_count': updated_count
        })

    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        """
        Bulk deactivate multiple users (admin only)
        """
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({
                'error': 'user_ids list is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(id__in=user_ids)
        updated_count = users.update(is_active=False)
        
        return Response({
            'message': f'{updated_count} users deactivated successfully',
            'deactivated_count': updated_count
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def admin_dashboard_stats(request):
    """
    Get comprehensive admin dashboard statistics
    """
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    verified_users = User.objects.filter(is_verified=True).count()
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_logins = User.objects.filter(last_login__gte=seven_days_ago).count()
    recent_registrations = User.objects.filter(date_joined__gte=seven_days_ago).count()
    
    # Growth metrics (last 30 days vs previous 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    sixty_days_ago = datetime.now() - timedelta(days=60)
    
    current_period_registrations = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()
    
    previous_period_registrations = User.objects.filter(
        date_joined__gte=sixty_days_ago,
        date_joined__lt=thirty_days_ago
    ).count()
    
    growth_rate = 0
    if previous_period_registrations > 0:
        growth_rate = round(
            ((current_period_registrations - previous_period_registrations) / 
             previous_period_registrations * 100), 2
        )
    
    return Response({
        'users': {
            'total': total_users,
            'active': active_users,
            'verified': verified_users,
            'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0,
            'recent_logins_7d': recent_logins,
            'recent_registrations_7d': recent_registrations,
            'registrations_30d': current_period_registrations,
            'growth_rate_30d': growth_rate
        },
        'roles': {
            role.name: User.objects.filter(roles=role).count()
            for role in UserRole.objects.all()
        },
        'generated_at': datetime.now().isoformat()
    })
