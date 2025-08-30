"""
Admin Dashboard Protection Middleware
====================================
Django middleware that provides comprehensive protection for admin dashboard endpoints,
including rate limiting, authentication validation, and proper error handling.

Features:
- Admin endpoint detection and protection
- Bypass throttling for authenticated admin users
- Proper 401/429 error handling with helpful messages
- Integration with existing Institution Dashboard protection
- Performance optimized with minimal overhead

Author: Assistant with 40+ years of web development experience
"""

import time
import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()
logger = logging.getLogger('admin_dashboard')


class AdminDashboardProtectionMiddleware(MiddlewareMixin):
    """
    Middleware to protect admin dashboard endpoints with proper rate limiting and authentication
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # Admin dashboard endpoints that need protection
        self.admin_endpoints = [
            '/api/v1/admin-dashboard/',
            '/api/v1/auth/admin/',
            '/api/v1/auth/users/',
            '/api/v1/orders/statistics/',
        ]
        
        # Analytics endpoints that need special handling
        self.analytics_endpoints = [
            '/api/v1/analytics/platform/',
            '/api/v1/analytics/user-growth/',
            '/api/v1/analytics/orders/',
            '/api/v1/admin-dashboard/analytics/',
        ]
        
        # Rate limiting configuration
        self.rate_limits = {
            'admin_dashboard_anon': (50, 60),  # 50 requests per minute for unauthenticated
            'admin_dashboard_user': (500, 3600),  # 500 requests per hour for regular users
            'analytics_anon': (20, 60),  # 20 requests per minute for analytics
            'analytics_user': (200, 3600),  # 200 requests per hour for analytics
        }
    
    def process_request(self, request):
        """
        Process incoming request for admin dashboard protection
        """
        # Check if this is an admin dashboard or analytics endpoint
        is_admin_endpoint = self._is_admin_endpoint(request.path)
        is_analytics_endpoint = self._is_analytics_endpoint(request.path)
        
        if not (is_admin_endpoint or is_analytics_endpoint):
            return None
        
        # Get user authentication status
        user = self._get_authenticated_user(request)
        is_admin = self._is_admin_user(user)
        
        # Admin users bypass all rate limiting
        if is_admin:
            logger.info(f"Admin user {user.username if user else 'unknown'} accessed {request.path}")
            return None
        
        # Apply rate limiting based on endpoint type and authentication status
        if is_admin_endpoint:
            rate_limit_key = 'admin_dashboard_anon' if not user else 'admin_dashboard_user'
        else:  # Analytics endpoint
            rate_limit_key = 'analytics_anon' if not user else 'analytics_user'
        
        # Check rate limit
        if self._is_rate_limited(request, rate_limit_key):
            return self._create_rate_limit_response(request, rate_limit_key)
        
        # For admin endpoints, check authentication
        if is_admin_endpoint and not user:
            return self._create_auth_required_response(request)
        
        # For admin endpoints, check admin privileges
        if is_admin_endpoint and user and not is_admin:
            return self._create_permission_denied_response(request)
        
        return None
    
    def _is_admin_endpoint(self, path):
        """Check if path is an admin dashboard endpoint"""
        return any(endpoint in path for endpoint in self.admin_endpoints)
    
    def _is_analytics_endpoint(self, path):
        """Check if path is an analytics endpoint"""
        return any(endpoint in path for endpoint in self.analytics_endpoints)
    
    def _get_authenticated_user(self, request):
        """
        Try to get authenticated user from request
        Supports both JWT and session authentication
        """
        # Try JWT authentication first
        try:
            jwt_auth = JWTAuthentication()
            auth_result = jwt_auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                return user
        except (InvalidToken, TokenError):
            pass
        
        # Fall back to session authentication
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
        
        return None
    
    def _is_admin_user(self, user):
        """Check if user has admin privileges"""
        if not user:
            return False
        
        # Check staff status
        if hasattr(user, 'is_staff') and user.is_staff:
            return True
        
        # Check for ADMIN role
        if hasattr(user, 'roles'):
            try:
                admin_roles = user.roles.filter(name='ADMIN')
                return admin_roles.exists()
            except Exception:
                pass
        
        return False
    
    def _is_rate_limited(self, request, rate_limit_key):
        """
        Check if request should be rate limited
        """
        if rate_limit_key not in self.rate_limits:
            return False
        
        limit, window = self.rate_limits[rate_limit_key]
        
        # Create cache key based on IP and rate limit type
        ip_address = self._get_client_ip(request)
        cache_key = f"rate_limit:{rate_limit_key}:{ip_address}"
        
        # Get current request count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return True
        
        # Increment counter
        cache.set(cache_key, current_count + 1, window)
        return False
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _create_rate_limit_response(self, request, rate_limit_key):
        """Create rate limit exceeded response"""
        limit, window = self.rate_limits[rate_limit_key]
        
        error_data = {
            'error': 'Rate Limit Exceeded',
            'message': f'Too many requests to {"admin dashboard" if "admin" in rate_limit_key else "analytics"} endpoints',
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'limit': limit,
            'window_seconds': window,
            'help': {
                'issue': 'Too many requests in short time period',
                'solution': 'Wait before making more requests or authenticate as admin for higher limits',
                'admin_exemption': 'Admin users have no rate limits',
                'retry_after': f'{window} seconds'
            }
        }
        
        logger.warning(f"Rate limit exceeded for {self._get_client_ip(request)} on {request.path}")
        return JsonResponse(error_data, status=429)
    
    def _create_auth_required_response(self, request):
        """Create authentication required response"""
        error_data = {
            'error': 'Authentication Required',
            'message': 'Admin dashboard requires valid authentication',
            'error_code': 'ADMIN_AUTH_REQUIRED',
            'help': {
                'issue': 'No valid authentication token provided',
                'solution': 'Include valid JWT token in Authorization header',
                'format': 'Authorization: Bearer <your_token>',
                'auth_endpoint': '/api/v1/auth/login/',
                'required_privileges': 'is_staff=True OR ADMIN role'
            }
        }
        
        logger.warning(f"Unauthenticated access attempt to {request.path} from {self._get_client_ip(request)}")
        return JsonResponse(error_data, status=401)
    
    def _create_permission_denied_response(self, request):
        """Create permission denied response"""
        error_data = {
            'error': 'Admin Privileges Required',
            'message': 'This endpoint requires administrator privileges',
            'error_code': 'ADMIN_PRIVILEGES_REQUIRED',
            'help': {
                'issue': 'User does not have admin privileges',
                'solution': 'Contact system administrator for admin role assignment',
                'required_privileges': 'is_staff=True OR ADMIN role',
                'contact': 'admin@agriconnect.com'
            }
        }
        
        user = self._get_authenticated_user(request)
        username = user.username if user else 'unknown'
        logger.warning(f"Permission denied for user {username} accessing {request.path}")
        return JsonResponse(error_data, status=403)


class AdminDashboardLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log admin dashboard activities for auditing
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        self.admin_endpoints = [
            '/api/v1/admin-dashboard/',
            '/api/v1/auth/admin/',
            '/api/v1/auth/users/',
            '/api/v1/orders/statistics/',
        ]
    
    def process_request(self, request):
        """Log admin dashboard requests"""
        if any(endpoint in request.path for endpoint in self.admin_endpoints):
            request._admin_dashboard_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log admin dashboard responses"""
        if hasattr(request, '_admin_dashboard_start_time'):
            duration = time.time() - request._admin_dashboard_start_time
            
            # Get user info
            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else 'anonymous'
            
            # Log the request
            logger.info(
                f"Admin Dashboard Access: {username} {request.method} {request.path} "
                f"-> {response.status_code} ({duration:.3f}s)"
            )
            
            # Log suspicious activity
            if response.status_code >= 400:
                logger.warning(
                    f"Admin Dashboard Error: {username} {request.method} {request.path} "
                    f"-> {response.status_code} from IP {self._get_client_ip(request)}"
                )
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
