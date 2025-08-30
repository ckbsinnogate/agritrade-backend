"""
AgriConnect Communications Views
Enhanced SMS & OTP Integration System (PRD Section 4.7)

Features:
- REST API for SMS management
- OTP generation and verification
- Communication preferences
- Analytics and reporting
- Bulk messaging
- Template management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

from .models import (
    SMSProvider, SMSTemplate, SMSMessage, OTPCode,
    CommunicationPreference, CommunicationLog
)
from .serializers import (
    SMSProviderSerializer, SMSTemplateSerializer, SMSMessageSerializer,
    OTPCodeSerializer, CommunicationPreferenceSerializer, CommunicationLogSerializer,
    SendSMSSerializer, GenerateOTPSerializer, VerifyOTPSerializer,
    BulkSMSSerializer, SMSAnalyticsSerializer
)
from .services import SMSService, OTPService

logger = logging.getLogger(__name__)

class SMSProviderViewSet(viewsets.ModelViewSet):
    """ViewSet for SMS providers management"""
    queryset = SMSProvider.objects.all()
    serializer_class = SMSProviderSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Filter providers based on status"""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('priority', 'name')

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SMS provider connection"""
        provider = self.get_object()
        
        try:
            # Initialize SMS service with specific provider
            sms_service = SMSService(provider=provider)
            
            # Send test message
            test_number = request.data.get('test_number', '+233200000000')
            result = sms_service.send_sms(
                phone_number=test_number,
                message="AgriConnect SMS provider test message",
                test_mode=True
            )
            
            return Response({
                'success': result['success'],
                'message': result.get('message', 'Test completed'),
                'provider_response': result.get('provider_response')
            })
            
        except Exception as e:
            logger.error(f"Provider test failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SMSTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for SMS templates management"""
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter templates based on language and category"""
        queryset = super().get_queryset()
        
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        active_only = self.request.query_params.get('active_only', 'false').lower() == 'true'
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('category', 'language', 'name')

    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """Create default SMS templates"""
        try:
            self._create_default_templates()
            return Response({
                'message': 'Default templates created successfully',
                'count': SMSTemplate.objects.filter(name__startswith='Default').count()
            })
        except Exception as e:
            logger.error(f"Failed to create default templates: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def _create_default_templates(self):
        """Create default SMS and email templates"""
        templates = [
            # OTP Templates
            {
                'name': 'Default OTP Verification - English',
                'category': 'otp',
                'language': 'en',
                'template_text': 'Your AgriConnect verification code is: {code}. Valid for {minutes} minutes. Do not share this code.',
                'variables': ['code', 'minutes']
            },
            {
                'name': 'Default OTP Verification - Twi',
                'category': 'otp',
                'language': 'tw',
                'template_text': 'Wo AgriConnect verification code ne: {code}. Ebeye adwuma sikafiri {minutes}. Mmfa code yi nkyekyɛ obiara.',
                'variables': ['code', 'minutes']
            },
            {
                'name': 'Default OTP Verification - Hausa',
                'category': 'otp',
                'language': 'ha',
                'template_text': 'Lambar tabbatar da AgriConnect naka ita ce: {code}. Tana aiki har zuwa mintuna {minutes}. Kada ka raba wannan lambar.',
                'variables': ['code', 'minutes']
            },
            
            # Order Confirmation Templates
            {
                'name': 'Default Order Confirmation - English',
                'category': 'order',
                'language': 'en',
                'template_text': 'Order confirmed! Order #{order_id} for {product_name} - {quantity} {unit}. Total: {currency}{amount}. Delivery: {delivery_date}.',
                'variables': ['order_id', 'product_name', 'quantity', 'unit', 'currency', 'amount', 'delivery_date']
            },
            {
                'name': 'Default Order Confirmation - Twi',
                'category': 'order',
                'language': 'tw',
                'template_text': 'Woapiè order no! Order #{order_id} wɔ {product_name} - {quantity} {unit}. Abodiè: {currency}{amount}. Delivery: {delivery_date}.',
                'variables': ['order_id', 'product_name', 'quantity', 'unit', 'currency', 'amount', 'delivery_date']
            },
            
            # Payment Notification Templates
            {
                'name': 'Default Payment Success - English',
                'category': 'payment',
                'language': 'en',
                'template_text': 'Payment received! {currency}{amount} for order #{order_id}. Transaction ID: {transaction_id}. Thank you for using AgriConnect!',
                'variables': ['currency', 'amount', 'order_id', 'transaction_id']
            },
            {
                'name': 'Default Payment Failed - English',
                'category': 'payment',
                'language': 'en',
                'template_text': 'Payment failed for order #{order_id}. Please try again or contact support. AgriConnect Team.',
                'variables': ['order_id']
            },
            
            # Welcome Templates
            {
                'name': 'Default Welcome Message - English',
                'category': 'marketing',
                'language': 'en',
                'template_text': 'Welcome to AgriConnect, {name}! Your account is now active. Start buying/selling agricultural products today. Download our app: {app_link}',
                'variables': ['name', 'app_link']
            },
            {
                'name': 'Default Welcome Message - Twi',
                'category': 'marketing',
                'language': 'tw',
                'template_text': 'Akwaaba wo AgriConnect mu, {name}! Wo account no ayε adwuma sεsei. Fi ase tɔn/tɔ kuayε nneεma nnε. Download yεn app: {app_link}',
                'variables': ['name', 'app_link']
            },
            
            # Price Alert Templates
            {
                'name': 'Default Price Alert - English',
                'category': 'alert',
                'language': 'en',
                'template_text': 'Price Alert! {product_name} is now {currency}{new_price}/{unit} (was {currency}{old_price}). Check it out on AgriConnect!',
                'variables': ['product_name', 'currency', 'new_price', 'unit', 'old_price']
            },
            
            # Delivery Notification Templates
            {
                'name': 'Default Delivery Update - English',
                'category': 'delivery',
                'language': 'en',
                'template_text': 'Delivery update for order #{order_id}: {status}. Expected delivery: {delivery_time}. Track: {tracking_link}',
                'variables': ['order_id', 'status', 'delivery_time', 'tracking_link']
            },
            
            # Emergency/Weather Alerts
            {
                'name': 'Default Weather Alert - English',
                'category': 'alert',
                'language': 'en',
                'template_text': 'Weather Alert for {location}: {weather_condition} expected. Temperature: {temperature}°C. Protect your crops! AgriConnect Weather Service.',
                'variables': ['location', 'weather_condition', 'temperature']
            },
        ]
        
        # Email Templates
        email_templates = [
            {
                'name': 'Default Email OTP - English',
                'category': 'otp',
                'language': 'en',
                'template_text': '''Subject: Your AgriConnect Verification Code
                
Hello,

Your AgriConnect verification code is: {code}

This code is valid for {minutes} minutes. Please do not share this code with anyone.

If you didn't request this code, please ignore this email.

Best regards,
AgriConnect Team''',
                'variables': ['code', 'minutes']
            },
            {
                'name': 'Default Email Order Confirmation - English',
                'category': 'order',
                'language': 'en',
                'template_text': '''Subject: Order Confirmation - #{order_id}
                
Dear {customer_name},

Thank you for your order on AgriConnect!

Order Details:
- Order ID: #{order_id}
- Product: {product_name}
- Quantity: {quantity} {unit}
- Total Amount: {currency}{amount}
- Delivery Date: {delivery_date}
- Delivery Address: {delivery_address}

You can track your order at: {tracking_link}

Thank you for choosing AgriConnect!

Best regards,
AgriConnect Team''',
                'variables': ['customer_name', 'order_id', 'product_name', 'quantity', 'unit', 'currency', 'amount', 'delivery_date', 'delivery_address', 'tracking_link']
            },
            {
                'name': 'Default Email Payment Receipt - English',
                'category': 'payment',
                'language': 'en',
                'template_text': '''Subject: Payment Receipt - Order #{order_id}
                
Dear {customer_name},

We have received your payment for order #{order_id}.

Payment Details:
- Amount: {currency}{amount}
- Transaction ID: {transaction_id}
- Payment Method: {payment_method}
- Date: {payment_date}

Your order is now being processed and will be delivered on {delivery_date}.

Thank you for your business!

Best regards,
AgriConnect Team''',
                'variables': ['customer_name', 'order_id', 'currency', 'amount', 'transaction_id', 'payment_method', 'payment_date', 'delivery_date']
            },
        ]
        
        # Create SMS templates
        for template_data in templates:
            SMSTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
        
        # Create email templates (stored as SMS templates with email category)
        for template_data in email_templates:
            template_data['category'] = 'email'
            SMSTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )

class SMSMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for SMS messages management"""
    queryset = SMSMessage.objects.all()
    serializer_class = SMSMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter messages based on user and status"""
        queryset = super().get_queryset()
        
        # Filter by user for non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(recipient=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['post'])
    def send_sms(self, request):
        """Send single SMS message"""
        serializer = SendSMSSerializer(data=request.data)
        if serializer.is_valid():
            try:
                sms_service = SMSService()                result = sms_service.send_sms(
                    phone_number=serializer.validated_data['phone_number'],
                    message_text=serializer.validated_data.get('message_text', ''),
                    template_id=serializer.validated_data.get('template_id'),
                    variables=serializer.validated_data.get('variables', {}),
                    user=request.user,
                    schedule_time=serializer.validated_data.get('schedule_time')
                )
                
                if result['success']:
                    return Response({
                        'success': True,
                        'message_id': result['message_id'],
                        'cost': result.get('cost'),
                        'message': 'SMS sent successfully'
                    })
                else:
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"SMS sending failed: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_bulk_sms(self, request):
        """Send bulk SMS messages"""
        serializer = BulkSMSSerializer(data=request.data)
        if serializer.is_valid():
            try:
                sms_service = SMSService()
                results = sms_service.send_bulk_sms(
                    recipients=serializer.validated_data['recipients'],
                    message_text=serializer.validated_data.get('message_text',
                    template_id=serializer.validated_data.get('template_id'),
                    variables=serializer.validated_data.get('variables', {}),
                    user=request.user,
                    schedule_time=serializer.validated_data.get('schedule_time')
                )
                
                return Response({
                    'success': True,
                    'total_recipients': len(serializer.validated_data['recipients']),
                    'successful_sends': results['successful'],
                    'failed_sends': results['failed'],
                    'total_cost': results['total_cost'],
                    'message': f"Bulk SMS completed: {results['successful']} sent, {results['failed']} failed"
                })
                
            except Exception as e:
                logger.error(f"Bulk SMS failed: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get SMS analytics"""
        try:
            # Date range filter
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)
            
            queryset = self.get_queryset().filter(created_at__gte=start_date)
            
            # Basic stats
            total_sent = queryset.count()
            total_delivered = queryset.filter(status='delivered').count()
            total_failed = queryset.filter(status='failed').count()
            
            delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
            
            # Cost analysis
            total_cost = queryset.aggregate(Sum('cost'))['cost__sum'] or 0
            avg_cost = total_cost / total_sent if total_sent > 0 else 0
            
            # Popular templates
            popular_templates = list(
                queryset.filter(template__isnull=False)
                .values('template__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
            
            # Daily stats for the last 7 days
            daily_stats = []
            for i in range(7):
                date = timezone.now().date() - timedelta(days=i)
                day_messages = queryset.filter(created_at__date=date)
                daily_stats.append({
                    'date': date.isoformat(),
                    'sent': day_messages.count(),
                    'delivered': day_messages.filter(status='delivered').count(),
                    'cost': float(day_messages.aggregate(Sum('cost'))['cost__sum'] or 0)
                })
            
            analytics_data = {
                'total_sent': total_sent,
                'total_delivered': total_delivered,
                'total_failed': total_failed,
                'delivery_rate': round(delivery_rate, 2),
                'total_cost': float(total_cost),
                'average_cost_per_sms': round(avg_cost, 4),
                'popular_templates': popular_templates,
                'daily_stats': daily_stats
            }
            
            serializer = SMSAnalyticsSerializer(analytics_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Analytics calculation failed: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OTPCodeViewSet(viewsets.ModelViewSet):
    """ViewSet for OTP management"""
    queryset = OTPCode.objects.all()
    serializer_class = OTPCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter OTP codes based on user"""
        queryset = super().get_queryset()
        
        # Filter by user for non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['post'])
    def generate_otp(self, request):
        """Generate new OTP code"""
        serializer = GenerateOTPSerializer(data=request.data)
        if serializer.is_valid():
            try:
                otp_service = OTPService()
                result = otp_service.generate_otp(
                    user=request.user,
                    phone_number=serializer.validated_data.get('phone_number'),
                    email=serializer.validated_data.get('email'),
                    purpose=serializer.validated_data['purpose'],
                    length=serializer.validated_data['length'],
                    expires_in_minutes=serializer.validated_data['expires_in_minutes']
                )
                
                if result['success']:
                    return Response({
                        'success': True,
                        'otp_id': result['otp_id'],
                        'expires_at': result['expires_at'],
                        'delivery_method': result['delivery_method'],
                        'message': 'OTP generated and sent successfully'
                    })
                else:
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"OTP generation failed: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        """Verify OTP code"""
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            try:
                otp_service = OTPService()
                result = otp_service.verify_otp(
                    otp_id=serializer.validated_data['otp_id'],
                    code=serializer.validated_data['code'],
                    user=request.user
                )
                
                if result['success']:
                    return Response({
                        'success': True,
                        'verified': True,
                        'purpose': result.get('purpose'),
                        'message': 'OTP verified successfully'
                    })
                else:
                    return Response({
                        'success': False,
                        'verified': False,
                        'error': result['error'],
                        'attempts_remaining': result.get('attempts_remaining')
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"OTP verification failed: {str(e)}")
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommunicationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for communication preferences"""
    queryset = CommunicationPreference.objects.all()
    serializer_class = CommunicationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter preferences based on user"""
        if not self.request.user.is_staff:
            return self.queryset.filter(user=self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):
        """Set user when creating preference"""
        serializer.save(user=self.request.user)

class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for communication logs (read-only)"""
    queryset = CommunicationLog.objects.all()
    serializer_class = CommunicationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter logs based on user"""
        queryset = super().get_queryset()
        
        # Filter by user for non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by channel
        channel = self.request.query_params.get('channel')
        if channel:
            queryset = queryset.filter(channel=channel)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversations_list(request):
    """List conversations or create new conversation"""
    try:
        if request.method == 'GET':
            # Get user's conversations (using communication logs as conversations)
            conversations = CommunicationLog.objects.filter(
                Q(sender=request.user) | Q(recipient_phone=request.user.phone_number)
            ).values('recipient_phone', 'sender').annotate(
                last_message_date=timezone.Max('created_at'),
                message_count=Count('id')
            ).order_by('-last_message_date')[:20]
            
            conversation_list = []
            for conv in conversations:
                # Get the latest message
                latest_message = CommunicationLog.objects.filter(
                    recipient_phone=conv['recipient_phone']
                ).order_by('-created_at').first()
                
                conversation_list.append({
                    'id': f"{conv['recipient_phone']}_{conv['sender']}",
                    'participant_phone': conv['recipient_phone'],
                    'participant_name': conv['recipient_phone'],  # Would need user lookup for real name
                    'last_message': latest_message.message_content if latest_message else '',
                    'last_message_date': conv['last_message_date'],
                    'message_count': conv['message_count'],
                    'unread_count': 0  # Would need to track read status
                })
            
            return Response({
                'success': True,
                'conversations': conversation_list,
                'total_count': len(conversation_list)
            })
            
        elif request.method == 'POST':
            # Create new conversation (send message)
            recipient_phone = request.data.get('recipient_phone')
            message_content = request.data.get('message')
            
            if not recipient_phone or not message_content:
                return Response({
                    'success': False,
                    'error': 'recipient_phone and message are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use SMS service to send message
            sms_service = SMSService()
            result = sms_service.send_sms(recipient_phone, message_content)
            
            if result.get('success'):
                # Log the conversation
                CommunicationLog.objects.create(
                    sender=request.user,
                    recipient_phone=recipient_phone,
                    message_content=message_content,
                    message_type='conversation',
                    delivery_status='sent'
                )
                
                return Response({
                    'success': True,
                    'message': 'Message sent successfully',
                    'conversation_id': f"{recipient_phone}_{request.user.id}"
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to send message')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """List notifications or create new notification"""
    try:
        if request.method == 'GET':
            # Get user's notifications (using communication logs as notifications)
            notifications = CommunicationLog.objects.filter(
                recipient_phone=request.user.phone_number,
                message_type__in=['notification', 'alert', 'reminder']
            ).order_by('-created_at')[:50]
            
            notification_list = []
            for notif in notifications:
                notification_list.append({
                    'id': notif.id,
                    'title': notif.message_type.title(),
                    'message': notif.message_content,
                    'type': notif.message_type,
                    'created_at': notif.created_at,
                    'read': False,  # Would need to track read status
                    'priority': 'normal'  # Would need priority field
                })
            
            return Response({
                'success': True,
                'notifications': notification_list,
                'unread_count': len([n for n in notification_list if not n['read']])
            })
            
        elif request.method == 'POST':
            # Create new notification (admin only)
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            message_content = request.data.get('message')
            recipient_phone = request.data.get('recipient_phone')
            message_type = request.data.get('type', 'notification')
            
            if not message_content or not recipient_phone:
                return Response({
                    'success': False,
                    'error': 'message and recipient_phone are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create notification log
            notification = CommunicationLog.objects.create(
                sender=request.user,
                recipient_phone=recipient_phone,
                message_content=message_content,
                message_type=message_type,
                delivery_status='pending'
            )
            
            return Response({
                'success': True,
                'notification_id': notification.id,
                'message': 'Notification created successfully'
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    """Get or update user notification settings"""
    try:
        if request.method == 'GET':
            # Get user's notification preferences
            try:
                preferences = CommunicationPreference.objects.get(user=request.user)
                return Response({
                    'success': True,
                    'settings': {
                        'email_notifications': preferences.email_enabled,
                        'sms_notifications': preferences.sms_enabled,
                        'marketing_emails': preferences.marketing_enabled,
                        'order_updates': preferences.order_notifications,
                        'price_alerts': preferences.price_alerts,
                        'weather_alerts': preferences.weather_alerts,
                        'language': preferences.language,
                        'timezone': preferences.timezone,
                        'quiet_hours': {
                            'start': preferences.quiet_hours_start,
                            'end': preferences.quiet_hours_end
                        }
                    }
                })
            except CommunicationPreference.DoesNotExist:
                # Return default settings
                return Response({
                    'success': True,
                    'settings': {
                        'email_notifications': True,
                        'sms_notifications': True,
                        'marketing_emails': False,
                        'order_updates': True,
                        'price_alerts': True,
                        'weather_alerts': True,
                        'language': 'en',
                        'timezone': 'Africa/Accra',
                        'quiet_hours': {
                            'start': None,
                            'end': None
                        }
                    }
                })
                
        elif request.method == 'POST':
            # Update notification settings
            try:
                preferences, created = CommunicationPreference.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'language': 'en',
                        'timezone': 'Africa/Accra'
                    }
                )
                
                # Update preferences from request data
                if 'email_notifications' in request.data:
                    preferences.email_enabled = request.data['email_notifications']
                if 'sms_notifications' in request.data:
                    preferences.sms_enabled = request.data['sms_notifications']
                if 'marketing_emails' in request.data:
                    preferences.marketing_enabled = request.data['marketing_emails']
                if 'order_updates' in request.data:
                    preferences.order_notifications = request.data['order_updates']
                if 'price_alerts' in request.data:
                    preferences.price_alerts = request.data['price_alerts']
                if 'weather_alerts' in request.data:
                    preferences.weather_alerts = request.data['weather_alerts']
                if 'language' in request.data:
                    preferences.language = request.data['language']
                if 'timezone' in request.data:
                    preferences.timezone = request.data['timezone']
                
                preferences.save()
                
                return Response({
                    'success': True,
                    'message': 'Notification settings updated successfully'
                })
                
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Failed to update settings: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
