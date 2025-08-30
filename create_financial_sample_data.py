#!/usr/bin/env python3
"""
Financial Services Sample Data Creation
Creates sample loan applications and financial data for testing
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from financial.models import LoanApplication, Investment, FinancialStats
from authentication.models import UserRole

User = get_user_model()


def print_section(title, color="36"):
    """Print a colored section header"""
    print(f"\n\033[{color}m{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\033[0m")


def create_financial_partner_user():
    """Create a financial partner user for testing"""
    print_section("Creating Financial Partner User")
    
    try:
        # Get or create financial partner role
        financial_role, created = UserRole.objects.get_or_create(
            name='FINANCIAL_PARTNER',
            defaults={'description': 'Financial Partner with loan management capabilities'}
        )
        
        if created:
            print("✅ Created FINANCIAL_PARTNER role")
        else:
            print("📋 FINANCIAL_PARTNER role already exists")
        
        # Create financial partner user
        financial_partner, created = User.objects.get_or_create(
            username='financial_partner_demo',
            defaults={
                'email': 'financial@agriconnect.gh',
                'first_name': 'First Atlantic',
                'last_name': 'Bank',
                'phone_number': '+233200000001',
                'country': 'GH',
                'is_verified': True,
                'email_verified': True,
                'phone_verified': True,
            }
        )
        
        if created:
            financial_partner.set_password('demo123')
            financial_partner.save()
            print("✅ Created financial partner user")
        else:
            print("📋 Financial partner user already exists")
        
        # Add role to user
        financial_partner.roles.add(financial_role)
        
        return financial_partner
        
    except Exception as e:
        print(f"❌ Error creating financial partner user: {e}")
        return None


def create_farmer_users():
    """Create farmer users for loan applications"""
    print_section("Creating Farmer Users")
    
    farmers = []
    
    try:
        # Get or create farmer role
        farmer_role, created = UserRole.objects.get_or_create(
            name='FARMER',
            defaults={'description': 'Farmer with agricultural operations'}
        )
        
        if created:
            print("✅ Created FARMER role")
        
        # Create sample farmers
        farmer_data = [
            {
                'username': 'farmer_kwame',
                'email': 'kwame@farmer.gh',
                'first_name': 'Kwame',
                'last_name': 'Asante',
                'phone_number': '+233240000001',
            },
            {
                'username': 'farmer_ama',
                'email': 'ama@farmer.gh',
                'first_name': 'Ama',
                'last_name': 'Osei',
                'phone_number': '+233240000002',
            },
            {
                'username': 'farmer_kofi',
                'email': 'kofi@farmer.gh',
                'first_name': 'Kofi',
                'last_name': 'Mensah',
                'phone_number': '+233240000003',
            }
        ]
        
        for data in farmer_data:
            farmer, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number'],
                    'country': 'GH',
                    'is_verified': True,
                    'email_verified': True,
                    'phone_verified': True,
                }
            )
            
            if created:
                farmer.set_password('demo123')
                farmer.save()
                print(f"✅ Created farmer: {farmer.get_full_name()}")
            else:
                print(f"📋 Farmer already exists: {farmer.get_full_name()}")
            
            farmer.roles.add(farmer_role)
            farmers.append(farmer)
        
        return farmers
        
    except Exception as e:
        print(f"❌ Error creating farmer users: {e}")
        return []


def create_sample_loan_applications(financial_partner, farmers):
    """Create sample loan applications"""
    print_section("Creating Sample Loan Applications")
    
    if not financial_partner or not farmers:
        print("❌ Missing financial partner or farmers")
        return
    
    loan_scenarios = [
        {
            'applicant': farmers[0],
            'loan_type': 'seasonal_loan',
            'amount_requested': Decimal('25000.00'),
            'purpose': 'Seasonal farming loan for tomato cultivation - 5 acres land preparation, seeds, fertilizers, and irrigation system setup',
            'status': 'pending',
            'monthly_income': Decimal('3500.00'),
            'existing_debts': Decimal('5000.00'),
        },
        {
            'applicant': farmers[1],
            'loan_type': 'equipment_financing',
            'amount_requested': Decimal('45000.00'),
            'amount_approved': Decimal('40000.00'),
            'purpose': 'Purchase of modern farming equipment including tractor, plowing tools, and harvesting machinery',
            'status': 'approved',
            'monthly_income': Decimal('4200.00'),
            'existing_debts': Decimal('8000.00'),
            'interest_rate': Decimal('12.5'),
        },
        {
            'applicant': farmers[2],
            'loan_type': 'working_capital',
            'amount_requested': Decimal('15000.00'),
            'amount_approved': Decimal('15000.00'),
            'purpose': 'Working capital for cocoa farm operations, labor costs, and transportation',
            'status': 'disbursed',
            'monthly_income': Decimal('2800.00'),
            'existing_debts': Decimal('3000.00'),
            'interest_rate': Decimal('15.0'),
        },
        {
            'applicant': farmers[0],
            'loan_type': 'harvest_advance',
            'amount_requested': Decimal('12000.00'),
            'purpose': 'Advance payment against expected harvest for immediate operational needs',
            'status': 'under_review',
            'monthly_income': Decimal('3500.00'),
            'existing_debts': Decimal('5000.00'),
        },
        {
            'applicant': farmers[1],
            'loan_type': 'microfinance',
            'amount_requested': Decimal('8000.00'),
            'amount_approved': Decimal('8000.00'),
            'purpose': 'Small-scale poultry farming expansion and feed purchase',
            'status': 'repaid',
            'monthly_income': Decimal('4200.00'),
            'existing_debts': Decimal('0.00'),
            'interest_rate': Decimal('18.0'),
        }
    ]
    
    created_loans = []
    
    for scenario in loan_scenarios:
        # Set dates based on status
        now = timezone.now()
        application_date = now - timedelta(days=30)
        
        loan_data = {
            'applicant': scenario['applicant'],
            'financial_partner': financial_partner,
            'loan_type': scenario['loan_type'],
            'amount_requested': scenario['amount_requested'],
            'purpose': scenario['purpose'],
            'status': scenario['status'],
            'monthly_income': scenario['monthly_income'],
            'existing_debts': scenario['existing_debts'],
            'application_date': application_date,
        }
        
        # Add approved amount and interest rate if loan is approved
        if 'amount_approved' in scenario:
            loan_data['amount_approved'] = scenario['amount_approved']
            loan_data['approval_date'] = application_date + timedelta(days=5)
        
        if 'interest_rate' in scenario:
            loan_data['interest_rate'] = scenario['interest_rate']
        
        # Set disbursement date for disbursed loans
        if scenario['status'] == 'disbursed':
            loan_data['disbursement_date'] = application_date + timedelta(days=7)
            loan_data['repayment_start_date'] = (application_date + timedelta(days=30)).date()
            loan_data['maturity_date'] = (application_date + timedelta(days=365)).date()
        
        try:
            loan = LoanApplication.objects.create(**loan_data)
            created_loans.append(loan)
            print(f"✅ Created loan: {loan.loan_type} - {loan.applicant.get_full_name()} - {loan.amount_requested} GHS")
            
        except Exception as e:
            print(f"❌ Error creating loan for {scenario['applicant'].get_full_name()}: {e}")
    
    print(f"\n✅ Created {len(created_loans)} loan applications")
    return created_loans


def create_sample_investments(financial_partner):
    """Create sample investments"""
    print_section("Creating Sample Investments")
    
    if not financial_partner:
        print("❌ Missing financial partner")
        return
    
    investment_scenarios = [
        {
            'investment_type': 'farmer_loan_portfolio',
            'title': 'Agricultural Loan Portfolio Q1 2025',
            'description': 'Diversified portfolio of seasonal and equipment financing loans to smallholder farmers',
            'principal_amount': Decimal('150000.00'),
            'current_value': Decimal('162000.00'),
            'expected_return_rate': Decimal('12.0'),
            'actual_return_rate': Decimal('8.0'),
            'risk_level': 'medium',
            'status': 'active',
        },
        {
            'investment_type': 'supply_chain_financing',
            'title': 'Cocoa Supply Chain Investment',
            'description': 'Investment in cocoa supply chain financing for export operations',
            'principal_amount': Decimal('200000.00'),
            'current_value': Decimal('225000.00'),
            'expected_return_rate': Decimal('15.0'),
            'actual_return_rate': Decimal('12.5'),
            'risk_level': 'low',
            'status': 'active',
        },
        {
            'investment_type': 'equipment_leasing',
            'title': 'Farm Equipment Leasing Program',
            'description': 'Leasing program for modern agricultural equipment to farmers',
            'principal_amount': Decimal('100000.00'),
            'current_value': Decimal('105000.00'),
            'expected_return_rate': Decimal('10.0'),
            'actual_return_rate': Decimal('5.0'),
            'risk_level': 'medium',
            'status': 'active',
        }
    ]
    
    created_investments = []
    
    for scenario in investment_scenarios:
        investment_date = timezone.now().date() - timedelta(days=60)
        
        investment_data = {
            'investor': financial_partner,
            'investment_date': investment_date,
            'maturity_date': investment_date + timedelta(days=365),
            **scenario
        }
        
        try:
            investment = Investment.objects.create(**investment_data)
            created_investments.append(investment)
            print(f"✅ Created investment: {investment.title} - {investment.principal_amount} GHS")
            
        except Exception as e:
            print(f"❌ Error creating investment {scenario['title']}: {e}")
    
    print(f"\n✅ Created {len(created_investments)} investments")
    return created_investments


def create_financial_stats(financial_partner):
    """Create financial statistics record"""
    print_section("Creating Financial Statistics")
    
    if not financial_partner:
        print("❌ Missing financial partner")
        return
    
    # Calculate stats from actual data
    loans = LoanApplication.objects.filter(financial_partner=financial_partner)
    investments = Investment.objects.filter(investor=financial_partner)
    
    # Current month stats
    now = timezone.now()
    month_start = now.replace(day=1).date()
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    total_loans = loans.count()
    total_loan_amount = sum(loan.amount_approved or loan.amount_requested for loan in loans)
    active_loans = loans.filter(status__in=['approved', 'disbursed'])
    
    stats_data = {
        'financial_partner': financial_partner,
        'period_type': 'monthly',
        'period_start': month_start,
        'period_end': month_end,
        'total_loans_issued': total_loans,
        'total_loan_amount': Decimal(str(total_loan_amount)),
        'active_loans_count': active_loans.count(),
        'active_loans_amount': Decimal(str(sum(loan.amount_approved or Decimal('0') for loan in active_loans))),
        'repaid_loans_count': loans.filter(status='repaid').count(),
        'repaid_loans_amount': Decimal('8000.00'),  # Sample data
        'defaulted_loans_count': 0,
        'defaulted_loans_amount': Decimal('0.00'),
        'total_investments_count': investments.count(),
        'total_investment_amount': sum(inv.principal_amount for inv in investments),
        'active_investments_value': sum(inv.current_value for inv in investments),
        'total_returns': Decimal('17000.00'),  # Sample calculated returns
        'average_loan_size': Decimal(str(total_loan_amount / total_loans)) if total_loans > 0 else Decimal('0.00'),
        'loan_approval_rate': Decimal('80.00'),  # 80% approval rate
        'average_interest_rate': Decimal('14.50'),
        'portfolio_return_rate': Decimal('8.50'),
    }
    
    try:
        stats, created = FinancialStats.objects.get_or_create(
            financial_partner=financial_partner,
            period_type='monthly',
            period_start=month_start,
            defaults=stats_data
        )
        
        if created:
            print(f"✅ Created financial stats for {financial_partner.get_full_name()}")
        else:
            print(f"📋 Financial stats already exist for {financial_partner.get_full_name()}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error creating financial stats: {e}")
        return None


def main():
    """Main function to create all sample data"""
    print_section("Financial Services Sample Data Creation", "32")
    
    try:
        # Create users
        financial_partner = create_financial_partner_user()
        farmers = create_farmer_users()
        
        if financial_partner and farmers:
            # Create financial data
            loans = create_sample_loan_applications(financial_partner, farmers)
            investments = create_sample_investments(financial_partner)
            stats = create_financial_stats(financial_partner)
            
            print_section("Sample Data Creation Complete", "32")
            print("✅ Financial services sample data created successfully!")
            print(f"   📊 Loans: {len(loans) if loans else 0}")
            print(f"   💼 Investments: {len(investments) if investments else 0}")
            print(f"   📈 Statistics: {'Created' if stats else 'Failed'}")
            
            print("\n🔑 Test Credentials:")
            print("   Financial Partner: financial_partner_demo / demo123")
            print("   Farmers: farmer_kwame, farmer_ama, farmer_kofi / demo123")
            
            print("\n🌐 Test Endpoints:")
            print("   POST /api/v1/auth/login/ - Login as financial partner")
            print("   GET /api/v1/financial/stats/overview/ - Financial overview")
            print("   GET /api/v1/financial/loans/ - Loan applications")
            
        else:
            print("❌ Failed to create required users")
            
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
