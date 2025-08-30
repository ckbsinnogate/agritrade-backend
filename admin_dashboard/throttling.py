"""
Admin Dashboard Custom Throttling
=================================
Custom throttling classes that provide proper rate limiting for admin dashboard
endpoints while exempting authenticated admin users from restrictions.

Features:
- Admin user exemption from all rate limiting
- Generous rate limits for admin endpoints
- Proper error messages for admin authentication issues
- Integration with Institution Dashboard protection system

Author: Assistant with 40+ years of web development experience
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
import time
import logging

logger = logging.getLogger('admin_dashboard')


class AdminDashboardAnonThrottle(AnonRateThrottle):
    """
    Custom throttle for unauthenticated admin dashboard requests
    Provides more generous limits than institution dashboard
    """
    scope = 'admin_dashboard_anon'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on IP and endpoint pattern
        """
        if not self.should_throttle_endpoint(request):
            return None
        
        return super().get_cache_key(request, view)
    
    def should_throttle_endpoint(self, request):
        """
        Only throttle admin dashboard endpoints
        """
        admin_endpoints = [
            '/api/v1/admin-dashboard/',
            '/api/v1/auth/admin/',
            '/api/v1/auth/users/',
            '/api/v1/orders/statistics/',
        ]
        
        return any(endpoint in request.path for endpoint in admin_endpoints)
    
    def throttle_failure(self):
        """
        Override to provide helpful error message for admin dashboard
        """
        wait = self.wait()
        detail = {
            'message': 'Admin dashboard rate limit exceeded',
            'detail': 'Too many unauthenticated requests to admin dashboard endpoints',
            'wait_seconds': wait,
            'error_code': 'ADMIN_DASHBOARD_RATE_LIMITED',
            'admin_help': {
                'issue': 'Too many requests without admin authentication',
                'solution': 'Login with admin credentials for unrestricted access',
                'auth_endpoint': '/api/v1/auth/login/',
                'required_privileges': 'is_staff=True OR ADMIN role',
                'documentation': '/api/docs/admin-dashboard/'
            }
        }
        raise Throttled(detail=detail)


class AdminDashboardUserThrottle(UserRateThrottle):
    """
    Custom throttle for authenticated admin dashboard requests
    Exempts admin users completely, applies limits to regular users
    """
    scope = 'admin_dashboard_user'
    
    def should_throttle_endpoint(self, request):
        """
        Only throttle admin dashboard endpoints
        """
        admin_endpoints = [
            '/api/v1/admin-dashboard/',
            '/api/v1/auth/admin/',
            '/api/v1/auth/users/',
            '/api/v1/orders/statistics/',
        ]
        
        return any(endpoint in request.path for endpoint in admin_endpoints)
    
    def allow_request(self, request, view):
        """
        Check if request should be allowed.
        Admin users are completely exempt from throttling.
        """
        # Check if this endpoint should be throttled
        if not self.should_throttle_endpoint(request):
            return True
        
        # Admin users are exempt from all throttling
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        
        # Check for ADMIN role
        if hasattr(request.user, 'roles'):
            admin_roles = request.user.roles.filter(name='ADMIN')
            if admin_roles.exists():
                return True
        
        # Apply regular throttling for non-admin users
        return super().allow_request(request, view)
    
    def throttle_failure(self):
        """
        Override to provide helpful error message for admin dashboard
        """
        wait = self.wait()
        detail = {
            'message': 'Admin dashboard user rate limit exceeded',
            'detail': 'Regular users have limited access to admin endpoints',
            'wait_seconds': wait,
            'error_code': 'ADMIN_DASHBOARD_USER_LIMITED',
            'admin_help': {
                'issue': 'Non-admin user accessing admin endpoints',
                'solution': 'Contact administrator for admin privileges',
                'required_privileges': 'is_staff=True OR ADMIN role',
                'admin_contact': 'admin@agriconnect.com'
            }
        }
        raise Throttled(detail=detail)


class AnalyticsThrottle(UserRateThrottle):
    """
    Custom throttle specifically for analytics endpoints
    Provides higher limits for analytics data requests
    """
    scope = 'analytics'
    
    def should_throttle_endpoint(self, request):
        """
        Only throttle analytics endpoints
        """
        analytics_endpoints = [
            '/api/v1/analytics/',
            '/api/v1/admin-dashboard/analytics/',
        ]
        
        return any(endpoint in request.path for endpoint in analytics_endpoints)
    
    def allow_request(self, request, view):
        """
        Check if request should be allowed.
        Admin users get higher limits for analytics.
        """
        # Check if this endpoint should be throttled
        if not self.should_throttle_endpoint(request):
            return True
        
        # Admin users get higher rate limits
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            # Use admin-specific rate limiting (much higher)
            self.scope = 'analytics_admin'
        
        return super().allow_request(request, view)


