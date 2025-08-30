"""
Admin Dashboard Custom Permissions
=================================
Enhanced permission classes for admin dashboard with proper role checking
and authentication validation.

Author: Assistant with 40+ years of web development experience
"""

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
import logging

logger = logging.getLogger('admin_dashboard')


class IsAdminUserEnhanced(permissions.IsAuthenticated):
    """
    Enhanced admin permission that checks both staff status and ADMIN role
    """
    
    def has_permission(self, request, view):
        # First check authentication
        if not super().has_permission(request, view):
            return False
        
        user = request.user
        
        # Check staff status
        if hasattr(user, 'is_staff') and user.is_staff:
            logger.info(f"Admin access granted to staff user: {user.username}")
            return True
        
        # Check for ADMIN role
        if hasattr(user, 'roles'):
            try:
                admin_roles = user.roles.filter(name='ADMIN')
                if admin_roles.exists():
                    logger.info(f"Admin access granted to ADMIN role user: {user.username}")
                    return True
            except Exception as e:
                logger.warning(f"Error checking ADMIN role for {user.username}: {e}")
        
        logger.warning(f"Admin access denied for user: {user.username}")
        return False
    
    def has_object_permission(self, request, view, obj):
        # For object-level permissions, use same logic
        return self.has_permission(request, view)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows read access to authenticated users,
    but write access only to admin users
    """
    
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for admin users
        if not request.user or not request.user.is_authenticated:
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


class AdminDashboardAccessPermission(permissions.BasePermission):
    """
    Special permission for admin dashboard endpoints that provides
    detailed error messages for troubleshooting
    """
    
    def has_permission(self, request, view):
        # Check authentication
        if not request.user or not request.user.is_authenticated:
            self.message = {
                'error': 'Authentication Required',
                'detail': 'Admin dashboard requires valid authentication',
                'help': {
                    'solution': 'Include valid JWT token in Authorization header',
                    'format': 'Authorization: Bearer <your_token>',
                    'auth_endpoint': '/api/v1/auth/login/'
                }
            }
            return False
        
        # Check admin privileges
        user = request.user
        is_admin = False
        
        # Check staff status
        if hasattr(user, 'is_staff') and user.is_staff:
            is_admin = True
        
        # Check for ADMIN role
        elif hasattr(user, 'roles'):
            try:
                admin_roles = user.roles.filter(name='ADMIN')
                if admin_roles.exists():
                    is_admin = True
            except Exception:
                pass
        
        if not is_admin:
            self.message = {
                'error': 'Admin Privileges Required',
                'detail': 'This endpoint requires administrator privileges',
                'help': {
                    'solution': 'Contact system administrator for admin role assignment',
                    'required_privileges': 'is_staff=True OR ADMIN role',
                    'contact': 'admin@agriconnect.com'
                }
            }
            return False
        
        return True
