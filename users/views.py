"""
AgriConnect Users Views
Comprehensive user profile management views
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
import logging

from .models import (
    ExtendedUserProfile,
    FarmerProfile,
    ConsumerProfile,
    InstitutionProfile,
    AgentProfile,
    FinancialPartnerProfile,
    GovernmentOfficialProfile
)
from .serializers import (
    ComprehensiveUserProfileSerializer,
    UserProfileUpdateSerializer,
    UserActivationSerializer,
    ExtendedUserProfileSerializer,
    FarmerProfileSerializer,
    ConsumerProfileSerializer,
    InstitutionProfileSerializer,
    AgentProfileSerializer,
    FinancialPartnerProfileSerializer,
    GovernmentOfficialProfileSerializer
)
from authentication.models import UserRole

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def users_api_root(request, format=None):
    """
    Users API Root
    User profile management endpoints
    """
    base_url = f"{request.scheme}://{request.get_host()}"
    
    return Response({
        'name': 'AgriConnect Users API',
        'version': '1.0',
        'description': 'User profile management system',
        'endpoints': {
            'profile': f'{base_url}/api/v1/users/profile/',
            'profile_update': f'{base_url}/api/v1/users/profile/update/',
            'profile_comprehensive': f'{base_url}/api/v1/users/profile/comprehensive/',
            'activate_account': f'{base_url}/api/v1/users/activate/',
            'extended_profile': f'{base_url}/api/v1/users/extended-profile/',
            'farmer_profile': f'{base_url}/api/v1/users/farmer-profile/',
            'consumer_profile': f'{base_url}/api/v1/users/consumer-profile/',
            'institution_profile': f'{base_url}/api/v1/users/institution-profile/',
        },
        'features': [
            'Comprehensive profile management',
            'Role-specific profile handling',
            'Account activation system',
            'Profile completion tracking',
            'Multi-user type support'
        ],
        'supported_user_types': [
            'FARMER', 'CONSUMER', 'INSTITUTION', 'AGENT',
            'FINANCIAL_PARTNER', 'GOVERNMENT_OFFICIAL', 'ADMIN'
        ]
    })


class UserProfileView(RetrieveUpdateAPIView):
    """
    Get and update basic user profile
    GET/PUT/PATCH /api/v1/users/profile/
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Update user profile with logging"""
        user = self.get_object()
        logger.info(f"Profile update requested by user: {user.username}")
        
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == 200:
            logger.info(f"Profile updated successfully for user: {user.username}")
        
        return response


class ComprehensiveUserProfileView(RetrieveUpdateAPIView):
    """
    Get and update comprehensive user profile including all role-specific profiles
    GET/PUT/PATCH /api/v1/users/profile/comprehensive/
    """
    serializer_class = ComprehensiveUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """Get comprehensive user profile"""
        user = self.get_object()
        
        # Ensure extended profile exists
        ExtendedUserProfile.objects.get_or_create(user=user)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update comprehensive user profile"""
        user = self.get_object()
        logger.info(f"Comprehensive profile update by: {user.username}")
        
        try:
            with transaction.atomic():
                response = super().update(request, *args, **kwargs)
                
                if response.status_code == 200:
                    logger.info(f"Comprehensive profile updated for: {user.username}")
                
                return response
        except Exception as e:
            logger.error(f"Profile update failed for {user.username}: {str(e)}")
            return Response({
                'error': 'Profile update failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserActivationView(UpdateAPIView):
    """
    Activate user account
    POST /api/v1/users/activate/
    """
    serializer_class = UserActivationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Activate user account"""
        user = self.get_object()
        
        if user.is_active and user.is_verified:
            return Response({
                'message': 'Account is already activated',
                'is_active': True,
                'is_verified': True
            })
        
        serializer = self.get_serializer(user, data={})
        if serializer.is_valid():
            updated_user = serializer.save()
            
            logger.info(f"Account activated for user: {updated_user.username}")
            
            return Response({
                'message': 'Account activated successfully',
                'is_active': updated_user.is_active,
                'is_verified': updated_user.is_verified,
                'email_verified': getattr(updated_user, 'email_verified', False),
                'phone_verified': getattr(updated_user, 'phone_verified', False)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtendedUserProfileView(RetrieveUpdateAPIView):
    """
    Manage extended user profile
    GET/PUT/PATCH /api/v1/users/extended-profile/
    """
    serializer_class = ExtendedUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        extended_profile, created = ExtendedUserProfile.objects.get_or_create(user=user)
        return extended_profile


class FarmerProfileView(RetrieveUpdateAPIView):
    """
    Manage farmer profile
    GET/PUT/PATCH /api/v1/users/farmer-profile/
    """
    serializer_class = FarmerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        # Check if user has FARMER role
        if not user.roles.filter(name='FARMER').exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must have FARMER role to access farmer profile")
        
        farmer_profile, created = FarmerProfile.objects.get_or_create(user=user)
        return farmer_profile


class ConsumerProfileView(RetrieveUpdateAPIView):
    """
    Manage consumer profile
    GET/PUT/PATCH /api/v1/users/consumer-profile/
    """
    serializer_class = ConsumerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        # Check if user has CONSUMER role
        if not user.roles.filter(name='CONSUMER').exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must have CONSUMER role to access consumer profile")
        
        consumer_profile, created = ConsumerProfile.objects.get_or_create(user=user)
        return consumer_profile


class InstitutionProfileView(RetrieveUpdateAPIView):
    """
    Manage institution profile
    GET/PUT/PATCH /api/v1/users/institution-profile/
    """
    serializer_class = InstitutionProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        # Check if user has INSTITUTION role
        if not user.roles.filter(name='INSTITUTION').exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must have INSTITUTION role to access institution profile")
        
        institution_profile, created = InstitutionProfile.objects.get_or_create(
            user=user,
            defaults={'organization_name': f"{user.get_full_name()}'s Organization"}
        )
        return institution_profile


class AgentProfileView(RetrieveUpdateAPIView):
    """
    Manage agent profile
    GET/PUT/PATCH /api/v1/users/agent-profile/
    """
    serializer_class = AgentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        # Check if user has AGENT role
        if not user.roles.filter(name='AGENT').exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must have AGENT role to access agent profile")
        
        agent_profile, created = AgentProfile.objects.get_or_create(user=user)
        return agent_profile


class FinancialPartnerProfileView(RetrieveUpdateAPIView):
    """
    Manage financial partner profile
    GET/PUT/PATCH /api/v1/users/financial-partner-profile/
    """
    serializer_class = FinancialPartnerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        # Check if user has FINANCIAL_PARTNER role
        if not user.roles.filter(name='FINANCIAL_PARTNER').exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must have FINANCIAL_PARTNER role to access financial partner profile")
        
        financial_profile, created = FinancialPartnerProfile.objects.get_or_create(
            user=user,
            defaults={'institution_name': f"{user.get_full_name()}'s Institution"}
        )
        return financial_profile


class GovernmentOfficialProfileView(RetrieveUpdateAPIView):
    """
    Manage government official profile
    GET/PUT/PATCH /api/v1/users/government-official-profile/
    """
    serializer_class = GovernmentOfficialProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        # Check if user has GOVERNMENT_OFFICIAL role
        if not user.roles.filter(name='GOVERNMENT_OFFICIAL').exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must have GOVERNMENT_OFFICIAL role to access government official profile")
        
        government_profile, created = GovernmentOfficialProfile.objects.get_or_create(
            user=user,
            defaults={'official_title': 'Officer', 'department': 'Agricultural Department'}
        )
        return government_profile


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_activate_accounts(request):
    """
    Bulk activate accounts (admin only)
    POST /api/v1/users/bulk-activate/
    """
    user = request.user
    
    # Check if user has admin privileges
    if not (user.is_staff or user.roles.filter(name='ADMIN').exists()):
        return Response({
            'error': 'Admin privileges required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    user_ids = request.data.get('user_ids', [])
    
    if not user_ids:
        return Response({
            'error': 'user_ids list is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            users = User.objects.filter(id__in=user_ids)
            
            activated_count = 0
            for user_obj in users:
                if not user_obj.is_active or not user_obj.is_verified:
                    user_obj.is_active = True
                    user_obj.is_verified = True
                    
                    # Verify contact information
                    if user_obj.email:
                        user_obj.email_verified = True
                    if user_obj.phone_number:
                        user_obj.phone_verified = True
                    
                    user_obj.save()
                    activated_count += 1
                    
                    # Ensure extended profile exists
                    ExtendedUserProfile.objects.get_or_create(user=user_obj)
                    
                    logger.info(f"Account activated by admin {user.username} for user: {user_obj.username}")
            
            return Response({
                'message': f'Successfully activated {activated_count} accounts',
                'activated_count': activated_count,
                'total_requested': len(user_ids)
            })
    
    except Exception as e:
        logger.error(f"Bulk activation failed: {str(e)}")
        return Response({
            'error': 'Bulk activation failed',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile_status(request):
    """
    Get user profile status and completion
    GET /api/v1/users/profile/status/
    """
    user = request.user
    
    # Calculate profile completion
    completion_data = ComprehensiveUserProfileSerializer().get_profile_completion(user)
    
    # Get user roles
    roles = [role.name for role in user.roles.all()]
    
    # Check which profiles exist
    profiles_status = {
        'extended_profile': hasattr(user, 'extended_profile'),
        'farmer_profile': hasattr(user, 'farmer_profile') and 'FARMER' in roles,
        'consumer_profile': hasattr(user, 'consumer_profile') and 'CONSUMER' in roles,
        'institution_profile': hasattr(user, 'institution_profile') and 'INSTITUTION' in roles,
        'agent_profile': hasattr(user, 'agent_profile') and 'AGENT' in roles,
        'financial_partner_profile': hasattr(user, 'financial_partner_profile') and 'FINANCIAL_PARTNER' in roles,
        'government_official_profile': hasattr(user, 'government_official_profile') and 'GOVERNMENT_OFFICIAL' in roles,
    }
    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'email_verified': getattr(user, 'email_verified', False),
        'phone_verified': getattr(user, 'phone_verified', False),
        'profile_completion': completion_data,
        'roles': roles,
        'profiles_status': profiles_status,
        'required_actions': [
            'Complete basic profile information' if completion_data < 50 else None,
            'Verify email address' if user.email and not getattr(user, 'email_verified', False) else None,
            'Verify phone number' if user.phone_number and not getattr(user, 'phone_verified', False) else None,
            'Activate account' if not user.is_active or not user.is_verified else None
        ]
    })