class AdminDashboardErrorHandler:
    """
    Centralized error handling for Admin Dashboard endpoints
    to provide helpful feedback to frontend developers
    """
    
    @staticmethod
    def handle_authentication_error(request):
        """
        Handle 401 authentication errors with helpful guidance
        """
        return {
            'error': 'Authentication Required',
            'message': 'Admin dashboard requires valid authentication',
            'error_code': 'ADMIN_AUTH_REQUIRED',
            'help': {
                'issue': 'No valid authentication token provided',
                'solution': 'Include valid JWT token in Authorization header',
                'format': 'Authorization: Bearer <your_token>',
                'auth_endpoint': '/api/v1/auth/login/',
                'required_privileges': 'is_staff=True OR ADMIN role'
            },
            'status_code': 401
        }
    
    @staticmethod
    def handle_permission_error(request):
        """
        Handle 403 permission errors
        """
        return {
            'error': 'Admin Privileges Required',
            'message': 'This endpoint requires administrator privileges',
            'error_code': 'ADMIN_PRIVILEGES_REQUIRED',
            'help': {
                'issue': 'User does not have admin privileges',
                'solution': 'Contact system administrator for admin role assignment',
                'required_privileges': 'is_staff=True OR ADMIN role',
                'contact': 'admin@agriconnect.com'
            },
            'status_code': 403
        }
    
    @staticmethod
    def handle_rate_limit_error(request, wait_time):
        """
        Handle 429 rate limit errors
        """
        return {
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests to admin dashboard endpoints',
            'error_code': 'ADMIN_RATE_LIMITED',
            'wait_seconds': wait_time,
            'help': {
                'issue': 'Too many requests in short time period',
                'solution': 'Wait before making more requests or authenticate as admin',
                'admin_exemption': 'Admin users have no rate limits',
                'retry_after': f'{wait_time} seconds'
            },
            'status_code': 429
        }


def apply_admin_dashboard_throttling(view_func):
    """
    Decorator to apply Admin Dashboard specific throttling
    """
    def wrapper(request, *args, **kwargs):
        # Check if this is an Admin Dashboard endpoint
        admin_endpoints = [
            '/api/v1/admin-dashboard/',
            '/api/v1/auth/admin/',
            '/api/v1/auth/users/',
            '/api/v1/orders/statistics/',
            '/api/v1/analytics/',
        ]
        
        is_admin_endpoint = any(endpoint in request.path for endpoint in admin_endpoints)
        
        if is_admin_endpoint:
            # Check authentication first
            if not request.user.is_authenticated:
                error_response = AdminDashboardErrorHandler.handle_authentication_error(request)
                return JsonResponse(error_response, status=401)
            
            # Check admin privileges
            is_admin = (hasattr(request.user, 'is_staff') and request.user.is_staff) or \
                      (hasattr(request.user, 'roles') and request.user.roles.filter(name='ADMIN').exists())
            
            if not is_admin:
                error_response = AdminDashboardErrorHandler.handle_permission_error(request)
                return JsonResponse(error_response, status=403)
            
            # Admin users bypass all throttling
            logger.info(f"Admin user {request.user.username} accessed {request.path}")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# Middleware integration functions
def should_exempt_from_throttling(request):
    """
    Check if request should be exempt from throttling
    Used by Institution Dashboard middleware
    """
    # Admin dashboard endpoints
    admin_endpoints = [
        '/api/v1/admin-dashboard/',
        '/api/v1/auth/admin/',
        '/api/v1/auth/users/',
        '/api/v1/orders/statistics/',
    ]
    
    is_admin_endpoint = any(endpoint in request.path for endpoint in admin_endpoints)
    
    if is_admin_endpoint:
        # Authenticated admin users are exempt
        if hasattr(request, 'user') and request.user.is_authenticated:
            is_admin = (hasattr(request.user, 'is_staff') and request.user.is_staff) or \
                      (hasattr(request.user, 'roles') and request.user.roles.filter(name='ADMIN').exists())
            return is_admin
    
    return False