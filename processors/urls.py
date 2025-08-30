"""
AgriConnect Processors App URLs
URL configuration for processing recipes and processor integration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'profiles', views.ProcessorProfileViewSet, basename='processor-profiles')
router.register(r'recipes', views.ProcessingRecipeViewSet, basename='processing-recipes')
router.register(r'ratings', views.RecipeRatingViewSet, basename='recipe-ratings')
router.register(r'comments', views.RecipeCommentViewSet, basename='recipe-comments')
router.register(r'usage-logs', views.RecipeUsageLogViewSet, basename='recipe-usage-logs')

app_name = 'processors'

urlpatterns = [
    # API Root
    path('', include(router.urls)),
]
