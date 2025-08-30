"""
AgriConnect Users App Configuration
Enhanced user profiles and role management system
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Profiles & Management'
    
    def ready(self):
        """Import signals when the app is ready"""
        import users.signals
