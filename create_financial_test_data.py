#!/usr/bin/env python3
"""
Create Financial Test Data Script
Creates sample users and financial data for testing the financial endpoints
"""

import os
import sys
import django
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

def create_test_data():
    """Create comprehensive test data for financial services"""
    
    print("🏦 Creating Financial Test Data...")
    print("=" * 50)
    
    # Create or get roles
    financial_role, created = UserRole.objects.get_or_create(
        name='FINANCIAL_PARTNER',
        defaults={'description': 'Financial institution partner'}
    )
    farmer_role, created = UserRole.objects.get_or_create(
        name='FARMER',
        defaults={'description': 'Agricultural farmer'}
    )
    
    print(f"✅ Roles configured: FINANCIAL_PARTNER, FARMER")
    
    # Create financial partner user (matching the one from logs)
    financial_partner, created = User.objects.get_or_create(
        username='fab1@gmail.com',
        defaults={
            'email': 'fab1@gmail.com',
            'first_name': 'First Atlantic',
            'last_name': 'Bank',
            'is_active': True,
            'is_verified': True,
            'email_verified': True
        }
    )
    
    if created:
        financial_partner.set_password('password123')
        financial_partner.save()
    
    financial_partner.roles.add(financial_role)
    print(f"✅ Financial Partner Created: {financial_partner.get_full_name()}")
    
    # Create farmer users
    farmers_data = [
        {'username': 'farmer1@test.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'farmer2@test.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'farmer3@test.com', 'first_name': 'Michael', 'last_name': 'Johnson'},
    ]
    
    farmers = []
    for data in farmers_data:
        farmer, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['username'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'is_active': True,
                'is_verified': True,
                'email_verified': True
            }
        )
        
        if created:
            farmer.set_password('password123')
            farmer.save()
        
        farmer.roles.add(farmer_role)
        farmers.append(farmer)
    
    print(f"✅ Created {len(farmers)} farmers")
    
    # Create diverse loan applications
    loan_data = [
        {
            'farmer': farmers[0],
            'loan_type': 'seasonal_loan',
            'amount_requested': Decimal('25000.00'),
            'amount_approved': Decimal('22500.00'),
            'interest_rate': Decimal('15.5'),
            'status': 'approved',
            'purpose': 'Seasonal tomato farming - purchase of seeds, fertilizers, and irrigation equipment',
            'monthly_income': Decimal('8000.00'),
            'existing_debts': Decimal('5000.00'),
            'credit_score': 750
        },
        {
            'farmer': farmers[1],
            'loan_type': 'equipment_financing',
            'amount_requested': Decimal('45000.00'),
            'amount_approved': Decimal('40000.00'),
            'interest_rate': Decimal('12.0'),
            'status': 'disbursed',
            'purpose': 'Purchase of modern tractor and farming equipment for increased productivity',
            'monthly_income': Decimal('12000.00'),
            'existing_debts': Decimal('8000.00'),
            'credit_score': 680
        },
        {
            'farmer': farmers[2],
            'loan_type': 'harvest_advance',
            'amount_requested': Decimal('15000.00'),
            'amount_approved': None,
            'interest_rate': Decimal('18.0'),
            'status': 'pending',
            'purpose': 'Advance against expected cocoa harvest for immediate cash flow needs',
            'monthly_income': Decimal('6000.00'),
            'existing_debts': Decimal('2000.00'),
            'credit_score': 620
        },
        {
            'farmer': farmers[0],
            'loan_type': 'working_capital',
            'amount_requested': Decimal('35000.00'),
            'amount_approved': None,
            'interest_rate': Decimal('16.5'),
            'status': 'under_review',
            'purpose': 'Working capital for expanding vegetable farming operations',
            'monthly_income': Decimal('8000.00'),
            'existing_debts': Decimal('5000.00'),
            'credit_score': 750
        },
        {
            'farmer': farmers[1],
            'loan_type': 'microfinance',
            'amount_requested': Decimal('8000.00'),
            'amount_approved': Decimal('7500.00'),
            'interest_rate': Decimal('20.0'),
            'status': 'repaid',
            'purpose': 'Small-scale poultry farming startup capital',
            'monthly_income': Decimal('12000.00'),
            'existing_debts': Decimal('8000.00'),
            'credit_score': 680
        }
    ]
    
    created_loans = []
    for loan_info in loan_data:
        loan, created = LoanApplication.objects.get_or_create(
            applicant=loan_info['farmer'],
            financial_partner=financial_partner,
            loan_type=loan_info['loan_type'],
            amount_requested=loan_info['amount_requested'],
            defaults={
                'amount_approved': loan_info['amount_approved'],
                'interest_rate': loan_info['interest_rate'],
                'term_months': 12,
                'status': loan_info['status'],
                'purpose': loan_info['purpose'],
                'monthly_income': loan_info['monthly_income'],
                'existing_debts': loan_info['existing_debts'],
                'credit_score': loan_info['credit_score'],
                'approval_date': timezone.now() - timedelta(days=10) if loan_info['status'] in ['approved', 'disbursed', 'repaid'] else None,
                'disbursement_date': timezone.now() - timedelta(days=5) if loan_info['status'] in ['disbursed', 'repaid'] else None
            }
        )
        
        if created:
            created_loans.append(loan)
    
    print(f"✅ Created {len(created_loans)} loan applications with various statuses")
    
    # Create investment portfolio
    investment_data = [
        {
            'title': 'Northern Ghana Farmer Loan Portfolio',
            'investment_type': 'farmer_loan_portfolio',
            'principal_amount': Decimal('500000.00'),
            'current_value': Decimal('547500.00'),
            'expected_return_rate': Decimal('15.0'),
            'actual_return_rate': Decimal('13.2'),
            'risk_level': 'medium'
        },
        {
            'title': 'Agricultural Equipment Leasing Program',
            'investment_type': 'equipment_leasing',
            'principal_amount': Decimal('300000.00'),
            'current_value': Decimal('325000.00'),
            'expected_return_rate': Decimal('12.0'),
            'actual_return_rate': Decimal('11.8'),
            'risk_level': 'low'
        },
        {
            'title': 'Cocoa Supply Chain Financing',
            'investment_type': 'supply_chain_financing',
            'principal_amount': Decimal('750000.00'),
            'current_value': Decimal('820000.00'),
            'expected_return_rate': Decimal('18.0'),
            'actual_return_rate': Decimal('16.5'),
            'risk_level': 'high'
        },
        {
            'title': 'Crop Insurance Syndicate',
            'investment_type': 'crop_insurance',
            'principal_amount': Decimal('200000.00'),
            'current_value': Decimal('210000.00'),
            'expected_return_rate': Decimal('8.0'),
            'actual_return_rate': Decimal('7.5'),
            'risk_level': 'low'
        }
    ]
    
    created_investments = []
    for inv_info in investment_data:
        investment, created = Investment.objects.get_or_create(
            investor=financial_partner,
            title=inv_info['title'],
            defaults={
                'investment_type': inv_info['investment_type'],
                'description': f"Strategic investment in {inv_info['title'].lower()} to support agricultural development",
                'principal_amount': inv_info['principal_amount'],
                'current_value': inv_info['current_value'],
                'expected_return_rate': inv_info['expected_return_rate'],
                'actual_return_rate': inv_info['actual_return_rate'],
                'investment_date': timezone.now().date() - timedelta(days=90),
                'maturity_date': timezone.now().date() + timedelta(days=275),
                'status': 'active',
                'risk_level': inv_info['risk_level']
            }
        )
        
        if created:
            created_investments.append(investment)
    
    print(f"✅ Created {len(created_investments)} investments")
    
    # Display summary statistics
    print("\n📊 FINANCIAL DATA SUMMARY")
    print("=" * 50)
    
    # Loan statistics
    total_loans = LoanApplication.objects.filter(financial_partner=financial_partner).count()
    pending_loans = LoanApplication.objects.filter(financial_partner=financial_partner, status__in=['pending', 'under_review']).count()
    active_loans = LoanApplication.objects.filter(financial_partner=financial_partner, status__in=['approved', 'disbursed']).count()
    total_loan_amount = LoanApplication.objects.filter(
        financial_partner=financial_partner, 
        status__in=['approved', 'disbursed', 'repaid']
    ).aggregate(total=models.Sum('amount_approved'))['total'] or Decimal('0.00')
    
    print(f"💰 Loans Overview:")
    print(f"   • Total Applications: {total_loans}")
    print(f"   • Pending Review: {pending_loans}")
    print(f"   • Active Loans: {active_loans}")
    print(f"   • Total Amount: GHS {total_loan_amount:,.2f}")
    
    # Investment statistics
    total_investments = Investment.objects.filter(investor=financial_partner).count()
    total_investment_value = Investment.objects.filter(investor=financial_partner).aggregate(
        total=models.Sum('current_value')
    )['total'] or Decimal('0.00')
    total_principal = Investment.objects.filter(investor=financial_partner).aggregate(
        total=models.Sum('principal_amount')
    )['total'] or Decimal('0.00')
    
    portfolio_return = ((total_investment_value - total_principal) / total_principal * 100) if total_principal > 0 else Decimal('0.00')
    
    print(f"\n📈 Investment Portfolio:")
    print(f"   • Total Investments: {total_investments}")
    print(f"   • Portfolio Value: GHS {total_investment_value:,.2f}")
    print(f"   • Portfolio Return: {portfolio_return:.2f}%")
    
    print(f"\n👥 Users Created:")
    print(f"   • Financial Partners: {User.objects.filter(roles__name='FINANCIAL_PARTNER').count()}")
    print(f"   • Farmers: {User.objects.filter(roles__name='FARMER').count()}")
    
    print(f"\n🔐 Test Credentials:")
    print(f"   • Financial Partner: fab1@gmail.com / password123")
    print(f"   • Farmer 1: farmer1@test.com / password123")
    print(f"   • Farmer 2: farmer2@test.com / password123")
    
    print(f"\n✅ Financial test data creation completed!")
    return True

if __name__ == "__main__":
    from django.db import models
    create_test_data()
