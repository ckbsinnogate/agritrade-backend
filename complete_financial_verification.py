#!/usr/bin/env python3
"""
Financial Services Complete Verification Script
Professional testing and validation of all financial endpoints
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
from financial.models import LoanApplication, Investment, FinancialStats, LoanRepayment

User = get_user_model()

def print_header(title, color="36"):
    """Print formatted header"""
    print(f"\n\033[{color}m{'='*80}\033[0m")
    print(f"\033[{color}m{title.center(80)}\033[0m")
    print(f"\033[{color}m{'='*80}\033[0m")

def create_complete_test_data():
    """Create comprehensive test data for financial services"""
    
    print_header("📊 CREATING COMPREHENSIVE FINANCIAL TEST DATA", "33")
    
    try:
        # Ensure roles exist
        financial_role, _ = UserRole.objects.get_or_create(
            name='FINANCIAL_PARTNER',
            defaults={'description': 'Financial institution partner'}
        )
        farmer_role, _ = UserRole.objects.get_or_create(
            name='FARMER', 
            defaults={'description': 'Agricultural farmer'}
        )
        
        print("✅ User roles verified")
        
        # Create financial partner user (the one from the logs)
        financial_partner, created = User.objects.get_or_create(
            username='fab1@gmail.com',
            defaults={
                'email': 'fab1@gmail.com',
                'first_name': 'First Atlantic',
                'last_name': 'Bank',
                'is_active': True,
                'is_verified': True,
                'email_verified': True,
                'phone_verified': True
            }
        )
        
        if created or not financial_partner.check_password('password123'):
            financial_partner.set_password('password123')
            financial_partner.save()
        
        financial_partner.roles.add(financial_role)
        print(f"✅ Financial Partner: {financial_partner.get_full_name()}")
        
        # Create farmer users
        farmer_data = [
            {
                'username': 'john.farmer@agriconnect.com',
                'email': 'john.farmer@agriconnect.com', 
                'first_name': 'John',
                'last_name': 'Osei',
                'phone_number': '+233241234567'
            },
            {
                'username': 'mary.grower@agriconnect.com',
                'email': 'mary.grower@agriconnect.com',
                'first_name': 'Mary',
                'last_name': 'Asante', 
                'phone_number': '+233242345678'
            },
            {
                'username': 'kwame.cocoa@agriconnect.com',
                'email': 'kwame.cocoa@agriconnect.com',
                'first_name': 'Kwame',
                'last_name': 'Nkrumah',
                'phone_number': '+233243456789'
            }
        ]
        
        farmers = []
        for data in farmer_data:
            farmer, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'], 
                    'last_name': data['last_name'],
                    'phone_number': data.get('phone_number', ''),
                    'is_active': True,
                    'is_verified': True,
                    'email_verified': True,
                    'phone_verified': True,
                    'country': 'GH',
                    'language': 'en'
                }
            )
            
            if created or not farmer.check_password('password123'):
                farmer.set_password('password123')
                farmer.save()
            
            farmer.roles.add(farmer_role)
            farmers.append(farmer)
        
        print(f"✅ Created {len(farmers)} farmer users")
        
        # Create diverse loan applications
        loan_scenarios = [
            {
                'applicant': farmers[0],
                'loan_type': 'seasonal_loan',
                'amount_requested': Decimal('25000.00'),
                'amount_approved': Decimal('22500.00'),
                'interest_rate': Decimal('15.5'),
                'term_months': 12,
                'status': 'approved',
                'purpose': 'Seasonal tomato farming - 5 acres cultivation with improved seeds and fertilizers',
                'monthly_income': Decimal('8000.00'),
                'existing_debts': Decimal('3000.00'),
                'credit_score': 720
            },
            {
                'applicant': farmers[1], 
                'loan_type': 'equipment_financing',
                'amount_requested': Decimal('45000.00'),
                'amount_approved': Decimal('40000.00'),
                'interest_rate': Decimal('18.0'),
                'term_months': 24,
                'status': 'disbursed',
                'purpose': 'Purchase of John Deere tractor and farming equipment for mechanized agriculture',
                'monthly_income': Decimal('12000.00'),
                'existing_debts': Decimal('5000.00'),
                'credit_score': 780
            },
            {
                'applicant': farmers[2],
                'loan_type': 'harvest_advance', 
                'amount_requested': Decimal('15000.00'),
                'amount_approved': Decimal('15000.00'),
                'interest_rate': Decimal('12.0'),
                'term_months': 6,
                'status': 'repaid',
                'purpose': 'Advance against cocoa harvest - 2 hectares plantation',
                'monthly_income': Decimal('6000.00'),
                'existing_debts': Decimal('1000.00'),
                'credit_score': 650
            },
            {
                'applicant': farmers[0],
                'loan_type': 'working_capital',
                'amount_requested': Decimal('8000.00'),
                'amount_approved': None,
                'interest_rate': Decimal('16.0'),
                'term_months': 8,
                'status': 'pending',
                'purpose': 'Working capital for vegetable farming inputs and labor costs',
                'monthly_income': Decimal('8000.00'),
                'existing_debts': Decimal('3000.00'),
                'credit_score': 720
            },
            {
                'applicant': farmers[1],
                'loan_type': 'microfinance',
                'amount_requested': Decimal('5000.00'),
                'amount_approved': None,
                'interest_rate': Decimal('20.0'),
                'term_months': 6,
                'status': 'under_review',
                'purpose': 'Small-scale poultry farming startup capital',
                'monthly_income': Decimal('12000.00'),
                'existing_debts': Decimal('5000.00'),
                'credit_score': 780
            }
        ]
        
        created_loans = []
        for scenario in loan_scenarios:
            loan, created = LoanApplication.objects.get_or_create(
                applicant=scenario['applicant'],
                financial_partner=financial_partner,
                loan_type=scenario['loan_type'],
                amount_requested=scenario['amount_requested'],
                defaults={
                    'amount_approved': scenario['amount_approved'],
                    'interest_rate': scenario['interest_rate'],
                    'term_months': scenario['term_months'],
                    'status': scenario['status'],
                    'purpose': scenario['purpose'],
                    'monthly_income': scenario['monthly_income'],
                    'existing_debts': scenario['existing_debts'],
                    'credit_score': scenario['credit_score'],
                    'business_plan': f"Detailed business plan for {scenario['purpose'].lower()}",
                    'collateral_description': 'Land title and farming equipment',
                    'approval_date': timezone.now() - timedelta(days=10) if scenario['status'] in ['approved', 'disbursed', 'repaid'] else None,
                    'disbursement_date': timezone.now() - timedelta(days=5) if scenario['status'] in ['disbursed', 'repaid'] else None,
                    'repayment_start_date': (timezone.now() - timedelta(days=5)).date() if scenario['status'] in ['disbursed', 'repaid'] else None,
                    'maturity_date': (timezone.now() + timedelta(days=scenario['term_months'] * 30 - 5)).date() if scenario['status'] in ['disbursed', 'repaid'] else None
                }
            )
            
            if created:
                created_loans.append(loan)
                print(f"   💰 {loan.applicant.get_full_name()} - {loan.get_loan_type_display()} - {loan.get_status_display()}")
        
        print(f"✅ Created {len(created_loans)} loan applications")
        
        # Create loan repayments for disbursed/repaid loans
        disbursed_loans = LoanApplication.objects.filter(
            financial_partner=financial_partner,
            status__in=['disbursed', 'repaid']
        )
        
        repayments_created = 0
        for loan in disbursed_loans:
            if loan.repayment_start_date and loan.maturity_date:
                # Create monthly repayments
                monthly_payment = loan.amount_approved / loan.term_months
                current_date = loan.repayment_start_date
                
                for month in range(loan.term_months):
                    due_date = current_date + timedelta(days=30 * month)
                    
                    # Determine repayment status
                    if loan.status == 'repaid':
                        repay_status = 'paid'
                        amount_paid = monthly_payment
                        payment_date = due_date + timedelta(days=2)  # Paid 2 days after due
                    elif due_date < timezone.now().date():
                        repay_status = 'paid'
                        amount_paid = monthly_payment
                        payment_date = due_date + timedelta(days=1)
                    else:
                        repay_status = 'scheduled'
                        amount_paid = Decimal('0.00')
                        payment_date = None
                    
                    repayment, created = LoanRepayment.objects.get_or_create(
                        loan_application=loan,
                        due_date=due_date,
                        defaults={
                            'amount_due': monthly_payment,
                            'amount_paid': amount_paid,
                            'payment_date': payment_date,
                            'status': repay_status,
                            'transaction_reference': f"PAY-{loan.id.hex[:8]}-{month+1:02d}" if repay_status == 'paid' else '',
                            'payment_method': 'mobile_money' if repay_status == 'paid' else ''
                        }
                    )
                    
                    if created:
                        repayments_created += 1
        
        print(f"✅ Created {repayments_created} loan repayments")
        
        # Create investment portfolio
        investment_data = [
            {
                'title': 'Northern Region Agricultural Equipment Leasing',
                'investment_type': 'equipment_leasing',
                'principal_amount': Decimal('150000.00'),
                'current_value': Decimal('165000.00'),
                'expected_return_rate': Decimal('12.0'),
                'actual_return_rate': Decimal('10.8'),
                'risk_level': 'low'
            },
            {
                'title': 'Smallholder Farmer Loan Portfolio - Ashanti',
                'investment_type': 'farmer_loan_portfolio', 
                'principal_amount': Decimal('300000.00'),
                'current_value': Decimal('335000.00'),
                'expected_return_rate': Decimal('18.0'),
                'actual_return_rate': Decimal('16.5'),
                'risk_level': 'medium'
            },
            {
                'title': 'Cocoa Supply Chain Financing Program',
                'investment_type': 'supply_chain_financing',
                'principal_amount': Decimal('500000.00'),
                'current_value': Decimal('545000.00'),
                'expected_return_rate': Decimal('15.0'),
                'actual_return_rate': Decimal('14.2'),
                'risk_level': 'medium'
            },
            {
                'title': 'Agricultural Commodity Trading - Maize',
                'investment_type': 'commodity_trading',
                'principal_amount': Decimal('200000.00'),
                'current_value': Decimal('210000.00'),
                'expected_return_rate': Decimal('20.0'),
                'actual_return_rate': Decimal('18.5'),
                'risk_level': 'high'
            }
        ]
        
        created_investments = []
        for data in investment_data:
            investment, created = Investment.objects.get_or_create(
                investor=financial_partner,
                title=data['title'],
                defaults={
                    'investment_type': data['investment_type'],
                    'description': f"Strategic investment in {data['title'].lower()} for agricultural sector development",
                    'principal_amount': data['principal_amount'],
                    'current_value': data['current_value'],
                    'expected_return_rate': data['expected_return_rate'],
                    'actual_return_rate': data['actual_return_rate'],
                    'investment_date': timezone.now().date() - timedelta(days=60),
                    'maturity_date': timezone.now().date() + timedelta(days=300),
                    'status': 'active',
                    'risk_level': data['risk_level']
                }
            )
            
            if created:
                created_investments.append(investment)
                print(f"   📈 {investment.title} - GHS {investment.principal_amount:,.2f}")
        
        print(f"✅ Created {len(created_investments)} investments")
        
        # Create financial stats record
        stats, created = FinancialStats.objects.get_or_create(
            financial_partner=financial_partner,
            period_type='monthly',
            period_start=timezone.now().date().replace(day=1),
            defaults={
                'period_end': (timezone.now().date().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
                'total_loans_issued': LoanApplication.objects.filter(financial_partner=financial_partner, status__in=['approved', 'disbursed', 'repaid']).count(),
                'total_loan_amount': LoanApplication.objects.filter(financial_partner=financial_partner, status__in=['approved', 'disbursed', 'repaid']).aggregate(total=Sum('amount_approved'))['total'] or Decimal('0.00'),
                'active_loans_count': LoanApplication.objects.filter(financial_partner=financial_partner, status__in=['approved', 'disbursed']).count(),
                'active_loans_amount': LoanApplication.objects.filter(financial_partner=financial_partner, status__in=['approved', 'disbursed']).aggregate(total=Sum('amount_approved'))['total'] or Decimal('0.00'),
                'total_investments_count': Investment.objects.filter(investor=financial_partner).count(),
                'total_investment_amount': Investment.objects.filter(investor=financial_partner).aggregate(total=Sum('principal_amount'))['total'] or Decimal('0.00'),
                'active_investments_value': Investment.objects.filter(investor=financial_partner, status='active').aggregate(total=Sum('current_value'))['total'] or Decimal('0.00'),
                'loan_approval_rate': Decimal('80.0'),
                'average_loan_size': Decimal('25500.00'),
                'portfolio_return_rate': Decimal('15.2')
            }
        )
        
        if created:
            print("✅ Created financial statistics record")
        
        print_header("📊 FINANCIAL DATA CREATION SUMMARY", "32")
        print(f"👥 Users: {User.objects.count()} total")
        print(f"🏦 Financial Partners: {User.objects.filter(roles__name='FINANCIAL_PARTNER').count()}")
        print(f"🚜 Farmers: {User.objects.filter(roles__name='FARMER').count()}")
        print(f"💰 Loan Applications: {LoanApplication.objects.count()}")
        print(f"💳 Loan Repayments: {LoanRepayment.objects.count()}")
        print(f"📈 Investments: {Investment.objects.count()}")
        print(f"📊 Financial Stats: {FinancialStats.objects.count()}")
        
        return financial_partner
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_authentication():
    """Test authentication and get token"""
    
    print_header("🔐 TESTING AUTHENTICATION", "35")
    
    try:
        # Test login
        login_data = {
            "identifier": "fab1@gmail.com",
            "password": "password123"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            refresh_token = token_data.get('refresh')
            
            print("✅ Authentication successful")
            print(f"   🔑 Access token received: {access_token[:20]}...")
            print(f"   🔄 Refresh token received: {refresh_token[:20]}...")
            
            return access_token, refresh_token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def test_financial_endpoints(access_token):
    """Test all financial endpoints with authentication"""
    
    print_header("🏦 TESTING FINANCIAL ENDPOINTS", "36")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    base_url = "http://127.0.0.1:8000/api/v1/financial"
    
    # Test endpoints
    endpoints = [
        ('Financial Stats Overview', f'{base_url}/stats/overview/'),
        ('Loan Applications', f'{base_url}/loans/'),
        ('Investments', f'{base_url}/investments/'),
        ('Loan Repayments', f'{base_url}/repayments/'),
        ('Financial Statistics', f'{base_url}/stats/')
    ]
    
    results = {}
    
    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results[name] = 'SUCCESS'
                
                if name == 'Financial Stats Overview':
                    if 'data' in data:
                        overview = data['data']
                        print(f"✅ {name}: Working")
                        print(f"   💰 Total Loans: {overview.get('total_loans_issued', 0)}")
                        loan_amount = overview.get('total_loan_amount', '0')
                        print(f"   💵 Loan Amount: GHS {loan_amount}")
                        print(f"   📈 Investments: {overview.get('total_investments', 0)}")
                        portfolio_performance = overview.get('portfolio_performance', '0')
                        print(f"   📊 Portfolio Performance: {portfolio_performance}%")
                    else:
                        print(f"✅ {name}: Working (no data)")
                        
                elif name == 'Loan Applications':
                    if 'results' in data:
                        loans = data['results']
                        print(f"✅ {name}: Working")
                        print(f"   📋 Found {len(loans)} loan applications")
                        for loan in loans[:3]:
                            print(f"   • {loan.get('applicant_name')} - {loan.get('status_display')}")
                    else:
                        print(f"✅ {name}: Working (no results)")
                          elif name == 'Investments':
                    if 'results' in data:
                        investments = data['results']
                        print(f"✅ {name}: Working")
                        print(f"   📈 Found {len(investments)} investments")
                        for inv in investments[:2]:
                            current_value = inv.get('current_value', '0')
                            print(f"   • {inv.get('title')} - GHS {current_value}")
                    else:
                        print(f"✅ {name}: Working (no results)")
                        
                else:
                    print(f"✅ {name}: Working")
                    
            else:
                results[name] = f'FAILED ({response.status_code})'
                print(f"❌ {name}: Failed with status {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            results[name] = f'ERROR ({str(e)})'
            print(f"❌ {name}: Error - {e}")
    
    return results

def test_logout(access_token, refresh_token):
    """Test logout functionality"""
    
    print_header("🚪 TESTING LOGOUT", "33")
    
    try:
        logout_data = {
            "refresh": refresh_token
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/logout/",
            json=logout_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Logout successful")
            print(f"   Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Logout failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return False

def main():
    """Main verification function"""
    
    print_header("🚀 AGRICONNECT FINANCIAL SERVICES VERIFICATION", "32")
    print("Professional end-to-end testing of financial endpoints")
    
    # Create test data
    financial_partner = create_complete_test_data()
    if not financial_partner:
        print("❌ Failed to create test data. Exiting.")
        return
    
    # Test authentication
    access_token, refresh_token = test_authentication()
    if not access_token:
        print("❌ Authentication failed. Exiting.")
        return
    
    # Test financial endpoints
    results = test_financial_endpoints(access_token)
    
    # Test logout
    logout_success = test_logout(access_token, refresh_token)
    
    # Summary
    print_header("📋 VERIFICATION RESULTS SUMMARY", "32")
    
    success_count = sum(1 for result in results.values() if result == 'SUCCESS')
    total_count = len(results)
    
    print(f"✅ Endpoint Tests: {success_count}/{total_count} passed")
    print(f"✅ Authentication: {'WORKING' if access_token else 'FAILED'}")
    print(f"✅ Logout: {'WORKING' if logout_success else 'FAILED'}")
    
    for endpoint, result in results.items():
        status_icon = "✅" if result == 'SUCCESS' else "❌"
        print(f"{status_icon} {endpoint}: {result}")
    
    if success_count == total_count and access_token and logout_success:
        print_header("🎉 ALL TESTS PASSED - PROFESSIONAL IMPLEMENTATION", "32")
        print("Financial services are ready for production!")
        print("\n📋 Frontend Integration Points:")
        print("• POST /api/v1/auth/login/ - Authentication")
        print("• GET /api/v1/financial/stats/overview/ - Dashboard statistics")
        print("• GET /api/v1/financial/loans/ - Loan applications management")
        print("• GET /api/v1/financial/investments/ - Investment portfolio")
        print("• POST /api/v1/auth/logout/ - Secure logout")
    else:
        print_header("⚠️  SOME ISSUES DETECTED", "31")
        print("Please review the failed tests above.")

if __name__ == "__main__":
    # Import missing module
    from django.db.models import Sum
    main()
