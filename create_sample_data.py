from django.contrib.auth import get_user_model
from products.models import Category, Product
from decimal import Decimal
from datetime import date, timedelta
from django.utils.text import slugify

User = get_user_model()

# Create categories
categories_data = [
    {'name': 'Grains & Cereals', 'description': 'Rice, wheat, millet, sorghum, maize and other cereal crops'},
    {'name': 'Vegetables', 'description': 'Fresh vegetables including leafy greens, roots, and seasonal vegetables'},
    {'name': 'Fruits', 'description': 'Fresh tropical and seasonal fruits'},
    {'name': 'Legumes & Pulses', 'description': 'Beans, lentils, peas, groundnuts and other protein-rich crops'},
    {'name': 'Root Crops', 'description': 'Cassava, yam, sweet potato, cocoyam and other tubers'},
]

categories = {}
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories[cat_data['name']] = category
    print(f'Category: {category.name} - {"Created" if created else "Exists"}')

# Create test user  
try:
    seller = User.objects.get(email='farmer@agriconnect.com')
    print(f'Using existing user: {seller.email}')
except User.DoesNotExist:
    seller = User.objects.create_user(
        identifier='farmer@agriconnect.com',
        password='farmpass123',
        first_name='John',
        last_name='Farmer',
        roles=['FARMER']
    )
    print(f'Created user: {seller.email}')

# Create sample products
products_data = [
    {
        'name': 'Premium Jasmine Rice',
        'description': 'High-quality aromatic jasmine rice from northern Ghana.',
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
        'description': 'Vine-ripened fresh tomatoes, perfect for cooking.',
        'category': 'Vegetables',
        'product_type': 'raw',
        'organic_status': 'non_organic',
        'price_per_unit': Decimal('2.80'),
        'unit': 'kg',
        'minimum_order_quantity': Decimal('10'),
        'stock_quantity': Decimal('200'),
        'harvest_date': date.today() - timedelta(days=2),
        'origin_region': 'Greater Accra',
        'origin_city': 'Accra',
        'quality_grade': 'A'
    },
    {
        'name': 'Organic Pineapples',
        'description': 'Sweet and juicy organic pineapples grown without pesticides.',
        'category': 'Fruits',
        'product_type': 'raw',
        'organic_status': 'organic',
        'price_per_unit': Decimal('3.20'),
        'unit': 'pieces',
        'minimum_order_quantity': Decimal('5'),
        'stock_quantity': Decimal('150'),
        'harvest_date': date.today() - timedelta(days=1),
        'origin_region': 'Central Region',
        'origin_city': 'Cape Coast',
        'quality_grade': 'A'
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
        print(f'Created product: {product.name}')
    else:
        print(f'Product exists: {product.name}')

print(f'Categories: {Category.objects.count()}')
print(f'Products: {Product.objects.count()}')
print(f'Users: {User.objects.count()}')
print('Sample data creation completed!')
