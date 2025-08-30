# Institution Dashboard Protection Middleware
# Prevents infinite API call loops and protects backend resources

import time
import json
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class InstitutionDashboardProtectionMiddleware:
    """
    Middleware to prevent Institution Dashboard frontend from overwhelming backend
    with infinite API call loops due to authentication failures.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Institution Dashboard endpoints that need protection
        self.protected_endpoints = [
            '/api/v1/analytics/institution/members/',
            '/api/v1/analytics/institution/budget-analytics/',
            '/api/v1/analytics/institution/stats/',
            '/api/v1/purchases/purchases/list/',
            '/api/v1/contracts/',
        ]
          # Rate limiting configuration
        self.rate_limits = {
            'unauthenticated_requests_per_minute': 10,  # Max 10 401s per minute per IP
            'total_requests_per_minute': 60,  # Max 60 requests per minute per IP
            'circuit_breaker_threshold': 20,  # Trip after 20 consecutive 401s
            'circuit_breaker_timeout': 300,  # 5 minutes timeout
        }
    
    def __call__(self, request):
        # Exempt admin dashboard endpoints for authenticated admin users
        if self._is_admin_endpoint(request) and self._is_admin_user(request):
            response = self.get_response(request)
            return response
        
        # Check if this is a protected Institution Dashboard endpoint
        if any(endpoint in request.path for endpoint in self.protected_endpoints):
            # Apply rate limiting and circuit breaker logic
            if not self._check_rate_limits(request):
                return self._create_rate_limit_response()
            
            # Check circuit breaker
            if self._is_circuit_breaker_open(request):
                return self._create_circuit_breaker_response()

        response = self.get_response(request)
        
        # Track 401 responses for circuit breaker
        if any(endpoint in request.path for endpoint in self.protected_endpoints):
            self._track_response(request, response)
        
        return response

    def _get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '127.0.0.1')

    def _check_rate_limits(self, request):
        """Check if request exceeds rate limits"""
        client_ip = self._get_client_ip(request)
        current_time = int(time.time())
        minute_key = f"rate_limit:{client_ip}:{current_time // 60}"
        
        # Check current requests in this minute
        current_requests = cache.get(minute_key, 0)
        
        if current_requests >= self.rate_limits['total_requests_per_minute']:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {current_requests} requests")
            return False
        
        # Increment counter
        cache.set(minute_key, current_requests + 1, 70)  # Expire after 70 seconds
        return True

    def _is_circuit_breaker_open(self, request):
        """Check if circuit breaker is open for this IP"""
        client_ip = self._get_client_ip(request)
        circuit_key = f"circuit_breaker:{client_ip}"
        
        circuit_data = cache.get(circuit_key)
        if not circuit_data:
            return False
        
        # Check if circuit breaker timeout has passed
        if time.time() > circuit_data['timeout']:
            cache.delete(circuit_key)
            return False
        
        return True

    def _track_response(self, request, response):
        """Track responses for circuit breaker logic"""
        if response.status_code != 401:
            return
        
        client_ip = self._get_client_ip(request)
        consecutive_key = f"consecutive_401:{client_ip}"
        
        # Get current consecutive 401 count
        consecutive_401s = cache.get(consecutive_key, 0)
        consecutive_401s += 1
        
        # Store updated count
        cache.set(consecutive_key, consecutive_401s, 600)  # 10 minutes expiry
        
        # Check if we should trip circuit breaker
        if consecutive_401s >= self.rate_limits['circuit_breaker_threshold']:
            circuit_key = f"circuit_breaker:{client_ip}"
            circuit_data = {
                'timeout': time.time() + self.rate_limits['circuit_breaker_timeout'],
                'triggered_at': time.time(),
                'consecutive_401s': consecutive_401s
            }
            cache.set(circuit_key, circuit_data, self.rate_limits['circuit_breaker_timeout'] + 60)
            
            # Reset consecutive counter
            cache.delete(consecutive_key)
            
            logger.error(f"Circuit breaker triggered for IP {client_ip} after {consecutive_401s} consecutive 401s")

    def _create_rate_limit_response(self):
        """Create rate limit exceeded response"""
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please slow down and ensure proper authentication.',
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'retry_after': 60,
            'institution_dashboard_help': {
                'issue': 'Frontend is making too many API calls',
                'solution': 'Implement proper authentication and error handling',
                'documentation': '/api/docs/institution-dashboard/'
            }
        }, status=429)

    def _create_circuit_breaker_response(self):
        """Create circuit breaker response"""
        return JsonResponse({
            'error': 'Circuit breaker open',
            'message': 'Too many authentication failures. Access temporarily blocked.',
            'error_code': 'CIRCUIT_BREAKER_OPEN',
            'retry_after': 300,
            'institution_dashboard_help': {
                'issue': 'Repeated authentication failures detected',
                'solution': 'Fix authentication implementation in frontend',
                'documentation': '/api/docs/institution-dashboard/',
                'auth_endpoints': {
                    'login': '/api/v1/auth/login/',
                    'token_refresh': '/api/v1/auth/token/refresh/',
                    'token_verify': '/api/v1/auth/token/verify/'
                }
            }
        }, status=503)

    def _is_admin_endpoint(self, request):
        """Check if this is an admin dashboard endpoint"""
        admin_endpoints = [
            '/api/v1/admin-dashboard/',
            '/api/v1/auth/admin/',
            '/api/v1/auth/users/',
            '/api/v1/orders/statistics/',
        ]
        return any(endpoint in request.path for endpoint in admin_endpoints)
    
    def _is_admin_user(self, request):
        """Check if the current user is an admin"""
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        
        # Check staff status
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        
        # Check for ADMIN role
        if hasattr(request.user, 'roles'):
            try:
                admin_roles = request.user.roles.filter(name='ADMIN')
                return admin_roles.exists()
            except Exception:
                pass
        
        return False


class InstitutionDashboardLoggingMiddleware:
    """
    Enhanced logging middleware for Institution Dashboard endpoints
    to help diagnose frontend integration issues.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.institution_endpoints = [
            '/api/v1/analytics/institution/',
            '/api/v1/purchases/purchases/list/',
            '/api/v1/contracts/',
        ]
    
    def __call__(self, request):
        # Log Institution Dashboard requests
        if any(endpoint in request.path for endpoint in self.institution_endpoints):
            self._log_request(request)
        
        response = self.get_response(request)
        
        # Log responses for Institution Dashboard
        if any(endpoint in request.path for endpoint in self.institution_endpoints):
            self._log_response(request, response)
        
        return response
    
    def _log_request(self, request):
        """Log Institution Dashboard requests"""
        client_ip = self._get_client_ip(request)
        auth_header = request.META.get('HTTP_AUTHORIZATION', 'None')
        has_token = 'Bearer' in auth_header
        
        logger.info(f"Institution Dashboard Request: {request.method} {request.path} "
                   f"from {client_ip} - Auth: {'Token Present' if has_token else 'No Token'}")
    
    def _log_response(self, request, response):
        """Log Institution Dashboard responses"""
        client_ip = self._get_client_ip(request)
        
        if response.status_code == 401:
            logger.warning(f"Institution Dashboard 401: {request.path} from {client_ip} "
                          f"- Frontend may be missing authentication")
        elif response.status_code >= 500:
            logger.error(f"Institution Dashboard Error: {response.status_code} "
                        f"for {request.path} from {client_ip}")
        else:
            logger.info(f"Institution Dashboard Success: {response.status_code} "
                       f"for {request.path} from {client_ip}")
    
    def _get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '127.0.0.1')
