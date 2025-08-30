"""
AgriConnect Communications Models
Enhanced SMS & OTP Integration System (PRD Section 4.7)

Features:
- Multi-language SMS support (25+ African languages)
- USSD integration for feature phones
- WhatsApp Business API integration
- Bulk messaging capabilities
- Advanced OTP management
- Communication preferences
- Performance analytics
- Integration with AVRSMS API
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()

class SMSProvider(models.Model):
    """SMS service providers for different regions"""
    PROVIDER_CHOICES = [
        ('avrsms', 'AVRSMS (Default)'),
        ('hubtel', 'Hubtel (Ghana)'),
        ('africas_talking', 'Africa\'s Talking (Pan-African)'),
        ('twilio', 'Twilio (Global)'),
        ('infobip', 'Infobip (Europe/Africa)'),
        ('termii', 'Termii (Nigeria)'),
        ('clickatell', 'Clickatell (Global)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    provider_code = models.CharField(max_length=20, choices=PROVIDER_CHOICES, unique=True)
    api_endpoint = models.URLField(default='https://api.avrsms.com/api/SendSMS')
    supported_countries = models.JSONField(default=list, help_text="List of ISO country codes")
    cost_per_sms = models.DecimalField(max_digits=6, decimal_places=4, default=0.02)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, help_text="1=highest priority")
    configuration = models.JSONField(default=dict, help_text="API keys and settings")
    daily_limit = models.IntegerField(default=10000, help_text="Daily SMS sending limit")
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=95.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'name']
        verbose_name = "SMS Provider"
        verbose_name_plural = "SMS Providers"
    
    def __str__(self):
        return f"{self.name} ({self.provider_code})"

class SMSTemplate(models.Model):
    """SMS message templates for different purposes and languages"""
    TEMPLATE_TYPES = [
        ('otp', 'OTP Verification'),
        ('order_confirmation', 'Order Confirmation'),
        ('payment_notification', 'Payment Notification'),
        ('delivery_update', 'Delivery Update'),
        ('price_alert', 'Price Alert'),
        ('weather_alert', 'Weather Alert'),
        ('marketing', 'Marketing Campaign'),
        ('reminder', 'Reminder'),
        ('welcome', 'Welcome Message'),
        ('password_reset', 'Password Reset'),
    ]
    
    LANGUAGES = [
        ('en', 'English'),
        ('tw', 'Twi (Ghana)'),
        ('ga', 'Ga (Ghana)'),
        ('ee', 'Ewe (Ghana/Togo)'),
        ('ha', 'Hausa (West Africa)'),
        ('yo', 'Yoruba (Nigeria)'),
        ('ig', 'Igbo (Nigeria)'),
        ('sw', 'Swahili (East Africa)'),
        ('fr', 'French (West/Central Africa)'),
        ('ar', 'Arabic (North Africa)'),
        ('am', 'Amharic (Ethiopia)'),
        ('zu', 'Zulu (South Africa)'),
        ('xh', 'Xhosa (South Africa)'),
        ('af', 'Afrikaans (South Africa)'),
        ('pt', 'Portuguese (Angola/Mozambique)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    language = models.CharField(max_length=10, choices=LANGUAGES)
    country = models.CharField(max_length=2, blank=True, help_text="ISO country code")
    
    subject = models.CharField(max_length=160, blank=True)
    content = models.TextField(help_text="SMS content with variable placeholders {variable_name}")
    variables = models.JSONField(default=list, help_text="List of variable names used in template")
    character_count = models.IntegerField(editable=False)
    
    # Default templates
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'language', 'country']
        ordering = ['template_type', 'language', 'name']
        verbose_name = "SMS Template"
        verbose_name_plural = "SMS Templates"
    
    def save(self, *args, **kwargs):
        self.character_count = len(self.content)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.language})"

    @classmethod
    def get_default_templates(cls):
        """Get default SMS templates for system setup"""
        return {
            'otp_en': {
                'name': 'OTP Verification - English',
                'template_type': 'otp',
                'language': 'en',
                'content': 'Your AgriConnect verification code is: {otp_code}. Valid for {validity_minutes} minutes. Do not share this code.',
                'variables': ['otp_code', 'validity_minutes'],
                'is_default': True
            },
            'otp_tw': {
                'name': 'OTP Verification - Twi',
                'template_type': 'otp',
                'language': 'tw', 
                'content': 'Wo AgriConnect verification code ne: {otp_code}. Ɛwɔ hɔ sima {validity_minutes}. Nkyɛ obi saa code yi.',
                'variables': ['otp_code', 'validity_minutes'],
                'is_default': True
            },
            'order_confirmation_en': {
                'name': 'Order Confirmation - English',
                'template_type': 'order_confirmation',
                'language': 'en',
                'content': 'Order #{order_id} confirmed! Total: {currency}{amount}. Delivery: {delivery_date}. Track: agriconnect.com/track/{order_id}',
                'variables': ['order_id', 'currency', 'amount', 'delivery_date'],
                'is_default': True
            },
            'payment_notification_en': {
                'name': 'Payment Notification - English', 
                'template_type': 'payment_notification',
                'language': 'en',
                'content': 'Payment of {currency}{amount} received for Order #{order_id}. Thank you for choosing AgriConnect!',
                'variables': ['currency', 'amount', 'order_id'],
                'is_default': True
            },
            'welcome_en': {
                'name': 'Welcome Message - English',
                'template_type': 'welcome',
                'language': 'en',
                'content': 'Welcome to AgriConnect! Your account is now active. Start trading with farmers across Africa. Visit: agriconnect.com',
                'variables': [],
                'is_default': True
            }
        }

class SMSMessage(models.Model):
    """Individual SMS messages sent through the platform"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_phone = models.CharField(max_length=20, validators=[
        RegexValidator(r'^\+[1-9]\d{1,14}$', 'Enter a valid international phone number')
    ])
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_id = models.CharField(max_length=20, default='AgriConnect')
    
    # Message details
    message_type = models.CharField(max_length=30)
    template = models.ForeignKey(SMSTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=160, blank=True)
    content = models.TextField()
    language = models.CharField(max_length=10, default='en')
    
    # Delivery tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    provider = models.ForeignKey(SMSProvider, on_delete=models.SET_NULL, null=True)
    provider_message_id = models.CharField(max_length=100, blank=True)
    provider_response = models.JSONField(default=dict)
    failure_reason = models.TextField(blank=True)
    
    # Timing
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Costs
    cost = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # Campaign tracking
    campaign_id = models.UUIDField(null=True, blank=True)
    batch_id = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_phone', 'status']),
            models.Index(fields=['campaign_id']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = "SMS Message"
        verbose_name_plural = "SMS Messages"
    
    def __str__(self):
        return f"SMS to {self.recipient_phone} - {self.status}"

class OTPCode(models.Model):
    """Enhanced OTP management with multi-purpose support"""
    PURPOSE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
        ('phone_verification', 'Phone Verification'),
        ('email_verification', 'Email Verification'),
        ('transaction', 'Transaction Confirmation'),
        ('order_confirmation', 'Order Confirmation'),
        ('payment_verification', 'Payment Verification'),
        ('profile_update', 'Profile Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, blank=True, validators=[
        RegexValidator(r'^\+[1-9]\d{1,14}$', 'Enter a valid international phone number')
    ])
    email = models.EmailField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                            related_name='communication_otp_codes')
    
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    
    # Expiry and limits
    expires_at = models.DateTimeField()
    attempts_count = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    
    # Status
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, help_text="Additional context data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'purpose', 'expires_at']),
            models.Index(fields=['email', 'purpose', 'expires_at']),
        ]
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired() and self.attempts_count < self.max_attempts
    
    def __str__(self):
        identifier = self.phone_number or self.email
        return f"OTP {self.code} for {identifier} ({self.purpose})"

