"""
Farmer Dashboard Signals
Automatic triggers for dashboard updates and notifications
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from .models import FarmerDashboardPreferences, FarmerAlert

User = get_user_model()


@receiver(post_save, sender=User)
def create_farmer_dashboard_preferences(sender, instance, created, **kwargs):
    """Create default dashboard preferences when a farmer user is created"""
    if created:
        # Check if user is a farmer (has farmer role or creates products)
        try:
            # Create default preferences for all new users
            # They can be updated later when the user is identified as a farmer
            FarmerDashboardPreferences.objects.get_or_create(
                farmer=instance,
                defaults={
                    'default_currency': 'GHS',
                    'preferred_language': 'en',
                    'dashboard_theme': 'light',
                    'weather_alerts': True,
                    'market_price_alerts': True,
                    'order_notifications': True,
                    'payment_reminders': True,
                    'show_revenue_trends': True,
                    'show_crop_analytics': True,
                    'show_market_insights': True,
                }
            )
        except Exception as e:
            # Log error but don't break user creation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not create farmer dashboard preferences for user {instance.username}: {e}")


# Product-related signals
try:
    from products.models import Product
    
    @receiver(post_save, sender=Product)
    def product_created_alert(sender, instance, created, **kwargs):
        """Create alert when farmer creates a new product"""
        if created and instance.farmer:
            try:
                FarmerAlert.objects.create(
                    farmer=instance.farmer,
                    title='New Product Added',
                    message=f'Your product "{instance.name}" has been successfully added to the marketplace.',
                    alert_type='general',
                    priority='low'
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create product alert: {e}")
    
    @receiver(post_save, sender=Product)
    def low_stock_alert(sender, instance, **kwargs):
        """Create alert when product stock is low"""
        if instance.farmer and instance.quantity_available <= 5 and instance.quantity_available > 0:
            try:
                # Check if alert already exists for this product
                existing_alert = FarmerAlert.objects.filter(
                    farmer=instance.farmer,
                    alert_type='inventory',
                    related_product_id=str(instance.id),
                    is_archived=False
                ).first()
                
                if not existing_alert:
                    FarmerAlert.objects.create(
                        farmer=instance.farmer,
                        title='Low Stock Alert',
                        message=f'Your product "{instance.name}" is running low (only {instance.quantity_available} units left).',
                        alert_type='inventory',
                        priority='medium',
                        related_product_id=str(instance.id)
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create low stock alert: {e}")
    
    @receiver(post_save, sender=Product)
    def out_of_stock_alert(sender, instance, **kwargs):
        """Create alert when product is out of stock"""
        if instance.farmer and instance.quantity_available == 0:
            try:
                # Check if alert already exists for this product
                existing_alert = FarmerAlert.objects.filter(
                    farmer=instance.farmer,
                    alert_type='inventory',
                    related_product_id=str(instance.id),
                    is_archived=False,
                    title__icontains='Out of Stock'
                ).first()
                
                if not existing_alert:
                    FarmerAlert.objects.create(
                        farmer=instance.farmer,
                        title='Out of Stock Alert',
                        message=f'Your product "{instance.name}" is now out of stock. Consider restocking to continue sales.',
                        alert_type='inventory',
                        priority='high',
                        related_product_id=str(instance.id)
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create out of stock alert: {e}")

except ImportError:
    # Products app not available
    pass


# Order-related signals
try:
    from orders.models import Order
    
    @receiver(post_save, sender=Order)
    def new_order_alert(sender, instance, created, **kwargs):
        """Create alert when farmer receives a new order"""
        if created and instance.seller:
            try:
                FarmerAlert.objects.create(
                    farmer=instance.seller,
                    title='New Order Received',
                    message=f'You have received a new order #{instance.order_number} for {instance.total_amount} {instance.currency or "GHS"}.',
                    alert_type='order',
                    priority='medium',
                    related_order_id=str(instance.id)
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create new order alert: {e}")
    
    @receiver(post_save, sender=Order)
    def order_status_update_alert(sender, instance, **kwargs):
        """Create alert when order status is updated"""
        if instance.seller and not kwargs.get('created', False):
            try:
                # Only create alerts for significant status changes
                important_statuses = ['confirmed', 'shipped', 'delivered', 'cancelled']
                if instance.status in important_statuses:
                    
                    status_messages = {
                        'confirmed': 'has been confirmed and is being prepared',
                        'shipped': 'has been shipped and is on its way to the customer',
                        'delivered': 'has been successfully delivered to the customer',
                        'cancelled': 'has been cancelled'
                    }
                    
                    message = f'Order #{instance.order_number} {status_messages.get(instance.status, "status has been updated")}.'
                    
                    FarmerAlert.objects.create(
                        farmer=instance.seller,
                        title=f'Order {instance.status.title()}',
                        message=message,
                        alert_type='order',
                        priority='low' if instance.status == 'delivered' else 'medium',
                        related_order_id=str(instance.id)
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create order status alert: {e}")

except ImportError:
    # Orders app not available
    pass


# Farm-related signals
try:
    from traceability.models import Farm
    
    @receiver(post_save, sender=Farm)
    def farm_registered_alert(sender, instance, created, **kwargs):
        """Create alert when farmer registers a new farm"""
        if created and instance.farmer:
            try:
                FarmerAlert.objects.create(
                    farmer=instance.farmer,
                    title='Farm Registered',
                    message=f'Your farm "{instance.name}" has been successfully registered. '
                             f'Area: {instance.farm_size_hectares} hectares.',
                    alert_type='general',
                    priority='low',
                    related_farm_id=str(instance.id)
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create farm registration alert: {e}")
    
    @receiver(post_save, sender=Farm)
    def farm_verification_alert(sender, instance, **kwargs):
        """Create alert when farm is verified"""
        if instance.farmer and instance.is_verified and not kwargs.get('created', False):
            try:
                # Check if verification alert already exists
                existing_alert = FarmerAlert.objects.filter(
                    farmer=instance.farmer,
                    title__icontains='Farm Verified',
                    related_farm_id=str(instance.id)
                ).first()
                
                if not existing_alert:
                    FarmerAlert.objects.create(
                        farmer=instance.farmer,
                        title='Farm Verified',
                        message=f'Congratulations! Your farm "{instance.name}" has been verified by our team.',
                        alert_type='general',
                        priority='medium',
                        related_farm_id=str(instance.id)
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create farm verification alert: {e}")

except ImportError:
    # Traceability app not available
    pass


# Payment-related signals (if payment models are available)
try:
    from payments.models import Transaction
    
    @receiver(post_save, sender=Transaction)
    def payment_received_alert(sender, instance, created, **kwargs):
        """Create alert when farmer receives a payment"""
        if created and instance.user and instance.status == 'completed' and instance.transaction_type == 'credit':
            try:
                FarmerAlert.objects.create(
                    farmer=instance.user,
                    title='Payment Received',
                    message=f'You have received a payment of {instance.amount} {instance.currency}.',
                    alert_type='payment',
                    priority='low'
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create payment alert: {e}")

except ImportError:
    # Payments app not available
    pass
