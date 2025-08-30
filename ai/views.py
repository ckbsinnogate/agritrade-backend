"""
AI Views for AgriConnect Platform
API endpoints for AI-powered agricultural intelligence
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
import json
import logging

from .models import (
    AIConversation, CropAdvisory, DiseaseDetection, 
    MarketIntelligence, AIUsageAnalytics, AIFeedback
)
from .services import ai_service_manager
from .serializers import (
    AIConversationSerializer, CropAdvisorySerializer,
    DiseaseDetectionSerializer, MarketIntelligenceSerializer,
    AIFeedbackSerializer
)

logger = logging.getLogger(__name__)


class AIConversationView(APIView):
    """Handle conversational AI interactions"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Send message to AI assistant"""
        try:
            # Check usage limits
            if not ai_service_manager.check_usage_limits(request.user, 'conversational_ai'):
                return Response({
                    'success': False,
                    'error': 'Daily usage limit exceeded'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Get request data
            message = request.data.get('message', '').strip()
            language = request.data.get('language', 'en')
            conversation_id = request.data.get('conversation_id')
            
            if not message:
                return Response({
                    'success': False,
                    'error': 'Message is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get conversational AI service
            conversation_service = ai_service_manager.get_service('conversation')
            
            # Process conversation
            result = conversation_service.chat(
                user=request.user,
                message=message,
                language=language,
                conversation_id=conversation_id
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Conversation API error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get conversation history"""
        try:
            conversations = AIConversation.objects.filter(
                user=request.user
            ).order_by('-updated_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(conversations, request)
            
            serializer = AIConversationSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            logger.error(f"Conversation history error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CropAdvisoryView(APIView):
    """Handle crop advisory requests"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Get crop advisory"""
        try:
            # Check usage limits
            if not ai_service_manager.check_usage_limits(request.user, 'crop_advisory'):
                return Response({
                    'success': False,
                    'error': 'Daily usage limit exceeded'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Get request data
            crop_type = request.data.get('crop_type', '').strip()
            farming_stage = request.data.get('farming_stage', '').strip()
            location = request.data.get('location', '').strip()
            season = request.data.get('season', '').strip()
            specific_question = request.data.get('specific_question', '').strip()
            
            if not all([crop_type, farming_stage, location, season]):
                return Response({
                    'success': False,
                    'error': 'crop_type, farming_stage, location, and season are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get crop advisory service
            crop_service = ai_service_manager.get_service('crop')
            
            # Get crop advice
            result = crop_service.get_crop_advice(
                user=request.user,
                crop_type=crop_type,
                farming_stage=farming_stage,
                location=location,
                season=season,
                specific_question=specific_question
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Crop advisory API error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get crop advisory history"""
        try:
            advisories = CropAdvisory.objects.filter(
                user=request.user
            ).order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(advisories, request)
            
            serializer = CropAdvisorySerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            logger.error(f"Crop advisory history error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiseaseDetectionView(APIView):
    """Handle disease detection requests"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Detect plant diseases"""
        try:
            # Log the incoming request data for debugging
            logger.info(f"Disease detection request from user {request.user}: {request.data}")
            
            # Check usage limits
            if not ai_service_manager.check_usage_limits(request.user, 'disease_detection'):
                return Response({
                    'success': False,
                    'error': 'Daily usage limit exceeded'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
              # Handle both JSON and FormData requests
            if hasattr(request, 'FILES') and 'image' in request.FILES:
                # Handle file upload (FormData)
                crop_type = request.data.get('crop_type', '').strip()
                symptoms = request.data.get('symptoms', '').strip()
                location = request.data.get('location', '').strip()
                
                # Process the uploaded image file
                image_file = request.FILES['image']
                
                # Convert image to base64 for AI processing
                import base64
                import io
                from PIL import Image
                
                try:
                    # Read and convert image
                    image_data = image_file.read()
                    
                    # Validate image data
                    if len(image_data) == 0:
                        logger.error("Uploaded image file is empty")
                        return Response({
                            'success': False,
                            'error': 'Uploaded image file is empty'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Convert to base64
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    image_url = f"data:image/jpeg;base64,{image_base64}"
                    
                    # If no symptoms provided, create a descriptive default
                    if not symptoms:
                        symptoms = f"Plant disease analysis from uploaded image for {crop_type} crop"
                    
                    logger.info(f"Image file processed - size: {len(image_data)} bytes, crop_type: '{crop_type}'")
                    
                except Exception as img_error:
                    logger.error(f"Image processing error: {img_error}")
                    return Response({
                        'success': False,
                        'error': 'Failed to process uploaded image'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            else:
                # Handle JSON data (original functionality)
                crop_type = request.data.get('crop_type', '').strip()
                symptoms = request.data.get('symptoms', '').strip()
                image_url = request.data.get('image_url', '').strip()
                location = request.data.get('location', '').strip()
            
            logger.info(f"Parsed data - crop_type: '{crop_type}', symptoms: '{symptoms}', image_url: {'[base64_image]' if image_url.startswith('data:') else image_url}, location: '{location}'")
              # Crop type is required and must be valid
            if not crop_type:
                logger.warning("Disease detection: crop_type is missing")
                return Response({
                    'success': False,
                    'error': 'crop_type is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for invalid crop types and provide helpful suggestions
            if crop_type.lower() in ['unknown', 'select', 'default', '']:
                logger.warning(f"Disease detection: invalid crop_type '{crop_type}'")
                return Response({
                    'success': False,
                    'error': 'Please select a valid crop type (e.g., tomato, rice, maize, cassava, cocoa)',
                    'code': 'invalid_crop_type',
                    'suggested_crops': ['tomato', 'rice', 'maize', 'cassava', 'cocoa', 'yam', 'plantain']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Either symptoms or image_url must be provided for meaningful detection
            if not symptoms and not image_url:
                logger.warning("Disease detection: both symptoms and image_url are missing")
                return Response({
                    'success': False,
                    'error': 'Either symptoms description or image_url must be provided for disease detection'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get disease detection service
            disease_service = ai_service_manager.get_service('disease')
            
            # Detect disease
            result = disease_service.detect_disease(
                user=request.user,
                crop_type=crop_type,
                symptoms=symptoms,
                image_url=image_url,
                location=location
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Disease detection API error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get disease detection history"""
        try:
            detections = DiseaseDetection.objects.filter(
                user=request.user
            ).order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(detections, request)
            
            serializer = DiseaseDetectionSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            logger.error(f"Disease detection history error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarketIntelligenceView(APIView):
    """Handle market intelligence requests"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Get market intelligence"""
        try:
            # Check usage limits
            if not ai_service_manager.check_usage_limits(request.user, 'market_intelligence'):
                return Response({
                    'success': False,
                    'error': 'Daily usage limit exceeded'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Get request data
            crop_type = request.data.get('crop_type', '').strip()
            location = request.data.get('location', '').strip()
            market_type = request.data.get('market_type', 'local').strip()
            
            if not all([crop_type, location]):
                return Response({
                    'success': False,
                    'error': 'crop_type and location are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get market intelligence service
            market_service = ai_service_manager.get_service('market')
            
            # Get market intelligence
            result = market_service.get_market_intelligence(
                user=request.user,
                crop_type=crop_type,
                location=location,
                market_type=market_type
            )
            
            if result['success']:
                                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Market intelligence API error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get market intelligence history"""
        try:
            intelligence = MarketIntelligence.objects.filter(
                conversation__user=request.user
            ).order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(intelligence, request)
            
            serializer = MarketIntelligenceSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            logger.error(f"Market intelligence history error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIFeedbackView(APIView):
    """Handle AI feedback collection"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Submit feedback for AI service"""
        try:
            # Get request data
            service_type = request.data.get('service_type', '').strip()
            service_id = request.data.get('service_id', '').strip()
            rating = request.data.get('rating')
            feedback_text = request.data.get('feedback_text', '').strip()
            
            if not all([service_type, service_id, rating]):
                return Response({
                    'success': False,
                    'error': 'service_type, service_id, and rating are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate rating
            try:
                rating = int(rating)
                if not (1 <= rating <= 5):
                    raise ValueError()
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'Rating must be an integer between 1 and 5'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create feedback
            feedback = AIFeedback.objects.create(
                user=request.user,
                service_type=service_type,
                service_id=service_id,
                rating=rating,
                feedback_text=feedback_text
            )
            
            serializer = AIFeedbackSerializer(feedback)
            return Response({
                'success': True,
                'feedback': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"AI feedback error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIAnalyticsView(APIView):
    """Handle AI analytics and insights"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user AI analytics"""
        try:
            days = int(request.GET.get('days', 30))
            
            # Get analytics service
            analytics_service = ai_service_manager.get_service('analytics')
            
            # Get user analytics
            analytics = analytics_service.get_user_analytics(
                user=request.user,
                days=days
            )
            
            return Response({
                'success': True,
                'analytics': analytics
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"AI analytics error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIHealthCheckView(APIView):
    """Health check for AI services"""
    def get(self, request):
        """Check AI service health"""
        try:
            # Test OpenAI connection
            test_response = ai_service_manager.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, this is a health check."}
                ],
                max_tokens=50
            )
            
            return Response({
                'success': True,
                'status': 'healthy',
                'model': settings.OPENAI_MODEL,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"AI health check error: {str(e)}")
            return Response({
                'success': False,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Web views for admin interface
@method_decorator(login_required, name='dispatch')
class AIAdminDashboardView(ListView):
    """Admin dashboard for AI services"""
    template_name = 'ai/admin_dashboard.html'
    context_object_name = 'analytics'
    
    def get_queryset(self):
        # Get platform analytics
        analytics_service = ai_service_manager.get_service('analytics')
        return analytics_service.get_platform_analytics(days=30)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add recent activities
        context['recent_conversations'] = AIConversation.objects.order_by('-updated_at')[:10]
        context['recent_advisories'] = CropAdvisory.objects.order_by('-created_at')[:10]
        context['recent_detections'] = DiseaseDetection.objects.order_by('-created_at')[:10]
        context['recent_feedback'] = AIFeedback.objects.order_by('-created_at')[:10]
        
        return context


@method_decorator(login_required, name='dispatch')
class AIConversationListView(ListView):
    """List all AI conversations"""
    model = AIConversation
    template_name = 'ai/conversation_list.html'
    context_object_name = 'conversations'
    paginate_by = 20
    
    def get_queryset(self):
        return AIConversation.objects.select_related('user').order_by('-updated_at')


@method_decorator(login_required, name='dispatch')
class CropAdvisoryListView(ListView):
    """List all crop advisories"""
    model = CropAdvisory
    template_name = 'ai/crop_advisory_list.html'
    context_object_name = 'advisories'
    paginate_by = 20
    
    def get_queryset(self):
        return CropAdvisory.objects.select_related('user').order_by('-created_at')
