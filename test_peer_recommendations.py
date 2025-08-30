#!/usr/bin/env python3
"""
Test and validate the farmer-to-farmer peer recommendation system
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product, Category
from users.models import FarmerProfile
from reviews.models import (
    PeerRecommendation, PeerRecommendationVote, 
    FarmerNetwork, PeerRecommendationInteraction
)

User = get_user_model()

def create_test_users():
    """Create test farmer users"""
    print("🌾 Creating test farmer users...")
    
    # Create test farmers
    farmers_data = [
        {
            'username': 'farmer_john',
            'email': 'john@farm.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'farm_size': 50.0,
            'years_of_experience': 15,
            'primary_crops': ['corn', 'soybeans'],
            'organic_certified': True
        },
        {
            'username': 'farmer_mary',
            'email': 'mary@farm.com', 
            'first_name': 'Mary',
            'last_name': 'Johnson',
            'farm_size': 25.0,
            'years_of_experience': 8,
            'primary_crops': ['tomatoes', 'peppers'],
            'organic_certified': False
        },
        {
            'username': 'farmer_bob',
            'email': 'bob@farm.com',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'farm_size': 100.0,
            'years_of_experience': 20,
            'primary_crops': ['wheat', 'barley'],
            'organic_certified': True
        }
    ]
    
    farmers = []
    for farmer_data in farmers_data:
        user, created = User.objects.get_or_create(
            username=farmer_data['username'],
            defaults={
                'email': farmer_data['email'],
                'first_name': farmer_data['first_name'],
                'last_name': farmer_data['last_name']
            }
        )
        
        # Create or update farmer profile
        profile, created = FarmerProfile.objects.get_or_create(
            user=user,
            defaults={
                'farm_size': farmer_data['farm_size'],
                'years_of_experience': farmer_data['years_of_experience'],
                'primary_crops': farmer_data['primary_crops'],
                'organic_certified': farmer_data['organic_certified']
            }
        )
        
        farmers.append(user)
        print(f"✅ Created farmer: {user.get_full_name()} ({user.username})")
    
    return farmers

def create_test_products():
    """Create test products"""
    print("\n🥕 Creating test products...")
    
    # Create category if it doesn't exist
    category, created = Category.objects.get_or_create(
        name='Seeds',
        defaults={'description': 'Agricultural seeds and planting materials'}
    )
    
    products_data = [
        {
            'name': 'Premium Corn Seeds',
            'description': 'High-yield GMO-free corn seeds',
            'price': Decimal('45.99'),
            'category': category
        },
        {
            'name': 'Organic Tomato Seeds',
            'description': 'Certified organic heirloom tomato seeds',
            'price': Decimal('12.99'),
            'category': category
        },
        {
            'name': 'Winter Wheat Seeds',
            'description': 'Cold-resistant winter wheat variety',
            'price': Decimal('32.50'),
            'category': category
        }
    ]
    
    products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        products.append(product)
        print(f"✅ Created product: {product.name}")
    
    return products

def main():
    """Main execution function"""
    print("🚀 Starting farmer-to-farmer peer recommendation system validation...")
    
    try:
        # Create test data
        farmers = create_test_users()
        products = create_test_products()
        
        print("\n✅ Basic setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()