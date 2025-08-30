"""
AI Services for AgriConnect Platform
Provides AI-powered agricultural intelligence including conversational AI,
crop advisory, disease detection, and market intelligence.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db import models
from django.utils import timezone
from openai import OpenAI
from .models import (
    AIConversation, CropAdvisory, DiseaseDetection, 
    MarketIntelligence, AIUsageAnalytics, AIFeedback
)

logger = logging.getLogger(__name__)


def _update_daily_analytics(user, service_type: str, tokens_used: int):
    """Update daily analytics for a user with race condition protection"""
    from .models import AIUsageAnalytics
    from django.db import transaction, IntegrityError
    
    today = timezone.now().date()
    try:
        # Retry logic to handle potential race conditions
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    # First try to get existing record with lock
                    try:
                        analytics = AIUsageAnalytics.objects.select_for_update().get(
                            user=user,
                            date=today
                        )
                        created = False
                    except AIUsageAnalytics.DoesNotExist:
                        # Create new record if doesn't exist
                        analytics = AIUsageAnalytics.objects.create(
                            user=user,
                            date=today,
                            daily_queries=0,
                            total_tokens_used=0,
                            general_queries=0,
                            crop_advisory_queries=0,
                            disease_detection_queries=0,
                            market_intelligence_queries=0,
                        )
                        created = True
                    
                    # Update counters
                    analytics.daily_queries += 1
                    analytics.total_tokens_used += tokens_used
                    
                    # Update service-specific counters
                    if service_type == 'crop_advisory':
                        analytics.crop_advisory_queries += 1
                    elif service_type == 'disease_detection':
                        analytics.disease_detection_queries += 1
                    elif service_type == 'market_intelligence':
                        analytics.market_intelligence_queries += 1
                    else:
                        analytics.general_queries += 1
                    
                    analytics.save()
                    break  # Success, exit retry loop
                    
            except IntegrityError:
                # Handle duplicate key constraint - retry
                if attempt == max_retries - 1:
                    logger.error(f"Analytics update failed after {max_retries} attempts for user {user.id}")
                    raise
                continue
                
    except Exception as e:
        # Log the error but don't fail the main request
        logger.warning(f"Analytics update failed: {str(e)}")
        pass


class AIServiceManager:
    """Central manager for all AI services"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=settings.OPENAI_TIMEOUT
        )
        self.conversation_service = ConversationalAIService(self.client)
        self.crop_service = CropAdvisoryService(self.client)
        self.disease_service = DiseaseDetectionService(self.client)
        self.market_service = MarketIntelligenceService(self.client)
        self.analytics_service = AIAnalyticsService()
    
    def get_service(self, service_type: str):
        """Get specific AI service"""
        services = {
            'conversation': self.conversation_service,
            'crop': self.crop_service,
            'disease': self.disease_service,
            'market': self.market_service,
            'analytics': self.analytics_service
        }
        return services.get(service_type)
    
    def check_usage_limits(self, user, service_type: str) -> bool:
        """Check if user has exceeded usage limits"""
        daily_limit = settings.AI_USAGE_LIMITS['DAILY_REQUESTS_PER_USER']
        monthly_limit = settings.AI_USAGE_LIMITS['MONTHLY_REQUESTS_PER_USER']          # Check daily usage
        today = timezone.now().date()
        daily_analytics = AIUsageAnalytics.objects.filter(
            user=user,
            date=today
        ).first()
        
        if daily_analytics and daily_analytics.daily_queries >= daily_limit:
            return False
          # Check monthly usage
        month_start = timezone.now().replace(day=1).date()
        
        monthly_usage = AIUsageAnalytics.objects.filter(
            user=user,
            date__gte=month_start
        ).aggregate(
            total=models.Sum('daily_queries')
        )['total'] or 0
        
        return monthly_usage < monthly_limit
    

