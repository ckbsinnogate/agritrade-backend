"""
AgriConnect SMS OTP Serializers
Professional serializers for SMS OTP functionality
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import OTPCode
from .services_sms_otp import SMSOTPService
import re

User = get_user_model()

class SMSOTPRequestSerializer(serializers.Serializer):
    """Serializer for requesting an SMS OTP"""
    
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number to send OTP to (international format)"
    )
    purpose = serializers.ChoiceField(
        choices=[
            ('registration', 'Registration'),
            ('login', 'Login'),
            ('password_reset', 'Password Reset'),
            ('phone_verification', 'Phone Verification'),
            ('account_security', 'Account Security')
        ],
        default='registration',
        help_text="Purpose of the OTP"
    )
    brand = serializers.CharField(
        max_length=50,
        default='AgriConnect',
        required=False,
        help_text="Brand name to include in SMS"
    )
    
    def validate_phone_number(self, value):
        """Validate and normalize phone number"""
        # Remove any whitespace, hyphens, or parentheses
        clean_phone = re.sub(r'[\s\-()]', '', value)
        
        # Handle Ghana format (0XXXXXXXXX -> +233XXXXXXXX)
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        # Add + if missing
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        # Validate international format
        if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +233201234567)"
            )
        
        return clean_phone
    
    class Meta:
        fields = ['phone_number', 'purpose', 'brand']


class SMSOTPVerifySerializer(serializers.Serializer):
    """Serializer for verifying SMS OTP"""
    
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number used for OTP"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=8,
        help_text="OTP code received via SMS"
    )
    purpose = serializers.ChoiceField(
        choices=[
            ('registration', 'Registration'),
            ('login', 'Login'),
            ('password_reset', 'Password Reset'),
            ('phone_verification', 'Phone Verification'),
            ('account_security', 'Account Security')
        ],
        default='registration',
        help_text="Purpose of the OTP"
    )
    
    def validate_phone_number(self, value):
        """Validate and normalize phone number"""
        clean_phone = re.sub(r'[\s\-()]', '', value)
        
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +233201234567)"
            )
        
        return clean_phone
    
    def validate_otp_code(self, value):
        """Validate OTP code format"""
        # Remove any whitespace
        cleaned = value.strip()
        
        # Ensure it's numeric
        if not cleaned.isdigit():
            raise serializers.ValidationError("OTP code must be numeric")
        
        return cleaned
    
    class Meta:
        fields = ['phone_number', 'otp_code', 'purpose']


class SMSOTPResendSerializer(serializers.Serializer):
    """Serializer for resending SMS OTP"""
    
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number to resend OTP to"
    )
    purpose = serializers.ChoiceField(
        choices=[
            ('registration', 'Registration'),
            ('login', 'Login'),
            ('password_reset', 'Password Reset'),
            ('phone_verification', 'Phone Verification'),
            ('account_security', 'Account Security')
        ],
        default='registration',
        help_text="Purpose of the OTP"
    )
    brand = serializers.CharField(
        max_length=50,
        default='AgriConnect',
        required=False,
        help_text="Brand name to include in SMS"
    )
    
    def validate_phone_number(self, value):
        """Validate and normalize phone number"""
        clean_phone = re.sub(r'[\s\-()]', '', value)
        
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +233201234567)"
            )
        
        return clean_phone
    
    class Meta:
        fields = ['phone_number', 'purpose', 'brand']


class SMSOTPStatusSerializer(serializers.ModelSerializer):
    """Serializer for OTP status information"""
    
    status = serializers.SerializerMethodField()
    expires_at = serializers.DateTimeField(read_only=True)
    attempts = serializers.SerializerMethodField()
    max_attempts = serializers.SerializerMethodField()
    
    class Meta:
        model = OTPCode
        fields = [
            'id', 'phone_number', 'purpose', 'status', 
            'created_at', 'expires_at', 'attempts', 'max_attempts'
        ]
        read_only_fields = ['id', 'phone_number', 'purpose', 'created_at']
    
    def get_status(self, obj):
        """Get OTP status"""
        from django.utils import timezone
        
        if obj.is_used:
            return 'verified' if obj.used_at else 'expired'
        
        if obj.expires_at <= timezone.now():
            return 'expired'
        
        return 'pending'
    
    def get_attempts(self, obj):
        """Get attempt count"""
        return getattr(obj, 'attempts', 0)
    
    def get_max_attempts(self, obj):
        """Get maximum attempts allowed"""
        from django.conf import settings
        return getattr(settings, 'SMS_OTP_SETTINGS', {}).get('MAX_ATTEMPTS', 3)


class SMSOTPRegistrationSerializer(serializers.Serializer):
    """Serializer for phone registration with SMS OTP verification"""
    
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number for registration"
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Account password"
    )
    password_confirm = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Password confirmation"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=8,
        help_text="SMS OTP code"
    )
    first_name = serializers.CharField(
        max_length=30,
        help_text="First name"
    )
    last_name = serializers.CharField(
        max_length=30,
        help_text="Last name"
    )
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('FARMER', 'Farmer'),
            ('CONSUMER', 'Consumer'),
            ('PROCESSOR', 'Processor'),
            ('INSTITUTION', 'Institution')
        ]),
        default=['CONSUMER'],
        help_text="User roles"
    )
    country = serializers.CharField(
        max_length=100,
        default='Ghana',
        required=False,
        help_text="Country"
    )
    region = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Region/State"
    )
    
    def validate_phone_number(self, value):
        """Validate and normalize phone number"""
        clean_phone = re.sub(r'[\s\-()]', '', value)
        
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +233201234567)"
            )
        
        # Check if phone number already exists
        if User.objects.filter(phone_number=clean_phone).exists():
            raise serializers.ValidationError("User with this phone number already exists")
        
        return clean_phone
    
    def validate(self, attrs):
        """Validate the entire registration data"""
        # Check password confirmation
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        
        # Verify SMS OTP
        phone_number = attrs['phone_number']
        otp_code = attrs['otp_code']
        
        service = SMSOTPService()
        success, message, otp = service.verify_otp(
            phone_number=phone_number,
            otp_code=otp_code,
            purpose='registration'
        )
        
        if not success:
            raise serializers.ValidationError({
                'otp_code': message
            })
        
        # Store OTP instance for later use
        attrs['_otp_instance'] = otp
        
        return attrs
    
    def create(self, validated_data):
        """Create user after OTP verification"""
        # Remove OTP-related fields
        validated_data.pop('password_confirm')
        validated_data.pop('otp_code')
        otp_instance = validated_data.pop('_otp_instance')
        
        # Extract user data
        phone_number = validated_data.pop('phone_number')
        password = validated_data.pop('password')
        roles = validated_data.pop('roles', ['CONSUMER'])
        
        # Create user
        user = User.objects.create_user(
            identifier=phone_number,
            password=password,
            roles=roles,
            **validated_data
        )
        
        # Mark user as phone verified
        user.is_verified = True
        user.phone_verified = True
        user.save()
        
        return user


class SMSOTPLoginSerializer(serializers.Serializer):
    """Serializer for phone login with SMS OTP verification"""
    
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number for login"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Account password"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=8,
        required=False,
        help_text="SMS OTP code for two-factor authentication"
    )
    
    def validate_phone_number(self, value):
        """Validate and normalize phone number"""
        clean_phone = re.sub(r'[\s\-()]', '', value)
        
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +233201234567)"
            )
        
        return clean_phone
    
    def validate(self, attrs):
        """Validate login credentials and OTP if provided"""
        phone_number = attrs['phone_number']
        password = attrs['password']
        otp_code = attrs.get('otp_code')
        
        # Check if user exists
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")
        
        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")
        
        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")
        
        # Verify OTP if provided (for 2FA)
        if otp_code:
            service = SMSOTPService()
            success, message, otp = service.verify_otp(
                phone_number=phone_number,
                otp_code=otp_code,
                purpose='login'
            )
            if not success:
                raise serializers.ValidationError({
                    'otp_code': message
                })
        
        attrs['user'] = user
        return attrs


class SMSOTPPasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset with SMS OTP verification"""
    
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number for password reset"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=8,
        help_text="SMS OTP code"
    )
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="New password"
    )
    new_password_confirm = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="New password confirmation"
    )
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        clean_phone = re.sub(r'[\s\-()]', '', value)
        
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '+233' + clean_phone[1:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
            raise serializers.ValidationError(
                "Invalid phone number format. Please use international format (e.g., +233201234567)"
            )
        
        # Check if user exists
        if not User.objects.filter(phone_number=clean_phone).exists():
            raise serializers.ValidationError("User with this phone number does not exist")
        
        return clean_phone
    
    def validate(self, attrs):
        """Validate password reset data"""
        # Check password confirmation
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match'
            })
        
        # Verify SMS OTP
        phone_number = attrs['phone_number']
        otp_code = attrs['otp_code']
        
        service = SMSOTPService()
        success, message, otp = service.verify_otp(
            phone_number=phone_number,
            otp_code=otp_code,
            purpose='password_reset'
        )
        
        if not success:
            raise serializers.ValidationError({
                'otp_code': message
            })
        
        # Get user
        user = User.objects.get(phone_number=phone_number)
        attrs['user'] = user
        
        return attrs
    
    def save(self):
        """Reset user password"""
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return user
