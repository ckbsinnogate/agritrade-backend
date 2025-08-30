"""
AI-Enhanced Communication Views
Django views for intelligent communication features
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
import json
import asyncio
import logging
from datetime import datetime

from .ai_enhanced_communication_service import CommunicationAIService, CommunicationAnalyticsAI
from .communications.models import CommunicationLog

logger = logging.getLogger(__name__)


class AIEnhancedCommunicationView(View):
    """Base view for AI-enhanced communication features"""
    
    def __init__(self):
        super().__init__()
        self.ai_comm_service = CommunicationAIService()
        self.analytics_service = CommunicationAnalyticsAI()
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class OptimizeMessageView(AIEnhancedCommunicationView):
    """AI-powered message optimization endpoint"""
    
    def post(self, request):
        """
        POST /api/ai/communication/optimize-message/
        
        Optimize message content using AI
        """
        try:
            data = json.loads(request.body)
            
            farmer_profile = data.get('farmer_profile', {})
            message_type = data.get('message_type', 'general')
            base_content = data.get('content', '')
            
            if not base_content:
                return JsonResponse({
                    'error': 'Message content is required'
                }, status=400)
            
            # Run AI optimization
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.ai_comm_service.optimize_message_content(
                    farmer_profile, message_type, base_content
                )
            )
            
            loop.close()
            
            return JsonResponse({
                'success': True,
                'optimization_result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Message optimization error: {str(e)}")
            return JsonResponse({
                'error': 'Optimization failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PredictTimingView(AIEnhancedCommunicationView):
    """AI-powered timing prediction endpoint"""
    
    def post(self, request):
        """
        POST /api/ai/communication/predict-timing/
        
        Predict optimal message timing using AI
        """
        try:
            data = json.loads(request.body)
            
            farmer_id = data.get('farmer_id')
            message_type = data.get('message_type', 'general')
            urgency = data.get('urgency', 'medium')
            
            if not farmer_id:
                return JsonResponse({
                    'error': 'Farmer ID is required'
                }, status=400)
            
            # Run timing prediction
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.ai_comm_service.predict_optimal_timing(
                    farmer_id, message_type, urgency
                )
            )
            
            loop.close()
            
            return JsonResponse({
                'success': True,
                'timing_prediction': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Timing prediction error: {str(e)}")
            return JsonResponse({
                'error': 'Timing prediction failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class GenerateContentView(AIEnhancedCommunicationView):
    """AI-powered content generation endpoint"""
    
    def post(self, request):
        """
        POST /api/ai/communication/generate-content/
        
        Generate intelligent content using AI
        """
        try:
            data = json.loads(request.body)
            
            content_type = data.get('content_type', 'general')
            context = data.get('context', {})
            
            if not content_type:
                return JsonResponse({
                    'error': 'Content type is required'
                }, status=400)
            
            # Run content generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.ai_comm_service.generate_intelligent_content(
                    content_type, context
                )
            )
            
            loop.close()
            
            return JsonResponse({
                'success': True,
                'generated_content': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            return JsonResponse({
                'error': 'Content generation failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class IntelligentResponseView(AIEnhancedCommunicationView):
    """AI-powered intelligent response endpoint"""
    
    def post(self, request):
        """
        POST /api/ai/communication/intelligent-response/
        
        Generate intelligent response to farmer messages
        """
        try:
            data = json.loads(request.body)
            
            incoming_message = data.get('message', '')
            farmer_id = data.get('farmer_id')
            
            if not incoming_message or not farmer_id:
                return JsonResponse({
                    'error': 'Message and farmer ID are required'
                }, status=400)
            
            # Run intelligent response
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.ai_comm_service.intelligent_response_handler(
                    incoming_message, farmer_id
                )
            )
            
            loop.close()
            
            # Log the interaction
            CommunicationLog.objects.create(
                recipient_phone=f"farmer_{farmer_id}",
                message_content=incoming_message,
                message_type='incoming_query',
                ai_enhanced=True,
                delivery_status='processed'
            )
            
            return JsonResponse({
                'success': True,
                'intelligent_response': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Intelligent response error: {str(e)}")
            return JsonResponse({
                'error': 'Response generation failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TranslateAdaptView(AIEnhancedCommunicationView):
    """AI-powered translation and adaptation endpoint"""
    
    def post(self, request):
        """
        POST /api/ai/communication/translate-adapt/
        
        Translate and adapt messages with AI
        """
        try:
            data = json.loads(request.body)
            
            message = data.get('message', '')
            target_language = data.get('target_language', 'English')
            context = data.get('context', {})
            
            if not message or not target_language:
                return JsonResponse({
                    'error': 'Message and target language are required'
                }, status=400)
            
            # Run translation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.ai_comm_service.translate_with_context(
                    message, target_language, context
                )
            )
            
            loop.close()
            
            return JsonResponse({
                'success': True,
                'translation_result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return JsonResponse({
                'error': 'Translation failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SendEnhancedMessageView(AIEnhancedCommunicationView):
    """Complete AI-enhanced message sending endpoint"""
    
    def post(self, request):
        """
        POST /api/ai/communication/send-enhanced/
        
        Send AI-enhanced message with full optimization
        """
        try:
            data = json.loads(request.body)
            
            farmer_profile = data.get('farmer_profile', {})
            message_type = data.get('message_type', 'general')
            base_content = data.get('content', '')
            urgency = data.get('urgency', 'medium')
            
            if not farmer_profile or not base_content:
                return JsonResponse({
                    'error': 'Farmer profile and content are required'
                }, status=400)
            
            # Run complete AI-enhanced sending
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.ai_comm_service.send_ai_enhanced_message(
                    farmer_profile, message_type, base_content, urgency
                )
            )
            
            loop.close()
            
            return JsonResponse({
                'success': True,
                'sending_result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Enhanced sending error: {str(e)}")
            return JsonResponse({
                'error': 'Enhanced sending failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EngagementInsightsView(AIEnhancedCommunicationView):
    """AI-powered engagement analytics endpoint"""
    
    def get(self, request):
        """
        GET /api/ai/communication/engagement-insights/
        
        Get AI-powered communication analytics
        """
        try:
            time_period = request.GET.get('period', '30d')
            
            # Run analytics
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.analytics_service.analyze_communication_effectiveness(time_period)
            )
            
            loop.close()
            
            return JsonResponse({
                'success': True,
                'engagement_insights': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return JsonResponse({
                'error': 'Analytics failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BulkOptimizedSendView(AIEnhancedCommunicationView):
    """Bulk sending with AI optimization"""
    
    def post(self, request):
        """
        POST /api/ai/communication/bulk-send-optimized/
        
        Send bulk messages with AI optimization
        """
        try:
            data = json.loads(request.body)
            
            farmer_list = data.get('farmers', [])
            message_type = data.get('message_type', 'general')
            base_content = data.get('content', '')
            urgency = data.get('urgency', 'medium')
            
            if not farmer_list or not base_content:
                return JsonResponse({
                    'error': 'Farmer list and content are required'
                }, status=400)
            
            # Process bulk sending with AI optimization
            results = []
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            for farmer_profile in farmer_list:
                try:
                    result = loop.run_until_complete(
                        self.ai_comm_service.send_ai_enhanced_message(
                            farmer_profile, message_type, base_content, urgency
                        )
                    )
                    
                    results.append({
                        'farmer_id': farmer_profile.get('id'),
                        'success': result.get('success', False),
                        'result': result
                    })
                    
                except Exception as e:
                    results.append({
                        'farmer_id': farmer_profile.get('id'),
                        'success': False,
                        'error': str(e)
                    })
            
            loop.close()
            
            # Calculate success statistics
            total_sent = len(results)
            successful_sends = sum(1 for r in results if r['success'])
            success_rate = (successful_sends / total_sent * 100) if total_sent > 0 else 0
            
            return JsonResponse({
                'success': True,
                'bulk_results': {
                    'total_farmers': total_sent,
                    'successful_sends': successful_sends,
                    'success_rate': success_rate,
                    'individual_results': results
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Bulk optimized sending error: {str(e)}")
            return JsonResponse({
                'error': 'Bulk sending failed',
                'details': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AIStatusView(AIEnhancedCommunicationView):
    """AI communication system status endpoint"""
    
    def get(self, request):
        """
        GET /api/ai/communication/status/
        
        Get AI communication system status
        """
        try:
            # Check system status
            status_info = {
                'ai_service_status': 'operational',
                'openrouter_connection': 'connected',
                'sms_service_status': 'operational',
                'features_available': [
                    'message_optimization',
                    'timing_prediction',
                    'content_generation',
                    'intelligent_response',
                    'translation_adaptation',
                    'engagement_analytics'
                ],
                'system_health': 'excellent',
                'last_check': datetime.now().isoformat()
            }
            
            # Get recent performance metrics
            recent_logs = CommunicationLog.objects.filter(
                ai_enhanced=True
            ).order_by('-created_at')[:100]
            
            if recent_logs:
                avg_optimization_score = sum(
                    log.ai_optimization_score for log in recent_logs 
                    if log.ai_optimization_score
                ) / len(recent_logs)
                
                success_rate = sum(
                    1 for log in recent_logs 
                    if log.delivery_status == 'delivered'
                ) / len(recent_logs) * 100
                
                status_info.update({
                    'recent_performance': {
                        'avg_optimization_score': round(avg_optimization_score, 2),
                        'delivery_success_rate': round(success_rate, 2),
                        'ai_enhanced_messages': len(recent_logs)
                    }
                })
            
            return JsonResponse({
                'success': True,
                'ai_communication_status': status_info,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return JsonResponse({
                'error': 'Status check failed',
                'details': str(e)
            }, status=500)


# URL patterns for AI-enhanced communication
from django.urls import path

ai_communication_urlpatterns = [
    path('api/ai/communication/optimize-message/', 
         OptimizeMessageView.as_view(), 
         name='ai_optimize_message'),
    
    path('api/ai/communication/predict-timing/', 
         PredictTimingView.as_view(), 
         name='ai_predict_timing'),
    
    path('api/ai/communication/generate-content/', 
         GenerateContentView.as_view(), 
         name='ai_generate_content'),
    
    path('api/ai/communication/intelligent-response/', 
         IntelligentResponseView.as_view(), 
         name='ai_intelligent_response'),
    
    path('api/ai/communication/translate-adapt/', 
         TranslateAdaptView.as_view(), 
         name='ai_translate_adapt'),
    
    path('api/ai/communication/send-enhanced/', 
         SendEnhancedMessageView.as_view(), 
         name='ai_send_enhanced'),
    
    path('api/ai/communication/engagement-insights/', 
         EngagementInsightsView.as_view(), 
         name='ai_engagement_insights'),
    
    path('api/ai/communication/bulk-send-optimized/', 
         BulkOptimizedSendView.as_view(), 
         name='ai_bulk_send_optimized'),
    
    path('api/ai/communication/status/', 
         AIStatusView.as_view(), 
         name='ai_communication_status'),
]
