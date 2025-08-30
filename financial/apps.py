"""
Financial Services App Configuration
Handles loan management, investment tracking, and financial analytics for AgriConnect
"""

from django.apps import AppConfig


class FinancialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financial'
    verbose_name = 'Financial Services'
    
    def ready(self):
        # Import signals if any
        try:
            import financial.signals  # noqa
        except ImportError:
            pass
