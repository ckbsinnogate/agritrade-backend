"""
AgriConnect SMS/USSD Integration System
Enables farmer access via feature phones across Africa
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.db import transaction

import requests
from twilio.rest import Client

# Import AI services
from ai.services import ai_service_manager

logger = logging.getLogger(__name__)
User = get_user_model()


@dataclass
class SMSFarmer:
    """Represents a farmer accessing via SMS"""
    phone_number: str
    name: str
    location: str
    language: str
    crops: List[str]
    registration_date: datetime
    last_interaction: datetime


class SMSLanguageManager:
    """Handles multi-language SMS responses"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'tw': 'Twi',
        'ha': 'Hausa', 
        'yo': 'Yoruba',
        'ig': 'Igbo',
        'fr': 'French',
        'sw': 'Swahili',
        'am': 'Amharic'
    }
    
    # SMS Response Templates
    MESSAGES = {
        'en': {
            'welcome': "Welcome to AgriConnect AI! Your smart farming assistant. Reply HELP for commands.",
            'help': "Commands: ASK [question], CROP [crop] [location], DISEASE [symptoms], PRICE [crop], WEATHER [location], PROFILE, LANG [code]",
            'crop_advice': "Crop advice for {crop} in {location}:",
            'disease_diagnosis': "Disease diagnosis for symptoms: {symptoms}",
            'market_prices': "Current market prices for {crop}:",
            'weather_update': "Weather forecast for {location}:",
            'profile_info': "Profile: {name}, {location}, Crops: {crops}",
            'language_changed': "Language changed to English",
            'error': "Sorry, I couldn't understand. Reply HELP for commands.",
            'processing': "Processing your request...",
            'ai_response': "🤖 AgriBot: {response}",
            'tokens_used': "Data usage: {tokens} tokens"
        },
        'tw': {
            'welcome': "Akwaaba AgriConnect AI! Wo smart farming boafoɔ. Ma wo nsa so HELP ma commands.",
            'help': "Commands: ASK [asɛmmisa], CROP [adua] [beaeɛ], DISEASE [sɛnkyerɛnne], PRICE [adua], WEATHER [beaeɛ]",
            'crop_advice': "Adua ho nyansafua ma {crop} wɔ {location}:",
            'disease_diagnosis': "Yadeɛ nhwehwɛmu ma sɛnkyerɛnne: {symptoms}",
            'market_prices': "Sesie so bo ma {crop}:",
            'weather_update': "Ewim tebea ho amanneɛ ma {location}:",
            'profile_info': "Profile: {name}, {location}, Adua: {crops}",
            'language_changed': "Kasa asesa kɔ Twi",
            'error': "Mepe wo kyɛw, mantumi ante ase. Ma wo nsa so HELP",
            'processing': "Meyɛ wo nsa so adwuma...",
            'ai_response': "🤖 AgriBot: {response}",
            'tokens_used': "Data usage: {tokens} tokens"
        },
        'ha': {
            'welcome': "Barka da zuwa AgriConnect AI! Mataimakiyar noma mai hankali. Ka mayar da HELP don umarni.",
            'help': "Umarni: ASK [tambaya], CROP [shuka] [wuri], DISEASE [alamomin], PRICE [shuka], WEATHER [wuri]",
            'crop_advice': "Shawarar noma na {crop} a {location}:",
            'disease_diagnosis': "Ganewar cuta na alamomin: {symptoms}",
            'market_prices': "Farashin kasuwa na {crop}:",
            'weather_update': "Hasashen yanayi na {location}:",
            'profile_info': "Profile: {name}, {location}, Shuke-shuke: {crops}",
            'language_changed': "An canja harshe zuwa Hausa",
            'error': "Ka yi hakuri, ban fahimta ba. Ka mayar da HELP",
            'processing': "Ina aiki akan bukatarka...",
            'ai_response': "🤖 AgriBot: {response}",
            'tokens_used': "Data usage: {tokens} tokens"
        },
        'yo': {
            'welcome': "Kaabo si AgriConnect AI! Oluranlọwọ ọgbin ti o ni ọgbọn. Dahun HELP fun awọn aṣẹ.",
            'help': "Awọn aṣẹ: ASK [ibeere], CROP [irugbin] [ibi], DISEASE [awọn ami], PRICE [irugbin], WEATHER [ibi]",
            'crop_advice': "Imọran ọgbin fun {crop} ni {location}:",
            'disease_diagnosis': "Iwadii arun fun awọn ami: {symptoms}",
            'market_prices': "Awọn idiyele ọja lọwọlọwọ fun {crop}:",
            'weather_update': "Asọtẹlẹ oju-ọjọ fun {location}:",
            'profile_info': "Profile: {name}, {location}, Awọn irugbin: {crops}",
            'language_changed': "Ede ti yipada si Yoruba",
            'error': "Pẹlẹ o, emi ko loye. Dahun HELP",
            'processing': "Mo n ṣiṣẹ lori ibeere rẹ...",
            'ai_response': "🤖 AgriBot: {response}",
            'tokens_used': "Data usage: {tokens} tokens"
        },
        'fr': {
            'welcome': "Bienvenue à AgriConnect AI! Votre assistant agricole intelligent. Répondez HELP pour les commandes.",
            'help': "Commandes: ASK [question], CROP [culture] [lieu], DISEASE [symptômes], PRICE [culture], WEATHER [lieu]",
            'crop_advice': "Conseils de culture pour {crop} à {location}:",
            'disease_diagnosis': "Diagnostic de maladie pour les symptômes: {symptoms}",
            'market_prices': "Prix du marché actuels pour {crop}:",
            'weather_update': "Prévisions météo pour {location}:",
            'profile_info': "Profil: {name}, {location}, Cultures: {crops}",
            'language_changed': "Langue changée en français",
            'error': "Désolé, je ne comprends pas. Répondez HELP",
            'processing': "Traitement de votre demande...",
            'ai_response': "🤖 AgriBot: {response}",
            'tokens_used': "Usage de données: {tokens} tokens"
        }
    }
    
    def get_message(self, language: str, key: str, **kwargs) -> str:
        """Get localized message"""
        if language not in self.MESSAGES:
            language = 'en'
        
        template = self.MESSAGES[language].get(key, self.MESSAGES['en'][key])
        return template.format(**kwargs)
    
    def detect_language(self, text: str) -> str:
        """Detect language from text (simplified)"""
        # Simple keyword-based detection
        language_indicators = {
            'tw': ['akwaaba', 'medaase', 'yɛ', 'wɔ', 'me', 'wo'],
            'ha': ['sannu', 'na gode', 'ina', 'wannan', 'ba', 'da'],
            'yo': ['bawo', 'e se', 'mi', 'ni', 'pe', 'ki'],
            'ig': ['ndewo', 'dalu', 'ihe', 'nke', 'na', 'ga'],
            'fr': ['bonjour', 'merci', 'oui', 'non', 'je', 'tu'],
            'sw': ['habari', 'asante', 'ndiyo', 'hapana', 'ni', 'wa']
        }
        
        text_lower = text.lower()
        for lang, indicators in language_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return lang
        
        return 'en'  # Default to English


