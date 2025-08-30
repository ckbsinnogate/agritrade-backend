"""
Financial Services Views
REST API views for financial loan and investment management
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from .models import LoanApplication, LoanRepayment, Investment, FinancialStats
from .serializers import (
    LoanApplicationSerializer,
    LoanApplicationListSerializer,
    LoanRepaymentSerializer,
    InvestmentSerializer,
    FinancialStatsSerializer,
    FinancialOverviewSerializer,
    LoanApplicationStatusUpdateSerializer,
    LoanApplicationCreateSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


class IsFinancialPartnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for financial partners
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow read access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is a financial partner for write operations
        return request.user.roles.filter(name='FINANCIAL_PARTNER').exists()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def financial_api_root(request, format=None):
    """Financial Services API Root"""
    return Response({
        'name': 'AgriConnect Financial Services API',
        'description': 'Loan management and investment tracking for agricultural finance',
        'version': '1.0',
        'endpoints': {
            'stats_overview': request.build_absolute_uri('stats/overview/'),
            'loans': request.build_absolute_uri('loans/'),
            'investments': request.build_absolute_uri('investments/'),
            'repayments': request.build_absolute_uri('repayments/'),
            'financial_stats': request.build_absolute_uri('stats/'),
        },
        'status': 'operational'
    })


class FinancialStatsOverviewView(APIView):
    """
    GET /api/v1/financial/stats/overview/
    Financial statistics overview for financial partners
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            
            # Check if user is a financial partner
            if not user.roles.filter(name='FINANCIAL_PARTNER').exists():
                return Response({
                    'error': 'Access denied',
                    'detail': 'Only financial partners can access financial statistics'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Calculate statistics for the financial partner
            now = timezone.now()
            thirty_days_ago = now - timedelta(days=30)
            
            # Loan statistics
            loans_managed = LoanApplication.objects.filter(financial_partner=user)
            active_loans = loans_managed.filter(status__in=['approved', 'disbursed'])
            pending_loans = loans_managed.filter(status__in=['pending', 'under_review'])
            
            total_loans_issued = loans_managed.filter(status__in=['approved', 'disbursed', 'repaid']).count()
            total_loan_amount = loans_managed.filter(
                status__in=['approved', 'disbursed', 'repaid']
            ).aggregate(total=Sum('amount_approved'))['total'] or Decimal('0.00')
            
            active_loans_count = active_loans.count()
            active_loans_amount = active_loans.aggregate(total=Sum('amount_approved'))['total'] or Decimal('0.00')
            pending_applications = pending_loans.count()
            
            # Investment statistics
            investments = Investment.objects.filter(investor=user)
            total_investments = investments.count()
            total_investment_value = investments.aggregate(total=Sum('current_value'))['total'] or Decimal('0.00')
            
            # Calculate portfolio performance
            total_principal = investments.aggregate(total=Sum('principal_amount'))['total'] or Decimal('0.00')
            if total_principal > 0:
                portfolio_performance = ((total_investment_value - total_principal) / total_principal) * 100
            else:
                portfolio_performance = Decimal('0.00')
            
            # Performance metrics
            approved_loans = loans_managed.filter(status__in=['approved', 'disbursed', 'repaid']).count()
            total_applications = loans_managed.count()
            loan_approval_rate = (approved_loans / total_applications * 100) if total_applications > 0 else Decimal('0.00')
            
            average_loan_size = total_loan_amount / total_loans_issued if total_loans_issued > 0 else Decimal('0.00')
            
            avg_return = investments.aggregate(avg=Avg('actual_return_rate'))['avg'] or Decimal('0.00')
            portfolio_return_rate = avg_return if avg_return else Decimal('0.00')
            
            # Recent activity
            recent_applications = loans_managed.filter(
                application_date__gte=thirty_days_ago
            ).order_by('-application_date')[:5]
            
            recent_investments = investments.filter(
                investment_date__gte=thirty_days_ago.date()
            ).order_by('-investment_date')[:5]
              # Prepare response data
            data = {
                'total_loans_issued': total_loans_issued,
                'total_loan_amount': str(total_loan_amount),
                'active_loans_count': active_loans_count,
                'active_loans_amount': str(active_loans_amount),
                'pending_applications': pending_applications,
                'total_investments': total_investments,
                'total_investment_value': str(total_investment_value),
                'portfolio_performance': str(portfolio_performance),
                'loan_approval_rate': str(loan_approval_rate),
                'average_loan_size': str(average_loan_size),
                'portfolio_return_rate': str(portfolio_return_rate),
                'recent_loan_applications': LoanApplicationListSerializer(recent_applications, many=True).data,
                'recent_investments': InvestmentSerializer(recent_investments, many=True).data,
                'last_updated': now
            }
            
            serializer = FinancialOverviewSerializer(data)
            
            logger.info(f"Financial stats overview requested by: {user.username}")
            
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Financial statistics retrieved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error retrieving financial stats overview: {str(e)}")
            return Response({
                'error': 'Failed to retrieve financial statistics',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing loan applications
    GET /api/v1/financial/loans/ - List loan applications
    POST /api/v1/financial/loans/ - Create loan application
    GET /api/v1/financial/loans/{id}/ - Get loan application details
    PUT /api/v1/financial/loans/{id}/ - Update loan application
    """
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filter options
    filterset_fields = {
        'status': ['exact', 'in'],
        'loan_type': ['exact', 'in'],
        'application_date': ['gte', 'lte'],
        'amount_requested': ['gte', 'lte'],
    }
    
    # Search fields
    search_fields = ['applicant__first_name', 'applicant__last_name', 'purpose']
    
    # Ordering
    ordering_fields = ['application_date', 'amount_requested', 'status']
    ordering = ['-application_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.roles.filter(name='FINANCIAL_PARTNER').exists():
            # Financial partners see loans they manage
            return LoanApplication.objects.filter(financial_partner=user)
        elif user.roles.filter(name='FARMER').exists():
            # Farmers see their own loan applications
            return LoanApplication.objects.filter(applicant=user)
        else:
            # Other users see no loans by default
            return LoanApplication.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LoanApplicationListSerializer
        elif self.action == 'create':
            return LoanApplicationCreateSerializer
        return LoanApplicationSerializer
    
    def perform_create(self, serializer):
        # Set applicant to current user
        serializer.save(applicant=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsFinancialPartnerOrReadOnly])
    def update_status(self, request, pk=None):
        """Update loan application status"""
        loan = self.get_object()
        serializer = LoanApplicationStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Update loan status
            status_data = serializer.validated_data['status']
            loan.status = status_data
            
            # Handle status-specific updates
            if status_data == 'approved' and 'amount_approved' in serializer.validated_data:
                loan.amount_approved = serializer.validated_data['amount_approved']
                loan.approval_date = timezone.now()
            
            if 'interest_rate' in serializer.validated_data:
                loan.interest_rate = serializer.validated_data['interest_rate']
            
            if 'reviewer_notes' in serializer.validated_data:
                loan.reviewer_notes = serializer.validated_data['reviewer_notes']
            
            if status_data == 'rejected' and 'rejection_reason' in serializer.validated_data:
                loan.rejection_reason = serializer.validated_data['rejection_reason']
            
            loan.save()
            
            logger.info(f"Loan {loan.id} status updated to {status_data} by {request.user.username}")
            
            return Response({
                'success': True,
                'message': f'Loan status updated to {loan.get_status_display()}',
                'data': LoanApplicationSerializer(loan).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing investments
    """
    serializer_class = InvestmentSerializer
    permission_classes = [IsFinancialPartnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'investment_type': ['exact', 'in'],
        'status': ['exact', 'in'],
        'risk_level': ['exact', 'in'],
        'investment_date': ['gte', 'lte'],
    }
    
    search_fields = ['title', 'description']
    ordering_fields = ['investment_date', 'principal_amount', 'current_value']
    ordering = ['-investment_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.roles.filter(name='FINANCIAL_PARTNER').exists():
            return Investment.objects.filter(investor=user)
        else:
            return Investment.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(investor=self.request.user)


class LoanRepaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing loan repayments
    """
    serializer_class = LoanRepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = {
        'status': ['exact', 'in'],
        'due_date': ['gte', 'lte'],
        'loan_application': ['exact'],
    }
    
    ordering_fields = ['due_date', 'amount_due']
    ordering = ['due_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.roles.filter(name='FINANCIAL_PARTNER').exists():
            # Financial partners see repayments for loans they manage
            return LoanRepayment.objects.filter(loan_application__financial_partner=user)
        elif user.roles.filter(name='FARMER').exists():
            # Farmers see repayments for their loans
            return LoanRepayment.objects.filter(loan_application__applicant=user)
        else:
            return LoanRepayment.objects.none()


class FinancialStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing financial statistics
    """
    serializer_class = FinancialStatsSerializer
    permission_classes = [IsFinancialPartnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = {
        'period_type': ['exact'],
        'period_start': ['gte', 'lte'],
    }
    
    ordering_fields = ['period_start', 'period_type']
    ordering = ['-period_start']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.roles.filter(name='FINANCIAL_PARTNER').exists():
            return FinancialStats.objects.filter(financial_partner=user)
        else:
            return FinancialStats.objects.none()
