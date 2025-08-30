# AgriConnect AI App
"""
AgriConnect AI Integration Module
OpenAI-powered agricultural intelligence for Ghana farmers
"""

from django.apps import AppConfig

class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai'
    verbose_name = 'AgriConnect AI'
    
    def ready(self):
        # Import signals when app is ready
        try:
            import ai.signals  # noqa
        except ImportError:
            pass
