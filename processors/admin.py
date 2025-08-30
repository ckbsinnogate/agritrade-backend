"""
AgriConnect Processors Admin
Django admin configuration for processing recipes and processor management
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ProcessingRecipe, RecipeRating, RecipeUsageLog, 
    RecipeComment, ProcessorProfile
)


@admin.register(ProcessorProfile)
class ProcessorProfileAdmin(admin.ModelAdmin):
    list_display = [
        'business_name', 'user', 'processor_type', 'is_verified',
        'total_recipes_shared', 'average_recipe_rating', 'created_at'
    ]
    list_filter = ['processor_type', 'is_verified', 'seasonal_operation', 'created_at']
    search_fields = ['business_name', 'user__username', 'user__email', 'specializations']
    readonly_fields = [
        'total_recipes_shared', 'average_recipe_rating', 'total_processing_orders',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'business_name', 'business_registration_number', 'processor_type')
        }),
        ('Capabilities', {
            'fields': ('specializations', 'processing_capabilities', 'equipment_list'),
            'classes': ('collapse',)
        }),
        ('Capacity & Operations', {
            'fields': (
                'daily_processing_capacity', 'capacity_unit', 'operating_hours',
                'seasonal_operation', 'operating_seasons', 'service_radius_km'
            ),
            'classes': ('collapse',)
        }),
        ('Certifications', {
            'fields': ('certifications', 'health_permits', 'quality_standards'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_at', 'verification_documents'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': (
                'total_recipes_shared', 'average_recipe_rating', 'total_processing_orders'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class RecipeRatingInline(admin.TabularInline):
    model = RecipeRating
    extra = 0
    readonly_fields = ['user', 'created_at']
    fields = [
        'user', 'overall_rating', 'clarity_rating', 'effectiveness_rating',
        'accuracy_rating', 'would_recommend', 'created_at'
    ]


class RecipeCommentInline(admin.TabularInline):
    model = RecipeComment
    extra = 0
    readonly_fields = ['user', 'created_at']
    fields = ['user', 'content', 'is_question', 'is_answered', 'helpful_count', 'created_at']


@admin.register(ProcessingRecipe)
class ProcessingRecipeAdmin(admin.ModelAdmin):
    list_display = [
        'recipe_name', 'processor', 'processor_type', 'skill_level_required',
        'status', 'is_public', 'is_verified', 'average_rating', 'times_used', 'created_at'
    ]
    list_filter = [
        'skill_level_required', 'status', 'is_public', 'is_verified',
        'seasonal_availability', 'created_at'
    ]
    search_fields = [
        'recipe_name', 'description', 'tags', 'processor__username',
        'processor__processor_profile__business_name'
    ]
    readonly_fields = [
        'processor', 'times_used', 'success_rate_percentage', 'average_rating',
        'rating_count', 'verified_by', 'verification_date', 'created_at', 'updated_at'
    ]
    inlines = [RecipeRatingInline, RecipeCommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'recipe_name', 'processor', 'description', 'skill_level_required',
                'processing_time_minutes', 'tags'
            )
        }),
        ('Recipe Details', {
            'fields': ('input_materials', 'processing_steps', 'equipment_required', 'output_products'),
            'classes': ('collapse',)
        }),
        ('Quality & Yield', {
            'fields': (
                'expected_yield_percentage', 'quality_checkpoints', 'quality_standards',
                'certifications_achieved', 'compliance_standards'
            ),
            'classes': ('collapse',)
        }),
        ('Cost Analysis', {
            'fields': (
                'processing_cost_per_unit', 'labor_hours_required', 'energy_consumption',
                'water_usage_liters', 'waste_generation_kg'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Verification', {
            'fields': (
                'status', 'is_public', 'is_verified', 'verified_by', 'verification_date'
            )
        }),
        ('Availability', {
            'fields': ('seasonal_availability', 'available_seasons'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('times_used', 'success_rate_percentage', 'average_rating', 'rating_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'processor', 'processor__processor_profile', 'verified_by'
        )
    
    def processor_type(self, obj):
        if hasattr(obj.processor, 'processor_profile'):
            return obj.processor.processor_profile.processor_type
        return '-'
    processor_type.short_description = 'Processor Type'
    
    def rating_display(self, obj):
        if obj.rating_count > 0:
            stars = '★' * int(obj.average_rating)
            return format_html(
                '{} <span style="color: orange;">{}</span> ({})',
                obj.average_rating, stars, obj.rating_count
            )
        return 'No ratings'
    rating_display.short_description = 'Rating'


@admin.register(RecipeRating)
class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = [
        'recipe', 'user', 'overall_rating', 'clarity_rating',
        'effectiveness_rating', 'accuracy_rating', 'would_recommend', 'created_at'
    ]
    list_filter = [
        'overall_rating', 'clarity_rating', 'effectiveness_rating',
        'accuracy_rating', 'would_recommend', 'created_at'
    ]
    search_fields = [
        'recipe__recipe_name', 'user__username', 'review_title', 'review_content'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recipe', 'user', 'review_title')
        }),
        ('Ratings', {
            'fields': (
                'overall_rating', 'clarity_rating', 'effectiveness_rating', 'accuracy_rating'
            )
        }),
        ('Review Content', {
            'fields': ('review_content', 'would_recommend', 'improvement_suggestions'),
            'classes': ('collapse',)
        }),
        ('Usage Experience', {
            'fields': ('actual_yield_achieved', 'processing_time_actual'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipe', 'user')


@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = [
        'recipe', 'user', 'content_preview', 'is_question',
        'is_answered', 'helpful_count', 'created_at'
    ]
    list_filter = ['is_question', 'is_answered', 'created_at']
    search_fields = ['recipe__recipe_name', 'user__username', 'content']
    readonly_fields = ['helpful_count', 'created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipe', 'user')


@admin.register(RecipeUsageLog)
class RecipeUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'recipe', 'user', 'used_at', 'processing_facility',
        'batch_size', 'success', 'actual_yield'
    ]
    list_filter = ['success', 'used_at']
    search_fields = [
        'recipe__recipe_name', 'user__username', 'processing_facility', 'notes'
    ]
    readonly_fields = ['used_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recipe', 'user', 'used_at', 'processing_facility')
        }),
        ('Processing Details', {
            'fields': ('batch_size', 'success', 'actual_yield', 'processing_time_actual')
        }),
        ('Notes & Issues', {
            'fields': ('notes', 'issues_encountered'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipe', 'user')
