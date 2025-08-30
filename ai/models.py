"""
AgriConnect AI Models
OpenAI-powered agricultural intelligence models
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json

User = get_user_model()

class AIConversation(models.Model):
    """Track farmer conversations with AI assistant"""
    
    CONVERSATION_TYPES = [
        ('crop_advisory', 'Crop Advisory'),
        ('disease_detection', 'Disease Detection'),
        ('market_inquiry', 'Market Inquiry'),
        ('general_farming', 'General Farming'),
        ('weather_query', 'Weather Query'),
        ('pest_control', 'Pest Control'),
        ('soil_management', 'Soil Management'),
        ('irrigation', 'Irrigation'),
        ('harvesting', 'Harvesting'),
        ('storage', 'Storage'),
    ]
    
    LANGUAGES = [
        ('en', 'English'),
        ('tw', 'Twi'),
        ('ga', 'Ga'),
        ('ee', 'Ewe'),
        ('ha', 'Hausa'),
        ('yo', 'Yoruba'),
        ('ig', 'Igbo'),
        ('fr', 'French'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    
    # Conversation Details
    conversation_type = models.CharField(max_length=30, choices=CONVERSATION_TYPES)
    language = models.CharField(max_length=5, choices=LANGUAGES, default='en')
    farmer_question = models.TextField(help_text="Original farmer question")
    ai_response = models.TextField(help_text="AI-generated response")
    
    # Context Information
    farmer_location = models.CharField(max_length=100, blank=True)
    crop_context = models.CharField(max_length=100, blank=True)
    season_context = models.CharField(max_length=50, blank=True)
    
    # AI Processing Metadata
    openai_model_used = models.CharField(max_length=50, default='gpt-3.5-turbo')
    tokens_used = models.IntegerField(default=0)
    processing_time_ms = models.IntegerField(default=0)
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Feedback and Quality
    farmer_satisfied = models.BooleanField(null=True, blank=True)
    farmer_rating = models.IntegerField(null=True, blank=True, help_text="1-5 rating")
    follow_up_needed = models.BooleanField(default=False)
    escalated_to_human = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'conversation_type']),
            models.Index(fields=['language', 'created_at']),
            models.Index(fields=['farmer_satisfied']),
        ]
        verbose_name = "AI Conversation"
        verbose_name_plural = "AI Conversations"
    
    def __str__(self):
        return f"AI Chat: {self.user.username} - {self.conversation_type}"

class CropAdvisory(models.Model):
    """AI-generated crop recommendations and farming advice"""
    
    CROP_CATEGORIES = [
        ('cereals', 'Cereals (Maize, Rice, Millet)'),
        ('legumes', 'Legumes (Beans, Cowpea, Soybean)'),
        ('roots_tubers', 'Roots & Tubers (Cassava, Yam, Potato)'),
        ('vegetables', 'Vegetables (Tomato, Onion, Pepper)'),
        ('fruits', 'Fruits (Mango, Citrus, Plantain)'),
        ('cash_crops', 'Cash Crops (Cocoa, Coffee, Cotton)'),
        ('spices', 'Spices & Herbs'),
    ]
    
    SEASONS = [
        ('major_rainy', 'Major Rainy Season (April-July)'),
        ('minor_rainy', 'Minor Rainy Season (September-November)'),
        ('dry_season', 'Dry Season (December-March)'),
        ('harmattan', 'Harmattan Period (December-February)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='crop_advisories')
    
    # Farmer Context
    farmer_location = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    soil_type = models.CharField(max_length=100, blank=True)
    farm_size_acres = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    budget_ghs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    experience_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('experienced', 'Experienced'),
        ('expert', 'Expert')
    ], default='intermediate')
    
    # Season and Timing
    target_season = models.CharField(max_length=20, choices=SEASONS)
    planting_month = models.CharField(max_length=20, blank=True)
    
    # AI Recommendations
    recommended_crops = models.JSONField(default=list, help_text="List of recommended crops with details")
    expected_yields = models.JSONField(default=dict, help_text="Expected yields for each crop")
    investment_requirements = models.JSONField(default=dict, help_text="Investment needed per crop")
    market_projections = models.JSONField(default=dict, help_text="Price and demand projections")
    risk_assessment = models.JSONField(default=dict, help_text="Risk factors and mitigation")
    
    # Implementation Details
    planting_schedule = models.JSONField(default=dict, help_text="Month-by-month planting schedule")
    resource_requirements = models.JSONField(default=dict, help_text="Seeds, fertilizer, labor requirements")
    
    # AI Metadata
    confidence_level = models.FloatField(default=0.0, help_text="AI confidence in recommendations (0-100)")
    data_sources_used = models.JSONField(default=list, help_text="Data sources used for recommendations")
    
    # Follow-up and Success Tracking
    farmer_implemented = models.BooleanField(null=True, blank=True)
    implementation_feedback = models.TextField(blank=True)
    actual_results = models.JSONField(default=dict, blank=True, help_text="Actual yields and outcomes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Crop Advisory"
        verbose_name_plural = "Crop Advisories"
    
    def __str__(self):
        return f"Crop Advisory: {self.farmer_location} - {self.target_season}"

class DiseaseDetection(models.Model):
    """AI-powered plant disease detection and treatment recommendations"""
    
    CROP_TYPES = [
        ('maize', 'Maize/Corn'),
        ('rice', 'Rice'),
        ('tomato', 'Tomato'),
        ('cassava', 'Cassava'),
        ('cocoa', 'Cocoa'),
        ('plantain', 'Plantain'),
        ('yam', 'Yam'),
        ('beans', 'Beans'),
        ('pepper', 'Pepper'),
        ('onion', 'Onion'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='disease_detections')
    
    # Plant Information
    crop_type = models.CharField(max_length=30, choices=CROP_TYPES)
    plant_age = models.CharField(max_length=50, blank=True)
    growth_stage = models.CharField(max_length=50, blank=True)
    
    # Symptom Description
    farmer_description = models.TextField(help_text="Farmer's description of symptoms")
    symptoms_observed = models.JSONField(default=list, help_text="List of observed symptoms")
    affected_plant_parts = models.JSONField(default=list, help_text="Parts of plant affected")
    
    # Environmental Context
    weather_conditions = models.CharField(max_length=100, blank=True)
    humidity_level = models.CharField(max_length=50, blank=True)
    temperature_range = models.CharField(max_length=50, blank=True)
    recent_treatments = models.TextField(blank=True)
    
    # AI Diagnosis
    identified_diseases = models.JSONField(default=list, help_text="Potential diseases identified")
    primary_diagnosis = models.CharField(max_length=100, blank=True)
    confidence_percentage = models.FloatField(default=0.0)
    severity_level = models.CharField(max_length=20, choices=SEVERITY_LEVELS, blank=True)
    
    # Treatment Recommendations
    immediate_actions = models.JSONField(default=list, help_text="Immediate treatment steps")
    treatment_plan = models.JSONField(default=dict, help_text="Detailed treatment plan")
    preventive_measures = models.JSONField(default=list, help_text="Prevention strategies")
    cost_estimate_ghs = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Follow-up
    treatment_effectiveness = models.CharField(max_length=20, choices=[
        ('very_effective', 'Very Effective'),
        ('effective', 'Effective'),
        ('partially_effective', 'Partially Effective'),
        ('not_effective', 'Not Effective'),
    ], blank=True)
    farmer_feedback = models.TextField(blank=True)
    
    # Image Analysis (if provided)
    image_analyzed = models.BooleanField(default=False)
    image_analysis_results = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Disease Detection"
        verbose_name_plural = "Disease Detections"
    
    def __str__(self):
        return f"Disease Detection: {self.crop_type} - {self.primary_diagnosis}"

class MarketIntelligence(models.Model):
    """AI-powered market analysis and price predictions"""
    
    PREDICTION_TIMEFRAMES = [
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
    ]
    
    MARKET_REGIONS = [
        ('greater_accra', 'Greater Accra'),
        ('ashanti', 'Ashanti Region'),
        ('northern', 'Northern Region'),
        ('western', 'Western Region'),
        ('eastern', 'Eastern Region'),
        ('central', 'Central Region'),
        ('volta', 'Volta Region'),
        ('upper_east', 'Upper East'),
        ('upper_west', 'Upper West'),
        ('brong_ahafo', 'Brong Ahafo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='market_intelligence')
    
    # Query Details
    crop_name = models.CharField(max_length=100)
    target_region = models.CharField(max_length=30, choices=MARKET_REGIONS)
    prediction_timeframe = models.CharField(max_length=20, choices=PREDICTION_TIMEFRAMES)
    quantity_interested = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Current Market Data
    current_price_ghs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_demand_level = models.CharField(max_length=20, choices=[
        ('very_low', 'Very Low'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], blank=True)
    
    # AI Predictions
    predicted_price_range = models.JSONField(default=dict, help_text="Min/max price predictions")
    demand_forecast = models.JSONField(default=dict, help_text="Demand predictions by month")
    market_trends = models.JSONField(default=list, help_text="Identified market trends")
    price_drivers = models.JSONField(default=list, help_text="Factors affecting price")
    
    # Recommendations
    optimal_selling_period = models.JSONField(default=dict, help_text="Best months to sell")
    market_entry_strategy = models.TextField(blank=True)
    risk_factors = models.JSONField(default=list, help_text="Market risks to consider")
    
    # External Factors
    seasonal_factors = models.JSONField(default=dict, help_text="Seasonal influences")
    export_opportunities = models.JSONField(default=dict, help_text="Export market potential")
    
    # Accuracy Tracking
    prediction_accuracy = models.FloatField(null=True, blank=True, help_text="Actual vs predicted accuracy")
    actual_price_achieved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Market Intelligence"
        verbose_name_plural = "Market Intelligence"
    
    def __str__(self):
        return f"Market Intel: {self.crop_name} - {self.target_region}"

class AIUsageAnalytics(models.Model):
    """Track AI usage patterns and performance metrics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage')
    
    # Usage Metrics
    daily_queries = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    
    # Feature Usage
    crop_advisory_queries = models.IntegerField(default=0)
    disease_detection_queries = models.IntegerField(default=0)
    market_intelligence_queries = models.IntegerField(default=0)
    general_queries = models.IntegerField(default=0)
    
    # Performance Metrics
    average_response_time_ms = models.FloatField(default=0.0)
    satisfaction_score = models.FloatField(default=0.0, help_text="Average user satisfaction (1-5)")
    accuracy_score = models.FloatField(default=0.0, help_text="Accuracy of AI responses (0-100)")
    
    # Usage Patterns
    peak_usage_hours = models.JSONField(default=list, help_text="Hours of peak usage")
    preferred_languages = models.JSONField(default=dict, help_text="Language preferences")
    common_topics = models.JSONField(default=dict, help_text="Most common query topics")
    
    # Date tracking
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = "AI Usage Analytics"
        verbose_name_plural = "AI Usage Analytics"
    
    def __str__(self):
        return f"AI Usage: {self.user.username} - {self.date}"

