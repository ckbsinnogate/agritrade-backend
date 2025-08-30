"""
Quick Superuser Creation Fix for AgriConnect
Fixes the superuser creation issue with dual authentication
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from authentication.models import UserRole

User = get_user_model()

def create_superuser():
    """Create a superuser with phone number"""
    
    print("🌍 AgriConnect Superuser Creation")
    print("=" * 40)
    
    # Check if superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superuser already exists!")
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            print(f"   - {user.username} ({user.email or user.phone_number})")
        return
    
    # Get input
    identifier = input("Enter email or phone number (+233273735500): ").strip()
    if not identifier:
        identifier = "+233273735500"  # Default
    
    password = input("Enter password (default: admin123): ").strip()
    if not password:
        password = "admin123"  # Default
    
    try:
        # Create superuser
        if '@' in identifier:
            # Email superuser
            user = User.objects.create_superuser(
                username=identifier,
                email=identifier,
                password=password,
                first_name="Admin",
                last_name="User"
            )
        else:
            # Phone superuser
            user = User.objects.create_superuser(
                username=identifier,
                password=password,
                first_name="Admin", 
                last_name="User"
            )
        
        print(f"✅ Superuser created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email or 'Not set'}")
        print(f"   Phone: {user.phone_number or 'Not set'}")
        print(f"   Roles: {[role.name for role in user.roles.all()]}")
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        print(f"   Full error: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    create_superuser()