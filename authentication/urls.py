from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import admin_views
from . import views_sms_otp  # Import SMS OTP views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', admin_views.AdminUserManagementViewSet, basename='admin-user')

app_name = 'authentication'

urlpatterns = [
    # Authentication API Root
    path('', views.auth_api_root, name='auth-root'),
      # User Registration and Verification
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('register-frontend/', views.FrontendUserRegistrationView.as_view(), name='register-frontend'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    
    # Email OTP Authentication System
    path('email-otp/request/', views.EmailOTPRequestView.as_view(), name='email-otp-request'),
    path('email-otp/verify/', views.EmailOTPVerifyView.as_view(), name='email-otp-verify'),
    path('email-otp/resend/', views.EmailOTPResendView.as_view(), name='email-otp-resend'),
    path('email-otp/status/', views.EmailOTPStatusView.as_view(), name='email-otp-status'),
    path('email-otp/register/', views.EmailOTPRegistrationView.as_view(), name='email-otp-register'),
    path('email-otp/login/', views.EmailOTPLoginView.as_view(), name='email-otp-login'),
    path('email-otp/password-reset/', views.EmailOTPPasswordResetView.as_view(), name='email-otp-password-reset'),
    
    # SMS OTP Authentication System
    path('sms-otp/request/', views_sms_otp.SMSOTPRequestView.as_view(), name='sms-otp-request'),
    path('sms-otp/verify/', views_sms_otp.SMSOTPVerifyView.as_view(), name='sms-otp-verify'),
    path('sms-otp/resend/', views_sms_otp.SMSOTPResendView.as_view(), name='sms-otp-resend'),
    path('sms-otp/status/', views_sms_otp.SMSOTPStatusView.as_view(), name='sms-otp-status'),
    path('sms-otp/register/', views_sms_otp.SMSOTPRegistrationView.as_view(), name='sms-otp-register'),
    path('sms-otp/login/', views_sms_otp.SMSOTPLoginView.as_view(), name='sms-otp-login'),
    path('sms-otp/password-reset/', views_sms_otp.SMSOTPPasswordResetView.as_view(), name='sms-otp-password-reset'),
    
    # SMS OTP Admin Endpoints (Admin only)
    path('sms-otp/admin/stats/', views_sms_otp.SMSOTPStatsView.as_view(), name='sms-otp-admin-stats'),
    path('sms-otp/admin/cleanup/', views_sms_otp.SMSOTPCleanupView.as_view(), name='sms-otp-admin-cleanup'),
    
    # User Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token-refresh'),
    
    # Password Management
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Profile Management
    path('profile/', views.UpdateProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    
    # Account Management
    path('deactivate/', views.DeactivateAccountView.as_view(), name='deactivate-account'),
    path('delete/', views.DeleteAccountView.as_view(), name='delete-account'),
    
    # Admin Dashboard
    path('admin/dashboard/stats/', admin_views.admin_dashboard_stats, name='admin-dashboard-stats'),
    
    # Include router URLs for admin user management
    path('', include(router.urls)),
]
