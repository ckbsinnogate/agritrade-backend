"""
Farmer Dashboard App Configuration
Comprehensive farmer dashboard for agricultural management
"""

from django.apps import AppConfig


class FarmerDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'farmer_dashboard'
    verbose_name = 'Farmer Dashboard'
    
    def ready(self):
        # Import signals here to ensure they are connected
        try:
            from . import signals
        except ImportError:
            pass
