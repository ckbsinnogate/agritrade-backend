
# Add this to your main urls.py file

from django.urls import path, include
from ai_views import (
    CropAnalysisView, DiseaseDetectionView, MarketPredictionView,
    WeatherAnalysisView, YieldPredictionView, FarmingAdviceView, AIStatusView
)

# AI Service URL patterns
ai_urlpatterns = [
    path('ai/crop-analysis/', CropAnalysisView.as_view(), name='ai_crop_analysis'),
    path('ai/disease-detection/', DiseaseDetectionView.as_view(), name='ai_disease_detection'),
    path('ai/market-prediction/', MarketPredictionView.as_view(), name='ai_market_prediction'),
    path('ai/weather-analysis/', WeatherAnalysisView.as_view(), name='ai_weather_analysis'),
    path('ai/yield-prediction/', YieldPredictionView.as_view(), name='ai_yield_prediction'),
    path('ai/farming-advice/', FarmingAdviceView.as_view(), name='ai_farming_advice'),
    path('ai/status/', AIStatusView.as_view(), name='ai_status'),
]

# Add to your main urlpatterns
urlpatterns = [
    # ... your existing patterns ...
    path('api/', include(ai_urlpatterns)),
]