class AIFeedback(models.Model):
    """Farmer feedback on AI responses for continuous improvement"""
    
    FEEDBACK_TYPES = [
        ('helpful', 'Very Helpful'),
        ('somewhat_helpful', 'Somewhat Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('incorrect', 'Incorrect Information'),
        ('incomplete', 'Incomplete Response'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.OneToOneField(AIConversation, on_delete=models.CASCADE, related_name='feedback')
    
    # Feedback Details
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    rating = models.IntegerField(help_text="1-5 star rating")
    comments = models.TextField(blank=True)
    
    # Specific Feedback Areas
    accuracy_rating = models.IntegerField(help_text="1-5 rating for accuracy")
    relevance_rating = models.IntegerField(help_text="1-5 rating for relevance")
    clarity_rating = models.IntegerField(help_text="1-5 rating for clarity")
    actionability_rating = models.IntegerField(help_text="1-5 rating for actionable advice")
    
    # Follow-up Actions
    human_review_requested = models.BooleanField(default=False)
    follow_up_needed = models.BooleanField(default=False)
    escalation_required = models.BooleanField(default=False)
    
    # Implementation Results
    farmer_implemented_advice = models.BooleanField(null=True, blank=True)
    implementation_results = models.TextField(blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI Feedback"
        verbose_name_plural = "AI Feedback"
    
    def __str__(self):
        return f"Feedback: {self.feedback_type} - {self.rating}★"
