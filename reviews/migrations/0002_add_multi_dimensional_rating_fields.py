# Generated migration for adding multi-dimensional rating fields

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),  # Adjust this to match your latest migration
    ]

    operations = [
        # Add new rating fields to Review model
        migrations.AddField(
            model_name='review',
            name='taste_rating',
            field=models.IntegerField(blank=True, help_text='Taste and flavor quality', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='review',
            name='communication_rating',
            field=models.IntegerField(blank=True, help_text='Farmer communication quality', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='review',
            name='consistency_rating',
            field=models.IntegerField(blank=True, help_text='Farmer reliability and consistency', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='review',
            name='logistics_rating',
            field=models.IntegerField(blank=True, help_text='Logistics and transportation quality', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='review',
            name='warehouse_handling_rating',
            field=models.IntegerField(blank=True, help_text='Warehouse handling and storage', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='review',
            name='customer_service_rating',
            field=models.IntegerField(blank=True, help_text='Customer service experience', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='review',
            name='sustainability_rating',
            field=models.IntegerField(blank=True, help_text='Environmental impact and sustainable practices', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        
        # Update help text for existing fields
        migrations.AlterField(
            model_name='review',
            name='quality_rating',
            field=models.IntegerField(blank=True, help_text='Overall product quality assessment', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='freshness_rating',
            field=models.IntegerField(blank=True, help_text='Product freshness and condition', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='packaging_rating',
            field=models.IntegerField(blank=True, help_text='Packaging quality and presentation', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='value_rating',
            field=models.IntegerField(blank=True, help_text='Value for money assessment', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='delivery_rating',
            field=models.IntegerField(blank=True, help_text='Delivery time and reliability', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='farmer_rating',
            field=models.IntegerField(blank=True, help_text='Overall farmer service rating', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
