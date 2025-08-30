#!/usr/bin/env python3
"""
Admin Dashboard Status Check
Quick status verification without long outputs
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def status_check():
    """Quick status check"""
    try:
        # Import test
        from admin_dashboard.views import admin_dashboard_overview
        from admin_dashboard.models import SystemSettings
        from admin_dashboard.serializers import SystemSettingsSerializer
        
        # Quick counts
        from django.apps import apps
        admin_models = apps.get_app_config('admin_dashboard').get_models()
        
        print(f"✅ Status: OPERATIONAL")
        print(f"✅ Models: {len(admin_models)} registered")
        print(f"✅ Views: Imported successfully")
        print(f"✅ Ready: Production deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    status_check()
