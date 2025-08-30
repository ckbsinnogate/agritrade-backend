from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import datetime

def health_check(request):
    """
    Health check endpoint for DigitalOcean App Platform
    Returns application status and database connectivity
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Get application info
        response_data = {
            "status": "healthy",
            "message": "AgriTrade API is running successfully",
            "version": "2.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "database": "connected",
            "total_applications": 17,
            "applications": [
                "users", "products", "orders", "payments", "communications",
                "admin_dashboard", "advertisements", "ai", "farmer_dashboard",
                "financial", "processing", "reviews", "subscriptions",
                "traceability", "warehouses", "weather", "notifications"
            ],
            "environment": "production" if not settings.DEBUG else "development",
            "deployment_platform": "DigitalOcean App Platform"
        }
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "message": "Health check failed",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }, status=503)
