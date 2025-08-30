"""
AgriConnect Users URLs
User profile management endpoints
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Users API Root
    path('', views.users_api_root, name='users-root'),
    
    # Basic Profile Management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UserProfileView.as_view(), name='user-profile-update'),
    path('profile/comprehensive/', views.ComprehensiveUserProfileView.as_view(), name='comprehensive-profile'),
    path('profile/status/', views.user_profile_status, name='profile-status'),
    
    # Account Management
    path('activate/', views.UserActivationView.as_view(), name='activate-account'),
    path('bulk-activate/', views.bulk_activate_accounts, name='bulk-activate'),
    
    # Extended Profile
    path('extended-profile/', views.ExtendedUserProfileView.as_view(), name='extended-profile'),
    
    # Role-Specific Profiles
    path('farmer-profile/', views.FarmerProfileView.as_view(), name='farmer-profile'),
    path('consumer-profile/', views.ConsumerProfileView.as_view(), name='consumer-profile'),
    path('institution-profile/', views.InstitutionProfileView.as_view(), name='institution-profile'),
    path('agent-profile/', views.AgentProfileView.as_view(), name='agent-profile'),
    path('financial-partner-profile/', views.FinancialPartnerProfileView.as_view(), name='financial-partner-profile'),
    path('government-official-profile/', views.GovernmentOfficialProfileView.as_view(), name='government-official-profile'),
]
