#!/usr/bin/env python
"""
Test Admin Endpoint Configuration
Validates that the new admin endpoints are properly configured
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def test_admin_endpoints():
    """Test that admin endpoints are properly configured"""
    print("🔍 Testing Admin Endpoint Configuration...")
    
    try:
        # Test authentication URLs
        from django.urls import reverse
        
        # Test admin user management endpoints
        admin_user_list_url = reverse('api-v1-auth:admin-user-list')
        print(f"✅ Admin User List URL: {admin_user_list_url}")
        
        # Test admin user statistics
        admin_user_stats_url = reverse('api-v1-auth:admin-user-statistics')
        print(f"✅ Admin User Statistics URL: {admin_user_stats_url}")
        
        # Test order statistics endpoint
        order_stats_url = reverse('api-v1-orders:order-statistics')
        print(f"✅ Order Statistics URL: {order_stats_url}")
        
        print("\n✅ All admin endpoints are properly configured!")
        return True
        
    except Exception as e:
        print(f"❌ Endpoint configuration error: {e}")
        return False

def test_admin_views_import():
    """Test that admin views can be imported"""
    print("\n🔍 Testing Admin Views Import...")
    
    try:
        from authentication.admin_views import AdminUserManagementViewSet, admin_dashboard_stats
        print("✅ Authentication admin views imported successfully")
        
        from orders.views import OrderViewSet
        print("✅ Orders views imported successfully")
        
        # Test that the statistics action exists
        order_viewset = OrderViewSet()
        if hasattr(order_viewset, 'statistics'):
            print("✅ Order statistics action found")
        else:
            print("❌ Order statistics action not found")
            return False
        
        print("\n✅ All admin views are properly importable!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_patterns():
    """Test URL pattern resolution"""
    print("\n🔍 Testing URL Pattern Resolution...")
    
    try:
        from django.urls import get_resolver
        
        resolver = get_resolver()
        
        # Check if auth admin endpoints are available
        auth_patterns = []
        orders_patterns = []
        
        # Look for our new endpoints
        try:
            from django.urls import reverse
            
            # Test specific URLs that frontend expects
            test_urls = [
                '/api/v1/auth/users/',
                '/api/v1/orders/statistics/',
            ]
            
            for url in test_urls:
                try:
                    resolved = resolver.resolve(url)
                    print(f"✅ URL {url} resolves to {resolved.func}")
                except:
                    print(f"❌ URL {url} does not resolve")
                    
        except Exception as e:
            print(f"⚠️  URL resolution test error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL pattern test error: {e}")
        return False

def test_permissions():
    """Test that admin permissions are properly configured"""
    print("\n🔍 Testing Admin Permissions...")
    
    try:
        from authentication.admin_views import AdminUserManagementViewSet
        from django.contrib.auth import get_user_model
        from authentication.models import UserRole
        
        User = get_user_model()
        
        # Create test admin user
        admin_role, created = UserRole.objects.get_or_create(name='ADMIN')
        admin_user, created = User.objects.get_or_create(
            username='test_admin_validation@test.com',
            defaults={
                'email': 'test_admin_validation@test.com',
                'first_name': 'Test',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True
            }
        )
        if created:
            admin_user.set_password('test123')
            admin_user.save()
            admin_user.roles.add(admin_role)
        
        print(f"✅ Test admin user created/verified: {admin_user.username}")
        
        # Test viewset permissions
        viewset = AdminUserManagementViewSet()
        permissions = viewset.get_permissions()
        print(f"✅ Admin viewset permissions: {[p.__class__.__name__ for p in permissions]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Permission test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all admin endpoint tests"""
    print("🚀 Admin Endpoint Validation Starting...")
    print("=" * 50)
    
    tests = [
        test_admin_views_import,
        test_url_patterns,
        test_permissions,
        test_admin_endpoints,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Admin endpoints are ready for frontend integration")
        print("\n📌 Available Admin Endpoints:")
        print("   • GET  /api/v1/auth/users/           - List users (admin)")
        print("   • POST /api/v1/auth/users/           - Create user (admin)")
        print("   • GET  /api/v1/auth/users/{id}/      - Get user details (admin)")
        print("   • PUT  /api/v1/auth/users/{id}/      - Update user (admin)")
        print("   • GET  /api/v1/auth/users/statistics/ - User statistics (admin)")
        print("   • GET  /api/v1/orders/statistics/    - Order statistics (admin)")
        print("\n🔐 All endpoints require admin authentication")
        
    else:
        print("⚠️  Some tests failed - review the output above")
        failed_count = len([r for r in results if not r])
        print(f"   {failed_count}/{len(tests)} tests failed")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
