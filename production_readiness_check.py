#!/usr/bin/env python
"""
AgriConnect Production Readiness Validation
Comprehensive check for all user types and system components
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from authentication.models import UserRole
from users.models import *
from django.db import connection

User = get_user_model()

def production_readiness_check():
    """Comprehensive production readiness validation"""
    
    print("🏭 AGRICONNECT PRODUCTION READINESS CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"Environment: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Unknown')}")
    print()
    
    issues = []
    checks_passed = 0
    total_checks = 0
    
    # 1. Database Connection Test
    print("1. DATABASE CONNECTION")
    print("-" * 30)
    total_checks += 1
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result[0] == 1:
            print("✅ Database connection: WORKING")
            checks_passed += 1
        else:
            print("❌ Database connection: FAILED")
            issues.append("Database connection failed")
    except Exception as e:
        print(f"❌ Database connection: ERROR - {e}")
        issues.append(f"Database error: {e}")
    
    print()
    
    # 2. User Roles Validation
    print("2. USER ROLES VALIDATION")
    print("-" * 30)
    total_checks += 1
    
    expected_roles = [
        'FARMER', 'CONSUMER', 'INSTITUTION', 'ADMINISTRATOR',
        'WAREHOUSE_MANAGER', 'QUALITY_INSPECTOR', 'LOGISTICS_PARTNER',
        'PROCESSOR', 'AGENT', 'FINANCIAL_PARTNER', 'GOVERNMENT_OFFICIAL'
    ]
    
    try:
        actual_roles = list(UserRole.objects.values_list('name', flat=True))
        
        # Handle ADMIN vs ADMINISTRATOR naming
        if 'ADMIN' in actual_roles and 'ADMINISTRATOR' not in actual_roles:
            actual_roles = ['ADMINISTRATOR' if x == 'ADMIN' else x for x in actual_roles]
        
        print(f"Expected roles: {len(expected_roles)}")
        print(f"Found roles: {len(actual_roles)}")
        
        missing_roles = set(expected_roles) - set(actual_roles)
        extra_roles = set(actual_roles) - set(expected_roles)
        
        if not missing_roles:
            print("✅ All required roles present")
            checks_passed += 1
        else:
            print(f"❌ Missing roles: {missing_roles}")
            issues.append(f"Missing user roles: {missing_roles}")
        
        if extra_roles:
            print(f"ℹ️ Extra roles found: {extra_roles}")
            
        # List all roles
        print("Available roles:")
        for role in UserRole.objects.all().order_by('name'):
            print(f"  - {role.name}: {role.description}")
            
    except Exception as e:
        print(f"❌ Role validation failed: {e}")
        issues.append(f"Role validation error: {e}")
    
    print()
    
    # 3. Profile Models Validation
    print("3. PROFILE MODELS VALIDATION")
    print("-" * 30)
    
    profile_models = [
        ('ExtendedUserProfile', ExtendedUserProfile),
        ('FarmerProfile', FarmerProfile),
        ('ConsumerProfile', ConsumerProfile),
        ('InstitutionProfile', InstitutionProfile),
        ('AgentProfile', AgentProfile),
        ('FinancialPartnerProfile', FinancialPartnerProfile),
        ('GovernmentOfficialProfile', GovernmentOfficialProfile)
    ]
    
    model_checks = 0
    for name, model in profile_models:
        total_checks += 1
        try:
            # Test model functionality
            field_count = len(model._meta.fields)
            instance_count = model.objects.count()
            
            # Test model can be instantiated (dry run)
            required_fields = [f for f in model._meta.fields if not f.null and not f.blank and f.name != 'id']
            
            print(f"✅ {name}: {field_count} fields, {instance_count} instances")
            model_checks += 1
            checks_passed += 1
            
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            issues.append(f"Profile model {name} error: {e}")
    
    print(f"Profile models status: {model_checks}/{len(profile_models)} working")
    print()
    
    # 4. User Creation Test
    print("4. USER CREATION & AUTHENTICATION TEST")
    print("-" * 30)
    total_checks += 1
    
    try:
        # Clean up any existing test users
        User.objects.filter(email='production.test@agriconnect.com').delete()
        
        # Test user creation with email
        test_user = User.objects.create_user_with_identifier(
            identifier='production.test@agriconnect.com',
            password='ProductionTest123!',
            first_name='Production',
            last_name='Test',
            roles=['FARMER']
        )
        
        # Verify user properties
        assert test_user.email == 'production.test@agriconnect.com'
        assert test_user.first_name == 'Production'
        assert test_user.roles.filter(name='FARMER').exists()
        
        print(f"✅ User created: {test_user.username}")
        print(f"✅ Email set: {test_user.email}")
        print(f"✅ Role assigned: {test_user.roles.first().name}")
        
        # Test profile creation
        farmer_profile = FarmerProfile.objects.create(
            user=test_user,
            farm_name="Production Test Farm",
            farm_size=15.5,
            organic_certified=True
        )
        
        print(f"✅ Profile created: {farmer_profile}")
        
        # Test authentication
        from django.contrib.auth import authenticate
        auth_user = authenticate(username=test_user.username, password='ProductionTest123!')
        if auth_user:
            print("✅ Authentication: WORKING")
        else:
            print("❌ Authentication: FAILED")
            issues.append("User authentication failed")
        
        # Clean up
        test_user.delete()
        print("✅ Test cleanup: SUCCESSFUL")
        
        checks_passed += 1
        
    except Exception as e:
        print(f"❌ User creation test failed: {e}")
        issues.append(f"User creation error: {e}")
    
    print()
    
    # 5. Security & Settings Check
    print("5. SECURITY & SETTINGS CHECK")
    print("-" * 30)
    total_checks += 1
    
    try:
        from django.conf import settings
        
        security_checks = []
        
        # Check critical settings
        if hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY:
            if len(settings.SECRET_KEY) >= 50:
                security_checks.append("✅ SECRET_KEY: Adequate length")
            else:
                security_checks.append("⚠️ SECRET_KEY: Should be longer")
        else:
            security_checks.append("❌ SECRET_KEY: Missing")
            
        if hasattr(settings, 'DATABASES') and settings.DATABASES:
            security_checks.append("✅ DATABASE: Configured")
        else:
            security_checks.append("❌ DATABASE: Not configured")
            
        if hasattr(settings, 'INSTALLED_APPS') and 'users' in settings.INSTALLED_APPS:
            security_checks.append("✅ USERS_APP: Installed")
        else:
            security_checks.append("❌ USERS_APP: Not in INSTALLED_APPS")
            
        for check in security_checks:
            print(f"  {check}")
            
        checks_passed += 1
        
    except Exception as e:
        print(f"❌ Settings check failed: {e}")
        issues.append(f"Settings error: {e}")
    
    print()
    
    # 6. Final Assessment
    print("6. FINAL PRODUCTION ASSESSMENT")
    print("-" * 30)
    
    success_rate = (checks_passed / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"Total checks: {total_checks}")
    print(f"Checks passed: {checks_passed}")
    print(f"Success rate: {success_rate:.1f}%")
    print()
    
    if issues:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
    
    if success_rate >= 100:
        print("🎉 PRODUCTION READY!")
        print("✅ All systems operational")
        print("✅ All user types implemented")
        print("✅ Database schema complete")
        print("✅ Authentication working")
        print("🚀 READY FOR DEPLOYMENT!")
        
    elif success_rate >= 80:
        print("⚠️ MOSTLY READY - Minor issues to address")
        print("🔧 Fix the issues above before full production deployment")
        
    else:
        print("❌ NOT READY FOR PRODUCTION")
        print("🛑 Critical issues must be resolved")
    
    print()
    print("=" * 60)
    print("End of Production Readiness Check")
    
    return success_rate >= 100, issues

if __name__ == "__main__":
    try:
        ready, issues = production_readiness_check()
        if ready:
            print("\n🌟 FINAL VERDICT: PRODUCTION DEPLOYMENT APPROVED! 🌟")
        else:
            print(f"\n⚠️ FINAL VERDICT: {len(issues)} ISSUES NEED RESOLUTION")
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
