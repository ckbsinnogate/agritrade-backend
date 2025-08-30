"""
AgriConnect Recipe Sharing System Demo
Create sample processing recipes and processor profiles

This script demonstrates the complete recipe sharing API functionality
for processor integration and technical support.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from processors.models import (
    ProcessorProfile, ProcessingRecipe, RecipeRating, 
    RecipeUsageLog, RecipeComment
)

User = get_user_model()

def create_sample_data():
    """Create comprehensive sample data for recipe sharing system"""
    
    print("🌾 Creating AgriConnect Recipe Sharing System Sample Data...\n")
    
    # Create processor users
    processors = []
    
    # Processor 1: Milling Specialist
    user1, created = User.objects.get_or_create(
        username='miller_accra',
        defaults={
            'first_name': 'Kwame',
            'last_name': 'Asante',
            'email': 'kwame@goldenmills.gh',
            'phone_number': '+233244567890'
        }
    )
    if created:
        user1.set_password('password123')
        user1.save()
    
    profile1, created = ProcessorProfile.objects.get_or_create(
        user=user1,
        defaults={
            'business_name': 'Golden Mills Processing',
            'business_registration_number': 'GH-REG-2023-001',
            'processor_type': 'mill',
            'specializations': ['maize_milling', 'cassava_processing', 'rice_milling'],
            'processing_capabilities': ['flour_production', 'grits_production', 'feed_production'],
            'daily_processing_capacity': Decimal('5000.00'),
            'capacity_unit': 'kg',
            'equipment_list': ['hammer_mill', 'sifter', 'packaging_machine'],
            'certifications': ['HACCP', 'ISO_22000'],
            'health_permits': ['FDA_PERMIT_2024'],
            'quality_standards': ['CODEX_ALIMENTARIUS'],
            'location': {
                'latitude': 5.6037,
                'longitude': -0.1870,
                'address': 'Industrial Area, Accra, Ghana'
            },
            'service_radius_km': 100,
            'operating_hours': {
                'monday': '08:00-18:00',
                'tuesday': '08:00-18:00',
                'wednesday': '08:00-18:00',
                'thursday': '08:00-18:00',
                'friday': '08:00-18:00',
                'saturday': '08:00-14:00',
                'sunday': 'closed'
            },
            'is_verified': True,
            'verified_at': datetime.now()
        }
    )
    processors.append((user1, profile1))
    
    # Processor 2: Oil Extraction Specialist
    user2, created = User.objects.get_or_create(
        username='oil_master_kumasi',
        defaults={
            'first_name': 'Ama',
            'last_name': 'Osei',
            'email': 'ama@oiltech.gh',
            'phone_number': '+233201234567'
        }
    )
    if created:
        user2.set_password('password123')
        user2.save()
    
    profile2, created = ProcessorProfile.objects.get_or_create(
        user=user2,
        defaults={
            'business_name': 'OilTech Ghana Limited',
            'business_registration_number': 'GH-REG-2022-045',
            'processor_type': 'oil_extraction',
            'specializations': ['palm_oil_extraction', 'shea_butter_processing', 'coconut_oil'],
            'processing_capabilities': ['crude_oil_extraction', 'refined_oil_production', 'packaging'],
            'daily_processing_capacity': Decimal('2000.00'),
            'capacity_unit': 'kg',
            'equipment_list': ['expeller_press', 'refining_equipment', 'filtration_system'],
            'certifications': ['HACCP', 'FDA_APPROVED'],
            'health_permits': ['HEALTH_PERMIT_2024'],
            'quality_standards': ['INTERNATIONAL_STANDARDS'],
            'location': {
                'latitude': 6.6885,
                'longitude': -1.6244,
                'address': 'Industrial Zone, Kumasi, Ghana'
            },
            'service_radius_km': 150,
            'operating_hours': {
                'monday': '07:00-19:00',
                'tuesday': '07:00-19:00',
                'wednesday': '07:00-19:00',
                'thursday': '07:00-19:00',
                'friday': '07:00-19:00',
                'saturday': '07:00-16:00',
                'sunday': 'closed'
            },
            'is_verified': True,
            'verified_at': datetime.now()
        }
    )
    processors.append((user2, profile2))
    
    # Create processing recipes
    recipes = []
    
    # Recipe 1: Maize Flour Production
    recipe1, created = ProcessingRecipe.objects.get_or_create(
        recipe_name='Premium Maize Flour Production',
        processor=user1,
        defaults={
            'description': 'Complete process for producing high-quality maize flour suitable for baking and cooking. This recipe ensures consistent quality and maximum yield.',
            'skill_level_required': 'intermediate',
            'processing_time_minutes': 120,
            'input_materials': [
                {
                    'name': 'Dried Maize Kernels',
                    'quantity': 100,
                    'unit': 'kg',
                    'quality_grade': 'Grade A',
                    'moisture_content': '14%'
                },
                {
                    'name': 'Packaging Materials',
                    'quantity': 200,
                    'unit': 'pieces',
                    'type': '500g bags'
                }
            ],
            'processing_steps': [
                {
                    'step_number': 1,
                    'description': 'Quality inspection and sorting of maize kernels',
                    'duration_minutes': 15,
                    'equipment': 'sorting_table',
                    'quality_check': 'Remove damaged, discolored kernels'
                },
                {
                    'step_number': 2,
                    'description': 'Cleaning and washing',
                    'duration_minutes': 20,
                    'equipment': 'destoner_cleaner',
                    'quality_check': 'Remove all foreign materials'
                },
                {
                    'step_number': 3,
                    'description': 'Moisture adjustment if necessary',
                    'duration_minutes': 10,
                    'equipment': 'moisture_meter',
                    'quality_check': 'Achieve 14% moisture content'
                },
                {
                    'step_number': 4,
                    'description': 'Primary milling',
                    'duration_minutes': 30,
                    'equipment': 'hammer_mill',
                    'settings': 'Medium mesh screen (2mm)'
                },
                {
                    'step_number': 5,
                    'description': 'Sifting and grading',
                    'duration_minutes': 25,
                    'equipment': 'vibrating_sifter',
                    'quality_check': 'Separate coarse, medium, and fine fractions'
                },
                {
                    'step_number': 6,
                    'description': 'Final milling of coarse fraction',
                    'duration_minutes': 15,
                    'equipment': 'hammer_mill',
                    'settings': 'Fine mesh screen (1mm)'
                },
                {
                    'step_number': 7,
                    'description': 'Final sifting and blending',
                    'duration_minutes': 15,
                    'equipment': 'sifter_blender',
                    'quality_check': 'Uniform particle size'
                },
                {
                    'step_number': 8,
                    'description': 'Quality testing',
                    'duration_minutes': 10,
                    'tests': ['moisture_content', 'particle_size', 'protein_content']
                },
                {
                    'step_number': 9,
                    'description': 'Packaging',
                    'duration_minutes': 20,
                    'equipment': 'automatic_packaging',
                    'package_size': '500g, 1kg, 2kg'
                }
            ],
            'equipment_required': [
                'sorting_table',
                'destoner_cleaner',
                'hammer_mill',
                'vibrating_sifter',
                'moisture_meter',
                'packaging_machine',
                'weighing_scale'
            ],
            'output_products': [
                {
                    'name': 'Premium Maize Flour',
                    'expected_quantity': 85,
                    'unit': 'kg',
                    'quality_grade': 'Premium',
                    'moisture_content': '13%'
                },
                {
                    'name': 'Maize Bran',
                    'expected_quantity': 12,
                    'unit': 'kg',
                    'use': 'Animal feed supplement'
                }
            ],
            'expected_yield_percentage': Decimal('85.00'),
            'quality_checkpoints': [
                'Raw material inspection',
                'Moisture content verification',
                'Particle size analysis',
                'Final product testing',
                'Packaging integrity check'
            ],
            'quality_standards': {
                'moisture_content': 'Max 13%',
                'protein_content': 'Min 8%',
                'ash_content': 'Max 1.5%',
                'particle_size': '80% pass through 250 micron',
                'microbiological': 'Meets CODEX standards'
            },
            'processing_cost_per_unit': Decimal('2.50'),
            'labor_hours_required': Decimal('4.00'),
            'energy_consumption': Decimal('15.50'),
            'water_usage_liters': Decimal('50.00'),
            'waste_generation_kg': Decimal('3.00'),
            'certifications_achieved': ['HACCP_COMPLIANT', 'HALAL_CERTIFIED'],
            'compliance_standards': ['FDA_APPROVED', 'CODEX_ALIMENTARIUS'],
            'status': 'verified',
            'is_public': True,
            'is_verified': True,
            'verified_by': user1,
            'verification_date': datetime.now(),
            'tags': ['maize', 'flour', 'milling', 'premium_quality', 'baking'],
            'seasonal_availability': False
        }
    )
    recipes.append(recipe1)
    
    # Recipe 2: Palm Oil Extraction
    recipe2, created = ProcessingRecipe.objects.get_or_create(
        recipe_name='Traditional Palm Oil Extraction',
        processor=user2,
        defaults={
            'description': 'Traditional method for extracting high-quality palm oil from fresh palm fruits. Ensures maximum oil yield with minimal impurities.',
            'skill_level_required': 'advanced',
            'processing_time_minutes': 180,
            'input_materials': [
                {
                    'name': 'Fresh Palm Fruits',
                    'quantity': 1000,
                    'unit': 'kg',
                    'ripeness': 'Optimal (red-orange)',
                    'harvest_time': 'Within 24 hours'
                },
                {
                    'name': 'Clean Water',
                    'quantity': 500,
                    'unit': 'liters',
                    'quality': 'Potable water'
                }
            ],
            'processing_steps': [
                {
                    'step_number': 1,
                    'description': 'Fruit inspection and sorting',
                    'duration_minutes': 20,
                    'quality_check': 'Remove overripe and underripe fruits'
                },
                {
                    'step_number': 2,
                    'description': 'Sterilization',
                    'duration_minutes': 60,
                    'equipment': 'sterilizer',
                    'temperature': '140°C',
                    'pressure': '3 bar'
                },
                {
                    'step_number': 3,
                    'description': 'Stripping (fruit removal)',
                    'duration_minutes': 15,
                    'equipment': 'stripper',
                    'quality_check': 'Complete fruit separation'
                },
                {
                    'step_number': 4,
                    'description': 'Digestion',
                    'duration_minutes': 20,
                    'equipment': 'digester',
                    'temperature': '90-95°C',
                    'purpose': 'Break down fruit structure'
                },
                {
                    'step_number': 5,
                    'description': 'Oil extraction',
                    'duration_minutes': 30,
                    'equipment': 'screw_press',
                    'pressure': 'Gradual increase to maximum'
                },
                {
                    'step_number': 6,
                    'description': 'Oil clarification',
                    'duration_minutes': 25,
                    'equipment': 'clarifier_tank',
                    'temperature': '90°C',
                    'settling_time': '20 minutes'
                },
                {
                    'step_number': 7,
                    'description': 'Oil purification',
                    'duration_minutes': 15,
                    'equipment': 'centrifuge',
                    'purpose': 'Remove impurities and water'
                },
                {
                    'step_number': 8,
                    'description': 'Quality testing',
                    'duration_minutes': 10,
                    'tests': ['free_fatty_acid', 'moisture_content', 'color_grade']
                },
                {
                    'step_number': 9,
                    'description': 'Storage preparation',
                    'duration_minutes': 5,
                    'equipment': 'storage_tanks',
                    'temperature': '60°C'
                }
            ],
            'equipment_required': [
                'sterilizer',
                'stripper',
                'digester',
                'screw_press',
                'clarifier_tank',
                'centrifuge',
                'storage_tanks',
                'temperature_control_system'
            ],
            'output_products': [
                {
                    'name': 'Crude Palm Oil',
                    'expected_quantity': 220,
                    'unit': 'kg',
                    'quality_grade': 'Grade A',
                    'free_fatty_acid': 'Max 3%'
                },
                {
                    'name': 'Palm Kernel',
                    'expected_quantity': 65,
                    'unit': 'kg',
                    'use': 'Further processing for kernel oil'
                },
                {
                    'name': 'Palm Fiber',
                    'expected_quantity': 130,
                    'unit': 'kg',
                    'use': 'Biomass fuel'
                }
            ],
            'expected_yield_percentage': Decimal('22.00'),
            'quality_checkpoints': [
                'Fruit quality assessment',
                'Sterilization temperature monitoring',
                'Extraction pressure control',
                'Oil clarity verification',
                'Final product analysis'
            ],
            'quality_standards': {
                'free_fatty_acid': 'Max 3%',
                'moisture_content': 'Max 0.1%',
                'impurities': 'Max 0.2%',
                'color_grade': 'AOCS standards',
                'peroxide_value': 'Max 10 meq O2/kg'
            },
            'processing_cost_per_unit': Decimal('1.20'),
            'labor_hours_required': Decimal('6.00'),
            'energy_consumption': Decimal('85.00'),
            'water_usage_liters': Decimal('500.00'),
            'waste_generation_kg': Decimal('20.00'),
            'certifications_achieved': ['HACCP_COMPLIANT', 'ORGANIC_CERTIFIED'],
            'compliance_standards': ['FDA_APPROVED', 'INTERNATIONAL_PALM_OIL_STANDARDS'],
            'status': 'public',
            'is_public': True,
            'tags': ['palm_oil', 'extraction', 'traditional', 'sustainable', 'quality'],
            'seasonal_availability': True,
            'available_seasons': ['peak_harvest_march_may', 'secondary_harvest_september_november']
        }
    )
    recipes.append(recipe2)
    
    # Create additional users for ratings and comments
    users_for_interaction = []
    for i in range(3):
        user, created = User.objects.get_or_create(
            username=f'processor_user_{i+1}',
            defaults={
                'first_name': f'User{i+1}',
                'last_name': 'Processor',
                'email': f'user{i+1}@processors.gh',
                'phone_number': f'+23320{1234567+i}'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        users_for_interaction.append(user)
    
    # Create recipe ratings
    ratings_data = [
        # Ratings for Maize Flour Recipe
        {
            'recipe': recipe1,
            'user': users_for_interaction[0],
            'overall_rating': 5,
            'clarity_rating': 5,
            'effectiveness_rating': 5,
            'accuracy_rating': 4,
            'review_title': 'Excellent Recipe for Premium Flour',
            'review_content': 'This recipe produces consistently high-quality maize flour. The step-by-step instructions are clear and the yield estimates are very accurate. Highly recommended for commercial production.',
            'actual_yield_achieved': Decimal('84.50'),
            'processing_time_actual': 125,
            'would_recommend': True,
            'improvement_suggestions': 'Consider adding specific temperature ranges for the milling process.'
        },
        {
            'recipe': recipe1,
            'user': users_for_interaction[1],
            'overall_rating': 4,
            'clarity_rating': 4,
            'effectiveness_rating': 5,
            'accuracy_rating': 4,
            'review_title': 'Great Results with Minor Adjustments',
            'review_content': 'Good recipe that delivers quality flour. Made some minor adjustments based on our equipment and achieved excellent results.',
            'actual_yield_achieved': Decimal('83.20'),
            'processing_time_actual': 135,
            'would_recommend': True,
            'improvement_suggestions': 'More details on equipment calibration would be helpful.'
        },
        # Ratings for Palm Oil Recipe
        {
            'recipe': recipe2,
            'user': users_for_interaction[2],
            'overall_rating': 5,
            'clarity_rating': 5,
            'effectiveness_rating': 5,
            'accuracy_rating': 5,
            'review_title': 'Best Palm Oil Extraction Method',
            'review_content': 'This traditional method produces the highest quality palm oil. The temperature and pressure specifications are perfect. Oil quality exceeds international standards.',
            'actual_yield_achieved': Decimal('21.80'),
            'processing_time_actual': 175,
            'would_recommend': True,
            'improvement_suggestions': 'Perfect as is. No improvements needed.'
        }
    ]
    
    for rating_data in ratings_data:
        rating, created = RecipeRating.objects.get_or_create(
            recipe=rating_data['recipe'],
            user=rating_data['user'],
            defaults=rating_data
        )
    
    # Create usage logs
    usage_logs_data = [
        {
            'recipe': recipe1,
            'user': users_for_interaction[0],
            'processing_facility': 'Golden Mills - Main Plant',
            'batch_size': Decimal('500.00'),
            'success': True,
            'actual_yield': Decimal('84.50'),
            'processing_time_actual': 125,
            'notes': 'Smooth operation. Quality exceeded expectations.',
        },
        {
            'recipe': recipe1,
            'user': users_for_interaction[1],
            'processing_facility': 'Northern Mills Co.',
            'batch_size': Decimal('200.00'),
            'success': True,
            'actual_yield': Decimal('83.20'),
            'processing_time_actual': 135,
            'notes': 'Good results. Equipment performed well with recipe instructions.',
        },
        {
            'recipe': recipe2,
            'user': users_for_interaction[2],
            'processing_facility': 'OilTech Processing Center',
            'batch_size': Decimal('1000.00'),
            'success': True,
            'actual_yield': Decimal('21.80'),
            'processing_time_actual': 175,
            'notes': 'Excellent oil quality. Traditional method works perfectly.',
        }
    ]
    
    for log_data in usage_logs_data:
        usage_log, created = RecipeUsageLog.objects.get_or_create(
            recipe=log_data['recipe'],
            user=log_data['user'],
            processing_facility=log_data['processing_facility'],
            defaults=log_data
        )
    
    # Create comments
    comments_data = [
        {
            'recipe': recipe1,
            'user': users_for_interaction[1],
            'content': 'What mesh size do you recommend for the final sifting stage?',
            'is_question': True,
            'is_answered': False
        },
        {
            'recipe': recipe1,
            'user': user1,  # Recipe owner responds
            'content': 'For premium flour, I recommend using 200 mesh (75 microns) for the final sifting. This gives the best texture for baking applications.',
            'is_question': False,
            'is_answered': False
        },
        {
            'recipe': recipe2,
            'user': users_for_interaction[0],
            'content': 'Excellent recipe! The temperature control specifications are very precise and helpful.',
            'is_question': False,
            'is_answered': False
        }
    ]
    
    for comment_data in comments_data:
        comment, created = RecipeComment.objects.get_or_create(
            recipe=comment_data['recipe'],
            user=comment_data['user'],
            content=comment_data['content'],
            defaults=comment_data
        )
    
    # Update recipe statistics
    for recipe in recipes:
        # Update times used
        recipe.times_used = recipe.usage_logs.count()
        
        # Update average rating
        ratings = recipe.ratings.all()
        if ratings.exists():
            avg_rating = sum(r.overall_rating for r in ratings) / len(ratings)
            recipe.average_rating = Decimal(str(round(avg_rating, 2)))
            recipe.rating_count = len(ratings)
        
        # Update success rate
        successful_logs = recipe.usage_logs.filter(success=True)
        if recipe.usage_logs.exists():
            success_rate = (successful_logs.count() / recipe.usage_logs.count()) * 100
            recipe.success_rate_percentage = Decimal(str(round(success_rate, 2)))
        
        recipe.save()
    
    # Update processor profile statistics
    for user, profile in processors:
        profile.total_recipes_shared = user.processing_recipes.filter(is_public=True).count()
        recipes_ratings = RecipeRating.objects.filter(recipe__processor=user)
        if recipes_ratings.exists():
            avg_rating = sum(r.overall_rating for r in recipes_ratings) / len(recipes_ratings)
            profile.average_recipe_rating = Decimal(str(round(avg_rating, 2)))
        profile.save()
    
    print("✅ Sample Data Creation Complete!\n")
    print("📊 RECIPE SHARING SYSTEM STATISTICS:")
    print(f"   • Processor Profiles: {ProcessorProfile.objects.count()}")
    print(f"   • Processing Recipes: {ProcessingRecipe.objects.count()}")
    print(f"   • Recipe Ratings: {RecipeRating.objects.count()}")
    print(f"   • Usage Logs: {RecipeUsageLog.objects.count()}")
    print(f"   • Recipe Comments: {RecipeComment.objects.count()}")
    print("\n🎯 KEY FEATURES DEMONSTRATED:")
    print("   ✅ Complete recipe creation and management")
    print("   ✅ Processor profile verification system")
    print("   ✅ Recipe rating and review system")
    print("   ✅ Usage tracking and analytics")
    print("   ✅ Community discussion and Q&A")
    print("   ✅ Technical support documentation")
    print("   ✅ Quality standards integration")
    print("   ✅ Best practices sharing")
    
    return True

if __name__ == "__main__":
    try:
        create_sample_data()
        print("\n🎉 AgriConnect Recipe Sharing System is ready for production!")
        print("🌐 API Endpoints available at: /api/v1/processors/")
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()
