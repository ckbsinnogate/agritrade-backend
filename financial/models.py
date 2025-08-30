"""
Financial Services Models
Models for loan management, investment tracking, and financial analytics
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class LoanApplication(models.Model):
    """Model for loan applications from farmers"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('rejected', 'Rejected'),
        ('repaid', 'Fully Repaid'),
        ('defaulted', 'Defaulted'),
    ]
    
    LOAN_TYPE_CHOICES = [
        ('seasonal_loan', 'Seasonal Farming Loan'),
        ('equipment_financing', 'Equipment Financing'),
        ('working_capital', 'Working Capital'),
        ('harvest_advance', 'Harvest Advance'),
        ('microfinance', 'Microfinance'),
        ('group_lending', 'Group Lending'),
        ('instant_advance', 'Instant Advance'),
        ('contract_financing', 'Contract Financing'),
        ('supply_chain_credit', 'Supply Chain Credit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications')
    financial_partner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='managed_loans',
        limit_choices_to={'roles__name': 'FINANCIAL_PARTNER'}
    )
    
    # Loan Details
    loan_type = models.CharField(max_length=30, choices=LOAN_TYPE_CHOICES)
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'))
    term_months = models.PositiveIntegerField(default=12)
    
    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    repayment_start_date = models.DateField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    
    # Application Details
    purpose = models.TextField()
    collateral_description = models.TextField(blank=True)
    business_plan = models.TextField(blank=True)
    credit_score = models.PositiveIntegerField(null=True, blank=True)
    
    # Financial Information
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    existing_debts = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Processing Notes
    reviewer_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_loan_applications'
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['loan_type']),
            models.Index(fields=['financial_partner']),
            models.Index(fields=['application_date']),
        ]
    
    def __str__(self):
        return f"Loan Application {self.id} - {self.applicant.get_full_name()} - {self.get_status_display()}"


class LoanRepayment(models.Model):
    """Model for tracking loan repayments"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partial Payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='repayments')
    
    # Repayment Details
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Payment Information
    transaction_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_loan_repayments'
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['loan_application']),
        ]
    
    def __str__(self):
        return f"Repayment {self.id} - {self.loan_application.applicant.get_full_name()}"


class Investment(models.Model):
    """Model for tracking financial partner investments"""
    
    INVESTMENT_TYPE_CHOICES = [
        ('agricultural_project', 'Agricultural Project'),
        ('farmer_loan_portfolio', 'Farmer Loan Portfolio'),
        ('supply_chain_financing', 'Supply Chain Financing'),
        ('equipment_leasing', 'Equipment Leasing'),
        ('crop_insurance', 'Crop Insurance'),
        ('commodity_trading', 'Commodity Trading'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('matured', 'Matured'),
        ('liquidated', 'Liquidated'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='investments',
        limit_choices_to={'roles__name': 'FINANCIAL_PARTNER'}
    )
    
    # Investment Details
    investment_type = models.CharField(max_length=30, choices=INVESTMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Financial Details
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    expected_return_rate = models.DecimalField(max_digits=5, decimal_places=2)
    actual_return_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Dates
    investment_date = models.DateField()
    maturity_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Risk Assessment
    risk_level = models.CharField(
        max_length=10, 
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_investments'
        ordering = ['-investment_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['investment_type']),
            models.Index(fields=['investor']),
        ]
    
    def __str__(self):
        return f"Investment {self.title} - {self.investor.get_full_name()}"


class FinancialStats(models.Model):
    """Model for storing aggregated financial statistics"""
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    financial_partner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='financial_stats',
        limit_choices_to={'roles__name': 'FINANCIAL_PARTNER'}
    )
    
    # Period Information
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Loan Statistics
    total_loans_issued = models.PositiveIntegerField(default=0)
    total_loan_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    active_loans_count = models.PositiveIntegerField(default=0)
    active_loans_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    repaid_loans_count = models.PositiveIntegerField(default=0)
    repaid_loans_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    defaulted_loans_count = models.PositiveIntegerField(default=0)
    defaulted_loans_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Investment Statistics
    total_investments_count = models.PositiveIntegerField(default=0)
    total_investment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    active_investments_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_returns = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Performance Metrics
    average_loan_size = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    loan_approval_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    average_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    portfolio_return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_stats'
        ordering = ['-period_start']
        unique_together = ['financial_partner', 'period_type', 'period_start']
        indexes = [
            models.Index(fields=['period_type']),
            models.Index(fields=['period_start']),
            models.Index(fields=['financial_partner']),
        ]
    
    def __str__(self):
        return f"Financial Stats - {self.financial_partner.get_full_name()} - {self.period_type} - {self.period_start}"
