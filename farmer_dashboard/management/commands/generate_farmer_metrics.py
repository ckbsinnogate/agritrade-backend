"""
Generate Daily Farmer Metrics Management Command
Automatically calculates and stores daily metrics for all farmers
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Avg, Q
from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from farmer_dashboard.models import FarmerDashboardMetrics

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate daily farmer dashboard metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to generate metrics for (YYYY-MM-DD). Defaults to yesterday.',
        )
        parser.add_argument(
            '--farmer-id',
            type=int,
            help='Generate metrics for specific farmer ID only',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing metrics for the date',
        )
    
    def handle(self, *args, **options):
        # Determine date
        if options['date']:
            try:
                target_date = date.fromisoformat(options['date'])
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f"Invalid date format: {options['date']}. Use YYYY-MM-DD")
                )
                return
        else:
            target_date = date.today() - timedelta(days=1)  # Default to yesterday
        
        # Get farmers to process
        if options['farmer_id']:
            try:
                farmers = User.objects.filter(id=options['farmer_id'])
                if not farmers.exists():
                    self.stdout.write(
                        self.style.ERROR(f"Farmer with ID {options['farmer_id']} not found")
                    )
                    return
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f"Invalid farmer ID: {options['farmer_id']}")
                )
                return
        else:            # Get all farmers (users who have products or sales)
            farmers = User.objects.filter(
                Q(products__isnull=False) |
                Q(sales__isnull=False)
            ).distinct()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Generating metrics for {farmers.count()} farmers for date: {target_date}"
            )
        )
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for farmer in farmers:
            try:
                # Check if metrics already exist
                existing_metrics = FarmerDashboardMetrics.objects.filter(
                    farmer=farmer, 
                    date=target_date
                ).first()
                
                if existing_metrics and not options['overwrite']:
                    self.stdout.write(
                        f"Metrics already exist for farmer {farmer.username} on {target_date}. "
                        f"Use --overwrite to update."
                    )
                    continue
                
                # Calculate metrics
                metrics_data = self.calculate_farmer_metrics(farmer, target_date)
                
                # Create or update metrics
                if existing_metrics:
                    for key, value in metrics_data.items():
                        setattr(existing_metrics, key, value)
                    existing_metrics.save()
                    updated_count += 1
                    action = "Updated"
                else:
                    FarmerDashboardMetrics.objects.create(
                        farmer=farmer,
                        date=target_date,
                        **metrics_data
                    )
                    created_count += 1
                    action = "Created"
                
                self.stdout.write(
                    f"{action} metrics for farmer: {farmer.username} "
                    f"(Revenue: {metrics_data['total_revenue']}, "
                    f"Orders: {metrics_data['orders_count']})"
                )
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Error processing farmer {farmer.username}: {str(e)}"
                    )
                )
        
        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("METRICS GENERATION SUMMARY"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(f"Date: {target_date}")
        self.stdout.write(f"Total farmers processed: {farmers.count()}")
        self.stdout.write(f"Metrics created: {created_count}")
        self.stdout.write(f"Metrics updated: {updated_count}")
        self.stdout.write(f"Errors: {error_count}")
        self.stdout.write(self.style.SUCCESS("="*50))
    
    def calculate_farmer_metrics(self, farmer, target_date):
        """Calculate all metrics for a farmer on a specific date"""
        
        # Import models here to avoid circular imports
        try:
            from products.models import Product
            from orders.models import Order, OrderItem
            from traceability.models import Farm
        except ImportError as e:
            self.stdout.write(
                self.style.WARNING(f"Could not import required models: {e}")
            )
            # Return default metrics if models not available
            return self.get_default_metrics()
        
        # Date range for the specific day
        start_date = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.min.time())
        )
        end_date = start_date + timedelta(days=1)
        
        # Revenue Metrics
        orders_on_date = Order.objects.filter(
            seller=farmer,
            order_date__gte=start_date,
            order_date__lt=end_date
        )
        
        total_revenue = orders_on_date.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        orders_count = orders_on_date.count()
        
        products_sold = OrderItem.objects.filter(
            order__in=orders_on_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        average_order_value = orders_on_date.aggregate(
            avg=Avg('total_amount')
        )['avg'] or Decimal('0')
        
        # Product Metrics (total counts, not just for the day)
        products = Product.objects.filter(farmer=farmer)
        total_products = products.count()
        active_products = products.filter(status='active').count()
        low_stock_products = products.filter(quantity_available__lt=10).count()
        out_of_stock_products = products.filter(quantity_available=0).count()
        
        # Customer Metrics (cumulative up to this date)
        all_orders = Order.objects.filter(
            seller=farmer,
            order_date__lt=end_date
        )
        
        total_customers = all_orders.values('buyer').distinct().count()
        
        # New customers on this specific date
        new_customers = orders_on_date.values('buyer').distinct().count()
        
        # Returning customers (who had orders before this date)
        previous_customers = Order.objects.filter(
            seller=farmer,
            order_date__lt=start_date
        ).values('buyer').distinct()
        
        returning_customers = orders_on_date.filter(
            buyer__in=previous_customers
        ).values('buyer').distinct().count()
        
        # Farm Metrics
        farms = Farm.objects.filter(farmer=farmer)
        farms_registered = farms.count()
        total_farm_area = farms.aggregate(
            total=Sum('farm_size_hectares')
        )['total'] or Decimal('0')
        
        return {
            'total_revenue': total_revenue,
            'orders_count': orders_count,
            'products_sold': products_sold,
            'average_order_value': average_order_value,
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'new_customers': new_customers,
            'returning_customers': returning_customers,
            'total_customers': total_customers,
            'farms_registered': farms_registered,
            'total_farm_area': total_farm_area,
        }
    
    def get_default_metrics(self):
        """Return default metrics when models are not available"""
        return {
            'total_revenue': Decimal('0'),
            'orders_count': 0,
            'products_sold': 0,
            'average_order_value': Decimal('0'),
            'total_products': 0,
            'active_products': 0,
            'low_stock_products': 0,
            'out_of_stock_products': 0,
            'new_customers': 0,
            'returning_customers': 0,
            'total_customers': 0,
            'farms_registered': 0,
            'total_farm_area': Decimal('0'),
        }
