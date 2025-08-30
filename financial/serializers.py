"""
Financial Services Serializers
REST API serializers for financial models
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import LoanApplication, LoanRepayment, Investment, FinancialStats

User = get_user_model()


class LoanApplicationSerializer(serializers.ModelSerializer):
    """Serializer for loan applications"""
    
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    financial_partner_name = serializers.CharField(source='financial_partner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    loan_type_display = serializers.CharField(source='get_loan_type_display', read_only=True)
    
    class Meta:
        model = LoanApplication
        fields = [
            'id', 'applicant', 'applicant_name', 'financial_partner', 'financial_partner_name',
            'loan_type', 'loan_type_display', 'amount_requested', 'amount_approved',
            'interest_rate', 'term_months', 'status', 'status_display',
            'application_date', 'approval_date', 'disbursement_date',
            'repayment_start_date', 'maturity_date', 'purpose', 'collateral_description',
            'business_plan', 'credit_score', 'monthly_income', 'existing_debts',
            'reviewer_notes', 'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'application_date']


class LoanApplicationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for loan application lists"""
    
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    loan_type_display = serializers.CharField(source='get_loan_type_display', read_only=True)
    
    class Meta:
        model = LoanApplication
        fields = [
            'id', 'applicant_name', 'loan_type', 'loan_type_display',
            'amount_requested', 'amount_approved', 'interest_rate',
            'status', 'status_display', 'application_date'
        ]


class LoanRepaymentSerializer(serializers.ModelSerializer):
    """Serializer for loan repayments"""
    
    loan_applicant_name = serializers.CharField(source='loan_application.applicant.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LoanRepayment
        fields = [
            'id', 'loan_application', 'loan_applicant_name', 'due_date',
            'amount_due', 'amount_paid', 'payment_date', 'status', 'status_display',
            'transaction_reference', 'payment_method', 'late_fee',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvestmentSerializer(serializers.ModelSerializer):
    """Serializer for investments"""
    
    investor_name = serializers.CharField(source='investor.get_full_name', read_only=True)
    investment_type_display = serializers.CharField(source='get_investment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_return = serializers.SerializerMethodField()
    
    class Meta:
        model = Investment
        fields = [
            'id', 'investor', 'investor_name', 'investment_type', 'investment_type_display',
            'title', 'description', 'principal_amount', 'current_value',
            'expected_return_rate', 'actual_return_rate', 'current_return',
            'investment_date', 'maturity_date', 'status', 'status_display',
            'risk_level', 'created_at', 'updated_at'        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_current_return(self, obj):
        """Calculate current return amount"""
        if obj.current_value and obj.principal_amount:
            return str(obj.current_value - obj.principal_amount)
        return "0.00"


class FinancialStatsSerializer(serializers.ModelSerializer):
    """Serializer for financial statistics"""
    
    financial_partner_name = serializers.CharField(source='financial_partner.get_full_name', read_only=True)
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    
    class Meta:
        model = FinancialStats
        fields = [
            'id', 'financial_partner', 'financial_partner_name',
            'period_type', 'period_type_display', 'period_start', 'period_end',
            'total_loans_issued', 'total_loan_amount', 'active_loans_count',
            'active_loans_amount', 'repaid_loans_count', 'repaid_loans_amount',
            'defaulted_loans_count', 'defaulted_loans_amount',
            'total_investments_count', 'total_investment_amount',
            'active_investments_value', 'total_returns',
            'average_loan_size', 'loan_approval_rate', 'average_interest_rate',
            'portfolio_return_rate', 'calculated_at', 'updated_at'
        ]
        read_only_fields = ['id', 'calculated_at', 'updated_at']


class FinancialOverviewSerializer(serializers.Serializer):
    """Serializer for financial overview/stats endpoint"""
    
    # Loan Statistics
    total_loans_issued = serializers.IntegerField()
    total_loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    active_loans_count = serializers.IntegerField()
    active_loans_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_applications = serializers.IntegerField()
    
    # Investment Statistics  
    total_investments = serializers.IntegerField()
    total_investment_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    portfolio_performance = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Performance Metrics
    loan_approval_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_loan_size = serializers.DecimalField(max_digits=12, decimal_places=2)
    portfolio_return_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Recent Activity
    recent_loan_applications = LoanApplicationListSerializer(many=True, read_only=True)
    recent_investments = InvestmentSerializer(many=True, read_only=True)
    
    # Dates
    last_updated = serializers.DateTimeField()


class LoanApplicationStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating loan application status"""
    
    status = serializers.ChoiceField(choices=LoanApplication.STATUS_CHOICES)
    amount_approved = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    reviewer_notes = serializers.CharField(required=False, allow_blank=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


class LoanApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating loan applications"""
    
    class Meta:
        model = LoanApplication
        fields = [
            'loan_type', 'amount_requested', 'term_months', 'purpose',
            'collateral_description', 'business_plan', 'monthly_income', 'existing_debts'
        ]
    
    def create(self, validated_data):
        # Set the applicant to the current user
        validated_data['applicant'] = self.context['request'].user
        
        # If no financial partner specified, assign to a default one or handle assignment logic
        if 'financial_partner' not in validated_data:
            # For now, we'll need to implement assignment logic
            # This could be based on loan type, amount, region, etc.
            pass
            
        return super().create(validated_data)
