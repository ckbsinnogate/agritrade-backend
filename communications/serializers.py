"""
AgriConnect Communications Serializers
Enhanced SMS & OTP Integration System (PRD Section 4.7)
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SMSProvider, SMSTemplate, SMSMessage, OTPCode, 
    CommunicationPreference, CommunicationLog
)

User = get_user_model()

class SMSProviderSerializer(serializers.ModelSerializer):
    """Serializer for SMS providers"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SMSProvider
        fields = [
            'id', 'name', 'api_key', 'api_secret', 'endpoint_url',
            'supported_countries', 'cost_per_sms', 'status', 'status_display',
            'priority', 'retry_count', 'timeout_seconds', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'api_secret': {'write_only': True}
        }

class SMSTemplateSerializer(serializers.ModelSerializer):
    """Serializer for SMS templates"""
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = SMSTemplate
        fields = [
            'id', 'name', 'category', 'category_display', 'language', 
            'language_display', 'template_text', 'variables', 'is_active',
            'character_count', 'sms_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'character_count', 'sms_count']

    def validate_template_text(self, value):
        """Validate template text for variables"""
        if '{' in value and '}' in value:
            # Basic validation for template variables
            pass
        return value

class SMSMessageSerializer(serializers.ModelSerializer):
    """Serializer for SMS messages"""
    recipient_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'recipient', 'recipient_display', 'phone_number', 'message_text',
            'provider', 'provider_name', 'template', 'template_name', 'variables',
            'status', 'status_display', 'provider_message_id', 'cost', 'currency',
            'sent_at', 'delivered_at', 'failed_at', 'retry_count', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'sent_at', 'delivered_at', 'failed_at',
            'provider_message_id', 'cost', 'status'
        ]

    def get_recipient_display(self, obj):
        """Get recipient display name"""
        if obj.recipient:
            return f"{obj.recipient.first_name} {obj.recipient.last_name}".strip()
        return "Anonymous"

class SendSMSSerializer(serializers.Serializer):
    """Serializer for sending SMS"""
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number in international format (e.g., +233201234567)"
    )
    message_text = serializers.CharField(
        max_length=1600,
        help_text="SMS message text (max 1600 characters for concatenated SMS)"
    )
    template_id = serializers.UUIDField(
        required=False,
        help_text="Optional template ID to use for message"
    )
    variables = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Variables to replace in template (if template_id provided)"
    )
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high'],
        default='normal',
        help_text="Message priority"
    )
    schedule_time = serializers.DateTimeField(
        required=False,
        help_text="Schedule message for future delivery"
    )

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code (e.g., +233)")
        
        # Remove + and check if remaining are digits
        digits = value[1:]
        if not digits.isdigit():
            raise serializers.ValidationError("Invalid phone number format")
        
        if len(digits) < 10 or len(digits) > 15:
            raise serializers.ValidationError("Phone number must be between 10-15 digits")
        
        return value

class OTPCodeSerializer(serializers.ModelSerializer):
    """Serializer for OTP codes"""
    user_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    
    class Meta:
        model = OTPCode
        fields = [
            'id', 'user', 'user_display', 'phone_number', 'email', 'code',
            'purpose', 'purpose_display', 'status', 'status_display', 'attempts',
            'max_attempts', 'expires_at', 'verified_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'code', 'verified_at', 'status'
        ]
        extra_kwargs = {
            'code': {'write_only': True}
        }

    def get_user_display(self, obj):
        """Get user display name"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return "Anonymous"

class GenerateOTPSerializer(serializers.Serializer):
    """Serializer for generating OTP"""
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        help_text="Phone number for SMS OTP"
    )
    email = serializers.EmailField(
        required=False,
        help_text="Email address for email OTP"
    )
    purpose = serializers.ChoiceField(
        choices=OTPCode.PURPOSE_CHOICES,
        default='phone_verification',
        help_text="Purpose of OTP"
    )
    length = serializers.IntegerField(
        min_value=4,
        max_value=8,
        default=6,
        help_text="OTP code length (4-8 digits)"
    )
    expires_in_minutes = serializers.IntegerField(
        min_value=1,
        max_value=60,
        default=10,
        help_text="OTP expiry time in minutes"
    )

    def validate(self, data):
        """Validate that either phone_number or email is provided"""
        phone_number = data.get('phone_number')
        email = data.get('email')
        
        if not phone_number and not email:
            raise serializers.ValidationError(
                "Either phone_number or email must be provided"
            )
        
        return data

class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP"""
    otp_id = serializers.UUIDField(
        help_text="OTP ID received when generating OTP"
    )
    code = serializers.CharField(
        max_length=8,
        help_text="OTP code received via SMS or email"
    )

class CommunicationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for communication preferences"""
    user_display = serializers.SerializerMethodField()
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = CommunicationPreference
        fields = [
            'id', 'user', 'user_display', 'language', 'language_display',
            'sms_enabled', 'email_enabled', 'whatsapp_enabled', 'ussd_enabled',
            'marketing_enabled', 'order_notifications', 'payment_notifications',
            'product_updates', 'price_alerts', 'weather_alerts', 'quiet_hours_start',
            'quiet_hours_end', 'timezone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_user_display(self, obj):
        """Get user display name"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

class CommunicationLogSerializer(serializers.ModelSerializer):
    """Serializer for communication logs"""
    user_display = serializers.SerializerMethodField()
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CommunicationLog
        fields = [
            'id', 'user', 'user_display', 'channel', 'channel_display',
            'message_type', 'subject', 'content', 'recipient_info', 'status',
            'status_display', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'cost', 'currency', 'provider_info', 'error_message', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'sent_at', 'delivered_at',
            'opened_at', 'clicked_at'
        ]

    def get_user_display(self, obj):
        """Get user display name"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return "Anonymous"

class BulkSMSSerializer(serializers.Serializer):
    """Serializer for bulk SMS sending"""
    recipients = serializers.ListField(
        child=serializers.CharField(max_length=20),
        min_length=1,
        max_length=1000,
        help_text="List of phone numbers (max 1000)"
    )
    message_text = serializers.CharField(
        max_length=1600,
        help_text="SMS message text"
    )
    template_id = serializers.UUIDField(
        required=False,
        help_text="Optional template ID"
    )
    variables = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Variables for template"
    )
    schedule_time = serializers.DateTimeField(
        required=False,
        help_text="Schedule for future delivery"
    )

    def validate_recipients(self, value):
        """Validate recipient phone numbers"""
        for phone in value:
            if not phone.startswith('+'):
                raise serializers.ValidationError(
                    f"Phone number {phone} must include country code"
                )
        return value

class SMSAnalyticsSerializer(serializers.Serializer):
    """Serializer for SMS analytics"""
    total_sent = serializers.IntegerField(read_only=True)
    total_delivered = serializers.IntegerField(read_only=True)
    total_failed = serializers.IntegerField(read_only=True)
    delivery_rate = serializers.FloatField(read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    average_cost_per_sms = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    popular_templates = serializers.ListField(read_only=True)
    daily_stats = serializers.ListField(read_only=True)