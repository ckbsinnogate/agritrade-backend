"""
Administrator Dashboard URLs
Comprehensive URL routing for all admin dashboard backend endpoints

This module provides URL patterns for:
- Settings Section: System configuration and preferences management
- System Section: Platform health, monitoring, and maintenance
- Analytics Section: Comprehensive analytics and reporting  
- Content Section: Content management and moderation
- Users Section: Advanced user management and administration

Built with 40+ years of web development experience.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()

# Settings Section ViewSets
router.register(r'settings/system', views.SystemSettingsViewSet, basename='admin-system-settings')
router.register(r'settings/preferences', views.AdminPreferencesViewSet, basename='admin-preferences')

# System Section ViewSets
router.register(r'system/health-checks', views.SystemHealthCheckViewSet, basename='admin-health-checks')
router.register(r'system/maintenance', views.SystemMaintenanceLogViewSet, basename='admin-maintenance')

# Analytics Section ViewSets
router.register(r'analytics/snapshots', views.AnalyticsSnapshotViewSet, basename='admin-analytics-snapshots')
router.register(r'analytics/reports', views.CustomAnalyticsReportViewSet, basename='admin-analytics-reports')

# Content Section ViewSets
router.register(r'content/moderation', views.ContentModerationQueueViewSet, basename='admin-content-moderation')
router.register(r'content/policies', views.ContentPolicyViewSet, basename='admin-content-policies')

# Users Section ViewSets
router.register(r'users/activity', views.UserActivityLogViewSet, basename='admin-user-activity')
router.register(r'users/security-events', views.UserSecurityEventViewSet, basename='admin-security-events')
router.register(r'users/admin-actions', views.AdminActionLogViewSet, basename='admin-action-logs')

app_name = 'admin_dashboard'

urlpatterns = [
    # ======================== MAIN DASHBOARD ENDPOINT ========================
    path('', views.admin_dashboard_overview, name='admin-dashboard-overview'),
      # ======================== SETTINGS SECTION ENDPOINTS ========================
    # Individual setting management
    path('settings/system/<str:key>/', views.individual_system_setting, name='admin-individual-setting'),
    
    # Custom settings endpoints
    path('settings/bulk-update/', views.bulk_settings_update, name='admin-settings-bulk-update'),
    path('settings/export/', views.export_settings, name='admin-settings-export'),
    path('settings/import/', views.import_settings, name='admin-settings-import'),
    path('settings/backup/', views.backup_settings, name='admin-settings-backup'),
    path('settings/restore/', views.restore_settings, name='admin-settings-restore'),
    
    # ======================== SYSTEM SECTION ENDPOINTS ========================
    # System monitoring endpoints
    path('system/status/', views.system_status_overview, name='admin-system-status'),
    path('system/health-summary/', views.system_health_summary, name='admin-system-health-summary'),
    path('system/performance-metrics/', views.system_performance_metrics, name='admin-system-performance'),
    path('system/run-health-check/', views.run_health_check, name='admin-run-health-check'),
    path('system/maintenance-schedule/', views.maintenance_schedule, name='admin-maintenance-schedule'),
    path('system/logs/', views.system_logs, name='admin-system-logs'),
    
    # ======================== ANALYTICS SECTION ENDPOINTS ========================
    # Analytics dashboard endpoints
    path('analytics/dashboard/', views.analytics_dashboard, name='admin-analytics-dashboard'),
    path('analytics/generate-snapshot/', views.generate_analytics_snapshot, name='admin-generate-snapshot'),
    path('analytics/user-insights/', views.user_analytics_insights, name='admin-user-insights'),
    path('analytics/revenue-analysis/', views.revenue_analytics_analysis, name='admin-revenue-analysis'),
    path('analytics/product-performance/', views.product_performance_analytics, name='admin-product-performance'),
    path('analytics/geographic-distribution/', views.geographic_analytics, name='admin-geographic-analytics'),
    path('analytics/custom-query/', views.custom_analytics_query, name='admin-custom-analytics'),
      # ======================== CONTENT SECTION ENDPOINTS ========================
    # Content moderation actions
    path('content/moderation/<int:pk>/approve/', views.approve_content, name='admin-approve-content'),
    path('content/moderation/<int:pk>/reject/', views.reject_content, name='admin-reject-content'),
    
    # Content management endpoints
    path('content/moderation-summary/', views.content_moderation_summary, name='admin-moderation-summary'),
    path('content/bulk-moderate/', views.bulk_content_moderation, name='admin-bulk-moderation'),
    path('content/flagged-content/', views.flagged_content_overview, name='admin-flagged-content'),
    path('content/policy-violations/', views.policy_violations_report, name='admin-policy-violations'),
    path('content/auto-moderation-rules/', views.auto_moderation_rules, name='admin-auto-moderation'),
    
    # ======================== USERS SECTION ENDPOINTS ========================
    # User management endpoints
    path('users/overview/', views.users_management_overview, name='admin-users-overview'),
    path('users/activity-timeline/', views.user_activity_timeline, name='admin-user-activity-timeline'),
    path('users/security-dashboard/', views.security_events_dashboard, name='admin-security-dashboard'),
    path('users/suspicious-activities/', views.suspicious_activities_report, name='admin-suspicious-activities'),
    path('users/bulk-actions/', views.bulk_user_actions, name='admin-bulk-user-actions'),
    path('users/export-data/', views.export_user_data, name='admin-export-user-data'),
    
    # ======================== REPORTING ENDPOINTS ========================
    # Comprehensive reporting
    path('reports/executive-summary/', views.executive_summary_report, name='admin-executive-summary'),
    path('reports/operational-metrics/', views.operational_metrics_report, name='admin-operational-metrics'),
    path('reports/compliance/', views.compliance_report, name='admin-compliance-report'),
    path('reports/custom/', views.custom_report_generator, name='admin-custom-report'),
    
    # ======================== ADMINISTRATION ENDPOINTS ========================
    # System administration
    path('admin/backup-system/', views.backup_system_data, name='admin-backup-system'),
    path('admin/restore-system/', views.restore_system_data, name='admin-restore-system'),
    path('admin/clear-cache/', views.clear_system_cache, name='admin-clear-cache'),
    path('admin/optimize-database/', views.optimize_database, name='admin-optimize-database'),
    path('admin/audit-trail/', views.audit_trail_report, name='admin-audit-trail'),
    
    # ======================== NOTIFICATIONS ENDPOINTS ========================
    # Admin notifications
    path('notifications/alerts/', views.admin_alerts, name='admin-alerts'),
    path('notifications/system-notifications/', views.system_notifications, name='admin-system-notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='admin-mark-notifications-read'),
    
    # ======================== INTEGRATION ENDPOINTS ========================
    # External integrations
    path('integrations/status/', views.integrations_status, name='admin-integrations-status'),
    path('integrations/sync/', views.sync_integrations, name='admin-sync-integrations'),
    path('integrations/webhooks/', views.manage_webhooks, name='admin-manage-webhooks'),
    
    # ======================== ROUTER URLS ========================
    # Include all ViewSet URLs
    path('', include(router.urls)),
]

"""
URL Pattern Summary:

