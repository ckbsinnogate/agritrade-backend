"""
Django management command to create sample categories and products
for AgriConnect API testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from products.models import Category, Product
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample categories and products for AgriConnect API testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample categories and products...'))
        
        # Create categories
        categories_data = [
            {
                'name': 'Grains & Cereals',
                'description': 'Rice, wheat, millet, sorghum, maize and other cereal crops'
            },
            {
                'name': 'Vegetables',
                'description': 'Fresh vegetables including leafy greens, roots, and seasonal vegetables'
            },
            {
                'name': 'Fruits',
                'description': 'Fresh tropical and seasonal fruits'
            },
            {
                'name': 'Legumes & Pulses',
                'description': 'Beans, lentils, peas, groundnuts and other protein-rich crops'
            },
            {
                'name': 'Root Crops',
                'description': 'Cassava, yam, sweet potato, cocoyam and other tubers'
            },
            {
                'name': 'Spices & Herbs',
                'description': 'Traditional spices, herbs, and medicinal plants'
            },
            {
                'name': 'Processed Foods',
                'description': 'Value-added and processed agricultural products'
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category exists: {category.name}')
        
        # Get or create a test user (seller)
        try:
            seller = User.objects.get(email='test@agriconnect.com')
        except User.DoesNotExist:
            seller = User.objects.create_user(
                email='test@agriconnect.com',
                phone='+233501234567',
                first_name='Test',
                last_name='Farmer',
                password='testpass123'
            )
            self.stdout.write(f'Created test user: {seller.email}')
        
        # Create sample products
        products_data = [
            {
                'name': 'Premium Jasmine Rice',
                'description': 'High-quality aromatic jasmine rice from northern Ghana. Carefully harvested and processed for superior taste and texture.',
                'category': 'Grains & Cereals',
                'product_type': 'raw',
                'organic_status': 'organic',
                'price_per_unit': Decimal('5.50'),
                'unit': 'kg',
                'minimum_order_quantity': Decimal('25'),
                'stock_quantity': Decimal('500'),
                'harvest_date': date.today() - timedelta(days=30),
                'origin_region': 'Northern Region',
                'origin_city': 'Tamale',
                'quality_grade': 'A',
                'is_featured': True
            },
            {
                'name': 'Fresh Tomatoes',
                'description': 'Vine-ripened fresh tomatoes, perfect for cooking and salads. Harvested at peak ripeness.',
                'category': 'Vegetables',
                'product_type': 'raw',
                'organic_status': 'non_organic',
                'price_per_unit': Decimal('2.80'),
                'unit': 'kg',
                'minimum_order_quantity': Decimal('10'),
                'stock_quantity': Decimal('200'),
                'harvest_date': date.today() - timedelta(days=2),
                'expiry_date': date.today() + timedelta(days=7),
                'origin_region': 'Greater Accra',
                'origin_city': 'Accra',
                'quality_grade': 'A',
                'is_featured': True
            },
            {
                'name': 'Organic Pineapples',
                'description': 'Sweet and juicy organic pineapples grown without pesticides. Rich in vitamin C and natural enzymes.',
                'category': 'Fruits',
                'product_type': 'raw',
                'organic_status': 'organic',
                'price_per_unit': Decimal('3.20'),
                'unit': 'pieces',
                'minimum_order_quantity': Decimal('5'),
                'stock_quantity': Decimal('150'),
                'harvest_date': date.today() - timedelta(days=1),
                'expiry_date': date.today() + timedelta(days=10),
                'origin_region': 'Central Region',
                'origin_city': 'Cape Coast',
                'quality_grade': 'A'
            },
            {
                'name': 'Black-Eyed Peas',
                'description': 'High-protein black-eyed peas, perfect for traditional African dishes. Dried and ready for cooking.',
                'category': 'Legumes & Pulses',
                'product_type': 'raw',
                'organic_status': 'non_organic',
                'price_per_unit': Decimal('4.20'),
                'unit': 'kg',
                'minimum_order_quantity': Decimal('20'),
                'stock_quantity': Decimal('300'),
                'harvest_date': date.today() - timedelta(days=60),
                'origin_region': 'Upper East',
                'origin_city': 'Bolgatanga',
                'quality_grade': 'B'
            },
            {
                'name': 'Fresh Cassava Tubers',
                'description': 'Fresh cassava tubers, ideal for fufu, gari production, or direct consumption. High starch content.',
                'category': 'Root Crops',
                'product_type': 'raw',
                'organic_status': 'non_organic',
                'price_per_unit': Decimal('1.50'),
                'unit': 'kg',
                'minimum_order_quantity': Decimal('50'),
                'stock_quantity': Decimal('1000'),
                'harvest_date': date.today() - timedelta(days=3),
                'expiry_date': date.today() + timedelta(days=5),
                'origin_region': 'Ashanti',
                'origin_city': 'Kumasi',
                'quality_grade': 'A'
            },
            {
                'name': 'Dried Ginger',
                'description': 'Premium dried ginger root, perfect for cooking, tea, and traditional medicine. Intense flavor and aroma.',
                'category': 'Spices & Herbs',
                'product_type': 'processed',
                'organic_status': 'organic',
                'price_per_unit': Decimal('12.00'),
                'unit': 'kg',
                'minimum_order_quantity': Decimal('2'),
                'stock_quantity': Decimal('50'),
                'processing_date': date.today() - timedelta(days=15),
                'origin_region': 'Eastern Region',
                'origin_city': 'Koforidua',
                'quality_grade': 'A',
                'processing_method': 'Sun-dried and ground'
            },
            {
                'name': 'Plantain Chips',
                'description': 'Crispy plantain chips made from premium plantains. Healthy snack option, lightly salted.',
                'category': 'Processed Foods',
                'product_type': 'processed',
                'organic_status': 'non_organic',
                'price_per_unit': Decimal('8.50'),
                'unit': 'kg',
                'minimum_order_quantity': Decimal('5'),
                'stock_quantity': Decimal('100'),
                'processing_date': date.today() - timedelta(days=7),
                'expiry_date': date.today() + timedelta(days=90),
                'origin_region': 'Western Region',
                'origin_city': 'Takoradi',
                'quality_grade': 'A',
                'processing_method': 'Deep-fried and seasoned',
                'processing_facility': 'AgriProcess Ghana Ltd'
            }
        ]
        
        created_count = 0
        for product_data in products_data:
            category = categories[product_data.pop('category')]
            
            # Create slug from name
            slug = slugify(product_data['name'])
            counter = 1
            original_slug = slug
            while Product.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            product_data.update({
                'category': category,
                'seller': seller,
                'slug': slug,
                'search_keywords': [
                    product_data['name'].lower(),
                    category.name.lower(),
                    product_data['product_type'],
                    product_data['organic_status']
                ]
            })
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                seller=seller,
                defaults=product_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product exists: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(categories_data)} categories and {created_count} new products!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Total products in database: {Product.objects.count()}'
            )
        )
