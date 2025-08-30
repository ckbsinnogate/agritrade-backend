#!/usr/bin/env python3
"""
Django Admin Timezone Diagnostic
Check for timezone field references in User admin
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

def diagnose_admin_timezone_issue():
    print("🔍 DJANGO ADMIN TIMEZONE DIAGNOSTIC")
    print("=" * 50)
    
    # Check User model fields
    print("1. Checking User model fields:")
    user_fields = [field.name for field in User._meta.get_fields()]
    if 'timezone' in user_fields:
        print("   ❌ User model HAS timezone field - this is the problem!")
        print(f"   User fields: {user_fields}")
    else:
        print("   ✅ User model does NOT have timezone field")
        print(f"   User has {len(user_fields)} fields")
    
    # Check admin registration
    print("\n2. Checking User admin registration:")
    if User in admin.site._registry:
        user_admin = admin.site._registry[User]
        print(f"   ✅ User admin class: {user_admin.__class__.__name__}")
        print(f"   ✅ Admin module: {user_admin.__class__.__module__}")
        
        # Check fieldsets
        print("\n3. Checking admin fieldsets:")
        if hasattr(user_admin, 'fieldsets') and user_admin.fieldsets:
            for i, (fieldset_name, fieldset_config) in enumerate(user_admin.fieldsets):
                fields = fieldset_config.get('fields', ())
                print(f"   Fieldset {i+1}: {fieldset_name}")
                print(f"      Fields: {fields}")
                
                if 'timezone' in fields:
                    print(f"   ❌ FOUND TIMEZONE FIELD in '{fieldset_name}' fieldset!")
                    return False
                else:
                    print(f"   ✅ No timezone field in '{fieldset_name}'")
        else:
            print("   No fieldsets defined")
    else:
        print("   ❌ User model NOT registered in admin")
        return False
    
    print("\n4. Result:")
    print("   ✅ No timezone field references found in admin configuration")
    return True

if __name__ == "__main__":
    success = diagnose_admin_timezone_issue()
    if success:
        print("\n🎉 Admin configuration appears correct!")
    else:
        print("\n❌ Admin configuration has timezone field issues!")
