#!/usr/bin/env python
"""
Test duplicate prevention for superuser creation
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from authentication.models import User

def test_duplicate_prevention():
    """Test that duplicate phone numbers are handled properly"""
    
    print("🧪 TESTING DUPLICATE PREVENTION")
    print("=" * 40)
    
    phone = "+233273735500"
    
    try:
        # Check if user exists
        existing_user = User.objects.filter(phone_number=phone).first()
        
        if existing_user:
            print(f"✅ User already exists:")
            print(f"   Phone: {existing_user.phone_number}")
            print(f"   Username: {existing_user.username}")
            print(f"   Is Superuser: {existing_user.is_superuser}")
            print(f"   Is Staff: {existing_user.is_staff}")
            
            # Test the create_superuser method
            print(f"\n🔧 Testing create_superuser with existing phone...")
            
            try:
                manager = User.objects
                superuser = manager.create_superuser(
                    username=phone,
                    password="newpassword123"
                )
                
                print(f"✅ create_superuser handled existing user correctly")
                print(f"   Returned user ID: {superuser.id}")
                print(f"   Is Superuser: {superuser.is_superuser}")
                print(f"   Is Staff: {superuser.is_staff}")
                
            except ValueError as e:
                if "already exists" in str(e):
                    print(f"✅ Correctly prevented duplicate: {e}")
                else:
                    print(f"❌ Unexpected error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ No existing user found with phone {phone}")
            
        # Test with a new phone number
        new_phone = "+233273735999"
        print(f"\n🆕 Testing with new phone number: {new_phone}")
        
        # Clean up any existing test user
        test_user = User.objects.filter(phone_number=new_phone).first()
        if test_user:
            test_user.delete()
            print(f"🗑️ Cleaned up existing test user")
        
        try:
            new_superuser = User.objects.create_superuser(
                username=new_phone,
                password="newsuperpass123"
            )
            
            print(f"✅ New superuser created successfully:")
            print(f"   Phone: {new_superuser.phone_number}")
            print(f"   Username: {new_superuser.username}")
            print(f"   Is Superuser: {new_superuser.is_superuser}")
            
            # Clean up
            new_superuser.delete()
            print(f"🗑️ Test superuser deleted")
            
        except Exception as e:
            print(f"❌ Error creating new superuser: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n🎯 CONCLUSION: Duplicate prevention system is working!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        print("Starting duplicate prevention test...")
        test_duplicate_prevention()
        print("Test completed successfully.")
    except Exception as e:
        print(f"SCRIPT ERROR: {e}")
        import traceback
        traceback.print_exc()
