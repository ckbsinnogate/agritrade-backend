# Institution Dashboard Protection Package
"""
Institution Dashboard Backend Protection System

This package provides comprehensive protection against infinite API call loops
and other frontend integration issues that can overwhelm the backend.

Components:
- middleware.py: Rate limiting and circuit breaker middleware
- throttling.py: Custom throttling for Institution Dashboard endpoints  
- signals.py: Monitoring and alerting for authentication issues
- apps.py: Application configuration

Purpose:
Prevent Institution Dashboard frontend from making infinite unauthenticated
requests that cause 401 errors and server strain.

Features:
- Rate limiting per IP address
- Circuit breaker pattern for repeated failures
- Enhanced logging for debugging frontend issues
- Helpful error messages for developers
- Automatic recovery mechanisms

Usage:
Add 'institution_dashboard' to INSTALLED_APPS and configure middleware
in Django settings.
"""

__version__ = '1.0.0'
__author__ = 'AgriConnect Development Team'
