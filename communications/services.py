"""
AgriConnect Communications Services
SMS & OTP Integration with AVRSMS API

This module provides:
- SMS sending via AVRSMS API 
- OTP generation and verification
- Multi-language message support
- Delivery status tracking
- Bulk messaging capabilities
"""

import requests
import random
import string
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import SMSProvider, SMSTemplate, SMSMessage, OTPCode, CommunicationLog

class AVRSMSService:
    """Service for sending SMS via AVRSMS API"""
    
    def __init__(self):
        self.api_id = getattr(settings, 'AVRSMS_API_ID', 'API113898428691')
        self.api_password = getattr(settings, 'AVRSMS_API_PASSWORD', 'Kingsco45@1')
        self.base_url = 'https://api.avrsms.com/api'
        self.sender_id = getattr(settings, 'AVRSMS_SENDER_ID', 'AgriConnect')
    
    def send_sms(self, phone_number: str, message: str, template_id: Optional[str] = None) -> Dict:
        """Send SMS via AVRSMS API"""
        try:
            # Clean phone number (remove + sign as per API requirements)
            clean_phone = phone_number.replace('+', '') if phone_number.startswith('+') else phone_number
            
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password,
                'sms_type': 'P',  # Promotional (changed from T since transactional is not allowed)
                'encoding': 'T',  # Text
                'sender_id': self.sender_id,
                'phonenumber': clean_phone,
                'textmessage': message,
                'uid': f"agri_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            if template_id:
                payload['templateid'] = template_id
            
            response = requests.post(f"{self.base_url}/SendSMS", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': result.get('status') == 'S',
                    'message_id': result.get('message_id'),
                    'status': result.get('status'),
                    'remarks': result.get('remarks'),
                    'uid': result.get('uid'),
                    'response': result
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'response': {}
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {}
            }
    
    def get_delivery_status(self, message_id: str) -> Dict:
        """Check delivery status of sent SMS"""
        try:
            payload = {
                'api_id': self.api_id,
                'api_password': self.api_password,
                'message_id': message_id
            }
            
            response = requests.post(f"{self.base_url}/GetDeliveryStatus", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('DLRStatus', 'Unknown'),
                    'phone_number': result.get('PhoneNumber'),
                    'cost': result.get('ClientCost', 0),
                    'sent_date': result.get('SentDateUTC'),
                    'response': result
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'response': {}
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': {}
            }

class SMSService:
    """Main SMS service that handles provider selection and message sending"""
    
    def __init__(self):
        self.avrsms = AVRSMSService()
    
    def get_active_provider(self, country_code: str = 'GH') -> Optional[SMSProvider]:
        """Get the best SMS provider for a country"""
        providers = SMSProvider.objects.filter(
            is_active=True
        ).order_by('priority')
        
        for provider in providers:
            if country_code in provider.supported_countries or not provider.supported_countries:
                return provider
        
        return providers.first() if providers.exists() else None
    
    def send_sms(self, 
                 phone_number: str, 
                 message: str, 
                 message_type: str = 'notification',
                 template_name: str = None,
                 variables: Dict = None,
                 user=None) -> SMSMessage:
        """Send SMS message and create database record"""
        
        # Create SMS message record
        sms_message = SMSMessage.objects.create(
            recipient_phone=phone_number,
            recipient=user,
            message_type=message_type,
            content=message,
            status='pending'
        )
        
        try:
            # Get template if specified
            if template_name and variables:
                message = self._format_template_message(template_name, variables, user)
                sms_message.content = message
            
            # Get provider
            country_code = self._extract_country_code(phone_number)
            provider = self.get_active_provider(country_code)
            
            if not provider:
                sms_message.status = 'failed'
                sms_message.failure_reason = 'No active SMS provider available'
                sms_message.save()
                return sms_message
            
            sms_message.provider = provider
            
            # Send via AVRSMS (default provider)
            if provider.provider_code == 'avrsms':
                result = self.avrsms.send_sms(phone_number, message)
                
                if result['success']:
                    sms_message.status = 'sent'
                    sms_message.provider_message_id = str(result.get('message_id', ''))
                    sms_message.provider_response = result['response']
                    sms_message.sent_at = timezone.now()
                else:
                    sms_message.status = 'failed'
                    sms_message.failure_reason = result.get('error', 'Unknown error')
                    sms_message.provider_response = result['response']
            
            sms_message.save()
            
            # Log communication
            self._log_communication(sms_message)
            
            return sms_message
            
        except Exception as e:
            sms_message.status = 'failed'
            sms_message.failure_reason = str(e)
            sms_message.save()
            return sms_message
    
    def _format_template_message(self, template_name: str, variables: Dict, user=None) -> str:
        """Format message using template and variables"""
        try:
            # Try to get template by name and user's language
            language = 'en'
            if user and hasattr(user, 'language'):
                language = user.language
            
            template = SMSTemplate.objects.filter(
                name__icontains=template_name,
                language=language,
                is_active=True
            ).first()
            
            if not template:
                # Fallback to English
                template = SMSTemplate.objects.filter(
                    name__icontains=template_name,
                    language='en',
                    is_active=True
                ).first()
            
            if template:
                message = template.content
                for key, value in variables.items():
                    message = message.replace(f'{{{key}}}', str(value))
                return message
            
        except Exception:
            pass
        
        # Fallback to default message format
        return f"AgriConnect notification: {variables.get('message', 'Update available')}"
    
    def _extract_country_code(self, phone_number: str) -> str:
        """Extract country code from phone number"""
        if phone_number.startswith('+233'):
            return 'GH'  # Ghana
        elif phone_number.startswith('+234'):
            return 'NG'  # Nigeria
        elif phone_number.startswith('+254'):
            return 'KE'  # Kenya
        elif phone_number.startswith('+256'):
            return 'UG'  # Uganda
        elif phone_number.startswith('+27'):
            return 'ZA'  # South Africa
        else:
            return 'GH'  # Default to Ghana
    
    def _log_communication(self, sms_message: SMSMessage):
        """Log communication for analytics"""
        CommunicationLog.objects.create(
            user=sms_message.recipient,
            communication_type='sms',
            recipient=sms_message.recipient_phone,
            purpose=sms_message.message_type,
            status=sms_message.status,
            content_snippet=sms_message.content[:200],
            sms_message=sms_message,
            cost=sms_message.cost
        )

