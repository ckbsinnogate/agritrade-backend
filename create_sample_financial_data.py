#!/usr/bin/env python3
"""
Create Sample Financial Data
Populates the financial app with sample loan applications and investments
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta, date
from django.utils import timezone

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

django.setup()

from django.contrib.auth import get_user_model
from authentication.models import UserRole
from financial.models import LoanApplication, Investment, FinancialStats, LoanRepayment

User = get_user_model()


def create_sample_financial_data():
    """Create sample financial data for testing"""
    
    print("🏦 CREATING SAMPLE FINANCIAL DATA")
    print("=" * 50)
    
    # Get or create financial partner
    financial_partner_role, _ = UserRole.objects.get_or_create(name='FINANCIAL_PARTNER')
    farmer_role, _ = UserRole.objects.get_or_create(name='FARMER')
    
    # Create financial partner user
    financial_partner, created = User.objects.get_or_create(
        username='fab1@gmail.com',
        defaults={
            'email': 'fab1@gmail.com',
            'first_name': 'First Atlantic',
            'last_name': 'Bank',
            'is_verified': True,
            'email_verified': True,
        }
    )
    financial_partner.roles.add(financial_partner_role)
    
    if created:
        print(f"✅ Created financial partner: {financial_partner.get_full_name()}")
    else:
        print(f"📋 Using existing financial partner: {financial_partner.get_full_name()}")
    
    # Create or get sample farmers
    farmers_data = [
        {
            'username': 'farmer1@test.com',
            'email': 'farmer1@test.com',
            'first_name': 'John',
            'last_name': 'Farmer',
        },
        {
            'username': 'farmer2@test.com',
            'email': 'farmer2@test.com',
            'first_name': 'Mary',
            'last_name': 'Grower',
        },
        {
            'username': 'farmer3@test.com',
            'email': 'farmer3@test.com',
            'first_name': 'David',
            'last_name': 'Cultivator',
        }
    ]
    
    farmers = []
    for farmer_data in farmers_data:
        farmer, created = User.objects.get_or_create(
            username=farmer_data['username'],
            defaults={
                'email': farmer_data['email'],
                'first_name': farmer_data['first_name'],
                'last_name': farmer_data['last_name'],
                'is_verified': True,
                'email_verified': True,
            }
        )
        farmer.roles.add(farmer_role)
        farmers.append(farmer)
        
        if created:
            print(f"✅ Created farmer: {farmer.get_full_name()}")
    
    print(f"📊 Total farmers: {len(farmers)}")
    
    # Create sample loan applications
    print("\n💰 CREATING SAMPLE LOAN APPLICATIONS")
    print("-" * 40)
    
    loan_applications_data = [
        {
            'applicant': farmers[0],
            'loan_type': 'seasonal_loan',
            'amount_requested': Decimal('25000.00'),
            'amount_approved': Decimal('20000.00'),
            'interest_rate': Decimal('12.50'),
            'term_months': 12,
            'status': 'approved',
            'purpose': 'Seasonal financing for tomato cultivation, including seeds, fertilizers, and labor costs',
            'monthly_income': Decimal('8500.00'),
            'existing_debts': Decimal('5000.00'),
            'credit_score': 720,
        },
        {
            'applicant': farmers[1],
            'loan_type': 'equipment_financing',
            'amount_requested': Decimal('45000.00'),
            'amount_approved': Decimal('40000.00'),
            'interest_rate': Decimal('15.00'),
            'term_months': 24,
            'status': 'disbursed',
            'purpose': 'Purchase of modern farming equipment including tractor and irrigation system',
            'monthly_income': Decimal('12000.00'),
            'existing_debts': Decimal('8000.00'),
            'credit_score': 680,
        },
        {
            'applicant': farmers[2],
            'loan_type': 'working_capital',
            'amount_requested': Decimal('15000.00'),
            'status': 'pending',
            'purpose': 'Working capital for expanding vegetable farming operations',
            'monthly_income': Decimal('6500.00'),
            'existing_debts': Decimal('2000.00'),
            'credit_score': 650,
        },
        {
            'applicant': farmers[0],
            'loan_type': 'harvest_advance',
            'amount_requested': Decimal('18000.00'),
            'status': 'under_review',
            'purpose': 'Advance payment for expected cocoa harvest to cover immediate expenses',
            'monthly_income': Decimal('8500.00'),
            'existing_debts': Decimal('5000.00'),
        },
        {
            'applicant': farmers[1],
            'loan_type': 'microfinance',
            'amount_requested': Decimal('8000.00'),
            'amount_approved': Decimal('7500.00'),
            'interest_rate': Decimal('18.00'),
            'term_months': 6,
            'status': 'repaid',
            'purpose': 'Small-scale poultry farming startup capital',
            'monthly_income': Decimal('12000.00'),
            'existing_debts': Decimal('8000.00'),
        }
    ]
    
    created_loans = []
    for loan_data in loan_applications_data:
        # Calculate dates based on status
        now = timezone.now()
        application_date = now - timedelta(days=30)
        
        loan = LoanApplication.objects.create(
            applicant=loan_data['applicant'],
            financial_partner=financial_partner,
            loan_type=loan_data['loan_type'],
            amount_requested=loan_data['amount_requested'],
            amount_approved=loan_data.get('amount_approved'),
            interest_rate=loan_data.get('interest_rate', Decimal('15.00')),
            term_months=loan_data.get('term_months', 12),
            status=loan_data['status'],
            purpose=loan_data['purpose'],
            monthly_income=loan_data.get('monthly_income'),
            existing_debts=loan_data.get('existing_debts', Decimal('0.00')),
            credit_score=loan_data.get('credit_score'),
            application_date=application_date,
            approval_date=now - timedelta(days=20) if loan_data['status'] in ['approved', 'disbursed', 'repaid'] else None,
            disbursement_date=now - timedelta(days=15) if loan_data['status'] in ['disbursed', 'repaid'] else None,
        )
        created_loans.append(loan)
        print(f"✅ Created {loan.get_status_display()} loan: {loan.get_loan_type_display()} - {loan.amount_requested} GHS")
    
    print(f"📊 Total loan applications created: {len(created_loans)}")
    
    # Create sample investments
    print("\n📈 CREATING SAMPLE INVESTMENTS")
    print("-" * 30)
    
    investments_data = [
        {
            'investment_type': 'farmer_loan_portfolio',
            'title': 'Seasonal Farming Loan Portfolio Q4 2024',
            'description': 'Portfolio of seasonal loans to small-scale farmers for crop cultivation',
            'principal_amount': Decimal('250000.00'),
            'current_value': Decimal('275000.00'),
            'expected_return_rate': Decimal('12.00'),
            'actual_return_rate': Decimal('13.50'),
            'investment_date': date.today() - timedelta(days=90),
            'status': 'active',
            'risk_level': 'medium',
        },
        {
            'investment_type': 'agricultural_project',
            'title': 'Smart Irrigation System Initiative',
            'description': 'Investment in smart irrigation technology for improved water management',
            'principal_amount': Decimal('150000.00'),
            'current_value': Decimal('160000.00'),
            'expected_return_rate': Decimal('15.00'),
            'actual_return_rate': Decimal('14.20'),
            'investment_date': date.today() - timedelta(days=120),
            'maturity_date': date.today() + timedelta(days=245),
            'status': 'active',
            'risk_level': 'high',
        },
        {
            'investment_type': 'supply_chain_financing',
            'title': 'Agricultural Supply Chain Financing',
            'description': 'Financing agricultural supply chain operations for improved efficiency',
            'principal_amount': Decimal('100000.00'),
            'current_value': Decimal('108000.00'),
            'expected_return_rate': Decimal('10.00'),
            'actual_return_rate': Decimal('11.20'),
            'investment_date': date.today() - timedelta(days=60),
            'status': 'active',
            'risk_level': 'low',
        }
    ]
    
    created_investments = []
    for inv_data in investments_data:
        investment = Investment.objects.create(
            investor=financial_partner,
            **inv_data
        )
        created_investments.append(investment)
        print(f"✅ Created investment: {investment.title} - {investment.principal_amount} GHS")
    
    print(f"📊 Total investments created: {len(created_investments)}")
    
    # Create sample financial stats
    print("\n📊 CREATING FINANCIAL STATISTICS")
    print("-" * 30)
    
    # Calculate current month stats
    today = date.today()
    month_start = today.replace(day=1)
    next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
    month_end = next_month - timedelta(days=1)
    
    # Calculate statistics
    active_loans = LoanApplication.objects.filter(
        financial_partner=financial_partner,
        status__in=['approved', 'disbursed']
    )
    
    total_loans = LoanApplication.objects.filter(financial_partner=financial_partner)
    repaid_loans = total_loans.filter(status='repaid')
    active_investments = Investment.objects.filter(investor=financial_partner, status='active')
    
    stats = FinancialStats.objects.create(
        financial_partner=financial_partner,
        period_type='monthly',
        period_start=month_start,
        period_end=month_end,
        total_loans_issued=total_loans.count(),
        total_loan_amount=sum(loan.amount_approved or loan.amount_requested for loan in total_loans),
        active_loans_count=active_loans.count(),
        active_loans_amount=sum(loan.amount_approved or loan.amount_requested for loan in active_loans),
        repaid_loans_count=repaid_loans.count(),
        repaid_loans_amount=sum(loan.amount_approved or loan.amount_requested for loan in repaid_loans),
        total_investments_count=active_investments.count(),
        total_investment_amount=sum(inv.principal_amount for inv in active_investments),
        active_investments_value=sum(inv.current_value for inv in active_investments),
        average_loan_size=Decimal('25000.00'),
        loan_approval_rate=Decimal('80.00'),
        average_interest_rate=Decimal('15.00'),
        portfolio_return_rate=Decimal('12.50'),
    )
    
    print(f"✅ Created financial statistics for {stats.period_type} period")
    
    print("\n🎉 SAMPLE FINANCIAL DATA CREATION COMPLETE!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Financial Partners: 1")
    print(f"   • Farmers: {len(farmers)}")
    print(f"   • Loan Applications: {len(created_loans)}")
    print(f"   • Investments: {len(created_investments)}")
    print(f"   • Financial Stats Records: 1")
    
    return {
        'financial_partner': financial_partner,
        'farmers': farmers,
        'loans': created_loans,
        'investments': created_investments,
        'stats': stats
    }


if __name__ == "__main__":
    try:
        result = create_sample_financial_data()
        print("\n✅ All sample financial data created successfully!")
        
    except Exception as e:
        print(f"\n❌ Error creating sample financial data: {str(e)}")
        import traceback
        traceback.print_exc()
