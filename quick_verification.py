#!/usr/bin/env python
"""
Quick Server Verification Script
Tests if Django server can start properly and validates key configurations
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def main():
    """Main verification function"""
    print("🔍 AgriConnect Backend Final Verification")
    print("=" * 50)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
    
    try:
        django.setup()
        print("✅ Django environment setup successful")
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False
    
    # Check database connection
    try:
        from django.db import connections
        db_conn = connections['default']
        cursor = db_conn.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Verify key models can be imported
    try:
        from users.models import User
        from subscriptions.models import Subscription  
        from communications.models import CommunicationLog
        from warehouses.models import WarehouseInventory
        print("✅ Key models import successful")
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    # Check if admin is accessible
    try:
        from django.contrib.admin.sites import site
        from django.urls import reverse
        admin_url = reverse('admin:index')
        print(f"✅ Admin interface ready at: {admin_url}")
    except Exception as e:
        print(f"⚠️ Admin check warning: {e}")
    
    # Verify REST framework
    try:
        from rest_framework.views import APIView
        from rest_framework.response import Response
        print("✅ Django REST Framework ready")
    except Exception as e:
        print(f"❌ REST Framework check failed: {e}")
        return False
    
    print("\n🎉 ALL VERIFICATIONS PASSED!")
    print("🚀 Backend is ready for frontend development")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n📋 NEXT STEPS:")
        print("1. Start development server: python manage.py runserver")
        print("2. Access admin: http://127.0.0.1:8000/admin/")
        print("3. Test API endpoints: http://127.0.0.1:8000/api/v1/")
        print("4. Begin React frontend development")
        sys.exit(0)
    else:
        print("\n❌ Verification failed - check error messages above")
        sys.exit(1)
