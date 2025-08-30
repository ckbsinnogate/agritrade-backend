"""
Create Sample Farmer Dashboard Data Management Command
Creates sample data for testing and demonstration purposes
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from farmer_dashboard.models import (
    FarmerDashboardPreferences, FarmerAlert, 
    FarmerDashboardMetrics, FarmerGoal
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample farmer dashboard data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--farmers',
            type=int,
            default=5,
            help='Number of sample farmers to create data for',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of historical data to create',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing sample data before creating new data',
        )
    
    def handle(self, *args, **options):
        if options['clean']:
            self.clean_sample_data()
        
        farmers_count = options['farmers']
        days_count = options['days']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Creating sample farmer dashboard data for {farmers_count} farmers "
                f"with {days_count} days of history..."
            )
        )
        
        # Get or create sample farmers
        farmers = self.get_or_create_sample_farmers(farmers_count)
        
        # Create sample data for each farmer
        for farmer in farmers:
            self.create_farmer_preferences(farmer)
            self.create_farmer_alerts(farmer)
            self.create_farmer_goals(farmer)
            self.create_farmer_metrics(farmer, days_count)
            
            self.stdout.write(f"Created sample data for farmer: {farmer.username}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSample data creation completed for {len(farmers)} farmers!"
            )
        )
    
    def clean_sample_data(self):
        """Clean existing sample data"""
        self.stdout.write("Cleaning existing sample data...")
        
        # Delete sample data (identify by usernames starting with 'sample_farmer')
        sample_farmers = User.objects.filter(username__startswith='sample_farmer')
        
        FarmerDashboardPreferences.objects.filter(farmer__in=sample_farmers).delete()
        FarmerAlert.objects.filter(farmer__in=sample_farmers).delete()
        FarmerGoal.objects.filter(farmer__in=sample_farmers).delete()
        FarmerDashboardMetrics.objects.filter(farmer__in=sample_farmers).delete()
        
        self.stdout.write("Sample data cleaned.")
    
    def get_or_create_sample_farmers(self, count):
        """Get or create sample farmers"""
        farmers = []
        
        for i in range(1, count + 1):
            username = f'sample_farmer_{i}'
            email = f'farmer{i}@example.com'
            
            farmer, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Sample',
                    'last_name': f'Farmer {i}',
                    'is_active': True,
                }
            )
            
            if created:
                farmer.set_password('samplepass123')
                farmer.save()
                self.stdout.write(f"Created sample farmer: {username}")
            
            farmers.append(farmer)
        
        return farmers
    
    def create_farmer_preferences(self, farmer):
        """Create sample preferences for farmer"""
        preferences, created = FarmerDashboardPreferences.objects.get_or_create(
            farmer=farmer,
            defaults={
                'default_currency': random.choice(['GHS', 'USD', 'NGN']),
                'preferred_language': random.choice(['en', 'tw', 'ha']),
                'dashboard_theme': random.choice(['light', 'dark', 'auto']),
                'weather_alerts': random.choice([True, False]),
                'market_price_alerts': True,
                'order_notifications': True,
                'payment_reminders': True,
                'show_revenue_trends': True,
                'show_crop_analytics': random.choice([True, False]),
                'show_market_insights': True,
            }
        )
    
    def create_farmer_alerts(self, farmer):
        """Create sample alerts for farmer"""
        alert_types = ['weather', 'market', 'inventory', 'order', 'payment', 'crop', 'general']
        priorities = ['low', 'medium', 'high', 'critical']
        
        # Create 3-8 random alerts
        for _ in range(random.randint(3, 8)):
            alert_type = random.choice(alert_types)
            priority = random.choice(priorities)
            
            # Generate contextual messages based on alert type
            messages = {
                'weather': [
                    'Heavy rainfall expected in your area this week',
                    'Drought conditions detected, consider irrigation',
                    'Perfect weather conditions for planting',
                    'Temperature fluctuations may affect crop growth'
                ],
                'market': [
                    'Tomato prices increased by 15% this week',
                    'High demand for organic vegetables in your region',
                    'New buyer interested in your maize crop',
                    'Market prices stabilizing after recent volatility'
                ],
                'inventory': [
                    'Low stock alert: Tomatoes below 10 units',
                    'Product out of stock: Rice varieties',
                    'Inventory update needed for seasonal crops',
                    'Popular product running low: Fresh vegetables'
                ],
                'order': [
                    'New order received for 50kg maize',
                    'Order delivery scheduled for tomorrow',
                    'Payment confirmed for recent order',
                    'Order status updated to processing'
                ],
                'payment': [
                    'Payment due in 3 days for equipment lease',
                    'Payment received for last week\'s delivery',
                    'Invoice generated for bulk order',
                    'Monthly subscription payment reminder'
                ],
                'crop': [
                    'Optimal time to plant tomatoes in your region',
                    'Pest alert: Monitor for aphids on vegetables',
                    'Harvest season approaching for maize crops',
                    'Soil moisture levels optimal for planting'
                ],
                'general': [
                    'Welcome to AgriConnect farmer dashboard!',
                    'New features available in the mobile app',
                    'Training session scheduled for organic farming',
                    'Community meetup planned for next week'
                ]
            }
            
            FarmerAlert.objects.create(
                farmer=farmer,
                title=f"{alert_type.title()} Alert",
                message=random.choice(messages[alert_type]),
                alert_type=alert_type,
                priority=priority,
                is_read=random.choice([True, False]),
                is_archived=random.choice([True, False]) if random.choice([True, False]) else False,
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
    
    def create_farmer_goals(self, farmer):
        """Create sample goals for farmer"""
        goal_types = ['revenue', 'production', 'customers', 'farms', 'sustainability']
        
        # Create 2-4 goals
        for _ in range(random.randint(2, 4)):
            goal_type = random.choice(goal_types)
            
            # Generate contextual goals
            goals_data = {
                'revenue': {
                    'title': 'Quarterly Revenue Target',
                    'description': 'Achieve target revenue for this quarter',
                    'target_value': Decimal(str(random.randint(5000, 20000))),
                    'unit': 'GHS'
                },
                'production': {
                    'title': 'Increase Crop Yield',
                    'description': 'Improve production efficiency and yield per hectare',
                    'target_value': Decimal(str(random.randint(100, 500))),
                    'unit': 'tons'
                },
                'customers': {
                    'title': 'Customer Base Expansion',
                    'description': 'Acquire new customers for product portfolio',
                    'target_value': Decimal(str(random.randint(50, 200))),
                    'unit': 'customers'
                },
                'farms': {
                    'title': 'Farm Area Expansion',
                    'description': 'Expand cultivated area for increased production',
                    'target_value': Decimal(str(random.randint(5, 50))),
                    'unit': 'hectares'
                },
                'sustainability': {
                    'title': 'Organic Certification',
                    'description': 'Achieve organic certification for premium pricing',
                    'target_value': Decimal('100'),
                    'unit': 'percent'
                }
            }
            
            goal_data = goals_data[goal_type]
            current_value = goal_data['target_value'] * Decimal(str(random.uniform(0.1, 0.8)))
            
            FarmerGoal.objects.create(
                farmer=farmer,
                title=goal_data['title'],
                description=goal_data['description'],
                goal_type=goal_type,
                target_value=goal_data['target_value'],
                current_value=current_value,
                unit=goal_data['unit'],
                start_date=date.today() - timedelta(days=random.randint(0, 90)),
                target_date=date.today() + timedelta(days=random.randint(30, 365)),
                status=random.choice(['active', 'active', 'active', 'completed'])
            )
    
    def create_farmer_metrics(self, farmer, days_count):
        """Create sample daily metrics for farmer"""
        for i in range(days_count):
            metric_date = date.today() - timedelta(days=i)
            
            # Generate realistic sample data with some randomness
            base_revenue = random.uniform(100, 1000)
            daily_variation = random.uniform(0.5, 1.5)
            
            FarmerDashboardMetrics.objects.get_or_create(
                farmer=farmer,
                date=metric_date,
                defaults={
                    'total_revenue': Decimal(str(base_revenue * daily_variation)),
                    'orders_count': random.randint(0, 10),
                    'products_sold': random.randint(0, 50),
                    'average_order_value': Decimal(str(random.uniform(50, 300))),
                    'total_products': random.randint(5, 25),
                    'active_products': random.randint(3, 20),
                    'low_stock_products': random.randint(0, 5),
                    'out_of_stock_products': random.randint(0, 3),
                    'new_customers': random.randint(0, 5),
                    'returning_customers': random.randint(0, 8),
                    'total_customers': random.randint(10, 100),                    'farms_registered': random.randint(1, 5),
                    'total_farm_area': Decimal(str(random.uniform(1, 20))),
                }
            )
