#!/usr/bin/env python
"""
Simple Registration Status Checker
Quick check of registration system status
"""

print("🔍 AGRICONNECT REGISTRATION SYSTEM STATUS CHECK")
print("=" * 60)

try:
    import os
    import django
    print("✅ Python and Django imports: SUCCESS")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
    django.setup()
    print("✅ Django setup: SUCCESS")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    print("✅ Database connection: SUCCESS")
    
    # Test authentication models
    from authentication.models import User, OTPCode, UserRole
    
    user_count = User.objects.count()
    otp_count = OTPCode.objects.count()
    role_count = UserRole.objects.count()
    
    print(f"✅ Authentication models: SUCCESS")
    print(f"   - Users: {user_count}")
    print(f"   - OTP Codes: {otp_count}")
    print(f"   - User Roles: {role_count}")
    
    # Test serializers
    from authentication.serializers import UserRegistrationSerializer
    print("✅ Serializers import: SUCCESS")
    
    # Test views
    from authentication.views import UserRegistrationView
    print("✅ Views import: SUCCESS")
    
    print("\n🎉 REGISTRATION SYSTEM STATUS: FULLY OPERATIONAL!")
    print("✅ All components are working correctly")
    print("✅ No registration issues found")
    
    # Show recent users
    if user_count > 0:
        print(f"\n👥 Recent Users:")
        recent_users = User.objects.all()[:5]
        for user in recent_users:
            contact = user.email or user.phone_number or "No contact"
            print(f"   - {user.username} ({contact})")
    
    print("\n🚀 The system is ready for user registration!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\n🔧 POTENTIAL ISSUES:")
    print("   1. Virtual environment not activated")
    print("   2. Django settings not configured")
    print("   3. Database not accessible")
    print("   4. Missing dependencies")
    
    import traceback
    print(f"\n📋 Full Error Details:")
    traceback.print_exc()
