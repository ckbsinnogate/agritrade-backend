# Institution Dashboard Monitoring Signals
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.core.cache import cache
import logging
import time

logger = logging.getLogger('institution_dashboard')


@receiver(user_login_failed)
def track_login_failures(sender, credentials, request, **kwargs):
    """
    Track failed login attempts that might affect Institution Dashboard
    """
    if request and hasattr(request, 'META'):
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Track failed logins that might lead to 401s on Institution Dashboard
        failed_login_key = f"failed_logins:{client_ip}"
        failed_count = cache.get(failed_login_key, 0)
        cache.set(failed_login_key, failed_count + 1, 300)  # 5 minutes
        
        if failed_count > 5:
            logger.warning(f"Multiple login failures from {client_ip} - "
                          f"may cause Institution Dashboard 401 loops")


@receiver(user_logged_in)
def reset_login_failure_tracking(sender, user, request, **kwargs):
    """
    Reset failure tracking on successful login
    """
    if request and hasattr(request, 'META'):
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Clear consecutive 401s and failed logins on successful auth
        cache.delete(f"consecutive_401:{client_ip}")
        cache.delete(f"failed_logins:{client_ip}")
        cache.delete(f"circuit_breaker:{client_ip}")
        
        logger.info(f"User {user.username} logged in from {client_ip} - "
                   f"clearing Institution Dashboard protection counters")


def log_institution_dashboard_metrics():
    """
    Log current metrics for Institution Dashboard protection
    """
    # This would be called periodically to monitor system health
    pass