class ConversationalAIService:
    """AI-powered conversational assistant for farmers"""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.system_prompt = """
        You are AgriBot, an AI assistant for AgriConnect - Africa's premier agricultural commerce platform.
        
        Your role:
        - Help farmers with agricultural questions and advice
        - Provide information about crops, farming techniques, and best practices
                - Assist with market information and trading opportunities
        - Support farmers in multiple African languages when requested
        - Be culturally sensitive and understand African farming contexts
        
        Key capabilities:
        - Crop cultivation guidance
        - Pest and disease identification
        - Market price information
        - Weather-based farming advice
        - Sustainable farming practices
        - Post-harvest handling and storage
        
        Communication style:
        - Friendly, supportive, and encouraging
        - Use simple, clear language
        - Provide practical, actionable advice
        - Acknowledge local farming conditions and challenges
        - Respect traditional knowledge while introducing modern techniques
        """

    def chat(self, user, message: str, language: str = 'en', 
             conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle conversational AI interaction"""
        try:
            # Add language instruction if not English
            language_instruction = ""
            if language != 'en':
                lang_names = {
                    'tw': 'Twi (Akan)',
                    'ha': 'Hausa',
                    'yo': 'Yoruba'
                }
                language_instruction = f"Please respond in {lang_names.get(language, language)}."
            
            # Build conversation context
            messages = [
                {"role": "system", "content": self.system_prompt + " " + language_instruction},
                {"role": "user", "content": message}
            ]
            
            # Get AI response
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
            
            ai_response = response.choices[0].message.content
            
            # Save conversation
            conversation = AIConversation.objects.create(
                user=user,
                conversation_type='general_farming',
                language=language,
                farmer_question=message,
                ai_response=ai_response,
                openai_model_used=settings.OPENAI_MODEL,
                tokens_used=response.usage.total_tokens,
                processing_time_ms=0  # Could be calculated if needed
            )              # Update daily usage analytics
            _update_daily_analytics(
                user=user,
                service_type='general',
                tokens_used=response.usage.total_tokens
            )
            
            return {
                'success': True,
                'response': ai_response,
                'conversation_id': str(conversation.id),
                'language': language,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Conversational AI error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_response': "I'm sorry, I'm having trouble processing your request right now. Please try again later."
            }


class CropAdvisoryService:
    """AI-powered crop advisory and farming guidance"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def get_crop_advice(self, user, crop_type: str, farming_stage: str,
                       location: str, season: str, specific_question: str = None) -> Dict[str, Any]:
        """Get comprehensive crop advisory"""
        try:
            prompt = f"""
            Provide detailed farming advice for {crop_type} cultivation in {location}, Africa.
            
            Current farming stage: {farming_stage}
            Season: {season}
            {f"Specific question: {specific_question}" if specific_question else ""}
            
            Please provide comprehensive advice covering:
            1. Current stage best practices
            2. Recommended fertilizers and nutrients
            3. Irrigation and water management
            4. Pest and disease prevention
            5. Expected timeline for next stages
            6. Yield optimization tips
            7. Common challenges and solutions
            8. Local climate considerations
            
            Format the response as practical, actionable advice suitable for African farmers.
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert agricultural advisor specializing in African farming systems."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=0.3  # Lower temperature for more consistent advice
            )
            
            advice = response.choices[0].message.content
              # Create AI conversation record first
            conversation = AIConversation.objects.create(
                user=user,
                conversation_type='crop_advisory',
                farmer_question=specific_question or f"Crop advice for {crop_type}",
                ai_response=advice,
                farmer_location=location,
                crop_context=crop_type,
                season_context=season,
                tokens_used=response.usage.total_tokens,
                openai_model_used=settings.OPENAI_MODEL
            )
            
            # Save advisory record
            advisory = CropAdvisory.objects.create(
                conversation=conversation,
                farmer_location=location,
                target_season=season,
                recommended_crops=[crop_type],
                confidence_level=85.0  # Placeholder
            )
            
            # Update daily usage analytics
            _update_daily_analytics(
                user=user,
                service_type='crop_advisory',
                tokens_used=response.usage.total_tokens
            )
            
            return {
                'success': True,
                'advice': advice,
                'advisory_id': str(advisory.id),
                'confidence_score': 0.85,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Crop advisory error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class DiseaseDetectionService:
    """AI-powered plant disease detection and treatment recommendations"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def detect_disease(self, user, crop_type: str, symptoms: str,
                      image_url: str = None, location: str = None) -> Dict[str, Any]:
        """Detect plant diseases and provide treatment recommendations"""
        try:
            # Build context based on available information
            if symptoms and image_url:
                prompt = f"""
                Analyze the following plant disease information for {crop_type}:
                
                Symptoms described: {symptoms}
                Location: {location or "Not specified"}
                Image provided: Yes (analyze both symptoms and image)
                
                Please provide:
                1. Most likely disease diagnosis based on symptoms and image
                2. Confidence level (1-10)
                3. Alternative possible diagnoses
                4. Detailed treatment recommendations
                5. Preventive measures
                6. Expected recovery timeline
                7. When to seek professional help
                8. Organic/natural treatment options
                
                Focus on treatments and solutions available to African farmers.
                """
            elif symptoms:
                prompt = f"""
                Analyze the following plant disease symptoms for {crop_type}:
                
                Symptoms: {symptoms}
                Location: {location or "Not specified"}
                
                Please provide:
                1. Most likely disease diagnosis based on symptoms
                2. Confidence level (1-10)
                3. Alternative possible diagnoses
                4. Detailed treatment recommendations
                5. Preventive measures
                6. Expected recovery timeline
                7. When to seek professional help
                8. Organic/natural treatment options
                
                Focus on treatments and solutions available to African farmers.
                """
            elif image_url:
                prompt = f"""
                Analyze the following plant image for disease diagnosis:
                
                Crop type: {crop_type}
                Location: {location or "Not specified"}
                Analysis method: Image-only analysis
                
                Please provide:
                1. Disease diagnosis based on visual symptoms in image
                2. Confidence level (1-10)
                3. Alternative possible diagnoses
                4. Detailed treatment recommendations
                5. Preventive measures
                6. Expected recovery timeline                7. When to seek professional help
                8. Organic/natural treatment options
                
                Focus on treatments and solutions available to African farmers.
                """
            else:
                # This shouldn't happen due to validation in view, but handle gracefully
                prompt = f"""
                Provide general disease prevention and management advice for {crop_type}:
                
                Location: {location or "Not specified"}
                
                Please provide:
                1. Common diseases affecting {crop_type} in African farming
                2. General prevention strategies
                3. Early detection signs to watch for
                4. When to seek professional help
                5. Organic/natural treatment options
                
                Focus on practical advice for African farmers.
                """
            
            messages = [
                {"role": "system", "content": "You are an expert plant pathologist specializing in African crop diseases."},
                {"role": "user", "content": prompt}
            ]
            
            # Add image analysis if provided
            if image_url:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please also analyze this image of the affected plant:"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                })
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=0.2  # Lower temperature for medical-like diagnosis
            )
            
            diagnosis = response.choices[0].message.content
            
            # Create AI conversation record first
            conversation = AIConversation.objects.create(
                user=user,
                conversation_type='disease_detection',
                farmer_question=f"Disease symptoms: {symptoms}",
                ai_response=diagnosis,
                farmer_location=location or "",
                crop_context=crop_type,
                tokens_used=response.usage.total_tokens,
                openai_model_used=settings.OPENAI_MODEL
            )
            
            # Save detection record
            detection = DiseaseDetection.objects.create(
                conversation=conversation,
                crop_type=crop_type,
                farmer_description=symptoms,
                primary_diagnosis=diagnosis[:100] if diagnosis else "",  # Truncate for field limit
                confidence_percentage=80.0,  # Placeholder
                image_analyzed=bool(image_url)
            )
            
            # Update daily usage analytics
            _update_daily_analytics(
                user=user,
                service_type='disease_detection',
                tokens_used=response.usage.total_tokens
            )
            
            return {
                'success': True,
                'diagnosis': diagnosis,
                'detection_id': str(detection.id),
                'confidence_score': 0.8,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Disease detection error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class MarketIntelligenceService:
    """AI-powered market intelligence and price predictions"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def get_market_intelligence(self, user, crop_type: str, location: str,
                               market_type: str = 'local') -> Dict[str, Any]:
        """Get market intelligence and price predictions"""
        try:
            prompt = f"""
            Provide comprehensive market intelligence for {crop_type} in {location}, Africa.
            
            Market scope: {market_type}
            
            Please provide:
            1. Current market price trends
            2. Price predictions for next 3-6 months
            3. Seasonal price patterns
            4. Market demand analysis
            5. Best selling periods
            6. Quality factors affecting prices
            7. Marketing and selling strategies
            8. Export opportunities (if applicable)
            9. Storage and timing recommendations
            10. Market risks and opportunities
            
            Focus on actionable insights for African farmers to maximize their profits.
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert agricultural market analyst specializing in African markets."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=0.3
            )
            
            intelligence = response.choices[0].message.content
              # Create AI conversation record first
            conversation = AIConversation.objects.create(
                user=user,
                conversation_type='market_inquiry',
                farmer_question=f"Market intelligence for {crop_type} in {location}",
                ai_response=intelligence,
                farmer_location=location,
                crop_context=crop_type,
                tokens_used=response.usage.total_tokens,
                openai_model_used=settings.OPENAI_MODEL
            )
            
            # Save intelligence record
            market_intel = MarketIntelligence.objects.create(
                conversation=conversation,
                crop_name=crop_type,
                target_region=location,
                prediction_timeframe='3_months',
                market_trends=[intelligence[:500]] if intelligence else []  # Truncate for field
            )
            
            # Update daily usage analytics
            _update_daily_analytics(
                user=user,
                service_type='market_intelligence',
                tokens_used=response.usage.total_tokens
            )
            
            return {
                'success': True,
                'intelligence': intelligence,
                'intelligence_id': str(market_intel.id),
                'confidence_score': 0.75,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Market intelligence error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class AIAnalyticsService:
    """Analytics and insights for AI usage and performance"""
    
    def get_user_analytics(self, user, days: int = 30) -> Dict[str, Any]:
        """Get user AI usage analytics"""
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            analytics = AIUsageAnalytics.objects.filter(
                user=user,
                date__gte=start_date.date()
            )
            
            # Calculate metrics
            total_requests = analytics.count()
            total_tokens = analytics.aggregate(
                total=models.Sum('total_tokens_used')
            )['total'] or 0
            
            service_breakdown = {}
            for service in ['conversational_ai', 'crop_advisory', 'disease_detection', 'market_intelligence']:
                service_breakdown[service] = analytics.filter(
                    service_type=service
                ).count()
              # Get feedback metrics
            feedback = AIFeedback.objects.filter(
                user=user,
                created_at__gte=start_date
            )
            
            avg_rating = feedback.aggregate(
                avg=models.Avg('rating')
            )['avg'] or 0
            
            return {
                'total_requests': total_requests,
                'total_tokens_used': total_tokens,
                'service_breakdown': service_breakdown,
                'average_rating': round(avg_rating, 2),
                'feedback_count': feedback.count(),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return {
                'error': str(e)
            }
    
    def get_platform_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get platform-wide AI analytics"""
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            analytics = AIUsageAnalytics.objects.filter(
                date__gte=start_date.date()
            )
            
            # Calculate platform metrics
            total_users = analytics.values('user').distinct().count()
            total_requests = analytics.count()
            total_tokens = analytics.aggregate(
                total=models.Sum('total_tokens_used')
            )['total'] or 0
              # Service popularity
            service_stats = {
                'crop_advisory': {
                    'requests': analytics.aggregate(total=models.Sum('crop_advisory_queries'))['total'] or 0,
                    'users': analytics.filter(crop_advisory_queries__gt=0).count()
                },
                'disease_detection': {
                    'requests': analytics.aggregate(total=models.Sum('disease_detection_queries'))['total'] or 0,
                    'users': analytics.filter(disease_detection_queries__gt=0).count()
                },
                'market_intelligence': {
                    'requests': analytics.aggregate(total=models.Sum('market_intelligence_queries'))['total'] or 0,
                    'users': analytics.filter(market_intelligence_queries__gt=0).count()
                },
                'general': {
                    'requests': analytics.aggregate(total=models.Sum('general_queries'))['total'] or 0,
                    'users': analytics.filter(general_queries__gt=0).count()
                }
            }
            
            return {
                'total_users': total_users,
                'total_requests': total_requests,
                'total_tokens_used': total_tokens,
                'service_statistics': service_stats,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Platform analytics error: {str(e)}")
            return {
                'error': str(e)
            }


# Initialize global AI service manager
ai_service_manager = AIServiceManager()
