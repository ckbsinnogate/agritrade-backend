"""
AgriConnect OpenRouter AI Views
Django views for AI-powered agricultural intelligence
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import base64
import logging
from datetime import datetime

from .openrouter_django_integration import openrouter_ai

logger = logging.getLogger(__name__)

class AgriAIView(View):
    """Base view for AgriConnect AI services"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class CropAnalysisView(AgriAIView):
    """AI-powered crop suitability analysis"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            location = data.get('location', '')
            soil_type = data.get('soil_type', '')
            crop = data.get('crop', '')
            season = data.get('season', 'major_season')
            
            if not all([location, soil_type, crop]):
                return JsonResponse({
                    'error': 'Missing required fields: location, soil_type, crop'
                }, status=400)
            
            # Get AI analysis
            analysis = openrouter_ai.analyze_crop_suitability(
                location=location,
                soil_type=soil_type,
                crop=crop,
                season=season
            )
            
            if 'error' in analysis:
                return JsonResponse({
                    'error': 'AI analysis failed',
                    'details': analysis['error']
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Crop analysis error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DiseaseDetectionView(AgriAIView):
    """AI-powered plant disease detection"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            image_data = data.get('image', '')
            crop_type = data.get('crop_type', '')
            symptoms = data.get('symptoms', '')
            
            if not image_data or not crop_type:
                return JsonResponse({
                    'error': 'Missing required fields: image, crop_type'
                }, status=400)
            
            # Extract base64 image data
            if ',' in image_data:
                image_base64 = image_data.split(',')[1]
            else:
                image_base64 = image_data
            
            # Get AI disease detection
            detection = openrouter_ai.detect_plant_disease(
                image_base64=image_base64,
                crop_type=crop_type,
                symptoms=symptoms
            )
            
            if 'error' in detection:
                return JsonResponse({
                    'error': 'Disease detection failed',
                    'details': detection['error']
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'detection': detection,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Disease detection error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class MarketPredictionView(AgriAIView):
    """AI-powered market price prediction"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            crop = data.get('crop', '')
            region = data.get('region', '')
            season = data.get('season', 'major_season')
            quantity = data.get('quantity', 1.0)
            
            if not all([crop, region]):
                return JsonResponse({
                    'error': 'Missing required fields: crop, region'
                }, status=400)
            
            # Get AI market prediction
            prediction = openrouter_ai.predict_market_prices(
                crop=crop,
                region=region,
                season=season,
                quantity=float(quantity)
            )
            
            if 'error' in prediction:
                return JsonResponse({
                    'error': 'Market prediction failed',
                    'details': prediction['error']
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'prediction': prediction,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity value'}, status=400)
        except Exception as e:
            logger.error(f"Market prediction error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class WeatherAnalysisView(AgriAIView):
    """AI-powered weather impact analysis"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            location = data.get('location', '')
            weather_data = data.get('weather_data', {})
            crop = data.get('crop', '')
            growth_stage = data.get('growth_stage', 'vegetative')
            
            if not all([location, weather_data, crop]):
                return JsonResponse({
                    'error': 'Missing required fields: location, weather_data, crop'
                }, status=400)
            
            # Get AI weather analysis
            analysis = openrouter_ai.analyze_weather_impact(
                location=location,
                weather_data=weather_data,
                crop=crop,
                growth_stage=growth_stage
            )
            
            if 'error' in analysis:
                return JsonResponse({
                    'error': 'Weather analysis failed',
                    'details': analysis['error']
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Weather analysis error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class YieldPredictionView(AgriAIView):
    """AI-powered crop yield prediction"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            farm_data = data.get('farm_data', {})
            historical_data = data.get('historical_data', [])
            
            if not farm_data:
                return JsonResponse({
                    'error': 'Missing required field: farm_data'
                }, status=400)
            
            # Get AI yield prediction
            prediction = openrouter_ai.predict_crop_yield(
                farm_data=farm_data,
                historical_data=historical_data
            )
            
            if 'error' in prediction:
                return JsonResponse({
                    'error': 'Yield prediction failed',
                    'details': prediction['error']
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'prediction': prediction,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Yield prediction error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class FarmingAdviceView(AgriAIView):
    """AI-powered farming advice assistant"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            question = data.get('question', '')
            farmer_context = data.get('farmer_context', {})
            language = data.get('language', 'English')
            
            if not question:
                return JsonResponse({
                    'error': 'Missing required field: question'
                }, status=400)
            
            # Get AI farming advice
            advice = openrouter_ai.get_farming_advice(
                question=question,
                farmer_context=farmer_context,
                language=language
            )
            
            if 'error' in advice:
                return JsonResponse({
                    'error': 'Farming advice failed',
                    'details': advice['error']
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'advice': advice,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Farming advice error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AIStatusView(AgriAIView):
    """Check AI service status"""
    
    def get(self, request):
        try:
            status = openrouter_ai.get_api_status()
            
            return JsonResponse({
                'success': True,
                'status': status,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"AI status check error: {str(e)}")
            return JsonResponse({
                'error': 'Status check failed',
                'details': str(e)
            }, status=500)

# URL patterns for inclusion in main urls.py
urlpatterns = [
    # AI Service endpoints
    ('ai/crop-analysis/', CropAnalysisView.as_view(), 'ai_crop_analysis'),
    ('ai/disease-detection/', DiseaseDetectionView.as_view(), 'ai_disease_detection'),
    ('ai/market-prediction/', MarketPredictionView.as_view(), 'ai_market_prediction'),
    ('ai/weather-analysis/', WeatherAnalysisView.as_view(), 'ai_weather_analysis'),
    ('ai/yield-prediction/', YieldPredictionView.as_view(), 'ai_yield_prediction'),
    ('ai/farming-advice/', FarmingAdviceView.as_view(), 'ai_farming_advice'),
    ('ai/status/', AIStatusView.as_view(), 'ai_status'),
]
