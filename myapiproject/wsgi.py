"""
WSGI config for myapiproject.
DigitalOcean App Platform compatible configuration.
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings for DigitalOcean App Platform
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings_production')

application = get_wsgi_application()