class OTPService:
    """Service for OTP generation, sending, and verification"""
    
    def __init__(self):
        self.sms_service = SMSService()
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp(self, 
                 identifier: str, 
                 purpose: str = 'verification',
                 user=None,
                 validity_minutes: int = 10) -> Dict:
        """Send OTP via SMS or Email"""
        
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=validity_minutes)
            
            # Determine if identifier is email or phone
            is_email = '@' in identifier
            
            # Create OTP record
            otp_data = {
                'code': otp_code,
                'purpose': purpose,
                'expires_at': expires_at,
                'user': user
            }
            
            if is_email:
                otp_data['email'] = identifier
                otp_record = OTPCode.objects.create(**otp_data)
                
                # Send via email
                success = self._send_otp_email(identifier, otp_code, purpose, validity_minutes)
                
            else:
                otp_data['phone_number'] = identifier
                otp_record = OTPCode.objects.create(**otp_data)
                
                # Send via SMS
                template_variables = {
                    'otp_code': otp_code,
                    'validity_minutes': validity_minutes
                }
                
                sms_result = self.sms_service.send_sms(
                    phone_number=identifier,
                    message=f"Your AgriConnect verification code is: {otp_code}. Valid for {validity_minutes} minutes.",
                    message_type='otp',
                    template_name='otp',
                    variables=template_variables,
                    user=user
                )
                
                success = sms_result.status != 'failed'
            
            return {
                'success': success,
                'otp_id': str(otp_record.id),
                'method': 'email' if is_email else 'sms',
                'expires_at': expires_at.isoformat(),
                'message': f"OTP sent to {identifier}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to send OTP'
            }
    
    def verify_otp(self, identifier: str, otp_code: str, purpose: str = 'verification') -> Dict:
        """Verify OTP code"""
        
        try:
            # Find OTP record
            is_email = '@' in identifier
            
            if is_email:
                otp_record = OTPCode.objects.filter(
                    email=identifier,
                    code=otp_code,
                    purpose=purpose,
                    is_used=False
                ).first()
            else:
                otp_record = OTPCode.objects.filter(
                    phone_number=identifier,
                    code=otp_code,
                    purpose=purpose,
                    is_used=False
                ).first()
            
            if not otp_record:
                return {
                    'success': False,
                    'error': 'invalid_otp',
                    'message': 'Invalid or expired OTP code'
                }
            
            # Check attempts
            otp_record.attempts_count += 1
            otp_record.save()
            
            if otp_record.attempts_count > otp_record.max_attempts:
                return {
                    'success': False,
                    'error': 'max_attempts_exceeded',
                    'message': 'Maximum verification attempts exceeded'
                }
            
            # Check expiry
            if otp_record.is_expired():
                return {
                    'success': False,
                    'error': 'expired',
                    'message': 'OTP code has expired'
                }
            
            # Mark as used
            otp_record.is_used = True
            otp_record.used_at = timezone.now()
            otp_record.save()
            
            return {
                'success': True,
                'message': 'OTP verified successfully',
                'user_id': otp_record.user.id if otp_record.user else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'OTP verification failed'
            }
    
    def _send_otp_email(self, email: str, otp_code: str, purpose: str, validity_minutes: int) -> bool:
        """Send OTP via email"""
        try:
            subject = f"AgriConnect - Your verification code: {otp_code}"
            
            message = f"""
            Your AgriConnect verification code is: {otp_code}
            
            This code is valid for {validity_minutes} minutes.
            
            Purpose: {purpose.replace('_', ' ').title()}
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            AgriConnect Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

# Convenience functions
def send_sms(phone_number: str, message: str, user=None) -> SMSMessage:
    """Send SMS message"""
    service = SMSService()
    return service.send_sms(phone_number, message, user=user)

def send_otp(identifier: str, purpose: str = 'verification', user=None) -> Dict:
    """Send OTP to phone or email"""
    service = OTPService()
    return service.send_otp(identifier, purpose, user)

def verify_otp(identifier: str, otp_code: str, purpose: str = 'verification') -> Dict:
    """Verify OTP code"""
    service = OTPService()
    return service.verify_otp(identifier, otp_code, purpose)
