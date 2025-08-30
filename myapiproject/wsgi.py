"""
WSGI config for myapiproject.
DigitalOcean App Platform compatible configuration.
"""

import os
from django.core.wsgi import get_wsgi_application

# Use App Platform optimized settings for DigitalOcean App Platform
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings_appplatform')

application = get_wsgi_application()
