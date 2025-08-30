"""
Fixed Communications Views for Frontend Compatibility
Simple implementation for conversations and notifications endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q, Count, Max
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import CommunicationLog, CommunicationPreference

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversations_list(request):
    """List conversations or create new conversation - Frontend Compatible"""
    try:
        if request.method == 'GET':
            # Return simplified conversations based on available data
            conversations = []
            
            # Get recent communication logs as conversations
            recent_logs = CommunicationLog.objects.filter(
                user=request.user
            ).order_by('-created_at')[:20]
            
            # Convert logs to conversation format
            for log in recent_logs:
                conversations.append({
                    'id': str(log.id),
                    'participant_phone': log.recipient if log.recipient else 'Unknown',
                    'participant_name': log.recipient if log.recipient else 'Unknown Contact',
                    'last_message': log.content_snippet[:100] if log.content_snippet else 'No content',
                    'last_message_date': log.created_at,
                    'message_count': 1,
                    'unread_count': 0
                })
            
            return Response({
                'success': True,
                'conversations': conversations,
                'total_count': len(conversations)
            })
            
        elif request.method == 'POST':
            # Create new conversation (basic implementation)
            recipient_phone = request.data.get('recipient_phone')
            message_content = request.data.get('message', '')
            
            if not recipient_phone:
                return Response({
                    'success': False,
                    'error': 'recipient_phone is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create communication log entry
            log = CommunicationLog.objects.create(
                user=request.user,
                communication_type='sms',
                recipient=recipient_phone,
                purpose='conversation',
                status='pending',
                content_snippet=message_content[:200]
            )
            
            return Response({
                'success': True,
                'conversation_id': str(log.id),
                'message': 'Conversation created successfully'
            })
            
    except Exception as e:
        logger.error(f"Conversations error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """List notifications or create new notification - Frontend Compatible"""
    try:
        if request.method == 'GET':
            # Get user's notifications
            notifications = []
            
            # Get recent communication logs as notifications
            recent_logs = CommunicationLog.objects.filter(
                user=request.user
            ).order_by('-created_at')[:50]
            
            # Convert logs to notification format
            for log in recent_logs:
                notifications.append({
                    'id': str(log.id),
                    'title': log.purpose.title() if log.purpose else 'Notification',
                    'message': log.content_snippet[:200] if log.content_snippet else 'No content',
                    'type': log.communication_type,
                    'created_at': log.created_at,
                    'read': False,
                    'priority': 'normal'
                })
            
            return Response({
                'success': True,
                'notifications': notifications,
                'unread_count': len([n for n in notifications if not n['read']])
            })
            
        elif request.method == 'POST':
            # Create new notification (admin only)
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            message_content = request.data.get('message', '')
            recipient_phone = request.data.get('recipient_phone', '')
            
            if not message_content:
                return Response({
                    'success': False,
                    'error': 'message is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create notification log
            log = CommunicationLog.objects.create(
                user=request.user,
                communication_type='push',
                recipient=recipient_phone or request.user.email,
                purpose='notification',
                status='pending',
                content_snippet=message_content[:200]
            )
            
            return Response({
                'success': True,
                'notification_id': str(log.id),
                'message': 'Notification created successfully'
            })
            
    except Exception as e:
        logger.error(f"Notifications error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    """Get or update user notification settings - Frontend Compatible"""
    try:
        if request.method == 'GET':
            # Get user's notification preferences
            try:
                preferences = CommunicationPreference.objects.get(user=request.user)
                return Response({
                    'success': True,
                    'settings': {
                        'email_notifications': getattr(preferences, 'email_enabled', True),
                        'sms_notifications': getattr(preferences, 'sms_enabled', True),
                        'marketing_emails': getattr(preferences, 'marketing_enabled', False),
                        'order_updates': getattr(preferences, 'order_notifications', True),
                        'price_alerts': getattr(preferences, 'price_alerts', True),
                        'weather_alerts': getattr(preferences, 'weather_alerts', True),
                        'language': getattr(preferences, 'language', 'en'),
                        'timezone': getattr(preferences, 'timezone', 'Africa/Accra'),
                        'quiet_hours': {
                            'start': getattr(preferences, 'quiet_hours_start', None),
                            'end': getattr(preferences, 'quiet_hours_end', None)
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
                    defaults={'language': 'en', 'timezone': 'Africa/Accra'}
                )
                
                # Update preferences from request data (using safe attribute setting)
                settings_map = {
                    'email_notifications': 'email_enabled',
                    'sms_notifications': 'sms_enabled', 
                    'marketing_emails': 'marketing_enabled',
                    'order_updates': 'order_notifications',
                    'price_alerts': 'price_alerts',
                    'weather_alerts': 'weather_alerts',
                    'language': 'language',
                    'timezone': 'timezone'
                }
                
                for frontend_key, model_field in settings_map.items():
                    if frontend_key in request.data:
                        if hasattr(preferences, model_field):
                            setattr(preferences, model_field, request.data[frontend_key])
                
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
