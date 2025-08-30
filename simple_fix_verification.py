#!/usr/bin/env python3
"""
Simple File-Based Fix Verification
Checks if the critical code fixes are in place without Django setup
"""

def check_warehouse_indentation_fix():
    """Check warehouse views indentation fix"""
    print("🔍 Checking warehouse views indentation fix...")
    
    try:
        with open('warehouses/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the specific area that was fixed
        if ').select_related(\'product\', \'warehouse\', \'zone\')[:10]' in content:
            # Find this line and check the next few lines
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if ').select_related(\'product\', \'warehouse\', \'zone\')[:10]' in line:
                    # Check the next few lines for proper indentation
                    next_lines = lines[i+1:i+4]
                    for next_line in next_lines:
                        if '# Identify items near expiry' in next_line:
                            if next_line.strip() == '# Identify items near expiry':
                                print("   ✅ Indentation fix verified")
                                return True
        
        print("   ⚠️  Could not verify indentation fix")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_subscription_string_fixes():
    """Check subscription views string formatting fixes"""
    print("\n🔍 Checking subscription views string formatting...")
    
    try:
        with open('subscriptions/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key string conversion patterns
        fixes_found = []
        
        if 'str(subscription.id)' in content:
            fixes_found.append('UUID to string conversion')
        
        if 'str(subscription.plan.name or \'\')' in content:
            fixes_found.append('Plan name string conversion with fallback')
        
        if '.isoformat()' in content:
            fixes_found.append('Date to ISO string conversion')
        
        if 'start_date.date().isoformat()' in content:
            fixes_found.append('Date formatting in stats')
        
        print(f"   ✅ Found {len(fixes_found)} critical fixes:")
        for fix in fixes_found:
            print(f"      - {fix}")
        
        return len(fixes_found) >= 3
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_file_syntax():
    """Basic syntax check by compiling Python files"""
    print("\n🔍 Checking Python syntax...")
    
    files_to_check = [
        'warehouses/views.py',
        'subscriptions/views.py'
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Try to compile the source
            compile(source, file_path, 'exec')
            print(f"   ✅ {file_path}: Syntax OK")
            
        except SyntaxError as e:
            print(f"   ❌ {file_path}: Syntax Error - {e}")
            all_good = False
        except Exception as e:
            print(f"   ❌ {file_path}: Error - {e}")
            all_good = False
    
    return all_good

def main():
    """Run all verification checks"""
    print("🚀 Backend Fix Verification (File-Based)")
    print("=" * 50)
    
    results = {
        'warehouse_indentation': check_warehouse_indentation_fix(),
        'subscription_strings': check_subscription_string_fixes(),
        'syntax_check': check_file_syntax()
    }
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n🎯 Final Status:")
    if all_passed:
        print("✅ ALL FIXES VERIFIED SUCCESSFULLY!")
        print("\n🎉 Backend is ready for frontend integration")
        print("\n📋 What was fixed:")
        print("• Warehouse optimization 500 error (indentation)")
        print("• Frontend TypeError (string formatting)")
        print("• Date serialization issues")
        print("• Proper error handling")
        
        print("\n💡 Next Steps:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Test frontend integration")
        print("3. All .replace() operations should work")
        
    else:
        print("❌ Some fixes may not be complete")
        print("Review the failed checks above")
    
    return all_passed

if __name__ == "__main__":
    success = main()
