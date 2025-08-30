"""
AgriConnect Processing Recipes Serializers
Comprehensive serializers for recipe sharing API

Features:
- Recipe CRUD operations
- Rating and review system
- Usage tracking and analytics
- Processor profile management
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg
from .models import (
    ProcessingRecipe, RecipeRating, RecipeUsageLog, 
    RecipeComment, ProcessorProfile
)

User = get_user_model()


class ProcessorProfileSerializer(serializers.ModelSerializer):
    """Serializer for processor profiles"""
    
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessorProfile
        fields = [
            'id', 'user', 'user_details', 'business_name', 'business_registration_number',
            'processor_type', 'specializations', 'processing_capabilities',
            'daily_processing_capacity', 'capacity_unit', 'equipment_list',
            'certifications', 'health_permits', 'quality_standards',
            'location', 'service_radius_km', 'operating_hours',
            'seasonal_operation', 'operating_seasons', 'is_verified',
            'verified_at', 'total_recipes_shared', 'average_recipe_rating',
            'total_processing_orders', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'is_verified', 'verified_at', 'total_recipes_shared',
            'average_recipe_rating', 'total_processing_orders', 'created_at', 'updated_at'
        ]
    
    def get_user_details(self, obj):
        return {
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email if obj.user.email else None,
            'phone_number': obj.user.phone_number if obj.user.phone_number else None,
        }


class RecipeRatingSerializer(serializers.ModelSerializer):
    """Serializer for recipe ratings"""
    
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeRating
        fields = [
            'id', 'recipe', 'user', 'user_details', 'overall_rating',
            'clarity_rating', 'effectiveness_rating', 'accuracy_rating',
            'review_title', 'review_content', 'actual_yield_achieved',
            'processing_time_actual', 'would_recommend', 'improvement_suggestions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_user_details(self, obj):
        return {
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }


class RecipeCommentSerializer(serializers.ModelSerializer):
    """Serializer for recipe comments"""
    
    user_details = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeComment
        fields = [
            'id', 'recipe', 'user', 'user_details', 'parent',
            'content', 'is_question', 'is_answered', 'helpful_count',
            'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'helpful_count', 'created_at', 'updated_at']
    
    def get_user_details(self, obj):
        return {
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return RecipeCommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []


class RecipeUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for recipe usage logs"""
    
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeUsageLog
        fields = [
            'id', 'recipe', 'user', 'user_details', 'used_at',
            'processing_facility', 'batch_size', 'success',
            'actual_yield', 'processing_time_actual', 'notes', 'issues_encountered'
        ]
        read_only_fields = ['user', 'used_at']
    
    def get_user_details(self, obj):
        return {
            'username': obj.user.username,
            'business_name': getattr(obj.user.processor_profile, 'business_name', '') if hasattr(obj.user, 'processor_profile') else '',
        }


class ProcessingRecipeListSerializer(serializers.ModelSerializer):
    """Serializer for recipe listing (minimal data)"""
    
    processor_details = serializers.SerializerMethodField()
    rating_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessingRecipe
        fields = [
            'id', 'recipe_name', 'processor', 'processor_details',
            'description', 'skill_level_required', 'processing_time_minutes',
            'expected_yield_percentage', 'processing_cost_per_unit',
            'status', 'is_public', 'is_verified', 'times_used',
            'average_rating', 'rating_count', 'rating_summary',
            'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'processor', 'times_used', 'average_rating', 'rating_count',
            'created_at', 'updated_at'
        ]
    
    def get_processor_details(self, obj):
        processor_profile = getattr(obj.processor, 'processor_profile', None)
        return {
            'username': obj.processor.username,
            'first_name': obj.processor.first_name,
            'last_name': obj.processor.last_name,
            'business_name': processor_profile.business_name if processor_profile else '',
            'processor_type': processor_profile.processor_type if processor_profile else '',
            'is_verified': processor_profile.is_verified if processor_profile else False,
        }
    
    def get_rating_summary(self, obj):
        return {
            'average_rating': float(obj.average_rating),
            'rating_count': obj.rating_count,
            'rating_distribution': {
                '5_star': obj.ratings.filter(overall_rating=5).count(),
                '4_star': obj.ratings.filter(overall_rating=4).count(),
                '3_star': obj.ratings.filter(overall_rating=3).count(),
                '2_star': obj.ratings.filter(overall_rating=2).count(),
                '1_star': obj.ratings.filter(overall_rating=1).count(),
            }
        }


class ProcessingRecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed recipe view"""
    
    processor_details = serializers.SerializerMethodField()
    rating_summary = serializers.SerializerMethodField()
    recent_ratings = RecipeRatingSerializer(source='ratings', many=True, read_only=True)
    comments = RecipeCommentSerializer(many=True, read_only=True)
    usage_statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessingRecipe
        fields = [
            'id', 'recipe_name', 'processor', 'processor_details',
            'description', 'skill_level_required', 'processing_time_minutes',
            'input_materials', 'processing_steps', 'equipment_required',
            'output_products', 'expected_yield_percentage', 'quality_checkpoints',
            'quality_standards', 'processing_cost_per_unit', 'labor_hours_required',
            'energy_consumption', 'water_usage_liters', 'waste_generation_kg',
            'certifications_achieved', 'compliance_standards', 'status',
            'is_public', 'is_verified', 'verified_by', 'verification_date',
            'times_used', 'success_rate_percentage', 'average_rating',
            'rating_count', 'tags', 'seasonal_availability', 'available_seasons',
            'rating_summary', 'recent_ratings', 'comments', 'usage_statistics',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'processor', 'is_verified', 'verified_by', 'verification_date',
            'times_used', 'success_rate_percentage', 'average_rating',
            'rating_count', 'created_at', 'updated_at'
        ]
    
    def get_processor_details(self, obj):
        processor_profile = getattr(obj.processor, 'processor_profile', None)
        return {
            'username': obj.processor.username,
            'first_name': obj.processor.first_name,
            'last_name': obj.processor.last_name,
            'business_name': processor_profile.business_name if processor_profile else '',
            'processor_type': processor_profile.processor_type if processor_profile else '',
            'specializations': processor_profile.specializations if processor_profile else [],
            'is_verified': processor_profile.is_verified if processor_profile else False,
            'total_recipes_shared': processor_profile.total_recipes_shared if processor_profile else 0,
            'average_recipe_rating': float(processor_profile.average_recipe_rating) if processor_profile else 0.0,
        }
    
    def get_rating_summary(self, obj):
        ratings = obj.ratings.all()
        return {
            'average_rating': float(obj.average_rating),
            'rating_count': obj.rating_count,
            'rating_distribution': {
                '5_star': ratings.filter(overall_rating=5).count(),
                '4_star': ratings.filter(overall_rating=4).count(),
                '3_star': ratings.filter(overall_rating=3).count(),
                '2_star': ratings.filter(overall_rating=2).count(),
                '1_star': ratings.filter(overall_rating=1).count(),
            },
            'average_clarity': ratings.aggregate(avg=Avg('clarity_rating'))['avg'] or 0,
            'average_effectiveness': ratings.aggregate(avg=Avg('effectiveness_rating'))['avg'] or 0,
            'average_accuracy': ratings.aggregate(avg=Avg('accuracy_rating'))['avg'] or 0,
        }
    
    def get_usage_statistics(self, obj):
        usage_logs = obj.usage_logs.all()
        successful_uses = usage_logs.filter(success=True)
        
        return {
            'total_uses': usage_logs.count(),
            'successful_uses': successful_uses.count(),
            'success_rate': (successful_uses.count() / usage_logs.count() * 100) if usage_logs.count() > 0 else 0,
            'average_actual_yield': successful_uses.aggregate(avg=Avg('actual_yield'))['avg'] or 0,
            'average_processing_time': successful_uses.aggregate(avg=Avg('processing_time_actual'))['avg'] or 0,
        }


class ProcessingRecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipes"""
    
    class Meta:
        model = ProcessingRecipe
        fields = [
            'recipe_name', 'description', 'skill_level_required',
            'processing_time_minutes', 'input_materials', 'processing_steps',
            'equipment_required', 'output_products', 'expected_yield_percentage',
            'quality_checkpoints', 'quality_standards', 'processing_cost_per_unit',
            'labor_hours_required', 'energy_consumption', 'water_usage_liters',
            'waste_generation_kg', 'certifications_achieved', 'compliance_standards',
            'status', 'is_public', 'tags', 'seasonal_availability', 'available_seasons'
        ]
    
    def validate_input_materials(self, value):
        """Validate input materials format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Input materials must be a list")
        
        for material in value:
            if not isinstance(material, dict):
                raise serializers.ValidationError("Each input material must be a dictionary")
            
            required_fields = ['name', 'quantity', 'unit']
            for field in required_fields:
                if field not in material:
                    raise serializers.ValidationError(f"Input material must include '{field}'")
        
        return value
    
    def validate_processing_steps(self, value):
        """Validate processing steps format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Processing steps must be a list")
        
        for i, step in enumerate(value, 1):
            if not isinstance(step, dict):
                raise serializers.ValidationError(f"Step {i} must be a dictionary")
            
            required_fields = ['step_number', 'description']
            for field in required_fields:
                if field not in step:
                    raise serializers.ValidationError(f"Step {i} must include '{field}'")
        
        return value
    
    def validate_output_products(self, value):
        """Validate output products format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Output products must be a list")
        
        for product in value:
            if not isinstance(product, dict):
                raise serializers.ValidationError("Each output product must be a dictionary")
            
            required_fields = ['name', 'expected_quantity', 'unit']
            for field in required_fields:
                if field not in product:
                    raise serializers.ValidationError(f"Output product must include '{field}'")
        
        return value