class CommunicationPreference(models.Model):
    """User communication preferences and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='communication_preferences')
    
    # SMS preferences
    sms_enabled = models.BooleanField(default=True)
    sms_order_updates = models.BooleanField(default=True)
    sms_payment_notifications = models.BooleanField(default=True)
    sms_price_alerts = models.BooleanField(default=False)
    sms_weather_alerts = models.BooleanField(default=True)
    sms_marketing = models.BooleanField(default=False)
    
    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_order_updates = models.BooleanField(default=True)
    email_payment_notifications = models.BooleanField(default=True)
    email_newsletters = models.BooleanField(default=False)
    email_marketing = models.BooleanField(default=False)
    
    # WhatsApp preferences
    whatsapp_enabled = models.BooleanField(default=False)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    whatsapp_order_updates = models.BooleanField(default=False)
    whatsapp_support = models.BooleanField(default=False)
    
    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_order_updates = models.BooleanField(default=True)
    push_chat_messages = models.BooleanField(default=True)
    push_marketing = models.BooleanField(default=False)
    
    # Language and timing
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='Africa/Accra')
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Communication Preference"
        verbose_name_plural = "Communication Preferences"
    
    def __str__(self):
        return f"Communication preferences for {self.user.username}"

class CommunicationLog(models.Model):
    """Log of all communications sent to users"""
    COMMUNICATION_TYPES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('whatsapp', 'WhatsApp'),
        ('ussd', 'USSD'),        ('voice', 'Voice Call'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
      # Frontend compatibility fields
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_communications')
    recipient_phone = models.CharField(max_length=20, blank=True, help_text="Recipient phone number")
    message_content = models.TextField(blank=True, default='', help_text="Full message content")
    message_type = models.CharField(max_length=30, default='general', help_text="Type of message")
    delivery_status = models.CharField(max_length=20, default='pending', help_text="Delivery status")
    
    # Original fields for backward compatibility
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES, default='sms')
    recipient = models.CharField(max_length=255, help_text="Phone, email, or device ID")
    
    purpose = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, default='pending')
    content_snippet = models.TextField(max_length=200, help_text="First 200 chars of content", blank=True)
    
    # Reference to original message
    sms_message = models.ForeignKey(SMSMessage, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    cost = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # AI Enhancement Fields
    ai_enhanced = models.BooleanField(default=False, help_text="Whether AI was used to enhance this communication")
    ai_optimization_score = models.FloatField(null=True, blank=True, help_text="AI-predicted engagement score (0-100)")
    ai_timing_optimized = models.BooleanField(default=False, help_text="Whether timing was AI-optimized")
    ai_content_generated = models.BooleanField(default=False, help_text="Whether content was AI-generated")
    ai_translated = models.BooleanField(default=False, help_text="Whether message was AI-translated")
    ai_model_used = models.CharField(max_length=100, blank=True, help_text="AI model used for processing")
    optimization_metadata = models.JSONField(default=dict, help_text="AI optimization metadata")
    
    # Enhanced Analytics Fields    read_confirmed = models.BooleanField(default=False, help_text="Whether message was confirmed as read")
    response_received = models.BooleanField(default=False, help_text="Whether farmer responded")
    engagement_score = models.FloatField(null=True, blank=True, help_text="Actual engagement score")
    response_time_minutes = models.IntegerField(null=True, blank=True, help_text="Response time in minutes")

    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the message was sent")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'communication_type']),
            models.Index(fields=['sent_at']),
        ]
        verbose_name = "Communication Log"
        verbose_name_plural = "Communication Logs"
    
    def __str__(self):
        return f"{self.communication_type.upper()} to {self.recipient} - {self.status}"


class AIMessageOptimization(models.Model):
    """Track AI message optimizations and their effectiveness"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Original Message Info
    original_content = models.TextField(help_text="Original message content")
    optimized_content = models.TextField(help_text="AI-optimized content")
    message_type = models.CharField(max_length=50, help_text="Type of message")
    
    # Farmer Context
    farmer_profile = models.JSONField(help_text="Farmer profile used for optimization")
    target_language = models.CharField(max_length=20, default='English')
    
    # AI Processing Info
    ai_model_used = models.CharField(max_length=100, help_text="AI model used")
    optimization_score = models.FloatField(help_text="AI-predicted engagement score")
    processing_time_ms = models.IntegerField(help_text="Processing time in milliseconds")
    
    # Effectiveness Tracking
    actual_engagement = models.FloatField(null=True, blank=True, help_text="Actual engagement measured")
    delivery_success = models.BooleanField(default=False)
    read_confirmed = models.BooleanField(default=False)
    response_received = models.BooleanField(default=False)
    
    # Metadata
    improvements_made = models.JSONField(default=list, help_text="List of improvements made by AI")
    timing_optimized = models.BooleanField(default=False)
    optimal_send_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_message_optimization'
        indexes = [
            models.Index(fields=['message_type', 'created_at']),
            models.Index(fields=['ai_model_used']),
            models.Index(fields=['optimization_score']),
        ]


