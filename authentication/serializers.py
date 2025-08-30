"""
AgriConnect Authentication Serializers
Handles dual authentication (phone/email + OTP) as specified in PRD Section 6
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import User, OTPCode, UserProfile
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration with dual authentication support (phone OR email)
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    identifier = serializers.CharField(write_only=True, help_text="Email address or phone number")
    role = serializers.ChoiceField(
        choices=['farmer', 'consumer', 'processor', 'institution'],
        default='consumer',
        help_text="User role: farmer, consumer, processor, institution"
    )

    class Meta:
        model = User
        fields = [
            'identifier', 'password', 'password_confirm', 'first_name', 
            'last_name', 'role', 'country', 'region', 'language'
        ]

    def validate(self, attrs):
        # Check password confirmation
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Validate and process identifier (email or phone)
        identifier = attrs['identifier'].strip()
        
        if '@' in identifier:
            # Email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', identifier):
                raise serializers.ValidationError("Invalid email format")
            attrs['email'] = identifier.lower()
            attrs['phone_number'] = None
        else:
            # Phone validation
            clean_phone = re.sub(r'[\s\-()]', '', identifier)
            if clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+233' + clean_phone[1:]  # Ghana format
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            
            if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
                raise serializers.ValidationError("Invalid phone number format")
            
            attrs['phone_number'] = clean_phone
            attrs['email'] = None
        
        # Check if user already exists
        if attrs.get('email'):
            if User.objects.filter(email=attrs['email']).exists():
                raise serializers.ValidationError("User with this email already exists")
        if attrs.get('phone_number'):
            if User.objects.filter(phone_number=attrs['phone_number']).exists():
                raise serializers.ValidationError("User with this phone number already exists")
        
        return attrs

    def create(self, validated_data):
        # Extract password_confirm and identifier
        validated_data.pop('password_confirm')
        identifier = validated_data.pop('identifier')
        
        # Extract role
        role = validated_data.get('role', 'consumer')
        password = validated_data.pop('password')
        
        # Create user with identifier
        user = User.objects.create_user(
            password=password,
            role=role,
            **validated_data
        )
        
        return user


class OTPVerificationSerializer(serializers.Serializer):
    """
    OTP verification for phone/email
    """
    identifier = serializers.CharField(help_text="Email or phone number")
    otp_code = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        identifier = attrs['identifier'].strip()
        
        # Normalize identifier
        if '@' in identifier:
            identifier = identifier.lower()
        else:
            # Normalize phone number
            clean_phone = re.sub(r'[\s\-()]', '', identifier)
            if clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+233' + clean_phone[1:]
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            identifier = clean_phone
        
        attrs['normalized_identifier'] = identifier
        return attrs


class UserLoginSerializer(serializers.Serializer):
    """
    User login with phone/email + password
    """
    identifier = serializers.CharField(help_text="Email, phone, or username")
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs['identifier']
        password = attrs['password']
        
        # Normalize identifier
        if '@' in identifier:
            identifier = identifier.lower()
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        else:
            # Normalize phone number
            clean_phone = re.sub(r'[\s\-()]', '', identifier)
            if clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+233' + clean_phone[1:]
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            try:
                user = User.objects.get(phone_number=clean_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        
        # Authenticate with username
        authenticated_user = authenticate(username=user.username, password=password)
        
        if not authenticated_user:
            raise serializers.ValidationError("Invalid credentials")
        
        if not authenticated_user.is_active:
            raise serializers.ValidationError("Account is disabled")
        
        attrs['user'] = authenticated_user
        return attrs


class PasswordlessLoginSerializer(serializers.Serializer):
    """
    Passwordless login using OTP
    """
    identifier = serializers.CharField(help_text="Email or phone number")
    otp_code = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        identifier = attrs['identifier'].strip()
        otp_code = attrs['otp_code']
        
        # Normalize identifier
        if '@' in identifier:
            identifier = identifier.lower()
        else:
            clean_phone = re.sub(r'[\s\-()]', '', identifier)
            if clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+233' + clean_phone[1:]
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            identifier = clean_phone
        
        # Find user
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(phone_number=identifier)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        # Verify OTP
        try:
            otp_record = OTPCode.objects.get(
                identifier=identifier,
                code=otp_code,
                is_used=False,
                is_expired=False
            )
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP")
        
        attrs['user'] = user
        attrs['otp_record'] = otp_record
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile information
    """
    roles_display = serializers.SerializerMethodField(read_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 
            'phone_number', 'roles', 'roles_display', 'user_type', 'country', 'region', 
            'language', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'is_verified', 'date_joined']
    
    def get_roles_display(self, obj):
        """Get display names for all user roles"""
        return [role.get_name_display() for role in obj.roles.all()]
    
    def get_user_type(self, obj):
        """Get primary user role as uppercase string for frontend compatibility"""
        # Get the first role if any roles exist
        first_role = obj.roles.first()
        if first_role:
            return first_role.name.upper()
        return 'USER'  # Default fallback


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change user password
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Invalid old password")
        return value


class OTPRequestSerializer(serializers.Serializer):
    """
    Request OTP for phone/email
    """
    identifier = serializers.CharField(help_text="Email or phone number")

    def validate_identifier(self, value):
        identifier = value.strip()
        
        if '@' in identifier:
            # Email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', identifier):
                raise serializers.ValidationError("Invalid email format")
            return identifier.lower()
        else:
            # Phone validation
            clean_phone = re.sub(r'[\s\-()]', '', identifier)
            if clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+233' + clean_phone[1:]
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            
            if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
                raise serializers.ValidationError("Invalid phone number format")
            
            return clean_phone


class PasswordResetSerializer(serializers.Serializer):
    """
    Reset password using OTP
    """
    identifier = serializers.CharField(help_text="Email or phone number")
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Normalize identifier
        identifier = attrs['identifier'].strip()
        if '@' in identifier:
            attrs['normalized_identifier'] = identifier.lower()
        else:
            clean_phone = re.sub(r'[\s\-()]', '', identifier)
            if clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+233' + clean_phone[1:]
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            attrs['normalized_identifier'] = clean_phone
        
        return attrs