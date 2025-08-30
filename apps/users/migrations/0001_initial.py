# Generated manually for AgriConnect profile models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create ExtendedUserProfile
        migrations.CreateModel(
            name='ExtendedUserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')], max_length=20)),
                ('address_line_1', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('newsletter_subscription', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extended_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Extended User Profile',
                'verbose_name_plural': 'Extended User Profiles',
            },
        ),
        
        # Create FarmerProfile
        migrations.CreateModel(
            name='FarmerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('farm_name', models.CharField(max_length=200)),
                ('farm_size', models.DecimalField(decimal_places=2, help_text='Farm size in hectares', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('primary_crops', models.JSONField(default=list, help_text='List of primary crops grown')),
                ('farming_experience', models.PositiveIntegerField(help_text='Years of farming experience', validators=[django.core.validators.MaxValueValidator(100)])),
                ('certification_status', models.CharField(choices=[('none', 'No Certification'), ('organic', 'Organic Certified'), ('gap', 'Good Agricultural Practices'), ('rainforest', 'Rainforest Alliance'), ('fairtrade', 'Fair Trade')], default='none', max_length=20)),
                ('preferred_payment_method', models.CharField(choices=[('mobile_money', 'Mobile Money'), ('bank_transfer', 'Bank Transfer'), ('cash', 'Cash'), ('check', 'Check')], default='mobile_money', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='farmer_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Farmer Profile',
                'verbose_name_plural': 'Farmer Profiles',
            },
        ),
        
        # Create ConsumerProfile  
        migrations.CreateModel(
            name='ConsumerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dietary_preferences', models.JSONField(default=list, help_text='List of dietary preferences')),
                ('preferred_product_categories', models.JSONField(default=list, help_text='Preferred product categories')),
                ('delivery_preferences', models.CharField(choices=[('home_delivery', 'Home Delivery'), ('pickup_point', 'Pickup Point'), ('both', 'Both')], default='home_delivery', max_length=20)),
                ('budget_range', models.CharField(choices=[('budget', 'Budget (Under $50)'), ('mid_range', 'Mid-range ($50-$200)'), ('premium', 'Premium ($200+)')], default='mid_range', max_length=20)),
                ('organic_preference', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='consumer_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Consumer Profile',
                'verbose_name_plural': 'Consumer Profiles',
            },
        ),
        
        # Create InstitutionProfile
        migrations.CreateModel(
            name='InstitutionProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_name', models.CharField(max_length=200)),
                ('institution_type', models.CharField(choices=[('restaurant', 'Restaurant'), ('hotel', 'Hotel'), ('school', 'School'), ('hospital', 'Hospital'), ('government', 'Government'), ('ngo', 'NGO'), ('retailer', 'Retailer'), ('wholesaler', 'Wholesaler')], max_length=20)),
                ('registration_number', models.CharField(blank=True, max_length=100)),
                ('tax_id', models.CharField(blank=True, max_length=100)),
                ('annual_volume_requirement', models.DecimalField(decimal_places=2, help_text='Expected annual purchase volume in metric tons', max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('preferred_supplier_count', models.PositiveIntegerField(default=5, help_text='Preferred number of suppliers to work with')),
                ('quality_requirements', models.JSONField(default=dict, help_text='Specific quality requirements')),
                ('payment_terms', models.CharField(choices=[('immediate', 'Immediate Payment'), ('net_7', 'Net 7 Days'), ('net_15', 'Net 15 Days'), ('net_30', 'Net 30 Days'), ('net_60', 'Net 60 Days')], default='net_30', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='institution_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Institution Profile',
                'verbose_name_plural': 'Institution Profiles',
            },
        ),
    ]
