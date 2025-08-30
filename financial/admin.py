"""
Financial Services Admin Configuration
Django admin interface for financial models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import LoanApplication, LoanRepayment, Investment, FinancialStats


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'applicant_name', 'financial_partner_name', 'loan_type',
        'amount_requested', 'amount_approved', 'status', 'application_date'
    ]
    list_filter = ['status', 'loan_type', 'application_date', 'financial_partner']
    search_fields = ['applicant__first_name', 'applicant__last_name', 'purpose']
    readonly_fields = ['id', 'application_date', 'created_at', 'updated_at']
    ordering = ['-application_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'applicant', 'financial_partner', 'application_date')
        }),
        ('Loan Details', {
            'fields': ('loan_type', 'amount_requested', 'amount_approved', 'interest_rate', 'term_months')
        }),
        ('Status & Dates', {
            'fields': ('status', 'approval_date', 'disbursement_date', 'repayment_start_date', 'maturity_date')
        }),
        ('Application Details', {
            'fields': ('purpose', 'collateral_description', 'business_plan', 'credit_score')
        }),
        ('Financial Information', {
            'fields': ('monthly_income', 'existing_debts')
        }),
        ('Processing', {
            'fields': ('reviewer_notes', 'rejection_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def applicant_name(self, obj):
        return obj.applicant.get_full_name()
    applicant_name.short_description = 'Applicant'
    
    def financial_partner_name(self, obj):
        return obj.financial_partner.get_full_name()
    financial_partner_name.short_description = 'Financial Partner'


@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'loan_applicant_name', 'due_date', 'amount_due',
        'amount_paid', 'status', 'payment_date'
    ]
    list_filter = ['status', 'due_date', 'payment_date']
    search_fields = ['loan_application__applicant__first_name', 'loan_application__applicant__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-due_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'loan_application')
        }),
        ('Repayment Details', {
            'fields': ('due_date', 'amount_due', 'amount_paid', 'payment_date', 'status')
        }),
        ('Payment Information', {
            'fields': ('transaction_reference', 'payment_method', 'late_fee')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def loan_applicant_name(self, obj):
        return obj.loan_application.applicant.get_full_name()
    loan_applicant_name.short_description = 'Loan Applicant'


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'investor_name', 'title', 'investment_type',
        'principal_amount', 'current_value', 'status', 'investment_date'
    ]
    list_filter = ['investment_type', 'status', 'risk_level', 'investment_date']
    search_fields = ['title', 'description', 'investor__first_name', 'investor__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-investment_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'investor', 'investment_type', 'title', 'description')
        }),
        ('Financial Details', {
            'fields': ('principal_amount', 'current_value', 'expected_return_rate', 'actual_return_rate')
        }),
        ('Timeline', {
            'fields': ('investment_date', 'maturity_date', 'status')
        }),
        ('Risk Assessment', {
            'fields': ('risk_level',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def investor_name(self, obj):
        return obj.investor.get_full_name()
    investor_name.short_description = 'Investor'


@admin.register(FinancialStats)
class FinancialStatsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'financial_partner_name', 'period_type',
        'period_start', 'total_loans_issued', 'total_loan_amount'
    ]
    list_filter = ['period_type', 'period_start', 'financial_partner']
    search_fields = ['financial_partner__first_name', 'financial_partner__last_name']
    readonly_fields = ['id', 'calculated_at', 'updated_at']
    ordering = ['-period_start']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'financial_partner', 'period_type', 'period_start', 'period_end')
        }),
        ('Loan Statistics', {
            'fields': (
                'total_loans_issued', 'total_loan_amount', 'active_loans_count',
                'active_loans_amount', 'repaid_loans_count', 'repaid_loans_amount',
                'defaulted_loans_count', 'defaulted_loans_amount'
            )
        }),
        ('Investment Statistics', {
            'fields': (
                'total_investments_count', 'total_investment_amount',
                'active_investments_value', 'total_returns'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'average_loan_size', 'loan_approval_rate',
                'average_interest_rate', 'portfolio_return_rate'
            )
        }),
        ('Metadata', {
            'fields': ('calculated_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def financial_partner_name(self, obj):
        return obj.financial_partner.get_full_name()
    financial_partner_name.short_description = 'Financial Partner'
