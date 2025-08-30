"""
AgriConnect AI Services URLs
URL patterns for AI-powered agricultural services
"""

from django.urls import path
from ai_views import (
    CropAnalysisView, DiseaseDetectionView, MarketPredictionView,
    WeatherAnalysisView, YieldPredictionView, FarmingAdviceView, AIStatusView
)

app_name = 'ai'

urlpatterns = [
    # AI Service endpoints
    path('crop-analysis/', CropAnalysisView.as_view(), name='crop_analysis'),
    path('disease-detection/', DiseaseDetectionView.as_view(), name='disease_detection'),
    path('market-prediction/', MarketPredictionView.as_view(), name='market_prediction'),
    path('weather-analysis/', WeatherAnalysisView.as_view(), name='weather_analysis'),
    path('yield-prediction/', YieldPredictionView.as_view(), name='yield_prediction'),
    path('farming-advice/', FarmingAdviceView.as_view(), name='farming_advice'),
    path('status/', AIStatusView.as_view(), name='ai_status'),
]