class FarmerCommunicationProfile(models.Model):
    """AI-enhanced farmer communication preferences and patterns"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer_id = models.IntegerField(unique=True, help_text="Reference to farmer")
    
    # Communication Preferences (AI-learned)
    preferred_message_length = models.CharField(
        max_length=20, 
        choices=[('short', 'Short (< 80 chars)'), ('medium', 'Medium (80-160 chars)'), ('long', 'Long (> 160 chars)')],
        default='medium'
    )
    preferred_communication_times = models.JSONField(
        default=list, 
        help_text="Preferred hours for receiving messages"
    )
    language_complexity_level = models.CharField(
        max_length=20,
        choices=[('simple', 'Simple'), ('medium', 'Medium'), ('advanced', 'Advanced')],
        default='medium'
    )
    
    # Engagement Patterns (AI-tracked)
    average_response_time_minutes = models.FloatField(null=True, blank=True)
    engagement_rate = models.FloatField(default=0.0, help_text="Overall engagement rate (0-100)")
    preferred_message_types = models.JSONField(default=list, help_text="Message types that get best engagement")
    
    # AI Optimization Settings
    ai_optimization_enabled = models.BooleanField(default=True)
    timing_optimization_enabled = models.BooleanField(default=True)
    content_personalization_enabled = models.BooleanField(default=True)
    
    # Learning Metadata
    total_messages_received = models.IntegerField(default=0)
    total_responses_sent = models.IntegerField(default=0)
    last_engagement_analysis = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farmer_communication_profile'
        indexes = [
            models.Index(fields=['farmer_id']),
            models.Index(fields=['engagement_rate']),
        ]


class IntelligentResponse(models.Model):
    """Track AI-generated intelligent responses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Input Message
    incoming_message = models.TextField(help_text="Original farmer message")
    farmer_id = models.IntegerField(help_text="Farmer who sent the message")
    message_language = models.CharField(max_length=20, default='English')
    
    # AI Analysis
    detected_intent = models.CharField(max_length=100, help_text="AI-detected intent")
    urgency_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    topic_category = models.CharField(max_length=50, help_text="Message topic category")
    
    # AI Response
    ai_response = models.TextField(help_text="AI-generated response")
    confidence_score = models.FloatField(help_text="AI confidence in response (0-100)")
    requires_human_intervention = models.BooleanField(default=False)
    
    # Processing Info
    ai_model_used = models.CharField(max_length=100)
    processing_time_ms = models.IntegerField()
    
    # Outcome Tracking
    response_sent = models.BooleanField(default=False)
    farmer_satisfied = models.BooleanField(null=True, blank=True)
    escalated_to_human = models.BooleanField(default=False)
    follow_up_needed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'intelligent_response'
        indexes = [
            models.Index(fields=['farmer_id', 'created_at']),
            models.Index(fields=['detected_intent']),
            models.Index(fields=['urgency_level']),
        ]


