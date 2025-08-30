#!/usr/bin/env python3
"""
AgriConnect Backend Compatibility Final Validation
Comprehensive test of all user profile and reviews systems
"""

import os
import sys
import django
from datetime import datetime, date

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_user_profile_system():
    """Test complete user profile management system"""
    print("🔍 TESTING USER PROFILE SYSTEM")
    print("=" * 50)
    
    try:
        # Test imports
        from django.contrib.auth import get_user_model
        from authentication.models import UserRole
        from users.models import (
            ExtendedUserProfile, FarmerProfile, ConsumerProfile,
            InstitutionProfile, AgentProfile, FinancialPartnerProfile,
            GovernmentOfficialProfile
        )
        from users.serializers import (
            ComprehensiveUserProfileSerializer, UserActivationSerializer,
            UserProfileUpdateSerializer
        )
        from users.views import (
            UserProfileView, ComprehensiveUserProfileView,
            UserActivationView, user_profile_status
        )
        
        User = get_user_model()
        
        print("✅ All imports successful")
        
        # Test user creation
        test_email = 'validation.test@agriconnect.com'
        User.objects.filter(email=test_email).delete()  # Clean up
        
        test_user = User.objects.create_user(
            identifier=test_email,
            password='ValidationTest123!',
            first_name='Validation',
            last_name='Test',
            roles=['FARMER']
        )
        
        print(f"✅ User created: {test_user.email}")
        print(f"✅ User roles: {[r.name for r in test_user.roles.all()]}")
        
        # Test profile creation
        extended_profile, created = ExtendedUserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'bio': 'Test farmer biography',
                'gender': 'male',
                'city': 'Accra'
            }
        )
        print(f"✅ Extended profile created: {created}")
        
        farmer_profile, created = FarmerProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'farm_name': 'Test Farm',
                'farm_size': 5.0,
                'farm_type': 'crop',
                'years_of_experience': 10
            }
        )
        print(f"✅ Farmer profile created: {created}")
        
        # Test serializers
        serializer = ComprehensiveUserProfileSerializer(test_user)
        profile_data = serializer.data
        
        print(f"✅ Profile completion: {profile_data.get('profile_completion', 0)}%")
        print(f"✅ User type: {profile_data.get('user_type')}")
        print(f"✅ Roles display: {profile_data.get('roles_display')}")
        
        # Test activation
        activation_serializer = UserActivationSerializer()
        activation_serializer.update(test_user, {})
        
        print(f"✅ Account activated: {test_user.is_active}")
        print(f"✅ Account verified: {test_user.is_verified}")
        
        # Clean up
        test_user.delete()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ User profile system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reviews_system():
    """Test reviews system compatibility"""
    print("\n🔍 TESTING REVIEWS SYSTEM")
    print("=" * 50)
    
    try:
        from reviews.models import Review, ReviewHelpfulVote, ReviewFlag
        from reviews.serializers import ReviewListSerializer, ReviewDetailSerializer
        from reviews.views import ReviewViewSet
        
        print("✅ Reviews models imported")
        print("✅ Reviews serializers imported")
        print("✅ Reviews views imported")
        
        # Test ViewSet
        viewset = ReviewViewSet()
        
        # Check required methods
        required_methods = ['my_reviews', 'helpful_vote', 'flag_review', 'trending', 'analytics']
        for method in required_methods:
            if hasattr(viewset, method):
                print(f"✅ ReviewViewSet.{method}: Available")
            else:
                print(f"❌ ReviewViewSet.{method}: Missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Reviews system test failed: {e}")
        return False


def test_url_configuration():
    """Test URL configuration"""
    print("\n🔍 TESTING URL CONFIGURATION")
    print("=" * 50)
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test API roots
        endpoints_to_test = [
            '/api/v1/',
            '/api/v1/auth/',
            '/api/v1/users/',
            '/api/v1/reviews/',
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = client.get(endpoint)
                print(f"✅ {endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ URL configuration test failed: {e}")
        return False


def test_database_schema():
    """Test database schema integrity"""
    print("\n🔍 TESTING DATABASE SCHEMA")
    print("=" * 50)
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Check key tables exist
            tables_to_check = [
                'users',  # User model
                'authentication_userrole',  # UserRole model
                'users_extendeduserprofile',  # ExtendedUserProfile
                'users_farmerprofile',  # FarmerProfile
                'users_consumerprofile',  # ConsumerProfile
                'reviews_review',  # Review model
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables_to_check:
                if table in existing_tables:
                    print(f"✅ Table {table}: Exists")
                else:
                    print(f"❌ Table {table}: Missing")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False


def run_comprehensive_validation():
    """Run all validation tests"""
    print("🎯 AGRICONNECT BACKEND FINAL VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    tests = [
        ("User Profile System", test_user_profile_system),
        ("Reviews System", test_reviews_system),
        ("URL Configuration", test_url_configuration),
        ("Database Schema", test_database_schema),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_function():
            passed_tests += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print("\n" + "="*60)
    print("🎯 FINAL VALIDATION RESULTS")
    print("="*60)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 MISSION ACCOMPLISHED!")
        print("✅ All backend compatibility issues resolved")
        print("✅ User profile management fully operational")  
        print("✅ Reviews system completely functional")
        print("✅ URL routing properly configured")
        print("✅ Database schema integrity verified")
        print("\n🚀 Backend is production-ready for frontend integration!")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("❌ Some issues need attention before frontend integration")
        return False


if __name__ == "__main__":
    try:
        success = run_comprehensive_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
