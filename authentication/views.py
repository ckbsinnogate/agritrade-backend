"""
AgriConnect Authentication Views
Implements dual authentication system (phone/email + OTP) per PRD Section 6
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.cache import cache
import random
import string
import logging

from .models import User, OTPCode
from .serializers import (
    UserRegistrationSerializer,
    OTPVerificationSerializer, 
    UserLoginSerializer,
    PasswordlessLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)

# Import the frontend-compatible serializer
from .frontend_serializers import FrontendUserRegistrationSerializer

# Email OTP imports
from .serializers_email_otp import (
    EmailOTPRequestSerializer,
    EmailOTPVerifySerializer,
    EmailOTPResendSerializer,
    EmailOTPStatusSerializer,
    EmailOTPRegistrationSerializer,
    EmailOTPLoginSerializer,
    EmailOTPPasswordResetSerializer
)
from .services_otp import EmailOTPService
from .models_otp import EmailOTP

# Email OTP Views - Professional Implementation
from .serializers_email_otp import (
    EmailOTPRequestSerializer,
    EmailOTPVerifySerializer,
    EmailOTPResendSerializer,
    EmailOTPStatusSerializer,
    EmailOTPRegistrationSerializer,
    EmailOTPLoginSerializer,
    EmailOTPPasswordResetSerializer
)
from .services_otp import EmailOTPService
from .models_otp import EmailOTP


logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    """
    User registration with dual authentication (phone OR email)
    POST /api/v1/auth/register/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                      # Generate OTP for verification
                    otp_code = self.generate_otp()
                    contact_method = 'email' if user.email else 'phone'
                    
                    # Create OTP record
                    if contact_method == 'email':
                        OTPCode.objects.create(
                            user=user,                            email=user.email,
                            code=otp_code,
                            purpose='registration',
                            expires_at=timezone.now() + timedelta(minutes=10)
                        )
                    else:
                        # Use SMS OTP service which generates its own code
                        from .services_sms_otp import SMSOTPService
                        sms_service = SMSOTPService()
                        
                        success, message, otp_instance = sms_service.send_otp(
                            phone_number=user.phone_number,
                            purpose='registration',
                            ip_address='127.0.0.1',
                            user_agent='FrontendRegistration'
                        )
                        
                        if success:
                            logger.info(f"SMS OTP sent successfully to {user.phone_number} via AVRSMS")
                        else:
                            logger.error(f"Failed to send SMS OTP to {user.phone_number}: {message}")
                            # Fall back to creating a manual OTP record  
                            otp_code = self.generate_otp()
                            OTPCode.objects.create(
                                user=user,
                                phone_number=user.phone_number,
                                code=otp_code,
                                purpose='registration',
                                expires_at=timezone.now() + timedelta(minutes=10)
                            )
                    
                    # Send OTP (implement SMS/Email service here)
                    self.send_otp(user, otp_code, contact_method)
                    
                    logger.info(f"User registered successfully: {user.username}")
                    
                    return Response({
                        'message': 'Registration successful. Please verify your contact method.',
                        'user_id': user.id,
                        'contact_method': contact_method,
                        'contact_value': user.email or user.phone_number
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                return Response({
                    'error': 'Registration failed. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_otp(self):
        """Generate 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_otp(self, user, otp_code, contact_method):
        """Send OTP via SMS or Email using professional services"""
        if contact_method == 'email':
            # Use the Email OTP Service for actual email sending
            service = EmailOTPService()
            
            # Create EmailOTP record for tracking and Mailtrap sending
            try:
                with transaction.atomic():
                    # Create EmailOTP instance
                    from .models_otp import EmailOTP
                    email_otp = EmailOTP.objects.create(
                        email=user.email,
                        user=user,
                        purpose='registration',
                        otp_code=otp_code,  # Use the generated OTP
                        ip_address='127.0.0.1',  # Default for internal calls
                        user_agent='UserRegistration'
                    )
                    
                    # Send email using the professional service
                    email_sent = service._send_otp_email(email_otp, {
                        'user_name': user.first_name,
                        'company_name': 'AgriConnect',
                        'support_email': 'support@agriconnect.com'
                    })
                    
                    if email_sent:
                        logger.info(f"Email OTP {otp_code} sent successfully to {user.email} via Mailtrap")
                    else:
                        logger.error(f"Failed to send email OTP to {user.email}")
                        
            except Exception as e:
                logger.error(f"Error sending email OTP: {str(e)}")
                # Fallback to logging for development
                logger.info(f"Fallback: Email OTP {otp_code} would be sent to {user.email}")
        else:
            # SMS sending placeholder - TODO: Implement SMS service
            logger.info(f"SMS OTP {otp_code} would be sent to {user.phone_number}")

        # TODO: Implement actual SMS sending for phone numbers


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp_view(request):
    """
    Send OTP to user's registered contact method
    POST /api/v1/auth/send-otp/
    """
    identifier = request.data.get('identifier', '').strip()
    purpose = request.data.get('purpose', 'verification')  # registration, login, password_reset
    
    if not identifier:
        return Response({
            'error': 'Identifier (email or phone) is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Rate limiting
    cache_key = f"otp_request_{identifier}"
    if cache.get(cache_key):
        return Response({
            'error': 'Please wait before requesting another OTP'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        # Find user by identifier
        if '@' in identifier:
            identifier = identifier.lower()
            user = User.objects.get(email=identifier)
            contact_method = 'email'
        else:
            # Normalize phone number
            import re
            clean_phone = re.sub(r'[\s\-()]', '', identifier)
            if clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+233' + clean_phone[1:]
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            
            user = User.objects.get(phone_number=clean_phone)
            contact_method = 'phone'
            identifier = clean_phone
        
        # Generate OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
          # Invalidate previous OTPs
        OTPCode.objects.filter(
            user=user, 
            purpose=purpose,
            is_used=False
        ).update(is_used=True)
          # Create new OTP
        if contact_method == 'email':
            OTPCode.objects.create(
                user=user,
                email=identifier,
                code=otp_code,
                purpose=purpose,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
        else:
            OTPCode.objects.create(
                user=user,
                phone_number=identifier,
                code=otp_code,
                purpose=purpose,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
        
        # Send OTP (implement actual sending)
        logger.info(f"OTP {otp_code} would be sent to {identifier}")
        
        # Set rate limiting cache
        cache.set(cache_key, True, timeout=30)  # 30 seconds cooldown
        
        return Response({
            'message': f'OTP sent to your {contact_method}',
            'contact_method': contact_method
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'No account found with this identifier'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Send OTP error: {str(e)}")
        return Response({
            'error': 'Failed to send OTP. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp_view(request):
    """
    Verify OTP code
    POST /api/v1/auth/verify-otp/
    """
    serializer = OTPVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        identifier = serializer.validated_data['normalized_identifier']
        otp_code = serializer.validated_data['otp_code']
        purpose = request.data.get('purpose', 'verification')
        
        try:
            # Find user
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(phone_number=identifier)
              # Find valid OTP
            otp = OTPCode.objects.filter(
                user=user,
                code=otp_code,
                purpose=purpose,
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if not otp:
                return Response({
                    'error': 'Invalid or expired OTP code'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            otp.is_used = True
            otp.used_at = timezone.now()
            otp.save()
              # Update user verification status
            if '@' in identifier:
                user.email_verified = True
            else:
                user.phone_verified = True
            
            user.is_verified = True
            user.save()
            
            # Generate tokens for login
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            logger.info(f"OTP verified successfully for user: {user.username}")
            
            return Response({
                'message': 'OTP verified successfully',
                'user': UserProfileSerializer(user).data,
                'access': str(access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return Response({
                'error': 'Verification failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Traditional login with email/phone/username + password
    POST /api/v1/auth/login/
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        logger.info(f"User logged in: {user.username}")
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'access': str(access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateAPIView):
    """
    Get and update user profile
    GET/PUT /api/v1/auth/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow logout even without valid auth
def logout_view(request):
    """
    Logout user (blacklist refresh token)
    POST /api/v1/auth/logout/
    
    Allows logout even if authentication token is expired or invalid
    """
    try:
        # Handle different ways refresh token might be sent
        refresh_token = None
        
        # Try to get refresh token from request data
        if hasattr(request, 'data') and request.data:
            refresh_token = request.data.get('refresh') or request.data.get('refresh_token')
        
        # Try to get from Authorization header if not found in data
        if not refresh_token:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                # Extract token from Bearer header
                token = auth_header.split(' ')[1]
                try:
                    # Try to use the access token to find and blacklist associated refresh token
                    from rest_framework_simplejwt.tokens import UntypedToken
                    UntypedToken(token)  # Validate the token
                    refresh_token = token  # Use the token itself
                except Exception:
                    pass
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"User logged out with token blacklisting: {request.user.username}")
            except Exception as token_error:
                logger.warning(f"Token blacklisting failed for {request.user.username}: {str(token_error)}")
                # Continue with logout even if token blacklisting fails
        else:
            logger.info(f"User logged out without token blacklisting: {request.user.username}")
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Logout error for user {getattr(request.user, 'username', 'Unknown')}: {str(e)}")
        # Return success even if there's an error to prevent frontend issues
        return Response({
            'success': True,
            'message': 'Logout completed',
            'warning': 'Token cleanup may have failed'
        }, status=status.HTTP_200_OK)


# JWT Token Views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
    TokenBlacklistView
)

class TokenRefreshView(BaseTokenRefreshView):
    """Custom token refresh view with logging"""
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Token refresh request from IP: {request.META.get('REMOTE_ADDR')}")
        return super().post(request, *args, **kwargs)


class ForgotPasswordView(APIView):
    """
    Send OTP for password reset
    POST /api/v1/auth/forgot-password/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        identifier = request.data.get('identifier')  # email or phone
        
        if not identifier:
            return Response({
                'error': 'Email or phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by email or phone
        user = None
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier, email_verified=True)
            else:
                user = User.objects.get(phone_number=identifier, phone_verified=True)
        except User.DoesNotExist:
            # Don't reveal if user exists or not
            return Response({
                'message': 'If the account exists, you will receive an OTP'
            }, status=status.HTTP_200_OK)
        
        # Generate and send OTP
        otp_code = self.generate_otp()
        contact_method = 'email' if '@' in identifier else 'phone'
        
        try:            # Create OTP record
            if contact_method == 'email':
                otp_record = OTPCode.objects.create(
                    user=user,
                    email=identifier,
                    code=otp_code,
                    purpose='password_reset',
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
            else:
                otp_record = OTPCode.objects.create(
                    user=user,
                    phone_number=identifier,
                    code=otp_code,
                    purpose='password_reset',
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
            
            # Send OTP (placeholder - implement actual SMS/email service)
            self.send_otp(identifier, otp_code, 'password_reset', contact_method)
            
            return Response({
                'message': 'Password reset OTP sent successfully',
                'otp_id': str(otp_record.id)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Password reset OTP error: {str(e)}")
            return Response({
                'error': 'Failed to send OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))
    
    def send_otp(self, contact, otp, purpose, method):        # Implement actual SMS/email sending
        logger.info(f"OTP {otp} sent to {contact} via {method} for {purpose}")


class ResetPasswordView(APIView):
    """
    Reset password with OTP verification
    POST /api/v1/auth/reset-password/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        otp_id = request.data.get('otp_id')
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')
        
        if not all([otp_id, otp_code, new_password]):
            return Response({
                'error': 'OTP ID, OTP code, and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify OTP
            otp_record = OTPCode.objects.get(
                id=otp_id,
                code=otp_code,
                purpose='password_reset',
                is_used=False
            )
            
            if not otp_record.is_valid() or otp_record.expires_at <= timezone.now():
                return Response({
                    'error': 'OTP has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Reset password
            user = otp_record.user
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp_record.is_used = True
            otp_record.save()
            
            logger.info(f"Password reset successful for user: {user.username}")
            
            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
            
        except OTPCode.DoesNotExist:
            return Response({
                'error': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Change password for authenticated users
    POST /api/v1/auth/change-password/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({
                    'error': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            logger.info(f"Password changed for user: {user.username}")
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(RetrieveUpdateAPIView):
    """
    Update user profile
    PUT/PATCH /api/v1/auth/profile/update/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class DeactivateAccountView(APIView):
    """
    Deactivate user account
    POST /api/v1/auth/deactivate/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        user.is_active = False
        user.save()
        
        logger.info(f"Account deactivated: {user.username}")
        
        return Response({
            'message': 'Account deactivated successfully'
        }, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    """
    Delete user account (soft delete by marking as inactive)
    POST /api/v1/auth/delete/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        password = request.data.get('password')
        
        if not password:
            return Response({
                'error': 'Password confirmation required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        if not user.check_password(password):
            return Response({
                'error': 'Password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Soft delete - mark as inactive and anonymize data
        user.is_active = False
        user.email = f"deleted_{user.id}@agriconnect.deleted"
        user.phone_number = None
        user.first_name = "Deleted"
        user.last_name = "User"
        user.save()
        
        logger.info(f"Account deleted: {user.username}")
        
        return Response({
            'message': 'Account deleted successfully'
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    Resend OTP for verification
    POST /api/v1/auth/resend-otp/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        identifier = request.data.get('identifier')
        purpose = request.data.get('purpose', 'registration')
        
        if not identifier:
            return Response({
                'error': 'Email or phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Rate limiting check
        cache_key = f"otp_resend_{identifier}"
        if cache.get(cache_key):
            return Response({
                'error': 'Please wait before requesting another OTP'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Find user
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(phone_number=identifier)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate new OTP
        otp_code = self.generate_otp()
        contact_method = 'email' if '@' in identifier else 'phone'
        
        try:
            # Invalidate old OTPs
            OTPCode.objects.filter(
                user=user,
                purpose=purpose,
                is_used=False
            ).update(is_used=True)
              # Create new OTP
            if contact_method == 'email':
                otp_record = OTPCode.objects.create(
                    user=user,
                    email=identifier,
                    code=otp_code,
                    purpose=purpose,
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
            else:
                otp_record = OTPCode.objects.create(
                    user=user,
                    phone_number=identifier,
                    code=otp_code,
                    purpose=purpose,
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
            
            # Send OTP
            self.send_otp(identifier, otp_code, purpose, contact_method)
            
            # Set rate limiting
            cache.set(cache_key, True, 60)  # 1 minute cooldown
            
            return Response({
                'message': 'OTP sent successfully',
                'otp_id': str(otp_record.id)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Resend OTP error: {str(e)}")
            return Response({
                'error': 'Failed to send OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))
    
    def send_otp(self, contact, otp, purpose, method):
        # Implement actual SMS/email sending
        logger.info(f"OTP {otp} sent to {contact} via {method} for {purpose}")


# Frontend-compatible User Registration View
class FrontendUserRegistrationView(APIView):
    """
    Frontend-compatible user registration endpoint
    POST /api/v1/auth/register-frontend/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = FrontendUserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Generate OTP for verification
                    contact_method = 'email' if user.email else 'phone'
                    
                    # Use appropriate OTP service based on contact method
                    if contact_method == 'email':
                        # Use email OTP generation
                        otp_code = self.generate_otp()
                        
                        # Create OTP record
                        OTPCode.objects.create(
                            user=user,
                            email=user.email,
                            code=otp_code,
                            purpose='registration',
                            expires_at=timezone.now() + timedelta(minutes=10)
                        )                          # Send email OTP
                        self.send_otp(user, otp_code, 'email')
                        
                    else:
                        # Use SMS OTP service which generates its own code
                        from .services_sms_otp import SMSOTPService
                        sms_service = SMSOTPService()
                        
                        success, message, otp_instance = sms_service.generate_and_send_otp(
                            phone_number=user.phone_number,
                            purpose='registration',
                            user=user,
                            ip_address='127.0.0.1',
                            user_agent='FrontendRegistration'
                        )
                        
                        if success:
                            logger.info(f"SMS OTP sent successfully to {user.phone_number} via AVRSMS")
                        else:
                            logger.error(f"Failed to send SMS OTP to {user.phone_number}: {message}")
                            # Fall back to creating a manual OTP record
                            otp_code = self.generate_otp()
                            OTPCode.objects.create(
                                user=user,
                                phone_number=user.phone_number,
                                code=otp_code,
                                purpose='registration',                                expires_at=timezone.now() + timedelta(minutes=10)
                            )
                    
                    logger.info(f"User registered successfully via frontend endpoint: {user.username}")
                    
                    return Response({
                        'message': 'Registration successful. Please verify your contact method.',
                        'user_id': user.id,
                        'contact_method': contact_method,
                        'contact_value': user.email or user.phone_number,
                        'otp_required': True
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                logger.error(f"Frontend registration error: {str(e)}")
                logger.error(f"Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return Response({
                    'error': 'Registration failed. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_otp(self):
        """Generate 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_otp(self, user, otp_code, contact_method):
        """Send OTP via SMS or Email using professional services"""
        if contact_method == 'email':
            # Use the Email OTP Service for actual email sending
            service = EmailOTPService()
            
            # Create EmailOTP record for tracking and Mailtrap sending
            try:
                with transaction.atomic():                    # Create EmailOTP instance
                    from .models_otp import EmailOTP
                    email_otp = EmailOTP.objects.create(
                        email=user.email,
                        user=user,
                        purpose='registration',
                        otp_code=otp_code,  # Use the generated OTP
                        ip_address='127.0.0.1',  # Default for internal calls
                        user_agent='FrontendRegistration'
                    )
                    
                    # Send email using the professional service
                    email_sent = service._send_otp_email(email_otp, {
                        'user_name': user.first_name,
                        'company_name': 'AgriConnect',
                        'support_email': 'support@agriconnect.com'
                    })
                    
                    if email_sent:
                        logger.info(f"Email OTP {otp_code} sent successfully to {user.email} via Mailtrap")
                    else:
                        logger.error(f"Failed to send email OTP to {user.email}")
                        
            except Exception as e:
                logger.error(f"Error sending email OTP: {str(e)}")
                # Fallback to logging for development
                logger.info(f"Fallback: OTP {otp_code} would be sent to email: {user.email}")
        else:
            # Use the SMS OTP Service for actual SMS sending
            from .services_sms_otp import SMSOTPService
            service = SMSOTPService()
            
            try:
                # Send SMS using our professional SMS OTP service
                success, message, otp_instance = service.send_otp(
                    phone_number=user.phone_number,
                    purpose='registration',
                    ip_address='127.0.0.1',  # Default for internal calls
                    user_agent='FrontendRegistration'
                )
                
                if success:
                    logger.info(f"SMS OTP sent successfully to {user.phone_number} via AVRSMS")
                else:
                    logger.error(f"Failed to send SMS OTP to {user.phone_number}: {message}")
                    
            except Exception as e:
                logger.error(f"Error sending SMS OTP: {str(e)}")
                # Fallback to logging for development
                logger.info(f"Fallback: SMS OTP {otp_code} would be sent to phone: {user.phone_number}")
        
        # SMS sending now implemented using AVRSMS service


# API Root Views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_api_root(request, format=None):
    """
    Authentication API Root
    Provides links to all authentication endpoints
    """
    return Response({
        'message': 'AgriConnect Authentication API',
        'version': '1.0',
        'endpoints': {
            'user_registration': reverse('authentication:register', request=request, format=format),
            'verify_otp': reverse('authentication:verify-otp', request=request, format=format),
            'resend_otp': reverse('authentication:resend-otp', request=request, format=format),
            'login': reverse('authentication:login', request=request, format=format),
            'logout': reverse('authentication:logout', request=request, format=format),
            'token_refresh': reverse('authentication:token-refresh', request=request, format=format),
            'forgot_password': reverse('authentication:forgot-password', request=request, format=format),
            'reset_password': reverse('authentication:reset-password', request=request, format=format),
            'change_password': reverse('authentication:change-password', request=request, format=format),
            'profile': reverse('authentication:profile', request=request, format=format),
            'deactivate_account': reverse('authentication:deactivate-account', request=request, format=format),
            'delete_account': reverse('authentication:delete-account', request=request, format=format),
        },
        'documentation': {
            'registration': 'POST to /register/ with phone/email, password, first_name, last_name',
            'verification': 'POST to /verify-otp/ with identifier and otp_code',
            'login': 'POST to /login/ with identifier and password',
            'profile': 'GET/PUT to /profile/ to view/update user profile'
        }
    })

# Email OTP Views - Professional Implementation

class EmailOTPRequestView(APIView):
    """
    Request email OTP
    POST /api/v1/auth/email-otp/request/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Request OTP to be sent to email"""
        serializer = EmailOTPRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            purpose = serializer.validated_data['purpose']
            
            # Get client information
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Check if user exists for certain purposes
            user = None
            if purpose in ['login', 'password_reset']:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return Response({
                        'error': 'User with this email does not exist',
                        'code': 'USER_NOT_FOUND'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Generate and send OTP
            service = EmailOTPService()
            success, message, otp_instance = service.generate_and_send_otp(
                email=email,
                purpose=purpose,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if success:
                return Response({
                    'message': message,
                    'email': email,
                    'purpose': purpose,
                    'expires_in_minutes': otp_instance.expires_at.minute if otp_instance else 10,
                    'code': 'OTP_SENT'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': message,
                    'code': 'OTP_SEND_FAILED'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid data provided',
            'details': serializer.errors,
            'code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EmailOTPVerifyView(APIView):
    """
    Verify email OTP
    POST /api/v1/auth/email-otp/verify/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Verify OTP code"""
        serializer = EmailOTPVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            purpose = serializer.validated_data['purpose']
            
            # Get client information
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Verify OTP
            service = EmailOTPService()
            success, message, otp_instance = service.verify_otp(
                email=email,
                otp_code=otp_code,
                purpose=purpose,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if success:
                response_data = {
                    'message': message,
                    'email': email,
                    'purpose': purpose,
                    'verified_at': otp_instance.verified_at.isoformat() if otp_instance else None,
                    'code': 'OTP_VERIFIED'
                }
                
                # For login purpose, include user info and tokens
                if purpose == 'login' and otp_instance and otp_instance.user:
                    user = otp_instance.user
                    refresh = RefreshToken.for_user(user)
                    response_data.update({
                        'user': {
                            'id': str(user.id),
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'is_verified': user.is_verified
                        },
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh)
                    })
                
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': message,
                    'code': 'OTP_VERIFICATION_FAILED'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid data provided',
            'details': serializer.errors,
            'code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EmailOTPResendView(APIView):
    """
    Resend email OTP
    POST /api/v1/auth/email-otp/resend/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Resend OTP to email"""
        serializer = EmailOTPResendSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            purpose = serializer.validated_data['purpose']
            
            # Get client information
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Resend OTP
            service = EmailOTPService()
            success, message, otp_instance = service.resend_otp(
                email=email,
                purpose=purpose,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if success:
                return Response({
                    'message': message,
                    'email': email,
                    'purpose': purpose,
                    'code': 'OTP_RESENT'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': message,
                    'code': 'OTP_RESEND_FAILED'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid data provided',
            'details': serializer.errors,
            'code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EmailOTPStatusView(APIView):
    """
    Get email OTP status
    GET /api/v1/auth/email-otp/status/?email=...&purpose=...
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get OTP status for email and purpose"""
        email = request.query_params.get('email')
        purpose = request.query_params.get('purpose', 'registration')
        
        if not email:
            return Response({
                'error': 'Email parameter is required',
                'code': 'MISSING_EMAIL'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find the most recent OTP
        otp = EmailOTP.objects.filter(
            email=email,
            purpose=purpose
        ).order_by('-created_at').first()
        
        if not otp:
            return Response({
                'error': 'No OTP found for this email and purpose',
                'code': 'OTP_NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmailOTPStatusSerializer(otp)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmailOTPRegistrationView(APIView):
    """
    Register user with email OTP verification
    POST /api/v1/auth/email-otp/register/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Register user with OTP verification"""
        serializer = EmailOTPRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    
                    logger.info(f"User registered successfully with email OTP: {user.email}")
                    
                    return Response({
                        'message': 'Registration successful',
                        'user': {
                            'id': str(user.id),
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'roles': [role.name for role in user.roles.all()],
                            'is_verified': user.is_verified,
                            'email_verified': user.email_verified
                        },
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh),
                        'code': 'REGISTRATION_SUCCESS'
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                return Response({
                    'error': 'Registration failed',
                    'details': str(e),
                    'code': 'REGISTRATION_ERROR'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Invalid data provided',
            'details': serializer.errors,
            'code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)


class EmailOTPLoginView(APIView):
    """
    Login with email and optional OTP for 2FA
    POST /api/v1/auth/email-otp/login/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Login with email and optional OTP"""
        serializer = EmailOTPLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            otp_code = serializer.validated_data.get('otp_code')
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            logger.info(f"User logged in successfully: {user.email}")
            
            response_data = {
                'message': 'Login successful',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'roles': [role.name for role in user.roles.all()],
                    'is_verified': user.is_verified,
                    'email_verified': getattr(user, 'email_verified', True)
                },
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'code': 'LOGIN_SUCCESS'
            }
            
            if otp_code:
                response_data['two_factor_verified'] = True
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid credentials',
            'details': serializer.errors,
            'code': 'LOGIN_FAILED'
        }, status=status.HTTP_401_UNAUTHORIZED)


class EmailOTPPasswordResetView(APIView):
    """
    Reset password with email OTP verification
    POST /api/v1/auth/email-otp/password-reset/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Reset password with OTP verification"""
        serializer = EmailOTPPasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            logger.info(f"Password reset successfully for user: {user.email}")
            
            return Response({
                'message': 'Password reset successful',
                'email': user.email,
                'code': 'PASSWORD_RESET_SUCCESS'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid data provided',
            'details': serializer.errors,
            'code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
