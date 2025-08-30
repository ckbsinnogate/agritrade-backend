"""
SMS/USSD Views for AgriConnect Farmer Onboarding
Handles incoming SMS and USSD requests from farmers
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

from .sms_farmer_onboarding import sms_onboarding_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def sms_webhook(request):
    """Handle incoming SMS messages from Africa's Talking"""
    try:
        # Parse incoming SMS data
        phone_number = request.POST.get('from')
        message = request.POST.get('text', '').strip()
        
        if not phone_number or not message:
            return JsonResponse({'error': 'Missing phone number or message'}, status=400)
        
        logger.info(f"Received SMS from {phone_number}: {message}")
        
        # Process SMS command
        response_message = sms_onboarding_service.process_sms_command(phone_number, message)
        
        # Send response back to farmer
        result = sms_onboarding_service.sms_service.send_sms(phone_number, response_message)
        
        return JsonResponse({
            'success': True,
            'response_sent': True,
            'message': response_message,
            'sms_result': result
        })
        
    except Exception as e:
        logger.error(f"SMS webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ussd_webhook(request):
    """Handle incoming USSD requests from Africa's Talking"""
    try:
        # Parse USSD data
        session_id = request.POST.get('sessionId')
        service_code = request.POST.get('serviceCode')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text', '')
        
        if not phone_number:
            return HttpResponse("END Error: Missing phone number", content_type="text/plain")
        
        logger.info(f"USSD session {session_id} from {phone_number}: {text}")
        
        # Process USSD request
        response = sms_onboarding_service.ussd_service.handle_ussd_request(
            session_id, service_code, phone_number, text
        )
        
        return HttpResponse(response, content_type="text/plain")
        
    except Exception as e:
        logger.error(f"USSD webhook error: {str(e)}")
        return HttpResponse("END Error processing request. Please try again.", content_type="text/plain")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def sms_test_endpoint(request):
    """Test endpoint for SMS functionality"""
    if request.method == 'GET':
        return JsonResponse({
            'service': 'AgriConnect SMS Service',
            'status': 'active',
            'supported_commands': [
                'START/HELP - Get help',
                'ASK [question] - Ask AgriBot',
                'CROP [crop] [location] - Get crop advice',
                'DISEASE [symptoms] - Disease diagnosis',
                'PRICE [crop] - Market prices',
                'WEATHER [location] - Weather update',
                'PROFILE - View profile',
                'LANG [code] - Change language'
            ],
            'supported_languages': ['en', 'tw', 'ha', 'yo', 'fr'],
            'test_numbers': ['+233XXXXXXXXX', '+234XXXXXXXXX', '+254XXXXXXXXX']
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            message = data.get('message')
            
            if not phone_number or not message:
                return JsonResponse({'error': 'Missing phone_number or message'}, status=400)
            
            # Process test SMS command
            response_message = sms_onboarding_service.process_sms_command(phone_number, message)
            
            return JsonResponse({
                'success': True,
                'phone_number': phone_number,
                'incoming_message': message,
                'response_message': response_message,
                'test_mode': True
            })
            
        except Exception as e:
            logger.error(f"SMS test error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ussd_test_endpoint(request):
    """Test endpoint for USSD functionality"""
    if request.method == 'GET':
        return JsonResponse({
            'service': 'AgriConnect USSD Service',
            'status': 'active',
            'ussd_code': '*123#',
            'menu_structure': {
                '1': 'Chat with AgriBot',
                '2': 'Crop Advisory',
                '3': 'Disease Detection',
                '4': 'Market Prices',
                '5': 'Weather Updates',
                '6': 'My Profile',
                '7': 'Language Settings',
                '0': 'Help & Support'
            },
            'test_numbers': ['+233XXXXXXXXX', '+234XXXXXXXXX', '+254XXXXXXXXX']
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('sessionId', 'test-session')
            service_code = data.get('serviceCode', '*123#')
            phone_number = data.get('phoneNumber')
            text = data.get('text', '')
            
            if not phone_number:
                return JsonResponse({'error': 'Missing phoneNumber'}, status=400)
            
            # Process test USSD request
            response = sms_onboarding_service.ussd_service.handle_ussd_request(
                session_id, service_code, phone_number, text
            )
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'phone_number': phone_number,
                'input_text': text,
                'response': response,
                'test_mode': True
            })
            
        except Exception as e:
            logger.error(f"USSD test error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def farmer_registration_sms(request):
    """Handle SMS-based farmer registration"""
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        name = data.get('name')
        location = data.get('location')
        crops = data.get('crops', [])
        language = data.get('language', 'en')
        
        if not phone_number or not name or not location:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Create or update farmer profile
        user = sms_onboarding_service._get_or_create_user(phone_number)
        
        # Update user profile
        if name:
            user.first_name = name
        if location:
            user.last_name = location  # Store location in last_name field
        user.save()
        
        # Send welcome SMS
        welcome_message = sms_onboarding_service.language_manager.get_message(
            language, 'welcome'
        )
        
        sms_result = sms_onboarding_service.sms_service.send_sms(
            phone_number, welcome_message
        )
        
        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'phone_number': phone_number,
            'name': name,
            'location': location,
            'crops': crops,
            'language': language,
            'welcome_sent': True,
            'sms_result': sms_result
        })
        
    except Exception as e:
        logger.error(f"SMS registration error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def sms_analytics(request):
    """Get SMS usage analytics"""
    try:
        from django.contrib.auth import get_user_model
        from ai.models import AIUsageAnalytics
        from datetime import datetime, timedelta
        
        User = get_user_model()
        
        # Get SMS users (users with phone number usernames)
        sms_users = User.objects.filter(
            username__startswith='+',
            email__endswith='@sms.agriconnect.com'
        )
        
        # Get recent analytics
        last_week = datetime.now() - timedelta(days=7)
        recent_analytics = AIUsageAnalytics.objects.filter(
            user__in=sms_users,
            date__gte=last_week.date()
        )
        
        # Calculate statistics
        total_sms_users = sms_users.count()
        active_sms_users = recent_analytics.values('user').distinct().count()
        total_queries = sum(analytics.daily_queries for analytics in recent_analytics)
        total_tokens = sum(analytics.total_tokens_used for analytics in recent_analytics)
        
        return JsonResponse({
            'sms_analytics': {
                'total_sms_users': total_sms_users,
                'active_sms_users_last_week': active_sms_users,
                'total_queries_last_week': total_queries,
                'total_tokens_used_last_week': total_tokens,
                'average_queries_per_user': total_queries / active_sms_users if active_sms_users > 0 else 0,
                'average_tokens_per_query': total_tokens / total_queries if total_queries > 0 else 0
            },
            'supported_countries': [
                'Ghana (+233)',
                'Nigeria (+234)',
                'Kenya (+254)',
                'South Africa (+27)',
                'Senegal (+221)',
                'Tanzania (+255)',
                'Uganda (+256)',
                'Zambia (+260)',
                'Ivory Coast (+225)',
                'Mali (+223)'
            ],
            'service_status': 'active'
        })
        
    except Exception as e:
        logger.error(f"SMS analytics error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt  
@require_http_methods(["POST"])
def bulk_sms_broadcast(request):
    """Send bulk SMS to farmers"""
    try:
        data = json.loads(request.body)
        message = data.get('message')
        target_country = data.get('target_country')  # e.g., 'ghana', 'nigeria'
        language = data.get('language', 'en')
        
        if not message:
            return JsonResponse({'error': 'Missing message'}, status=400)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get target farmers
        if target_country:
            country_codes = {
                'ghana': '+233',
                'nigeria': '+234',
                'kenya': '+254',
                'south_africa': '+27',
                'senegal': '+221'
            }
            
            country_code = country_codes.get(target_country.lower())
            if country_code:
                target_users = User.objects.filter(
                    username__startswith=country_code,
                    email__endswith='@sms.agriconnect.com'
                )
            else:
                target_users = User.objects.filter(
                    email__endswith='@sms.agriconnect.com'
                )
        else:
            target_users = User.objects.filter(
                email__endswith='@sms.agriconnect.com'
            )
        
        # Send SMS to all target users
        success_count = 0
        error_count = 0
        results = []
        
        for user in target_users[:100]:  # Limit to 100 for safety
            try:
                result = sms_onboarding_service.sms_service.send_sms(
                    user.username, message
                )
                results.append({
                    'phone_number': user.username,
                    'status': 'sent',
                    'result': result
                })
                success_count += 1
            except Exception as e:
                results.append({
                    'phone_number': user.username,
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        return JsonResponse({
            'success': True,
            'message_sent': message,
            'target_country': target_country,
            'language': language,
            'total_targeted': target_users.count(),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Bulk SMS error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