class CommunicationAnalytics(models.Model):
    """Aggregate communication analytics and AI performance metrics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Time Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    period_type = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='daily'
    )
    
    # Overall Metrics
    total_messages_sent = models.IntegerField(default=0)
    ai_enhanced_messages = models.IntegerField(default=0)
    delivery_success_rate = models.FloatField(default=0.0)
    engagement_rate = models.FloatField(default=0.0)
    
    # AI Performance Metrics
    avg_optimization_score = models.FloatField(null=True, blank=True)
    ai_accuracy_rate = models.FloatField(null=True, blank=True)
    avg_processing_time_ms = models.FloatField(null=True, blank=True)
    
    # Message Type Breakdown
    message_type_stats = models.JSONField(default=dict, help_text="Performance by message type")
    
    # Timing Insights
    best_sending_hours = models.JSONField(default=list, help_text="Most effective sending hours")
    engagement_by_hour = models.JSONField(default=dict, help_text="Engagement rates by hour")
    
    # AI Model Performance
    model_performance_stats = models.JSONField(default=dict, help_text="Performance by AI model")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'communication_analytics'
        unique_together = ['period_start', 'period_end', 'period_type']
        indexes = [
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['period_type']),
        ]


class AITranslationCache(models.Model):
    """Cache AI translations to improve performance and reduce costs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Translation Key
    source_text_hash = models.CharField(max_length=64, help_text="SHA256 hash of source text")
    source_language = models.CharField(max_length=20, default='English')
    target_language = models.CharField(max_length=20)
    context_type = models.CharField(max_length=50, help_text="Agricultural context type")
    
    # Translation Data
    source_text = models.TextField()
    translated_text = models.TextField()
    confidence_score = models.FloatField()
    ai_model_used = models.CharField(max_length=100)
    
    # Usage Tracking
    times_used = models.IntegerField(default=1)
    last_used = models.DateTimeField(auto_now=True)
    
    # Quality Metrics
    human_approved = models.BooleanField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_translation_cache'
        unique_together = ['source_text_hash', 'target_language', 'context_type']
        indexes = [
            models.Index(fields=['source_text_hash']),
            models.Index(fields=['target_language']),
            models.Index(fields=['times_used']),
        ]
