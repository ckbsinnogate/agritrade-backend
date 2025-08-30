"""
AgriConnect SMS OTP Views
Professional API endpoints for SMS OTP functionality
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db import transaction
import logging

from .serializers_sms_otp import (
    SMSOTPRequestSerializer,
    SMSOTPVerifySerializer,
    SMSOTPResendSerializer,
    SMSOTPStatusSerializer,
    SMSOTPRegistrationSerializer,
    SMSOTPLoginSerializer,
    SMSOTPPasswordResetSerializer
)
from .services_sms_otp import SMSOTPService
from .models import OTPCode

logger = logging.getLogger(__name__)


class SMSOTPRequestView(APIView):
    """
    Request SMS OTP
    POST /api/v1/auth/sms-otp/request/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Request SMS OTP"""
        serializer = SMSOTPRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            purpose = serializer.validated_data['purpose']
            brand = serializer.validated_data.get('brand', 'AgriConnect')
            
            # Get client information
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Request OTP
            service = SMSOTPService()
            success, message, otp_instance = service.generate_and_send_otp(
                phone_number=phone_number,
                purpose=purpose,
                ip_address=ip_address,
                user_agent=user_agent,
                brand=brand
            )
            
            if success:
                return Response({
                    'message': message,
                    'phone_number': phone_number,
                    'purpose': purpose,
                    'expires_in_minutes': 10,
                    'code': 'SMS_OTP_SENT'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': message,
                    'phone_number': phone_number,
                    'code': 'SMS_OTP_FAILED'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SMSOTPVerifyView(APIView):
    """
    Verify SMS OTP
    POST /api/v1/auth/sms-otp/verify/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Verify OTP code"""
        serializer = SMSOTPVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp_code = serializer.validated_data['otp_code']
            purpose = serializer.validated_data['purpose']
            
            # Get client information
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Verify OTP
            service = SMSOTPService()
            success, message, otp_instance = service.verify_otp(
                phone_number=phone_number,
                otp_code=otp_code,
                purpose=purpose,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if success:
                response_data = {
                    'message': message,
                    'phone_number': phone_number,
                    'purpose': purpose,
                    'verified_at': otp_instance.used_at.isoformat() if otp_instance else None,
                    'code': 'SMS_OTP_VERIFIED'
                }
                
                # For login purpose, include user info and tokens
                if purpose == 'login' and otp_instance and otp_instance.user:
                    user = otp_instance.user
                    refresh = RefreshToken.for_user(user)
                    response_data.update({
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'phone_number': user.phone_number,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'roles': user.roles,
                            'is_verified': user.is_verified,
                            'phone_verified': user.phone_verified
                        },
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    })
                
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': message,
                    'phone_number': phone_number,
                    'code': 'SMS_OTP_INVALID'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SMSOTPResendView(APIView):
    """
    Resend SMS OTP
    POST /api/v1/auth/sms-otp/resend/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Resend SMS OTP"""
        serializer = SMSOTPResendSerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            purpose = serializer.validated_data['purpose']
            brand = serializer.validated_data.get('brand', 'AgriConnect')
            
            # Get client information
            ip_address = self.get_client_ip(request)
            
            # Resend OTP
            service = SMSOTPService()
            success, message, otp_instance = service.resend_otp(
                phone_number=phone_number,
                purpose=purpose,
                ip_address=ip_address,
                brand=brand
            )
            
            if success:
                return Response({
                    'message': message,
                    'phone_number': phone_number,
                    'purpose': purpose,
                    'expires_in_minutes': 10,
                    'code': 'SMS_OTP_RESENT'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': message,
                    'phone_number': phone_number,
                    'code': 'SMS_OTP_RESEND_FAILED'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SMSOTPStatusView(APIView):
    """
    Check SMS OTP status
    GET /api/v1/auth/sms-otp/status/?phone_number=...&purpose=...
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Check OTP status"""
        phone_number = request.query_params.get('phone_number')
        purpose = request.query_params.get('purpose', 'registration')
        
        if not phone_number:
            return Response({
                'error': 'Phone number parameter is required',
                'code': 'MISSING_PHONE_NUMBER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get OTP status
        service = SMSOTPService()
        status_info = service.get_otp_status(phone_number, purpose)
        
        return Response(status_info, status=status.HTTP_200_OK)


class SMSOTPRegistrationView(APIView):
    """
    Register user with SMS OTP verification
    POST /api/v1/auth/sms-otp/register/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Register user with OTP verification"""
        serializer = SMSOTPRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'message': 'Registration successful',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'phone_number': user.phone_number,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'roles': user.roles,
                            'is_verified': user.is_verified,
                            'phone_verified': user.phone_verified,
                            'country': user.country,
                            'region': user.region
                        },
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'code': 'REGISTRATION_SUCCESS'
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                logger.error(f"SMS OTP registration error: {str(e)}")
                return Response({
                    'error': 'Registration failed',
                    'code': 'REGISTRATION_FAILED'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SMSOTPLoginView(APIView):
    """
    Login with SMS OTP (2FA)
    POST /api/v1/auth/sms-otp/login/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Login with SMS OTP"""
        serializer = SMSOTPLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone_number': user.phone_number,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'roles': user.roles,
                    'is_verified': user.is_verified,
                    'phone_verified': user.phone_verified,
                    'email_verified': user.email_verified
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'code': 'LOGIN_SUCCESS'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SMSOTPPasswordResetView(APIView):
    """
    Reset password with SMS OTP verification
    POST /api/v1/auth/sms-otp/password-reset/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Reset password with OTP"""
        serializer = SMSOTPPasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                return Response({
                    'message': 'Password reset successful',
                    'phone_number': user.phone_number,
                    'code': 'PASSWORD_RESET_SUCCESS'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"SMS OTP password reset error: {str(e)}")
                return Response({
                    'error': 'Password reset failed',
                    'code': 'PASSWORD_RESET_FAILED'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Statistics and management endpoints
class SMSOTPStatsView(APIView):
    """
    Get SMS OTP statistics
    GET /api/v1/auth/sms-otp/stats/?days=30
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Get SMS OTP statistics"""
        days = int(request.query_params.get('days', 30))
        
        service = SMSOTPService()
        stats = service.get_statistics(days)
        
        return Response(stats, status=status.HTTP_200_OK)


class SMSOTPCleanupView(APIView):
    """
    Clean up expired SMS OTPs
    POST /api/v1/auth/sms-otp/admin/cleanup/
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Clean up expired SMS OTPs"""
        try:
            service = SMSOTPService()
            result = service.cleanup_expired_otps()
            
            return Response({
                'success': True,
                'message': 'SMS OTP cleanup completed successfully',
                'result': result,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"SMS OTP cleanup failed: {str(e)}")
            return Response({
                'success': False,
                'message': 'SMS OTP cleanup failed',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def cleanup_expired_sms_otps(request):
    """
    Clean up expired SMS OTPs (legacy function-based view)
    POST /api/v1/auth/sms-otp/cleanup/
    """
    service = SMSOTPService()
    cleaned_count = service.cleanup_expired_otps()
    
    return Response({
        'message': f'Cleaned up {cleaned_count} expired SMS OTPs',
        'cleaned_count': cleaned_count,
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)
