
from django.http import JsonResponse
from django.views import View
from payments.models import PaymentGateway
from django.db import connection

class HealthCheckView(View):
    """Health check endpoint for production monitoring"""
    
    def get(self, request):
        """Return system health status"""
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": "production",
            "market": "Ghana",
            "currency": "GHS"
        }
        
        try:
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["database"] = "connected"
            
            # Check payment gateway
            paystack = PaymentGateway.objects.get(name='paystack')
            health_status["paystack"] = "configured"
            health_status["primary_currency"] = paystack.supported_currencies[0]
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            
        return JsonResponse(health_status)
