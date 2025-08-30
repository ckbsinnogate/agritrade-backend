#!/usr/bin/env python
"""
Test phone number registration functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User
from authentication.serializers import UserRegistrationSerializer

def test_phone_registration():
    """Test phone number registration"""
    
    print("🧪 TESTING PHONE NUMBER REGISTRATION")
    print("=" * 50)
    
    # Test data
    test_phone = "+233273735501"  # Different number to avoid conflicts
    test_password = "testpass123"
    
    try:
        # 1. Test User Manager directly
        print("\n1. Testing UserManager.create_user()...")
        try:
            user = User.objects.create_user(
                identifier=test_phone,
                password=test_password,
                roles=['FARMER']
            )
            print(f"   ✅ User created via manager")
            print(f"   Phone: {user.phone_number}")
            print(f"   Username: {user.username}")
            print(f"   Is verified: {user.is_verified}")
            
            # Clean up
            user.delete()
            print("   🗑️ Test user deleted")
            
        except Exception as e:
            print(f"   ❌ Manager creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # 2. Test Registration Serializer
        print("\n2. Testing Registration Serializer...")
        try:
            registration_data = {
                'identifier': test_phone,
                'password': test_password,
                'confirm_password': test_password,
                'first_name': 'Test',
                'last_name': 'User',
                'roles': ['FARMER']
            }
            
            serializer = UserRegistrationSerializer(data=registration_data)
            if serializer.is_valid():
                user = serializer.save()
                print(f"   ✅ User created via serializer")
                print(f"   Phone: {user.phone_number}")
                print(f"   Username: {user.username}")
                
                # Clean up
                user.delete()
                print("   🗑️ Test user deleted")
            else:
                print(f"   ❌ Serializer validation failed: {serializer.errors}")
                
        except Exception as e:
            print(f"   ❌ Serializer creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Test normalize_identifier method
        print("\n3. Testing identifier normalization...")
        try:
            from authentication.models import UserManager
            manager = UserManager()
            
            test_cases = [
                "+233273735500",
                "0273735500",
                "233273735500",
                "test@example.com"
            ]
            
            for test_case in test_cases:
                normalized = manager._normalize_identifier(test_case)
                print(f"   Input: {test_case} -> Output: {normalized}")
                
        except Exception as e:
            print(f"   ❌ Normalization failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("🎯 REGISTRATION TEST SUMMARY")
        print("✅ Check results above for any issues")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_phone_registration()
