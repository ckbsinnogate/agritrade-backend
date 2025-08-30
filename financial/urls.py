"""
Financial Services URLs
URL configuration for financial loan and investment management APIs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'loans', views.LoanApplicationViewSet, basename='loan-application')
router.register(r'investments', views.InvestmentViewSet, basename='investment')
router.register(r'repayments', views.LoanRepaymentViewSet, basename='loan-repayment')
router.register(r'stats', views.FinancialStatsViewSet, basename='financial-stats')

app_name = 'financial'

urlpatterns = [
    # API Root
    path('', views.financial_api_root, name='financial-api-root'),
    
    # Financial Statistics Overview (for dashboard)
    path('stats/overview/', views.FinancialStatsOverviewView.as_view(), name='financial-stats-overview'),
    
    # Include router URLs
    path('', include(router.urls)),
]

"""
Financial API Endpoints Summary:

MAIN ENDPOINTS:
- GET /api/v1/financial/ - API root with endpoint documentation

STATISTICS:
- GET /api/v1/financial/stats/overview/ - Financial statistics overview (dashboard)
- GET /api/v1/financial/stats/ - List financial statistics records
- GET /api/v1/financial/stats/{id}/ - Get specific statistics record

LOAN MANAGEMENT:
- GET /api/v1/financial/loans/ - List loan applications (filtered by user role)
- POST /api/v1/financial/loans/ - Create new loan application
- GET /api/v1/financial/loans/{id}/ - Get loan application details
- PUT /api/v1/financial/loans/{id}/ - Update loan application
- POST /api/v1/financial/loans/{id}/update_status/ - Update loan status (financial partners)

INVESTMENT MANAGEMENT:
- GET /api/v1/financial/investments/ - List investments
- POST /api/v1/financial/investments/ - Create new investment
- GET /api/v1/financial/investments/{id}/ - Get investment details
- PUT /api/v1/financial/investments/{id}/ - Update investment

REPAYMENT TRACKING:
- GET /api/v1/financial/repayments/ - List loan repayments
- POST /api/v1/financial/repayments/ - Record new repayment
- GET /api/v1/financial/repayments/{id}/ - Get repayment details
- PUT /api/v1/financial/repayments/{id}/ - Update repayment

FILTERING & SEARCH:
All list endpoints support filtering, searching, and ordering:
- ?status=pending,under_review - Filter by status
- ?loan_type=seasonal_loan - Filter by loan type
- ?search=tomato - Search in relevant fields
- ?ordering=-application_date - Order by date (desc)

PERMISSIONS:
- Financial Partners: Full access to loans they manage and their investments
- Farmers: Can view their own loan applications and repayments
- Other users: Limited access based on role
"""
