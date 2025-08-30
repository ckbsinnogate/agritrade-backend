#!/usr/bin/env python3
"""
AgriConnect SMS Service - AVRSMS API Integration
Clean implementation of AVRSMS service for farmer onboarding
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class AVRSMSService:
    """Integration with AVRSMS service - Clean implementation"""
    
    def __init__(self):
        self.api_id = settings.AVRSMS_API_ID
        self.api_password = settings.AVRSMS_API_PASSWORD  
        self.base_url = "https://api.avrsms.com/api"  # Updated with correct /api path
        self.sender_id = "AgriConnect"
        
    def send_sms(self, phone_number: str, message: str, uid: str = None) -> Dict:
        """Send SMS using AVRSMS API"""
        try:
            # Format phone number
            formatted_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Prepare SMS data
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
            
            # Send POST request
            url = f"{self.base_url}/SendSMS"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"AVRSMS Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
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
            logger.error(f"AVRSMS request failed: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'phone_number': phone_number
            }
        except Exception as e:
            logger.error(f"AVRSMS send failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone_number': phone_number
            }
    
    def get_delivery_status(self, message_id: str = None, uid: str = None) -> Dict:
        """Check delivery status of sent SMS"""
        try:
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password
            }
            
            if message_id:
                payload['message_id'] = message_id
            if uid:
                payload['uid'] = uid
            
            url = f"{self.base_url}/GetDeliveryStatus"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
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
                
        except Exception as e:
            logger.error(f"Delivery status check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_balance(self) -> Dict:
        """Check SMS account balance"""
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
                
        except Exception as e:
            logger.error(f"Balance check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_verification_otp(self, phone_number: str, brand: str = "AgriConnect") -> Dict:
        """Send OTP verification SMS"""
        try:
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
                
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone_number': phone_number
            }
    
    def verify_otp(self, verification_id: int, verification_code: str) -> Dict:
        """Verify OTP code"""
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
                
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            return {
                'success': False,
                'verified': False,
                'error': str(e),
                'verification_id': verification_id
            }
