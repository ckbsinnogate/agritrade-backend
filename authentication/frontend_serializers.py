"""
Frontend-Compatible Authentication Serializers
Handles field name transformations and frontend compatibility
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import User, OTPCode, UserProfile
import re


class FrontendUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Frontend-compatible user registration serializer
    Accepts frontend field names and transforms them for backend
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=False)
    
    # Support both identifier (backend style) and separate email/phone (frontend style)
    identifier = serializers.CharField(write_only=True, required=False, help_text="Email address or phone number")
    email = serializers.EmailField(write_only=True, required=False, help_text="Email address")
    phone_number = serializers.CharField(write_only=True, required=False, help_text="Phone number")
    
    # Frontend field names
    user_type = serializers.CharField(write_only=True, required=False, help_text="farmer, processor, consumer, institution")
    preferred_language = serializers.CharField(max_length=10, required=False, default='en')
    
    # Backend field names (for compatibility)
    roles = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="User roles: FARMER, CONSUMER, PROCESSOR, INSTITUTION"
    )
    language = serializers.CharField(max_length=10, required=False)

    class Meta:
        model = User
        fields = [
            'identifier', 'email', 'phone_number', 'password', 'password_confirm', 'first_name', 
            'last_name', 'user_type', 'roles', 'country', 'region', 
            'preferred_language', 'language'
        ]

    def validate(self, attrs):
        # Handle password confirmation (optional for frontend compatibility)
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password_confirm and password != password_confirm:
            raise serializers.ValidationError("Passwords do not match")
        
        # Transform frontend fields to backend fields
        self._transform_frontend_fields(attrs)
        
        # Handle identifier vs separate email/phone fields
        identifier = attrs.get('identifier')
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        
        if identifier:
            # Backend style: single identifier field
            identifier = identifier.strip()
            
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
                
            # Set the processed identifier for backend
            attrs['identifier'] = attrs.get('email') or attrs.get('phone_number')
            
        elif email or phone_number:
            # Frontend style: separate email and phone fields
            if email and phone_number:
                raise serializers.ValidationError("Provide either email or phone number, not both")
            
            if email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    raise serializers.ValidationError("Invalid email format")
                attrs['email'] = email.lower()
                attrs['phone_number'] = None
                attrs['identifier'] = email.lower()
            
            if phone_number:
                clean_phone = re.sub(r'[\s\-()]', '', phone_number)
                if clean_phone.startswith('0') and len(clean_phone) == 10:
                    clean_phone = '+233' + clean_phone[1:]  # Ghana format
                elif not clean_phone.startswith('+'):
                    clean_phone = '+' + clean_phone
                
                if not re.match(r'^\+[1-9]\d{1,14}$', clean_phone):
                    raise serializers.ValidationError("Invalid phone number format")
                
                attrs['phone_number'] = clean_phone
                attrs['email'] = None
                attrs['identifier'] = clean_phone
        else:
            raise serializers.ValidationError("Either identifier or email/phone_number is required")
        
        # Check if user already exists
        if attrs.get('email'):
            if User.objects.filter(email=attrs['email']).exists():
                raise serializers.ValidationError("User with this email already exists")
        if attrs.get('phone_number'):
            if User.objects.filter(phone_number=attrs['phone_number']).exists():
                raise serializers.ValidationError("User with this phone number already exists")
        
        return attrs
    
    def _transform_frontend_fields(self, attrs):
        """Transform frontend field names to backend field names"""
        
        # Transform user_type to roles
        user_type = attrs.get('user_type')
        if user_type and not attrs.get('roles'):
            # Map frontend user types to backend roles
            type_mapping = {
                'farmer': 'FARMER',
                'processor': 'PROCESSOR', 
                'consumer': 'CONSUMER',
                'institution': 'INSTITUTION'
            }
            backend_role = type_mapping.get(user_type.lower())
            if backend_role:
                attrs['roles'] = [backend_role]
            else:
                raise serializers.ValidationError(f"Invalid user type: {user_type}")
        elif not attrs.get('roles'):
            # Default role
            attrs['roles'] = ['CONSUMER']
        
        # Transform preferred_language to language
        preferred_language = attrs.get('preferred_language')
        if preferred_language and not attrs.get('language'):
            attrs['language'] = preferred_language
        elif not attrs.get('language'):
            attrs['language'] = 'en'
          # Remove frontend-only fields        attrs.pop('user_type', None)
        attrs.pop('preferred_language', None)
        
        return attrs
    
    def create(self, validated_data):
        # Extract password_confirm and identifier
        validated_data.pop('password_confirm', None)
        
        # Get the identifier that was set during validation
        identifier = validated_data.get('identifier')
        
        # Extract roles and password
        roles = validated_data.pop('roles', ['CONSUMER'])
        password = validated_data.pop('password')
          # Remove fields that shouldn't be passed to create_user
        validated_data.pop('identifier', None)
        validated_data.pop('email', None)
        validated_data.pop('phone_number', None)
        validated_data.pop('user_type', None)  # Remove user_type as it's not a User model field
        validated_data.pop('password_confirm', None)  # Remove password_confirm as it's not needed
        
        # Create user with identifier (correct method signature)
        user = User.objects.create_user(
            identifier=identifier,  # Use identifier parameter, not username
            password=password,
            roles=roles,
            **validated_data
        )
        
        return user


# Keep original serializer for backward compatibility
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Original user registration serializer (backend format)
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    identifier = serializers.CharField(write_only=True, help_text="Email address or phone number")
    roles = serializers.ListField(
        child=serializers.CharField(max_length=50),
        default=['CONSUMER'],
        help_text="User roles: FARMER, CONSUMER, PROCESSOR, INSTITUTION"
    )

    class Meta:
        model = User
        fields = [
            'identifier', 'password', 'password_confirm', 'first_name', 
            'last_name', 'roles', 'country', 'region', 'language'
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
        
        # Extract roles
        roles = validated_data.pop('roles', ['CONSUMER'])
        password = validated_data.pop('password')
        
        # Create user with identifier
        user = User.objects.create_user(
            identifier=identifier,
            password=password,
            roles=roles,
            **validated_data
        )
        
        return user
