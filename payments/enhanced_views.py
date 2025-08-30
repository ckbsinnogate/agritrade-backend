"""
Enhanced Payment Views with Real Paystack Integration
Complete payment processing with real API integration
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from decimal import Decimal
import requests
import json
import uuid
from datetime import datetime

from .models import PaymentGateway, Transaction
from .serializers import TransactionSerializer
from orders.models import Order


class PaystackPaymentService:
    """Real Paystack payment service integration"""
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.secret_key = gateway.secret_key
        self.public_key = gateway.public_key
        self.base_url = "https://api.paystack.co"
        
    def initialize_payment(self, amount, email, currency="NGN", metadata=None):
        """Initialize payment with Paystack"""
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
          # Convert amount to kobo/smallest unit
        amount_in_kobo = int(amount * 100)
        
        # Don't specify currency to use account default (fixes currency error)
        payload = {
            "email": email,
            "amount": amount_in_kobo,
            "callback_url": f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/api/v1/payments/callback/",
            "metadata": metadata or {}
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    return {
                        "success": True,
                        "reference": data["data"]["reference"],
                        "authorization_url": data["data"]["authorization_url"],
                        "access_code": data["data"]["access_code"]
                    }
            
            return {
                "success": False,
                "error": response.json().get("message", "Payment initialization failed")
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
    
    def verify_payment(self, reference):
        """Verify payment with Paystack"""
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    transaction_data = data["data"]
                    return {
                        "success": True,
                        "status": transaction_data["status"],
                        "amount": Decimal(str(transaction_data["amount"])) / 100,
                        "currency": transaction_data["currency"],
                        "paid_at": transaction_data.get("paid_at"),
                        "gateway_response": transaction_data
                    }
            
            return {
                "success": False,
                "error": response.json().get("message", "Payment verification failed")
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }


class PaystackPaymentView(APIView):
    """Enhanced payment view with real Paystack integration"""
    
    def post(self, request):
        """Initialize payment with Paystack"""
        
        try:
            # Get request data
            order_id = request.data.get('order_id')
            amount = Decimal(str(request.data.get('amount', 0)))
            currency = request.data.get('currency', 'NGN')
            email = request.data.get('email') or request.user.email
            
            # Validate inputs
            if not order_id or amount <= 0 or not email:
                return Response({
                    "error": "Missing required fields: order_id, amount, email"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get order
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response({
                    "error": "Order not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get Paystack gateway
            paystack_gateway = PaymentGateway.objects.filter(
                name='paystack', 
                is_active=True
            ).first()
            
            if not paystack_gateway or not paystack_gateway.secret_key:
                return Response({
                    "error": "Paystack gateway not configured"
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Initialize Paystack service
            paystack_service = PaystackPaymentService(paystack_gateway)
            
            # Create transaction record
            transaction = Transaction.objects.create(
                user=request.user,
                order=order,
                gateway=paystack_gateway,
                amount=amount,
                currency=currency,
                gateway_reference=f"TXN_{uuid.uuid4().hex[:12].upper()}",
                status='pending',
                transaction_type='payment',
                metadata={
                    "email": email,
                    "order_number": order.order_number,
                    "customer_name": f"{request.user.first_name} {request.user.last_name}".strip(),
                    "initiated_at": datetime.now().isoformat()
                }
            )
            
            # Initialize payment with Paystack
            payment_result = paystack_service.initialize_payment(
                amount=amount,
                email=email,
                currency=currency,
                metadata={
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                    "transaction_id": str(transaction.id),
                    "customer_id": str(request.user.id),
                    "purpose": "Agricultural Product Purchase - AgriConnect"
                }
            )
            
            if payment_result["success"]:
                # Update transaction with Paystack reference
                transaction.external_reference = payment_result["reference"]
                transaction.gateway_response = {
                    "authorization_url": payment_result["authorization_url"],
                    "access_code": payment_result["access_code"],
                    "reference": payment_result["reference"]
                }
                transaction.save()
                
                return Response({
                    "success": True,
                    "message": "Payment initialized successfully",
                    "data": {
                        "transaction_id": str(transaction.id),
                        "reference": payment_result["reference"],
                        "authorization_url": payment_result["authorization_url"],
                        "amount": float(amount),
                        "currency": currency,
                        "email": email,
                        "order_number": order.order_number
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                # Update transaction status
                transaction.status = 'failed'
                transaction.gateway_response = {"error": payment_result["error"]}
                transaction.save()
                
                return Response({
                    "success": False,
                    "error": payment_result["error"]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "error": f"Payment initialization failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaystackVerifyView(APIView):
    """Verify Paystack payment"""
    
    def post(self, request):
        """Verify payment with Paystack"""
        
        try:
            reference = request.data.get('reference')
            
            if not reference:
                return Response({
                    "error": "Payment reference is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get transaction
            try:
                transaction = Transaction.objects.get(
                    external_reference=reference,
                    user=request.user
                )
            except Transaction.DoesNotExist:
                return Response({
                    "error": "Transaction not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get Paystack gateway
            paystack_gateway = transaction.gateway
            paystack_service = PaystackPaymentService(paystack_gateway)
            
            # Verify payment
            verify_result = paystack_service.verify_payment(reference)
            
            if verify_result["success"]:
                # Update transaction status
                if verify_result["status"] == "success":
                    transaction.status = 'completed'
                    transaction.processed_at = datetime.now()
                elif verify_result["status"] == "failed":
                    transaction.status = 'failed'
                else:
                    transaction.status = 'processing'
                
                transaction.gateway_response.update(verify_result["gateway_response"])
                transaction.save()
                
                # Update order status if payment successful
                if transaction.status == 'completed':
                    order = transaction.order
                    order.status = 'paid'
                    order.save()
                
                return Response({
                    "success": True,
                    "message": "Payment verification completed",
                    "data": {
                        "transaction_id": str(transaction.id),
                        "reference": reference,
                        "status": transaction.status,
                        "amount": float(verify_result.get("amount", transaction.amount)),
                        "currency": verify_result.get("currency", transaction.currency),
                        "paid_at": verify_result.get("paid_at"),
                        "order_status": transaction.order.status
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "error": verify_result["error"]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "error": f"Payment verification failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusView(APIView):
    """Get payment status and transaction history"""
    
    def get(self, request, transaction_id=None):
        """Get payment status"""
        
        try:
            if transaction_id:
                # Get specific transaction
                try:
                    transaction = Transaction.objects.get(
                        id=transaction_id,
                        user=request.user
                    )
                    serializer = TransactionSerializer(transaction)
                    return Response({
                        "success": True,
                        "data": serializer.data
                    }, status=status.HTTP_200_OK)
                    
                except Transaction.DoesNotExist:
                    return Response({
                        "error": "Transaction not found"
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # Get all user transactions
                transactions = Transaction.objects.filter(
                    user=request.user
                ).order_by('-created_at')
                
                serializer = TransactionSerializer(transactions, many=True)
                return Response({
                    "success": True,
                    "data": serializer.data,
                    "count": transactions.count()
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "error": f"Failed to get payment status: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
