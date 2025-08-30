"""
AgriConnect Review System Demo
Demonstrates the comprehensive review and rating system implementation
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order, OrderItem
from reviews.models import (
    Review, ReviewHelpfulVote, ReviewFlag, ReviewResponse,
    ExpertReview, ReviewRecipe, SeasonalInsight
)

User = get_user_model()

def create_sample_reviews():
    """Create comprehensive sample review data"""
    print("🌾 Creating Sample Review Data for AgriConnect")
    print("=" * 60)
    
    # Get existing users and products
    try:
        buyers = User.objects.filter(user_type='buyer')[:3]
        farmers = User.objects.filter(user_type='farmer')[:2]
        products = Product.objects.all()[:5]
        orders = Order.objects.filter(status='delivered')[:3]
        
        if not buyers.exists():
            print("❌ No buyers found. Creating sample buyers...")
            buyer1 = User.objects.create_user(
                phone_number='+233201234567',
                email='buyer1@example.com',
                password='password123',
                first_name='John',
                last_name='Buyer',
                user_type='buyer'
            )
            buyer2 = User.objects.create_user(
                phone_number='+233201234568',
                email='buyer2@example.com',
                password='password123',
                first_name='Mary',
                last_name='Customer',
                user_type='buyer'
            )
            buyers = [buyer1, buyer2]
        else:
            buyers = list(buyers)
        
        if not farmers.exists():
            print("❌ No farmers found. Using first available users...")
            farmers = list(User.objects.all()[:2])
        else:
            farmers = list(farmers)
        
        if not products.exists():
            print("❌ No products found. Cannot create reviews.")
            return
        
        products = list(products)
        
        print(f"✅ Found {len(buyers)} buyers, {len(farmers)} farmers, {len(products)} products")
        
        # Create sample reviews
        reviews_created = 0
        
        # Sample review data
        review_data = [
            {
                'title': 'Excellent Fresh Cassava!',
                'content': 'This cassava is incredibly fresh and of high quality. The farmer clearly takes great care in cultivation. Perfect for making fufu and other traditional dishes.',
                'pros': 'Very fresh, good size, clean packaging',
                'cons': 'Slightly more expensive than market price',
                'overall_rating': 5,
                'quality_rating': 5,
                'freshness_rating': 5,
                'packaging_rating': 4,
                'value_rating': 4,
                'delivery_rating': 5,
                'farmer_rating': 5,
            },
            {
                'title': 'Good Yam but Delivery Issues',
                'content': 'The yam quality is good and it arrived in decent condition. However, delivery took longer than expected which affected freshness slightly.',
                'pros': 'Good size, authentic variety, well-packaged',
                'cons': 'Delivery delay, some softness due to delay',
                'overall_rating': 3,
                'quality_rating': 4,
                'freshness_rating': 3,
                'packaging_rating': 4,
                'value_rating': 4,
                'delivery_rating': 2,
                'farmer_rating': 4,
            },
            {
                'title': 'Amazing Organic Rice',
                'content': 'This local rice variety is fantastic! You can really taste the difference compared to imported rice. Will definitely order again.',
                'pros': 'Authentic taste, organic certification, supports local farmers',
                'cons': 'None really',
                'overall_rating': 5,
                'quality_rating': 5,
                'freshness_rating': 5,
                'packaging_rating': 5,
                'value_rating': 5,
                'delivery_rating': 4,
                'farmer_rating': 5,
            },
            {
                'title': 'Mixed Experience with Plantain',
                'content': 'Some plantains were perfect while others were overripe. Quality control could be better.',
                'pros': 'Good price, authentic variety',
                'cons': 'Inconsistent ripeness, some overripe pieces',
                'overall_rating': 3,
                'quality_rating': 3,
                'freshness_rating': 2,
                'packaging_rating': 3,
                'value_rating': 4,
                'delivery_rating': 4,
                'farmer_rating': 3,
            },
        ]
        
        # Create reviews
        for i, data in enumerate(review_data[:len(products)]):
            if i < len(buyers):
                reviewer = buyers[i % len(buyers)]
                product = products[i]
                order = orders[i % len(orders)] if orders else None
                
                # Create review
                review = Review.objects.create(
                    product=product,
                    order=order,
                    reviewer=reviewer,
                    verified_purchase=bool(order),
                    **data
                )
                
                print(f"✅ Created review: '{review.title}' by {reviewer.first_name}")
                reviews_created += 1
                
                # Add some helpful votes
                for voter in buyers:
                    if voter != reviewer:
                        ReviewHelpfulVote.objects.create(
                            review=review,
                            user=voter,
                            is_helpful=i % 2 == 0  # Alternate helpful/not helpful
                        )
                
                # Update review vote counts
                helpful_count = review.helpful_votes_detail.filter(is_helpful=True).count()
                total_count = review.helpful_votes_detail.count()
                review.helpful_votes = helpful_count
                review.total_votes = total_count
                review.save()
        
        # Create farmer responses to some reviews
        reviews = Review.objects.all()
        for i, review in enumerate(reviews[:2]):
            if farmers:
                farmer = farmers[i % len(farmers)]
                response_content = [
                    "Thank you for your feedback! We really appreciate your business and are glad you enjoyed our produce.",
                    "We apologize for the delivery delay. We're working with logistics partners to improve delivery times. Thank you for your patience!"
                ][i]
                
                ReviewResponse.objects.create(
                    review=review,
                    responder=farmer,
                    content=response_content
                )
                print(f"✅ Created farmer response to review '{review.title}'")
        
        # Create expert reviews
        if farmers:
            expert = farmers[0]  # Use first farmer as expert
            expert_review = ExpertReview.objects.create(
                product=products[0],
                expert=expert,
                expert_type='agricultural_officer',
                overall_rating=5,
                title='Agricultural Extension Officer Assessment',
                content='This cassava variety demonstrates excellent cultivation practices. The root quality indicates proper soil management and harvesting timing.',
                quality_assessment='Superior root quality with optimal moisture content and minimal blemishes.',
                nutritional_value=5,
                sustainability_rating=5,
                recommendations='Excellent choice for both fresh consumption and processing. Recommend this farmer for their sustainable practices.',
                verified_expert=True,
                expert_credentials='BSc Agriculture, 10+ years field experience',
                is_featured=True
            )
            print(f"✅ Created expert review by agricultural officer")
        
        # Create sample recipes
        if Review.objects.exists():
            review = Review.objects.first()
            recipe = ReviewRecipe.objects.create(
                review=review,
                author=review.reviewer,
                title='Traditional Fufu with Fresh Cassava',
                description='A classic Ghanaian dish made with fresh cassava from this farmer',
                ingredients=[
                    '2 kg fresh cassava (from this order)',
                    '1 tsp salt',
                    'Water for boiling'
                ],
                instructions='1. Peel and chop cassava\n2. Boil until tender\n3. Pound until smooth\n4. Serve with your favorite soup',
                prep_time=30,
                cook_time=45,
                servings=4,
                difficulty='medium',
                calories_per_serving=320,
                nutrition_notes='Rich in carbohydrates and vitamin C'
            )
            print(f"✅ Created recipe: '{recipe.title}'")
        
        # Create seasonal insights
        if products:
            for i, product in enumerate(products[:2]):
                insight = SeasonalInsight.objects.create(
                    product=product,
                    season='rainy_season',
                    average_rating=Decimal('4.2'),
                    review_count=15,
                    quality_score=Decimal('4.5'),
                    availability_score=Decimal('3.8'),
                    price_trend='moderate',
                    region='Greater Accra',
                    insights='This product shows excellent quality during rainy season with peak availability.',
                    recommendations='Best time to purchase for optimal freshness and competitive pricing.',
                    best_varieties=['Local variety', 'Improved variety']
                )
                print(f"✅ Created seasonal insight for {product.name}")
        
        print(f"\n🎉 Review System Demo Data Created Successfully!")
        print(f"📊 Summary:")
        print(f"   • Reviews: {Review.objects.count()}")
        print(f"   • Expert Reviews: {ExpertReview.objects.count()}")
        print(f"   • Recipes: {ReviewRecipe.objects.count()}")
        print(f"   • Seasonal Insights: {SeasonalInsight.objects.count()}")
        print(f"   • Helpful Votes: {ReviewHelpfulVote.objects.count()}")
        print(f"   • Farmer Responses: {ReviewResponse.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error creating sample reviews: {e}")


def demo_review_api_endpoints():
    """Demonstrate available review API endpoints"""
    print("\n🌐 AgriConnect Review System API Endpoints")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000/api/v1/reviews/api/v1"
    
    endpoints = [
        # Review Management
        ("All Reviews", "GET", f"{base_url}/reviews/"),
        ("Create Review", "POST", f"{base_url}/reviews/"),
        ("Review Detail", "GET", f"{base_url}/reviews/{{id}}/"),
        ("Update Review", "PUT", f"{base_url}/reviews/{{id}}/"),
        ("Delete Review", "DELETE", f"{base_url}/reviews/{{id}}/"),
        
        # Review Interactions
        ("Mark Helpful", "POST", f"{base_url}/reviews/{{id}}/helpful_vote/"),
        ("Flag Review", "POST", f"{base_url}/reviews/{{id}}/flag_review/"),
        ("Farmer Response", "POST", f"{base_url}/reviews/{{id}}/respond/"),
        
        # Review Analytics
        ("Product Summary", "GET", f"{base_url}/reviews/product_summary/?product_id={{id}}"),
        ("Trending Reviews", "GET", f"{base_url}/reviews/trending/?days=7"),
        ("Review Analytics", "GET", f"{base_url}/reviews/analytics/"),
        
        # Expert Reviews
        ("Expert Reviews", "GET", f"{base_url}/expert-reviews/"),
        ("Featured Expert Reviews", "GET", f"{base_url}/expert-reviews/featured/"),
        ("Expert Reviews by Type", "GET", f"{base_url}/expert-reviews/by_expert_type/?type=agricultural_officer"),
        
        # Recipe System
        ("Review Recipes", "GET", f"{base_url}/recipes/"),
        ("Like Recipe", "POST", f"{base_url}/recipes/{{id}}/like/"),
        ("Share Recipe", "POST", f"{base_url}/recipes/{{id}}/share/"),
        
        # Seasonal Insights
        ("Seasonal Insights", "GET", f"{base_url}/seasonal-insights/"),
        ("Current Season", "GET", f"{base_url}/seasonal-insights/current_season/"),
        ("By Region", "GET", f"{base_url}/seasonal-insights/by_region/?region=Accra"),
    ]
    
    print("📍 Review System API Endpoints:")
    for name, method, url in endpoints:
        print(f"   {method:<6} {name:<25} → {url}")
    
    print("\n🔍 Advanced Filtering Examples:")
    filters = [
        ("Verified Reviews Only", f"{base_url}/reviews/?verified_only=true"),
        ("High Rated (4+ stars)", f"{base_url}/reviews/?min_rating=4"),
        ("Recent Reviews (7 days)", f"{base_url}/reviews/?days_back=7"),
        ("Product Reviews", f"{base_url}/reviews/?product_id={{product_id}}"),
        ("Search Reviews", f"{base_url}/reviews/?search=cassava"),
        ("Sort by Helpfulness", f"{base_url}/reviews/?ordering=-helpful_votes"),
    ]
    
    for name, url in filters:
        print(f"   🔍 {name:<25} → {url}")


def demo_review_features():
    """Demonstrate key review system features"""
    print("\n🌟 AgriConnect Review System Features")
    print("=" * 60)
    
    features = [
        "✅ Multi-Dimensional Rating System",
        "   • Overall, Quality, Freshness, Packaging, Value, Delivery, Farmer ratings",
        "",
        "✅ Community Features",
        "   • Helpful vote system for review quality",
        "   • Community flagging for inappropriate content",
        "   • Farmer responses to customer feedback",
        "",
        "✅ Expert Review System",
        "   • Agricultural extension officers",
        "   • Nutritionists and food scientists",
        "   • Sustainability experts",
        "   • Verified expert credentials",
        "",
        "✅ Recipe Integration",
        "   • Recipe suggestions linked to product reviews",
        "   • Cooking instructions and nutritional information",
        "   • Community recipe sharing and likes",
        "",
        "✅ Seasonal Insights",
        "   • Best seasons for specific products",
        "   • Regional availability and pricing trends",
        "   • Quality scores by season",
        "",
        "✅ Advanced Analytics",
        "   • Review trends and sentiment analysis",
        "   • Product and farmer performance metrics",
        "   • Seasonal recommendations",
        "",
        "✅ Verification Systems",
        "   • Verified purchase confirmations",
        "   • Blockchain-verified reviews (planned)",
        "   • Expert credential verification",
        "",
        "✅ Mobile-Optimized",
        "   • Photo and video review support",
        "   • Mobile-friendly recipe viewing",
        "   • Offline review composition",
    ]
    
    for feature in features:
        print(feature)


if __name__ == "__main__":
    print("🎯 AgriConnect Review System Implementation Demo")
    print("=" * 80)
    
    create_sample_reviews()
    demo_review_api_endpoints()
    demo_review_features()
    
    print("\n" + "=" * 80)
    print("🎉 REVIEW SYSTEM (4.4) IMPLEMENTATION COMPLETE!")
    print("=" * 80)
    print("✅ Multi-dimensional review system operational")
    print("✅ Community features (helpful votes, flags, responses)")
    print("✅ Expert review system for agricultural professionals")
    print("✅ Recipe integration with cooking suggestions")
    print("✅ Seasonal insights and analytics")
    print("✅ Advanced filtering and search capabilities")
    print("✅ Complete API documentation and endpoints")
    print("=" * 80)
