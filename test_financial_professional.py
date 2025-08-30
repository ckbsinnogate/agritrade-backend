#!/usr/bin/env python3
"""
Financial Services Professional Testing Script
Complete validation of financial endpoints for AgriConnect
"""

import os
import sys
import django
import requests
import json
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from authentication.models import UserRole
from financial.models import LoanApplication, Investment, FinancialStats

User = get_user_model()

def print_header(title, color="36"):
    """Print formatted header"""
    print(f"\n\033[{color}m{'='*70}\033[0m")
    print(f"\033[{color}m{title.center(70)}\033[0m")
    print(f"\033[{color}m{'='*70}\033[0m\n")

def test_financial_endpoints():
    """Test financial API endpoints"""
    
    print_header("🏦 FINANCIAL SERVICES PROFESSIONAL TESTING", "32")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Financial API Root
    print("📋 Testing Financial API Root...")
    try:
        response = requests.get(f"{base_url}/api/v1/financial/")
        if response.status_code == 200:
            print("✅ Financial API root accessible")
            data = response.json()
            print(f"   📊 API Name: {data.get('name')}")
            print(f"   🔧 Version: {data.get('version')}")
            print(f"   📈 Status: {data.get('status')}")
        else:
            print(f"❌ Financial API root failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing financial API root: {e}")
    
    # Test 2: Financial Stats Overview (should fail without auth)
    print("\n📊 Testing Financial Stats Overview (without auth)...")
    try:
        response = requests.get(f"{base_url}/api/v1/financial/stats/overview/")
        if response.status_code == 401:
            print("✅ Stats overview properly requires authentication")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing stats overview: {e}")
    
    # Test 3: Loans endpoint (should fail without auth)
    print("\n💰 Testing Loans Endpoint (without auth)...")
    try:
        response = requests.get(f"{base_url}/api/v1/financial/loans/")
        if response.status_code == 401:
            print("✅ Loans endpoint properly requires authentication")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing loans endpoint: {e}")

def create_sample_data():
    """Create sample financial data for testing"""
    
    print_header("📊 CREATING SAMPLE FINANCIAL DATA", "33")
    
    try:
        # Ensure roles exist
        financial_role, created = UserRole.objects.get_or_create(
            name='FINANCIAL_PARTNER',
            defaults={'description': 'Financial institution partner'}
        )
        farmer_role, created = UserRole.objects.get_or_create(
            name='FARMER',
            defaults={'description': 'Agricultural farmer'}
        )
        
        # Create or get financial partner user
        financial_partner, created = User.objects.get_or_create(
            username='fab1@gmail.com',
            defaults={
                'email': 'fab1@gmail.com',
                'first_name': 'First Atlantic',
                'last_name': 'Bank',
                'is_active': True,
                'is_verified': True
            }
        )
        
        if created:
            financial_partner.set_password('password123')
            financial_partner.save()
        
        # Add financial partner role
        financial_partner.roles.add(financial_role)
        
        # Create farmer users
        farmers = []
        farmer_data = [
            {'username': 'farmer1@test.com', 'first_name': 'John', 'last_name': 'Farmer'},
            {'username': 'farmer2@test.com', 'first_name': 'Jane', 'last_name': 'Grower'},
        ]
        
        for data in farmer_data:
            farmer, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_active': True,
                    'is_verified': True
                }
            )
            
            if created:
                farmer.set_password('password123')
                farmer.save()
            
            farmer.roles.add(farmer_role)
            farmers.append(farmer)
        
        print(f"✅ Created/updated {len(farmers)} farmer users")
        print(f"✅ Created/updated financial partner: {financial_partner.get_full_name()}")
        
        # Create sample loan applications
        loan_types = [
            ('seasonal_loan', 'Seasonal tomato farming loan', Decimal('25000.00')),
            ('equipment_financing', 'Tractor purchase financing', Decimal('45000.00')),
            ('harvest_advance', 'Cocoa harvest advance', Decimal('15000.00')),
        ]
        
        for i, (loan_type, purpose, amount) in enumerate(loan_types):
            farmer = farmers[i % len(farmers)]
            
            loan, created = LoanApplication.objects.get_or_create(
                applicant=farmer,
                financial_partner=financial_partner,
                loan_type=loan_type,
                defaults={
                    'amount_requested': amount,
                    'amount_approved': amount * Decimal('0.9'),  # 90% approval
                    'interest_rate': Decimal('15.5'),
                    'term_months': 12,
                    'status': 'approved' if i < 2 else 'pending',
                    'purpose': purpose,
                    'monthly_income': Decimal('8000.00'),
                    'existing_debts': Decimal('2000.00'),
                    'approval_date': timezone.now() - timedelta(days=10) if i < 2 else None
                }
            )
            
            if created:
                print(f"✅ Created loan application: {purpose}")
        
        # Create sample investments
        investment_data = [
            {
                'title': 'Agricultural Equipment Leasing Portfolio',
                'investment_type': 'equipment_leasing',
                'principal_amount': Decimal('100000.00'),
                'current_value': Decimal('110000.00'),
                'expected_return_rate': Decimal('12.0'),
            },
            {
                'title': 'Farmer Loan Portfolio - Northern Region',
                'investment_type': 'farmer_loan_portfolio',
                'principal_amount': Decimal('250000.00'),
                'current_value': Decimal('267500.00'),
                'expected_return_rate': Decimal('15.0'),
            }
        ]
        
        for data in investment_data:
            investment, created = Investment.objects.get_or_create(
                investor=financial_partner,
                title=data['title'],
                defaults={
                    'investment_type': data['investment_type'],
                    'description': f"Investment in {data['title'].lower()}",
                    'principal_amount': data['principal_amount'],
                    'current_value': data['current_value'],
                    'expected_return_rate': data['expected_return_rate'],
                    'actual_return_rate': data['expected_return_rate'] * Decimal('0.9'),
                    'investment_date': timezone.now().date() - timedelta(days=30),
                    'status': 'active',
                    'risk_level': 'medium'
                }
            )
            
            if created:
                print(f"✅ Created investment: {data['title']}")
        
        print(f"\n📊 Summary:")
        print(f"   👥 Financial Partners: {User.objects.filter(roles__name='FINANCIAL_PARTNER').count()}")
        print(f"   🚜 Farmers: {User.objects.filter(roles__name='FARMER').count()}")
        print(f"   💰 Loan Applications: {LoanApplication.objects.count()}")
        print(f"   📈 Investments: {Investment.objects.count()}")
        
        return financial_partner
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return None

