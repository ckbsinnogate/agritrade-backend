# Institution Dashboard Rate Limiting Configuration
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status
import time
from django.core.cache import cache
from django.conf import settings


class InstitutionDashboardAnonThrottle(AnonRateThrottle):
    """
    Custom throttle for unauthenticated Institution Dashboard requests
    to prevent infinite loop issues from frontend
    """
    scope = 'institution_dashboard_anon'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on IP and endpoint pattern
        """
        if not self.should_throttle_endpoint(request):
            return None
        
        return super().get_cache_key(request, view)
    
    def should_throttle_endpoint(self, request):
        """
        Only throttle Institution Dashboard endpoints
        """
        institution_endpoints = [
            '/api/v1/analytics/institution/',
            '/api/v1/purchases/purchases/list/',
            '/api/v1/contracts/',
        ]
        
        return any(endpoint in request.path for endpoint in institution_endpoints)
    
    def throttle_failure(self):
        """
        Override to provide helpful error message for Institution Dashboard
        """
        wait = self.wait()
        detail = {
            'message': 'Institution Dashboard rate limit exceeded',
            'detail': 'Too many unauthenticated requests to Institution Dashboard endpoints',
            'wait_seconds': wait,
            'error_code': 'INSTITUTION_DASHBOARD_RATE_LIMITED',
            'help': {
                'issue': 'Frontend making too many requests without authentication',
                'solution': 'Implement proper JWT authentication in frontend',
                'auth_required': True,
                'documentation': 'See INSTITUTION_DASHBOARD_FRONTEND_INTEGRATION_FINAL_GUIDE.md'
            }
        }
        raise Throttled(detail=detail)


class InstitutionDashboardUserThrottle(UserRateThrottle):
    """
    Custom throttle for authenticated Institution Dashboard requests
    """
    scope = 'institution_dashboard_user'
    
    def should_throttle_endpoint(self, request):
        """
        Only throttle Institution Dashboard endpoints
        """
        institution_endpoints = [
            '/api/v1/analytics/institution/',
            '/api/v1/purchases/purchases/list/',
            '/api/v1/contracts/',
        ]
        
        return any(endpoint in request.path for endpoint in institution_endpoints)


class InstitutionDashboardErrorHandler:
    """
    Centralized error handling for Institution Dashboard endpoints
    to provide helpful feedback to frontend developers
    """
    
    @staticmethod
    def handle_authentication_error(request):
        """
        Handle 401 authentication errors with helpful guidance
        """
        return Response({
            'error': 'Authentication required',
            'message': 'Institution Dashboard endpoints require JWT authentication',
            'error_code': 'AUTHENTICATION_REQUIRED',
            'institution_dashboard_integration': {
                'problem': 'Frontend is not sending authentication token',
                'solution': 'Include JWT token in Authorization header',
                'example': 'Authorization: Bearer <your-jwt-token>',
                'endpoints': {
                    'login': '/api/v1/auth/login/',
                    'token_refresh': '/api/v1/auth/token/refresh/',
                    'token_verify': '/api/v1/auth/token/verify/'
                },
                'documentation': {
                    'frontend_guide': 'INSTITUTION_DASHBOARD_FRONTEND_INTEGRATION_FINAL_GUIDE.md',
                    'api_reference': 'INSTITUTION_DASHBOARD_API_REFERENCE_COMPLETE.md',
                    'quick_start': 'INSTITUTION_DASHBOARD_IMPLEMENTATION_CHECKLIST.md'
                },
                'common_fixes': [
                    'Check if JWT token is stored and retrieved correctly',
                    'Verify token is included in Authorization header',
                    'Ensure token is not expired',
                    'Check if user is logged in before making requests'
                ]
            }
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def handle_permission_error(request):
        """
        Handle 403 permission errors
        """
        return Response({
            'error': 'Permission denied',
            'message': 'User does not have permission to access institution data',
            'error_code': 'PERMISSION_DENIED',
            'institution_dashboard_integration': {
                'problem': 'User is not associated with an institution',
                'solution': 'Ensure user has proper institution membership',
                'common_causes': [
                    'User is not linked to any institution',
                    'User lacks required role/permissions',
                    'Institution data is restricted'
                ]
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def handle_server_error(request, error):
        """
        Handle 500 server errors with debugging info
        """
        return Response({
            'error': 'Internal server error',
            'message': 'An error occurred while processing Institution Dashboard request',
            'error_code': 'INTERNAL_SERVER_ERROR',
            'debug_info': str(error) if settings.DEBUG else 'Contact support',
            'institution_dashboard_support': {
                'status': 'Backend endpoints are operational',
                'issue': 'Temporary server error',
                'retry': 'Please try again in a few moments',
                'support_email': 'support@agriconnect.com'
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def apply_institution_dashboard_throttling(view_func):
    """
    Decorator to apply Institution Dashboard specific throttling
    """
    def wrapper(request, *args, **kwargs):
        # Check if this is an Institution Dashboard endpoint
        institution_endpoints = [
            '/api/v1/analytics/institution/',
            '/api/v1/purchases/purchases/list/',
            '/api/v1/contracts/',
        ]
        
        is_institution_endpoint = any(endpoint in request.path for endpoint in institution_endpoints)
        
        if is_institution_endpoint:
            # Apply throttling check
            if not request.user.is_authenticated:
                throttle = InstitutionDashboardAnonThrottle()
                if not throttle.allow_request(request, None):
                    throttle.throttle_failure()
            else:
                throttle = InstitutionDashboardUserThrottle()
                if not throttle.allow_request(request, None):
                    raise Throttled(detail="Institution Dashboard user rate limit exceeded")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
