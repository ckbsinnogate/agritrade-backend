from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q, Case, When, IntegerField, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import (
    Review, ReviewHelpfulVote, ReviewFlag, ReviewResponse,
    ExpertReview, ReviewRecipe, SeasonalInsight,
    PeerRecommendation, PeerRecommendationVote, FarmerNetwork, PeerRecommendationInteraction
)
from .serializers import (
    ReviewDetailSerializer, ReviewListSerializer, ReviewCreateSerializer,
    ReviewHelpfulVoteSerializer, ReviewFlagSerializer, ReviewResponseSerializer,
    ExpertReviewSerializer, ReviewRecipeSerializer, SeasonalInsightSerializer,
    ProductReviewSummarySerializer, ReviewAnalyticsSerializer,
    PeerRecommendationListSerializer, PeerRecommendationDetailSerializer, 
    PeerRecommendationCreateSerializer, PeerRecommendationVoteSerializer,
    FarmerNetworkSerializer, PeerRecommendationInteractionSerializer
)
from products.models import Product
from orders.models import Order

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Comprehensive review management with multi-dimensional ratings,
    community features, and verification systems.
    """
    
    queryset = Review.objects.select_related(
        'reviewer', 'product', 'order', 'response__responder'
    ).prefetch_related(
        'recipes', 'helpful_votes_detail', 'flags'
    ).filter(status='published')
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'overall_rating', 'verified_purchase', 'blockchain_verified',
        'product', 'reviewer'
    ]
    search_fields = ['title', 'content', 'pros', 'cons']
    ordering_fields = [
        'created_at', 'overall_rating', 'helpful_votes', 'helpfulness_ratio'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['list']:
            return ReviewListSerializer
        return ReviewDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by rating range
        min_rating = self.request.query_params.get('min_rating')
        max_rating = self.request.query_params.get('max_rating')
        if min_rating:
            queryset = queryset.filter(overall_rating__gte=min_rating)
        if max_rating:
            queryset = queryset.filter(overall_rating__lte=max_rating)
        
        # Filter by verification status
        verified_only = self.request.query_params.get('verified_only')
        if verified_only and verified_only.lower() == 'true':
            queryset = queryset.filter(
                Q(verified_purchase=True) | Q(blockchain_verified=True)
            )
        
        # Filter by time period
        days_back = self.request.query_params.get('days_back')
        if days_back:
            try:
                days = int(days_back)
                since_date = timezone.now() - timezone.timedelta(days=days)
                queryset = queryset.filter(created_at__gte=since_date)
            except ValueError:
                pass
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign reviewer and validate purchase"""
        review = serializer.save(reviewer=self.request.user)
        
        # Check for verified purchase
        if review.order:
            # Verify the order is delivered and belongs to the user
            if (review.order.buyer == self.request.user and 
                review.order.status == 'delivered'):
                review.verified_purchase = True
                review.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def helpful_vote(self, request, pk=None):
        """Mark review as helpful or not helpful"""
        review = self.get_object()
        is_helpful = request.data.get('is_helpful', True)
        
        # Remove existing vote if any
        ReviewHelpfulVote.objects.filter(
            review=review, user=request.user
        ).delete()
        
        # Create new vote
        vote = ReviewHelpfulVote.objects.create(
            review=review,
            user=request.user,
            is_helpful=is_helpful
        )
        
        # Update review vote counts
        helpful_count = review.helpful_votes_detail.filter(is_helpful=True).count()
        total_count = review.helpful_votes_detail.count()
        
        review.helpful_votes = helpful_count
        review.total_votes = total_count
        review.save()
        
        serializer = ReviewHelpfulVoteSerializer(vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def flag_review(self, request, pk=None):
        """Flag review for inappropriate content"""
        review = self.get_object()
        reason = request.data.get('reason')
        description = request.data.get('description', '')
        
        if not reason:
            return Response(
                {'error': 'Reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already flagged this review
        existing_flag = ReviewFlag.objects.filter(
            review=review, flagger=request.user
        ).first()
        
        if existing_flag:
            return Response(
                {'error': 'You have already flagged this review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        flag = ReviewFlag.objects.create(
            review=review,
            flagger=request.user,
            reason=reason,
            description=description
        )
        
        serializer = ReviewFlagSerializer(flag)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def respond(self, request, pk=None):
        """Farmer response to review"""
        review = self.get_object()
        
        # Check if user is the product seller
        if review.product.seller != request.user:
            return Response(
                {'error': 'Only the product seller can respond to reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if response already exists
        if hasattr(review, 'response'):
            return Response(
                {'error': 'Response already exists for this review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(review=review, responder=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def product_summary(self, request):
        """Get review summary for a specific product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reviews = Review.objects.filter(product=product, status='published')
        
        # Calculate summary statistics
        summary_data = {
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(
                avg=Avg('overall_rating')
            )['avg'] or 0,
            'verified_reviews_count': reviews.filter(verified_purchase=True).count(),
            
            # Rating distribution
            'rating_distribution': {
                str(i): reviews.filter(overall_rating=i).count()
                for i in range(1, 6)
            },
            
            # Detailed rating averages
            'average_quality_rating': reviews.aggregate(
                avg=Avg('quality_rating')
            )['avg'] or 0,
            'average_freshness_rating': reviews.aggregate(
                avg=Avg('freshness_rating')
            )['avg'] or 0,
            'average_packaging_rating': reviews.aggregate(
                avg=Avg('packaging_rating')
            )['avg'] or 0,
            'average_value_rating': reviews.aggregate(
                avg=Avg('value_rating')
            )['avg'] or 0,
            'average_delivery_rating': reviews.aggregate(
                avg=Avg('delivery_rating')
            )['avg'] or 0,
            'average_farmer_rating': reviews.aggregate(
                avg=Avg('farmer_rating')
            )['avg'] or 0,
            
            # Recent reviews
            'recent_reviews': ReviewListSerializer(
                reviews.order_by('-created_at')[:5],
                many=True,
                context={'request': request}
            ).data,
            
            # Expert reviews
            'expert_reviews_count': ExpertReview.objects.filter(
                product=product, is_published=True
            ).count(),
            'has_expert_reviews': ExpertReview.objects.filter(
                product=product, is_published=True
            ).exists(),        }
        
        serializer = ProductReviewSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending reviews based on recent activity"""
        days_back = int(request.query_params.get('days', 7))
        since_date = timezone.now() - timezone.timedelta(days=days_back)
        
        trending_reviews = self.get_queryset().filter(
            created_at__gte=since_date
        ).annotate(
            popularity_score=F('helpful_votes') + F('total_votes')
        ).order_by('-popularity_score', '-created_at')[:20]
        
        serializer = self.get_serializer(trending_reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get review analytics and insights"""
        # This would include comprehensive analytics
        # For now, return basic structure
        analytics_data = {
            'review_trends': {},
            'sentiment_analysis': {},
            'top_rated_products': [],
            'top_rated_farmers': [],
            'seasonal_recommendations': [],
            'most_helpful_reviewers': [],
            'most_active_reviewers': []
        }
        
        serializer = ReviewAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        """Get current user's reviews"""
        user_reviews = self.get_queryset().filter(reviewer=request.user)
        
        # Apply any additional filtering from query params
        product_id = request.query_params.get('product_id')
        if product_id:
            user_reviews = user_reviews.filter(product_id=product_id)
        
        # Filter by rating range
        min_rating = request.query_params.get('min_rating')
        max_rating = request.query_params.get('max_rating')
        if min_rating:
            user_reviews = user_reviews.filter(overall_rating__gte=min_rating)
        if max_rating:
            user_reviews = user_reviews.filter(overall_rating__lte=max_rating)
        
        # Filter by time period
        days_back = request.query_params.get('days_back')
        if days_back:
            try:
                days = int(days_back)
                since_date = timezone.now() - timezone.timedelta(days=days)
                user_reviews = user_reviews.filter(created_at__gte=since_date)
            except ValueError:
                pass
        
        # Order by creation date (most recent first)
        user_reviews = user_reviews.order_by('-created_at')
        
        # Paginate the results
        page = self.paginate_queryset(user_reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(user_reviews, many=True)
        return Response(serializer.data)

    # ...existing code...


class ExpertReviewViewSet(viewsets.ModelViewSet):
    """
    Expert review management for agricultural extension officers,
    nutritionists, and industry experts.
    """
    
    queryset = ExpertReview.objects.select_related(
        'expert', 'product'
    ).filter(is_published=True)
    
    serializer_class = ExpertReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['expert_type', 'verified_expert', 'is_featured', 'product']
    search_fields = ['title', 'content', 'quality_assessment', 'recommendations']
    ordering_fields = ['created_at', 'overall_rating']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Auto-assign expert"""
        serializer.save(expert=self.request.user)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured expert reviews"""
        featured_reviews = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_expert_type(self, request):
        """Get reviews grouped by expert type"""
        expert_type = request.query_params.get('type')
        if not expert_type:
            return Response(
                {'error': 'type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.get_queryset().filter(expert_type=expert_type)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class ReviewRecipeViewSet(viewsets.ModelViewSet):
    """
    Recipe suggestions linked to product reviews.
    """
    
    queryset = ReviewRecipe.objects.select_related(
        'author', 'review'
    ).all()
    
    serializer_class = ReviewRecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'review__product']
    search_fields = ['title', 'description', 'ingredients']
    ordering_fields = ['created_at', 'likes_count', 'prep_time', 'cook_time']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Auto-assign author"""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like a recipe"""
        recipe = self.get_object()
        recipe.likes_count += 1
        recipe.save()
        
        return Response({
            'likes_count': recipe.likes_count,
            'message': 'Recipe liked successfully'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def share(self, request, pk=None):
        """Share a recipe"""
        recipe = self.get_object()
        recipe.shares_count += 1
        recipe.save()
        
        return Response({
            'shares_count': recipe.shares_count,
            'message': 'Recipe shared successfully'
        })


class SeasonalInsightViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Seasonal product insights based on review data.
    """
    
    queryset = SeasonalInsight.objects.select_related('product').all()
    serializer_class = SeasonalInsightSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['season', 'region', 'product']
    ordering_fields = ['average_rating', 'review_count', 'quality_score']
    ordering = ['-average_rating']
    
    @action(detail=False, methods=['get'])
    def current_season(self, request):
        """Get insights for current season"""
        # This would determine current season based on location/date
        # For now, return all seasons
        insights = self.get_queryset()
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_region(self, request):
        """Get insights filtered by region"""
        region = request.query_params.get('region')
        if not region:
            return Response(
                {'error': 'region parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        insights = self.get_queryset().filter(region__icontains=region)
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)


class PeerRecommendationViewSet(viewsets.ModelViewSet):
    """
    Farmer-to-farmer peer recommendation system for product endorsements
    and knowledge sharing.
    """
    
    queryset = PeerRecommendation.objects.select_related(
        'recommender', 'product', 'farmer_recommended'
    ).prefetch_related(
        'votes', 'interactions'
    ).filter(is_active=True)
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'recommendation_type', 'recommendation_strength', 'verified_peer',
        'is_featured', 'product', 'recommender'
    ]
    search_fields = ['title', 'content', 'results_achieved', 'conditions_for_success']
    ordering_fields = [
        'created_at', 'peer_helpful_votes', 'helpfulness_percentage'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PeerRecommendationCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return PeerRecommendationDetailSerializer
        return PeerRecommendationListSerializer
    
    def get_queryset(self):
        """Filter recommendations based on user context"""
        queryset = super().get_queryset()
        
        # Filter by region if provided
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(
                Q(relevant_regions__icontains=region) | Q(relevant_regions=[])
            )
        
        # Filter by season if provided
        season = self.request.query_params.get('season')
        if season:
            queryset = queryset.filter(
                Q(seasonal_relevance__icontains=season) | Q(seasonal_relevance=[])
            )
        
        # Filter featured recommendations
        if self.request.query_params.get('featured') == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Filter by recommendation type
        rec_type = self.request.query_params.get('type')
        if rec_type:
            queryset = queryset.filter(recommendation_type=rec_type)
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign recommender and verify farmer status"""
        # Check if user is a farmer
        if not hasattr(self.request.user, 'farmer_profile'):
            raise serializers.ValidationError("Only farmers can create peer recommendations")
        
        # Auto-verify if farmer has significant experience
        farmer_profile = self.request.user.farmer_profile
        verified_peer = farmer_profile.years_of_experience >= 5 and farmer_profile.organic_certified
        
        serializer.save(
            recommender=self.request.user,
            verified_peer=verified_peer
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """Vote on the helpfulness of a peer recommendation"""
        recommendation = self.get_object()
        
        # Check if user is a farmer
        if not hasattr(request.user, 'farmer_profile'):
            return Response(
                {'error': 'Only farmers can vote on peer recommendations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        is_helpful = request.data.get('is_helpful')
        comment = request.data.get('comment', '')
        
        if is_helpful is None:
            return Response(
                {'error': 'is_helpful field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update vote
        vote, created = PeerRecommendationVote.objects.update_or_create(
            recommendation=recommendation,
            voter=request.user,
            defaults={'is_helpful': is_helpful, 'comment': comment}
        )
        
        # Update recommendation vote counts
        recommendation.peer_helpful_votes = recommendation.votes.filter(is_helpful=True).count()
        recommendation.peer_total_votes = recommendation.votes.count()
        recommendation.save(update_fields=['peer_helpful_votes', 'peer_total_votes'])
        
        serializer = PeerRecommendationVoteSerializer(vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def interact(self, request, pk=None):
        """Record interaction with a peer recommendation"""
        recommendation = self.get_object()
        
        serializer = PeerRecommendationInteractionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                recommendation=recommendation,
                user=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending peer recommendations"""
        # Recommendations with high recent interaction
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=30)
        
        trending = self.get_queryset().filter(
            created_at__gte=recent_date
        ).annotate(
            recent_interactions=Count('interactions', filter=Q(interactions__created_at__gte=recent_date))
        ).order_by('-recent_interactions', '-peer_helpful_votes')[:10]
        
        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured peer recommendations"""
        featured = self.get_queryset().filter(is_featured=True).order_by('-created_at')[:10]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def for_me(self, request):
        """Get personalized recommendations for the current farmer"""
        if not hasattr(request.user, 'farmer_profile'):
            return Response(
                {'error': 'Only farmers can get personalized recommendations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        farmer_profile = request.user.farmer_profile
        
        # Get recommendations relevant to farmer's crops and region
        queryset = self.get_queryset()
        
        # Filter by farmer's primary crops
        if farmer_profile.primary_crops:
            queryset = queryset.filter(
                Q(product__name__in=farmer_profile.primary_crops) |
                Q(conditions_for_success__icontains=' '.join(farmer_profile.primary_crops))
            )
        
        # Order by relevance
        recommendations = queryset.order_by('-verified_peer', '-peer_helpful_votes')[:20]
        
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Get recommendations for a specific product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendations = self.get_queryset().filter(
            product_id=product_id,
            recommendation_type='product_endorsement'
        ).order_by('-verified_peer', '-peer_helpful_votes')
        
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_farmer(self, request):
        """Get recommendations for working with a specific farmer"""
        farmer_id = request.query_params.get('farmer_id')
        if not farmer_id:
            return Response(
                {'error': 'farmer_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendations = self.get_queryset().filter(
            farmer_recommended_id=farmer_id,
            recommendation_type='farmer_endorsement'
        ).order_by('-verified_peer', '-peer_helpful_votes')
        
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)


class FarmerNetworkViewSet(viewsets.ModelViewSet):
    """
    Farmer networking system for building trusted connections
    """
    
    queryset = FarmerNetwork.objects.select_related('follower', 'following')
    serializer_class = FarmerNetworkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['trust_level']
    ordering_fields = ['created_at', 'success_rate']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter network connections for the authenticated user"""
        if not hasattr(self.request.user, 'farmer_profile'):
            return FarmerNetwork.objects.none()
        
        return super().get_queryset().filter(
            Q(follower=self.request.user) | Q(following=self.request.user)
        )
    
    def perform_create(self, serializer):
        """Create farmer network connection"""
        # Check if user is a farmer
        if not hasattr(self.request.user, 'farmer_profile'):
            raise serializers.ValidationError("Only farmers can create network connections")
        
        serializer.save(follower=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_network(self, request):
        """Get current user's farmer network"""
        following = FarmerNetwork.objects.filter(follower=request.user)
        followers = FarmerNetwork.objects.filter(following=request.user)
        
        return Response({
            'following': FarmerNetworkSerializer(following, many=True).data,
            'followers': FarmerNetworkSerializer(followers, many=True).data,
            'following_count': following.count(),
            'followers_count': followers.count()
        })
    
    @action(detail=False, methods=['get'])
    def recommended_farmers(self, request):
        """Get recommended farmers to follow based on similar interests"""
        if not hasattr(request.user, 'farmer_profile'):
            return Response(
                {'error': 'Only farmers can get farmer recommendations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        farmer_profile = request.user.farmer_profile
        
        # Find farmers with similar crops or in same region
        similar_farmers = User.objects.filter(
            farmer_profile__isnull=False
        ).exclude(id=request.user.id).exclude(
            farmer_followers__follower=request.user
        )
        
        # Filter by similar crops if available
        if farmer_profile.primary_crops:
            similar_farmers = similar_farmers.filter(
                farmer_profile__primary_crops__overlap=farmer_profile.primary_crops
            )
        
        # Get top recommended farmers
        recommended = similar_farmers.order_by(
            '-farmer_profile__years_of_experience',
            '-farmer_profile__organic_certified'
        )[:10]
        
        from .serializers import FarmerProfileSerializer
        serializer = FarmerProfileSerializer(recommended, many=True)
        return Response(serializer.data)
