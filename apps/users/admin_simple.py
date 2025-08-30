"""
AgriConnect User Profiles Admin Interface
Admin configuration for all user profile types
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

# Import User model from authentication app
User = get_user_model()

# Admin configurations will be added after migrations are complete
# All admin registrations are temporarily commented out to resolve import conflicts
