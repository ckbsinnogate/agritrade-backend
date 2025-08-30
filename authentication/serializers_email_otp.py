"""
AgriConnect Email OTP Serializers
Professional serializers for email OTP functionality
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from .models_otp import EmailOTP, EmailOTPAttempt
from .services_otp import EmailOTPService

User = get_user_model()


class EmailOTPRequestSerializer(serializers.Serializer):
    """Serializer for requesting an email OTP"""
    
    email = serializers.EmailField(
        validators=[EmailValidator()],
        help_text="Email address to send OTP to"
    )
    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default='registration',
        help_text="Purpose of the OTP"
    )
    
    def validate_email(self, value):
        """Validate email address"""
        return value.lower().strip()
    
    class Meta:
        fields = ['email', 'purpose']


class EmailOTPVerifySerializer(serializers.Serializer):
    """Serializer for verifying email OTP"""
    
    email = serializers.EmailField(
        validators=[EmailValidator()],
        help_text="Email address used for OTP"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=10,
        help_text="OTP code received via email"
    )
    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default='registration',
        help_text="Purpose of the OTP"
    )
    
    def validate_email(self, value):
        """Validate email address"""
        return value.lower().strip()
    
    def validate_otp_code(self, value):
        """Validate OTP code format"""
        # Remove any whitespace and ensure it's digits only for numeric OTPs
        cleaned = value.strip()
        if cleaned.isdigit():
            return cleaned
        # For alphanumeric OTPs, convert to uppercase
        return cleaned.upper()
    
    class Meta:
        fields = ['email', 'otp_code', 'purpose']


class EmailOTPResendSerializer(serializers.Serializer):
    """Serializer for resending email OTP"""
    
    email = serializers.EmailField(
        validators=[EmailValidator()],
        help_text="Email address to resend OTP to"
    )
    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default='registration',
        help_text="Purpose of the OTP"
    )
    
    def validate_email(self, value):
        """Validate email address"""
        return value.lower().strip()
    
    class Meta:
        fields = ['email', 'purpose']


class EmailOTPStatusSerializer(serializers.ModelSerializer):
    """Serializer for OTP status information"""
    
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_valid = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    attempts_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailOTP
        fields = [
            'id', 'email', 'purpose', 'purpose_display', 
            'status', 'status_display', 'created_at', 'expires_at',
            'attempts_count', 'max_attempts', 'is_valid', 'is_expired',
            'time_remaining', 'attempts_remaining'
        ]
        read_only_fields = fields
    
    def get_is_valid(self, obj):
        """Check if OTP is currently valid"""
        return obj.is_valid()
    
    def get_is_expired(self, obj):
        """Check if OTP has expired"""
        return obj.is_expired()
    
    def get_time_remaining(self, obj):
        """Get remaining time in seconds"""
        if obj.is_expired():
            return 0
        from django.utils import timezone
        remaining = obj.expires_at - timezone.now()
        return max(0, int(remaining.total_seconds()))
    
    def get_attempts_remaining(self, obj):
        """Get remaining verification attempts"""
        return max(0, obj.max_attempts - obj.attempts_count)


class EmailOTPAttemptSerializer(serializers.ModelSerializer):
    """Serializer for OTP verification attempts"""
    
    class Meta:
        model = EmailOTPAttempt
        fields = [
            'attempted_code', 'is_successful', 'attempted_at',
            'response_time_ms', 'failure_reason'
        ]
        read_only_fields = fields


class EmailOTPRegistrationSerializer(serializers.Serializer):
    """Serializer for email registration with OTP verification"""
    
    email = serializers.EmailField(
        validators=[EmailValidator()],
        help_text="Email address for registration"
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Password for the account"
    )
    password_confirm = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Password confirmation"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=10,
        help_text="OTP code received via email"
    )
    first_name = serializers.CharField(
        max_length=50,
        required=False,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        max_length=50,
        required=False,
        help_text="User's last name"
    )
    roles = serializers.ListField(
        child=serializers.CharField(),
        default=['CONSUMER'],
        help_text="User roles (e.g., ['FARMER', 'PROCESSOR'])"
    )
    
    def validate_email(self, value):
        """Validate email address"""
        email = value.lower().strip()
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        
        return email
    
    def validate(self, attrs):
        """Validate the entire registration data"""
        # Check password confirmation
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        
        # Verify OTP
        email = attrs['email']
        otp_code = attrs['otp_code']
        
        service = EmailOTPService()
        success, message, otp = service.verify_otp(
            email=email,
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
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        roles = validated_data.pop('roles', ['CONSUMER'])
        
        # Create user
        user = User.objects.create_user(
            identifier=email,
            password=password,
            roles=roles,
            **validated_data
        )
        
        # Mark user as email verified
        user.is_verified = True
        user.email_verified = True
        user.save()
        
        return user


class EmailOTPLoginSerializer(serializers.Serializer):
    """Serializer for email login with OTP verification"""
    
    email = serializers.EmailField(
        validators=[EmailValidator()],
        help_text="Email address for login"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Account password"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=10,
        required=False,
        help_text="OTP code for two-factor authentication"
    )
    
    def validate_email(self, value):
        """Validate email address"""
        return value.lower().strip()
    
    def validate(self, attrs):
        """Validate login credentials and OTP if provided"""
        email = attrs['email']
        password = attrs['password']
        otp_code = attrs.get('otp_code')
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'User with this email does not exist'
            })
        
        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': 'Invalid password'
            })
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'Account is deactivated'
            })
        
        # If OTP is provided, verify it
        if otp_code:
            service = EmailOTPService()
            success, message, otp = service.verify_otp(
                email=email,
                otp_code=otp_code,
                purpose='login'
            )
            
            if not success:
                raise serializers.ValidationError({
                    'otp_code': message
                })
        
        attrs['user'] = user
        return attrs


class EmailOTPPasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset with OTP verification"""
    
    email = serializers.EmailField(
        validators=[EmailValidator()],
        help_text="Email address for password reset"
    )
    otp_code = serializers.CharField(
        min_length=4,
        max_length=10,
        help_text="OTP code received via email"
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
    
    def validate_email(self, value):
        """Validate email address"""
        email = value.lower().strip()
        
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email does not exist")
        
        return email
    
    def validate(self, attrs):
        """Validate password reset data"""
        # Check password confirmation
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match'
            })
        
        # Verify OTP
        email = attrs['email']
        otp_code = attrs['otp_code']
        
        service = EmailOTPService()
        success, message, otp = service.verify_otp(
            email=email,
            otp_code=otp_code,
            purpose='password_reset'
        )
        
        if not success:
            raise serializers.ValidationError({
                'otp_code': message
            })
        
        # Get user
        user = User.objects.get(email=email)
        attrs['user'] = user
        
        return attrs
    
    def save(self):
        """Reset user password"""
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return user