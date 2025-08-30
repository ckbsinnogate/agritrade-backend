from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from .models import (
    Review, ReviewHelpfulVote, ReviewFlag, ReviewResponse, 
    ExpertReview, ReviewRecipe, SeasonalInsight,
    PeerRecommendation, PeerRecommendationVote, FarmerNetwork, PeerRecommendationInteraction
)
from products.models import Product
from orders.models import Order

User = get_user_model()


class ReviewerSerializer(serializers.ModelSerializer):
    """Simplified user serializer for review display"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for farmer responses to reviews"""
    
    responder = ReviewerSerializer(read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = [
            'id', 'content', 'responder', 'is_public', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'responder', 'created_at', 'updated_at']


class ReviewFlagSerializer(serializers.ModelSerializer):
    """Serializer for review flagging system"""
    
    flagger = ReviewerSerializer(read_only=True)
    reviewed_by = ReviewerSerializer(read_only=True)
    
    class Meta:
        model = ReviewFlag
        fields = [
            'id', 'reason', 'description', 'status', 
            'flagger', 'reviewed_by', 'reviewed_at', 'created_at'
        ]
        read_only_fields = ['id', 'flagger', 'reviewed_by', 'reviewed_at', 'created_at']


class ReviewHelpfulVoteSerializer(serializers.ModelSerializer):
    """Serializer for helpful vote tracking"""
    
    user = ReviewerSerializer(read_only=True)
    
    class Meta:
        model = ReviewHelpfulVote
        fields = ['id', 'is_helpful', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReviewRecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe suggestions in reviews"""
    
    author = ReviewerSerializer(read_only=True)
    total_time = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewRecipe
        fields = [
            'id', 'title', 'description', 'ingredients', 'instructions',
            'prep_time', 'cook_time', 'total_time', 'servings', 'difficulty',
            'calories_per_serving', 'nutrition_notes', 'images',
            'likes_count', 'shares_count', 'author', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'likes_count', 'shares_count', 
            'created_at', 'updated_at'
        ]
    
    def get_total_time(self, obj):
        return obj.prep_time + obj.cook_time


class ReviewListSerializer(serializers.ModelSerializer):
    """Simplified serializer for review lists"""
    
    reviewer = ReviewerSerializer(read_only=True)
    response = ReviewResponseSerializer(read_only=True)
    helpfulness_ratio = serializers.ReadOnlyField()
    average_detailed_rating = serializers.ReadOnlyField()
    product_quality_average = serializers.ReadOnlyField()
    farmer_reliability_average = serializers.ReadOnlyField()
    service_quality_average = serializers.ReadOnlyField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'overall_rating', 
            # Product Quality Ratings
            'quality_rating', 'freshness_rating', 'taste_rating', 'packaging_rating', 'value_rating',
            # Farmer Reliability Ratings
            'delivery_rating', 'communication_rating', 'consistency_rating', 'farmer_rating',
            # Service Quality Ratings
            'logistics_rating', 'warehouse_handling_rating', 'customer_service_rating',
            # Sustainability Rating
            'sustainability_rating',            'title', 'content', 'verified_purchase', 'blockchain_verified',
            'helpful_votes', 'total_votes', 'helpfulness_ratio',
            'average_detailed_rating', 'product_quality_average', 
            'farmer_reliability_average', 'service_quality_average',
            'reviewer', 'response', 'created_at'
        ]
        read_only_fields = [
            'id', 'verified_purchase', 'blockchain_verified', 'helpful_votes',
            'total_votes', 'helpfulness_ratio', 'average_detailed_rating',
            'reviewer', 'response', 'created_at'
        ]


class ReviewDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual review operations"""
    
    reviewer = ReviewerSerializer(read_only=True)
    response = ReviewResponseSerializer(read_only=True)
    recipes = ReviewRecipeSerializer(many=True, read_only=True)
    helpful_votes_detail = ReviewHelpfulVoteSerializer(many=True, read_only=True)
    flags = ReviewFlagSerializer(many=True, read_only=True)
    helpfulness_ratio = serializers.ReadOnlyField()
    average_detailed_rating = serializers.ReadOnlyField()
    product_quality_average = serializers.ReadOnlyField()
    farmer_reliability_average = serializers.ReadOnlyField()
    service_quality_average = serializers.ReadOnlyField()
    can_respond = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'order', 'overall_rating', 
            # Product Quality Ratings
            'quality_rating', 'freshness_rating', 'taste_rating', 'packaging_rating', 'value_rating',
            # Farmer Reliability Ratings
            'delivery_rating', 'communication_rating', 'consistency_rating', 'farmer_rating',
            # Service Quality Ratings
            'logistics_rating', 'warehouse_handling_rating', 'customer_service_rating',
            # Sustainability Rating
            'sustainability_rating',
            'title', 'content', 'pros', 'cons', 'verified_purchase', 'blockchain_verified',            'images', 'videos', 'status', 'helpful_votes', 'total_votes',
            'helpfulness_ratio', 'average_detailed_rating',        'product_quality_average', 'farmer_reliability_average', 'service_quality_average',
            'reviewer', 'response', 'recipes', 'helpful_votes_detail', 'flags',
            'can_respond', 'user_vote', 'created_at', 'updated_at'
        ]
        
        read_only_fields = [
            'id', 'verified_purchase', 'blockchain_verified', 'status',
            'helpful_votes', 'total_votes', 'helpfulness_ratio',
            'average_detailed_rating', 'product_quality_average', 
            'farmer_reliability_average', 'service_quality_average',
            'reviewer', 'response', 'recipes', 'helpful_votes_detail', 
            'flags', 'can_respond', 'user_vote', 'created_at', 'updated_at'
        ]
    
    def get_can_respond(self, obj):
        """Check if current user can respond to this review"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Only the product seller can respond
        return obj.product.seller == request.user and not hasattr(obj, 'response')
    
    def get_user_vote(self, obj):
        """Get current user's helpful vote for this review"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            vote = obj.helpful_votes_detail.get(user=request.user)
            return {'is_helpful': vote.is_helpful, 'created_at': vote.created_at}
        except ReviewHelpfulVote.DoesNotExist:
            return None
    
    def validate(self, data):
        """Validate review data"""
        request = self.context.get('request')
        
        # Check if user has purchased this product
        if request and hasattr(request, 'user'):
            product = data.get('product')
            order = data.get('order')
            
            if order and product:
                # Verify the order contains this product and belongs to the user
                if not order.items.filter(product=product).exists():
                    raise serializers.ValidationError(
                        "The specified order does not contain this product."
                    )
                
                if order.buyer != request.user:
                    raise serializers.ValidationError(
                        "You can only review products from your own orders."
                    )
                
                # Set verified purchase if valid order
                data['verified_purchase'] = True
        
        return data


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reviews"""
    
    class Meta:
        model = Review
        fields = [
            'product', 'order', 'overall_rating', 'quality_rating',
            'freshness_rating', 'packaging_rating', 'value_rating',
            'delivery_rating', 'farmer_rating', 'title', 'content',
            'pros', 'cons', 'images', 'videos'
        ]
    
    def create(self, validated_data):
        """Create review with automatic reviewer assignment"""
        request = self.context.get('request')
        validated_data['reviewer'] = request.user
        return super().create(validated_data)


class ExpertReviewSerializer(serializers.ModelSerializer):
    """Serializer for expert reviews"""
    
    expert = ReviewerSerializer(read_only=True)
    
    class Meta:
        model = ExpertReview
        fields = [
            'id', 'product', 'expert', 'expert_type', 'overall_rating',
            'quality_assessment', 'nutritional_value', 'sustainability_rating',
            'title', 'content', 'recommendations', 'certifications',
            'verified_expert', 'expert_credentials', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'expert', 'verified_expert', 'is_featured',
            'created_at', 'updated_at'
        ]


class SeasonalInsightSerializer(serializers.ModelSerializer):
    """Serializer for seasonal product insights"""
    
    class Meta:
        model = SeasonalInsight
        fields = [
            'id', 'product', 'season', 'average_rating', 'review_count',
            'quality_score', 'availability_score', 'price_trend',
            'insights', 'recommendations', 'best_varieties', 'region',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductReviewSummarySerializer(serializers.Serializer):
    """Serializer for product review summary statistics"""
    
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    verified_reviews_count = serializers.IntegerField()
    
    # Rating distribution
    rating_distribution = serializers.DictField()
    
    # Detailed rating averages
    average_quality_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    average_freshness_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    average_packaging_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    average_value_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    average_delivery_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    average_farmer_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    
    # Recent reviews
    recent_reviews = ReviewListSerializer(many=True)
    
    # Expert reviews
    expert_reviews_count = serializers.IntegerField()
    has_expert_reviews = serializers.BooleanField()


class ReviewAnalyticsSerializer(serializers.Serializer):
    """Serializer for review analytics and insights"""
    
    # Trend data
    review_trends = serializers.DictField()
    sentiment_analysis = serializers.DictField()
    
    # Top performers
    top_rated_products = serializers.ListField()
    top_rated_farmers = serializers.ListField()
    
    # Seasonal insights
    seasonal_recommendations = serializers.ListField()
    
    # Community metrics
    most_helpful_reviewers = serializers.ListField()
    most_active_reviewers = serializers.ListField()


class FarmerProfileSerializer(serializers.ModelSerializer):
    """Simplified farmer profile serializer for peer recommendations"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    experience_level = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'user_name', 'experience_level', 'farm_size', 'years_of_experience', 'primary_crops']
        read_only_fields = ['id', 'username', 'user_name', 'experience_level']
    
    def get_experience_level(self, obj):
        """Determine farmer experience level"""
        if hasattr(obj, 'farmer_profile'):
            years = obj.farmer_profile.years_of_experience
            if years >= 15:
                return 'Expert Farmer'
            elif years >= 8:
                return 'Experienced Farmer'
            elif years >= 3:
                return 'Intermediate Farmer'
            else:
                return 'Beginning Farmer'
        return 'Unknown'


class PeerRecommendationVoteSerializer(serializers.ModelSerializer):
    """Serializer for peer recommendation voting"""
    
    voter = ReviewerSerializer(read_only=True)
    
    class Meta:
        model = PeerRecommendationVote
        fields = ['id', 'is_helpful', 'comment', 'voter', 'created_at']
        read_only_fields = ['id', 'voter', 'created_at']


class PeerRecommendationInteractionSerializer(serializers.ModelSerializer):
    """Serializer for peer recommendation interactions"""
    
    user = ReviewerSerializer(read_only=True)
    
    class Meta:
        model = PeerRecommendationInteraction
        fields = [
            'id', 'interaction_type', 'notes', 'implementation_success',
            'implementation_notes', 'user', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class PeerRecommendationListSerializer(serializers.ModelSerializer):
    """Serializer for listing peer recommendations"""
    
    recommender = FarmerProfileSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    farmer_recommended_name = serializers.CharField(source='farmer_recommended.get_full_name', read_only=True)
    average_farmer_rating = serializers.ReadOnlyField()
    helpfulness_percentage = serializers.ReadOnlyField()
    vote_count = serializers.SerializerMethodField()
    interaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PeerRecommendation
        fields = [
            'id', 'recommender', 'product_name', 'farmer_recommended_name',
            'recommendation_type', 'recommendation_strength', 'title',
            'experience_duration', 'average_farmer_rating', 'helpfulness_percentage',
            'vote_count', 'interaction_count', 'verified_peer', 'is_featured',
            'relevant_regions', 'seasonal_relevance', 'created_at'
        ]
        read_only_fields = [
            'id', 'recommender', 'product_name', 'farmer_recommended_name',
            'average_farmer_rating', 'helpfulness_percentage', 'vote_count',
            'interaction_count', 'created_at'
        ]
    
    def get_vote_count(self, obj):
        return obj.peer_total_votes
    
    def get_interaction_count(self, obj):
        return obj.interactions.count()


class PeerRecommendationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for peer recommendations"""
    
    recommender = FarmerProfileSerializer(read_only=True)
    product_details = serializers.SerializerMethodField()
    farmer_recommended_details = serializers.SerializerMethodField()
    average_farmer_rating = serializers.ReadOnlyField()
    helpfulness_percentage = serializers.ReadOnlyField()
    recent_votes = PeerRecommendationVoteSerializer(source='votes', many=True, read_only=True)
    recent_interactions = PeerRecommendationInteractionSerializer(source='interactions', many=True, read_only=True)
    
    class Meta:
        model = PeerRecommendation
        fields = [
            'id', 'recommender', 'product_details', 'farmer_recommended_details',
            'recommendation_type', 'recommendation_strength', 'title', 'content',
            'experience_duration', 'farm_context', 'results_achieved', 'conditions_for_success',
            'value_for_farmers', 'ease_of_use', 'yield_impact', 'cost_effectiveness',
            'average_farmer_rating', 'helpfulness_percentage', 'peer_helpful_votes',
            'peer_total_votes', 'verified_peer', 'is_featured',
            'relevant_regions', 'seasonal_relevance', 'recent_votes', 'recent_interactions',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'recommender', 'product_details', 'farmer_recommended_details',
            'average_farmer_rating', 'helpfulness_percentage', 'peer_helpful_votes',
            'peer_total_votes', 'recent_votes', 'recent_interactions', 'created_at', 'updated_at'
        ]
    
    def get_product_details(self, obj):
        if obj.product:
            return {
                'id': obj.product.id,
                'name': obj.product.name,
                'category': obj.product.category.name if obj.product.category else None,
                'farmer_name': obj.product.farmer.get_full_name() if obj.product.farmer else None,
            }
        return None
    
    def get_farmer_recommended_details(self, obj):
        if obj.farmer_recommended:
            farmer_profile = getattr(obj.farmer_recommended, 'farmer_profile', None)
            return {
                'id': obj.farmer_recommended.id,
                'name': obj.farmer_recommended.get_full_name(),
                'username': obj.farmer_recommended.username,
                'farm_size': farmer_profile.farm_size if farmer_profile else None,
                'experience_years': farmer_profile.years_of_experience if farmer_profile else None,
                'primary_crops': farmer_profile.primary_crops if farmer_profile else [],
            }
        return None


class PeerRecommendationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating peer recommendations"""
    
    class Meta:
        model = PeerRecommendation
        fields = [
            'product', 'farmer_recommended', 'recommendation_type', 'recommendation_strength',
            'title', 'content', 'experience_duration', 'farm_context', 'results_achieved',
            'conditions_for_success', 'value_for_farmers', 'ease_of_use', 'yield_impact',
            'cost_effectiveness', 'relevant_regions', 'seasonal_relevance'
        ]
    
    def validate(self, data):
        """Validate recommendation data"""
        recommendation_type = data.get('recommendation_type')
        
        if recommendation_type == 'product_endorsement' and not data.get('product'):
            raise serializers.ValidationError("Product is required for product endorsements")
        
        if recommendation_type == 'farmer_endorsement' and not data.get('farmer_recommended'):
            raise serializers.ValidationError("Farmer is required for farmer endorsements")
        
        return data


class FarmerNetworkSerializer(serializers.ModelSerializer):
    """Serializer for farmer networking"""
    
    follower_details = FarmerProfileSerializer(source='follower', read_only=True)
    following_details = FarmerProfileSerializer(source='following', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = FarmerNetwork
        fields = [
            'id', 'follower_details', 'following_details', 'trust_level',
            'recommendations_received', 'successful_recommendations', 'success_rate',
            'created_at'
        ]
        read_only_fields = [
            'id', 'follower_details', 'following_details', 'success_rate', 'created_at'
        ]
