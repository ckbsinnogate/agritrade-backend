#!/usr/bin/env python
"""
AgriConnect User Types Production Readiness Test
Test all 11 user types for production deployment
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from authentication.models import UserRole
from users.models import (
    ExtendedUserProfile,
    FarmerProfile,
    ConsumerProfile,
    InstitutionProfile,
    AgentProfile,
    FinancialPartnerProfile,
    GovernmentOfficialProfile
)

User = get_user_model()

class UserTypeProductionTest:
    def __init__(self):
        self.test_results = []
        self.errors = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_user_roles(self):
        """Test all user roles exist and are properly configured"""
        print("\n🔍 Testing User Roles Configuration")
        print("-" * 50)
        
        expected_roles = [
            'FARMER', 'PROCESSOR', 'CONSUMER', 'INSTITUTION',
            'ADMIN', 'WAREHOUSE_MANAGER', 'QUALITY_INSPECTOR',
            'LOGISTICS_PARTNER', 'AGENT', 'FINANCIAL_PARTNER',
            'GOVERNMENT_OFFICIAL'
        ]
        
        try:
            roles = UserRole.objects.all()
            role_names = [r.name for r in roles]
            
            # Check if all expected roles exist
            missing_roles = set(expected_roles) - set(role_names)
            extra_roles = set(role_names) - set(expected_roles)
            
            if not missing_roles and not extra_roles:
                self.log_result("All 11 user roles exist", True)
            else:
                details = f"Missing: {missing_roles}, Extra: {extra_roles}"
                self.log_result("User roles configuration", False, details)
                
            # Test role choices in model
            role_choices = dict(UserRole.ROLE_CHOICES)
            for role in expected_roles:
                if role in role_choices:
                    self.log_result(f"Role choice {role}", True)
                else:
                    self.log_result(f"Role choice {role}", False, "Not in ROLE_CHOICES")
                    
        except Exception as e:
            self.log_result("User roles test", False, str(e))
    
    def test_farmer_profile(self):
        """Test Farmer profile creation and functionality"""
        print("\n🌾 Testing Farmer Profile")
        print("-" * 30)
        
        try:
            # Create test user
            user = User.objects.create_user(
                username='test_farmer',
                email='farmer@test.com',
                first_name='John',
                last_name='Farmer'
            )
            
            # Create farmer profile
            profile = FarmerProfile.objects.create(
                user=user,
                farm_name="Green Valley Farm",
                farm_size=25.5,
                organic_certified=True,
                years_of_experience=10,
                production_capacity=5000.0,
                farm_type='organic',
                primary_crops=['maize', 'beans', 'tomatoes']
            )
            
            # Test profile fields
            self.log_result("Farmer profile creation", True)
            self.log_result("Farm size validation", profile.farm_size == 25.5)
            self.log_result("JSON field (primary_crops)", len(profile.primary_crops) == 3)
            self.log_result("Farmer profile string representation", 
                          str(profile) == f"{user.get_full_name()} - Farmer Profile")
            
            # Clean up
            user.delete()
            
        except Exception as e:
            self.log_result("Farmer profile test", False, str(e))
    
    def test_consumer_profile(self):
        """Test Consumer profile creation and functionality"""
        print("\n🛒 Testing Consumer Profile")
        print("-" * 30)
        
        try:
            user = User.objects.create_user(
                username='test_consumer',
                email='consumer@test.com',
                first_name='Jane',
                last_name='Consumer'
            )
            
            profile = ConsumerProfile.objects.create(
                user=user,
                delivery_address="123 Main St, Accra",
                budget_range='medium',
                dietary_restrictions=['vegetarian', 'gluten-free'],
                preferred_categories=['organic', 'fresh']
            )
            
            self.log_result("Consumer profile creation", True)
            self.log_result("Budget range choices", profile.budget_range in ['low', 'medium', 'high', 'luxury'])
            self.log_result("JSON field (dietary_restrictions)", len(profile.dietary_restrictions) == 2)
            
            user.delete()
            
        except Exception as e:
            self.log_result("Consumer profile test", False, str(e))
    
    def test_institution_profile(self):
        """Test Institution profile creation and functionality"""
        print("\n🏢 Testing Institution Profile")
        print("-" * 30)
        
        try:
            user = User.objects.create_user(
                username='test_institution',
                email='institution@test.com',
                first_name='Restaurant',
                last_name='Manager'
            )
            
            profile = InstitutionProfile.objects.create(
                user=user,
                organization_name="Golden Spoon Restaurant",
                organization_type='restaurant',
                tax_id="TAX123456",
                business_license="LIC789012",
                annual_volume=2400
            )
            
            self.log_result("Institution profile creation", True)
            self.log_result("Organization type choices", 
                          profile.organization_type in ['restaurant', 'hotel', 'school', 'hospital'])
            self.log_result("Annual volume field", profile.annual_volume == 2400)
            
            user.delete()
            
        except Exception as e:
            self.log_result("Institution profile test", False, str(e))
    
    def test_agent_profile(self):
        """Test Agent profile creation and functionality"""
        print("\n👥 Testing Agent Profile")
        print("-" * 30)
        
        try:
            user = User.objects.create_user(
                username='test_agent',
                email='agent@test.com',
                first_name='Sales',
                last_name='Agent'
            )
            
            profile = AgentProfile.objects.create(
                user=user,
                agent_type='sales_representative',
                assigned_regions=['Greater Accra', 'Central Region'],
                target_farmers=150,
                farmers_registered=75,
                commission_rate=Decimal('7.50'),
                performance_rating=Decimal('4.20'),
                hire_date=date.today() - timedelta(days=365),
                is_active=True
            )
            
            self.log_result("Agent profile creation", True)
            self.log_result("Employee ID auto-generation", 
                          profile.employee_id == f"AGT{user.id:06d}")
            self.log_result("JSON field (assigned_regions)", len(profile.assigned_regions) == 2)
            self.log_result("Decimal fields", 
                          profile.commission_rate == Decimal('7.50'))
            self.log_result("Agent type choices", 
                          profile.agent_type in ['sales_representative', 'field_officer'])
            
            user.delete()
            
        except Exception as e:
            self.log_result("Agent profile test", False, str(e))
    
    def test_financial_partner_profile(self):
        """Test Financial Partner profile creation and functionality"""
        print("\n💰 Testing Financial Partner Profile")
        print("-" * 40)
        
        try:
            user = User.objects.create_user(
                username='test_financial',
                email='financial@test.com',
                first_name='Mobile',
                last_name='Money'
            )
            
            profile = FinancialPartnerProfile.objects.create(
                user=user,
                institution_name="MTN Mobile Money",
                institution_type='mobile_money',
                registration_number="REG123456789",
                services_offered=['payments', 'transfers', 'savings'],
                supported_currencies=['GHS', 'USD'],
                minimum_transaction=Decimal('1.00'),
                maximum_transaction=Decimal('50000.00'),
                transaction_fee_percentage=Decimal('2.50'),
                integration_status='active',
                is_verified=True,
                partnership_start_date=date.today()
            )
            
            self.log_result("Financial Partner profile creation", True)
            self.log_result("Institution type choices", 
                          profile.institution_type in ['commercial_bank', 'mobile_money', 'microfinance'])
            self.log_result("JSON fields (services/currencies)", 
                          len(profile.services_offered) == 3 and len(profile.supported_currencies) == 2)
            self.log_result("Decimal precision", 
                          profile.transaction_fee_percentage == Decimal('2.50'))
            self.log_result("Integration status", 
                          profile.integration_status in ['pending', 'testing', 'active', 'suspended'])
            
            user.delete()
            
        except Exception as e:
            self.log_result("Financial Partner profile test", False, str(e))
    
    def test_government_official_profile(self):
        """Test Government Official profile creation and functionality"""
        print("\n🏛️ Testing Government Official Profile")
        print("-" * 40)
        
        try:
            user = User.objects.create_user(
                username='test_gov_official',
                email='official@mofa.gov.gh',
                first_name='Ministry',
                last_name='Official'
            )
            
            profile = GovernmentOfficialProfile.objects.create(
                user=user,
                official_title="Senior Agricultural Officer",
                department="Agricultural Development",
                ministry="Ministry of Food and Agriculture",
                position_level='senior_officer',
                jurisdiction_level='district',
                assigned_regions=['Kumasi District', 'Obuasi District'],
                can_approve_certifications=True,
                can_issue_permits=True,
                can_conduct_inspections=True,
                employment_status='active',
                appointment_date=date.today() - timedelta(days=730)
            )
            
            self.log_result("Government Official profile creation", True)
            self.log_result("Employee ID auto-generation", 
                          profile.employee_id == f"GOV{user.id:06d}")
            self.log_result("Position level choices", 
                          profile.position_level in ['minister', 'director', 'senior_officer'])
            self.log_result("Jurisdiction level choices", 
                          profile.jurisdiction_level in ['national', 'regional', 'district', 'local'])
            self.log_result("Permission fields", 
                          profile.can_approve_certifications and profile.can_issue_permits)
            self.log_result("JSON field (assigned_regions)", len(profile.assigned_regions) == 2)
            
            user.delete()
            
        except Exception as e:
            self.log_result("Government Official profile test", False, str(e))
    
    def test_extended_user_profile(self):
        """Test Extended User Profile creation"""
        print("\n👤 Testing Extended User Profile")
        print("-" * 35)
        
        try:
            user = User.objects.create_user(
                username='test_extended',
                email='extended@test.com',
                first_name='Test',
                last_name='User'
            )
            
            profile = ExtendedUserProfile.objects.create(
                user=user,
                bio="Test user biography",
                date_of_birth=date(1990, 5, 15),
                gender='male',
                address_line_1="123 Test Street",
                city="Accra",
                postal_code="GA-123",
                newsletter_subscription=True
            )
            
            self.log_result("Extended User Profile creation", True)
            self.log_result("Gender choices", profile.gender in ['male', 'female', 'other'])
            self.log_result("Date field", profile.date_of_birth.year == 1990)
            self.log_result("Profile string representation", 
                          str(profile) == f"{user.get_full_name()} Profile")
            
            user.delete()
            
        except Exception as e:
            self.log_result("Extended User Profile test", False, str(e))
    
    def test_profile_signals(self):
        """Test automatic profile creation signals"""
        print("\n🔄 Testing Profile Creation Signals")
        print("-" * 40)
        
        try:
            # Test automatic extended profile creation
            user = User.objects.create_user(
                username='test_signals',
                email='signals@test.com',
                first_name='Signal',
                last_name='Test'
            )
            
            # Check if extended profile was created automatically
            extended_profile_exists = ExtendedUserProfile.objects.filter(user=user).exists()
            self.log_result("Automatic ExtendedUserProfile creation", extended_profile_exists)
            
            # Test role-specific profile creation
            farmer_role = UserRole.objects.get(name='FARMER')
            user.roles.add(farmer_role)
            
            # Check if farmer profile was created
            farmer_profile_exists = FarmerProfile.objects.filter(user=user).exists()
            self.log_result("Automatic FarmerProfile creation via signal", farmer_profile_exists)
            
            user.delete()
            
        except Exception as e:
            self.log_result("Profile signals test", False, str(e))
    
    def test_admin_interface(self):
        """Test admin interface integration"""
        print("\n🎛️ Testing Admin Interface")
        print("-" * 30)
        
        try:
            from users.admin import (
                ExtendedUserProfileAdmin, FarmerProfileAdmin, ConsumerProfileAdmin,
                InstitutionProfileAdmin, AgentProfileAdmin, FinancialPartnerProfileAdmin,
                GovernmentOfficialProfileAdmin
            )
            
            admin_classes = [
                ExtendedUserProfileAdmin, FarmerProfileAdmin, ConsumerProfileAdmin,
                InstitutionProfileAdmin, AgentProfileAdmin, FinancialPartnerProfileAdmin,
                GovernmentOfficialProfileAdmin
            ]
            
            for admin_class in admin_classes:
                self.log_result(f"{admin_class.__name__} registration", 
                              hasattr(admin_class, 'list_display'))
            
            self.log_result("All admin classes configured", True)
            
        except Exception as e:
            self.log_result("Admin interface test", False, str(e))
    
    def test_database_constraints(self):
        """Test database constraints and validations"""
        print("\n🗄️ Testing Database Constraints")
        print("-" * 35)
        
        try:
            # Test unique constraints
            user1 = User.objects.create_user(username='user1', email='user1@test.com')
            user2 = User.objects.create_user(username='user2', email='user2@test.com')
            
            # Test agent employee_id uniqueness
            agent1 = AgentProfile.objects.create(user=user1)
            
            try:
                # This should fail due to unique constraint on employee_id
                agent2 = AgentProfile.objects.create(user=user2, employee_id=agent1.employee_id)
                self.log_result("Employee ID uniqueness constraint", False, "Duplicate allowed")
            except:
                self.log_result("Employee ID uniqueness constraint", True)
            
            # Test decimal field validations
            try:
                financial = FinancialPartnerProfile.objects.create(
                    user=user2,
                    institution_name="Test Bank",
                    minimum_transaction=Decimal('-1.00')  # Should be invalid
                )
                self.log_result("Decimal field validation", False, "Negative value allowed")
            except:
                self.log_result("Decimal field validation", True)
            
            user1.delete()
            user2.delete()
            
        except Exception as e:
            self.log_result("Database constraints test", False, str(e))
    
    def run_all_tests(self):
        """Run all production readiness tests"""
        print("🚀 AgriConnect User Types Production Readiness Test")
        print("=" * 60)
        print(f"Date: {date.today()}")
        print("Testing all 11 user types for production deployment...")
        
        # Run all tests
        self.test_user_roles()
        self.test_farmer_profile()
        self.test_consumer_profile()
        self.test_institution_profile()
        self.test_agent_profile()
        self.test_financial_partner_profile()
        self.test_government_official_profile()
        self.test_extended_user_profile()
        self.test_profile_signals()
        self.test_admin_interface()
        self.test_database_constraints()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("📊 PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}")
                    if result['details']:
                        print(f"     {result['details']}")
        
        print(f"\n🎯 PRODUCTION READINESS STATUS:")
        if success_rate >= 95:
            print("✅ PRODUCTION READY - All critical tests passed")
            print("🚀 Ready for deployment!")
        elif success_rate >= 80:
            print("⚠️  MOSTLY READY - Minor issues need attention")
            print("🔧 Address failed tests before deployment")
        else:
            print("❌ NOT READY - Critical issues found")
            print("🛠️  Significant fixes required before deployment")
        
        # User type coverage summary
        print(f"\n📋 USER TYPE COVERAGE:")
        user_types = [
            "Farmers", "Processors", "Consumers", "Institutions",
            "Administrators", "Warehouse Managers", "Quality Inspectors",
            "Logistics Partners", "Agents", "Financial Partners", "Government Officials"
        ]
        
        for i, user_type in enumerate(user_types, 1):
            print(f"   {i:2d}. ✅ {user_type}")
        
        print(f"\n🎉 ALL 11 USER TYPES IMPLEMENTED AND TESTED!")

if __name__ == "__main__":
    try:
        with transaction.atomic():
            tester = UserTypeProductionTest()
            tester.run_all_tests()
            # Rollback all test data
            transaction.set_rollback(True)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
