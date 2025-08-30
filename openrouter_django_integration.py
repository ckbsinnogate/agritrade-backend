"""
AgriConnect OpenRouter AI Integration - Django Synchronous Version
Comprehensive AI-powered agricultural intelligence for Ghana farmers

This module provides synchronous Django-compatible AI services using OpenRouter API
with multiple AI models for enhanced agricultural decision-making.
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterDjangoIntegration:
    """
    Synchronous Django-compatible OpenRouter AI Integration
    Provides AI-powered agricultural intelligence services
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agriconnect-ghana.com",
            "X-Title": "AgriConnect Ghana - AI Agricultural Platform"
        }
        
        # AI Models configuration
        self.models = {
            'crop_analysis': 'anthropic/claude-3.5-sonnet:beta',
            'disease_detection': 'openai/gpt-4-vision-preview',
            'market_prediction': 'google/gemini-pro-1.5',
            'weather_analysis': 'meta-llama/llama-3.2-90b-vision-instruct',
            'general_farming': 'anthropic/claude-3-haiku',
            'yield_prediction': 'openai/gpt-4-turbo'
        }
        
        # Ghana-specific agricultural context
        self.ghana_context = {
            'climate_zones': ['Forest', 'Coastal Savanna', 'Guinea Savanna', 'Sudan Savanna'],
            'major_crops': ['Cocoa', 'Maize', 'Rice', 'Cassava', 'Yam', 'Plantain', 'Tomato', 'Pepper'],
            'seasons': {
                'major_season': 'April-July',
                'minor_season': 'September-December',
                'harmattan': 'December-February'
            },
            'common_diseases': [
                'Black pod disease (Cocoa)', 'Maize streak virus', 'Cassava mosaic disease',
                'Rice blast', 'Tomato bacterial wilt', 'Yam anthracnose'
            ],
            'regions': [
                'Greater Accra', 'Ashanti', 'Western', 'Central', 'Eastern', 'Volta',
                'Northern', 'Upper East', 'Upper West', 'Brong-Ahafo'
            ]
        }

    def _make_request(self, model: str, messages: List[Dict], max_tokens: int = 1000) -> Dict:
        """Make synchronous request to OpenRouter API"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {"error": f"API request failed: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}

    def analyze_crop_suitability(self, location: str, soil_type: str, crop: str, season: str) -> Dict:
        """
        Analyze crop suitability for specific Ghana location and conditions
        """
        cache_key = f"crop_analysis_{location}_{soil_type}_{crop}_{season}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        messages = [
            {
                "role": "system",
                "content": f"""You are an expert agricultural advisor specializing in Ghana's farming conditions. 
                Provide detailed crop suitability analysis considering Ghana's climate zones: {', '.join(self.ghana_context['climate_zones'])}.
                Focus on practical, actionable advice for local farmers."""
            },
            {
                "role": "user",
                "content": f"""
                Analyze the suitability of growing {crop} in {location}, Ghana with {soil_type} soil during {season} season.
                
                Consider:
                1. Climate compatibility with Ghana's {season} season conditions
                2. Soil type suitability for {crop}
                3. Regional agricultural practices in {location}
                4. Expected yield potential
                5. Potential challenges and mitigation strategies
                6. Best planting and harvesting times
                7. Market demand and pricing trends
                
                Provide response in JSON format with scores (1-10) and detailed recommendations.
                """
            }
        ]
        
        result = self._make_request(self.models['crop_analysis'], messages, 1500)
        
        if 'error' not in result:
            # Parse and structure the response
            try:
                content = result['choices'][0]['message']['content']
                analysis = {
                    'location': location,
                    'crop': crop,
                    'soil_type': soil_type,
                    'season': season,
                    'analysis': content,
                    'timestamp': timezone.now().isoformat(),
                    'model_used': self.models['crop_analysis']
                }
                
                # Cache for 6 hours
                cache.set(cache_key, analysis, 21600)
                return analysis
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing crop analysis response: {e}")
                return {"error": "Failed to parse AI response"}
        
        return result

    def detect_plant_disease(self, image_base64: str, crop_type: str, symptoms: str = "") -> Dict:
        """
        Detect plant diseases from image using AI vision models
        """
        messages = [
            {
                "role": "system",
                "content": f"""You are a plant pathology expert specializing in diseases common to Ghana agriculture.
                Focus on diseases affecting: {', '.join(self.ghana_context['major_crops'])}.
                Common diseases in Ghana: {', '.join(self.ghana_context['common_diseases'])}."""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        Analyze this image of a {crop_type} plant for disease detection.
                        Additional symptoms reported: {symptoms}
                        
                        Provide:
                        1. Disease identification with confidence level
                        2. Severity assessment (mild/moderate/severe)
                        3. Treatment recommendations available in Ghana
                        4. Prevention strategies
                        5. Expected recovery time
                        6. Risk of spread to other plants
                        
                        Format response as JSON with clear diagnosis and actionable advice.
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        result = self._make_request(self.models['disease_detection'], messages, 2000)
        
        if 'error' not in result:
            try:
                content = result['choices'][0]['message']['content']
                detection = {
                    'crop_type': crop_type,
                    'symptoms': symptoms,
                    'diagnosis': content,
                    'timestamp': timezone.now().isoformat(),
                    'model_used': self.models['disease_detection']
                }
                return detection
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing disease detection response: {e}")
                return {"error": "Failed to parse AI response"}
        
        return result

    def predict_market_prices(self, crop: str, region: str, season: str, quantity: float) -> Dict:
        """
        Predict market prices for crops in Ghana markets
        """
        cache_key = f"market_prediction_{crop}_{region}_{season}_{quantity}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        messages = [
            {
                "role": "system",
                "content": f"""You are a Ghana agricultural market analyst with deep knowledge of local market dynamics.
                Key markets: Techiman, Kumasi Central, Agbogbloshie, Tamale, Cape Coast.
                Major regions: {', '.join(self.ghana_context['regions'])}."""
            },
            {
                "role": "user",
                "content": f"""
                Predict market prices for {quantity} tons of {crop} in {region}, Ghana during {season} season.
                
                Analysis should include:
                1. Current market trends for {crop}
                2. Seasonal price variations in Ghana
                3. Supply and demand factors
                4. Regional price differences
                5. Quality grade impact on pricing
                6. Best selling strategies and timing
                7. Transportation and storage considerations
                8. Price forecast for next 3-6 months
                
                Provide detailed market analysis with price ranges in Ghana Cedis (GHS).
                """
            }
        ]
        
        result = self._make_request(self.models['market_prediction'], messages, 1500)
        
        if 'error' not in result:
            try:
                content = result['choices'][0]['message']['content']
                prediction = {
                    'crop': crop,
                    'region': region,
                    'season': season,
                    'quantity': quantity,
                    'analysis': content,
                    'timestamp': timezone.now().isoformat(),
                    'model_used': self.models['market_prediction']
                }
                
                # Cache for 4 hours
                cache.set(cache_key, prediction, 14400)
                return prediction
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing market prediction response: {e}")
                return {"error": "Failed to parse AI response"}
        
        return result

    def analyze_weather_impact(self, location: str, weather_data: Dict, crop: str, growth_stage: str) -> Dict:
        """
        Analyze weather impact on crop growth and provide recommendations
        """
        messages = [
            {
                "role": "system",
                "content": f"""You are a climatology expert specializing in Ghana's agricultural weather patterns.
                Ghana seasons: {self.ghana_context['seasons']}
                Climate zones: {', '.join(self.ghana_context['climate_zones'])}."""
            },
            {
                "role": "user",
                "content": f"""
                Analyze weather impact on {crop} at {growth_stage} growth stage in {location}, Ghana.
                
                Weather data: {json.dumps(weather_data, indent=2)}
                
                Provide analysis on:
                1. Weather suitability for current growth stage
                2. Risk assessment (drought, flooding, wind damage)
                3. Irrigation recommendations
                4. Pest and disease risk due to weather
                5. Harvest timing adjustments
                6. Protective measures needed
                7. Expected yield impact
                8. 7-day weather-based action plan
                
                Consider Ghana's seasonal patterns and provide practical advice.
                """
            }
        ]
        
        result = self._make_request(self.models['weather_analysis'], messages, 1500)
        
        if 'error' not in result:
            try:
                content = result['choices'][0]['message']['content']
                analysis = {
                    'location': location,
                    'crop': crop,
                    'growth_stage': growth_stage,
                    'weather_data': weather_data,
                    'analysis': content,
                    'timestamp': timezone.now().isoformat(),
                    'model_used': self.models['weather_analysis']
                }
                return analysis
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing weather analysis response: {e}")
                return {"error": "Failed to parse AI response"}
        
        return result

    def predict_crop_yield(self, farm_data: Dict, historical_data: List[Dict] = None) -> Dict:
        """
        Predict crop yield based on various factors
        """
        messages = [
            {
                "role": "system",
                "content": """You are an agricultural data scientist specializing in yield prediction for Ghana's farming systems.
                Use scientific methods and local agricultural knowledge to provide accurate predictions."""
            },
            {
                "role": "user",
                "content": f"""
                Predict crop yield based on the following farm data:
                
                Farm Information: {json.dumps(farm_data, indent=2)}
                Historical Data: {json.dumps(historical_data or [], indent=2)}
                
                Provide analysis including:
                1. Expected yield per hectare
                2. Confidence level of prediction
                3. Key factors affecting yield
                4. Optimization recommendations
                5. Risk factors and mitigation
                6. Comparison with regional averages
                7. Revenue projections
                8. Recommendations for next season
                
                Base predictions on Ghana agricultural standards and practices.
                """
            }
        ]
        
        result = self._make_request(self.models['yield_prediction'], messages, 1800)
        
        if 'error' not in result:
            try:
                content = result['choices'][0]['message']['content']
                prediction = {
                    'farm_data': farm_data,
                    'historical_data': historical_data,
                    'prediction': content,
                    'timestamp': timezone.now().isoformat(),
                    'model_used': self.models['yield_prediction']
                }
                return prediction
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing yield prediction response: {e}")
                return {"error": "Failed to parse AI response"}
        
        return result

    def get_farming_advice(self, question: str, farmer_context: Dict = None, language: str = "English") -> Dict:
        """
        Provide general farming advice in multiple languages
        """
        context_str = json.dumps(farmer_context or {}, indent=2)
        
        messages = [
            {
                "role": "system",
                "content": f"""You are an experienced agricultural extension officer in Ghana with expertise in local farming practices.
                Respond in {language}. Provide practical, culturally appropriate advice for Ghana farmers.
                Consider local resources, climate, and economic conditions."""
            },
            {
                "role": "user",
                "content": f"""
                Farmer's question: {question}
                
                Farmer context: {context_str}
                
                Provide helpful, practical advice considering:
                1. Ghana's agricultural context
                2. Local farming practices and traditions
                3. Available resources and technologies
                4. Economic considerations
                5. Seasonal factors
                6. Sustainability practices
                
                Respond in {language} with clear, actionable guidance.
                """
            }
        ]
        
        result = self._make_request(self.models['general_farming'], messages, 1200)
        
        if 'error' not in result:
            try:
                content = result['choices'][0]['message']['content']
                advice = {
                    'question': question,
                    'farmer_context': farmer_context,
                    'language': language,
                    'advice': content,
                    'timestamp': timezone.now().isoformat(),
                    'model_used': self.models['general_farming']
                }
                return advice
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing farming advice response: {e}")
                return {"error": "Failed to parse AI response"}
        
        return result

    def get_api_status(self) -> Dict:
        """Check OpenRouter API status and available models"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json()
                return {
                    'status': 'operational',
                    'available_models': len(models_data.get('data', [])),
                    'configured_models': self.models,
                    'ghana_context': self.ghana_context,
                    'timestamp': timezone.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'error': f"API status check failed: {response.status_code}",
                    'timestamp': timezone.now().isoformat()
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error': f"Connection failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }

# Initialize the integration instance
openrouter_ai = OpenRouterDjangoIntegration()


def test_openrouter_integration():
    """
    Test function to validate OpenRouter AI integration
    """
    print("🌾 Testing AgriConnect OpenRouter AI Integration...")
    print("=" * 60)
    
    # Test 1: API Status Check
    print("\n1. Testing API Connection...")
    status = openrouter_ai.get_api_status()
    print(f"Status: {status['status']}")
    
    if status['status'] == 'operational':
        print(f"✅ Connected successfully!")
        print(f"Available models: {status['available_models']}")
    else:
        print(f"❌ Connection failed: {status.get('error', 'Unknown error')}")
        return False
    
    # Test 2: Crop Analysis
    print("\n2. Testing Crop Suitability Analysis...")
    try:
        crop_analysis = openrouter_ai.analyze_crop_suitability(
            location="Ashanti Region",
            soil_type="Clay loam",
            crop="Maize",
            season="Major season"
        )
        
        if 'error' not in crop_analysis:
            print("✅ Crop analysis completed successfully!")
            print(f"Model used: {crop_analysis['model_used']}")
        else:
            print(f"❌ Crop analysis failed: {crop_analysis['error']}")
            
    except Exception as e:
        print(f"❌ Crop analysis error: {str(e)}")
    
    # Test 3: Market Prediction
    print("\n3. Testing Market Price Prediction...")
    try:
        market_prediction = openrouter_ai.predict_market_prices(
            crop="Tomato",
            region="Greater Accra",
            season="Minor season",
            quantity=2.5
        )
        
        if 'error' not in market_prediction:
            print("✅ Market prediction completed successfully!")
            print(f"Model used: {market_prediction['model_used']}")
        else:
            print(f"❌ Market prediction failed: {market_prediction['error']}")
            
    except Exception as e:
        print(f"❌ Market prediction error: {str(e)}")
    
    # Test 4: Farming Advice
    print("\n4. Testing General Farming Advice...")
    try:
        advice = openrouter_ai.get_farming_advice(
            question="What's the best time to plant cassava in Northern Ghana?",
            farmer_context={
                "location": "Northern Region",
                "farm_size": "2 hectares",
                "experience": "5 years"
            }
        )
        
        if 'error' not in advice:
            print("✅ Farming advice generated successfully!")
            print(f"Model used: {advice['model_used']}")
        else:
            print(f"❌ Farming advice failed: {advice['error']}")
            
    except Exception as e:
        print(f"❌ Farming advice error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🚀 OpenRouter AI Integration Test Complete!")
    print("Ready for production integration with AgriConnect Ghana!")
    
    return True


if __name__ == "__main__":
    test_openrouter_integration()
