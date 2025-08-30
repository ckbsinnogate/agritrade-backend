#!/usr/bin/env python
"""
AgriConnect Development Environment Verification Script
Comprehensive check of all development components
"""

import sys
import os
import django
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "\033[92m✅",
        "error": "\033[91m❌", 
        "warning": "\033[93m⚠️",
        "info": "\033[94mℹ️"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['info'])} {message}{reset}")

def check_virtual_env():
    """Check if virtual environment is active"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print_status(f"Virtual environment is ACTIVE", "success")
        print_status(f"Python path: {sys.executable}", "info")
        return True
    else:
        print_status("Virtual environment is NOT active", "error")
        print_status("Run: .\\venv\\Scripts\\Activate.ps1", "warning")
        return False

def check_django_setup():
    """Check Django configuration"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
        django.setup()
        print_status("Django setup successful", "success")
        print_status(f"Django version: {django.get_version()}", "info")
        return True
    except Exception as e:
        print_status(f"Django setup failed: {e}", "error")
        return False

def check_database_connection():
    """Check database connectivity"""
    try:
        from django.db import connection
        from django.conf import settings
        
        connection.ensure_connection()
        db_config = settings.DATABASES['default']
        db_name = db_config['NAME']
        db_engine = db_config['ENGINE'].split('.')[-1]
        
        print_status("Database connection successful", "success")
        print_status(f"Database: {db_engine} ({db_name})", "info")
        return True
    except Exception as e:
        print_status(f"Database connection failed: {e}", "error")
        return False

def check_project_structure():
    """Check required project apps"""
    required_apps = [
        'authentication', 'users', 'products', 'orders', 
        'warehouses', 'payments', 'traceability', 'reviews',
        'subscriptions', 'communications', 'advertisements'
    ]
    
    missing_apps = []
    for app in required_apps:
        if Path(app).exists():
            print_status(f"{app} app found", "success")
        else:
            print_status(f"{app} app missing", "error")
            missing_apps.append(app)
    
    return len(missing_apps) == 0

def check_dependencies():
    """Check key Python dependencies"""
    dependencies = [
        'django', 'rest_framework', 'psycopg2', 
        'requests', 'celery', 'django_filters'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            print_status(f"{dep} installed", "success")
        except ImportError:
            print_status(f"{dep} missing", "error")
            missing_deps.append(dep)
    
    return len(missing_deps) == 0

def check_migrations():
    """Check migration status"""
    try:
        from django.core.management import execute_from_command_line
        from io import StringIO
        import contextlib
        
        # Capture migration status
        f = StringIO()
        with contextlib.redirect_stdout(f):
            execute_from_command_line(['manage.py', 'showmigrations', '--format=plan'])
        
        output = f.getvalue()
        applied = output.count('[X]')
        pending = output.count('[ ]')
        
        print_status("Migration check successful", "success")
        print_status(f"Applied: {applied}, Pending: {pending}", "info")
        
        if pending > 0:
            print_status(f"{pending} pending migrations", "warning")
            print_status("Run: python manage.py migrate", "warning")
        
        return pending == 0
    except Exception as e:
        print_status(f"Migration check failed: {e}", "error")
        return False

def check_environment_files():
    """Check environment configuration files"""
    env_files = ['.env', '.env.production']
    for env_file in env_files:
        if Path(env_file).exists():
            print_status(f"{env_file} file found", "success")
        else:
            print_status(f"{env_file} file not found", "warning")

def main():
    """Main verification function"""
    print("🌾 AgriConnect Development Environment Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("1️⃣  Virtual Environment Status", check_virtual_env),
        ("2️⃣  Django Framework Status", check_django_setup),
        ("3️⃣  Database Connection Status", check_database_connection),
        ("4️⃣  Project Structure Verification", check_project_structure),
        ("5️⃣  Dependencies Status", check_dependencies),
        ("6️⃣  Migration Status", check_migrations),
    ]
    
    results = []
    for title, check_func in checks:
        print(f"\n{title}")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print_status(f"Check failed: {e}", "error")
            results.append(False)
    
    print(f"\n7️⃣  Environment Configuration")
    check_environment_files()
    
    # Summary
    print(f"\n🎯 Development Environment Summary")
    print("=" * 40)
    
    if all(results):
        print_status("All core checks passed!", "success")
        print_status("AgriConnect Platform: Development Ready", "success")
    else:
        failed_checks = sum(1 for r in results if not r)
        print_status(f"{failed_checks} checks failed", "error")
        print_status("Please fix issues before continuing", "warning")
    
    print(f"\n🚀 Quick Start Commands:")
    print("   python manage.py runserver          # Start development server")
    print("   python manage.py migrate            # Apply pending migrations")
    print("   python manage.py shell              # Django interactive shell")
    print("   python manage.py createsuperuser    # Create admin user")
    print("   python manage.py test               # Run test suite")
    
    print(f"\n📚 Available Documentation:")
    print("   📄 DATABASE_DESIGN_PRINCIPLES_VERIFICATION_COMPLETE.md")
    print("   📄 FINAL_PRD_COMPLIANCE_COMPLETE.md")
    print("   📄 PRODUCTION_DEPLOYMENT_APPROVED.md")
    
    print(f"\n🎉 AgriConnect is ready for development!")

if __name__ == "__main__":
    main()
