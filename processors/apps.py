"""
AgriConnect Processors App Configuration
Recipe sharing and processor integration system
"""

from django.apps import AppConfig


class ProcessorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'processors'
    verbose_name = 'Processing Recipes & Processor Integration'
    
    def ready(self):
        """Import signals when the app is ready"""
        pass