class AVRSMSService:
    """Integration with AVRSMS service - Using actual API documentation"""
    
    def __init__(self):
        self.api_id = settings.AVRSMS_API_ID
        self.api_password = settings.AVRSMS_API_PASSWORD  
        self.base_url = "https://api.avrsms.com"
        self.sender_id = "AgriConnect"
        
    def send_sms(self, phone_number: str, message: str, uid: str = None) -> Dict:
        """Send SMS using AVRSMS API - POST method"""
        try:
            # Format phone number (remove + and ensure proper format)
            formatted_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Prepare SMS data according to AVRSMS API documentation
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password,
                'sms_type': 'T',  # Text message
                'encoding': 'T',  # Text encoding
                'sender_id': self.sender_id,
                'phonenumber': formatted_number,
                'textmessage': message,
                'ValidityPeriodInSeconds': 86400,  # 24 hours
                'uid': uid or f"agriconnect_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # Send POST request to AVRSMS API
            url = f"{self.base_url}/SendSMS"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            # Log the response for debugging
            logger.info(f"AVRSMS API Response Status: {response.status_code}")
            logger.info(f"AVRSMS API Response: {response.text}")
            
            # Parse response
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"SMS sent to {phone_number}: {result}")
                    
                    # Check for success status
                    if result.get('status') == 'S':
                        return {
                            'success': True,
                            'message_id': result.get('message_id'),
                            'status': result.get('status'),
                            'remarks': result.get('remarks'),
                            'uid': result.get('uid'),
                            'phone_number': formatted_number
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('remarks', 'SMS sending failed'),
                            'status': result.get('status'),
                            'phone_number': formatted_number
                        }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': f'Invalid JSON response: {response.text}',
                        'phone_number': formatted_number
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'phone_number': formatted_number
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AVRSMS API request failed: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'phone_number': phone_number            }
        except Exception as e:
            logger.error(f"AVRSMS send failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone_number': phone_number
            }
    
    def get_delivery_status(self, message_id: str = None, uid: str = None) -> Dict:
        """Check delivery status of sent SMS using AVRSMS API"""
        try:
            # Prepare status check data
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password
            }
            
            if message_id:
                payload['message_id'] = message_id
            if uid:
                payload['uid'] = uid
            
            # Send POST request to check delivery status
            url = f"{self.base_url}/GetDeliveryStatus"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"Delivery status check response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return {
                        'success': True,
                        'message_id': result.get('message_id'),
                        'phone_number': result.get('PhoneNumber'),
                        'delivery_status': result.get('DLRStatus'),
                        'sent_date': result.get('SentDateUTC'),
                        'error_code': result.get('ErrorCode'),
                        'remarks': result.get('Remarks')
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': f'Invalid JSON response: {response.text}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Delivery status check network error: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Delivery status check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_balance(self) -> Dict:
        """Check SMS account balance using AVRSMS API"""
        try:
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password
            }
            
            url = f"{self.base_url}/CheckBalance"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"Balance check response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return {
                        'success': True,
                        'balance': result.get('BalanceAmount'),
                        'currency': result.get('CurrenceCode', 'USD')
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': f'Invalid JSON response: {response.text}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Balance check network error: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Balance check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_verification_otp(self, phone_number: str, brand: str = "AgriConnect") -> Dict:
        """Send OTP verification SMS using AVRSMS API"""
        try:
            # Format phone number
            formatted_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password,
                'brand': brand,
                'phonenumber': formatted_number,
                'sender_id': self.sender_id
            }
            
            url = f"{self.base_url}/Verify"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"OTP verification response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    if result.get('status') == 'S':
                        return {
                            'success': True,
                            'verification_id': result.get('verification_id'),
                            'message': result.get('message'),
                            'phone_number': formatted_number
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('message', 'OTP sending failed'),
                            'phone_number': formatted_number
                        }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': f'Invalid JSON response: {response.text}',
                        'phone_number': formatted_number
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'phone_number': formatted_number
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OTP verification network error: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'phone_number': phone_number
            }
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone_number': phone_number
            }
    
    def verify_otp(self, verification_id: int, verification_code: str) -> Dict:
        """Verify OTP code using AVRSMS API"""
        try:
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password,
                'verification_id': verification_id,
                'verification_code': verification_code
            }
            
            url = f"{self.base_url}/VerifyOTP"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"OTP verification response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    if result.get('status') == 'S':
                        return {
                            'success': True,
                            'verified': True,
                            'message': result.get('message'),
                            'verification_id': verification_id
                        }
                    else:
                        return {
                            'success': False,
                            'verified': False,
                            'error': result.get('message', 'OTP verification failed'),
                            'verification_id': verification_id
                        }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'verified': False,
                        'error': f'Invalid JSON response: {response.text}',
                        'verification_id': verification_id
                    }
            else:
                return {
                    'success': False,
                    'verified': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'verification_id': verification_id
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OTP verification network error: {str(e)}")
            return {
                'success': False,
                'verified': False,
                'error': f'Network error: {str(e)}',
                'verification_id': verification_id
            }
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            return {
                'success': False,
                'verified': False,
                'error': str(e),
                'verification_id': verification_id
            }
                return {
                    'success': True,
                    'verification_id': result.get('verfication_id'),
                    'status': result.get('status'),
                    'remarks': result.get('remarks')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('remarks', 'Failed to send OTP'),
                    'status': result.get('status')
                }
            
        except Exception as e:
            logger.error(f"OTP send failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_otp(self, verification_id: int, verification_code: str) -> Dict:
        """Verify OTP code"""
        try:
            verify_data = {
                'verfication_id': verification_id,
                'verfication_code': verification_code
            }
            
            url = f"{self.base_url}/VerifyStatus"
            response = requests.post(url, json=verify_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"OTP verification: {result}")
            
            return {
                'success': result.get('status') == 'V',
                'verification_id': result.get('verfication_id'),
                'status': result.get('status'),
                'remarks': result.get('remarks'),
                'verified': result.get('status') == 'V'
            }
            
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def receive_sms(self, request_data: Dict) -> Dict:
        """Process incoming SMS (webhook handler)"""
        try:
            phone_number = request_data.get('from')
            message = request_data.get('text', '').strip()
            
            return {
                'phone_number': phone_number,
                'message': message,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"SMS receive failed: {str(e)}")
            return {'error': str(e)}


class USSDService:
    """USSD Menu System for feature phones"""
    
    MAIN_MENU = """CON Welcome to AgriConnect AI
1. Chat with AgriBot
2. Crop Advisory
3. Disease Detection
4. Market Prices
5. Weather Updates
6. My Profile
7. Language Settings
0. Help & Support"""
    
    def __init__(self):
        self.language_manager = SMSLanguageManager()
    
    def handle_ussd_request(self, session_id: str, service_code: str, 
                           phone_number: str, text: str) -> str:
        """Handle USSD session"""
        try:
            # Parse USSD input
            levels = text.split('*') if text else []
            
            if not levels or levels == ['']:
                return self.MAIN_MENU
            
            # Main menu selection
            if len(levels) == 1:
                return self._handle_main_menu(levels[0], phone_number)
            
            # Submenu handling
            return self._handle_submenu(levels, phone_number)
            
        except Exception as e:
            logger.error(f"USSD error: {str(e)}")
            return f"END Error processing request. Please try again."
    
    def _handle_main_menu(self, selection: str, phone_number: str) -> str:
        """Handle main menu selection"""
        if selection == '1':
            return "CON Enter your farming question:"
        elif selection == '2':
            return "CON Crop Advisory\n1. Maize\n2. Rice\n3. Cassava\n4. Yam\n5. Beans\n6. Other"
        elif selection == '3':
            return "CON Disease Detection\nDescribe the symptoms you observe:"
        elif selection == '4':
            return "CON Market Prices\n1. Local Market\n2. Regional Market\n3. Export Market"
        elif selection == '5':
            return "CON Weather Updates\nEnter your location:"
        elif selection == '6':
            return self._get_profile_info(phone_number)
        elif selection == '7':
            return "CON Language Settings\n1. English\n2. Twi\n3. Hausa\n4. Yoruba\n5. French"
        elif selection == '0':
            return self._get_help_menu()
        else:
            return "END Invalid selection. Please try again."
    
    def _handle_submenu(self, levels: List[str], phone_number: str) -> str:
        """Handle submenu selections"""
        try:
            main_selection = levels[0]
            
            if main_selection == '1':  # Chat with AgriBot
                if len(levels) == 2:
                    question = levels[1]
                    return self._process_ai_chat(question, phone_number)
            
            elif main_selection == '2':  # Crop Advisory
                if len(levels) == 2:
                    crop_selection = levels[1]
                    return "CON Enter your location:"
                elif len(levels) == 3:
                    crop_selection = levels[1]
                    location = levels[2]
                    return self._process_crop_advisory(crop_selection, location, phone_number)
            
            elif main_selection == '3':  # Disease Detection
                if len(levels) == 2:
                    symptoms = levels[1]
                    return self._process_disease_detection(symptoms, phone_number)
            
            elif main_selection == '4':  # Market Prices
                if len(levels) == 2:
                    market_type = levels[1]
                    return "CON Enter crop name:"
                elif len(levels) == 3:
                    market_type = levels[1]
                    crop = levels[2]
                    return self._process_market_prices(crop, market_type, phone_number)
            
            elif main_selection == '5':  # Weather Updates
                if len(levels) == 2:
                    location = levels[1]
                    return self._process_weather_update(location, phone_number)
            
            elif main_selection == '7':  # Language Settings
                if len(levels) == 2:
                    language_choice = levels[1]
                    return self._change_language(language_choice, phone_number)
            
            return "END Invalid selection. Please try again."
            
        except Exception as e:
            logger.error(f"Submenu error: {str(e)}")
            return "END Error processing request. Please try again."
    
    def _process_ai_chat(self, question: str, phone_number: str) -> str:
        """Process AI chat request"""
        try:
            # Get or create user
            user = self._get_or_create_user(phone_number)
            
            # Get AI response
            response = ai_service_manager.conversation_service.process_conversation(
                user=user,
                message=question,
                language='en'
            )
            
            if response['success']:
                ai_response = response['response'][:140]  # Truncate for USSD
                return f"END 🤖 AgriBot: {ai_response}"
            else:
                return "END Sorry, I couldn't process your question. Please try again."
                
        except Exception as e:
            logger.error(f"AI chat error: {str(e)}")
            return "END Error processing your question. Please try again."
    
    def _process_crop_advisory(self, crop_selection: str, location: str, phone_number: str) -> str:
        """Process crop advisory request"""
        try:
            crop_mapping = {
                '1': 'maize',
                '2': 'rice', 
                '3': 'cassava',
                '4': 'yam',
                '5': 'beans'
            }
            
            crop_type = crop_mapping.get(crop_selection, 'other')
            user = self._get_or_create_user(phone_number)
            
            # Get crop advisory
            response = ai_service_manager.crop_service.get_crop_advisory(
                user=user,
                crop_type=crop_type,
                location=location,
                season='current',
                farming_stage='general',
                question=f"Give me advice for {crop_type} farming in {location}"
            )
            
            if response['success']:
                advice = response['advice'][:140]  # Truncate for USSD
                return f"END 🌾 Crop Advice: {advice}"
            else:
                return "END Sorry, I couldn't get crop advice. Please try again."
                
        except Exception as e:
            logger.error(f"Crop advisory error: {str(e)}")
            return "END Error getting crop advice. Please try again."
    
    def _process_disease_detection(self, symptoms: str, phone_number: str) -> str:
        """Process disease detection request"""
        try:
            user = self._get_or_create_user(phone_number)
            
            # Get disease detection
            response = ai_service_manager.disease_service.detect_disease(
                user=user,
                crop_type='general',
                symptoms=symptoms,
                location='Africa'
            )
            
            if response['success']:
                diagnosis = response['diagnosis'][:140]  # Truncate for USSD
                return f"END 🔍 Diagnosis: {diagnosis}"
            else:
                return "END Sorry, I couldn't analyze the symptoms. Please try again."
                
        except Exception as e:
            logger.error(f"Disease detection error: {str(e)}")
            return "END Error analyzing symptoms. Please try again."
    
    def _process_market_prices(self, crop: str, market_type: str, phone_number: str) -> str:
        """Process market prices request"""
        try:
            user = self._get_or_create_user(phone_number)
            
            # Get market intelligence
            response = ai_service_manager.market_service.get_market_intelligence(
                user=user,
                crop_type=crop,
                location='Africa',
                market_type='local'
            )
            
            if response['success']:
                intelligence = response['intelligence'][:140]  # Truncate for USSD
                return f"END 📊 Market: {intelligence}"
            else:
                return "END Sorry, I couldn't get market information. Please try again."
                
        except Exception as e:
            logger.error(f"Market prices error: {str(e)}")
            return "END Error getting market prices. Please try again."
    
    def _process_weather_update(self, location: str, phone_number: str) -> str:
        """Process weather update request"""
        try:
            # Simplified weather response
            return f"END 🌤️ Weather for {location}: Partly cloudy, 28°C. Good conditions for farming activities."
            
        except Exception as e:
            logger.error(f"Weather update error: {str(e)}")
            return "END Error getting weather update. Please try again."
    
    def _get_profile_info(self, phone_number: str) -> str:
        """Get farmer profile information"""
        try:
            user = self._get_or_create_user(phone_number)
            return f"END 👤 Profile: {user.username}\nPhone: {phone_number}\nJoined: {user.date_joined.strftime('%Y-%m-%d')}"
            
        except Exception as e:
            logger.error(f"Profile info error: {str(e)}")
            return "END Error getting profile. Please try again."
    
    def _change_language(self, language_choice: str, phone_number: str) -> str:
        """Change user language preference"""
        try:
            language_mapping = {
                '1': 'en',
                '2': 'tw',
                '3': 'ha',
                '4': 'yo',
                '5': 'fr'
            }
            
            language_code = language_mapping.get(language_choice, 'en')
            language_name = self.language_manager.SUPPORTED_LANGUAGES[language_code]
            
            # Update user preference (simplified)
            return f"END ✅ Language changed to {language_name}"
            
        except Exception as e:
            logger.error(f"Language change error: {str(e)}")
            return "END Error changing language. Please try again."
    
    def _get_help_menu(self) -> str:
        """Get help menu"""
        return """END AgriConnect AI Help:
- Chat with AI assistant
- Get crop recommendations
- Diagnose plant diseases
- Check market prices
- Weather updates
- Manage profile
For support: Call +233-XXX-XXXX"""
    
    def _get_or_create_user(self, phone_number: str) -> User:
        """Get or create user from phone number"""
        try:
            # Try to find existing user
            user = User.objects.filter(username=phone_number).first()
            
            if not user:
                # Create new user
                user = User.objects.create_user(
                    username=phone_number,
                    email=f"{phone_number}@sms.agriconnect.com",
                    first_name="SMS",
                    last_name="User"
                )
            
            return user
            
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            raise


class SMSFarmerOnboardingService:
    """Complete SMS-based farmer onboarding system"""
    
    def __init__(self):
        self.sms_service = AfricasTalkingSMSService()
        self.ussd_service = USSDService()
        self.language_manager = SMSLanguageManager()
    
    def process_sms_command(self, phone_number: str, message: str) -> str:
        """Process incoming SMS command"""
        try:
            message = message.strip().upper()
            
            # Detect language
            language = self.language_manager.detect_language(message)
            
            # Parse command
            parts = message.split(' ', 1)
            command = parts[0] if parts else ''
            content = parts[1] if len(parts) > 1 else ''
            
            # Route to appropriate handler
            if command == 'START' or command == 'HELP':
                return self._handle_help_command(phone_number, language)
            elif command == 'ASK':
                return self._handle_ask_command(phone_number, content, language)
            elif command == 'CROP':
                return self._handle_crop_command(phone_number, content, language)
            elif command == 'DISEASE':
                return self._handle_disease_command(phone_number, content, language)
            elif command == 'PRICE':
                return self._handle_price_command(phone_number, content, language)
            elif command == 'WEATHER':
                return self._handle_weather_command(phone_number, content, language)
            elif command == 'PROFILE':
                return self._handle_profile_command(phone_number, language)
            elif command == 'LANG':
                return self._handle_language_command(phone_number, content, language)
            else:
                return self._handle_unknown_command(phone_number, language)
                
        except Exception as e:
            logger.error(f"SMS command processing error: {str(e)}")
            return self.language_manager.get_message('en', 'error')
    
    def _handle_help_command(self, phone_number: str, language: str) -> str:
        """Handle help command"""
        return self.language_manager.get_message(language, 'help')
    
    def _handle_ask_command(self, phone_number: str, question: str, language: str) -> str:
        """Handle ask command"""
        try:
            user = self._get_or_create_user(phone_number)
            
            response = ai_service_manager.conversation_service.process_conversation(
                user=user,
                message=question,
                language=language
            )
            
            if response['success']:
                ai_response = response['response'][:140]  # SMS character limit
                return self.language_manager.get_message(
                    language, 'ai_response', response=ai_response
                )
            else:
                return self.language_manager.get_message(language, 'error')
                
        except Exception as e:
            logger.error(f"Ask command error: {str(e)}")
            return self.language_manager.get_message(language, 'error')
    
    def _handle_crop_command(self, phone_number: str, content: str, language: str) -> str:
        """Handle crop advisory command"""
        try:
            parts = content.split(' ', 1)
            crop_type = parts[0] if parts else 'maize'
            location = parts[1] if len(parts) > 1 else 'Africa'
            
            user = self._get_or_create_user(phone_number)
            
            response = ai_service_manager.crop_service.get_crop_advisory(
                user=user,
                crop_type=crop_type,
                location=location,
                season='current',
                farming_stage='general',
                question=f"Give me advice for {crop_type} farming in {location}"
            )
            
            if response['success']:
                advice = response['advice'][:140]  # SMS character limit
                return self.language_manager.get_message(
                    language, 'crop_advice', crop=crop_type, location=location
                ) + f"\n{advice}"
            else:
                return self.language_manager.get_message(language, 'error')
                
        except Exception as e:
            logger.error(f"Crop command error: {str(e)}")
            return self.language_manager.get_message(language, 'error')
    
    def _handle_disease_command(self, phone_number: str, symptoms: str, language: str) -> str:
        """Handle disease detection command"""
        try:
            user = self._get_or_create_user(phone_number)
            
            response = ai_service_manager.disease_service.detect_disease(
                user=user,
                crop_type='general',
                symptoms=symptoms,
                location='Africa'
            )
            
            if response['success']:
                diagnosis = response['diagnosis'][:140]  # SMS character limit
                return self.language_manager.get_message(
                    language, 'disease_diagnosis', symptoms=symptoms
                ) + f"\n{diagnosis}"
            else:
                return self.language_manager.get_message(language, 'error')
                
        except Exception as e:
            logger.error(f"Disease command error: {str(e)}")
            return self.language_manager.get_message(language, 'error')
    
    def _handle_price_command(self, phone_number: str, crop: str, language: str) -> str:
        """Handle market price command"""
        try:
            user = self._get_or_create_user(phone_number)
            
            response = ai_service_manager.market_service.get_market_intelligence(
                user=user,
                crop_type=crop,
                location='Africa',
                market_type='local'
            )
            
            if response['success']:
                intelligence = response['intelligence'][:140]  # SMS character limit
                return self.language_manager.get_message(
                    language, 'market_prices', crop=crop
                ) + f"\n{intelligence}"
            else:
                return self.language_manager.get_message(language, 'error')
                
        except Exception as e:
            logger.error(f"Price command error: {str(e)}")
            return self.language_manager.get_message(language, 'error')
    
    def _handle_weather_command(self, phone_number: str, location: str, language: str) -> str:
        """Handle weather update command"""
        try:
            # Simplified weather response
            weather_info = f"Partly cloudy, 28°C. Good farming conditions."
            return self.language_manager.get_message(
                language, 'weather_update', location=location
            ) + f"\n{weather_info}"
            
        except Exception as e:
            logger.error(f"Weather command error: {str(e)}")
            return self.language_manager.get_message(language, 'error')
    
    def _handle_profile_command(self, phone_number: str, language: str) -> str:
        """Handle profile command"""
        try:
            user = self._get_or_create_user(phone_number)
            return self.language_manager.get_message(
                language, 'profile_info', 
                name=user.username, 
                location="Africa", 
                crops="Various"
            )
            
        except Exception as e:
            logger.error(f"Profile command error: {str(e)}")
            return self.language_manager.get_message(language, 'error')
    
    def _handle_language_command(self, phone_number: str, language_code: str, language: str) -> str:
        """Handle language change command"""
        try:
            if language_code.lower() in self.language_manager.SUPPORTED_LANGUAGES:
                new_language = language_code.lower()
                return self.language_manager.get_message(new_language, 'language_changed')
            else:
                return self.language_manager.get_message(language, 'error')
                
        except Exception as e:
            logger.error(f"Language command error: {str(e)}")
            return self.language_manager.get_message(language, 'error')
    
    def _handle_unknown_command(self, phone_number: str, language: str) -> str:
        """Handle unknown command"""
        return self.language_manager.get_message(language, 'error')
    
    def _get_or_create_user(self, phone_number: str) -> User:
        """Get or create user from phone number"""
        try:
            user = User.objects.filter(username=phone_number).first()
            
            if not user:
                user = User.objects.create_user(
                    username=phone_number,
                    email=f"{phone_number}@sms.agriconnect.com",
                    first_name="SMS",
                    last_name="User"
                )
            
            return user
            
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            raise


# Initialize the SMS onboarding service
sms_onboarding_service = SMSFarmerOnboardingService()
