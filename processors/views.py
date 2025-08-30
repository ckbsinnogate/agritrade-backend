"""
AgriConnect Processing Recipes Views
Complete API endpoints for recipe sharing and processor integration

Features:
- Recipe CRUD operations
- Recipe rating and review system
- Recipe usage tracking
- Processor profile management
- Technical support and knowledge sharing
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    ProcessingRecipe, RecipeRating, RecipeUsageLog, 
    RecipeComment, ProcessorProfile
)
from .serializers import (
    ProcessingRecipeListSerializer, ProcessingRecipeDetailSerializer,
    ProcessingRecipeCreateUpdateSerializer, RecipeRatingSerializer,
    RecipeUsageLogSerializer, RecipeCommentSerializer, ProcessorProfileSerializer
)


class ProcessorProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for processor profile management
    """
    
    queryset = ProcessorProfile.objects.select_related('user').all()
    serializer_class = ProcessorProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['processor_type', 'is_verified', 'seasonal_operation']
    search_fields = ['business_name', 'user__username', 'specializations']
    ordering_fields = ['created_at', 'average_recipe_rating', 'total_recipes_shared']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by service radius if location provided
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 50)
        
        if lat and lng:
            # Note: This is a simplified distance filter
            # In production, use PostGIS for proper geospatial queries
            queryset = queryset.filter(service_radius_km__gte=radius)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def recipes(self, request, pk=None):
        """Get all recipes by this processor"""
        processor_profile = self.get_object()
        recipes = ProcessingRecipe.objects.filter(
            processor=processor_profile.user,
            is_public=True
        ).order_by('-created_at')
        
        serializer = ProcessingRecipeListSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get processor statistics"""
        processor_profile = self.get_object()
        
        recipes = ProcessingRecipe.objects.filter(processor=processor_profile.user)
        usage_logs = RecipeUsageLog.objects.filter(recipe__processor=processor_profile.user)
        
        stats = {
            'total_recipes': recipes.count(),
            'public_recipes': recipes.filter(is_public=True).count(),
            'verified_recipes': recipes.filter(is_verified=True).count(),
            'total_recipe_uses': usage_logs.count(),
            'successful_uses': usage_logs.filter(success=True).count(),
            'average_recipe_rating': recipes.aggregate(avg=Avg('average_rating'))['avg'] or 0,
            'total_ratings_received': RecipeRating.objects.filter(recipe__processor=processor_profile.user).count(),
            'recent_activity': usage_logs.filter(
                used_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        return Response(stats)


class ProcessingRecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for processing recipe management
    """
    
    queryset = ProcessingRecipe.objects.select_related('processor').prefetch_related('ratings', 'comments').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'skill_level_required', 'status', 'is_public', 'is_verified',
        'processor__processor_profile__processor_type', 'seasonal_availability'
    ]
    search_fields = [
        'recipe_name', 'description', 'tags', 'processor__username',
        'processor__processor_profile__business_name'
    ]
    ordering_fields = [
        'created_at', 'updated_at', 'average_rating', 'times_used',
        'processing_time_minutes', 'expected_yield_percentage'
    ]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProcessingRecipeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProcessingRecipeCreateUpdateSerializer
        else:
            return ProcessingRecipeDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by public recipes for non-owners
        if not self.request.user.is_authenticated:
            return queryset.filter(is_public=True, status='public')
        
        # Show all public recipes plus user's own recipes
        if self.action == 'list':
            return queryset.filter(
                Q(is_public=True) | Q(processor=self.request.user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(processor=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        """Rate a recipe"""
        recipe = self.get_object()
        
        # Check if user already rated this recipe
        existing_rating = RecipeRating.objects.filter(
            recipe=recipe, user=request.user
        ).first()
        
        if existing_rating:
            serializer = RecipeRatingSerializer(existing_rating, data=request.data, partial=True)
        else:
            serializer = RecipeRatingSerializer(data=request.data)
        
        if serializer.is_valid():
            if existing_rating:
                serializer.save()
            else:
                serializer.save(recipe=recipe, user=request.user)
            
            # Update recipe average rating
            self._update_recipe_rating(recipe)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def log_usage(self, request, pk=None):
        """Log usage of a recipe"""
        recipe = self.get_object()
        
        serializer = RecipeUsageLogSerializer(data=request.data)
        if serializer.is_valid():
            usage_log = serializer.save(recipe=recipe, user=request.user)
            
            # Update recipe usage count
            recipe.times_used += 1
            recipe.save(update_fields=['times_used'])
            
            # Update success rate if applicable
            if usage_log.success is not None:
                self._update_recipe_success_rate(recipe)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        """Add a comment to a recipe"""
        recipe = self.get_object()
        
        serializer = RecipeCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar recipes"""
        recipe = self.get_object()
        
        # Find similar recipes based on tags, input materials, and processor type
        similar_recipes = ProcessingRecipe.objects.filter(
            is_public=True,
            status='public'
        ).exclude(id=recipe.id)
        
        # Filter by similar tags
        if recipe.tags:
            similar_recipes = similar_recipes.filter(
                tags__overlap=recipe.tags
            )
        
        # Filter by processor type if available
        if hasattr(recipe.processor, 'processor_profile'):
            processor_type = recipe.processor.processor_profile.processor_type
            similar_recipes = similar_recipes.filter(
                processor__processor_profile__processor_type=processor_type
            )
        
        similar_recipes = similar_recipes.order_by('-average_rating', '-times_used')[:5]
        
        serializer = ProcessingRecipeListSerializer(similar_recipes, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending recipes"""
        # Get recipes with high usage in the last 30 days
        recent_date = timezone.now() - timedelta(days=30)
        trending_recipes = ProcessingRecipe.objects.filter(
            is_public=True,
            status='public',
            usage_logs__used_at__gte=recent_date
        ).annotate(
            recent_uses=Count('usage_logs', filter=Q(usage_logs__used_at__gte=recent_date))
        ).order_by('-recent_uses', '-average_rating')[:10]
        
        serializer = ProcessingRecipeListSerializer(trending_recipes, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured recipes (high-rated and verified)"""
        featured_recipes = ProcessingRecipe.objects.filter(
            is_public=True,
            status='verified',
            average_rating__gte=4.0,
            rating_count__gte=5
        ).order_by('-average_rating', '-times_used')[:10]
        
        serializer = ProcessingRecipeListSerializer(featured_recipes, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_recipes(self, request):
        """Get current user's recipes"""
        my_recipes = ProcessingRecipe.objects.filter(
            processor=request.user
        ).order_by('-created_at')
        
        serializer = ProcessingRecipeListSerializer(my_recipes, many=True, context={'request': request})
        return Response(serializer.data)
    
    def _update_recipe_rating(self, recipe):
        """Update recipe average rating"""
        ratings = recipe.ratings.all()
        if ratings.exists():
            avg_rating = ratings.aggregate(avg=Avg('overall_rating'))['avg']
            recipe.average_rating = round(avg_rating, 2)
            recipe.rating_count = ratings.count()
            recipe.save(update_fields=['average_rating', 'rating_count'])
    
    def _update_recipe_success_rate(self, recipe):
        """Update recipe success rate"""
        usage_logs = recipe.usage_logs.filter(success__isnull=False)
        if usage_logs.exists():
            successful_uses = usage_logs.filter(success=True).count()
            total_uses = usage_logs.count()
            success_rate = (successful_uses / total_uses) * 100
            recipe.success_rate_percentage = round(success_rate, 2)
            recipe.save(update_fields=['success_rate_percentage'])


class RecipeRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for recipe ratings
    """
    
    queryset = RecipeRating.objects.select_related('recipe', 'user').all()
    serializer_class = RecipeRatingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['recipe', 'overall_rating', 'would_recommend']
    ordering_fields = ['created_at', 'overall_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for recipe comments
    """
    
    queryset = RecipeComment.objects.select_related('recipe', 'user', 'parent').all()
    serializer_class = RecipeCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['recipe', 'is_question', 'is_answered']
    ordering_fields = ['created_at', 'helpful_count']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        """Mark a comment as helpful"""
        comment = self.get_object()
        comment.helpful_count += 1
        comment.save(update_fields=['helpful_count'])
        
        return Response({
            'helpful_count': comment.helpful_count,
            'message': 'Comment marked as helpful'
        })


class RecipeUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for recipe usage logs (read-only for analytics)
    """
    
    queryset = RecipeUsageLog.objects.select_related('recipe', 'user').all()
    serializer_class = RecipeUsageLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['recipe', 'success', 'user']
    ordering_fields = ['used_at']
    ordering = ['-used_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Users can only see their own usage logs or logs for their recipes
        return queryset.filter(
            Q(user=self.request.user) | Q(recipe__processor=self.request.user)
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get usage analytics"""
        queryset = self.get_queryset()
        
        total_uses = queryset.count()
        successful_uses = queryset.filter(success=True).count()
        
        analytics = {
            'total_uses': total_uses,
            'successful_uses': successful_uses,
            'success_rate': (successful_uses / total_uses * 100) if total_uses > 0 else 0,
            'average_batch_size': queryset.aggregate(avg=Avg('batch_size'))['avg'] or 0,
            'most_used_recipes': queryset.values('recipe__recipe_name').annotate(
                use_count=Count('id')
            ).order_by('-use_count')[:5],
            'recent_activity': queryset.filter(
                used_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        }
        
        return Response(analytics)
