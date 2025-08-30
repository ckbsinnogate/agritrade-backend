# Institution Dashboard Apps Configuration
from django.apps import AppConfig


class InstitutionDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'institution_dashboard'
    verbose_name = 'Institution Dashboard Protection'
    
    def ready(self):
        """
        Initialize Institution Dashboard protection systems
        """
        # Import signals for monitoring
        from . import signals
        
        # Set up logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Institution Dashboard Protection Middleware loaded")
        logger.info("Rate limiting and circuit breaker protection active")
        logger.info("Enhanced logging for frontend integration debugging enabled")
