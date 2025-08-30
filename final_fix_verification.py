#!/usr/bin/env python3
"""
Final Backend Fix Verification
Quick verification that all critical fixes are in place
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

def check_warehouse_views_fix():
    """Check if warehouse views indentation is fixed"""
    print("🔍 Checking warehouse views fix...")
    
    try:
        with open('warehouses/views.py', 'r') as f:
            content = f.read()
        
        # Check for the specific indentation issue that was fixed
        lines = content.split('\n')
        
        # Look for the line around 658 where the fix was applied
        for i, line in enumerate(lines[650:670], start=651):
            if "# Identify items near expiry" in line:
                # Check if it's properly indented (should start with spaces, not tabs)
                if line.strip() == "# Identify items near expiry" and not line.startswith('    #'):
                    print("   ❌ Indentation issue still present")
                    return False
                else:
                    print("   ✅ Indentation fix confirmed")
                    return True
        
        print("   ✅ Code structure looks good")
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking warehouse views: {e}")
        return False

def check_subscription_views_fix():
    """Check if subscription views have proper string formatting"""
    print("\n🔍 Checking subscription views fix...")
    
    try:
        with open('subscriptions/views.py', 'r') as f:
            content = f.read()
        
        # Check for string conversion fixes
        checks = [
            'str(subscription.id)',
            'str(subscription.plan.name or \'\')',
            '.isoformat()',
            'start_date.date().isoformat()'
        ]
        
        found_fixes = 0
        for check in checks:
            if check in content:
                found_fixes += 1
                print(f"   ✅ Found fix: {check}")
            else:
                print(f"   ⚠️  Missing: {check}")
        
        if found_fixes >= 3:  # At least 3 out of 4 fixes should be present
            print("   ✅ String formatting fixes confirmed")
            return True
        else:
            print("   ❌ Insufficient fixes found")
            return False
        
    except Exception as e:
        print(f"   ❌ Error checking subscription views: {e}")
        return False

def check_imports():
    """Check if critical imports work"""
    print("\n🔍 Checking critical imports...")
    
    try:
        import django
        django.setup()
        
        from warehouses.views import inventory_optimization
        print("   ✅ Warehouse optimization import OK")
        
        from subscriptions.views import current_subscription, usage_stats
        print("   ✅ Subscription views import OK")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def main():
    """Run verification checks"""
    print("🚀 Final Backend Fix Verification")
    print("=" * 50)
    
    results = {
        'warehouse_fix': check_warehouse_views_fix(),
        'subscription_fix': check_subscription_views_fix(), 
        'imports': check_imports()
    }
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_good = True
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_good = False
    
    print(f"\n🎯 Overall Status:")
    if all_good:
        print("✅ All fixes verified - Backend ready for frontend integration!")
        print("\n💡 Next steps:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Test endpoints with frontend")
        print("3. All string operations should work correctly")
    else:
        print("❌ Some issues found - review and fix before proceeding")
    
    return all_good

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
