
from django.contrib.auth import get_user_model
from products.models import Category, Product
from decimal import Decimal
from datetime import date, timedelta

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
    print(f'Category: {category.name} - {\
Created\ if created else \Exists\}')

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

print(f'Categories: {Category.objects.count()}')
print(f'Users: {User.objects.count()}')
print('Sample data creation completed!')

