"""
Main URL configuration for myapiproject.
DigitalOcean App Platform compatible URL routing.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health import health_check

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health check for DigitalOcean App Platform
    path('api/health/', health_check, name='health-check'),
    
    # Main API routes - delegate to agriconnect app
    path('', include('agriconnect.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
