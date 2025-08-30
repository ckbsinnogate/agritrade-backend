#!/usr/bin/env python
"""
Simple test of frontend registration endpoint
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
sys.path.insert(0, os.path.abspath('.'))
django.setup()

print("🔧 Django setup complete")

try:
    from authentication.views import FrontendUserRegistrationView
    print("✅ Successfully imported FrontendUserRegistrationView")
    
    from authentication.frontend_serializers import FrontendUserRegistrationSerializer
    print("✅ Successfully imported FrontendUserRegistrationSerializer")
    
    # Test creating an instance
    view = FrontendUserRegistrationView()
    print("✅ Successfully created view instance")
    
    # Test the generate_otp method
    otp = view.generate_otp()
    print(f"✅ Generated OTP: {otp}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("🎯 Test complete")