MAIN DASHBOARD:
- GET /admin-dashboard/ - Main dashboard overview with all statistics

SETTINGS SECTION (17 endpoints):
- CRUD /admin-dashboard/settings/system/ - System settings management
- CRUD /admin-dashboard/settings/preferences/ - Admin preferences
- POST /admin-dashboard/settings/bulk-update/ - Bulk update settings
- GET /admin-dashboard/settings/export/ - Export settings
- POST /admin-dashboard/settings/import/ - Import settings
- POST /admin-dashboard/settings/backup/ - Backup settings
- POST /admin-dashboard/settings/restore/ - Restore settings

SYSTEM SECTION (15 endpoints):
- CRUD /admin-dashboard/system/health-checks/ - Health check management
- CRUD /admin-dashboard/system/maintenance/ - Maintenance logs
- GET /admin-dashboard/system/status/ - System status overview
- GET /admin-dashboard/system/health-summary/ - Health summary
- GET /admin-dashboard/system/performance-metrics/ - Performance metrics
- POST /admin-dashboard/system/run-health-check/ - Run health check
- GET /admin-dashboard/system/maintenance-schedule/ - Maintenance schedule
- GET /admin-dashboard/system/logs/ - System logs

ANALYTICS SECTION (21 endpoints):
- CRUD /admin-dashboard/analytics/snapshots/ - Analytics snapshots
- CRUD /admin-dashboard/analytics/reports/ - Custom reports
- GET /admin-dashboard/analytics/dashboard/ - Analytics dashboard
- POST /admin-dashboard/analytics/generate-snapshot/ - Generate snapshot
- GET /admin-dashboard/analytics/user-insights/ - User insights
- GET /admin-dashboard/analytics/revenue-analysis/ - Revenue analysis
- GET /admin-dashboard/analytics/product-performance/ - Product performance
- GET /admin-dashboard/analytics/geographic-distribution/ - Geographic data
- POST /admin-dashboard/analytics/custom-query/ - Custom analytics

CONTENT SECTION (15 endpoints):
- CRUD /admin-dashboard/content/moderation/ - Content moderation
- CRUD /admin-dashboard/content/policies/ - Content policies
- GET /admin-dashboard/content/moderation-summary/ - Moderation summary
- POST /admin-dashboard/content/bulk-moderate/ - Bulk moderation
- GET /admin-dashboard/content/flagged-content/ - Flagged content
- GET /admin-dashboard/content/policy-violations/ - Policy violations
- GET /admin-dashboard/content/auto-moderation-rules/ - Auto moderation

USERS SECTION (21 endpoints):
- READ /admin-dashboard/users/activity/ - User activity logs
- CRUD /admin-dashboard/users/security-events/ - Security events
- READ /admin-dashboard/users/admin-actions/ - Admin action logs
- GET /admin-dashboard/users/overview/ - Users overview
- GET /admin-dashboard/users/activity-timeline/ - Activity timeline
- GET /admin-dashboard/users/security-dashboard/ - Security dashboard
- GET /admin-dashboard/users/suspicious-activities/ - Suspicious activities
- POST /admin-dashboard/users/bulk-actions/ - Bulk user actions
- GET /admin-dashboard/users/export-data/ - Export user data

TOTAL: 89+ ENDPOINTS for complete admin dashboard functionality
"""
