"""
Paystack Webhook Views
Handle real-time payment notifications from Paystack
"""

import json
import hashlib
import hmac
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.conf import settings
from .models import PaymentGateway, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class PaystackWebhookView(View):
    """
    Paystack Webhook Handler
    Receives and processes real-time payment notifications from Paystack
    """
    
    def post(self, request, *args, **kwargs):
        """Process Paystack webhook notification"""
        
        try:
            # Get webhook payload
            payload = request.body.decode('utf-8')
            signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
            
            # Get Paystack gateway configuration
            try:
                paystack = PaymentGateway.objects.get(name='paystack')
            except PaymentGateway.DoesNotExist:
                logger.error("Paystack gateway not found")
                return HttpResponse('Gateway not configured', status=400)
            
            # Verify webhook signature (if webhook secret is configured)
            if paystack.webhook_secret:
                if not self.verify_signature(payload, signature, paystack.webhook_secret):
                    logger.warning("Invalid webhook signature")
                    return HttpResponse('Invalid signature', status=400)
            else:
                logger.warning("Webhook secret not configured - signature not verified")
            
            # Parse webhook data
            try:
                webhook_data = json.loads(payload)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in webhook payload")
                return HttpResponse('Invalid JSON', status=400)
            
            # Extract event and data
            event = webhook_data.get('event')
            data = webhook_data.get('data', {})
            
            logger.info(f"Received Paystack webhook: {event}")
            
            # Handle different webhook events
            if event == 'charge.success':
                self.handle_payment_success(data)
            elif event == 'charge.failed':
                self.handle_payment_failed(data)
            elif event == 'transfer.success':
                self.handle_transfer_success(data)
            elif event == 'transfer.failed':
                self.handle_transfer_failed(data)
            elif event == 'transfer.reversed':
                self.handle_transfer_reversed(data)
            else:
                logger.info(f"Unhandled webhook event: {event}")
            
            return HttpResponse('OK', status=200)
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return HttpResponse('Server Error', status=500)
    
    def verify_signature(self, payload, signature, secret):
        """Verify Paystack webhook signature"""
        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return False
    
    def handle_payment_success(self, data):
        """Handle successful payment notification"""
        try:
            reference = data.get('reference')
            if not reference:
                logger.error("No reference in payment success data")
                return
            
            # Find transaction by gateway reference
            try:
                transaction = Transaction.objects.get(gateway_reference=reference)
            except Transaction.DoesNotExist:
                logger.error(f"Transaction not found for reference: {reference}")
                return
            
            # Update transaction status
            transaction.status = 'success'
            transaction.processed_at = timezone.now()
            
            # Store external reference (Paystack transaction ID)
            if data.get('id'):
                transaction.external_reference = str(data['id'])
            
            # Update gateway response with webhook data
            if not transaction.gateway_response:
                transaction.gateway_response = {}
            transaction.gateway_response.update({
                'webhook_data': data,
                'webhook_received_at': timezone.now().isoformat()
            })
            
            transaction.save()
            
            # Log successful payment
            amount = data.get('amount', 0) / 100  # Convert from kobo to naira
            customer_email = data.get('customer', {}).get('email', 'Unknown')
            
            logger.info(f"Payment success: {reference} - NGN {amount} - {customer_email}")
            
            # Additional business logic can be added here:
            # - Send confirmation email to customer
            # - Update order status
            # - Release escrow funds
            # - Notify seller/farmer
            # - Update inventory
            
            # Example: Update order status if transaction is linked to an order
            if hasattr(transaction, 'order') and transaction.order:
                self.update_order_status(transaction.order, 'paid')
            
        except Exception as e:
            logger.error(f"Error handling payment success: {str(e)}")
    
    def handle_payment_failed(self, data):
        """Handle failed payment notification"""
        try:
            reference = data.get('reference')
            if not reference:
                logger.error("No reference in payment failed data")
                return
            
            # Find transaction
            try:
                transaction = Transaction.objects.get(gateway_reference=reference)
            except Transaction.DoesNotExist:
                logger.error(f"Transaction not found for reference: {reference}")
                return
            
            # Update transaction status
            transaction.status = 'failed'
            transaction.processed_at = timezone.now()
            
            # Store failure reason
            failure_reason = data.get('gateway_response', 'Payment failed')
            if not transaction.gateway_response:
                transaction.gateway_response = {}
            transaction.gateway_response.update({
                'failure_reason': failure_reason,
                'webhook_data': data,
                'webhook_received_at': timezone.now().isoformat()
            })
            
            transaction.save()
            
            logger.info(f"Payment failed: {reference} - {failure_reason}")
            
            # Additional business logic:
            # - Send failure notification to customer
            # - Cancel order
            # - Restore inventory
            # - Offer retry payment option
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {str(e)}")
    
    def handle_transfer_success(self, data):
        """Handle successful transfer notification"""
        try:
            reference = data.get('reference')
            logger.info(f"Transfer success: {reference}")
            
            # Handle transfer success logic
            # This could be for farmer payouts, refunds, etc.
            
        except Exception as e:
            logger.error(f"Error handling transfer success: {str(e)}")
    
    def handle_transfer_failed(self, data):
        """Handle failed transfer notification"""
        try:
            reference = data.get('reference')
            logger.info(f"Transfer failed: {reference}")
            
            # Handle transfer failure logic
            
        except Exception as e:
            logger.error(f"Error handling transfer failure: {str(e)}")
    
    def handle_transfer_reversed(self, data):
        """Handle reversed transfer notification"""
        try:
            reference = data.get('reference')
            logger.info(f"Transfer reversed: {reference}")
            
            # Handle transfer reversal logic
            
        except Exception as e:
            logger.error(f"Error handling transfer reversal: {str(e)}")
    
    def update_order_status(self, order, status):
        """Update order status based on payment status"""
        try:
            order.payment_status = status
            if status == 'paid':
                order.status = 'confirmed'
            elif status == 'failed':
                order.status = 'payment_failed'
            order.save()
            
            logger.info(f"Order {order.id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")


# Test webhook view for development
@csrf_exempt
@require_POST
def test_webhook(request):
    """Test webhook endpoint for development testing"""
    try:
        payload = json.loads(request.body.decode('utf-8'))
        
        # Log the test webhook
        logger.info(f"Test webhook received: {payload}")
        
        return HttpResponse(json.dumps({
            'status': 'success',
            'message': 'Test webhook received',
            'data': payload
        }), content_type='application/json')
        
    except Exception as e:
        return HttpResponse(json.dumps({
            'status': 'error',
            'message': str(e)
        }), content_type='application/json', status=400)
