"""
Farmer Dashboard Serializers
API serializers for farmer dashboard functionality
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Avg
from decimal import Decimal
import json

from .models import FarmerDashboardPreferences, FarmerAlert, FarmerDashboardMetrics, FarmerGoal

User = get_user_model()


class FarmerDashboardPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for farmer dashboard preferences"""
    
    class Meta:
        model = FarmerDashboardPreferences
        fields = [
            'default_currency', 'preferred_language', 'dashboard_theme',
            'weather_alerts', 'market_price_alerts', 'order_notifications',
            'payment_reminders', 'show_revenue_trends', 'show_crop_analytics',
            'show_market_insights', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FarmerAlertSerializer(serializers.ModelSerializer):
    """Serializer for farmer alerts"""
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = FarmerAlert
        fields = [
            'id', 'title', 'message', 'alert_type', 'priority',
            'is_read', 'is_archived', 'related_product_id',
            'related_order_id', 'related_farm_id', 'created_at',
            'expires_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'is_expired']


class FarmerDashboardMetricsSerializer(serializers.ModelSerializer):
    """Serializer for farmer dashboard metrics"""
    
    class Meta:
        model = FarmerDashboardMetrics
        fields = [
            'date', 'total_revenue', 'orders_count', 'products_sold',
            'average_order_value', 'total_products', 'active_products',
            'low_stock_products', 'out_of_stock_products', 'new_customers',
            'returning_customers', 'total_customers', 'farms_registered',
            'total_farm_area', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FarmerGoalSerializer(serializers.ModelSerializer):
    """Serializer for farmer goals"""
    progress_percentage = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = FarmerGoal
        fields = [
            'id', 'title', 'description', 'goal_type', 'target_value',
            'current_value', 'unit', 'start_date', 'target_date',
            'status', 'progress_percentage', 'days_remaining',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'progress_percentage', 'days_remaining']


class FarmerOverviewSerializer(serializers.Serializer):
    """Serializer for farmer dashboard overview"""
    
    # Quick Stats
    today_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    week_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    month_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    year_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Orders
    pending_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    
    # Products
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    
    # Farms
    total_farms = serializers.IntegerField()
    verified_farms = serializers.IntegerField()
    total_farm_area = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Customers
    total_customers = serializers.IntegerField()
    repeat_customers = serializers.IntegerField()
    
    # Recent Activity
    recent_orders = serializers.JSONField()
    recent_products = serializers.JSONField()
    low_stock_alerts = serializers.JSONField()
    
    # Goals Progress
    active_goals = serializers.JSONField()
    
    # Market Insights
    trending_crops = serializers.JSONField()
    price_trends = serializers.JSONField()
    
    # Weather Info
    weather_alerts = serializers.JSONField()
    
    # Performance Metrics
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    customer_satisfaction = serializers.DecimalField(max_digits=3, decimal_places=2)
    revenue_growth = serializers.DecimalField(max_digits=5, decimal_places=2)


class FarmerProductSummarySerializer(serializers.Serializer):
    """Serializer for farmer product summary"""
    
    id = serializers.CharField()
    name = serializers.CharField()
    category = serializers.CharField()
    price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = serializers.IntegerField()
    unit = serializers.CharField()
    status = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    orders_count = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class FarmerOrderSummarySerializer(serializers.Serializer):
    """Serializer for farmer order summary"""
    
    id = serializers.CharField()
    order_number = serializers.CharField()
    buyer = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField()
    payment_status = serializers.CharField()
    order_date = serializers.DateTimeField()
    expected_delivery_date = serializers.DateTimeField()
    items_count = serializers.IntegerField()
    delivery_city = serializers.CharField()
    delivery_region = serializers.CharField()


class FarmerFarmSummarySerializer(serializers.Serializer):
    """Serializer for farmer farm summary"""
    
    id = serializers.CharField()
    name = serializers.CharField()
    location = serializers.CharField()
    farm_size_hectares = serializers.DecimalField(max_digits=10, decimal_places=2)
    organic_certified = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    primary_crops = serializers.JSONField()
    registration_number = serializers.CharField()
    created_at = serializers.DateTimeField()


class WeatherInsightSerializer(serializers.Serializer):
    """Serializer for weather insights"""
    
    location = serializers.CharField()
    current_temperature = serializers.DecimalField(max_digits=5, decimal_places=2)
    humidity = serializers.DecimalField(max_digits=5, decimal_places=2)
    weather_condition = serializers.CharField()
    rainfall_prediction = serializers.DecimalField(max_digits=5, decimal_places=2)
    alerts = serializers.JSONField()
    recommendations = serializers.JSONField()
    forecast = serializers.JSONField()


class MarketInsightSerializer(serializers.Serializer):
    """Serializer for market insights"""
    
    trending_products = serializers.JSONField()
    price_changes = serializers.JSONField()
    demand_forecast = serializers.JSONField()
    competitor_analysis = serializers.JSONField()
    opportunities = serializers.JSONField()
    recommendations = serializers.JSONField()
