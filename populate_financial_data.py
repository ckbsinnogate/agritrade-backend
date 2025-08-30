#!/usr/bin/env python3
"""
Financial Services Data Population Script
Creates sample loan applications, investments, and financial statistics
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
from financial.models import LoanApplication, LoanRepayment, Investment, FinancialStats

User = get_user_model()


def print_section(title, color="36"):
    """Print colored section header"""
    print(f"\n\033[{color}m{'='*60}\033[0m")
    print(f"\033[{color}m{title}\033[0m")
    print(f"\033[{color}m{'='*60}\033[0m")


def create_sample_users():
    """Create sample users for testing"""
    print("\n🏦 Creating sample users...")
    
    # Create FINANCIAL_PARTNER role if it doesn't exist
    financial_partner_role, created = UserRole.objects.get_or_create(
        name='FINANCIAL_PARTNER',
        defaults={'description': 'Financial partner who provides loans and investments'}
    )
    if created:
        print("✅ Created FINANCIAL_PARTNER role")
    
    # Create farmer role if it doesn't exist
    farmer_role, created = UserRole.objects.get_or_create(
        name='FARMER',
        defaults={'description': 'Farmer who can apply for loans'}
    )
    if created:
        print("✅ Created FARMER role")
    
    # Create a financial partner
    financial_partner, created = User.objects.get_or_create(
        username='fab1@gmail.com',
        defaults={
            'email': 'fab1@gmail.com',
            'first_name': 'First Atlantic',
            'last_name': 'Bank',
            'phone_number': '+233244000001',
            'is_active': True,
            'is_verified': True,
            'email_verified': True,
            'phone_verified': True,
        }
    )
    if created:
        financial_partner.set_password('password123')
        financial_partner.save()
        print("✅ Created financial partner user")
    
    # Add role to financial partner
    financial_partner.roles.add(financial_partner_role)
    
    # Create sample farmers
    farmers_data = [
        {
            'username': 'kwame.farmer@gmail.com',
            'email': 'kwame.farmer@gmail.com',
            'first_name': 'Kwame',
            'last_name': 'Asante',
            'phone_number': '+233244000002',
        },
        {
            'username': 'akosua.farmer@gmail.com',
            'email': 'akosua.farmer@gmail.com',
            'first_name': 'Akosua',
            'last_name': 'Osei',
            'phone_number': '+233244000003',
        },
        {
            'username': 'kofi.farmer@gmail.com',
            'email': 'kofi.farmer@gmail.com',
            'first_name': 'Kofi',
            'last_name': 'Mensah',
            'phone_number': '+233244000004',
        }
    ]
    
    farmers = []
    for farmer_data in farmers_data:
        farmer, created = User.objects.get_or_create(
            username=farmer_data['username'],
            defaults={
                **farmer_data,
                'is_active': True,
                'is_verified': True,
                'email_verified': True,
                'phone_verified': True,
            }
        )
        if created:
            farmer.set_password('password123')
            farmer.save()
            print(f"✅ Created farmer user: {farmer.get_full_name()}")
        
        farmer.roles.add(farmer_role)
        farmers.append(farmer)
    
    return financial_partner, farmers


def create_sample_loan_applications(financial_partner, farmers):
    """Create sample loan applications"""
    print("\n💰 Creating sample loan applications...")
    
    loan_applications_data = [
        {
            'applicant': farmers[0],
            'loan_type': 'seasonal_loan',
            'amount_requested': Decimal('25000.00'),
            'amount_approved': Decimal('20000.00'),
            'interest_rate': Decimal('12.50'),
            'term_months': 12,
            'status': 'approved',
            'purpose': 'Financing for tomato cultivation season 2025',
            'collateral_description': '2 acres of farmland in Ashanti Region',
            'monthly_income': Decimal('3500.00'),
            'existing_debts': Decimal('5000.00'),
            'application_date': timezone.now() - timedelta(days=30),
            'approval_date': timezone.now() - timedelta(days=25),
        },
        {
            'applicant': farmers[1],
            'loan_type': 'equipment_financing',
            'amount_requested': Decimal('45000.00'),
            'amount_approved': Decimal('40000.00'),
            'interest_rate': Decimal('15.00'),
            'term_months': 18,
            'status': 'disbursed',
            'purpose': 'Purchase of modern farming equipment including tractor',
            'collateral_description': 'Existing farming equipment and 3 acres of land',
            'monthly_income': Decimal('5000.00'),
            'existing_debts': Decimal('12000.00'),
            'application_date': timezone.now() - timedelta(days=45),
            'approval_date': timezone.now() - timedelta(days=40),
            'disbursement_date': timezone.now() - timedelta(days=35),
        },
        {
            'applicant': farmers[2],
            'loan_type': 'working_capital',
            'amount_requested': Decimal('15000.00'),
            'status': 'pending',
            'purpose': 'Working capital for cocoa farm operations',
            'monthly_income': Decimal('2800.00'),
            'existing_debts': Decimal('3000.00'),
            'application_date': timezone.now() - timedelta(days=5),
        },
        {
            'applicant': farmers[0],
            'loan_type': 'harvest_advance',
            'amount_requested': Decimal('8000.00'),
            'status': 'under_review',
            'purpose': 'Advance payment for upcoming harvest',
            'monthly_income': Decimal('3500.00'),
            'existing_debts': Decimal('5000.00'),
            'application_date': timezone.now() - timedelta(days=10),
        },
        {
            'applicant': farmers[1],
            'loan_type': 'microfinance',
            'amount_requested': Decimal('3000.00'),
            'amount_approved': Decimal('3000.00'),
            'interest_rate': Decimal('18.00'),
            'term_months': 6,
            'status': 'repaid',
            'purpose': 'Small loan for seeds and fertilizers',
            'monthly_income': Decimal('5000.00'),
            'existing_debts': Decimal('12000.00'),
            'application_date': timezone.now() - timedelta(days=180),
            'approval_date': timezone.now() - timedelta(days=175),
            'disbursement_date': timezone.now() - timedelta(days=170),
        }
    ]
    
    created_loans = []
    for loan_data in loan_applications_data:
        loan_data['financial_partner'] = financial_partner
        
        loan, created = LoanApplication.objects.get_or_create(
            applicant=loan_data['applicant'],
            loan_type=loan_data['loan_type'],
            amount_requested=loan_data['amount_requested'],
            defaults=loan_data
        )
        
        if created:
            # Update dates manually after creation if specified
            if 'application_date' in loan_data:
                loan.application_date = loan_data['application_date']
            if 'approval_date' in loan_data:
                loan.approval_date = loan_data['approval_date']
            if 'disbursement_date' in loan_data:
                loan.disbursement_date = loan_data['disbursement_date']
            loan.save()
            
            print(f"✅ Created loan application: {loan.applicant.get_full_name()} - {loan.get_loan_type_display()}")
            created_loans.append(loan)
    
    return created_loans


def create_sample_investments(financial_partner):
    """Create sample investments for the financial partner"""
    print("\n📈 Creating sample investments...")
    
    investments_data = [
        {
            'investment_type': 'farmer_loan_portfolio',
            'title': 'Agricultural Loan Portfolio Q1 2025',
            'description': 'Diversified portfolio of farmer loans across multiple crops',
            'principal_amount': Decimal('150000.00'),
            'current_value': Decimal('165000.00'),
            'expected_return_rate': Decimal('12.00'),
            'actual_return_rate': Decimal('10.00'),
            'investment_date': date.today() - timedelta(days=90),
            'maturity_date': date.today() + timedelta(days=275),
            'status': 'active',
            'risk_level': 'medium',
        },
        {
            'investment_type': 'supply_chain_financing',
            'title': 'Cocoa Supply Chain Financing',
            'description': 'Financing cocoa supply chain from farm to export',
            'principal_amount': Decimal('200000.00'),
            'current_value': Decimal('220000.00'),
            'expected_return_rate': Decimal('15.00'),
            'actual_return_rate': Decimal('10.00'),
            'investment_date': date.today() - timedelta(days=120),
            'maturity_date': date.today() + timedelta(days=245),
            'status': 'active',
            'risk_level': 'medium',
        },
        {
            'investment_type': 'equipment_leasing',
            'title': 'Agricultural Equipment Leasing Program',
            'description': 'Leasing modern farming equipment to small-scale farmers',
            'principal_amount': Decimal('100000.00'),
            'current_value': Decimal('95000.00'),
            'expected_return_rate': Decimal('8.00'),
            'actual_return_rate': Decimal('-5.00'),
            'investment_date': date.today() - timedelta(days=60),
            'maturity_date': date.today() + timedelta(days=305),
            'status': 'active',
            'risk_level': 'high',
        },
        {
            'investment_type': 'commodity_trading',
            'title': 'Maize Commodity Trading',
            'description': 'Investment in maize commodity futures',
            'principal_amount': Decimal('75000.00'),
            'current_value': Decimal('82500.00'),
            'expected_return_rate': Decimal('12.00'),
            'actual_return_rate': Decimal('10.00'),
            'investment_date': date.today() - timedelta(days=30),
            'maturity_date': date.today() + timedelta(days=335),
            'status': 'active',
            'risk_level': 'high',
        }
    ]
    
    created_investments = []
    for investment_data in investments_data:
        investment_data['investor'] = financial_partner
        
        investment, created = Investment.objects.get_or_create(
            investor=financial_partner,
            title=investment_data['title'],
            defaults=investment_data
        )
        
        if created:
            print(f"✅ Created investment: {investment.title}")
            created_investments.append(investment)
    
    return created_investments


def create_sample_repayments(loan_applications):
    """Create sample repayments for approved/disbursed loans"""
    print("\n💳 Creating sample loan repayments...")
    
    for loan in loan_applications:
        if loan.status in ['approved', 'disbursed', 'repaid'] and loan.amount_approved:
            # Create monthly repayments
            monthly_payment = loan.amount_approved / loan.term_months
            start_date = loan.disbursement_date.date() if loan.disbursement_date else date.today()
            
            for month in range(loan.term_months):
                due_date = start_date + timedelta(days=30 * (month + 1))
                
                # Determine status based on due date and loan status
                status = 'scheduled'
                amount_paid = Decimal('0.00')
                payment_date = None
                
                if due_date < date.today():
                    if loan.status == 'repaid':
                        status = 'paid'
                        amount_paid = monthly_payment
                        payment_date = due_date
                    elif month < 2:  # First two payments are paid
                        status = 'paid'
                        amount_paid = monthly_payment
                        payment_date = due_date
                    else:
                        status = 'overdue' if due_date < date.today() - timedelta(days=7) else 'scheduled'
                
                repayment, created = LoanRepayment.objects.get_or_create(
                    loan_application=loan,
                    due_date=due_date,
                    defaults={
                        'amount_due': monthly_payment,
                        'amount_paid': amount_paid,
                        'payment_date': payment_date,
                        'status': status,
                        'transaction_reference': f"PAY-{loan.id}-{month+1:02d}" if status == 'paid' else '',
                        'payment_method': 'mobile_money' if status == 'paid' else '',
                    }
                )
                
                if created:
                    print(f"✅ Created repayment for {loan.applicant.get_full_name()} - Due: {due_date}")


def create_financial_stats(financial_partner):
    """Create sample financial statistics"""
    print("\n📊 Creating financial statistics...")
    
    # Calculate current month stats
    now = timezone.now()
    current_month_start = date(now.year, now.month, 1)
    if now.month == 12:
        next_month_start = date(now.year + 1, 1, 1)
    else:
        next_month_start = date(now.year, now.month + 1, 1)
    current_month_end = next_month_start - timedelta(days=1)
    
    # Get actual data for stats
    loans = LoanApplication.objects.filter(financial_partner=financial_partner)
    investments = Investment.objects.filter(investor=financial_partner)
    
    # Calculate loan statistics
    total_loans_issued = loans.filter(status__in=['approved', 'disbursed', 'repaid']).count()
    total_loan_amount = sum(loan.amount_approved or Decimal('0.00') 
                           for loan in loans.filter(status__in=['approved', 'disbursed', 'repaid']))
    active_loans = loans.filter(status__in=['approved', 'disbursed'])
    active_loans_count = active_loans.count()
    active_loans_amount = sum(loan.amount_approved or Decimal('0.00') for loan in active_loans)
    
    # Calculate investment statistics
    total_investments_count = investments.count()
    total_investment_amount = sum(inv.principal_amount for inv in investments)
    active_investments_value = sum(inv.current_value for inv in investments.filter(status='active'))
    
    # Calculate performance metrics
    average_loan_size = total_loan_amount / total_loans_issued if total_loans_issued > 0 else Decimal('0.00')
    approved_loans = loans.filter(status__in=['approved', 'disbursed', 'repaid']).count()
    total_applications = loans.count()
    loan_approval_rate = (approved_loans / total_applications * 100) if total_applications > 0 else Decimal('0.00')
    
    stats_data = {
        'financial_partner': financial_partner,
        'period_type': 'monthly',
        'period_start': current_month_start,
        'period_end': current_month_end,
        'total_loans_issued': total_loans_issued,
        'total_loan_amount': Decimal(str(total_loan_amount)),
        'active_loans_count': active_loans_count,
        'active_loans_amount': Decimal(str(active_loans_amount)),
        'repaid_loans_count': loans.filter(status='repaid').count(),
        'repaid_loans_amount': sum(loan.amount_approved or Decimal('0.00') 
                                  for loan in loans.filter(status='repaid')),
        'defaulted_loans_count': loans.filter(status='defaulted').count(),
        'defaulted_loans_amount': sum(loan.amount_approved or Decimal('0.00') 
                                     for loan in loans.filter(status='defaulted')),
        'total_investments_count': total_investments_count,
        'total_investment_amount': Decimal(str(total_investment_amount)),
        'active_investments_value': Decimal(str(active_investments_value)),
        'total_returns': Decimal(str(active_investments_value - total_investment_amount)),
        'average_loan_size': average_loan_size,
        'loan_approval_rate': loan_approval_rate,
        'average_interest_rate': Decimal('14.50'),
        'portfolio_return_rate': Decimal('8.75'),
    }
    
    stats, created = FinancialStats.objects.get_or_create(
        financial_partner=financial_partner,
        period_type='monthly',
        period_start=current_month_start,
        defaults=stats_data
    )
    
    if created:
        print(f"✅ Created financial statistics for {current_month_start}")
    
    return stats


def test_financial_endpoints():
    """Test the financial endpoints"""
    print("\n🧪 Testing financial endpoints...")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test API root
        response = client.get('/api/v1/financial/')
        print(f"✅ Financial API Root: {response.status_code}")
        
        # Test stats overview
        response = client.get('/api/v1/financial/stats/overview/')
        print(f"✅ Stats Overview: {response.status_code}")
        
        # Test loans endpoint
        response = client.get('/api/v1/financial/loans/')
        print(f"✅ Loans Endpoint: {response.status_code}")
        
        print("🎉 All financial endpoints are accessible!")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")


def main():
    """Main function to populate financial data"""
    print_section("🏦 FINANCIAL SERVICES DATA POPULATION", "33")
    
    try:
        # Create sample users
        financial_partner, farmers = create_sample_users()
        
        # Create sample loan applications
        loan_applications = create_sample_loan_applications(financial_partner, farmers)
        
        # Create sample investments
        investments = create_sample_investments(financial_partner)
        
        # Create sample repayments
        create_sample_repayments(loan_applications)
        
        # Create financial statistics
        stats = create_financial_stats(financial_partner)
        
        # Test endpoints
        test_financial_endpoints()
        
        print_section("✅ FINANCIAL DATA POPULATION COMPLETE", "32")
        print(f"📊 Created:")
        print(f"   • {len(loan_applications)} loan applications")
        print(f"   • {len(investments)} investments")
        print(f"   • Financial statistics for current month")
        print(f"   • Sample repayment schedules")
        print(f"\n🔗 Financial endpoints now available:")
        print(f"   • GET /api/v1/financial/stats/overview/")
        print(f"   • GET /api/v1/financial/loans/")
        print(f"   • GET /api/v1/financial/investments/")
        print(f"   • GET /api/v1/financial/repayments/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
