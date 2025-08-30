from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Review, ReviewHelpfulVote, ReviewFlag, ReviewResponse,
    ExpertReview, ReviewRecipe, SeasonalInsight,
    PeerRecommendation, PeerRecommendationVote, FarmerNetwork, PeerRecommendationInteraction
)


class ReviewHelpfulVoteInline(admin.TabularInline):
    model = ReviewHelpfulVote
    extra = 0
    readonly_fields = ['user', 'is_helpful', 'created_at']
    can_delete = False


class ReviewFlagInline(admin.TabularInline):
    model = ReviewFlag
    extra = 0
    readonly_fields = ['flagger', 'reason', 'description', 'created_at']


class ReviewResponseInline(admin.StackedInline):
    model = ReviewResponse
    extra = 0
    readonly_fields = ['responder', 'created_at', 'updated_at']


class ReviewRecipeInline(admin.TabularInline):
    model = ReviewRecipe
    extra = 0
    readonly_fields = ['author', 'title', 'difficulty', 'likes_count', 'created_at']
    fields = ['title', 'author', 'difficulty', 'prep_time', 'cook_time', 'servings', 'likes_count']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'product', 'reviewer', 'overall_rating_display', 
        'verified_purchase', 'helpful_votes', 'status', 'created_at'
    ]
    
    list_filter = [
        'status', 'verified_purchase', 'blockchain_verified', 'overall_rating',
        'quality_rating', 'sustainability_rating', 'farmer_rating',
        'created_at', 'product__category'
    ]
    
    search_fields = ['title', 'content', 'reviewer__username', 'product__name']
    
    readonly_fields = [
        'reviewer', 'product', 'order', 'verified_purchase', 'blockchain_verified',
        'helpful_votes', 'total_votes', 'helpfulness_ratio', 'average_detailed_rating',
        'product_quality_average', 'farmer_reliability_average', 'service_quality_average',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('reviewer', 'product', 'order', 'title', 'content')
        }),        ('Ratings', {
            'fields': (
                'overall_rating',
                # Product Quality Ratings
                ('quality_rating', 'freshness_rating', 'taste_rating'),
                ('packaging_rating', 'value_rating'),
                # Farmer Reliability Ratings  
                ('delivery_rating', 'communication_rating', 'consistency_rating'),
                'farmer_rating',
                # Service Quality Ratings
                ('logistics_rating', 'warehouse_handling_rating', 'customer_service_rating'),
                # Sustainability Rating
                'sustainability_rating'
            )
        }),
        ('Additional Content', {
            'fields': ('pros', 'cons', 'images', 'videos'),
            'classes': ('collapse',)
        }),
        ('Verification & Status', {
            'fields': (
                'verified_purchase', 'blockchain_verified', 'status',
                'flagged_reason', 'moderated_by', 'moderated_at'
            )
        }),        ('Metrics', {
            'fields': (
                'helpful_votes', 'total_votes', 'helpfulness_ratio',
                'average_detailed_rating', 'product_quality_average',
                'farmer_reliability_average', 'service_quality_average'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [ReviewResponseInline, ReviewRecipeInline, ReviewHelpfulVoteInline, ReviewFlagInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def overall_rating_display(self, obj):
        stars = '★' * obj.overall_rating + '☆' * (5 - obj.overall_rating)
        return format_html(
            '<span style="color: #ffa500; font-size: 16px;">{}</span> ({})',
            stars, obj.overall_rating
        )
    overall_rating_display.short_description = 'Rating'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'reviewer', 'product', 'order'
        ).prefetch_related('helpful_votes_detail', 'flags')


@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['review__title', 'user__username']
    readonly_fields = ['review', 'user', 'is_helpful', 'created_at']
    ordering = ['-created_at']


@admin.register(ReviewFlag)
class ReviewFlagAdmin(admin.ModelAdmin):
    list_display = [
        'review', 'flagger', 'reason', 'status', 'reviewed_by', 'created_at'
    ]
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['review__title', 'flagger__username', 'description']
    readonly_fields = ['review', 'flagger', 'created_at']
    fieldsets = (
        ('Flag Information', {
            'fields': ('review', 'flagger', 'reason', 'description')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
    ordering = ['-created_at']
    
    def save_model(self, request, obj, form, change):
        if change and obj.status in ['reviewed', 'resolved', 'dismissed']:
            if not obj.reviewed_by:
                obj.reviewed_by = request.user
            if not obj.reviewed_at:
                obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'responder', 'is_public', 'created_at'
]
    list_filter = ['is_public', 'created_at']
    search_fields = ['review__title', 'responder__username', 'content']
    readonly_fields = ['review', 'responder', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ExpertReview)
class ExpertReviewAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'product', 'expert', 'expert_type', 'overall_rating',
        'verified_expert', 'is_featured', 'created_at'
    ]
    list_filter = [
        'expert_type', 'verified_expert', 'is_featured', 'is_published',
        'overall_rating', 'created_at'
    ]
    search_fields = ['title', 'content', 'expert__username', 'product__name']
    readonly_fields = ['expert', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'expert', 'expert_type', 'title', 'content')
        }),
        ('Expert Assessment', {
            'fields': (
                'overall_rating', 'quality_assessment', 'nutritional_value',
                'sustainability_rating', 'recommendations'
            )
        }),
        ('Expert Credentials', {
            'fields': ('verified_expert', 'expert_credentials', 'certifications'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_featured', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-created_at']


@admin.register(ReviewRecipe)
class ReviewRecipeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'review', 'author', 'difficulty', 'prep_time',
        'cook_time', 'servings', 'likes_count', 'created_at'
    ]
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title', 'description', 'author__username', 'review__title']
    readonly_fields = ['author', 'likes_count', 'shares_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('review', 'author', 'title', 'description')
        }),
        ('Recipe Details', {
            'fields': (
                'ingredients', 'instructions', 'prep_time', 'cook_time',
                'servings', 'difficulty'
            )
        }),
        ('Nutrition & Media', {
            'fields': ('calories_per_serving', 'nutrition_notes', 'images'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('likes_count', 'shares_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-created_at']


@admin.register(SeasonalInsight)
class SeasonalInsightAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'season', 'region', 'average_rating',
        'review_count', 'quality_score', 'price_trend', 'updated_at'
    ]
    list_filter = ['season', 'price_trend', 'region']
    search_fields = ['product__name', 'region', 'insights']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'season', 'region')
        }),
        ('Metrics', {
            'fields': (
                'average_rating', 'review_count', 'quality_score',
                'availability_score', 'price_trend'
            )
        }),
        ('Insights', {
            'fields': ('insights', 'recommendations', 'best_varieties')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-updated_at']


# ========================================
# PEER RECOMMENDATION ADMIN CONFIGURATIONS
# ========================================

class PeerRecommendationVoteInline(admin.TabularInline):
    model = PeerRecommendationVote
    extra = 0
    readonly_fields = ['voter', 'is_helpful', 'comment', 'created_at']
    can_delete = False
    fields = ['voter', 'is_helpful', 'comment', 'created_at']


class PeerRecommendationInteractionInline(admin.TabularInline):
    model = PeerRecommendationInteraction
    extra = 0
    readonly_fields = ['user', 'interaction_type', 'implementation_success', 'created_at']
    can_delete = False
    fields = ['user', 'interaction_type', 'notes', 'implementation_success', 'created_at']


@admin.register(PeerRecommendation)
class PeerRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'recommender', 'recommendation_type', 'recommendation_strength',
        'product', 'verified_peer_badge', 'helpfulness_display', 'vote_count',
        'created_at'
    ]
    
    list_filter = [
        'recommendation_type', 'recommendation_strength', 'verified_peer',
        'is_featured', 'is_active', 'created_at', 'relevant_regions'
    ]
    
    search_fields = [
        'title', 'content', 'recommender__username', 'product__name',
        'farmer_recommended__username', 'results_achieved'
    ]
    
    readonly_fields = [
        'id', 'recommender', 'peer_helpful_votes', 'peer_total_votes',
        'average_farmer_rating', 'helpfulness_percentage', 'created_at', 'updated_at'
    ]
    
    inlines = [PeerRecommendationVoteInline, PeerRecommendationInteractionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'recommender', 'recommendation_type', 'recommendation_strength',
                'title', 'content'
            )
        }),
        ('Product/Farmer Details', {
            'fields': ('product', 'farmer_recommended', 'recommended_to')
        }),
        ('Experience Details', {
            'fields': (
                'experience_duration', 'farm_context', 'results_achieved',
                'conditions_for_success'
            )
        }),
        ('Farmer Ratings', {
            'fields': (
                'value_for_farmers', 'ease_of_use', 'yield_impact',
                'cost_effectiveness', 'average_farmer_rating'
            )
        }),
        ('Community Validation', {
            'fields': (
                'peer_helpful_votes', 'peer_total_votes', 'helpfulness_percentage',
                'verified_peer'
            )
        }),
        ('Relevance & Visibility', {
            'fields': (
                'relevant_regions', 'seasonal_relevance', 'is_active',
                'is_featured', 'moderated_by'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def verified_peer_badge(self, obj):
        if obj.verified_peer:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: orange;">Pending</span>')
    verified_peer_badge.short_description = 'Verification Status'
    
    def helpfulness_display(self, obj):
        percentage = obj.helpfulness_percentage
        if percentage >= 80:
            color = 'green'
        elif percentage >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    helpfulness_display.short_description = 'Helpfulness'
    
    def vote_count(self, obj):
        return f"{obj.peer_helpful_votes}/{obj.peer_total_votes}"
    vote_count.short_description = 'Votes (Helpful/Total)'
    
    ordering = ['-created_at']


@admin.register(PeerRecommendationVote)
class PeerRecommendationVoteAdmin(admin.ModelAdmin):
    list_display = [
        'recommendation_title', 'voter', 'is_helpful', 'has_comment', 'created_at'
    ]
    
    list_filter = ['is_helpful', 'created_at']
    
    search_fields = [
        'recommendation__title', 'voter__username', 'comment'
    ]
    
    readonly_fields = ['id', 'recommendation', 'voter', 'created_at']
    
    def recommendation_title(self, obj):
        return obj.recommendation.title[:50]
    recommendation_title.short_description = 'Recommendation'
    
    def has_comment(self, obj):
        return bool(obj.comment)
    has_comment.boolean = True
    has_comment.short_description = 'Has Comment'
    
    ordering = ['-created_at']


@admin.register(FarmerNetwork)
class FarmerNetworkAdmin(admin.ModelAdmin):
    list_display = [
        'follower', 'following', 'trust_level', 'success_rate_display',
        'recommendations_received', 'successful_recommendations', 'created_at'
    ]
    
    list_filter = ['trust_level', 'created_at']
    
    search_fields = ['follower__username', 'following__username']
    
    readonly_fields = [
        'id', 'follower', 'following', 'success_rate', 'created_at'
    ]
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    ordering = ['-created_at']


@admin.register(PeerRecommendationInteraction)
class PeerRecommendationInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'recommendation_title', 'user', 'interaction_type',
        'implementation_success', 'created_at'
    ]
    
    list_filter = [
        'interaction_type', 'implementation_success', 'created_at'
    ]
    
    search_fields = [
        'recommendation__title', 'user__username', 'notes'
    ]
    
    readonly_fields = ['id', 'recommendation', 'user', 'created_at']
    
    def recommendation_title(self, obj):
        return obj.recommendation.title[:50]
    recommendation_title.short_description = 'Recommendation'
    
    ordering = ['-created_at']