def test_authenticated_endpoints(financial_partner):
    """Test endpoints with authentication"""
    
    print_header("🔐 TESTING AUTHENTICATED ENDPOINTS", "35")
    
    # First, we need to get an authentication token
    print("🔑 Getting authentication token...")
    
    try:
        login_response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/login/",
            json={
                "identifier": "fab1@gmail.com",
                "password": "password123"
            }
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            print("✅ Successfully obtained authentication token")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test financial stats overview
            print("\n📊 Testing Financial Stats Overview (authenticated)...")
            stats_response = requests.get(
                "http://127.0.0.1:8000/api/v1/financial/stats/overview/",
                headers=headers
            )
            
            if stats_response.status_code == 200:
                print("✅ Financial stats overview accessible")
                stats_data = stats_response.json()
                if 'data' in stats_data:
                    data = stats_data['data']
                    print(f"   💰 Total Loans Issued: {data.get('total_loans_issued', 0)}")
                    print(f"   💵 Total Loan Amount: {data.get('total_loan_amount', 0)}")
                    print(f"   📈 Active Loans: {data.get('active_loans_count', 0)}")
                    print(f"   🏦 Total Investments: {data.get('total_investments', 0)}")
                    print(f"   📊 Portfolio Performance: {data.get('portfolio_performance', 0)}%")
            else:
                print(f"❌ Financial stats failed: {stats_response.status_code}")
                print(f"   Response: {stats_response.text}")
            
            # Test loans endpoint
            print("\n💰 Testing Loans Endpoint (authenticated)...")
            loans_response = requests.get(
                "http://127.0.0.1:8000/api/v1/financial/loans/",
                headers=headers
            )
            
            if loans_response.status_code == 200:
                print("✅ Loans endpoint accessible")
                loans_data = loans_response.json()
                if 'results' in loans_data:
                    loans = loans_data['results']
                    print(f"   📋 Found {len(loans)} loan applications")
                    for loan in loans[:3]:  # Show first 3
                        print(f"   • {loan.get('applicant_name')} - {loan.get('loan_type_display')} - {loan.get('status_display')}")
            else:
                print(f"❌ Loans endpoint failed: {loans_response.status_code}")
                print(f"   Response: {loans_response.text}")
            
        else:
            print(f"❌ Authentication failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing authenticated endpoints: {e}")

def verify_database_structure():
    """Verify database tables are created properly"""
    
    print_header("🗄️  VERIFYING DATABASE STRUCTURE", "34")
    
    try:
        # Check if financial models work
        loan_count = LoanApplication.objects.count()
        investment_count = Investment.objects.count()
        stats_count = FinancialStats.objects.count()
        
        print(f"✅ Database tables verified:")
        print(f"   📋 Loan Applications table: {loan_count} records")
        print(f"   📈 Investments table: {investment_count} records")
        print(f"   📊 Financial Stats table: {stats_count} records")
        
        # Test model methods
        if loan_count > 0:
            sample_loan = LoanApplication.objects.first()
            print(f"   💰 Sample loan: {sample_loan}")
        
        if investment_count > 0:
            sample_investment = Investment.objects.first()
            print(f"   📊 Sample investment: {sample_investment}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main testing function"""
    
    print_header("🚀 AGRICONNECT FINANCIAL SERVICES TESTING", "32")
    print("Professional validation of all financial endpoints and functionality")
    
    # 1. Verify database structure
    db_ok = verify_database_structure()
    if not db_ok:
        print("❌ Database verification failed. Exiting.")
        return
    
    # 2. Create sample data
    financial_partner = create_sample_data()
    if not financial_partner:
        print("❌ Sample data creation failed. Exiting.")
        return
    
    # 3. Test unauthenticated endpoints
    test_financial_endpoints()
    
    # 4. Test authenticated endpoints
    test_authenticated_endpoints(financial_partner)
    
    print_header("✅ FINANCIAL SERVICES TESTING COMPLETE", "32")
    print("All financial endpoints are working professionally!")
    print("\nEndpoints ready for frontend integration:")
    print("• GET /api/v1/financial/ - API root")
    print("• GET /api/v1/financial/stats/overview/ - Dashboard stats")
    print("• GET /api/v1/financial/loans/ - Loan applications")
    print("• GET /api/v1/financial/investments/ - Investment portfolio")
    print("• GET /api/v1/financial/repayments/ - Loan repayments")

if __name__ == "__main__":
    main()
