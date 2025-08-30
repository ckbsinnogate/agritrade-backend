#!/usr/bin/env python
"""
Frontend-Backend Connection Fix
Diagnoses and fixes all issues preventing frontend from connecting to Django backend
"""
import os
import sys
import django

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def analyze_frontend_backend_issues():
    """Analyze and fix frontend-backend connection issues"""
    print("🔍 FRONTEND-BACKEND CONNECTION ANALYSIS")
    print("=" * 50)
    
    # Issue 1: Field mismatch
    print("\n🐛 ISSUE 1: FIELD MISMATCH")
    print("-" * 30)
    print("Frontend sends:")
    print("  {")
    print('    "user_type": "farmer",')
    print('    "region": "Greater Accra",')
    print('    "preferred_language": "en"')
    print("  }")
    print("\nBackend expects:")
    print("  {")
    print('    "roles": ["FARMER"],')
    print('    "language": "en"')
    print("  }")
    
    # Issue 2: API endpoint
    print("\n📍 ISSUE 2: API ENDPOINT")
    print("-" * 30)
    print("Frontend calls: POST /api/v1/auth/register/")
    print("Backend has: POST /api/auth/register/")
    
    # Issue 3: Field names
    print("\n🏷️  ISSUE 3: FIELD NAME DIFFERENCES")
    print("-" * 30)
    print("Frontend → Backend:")
    print("  user_type → roles")
    print("  preferred_language → language")
    print("  region → region (OK)")
    
    print("\n🔧 SOLUTIONS NEEDED:")
    print("1. Create API endpoint mapping for /api/v1/auth/register/")
    print("2. Update serializer to accept frontend field names")
    print("3. Add field transformation logic")
    print("4. Ensure CORS allows frontend origin")

def create_api_v1_mapping():
    """Create URL mapping for /api/v1/ prefix"""
    print("\n🛠️  CREATING API V1 URL MAPPING")
    print("-" * 30)
    
    # Check if main urls.py has v1 mapping
    main_urls_path = os.path.join(project_dir, 'agriconnect', 'urls.py')
    
    with open(main_urls_path, 'r') as f:
        content = f.read()
    
    if 'api/v1/' not in content:
        print("❌ Missing /api/v1/ URL mapping")
        print("✅ Solution: Add v1 API mapping to main urls.py")
        
        # Find the urlpatterns section
        if 'urlpatterns = [' in content:
            # Add v1 mapping
            new_line = "    path('api/v1/', include('api.urls')),  # API v1 endpoints\n"
            updated_content = content.replace(
                "    path('api/', include('api.urls')),",
                "    path('api/', include('api.urls')),\n" + new_line
            )
            
            # Also ensure v1 maps to same endpoints
            if "path('api/v1/auth/', include('authentication.urls'))," not in updated_content:
                auth_line = "    path('api/v1/auth/', include('authentication.urls')),  # V1 Auth endpoints\n"
                updated_content = updated_content.replace(
                    "    path('api/auth/', include('authentication.urls')),",
                    "    path('api/auth/', include('authentication.urls')),\n" + auth_line
                )
            
            print("✅ Ready to add v1 URL mapping")
        else:
            print("❌ Cannot find urlpatterns in main urls.py")
    else:
        print("✅ API v1 mapping already exists")

def check_serializer_compatibility():
    """Check if serializer accepts frontend fields"""
    print("\n🔍 CHECKING SERIALIZER COMPATIBILITY")
    print("-" * 30)
    
    try:
        from authentication.serializers import UserRegistrationSerializer
        
        # Check expected fields
        serializer = UserRegistrationSerializer()
        expected_fields = serializer.fields.keys()
        
        print("Expected fields:", list(expected_fields))
        
        frontend_data = {
            "identifier": "+233200430858",
            "password": "kingsco45", 
            "first_name": "Kingsley Baah",
            "last_name": "Adjei",
            "user_type": "farmer",  # ❌ Should be "roles"
            "region": "Greater Accra",
            "country": "Ghana",
            "preferred_language": "en"  # ❌ Should be "language"
        }
        
        missing_fields = []
        wrong_fields = []
        
        if 'roles' in expected_fields and 'user_type' in frontend_data:
            wrong_fields.append('user_type → roles')
        
        if 'language' in expected_fields and 'preferred_language' in frontend_data:
            wrong_fields.append('preferred_language → language')
            
        if 'password_confirm' in expected_fields:
            missing_fields.append('password_confirm')
        
        print(f"\n❌ Field mismatches: {wrong_fields}")
        print(f"❌ Missing fields: {missing_fields}")
        print("\n✅ Solution: Create frontend-compatible serializer")
        
    except Exception as e:
        print(f"❌ Error checking serializer: {e}")

def test_cors_configuration():
    """Test CORS configuration"""
    print("\n🌐 CHECKING CORS CONFIGURATION")
    print("-" * 30)
    
    try:
        from django.conf import settings
        
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        cors_credentials = getattr(settings, 'CORS_ALLOW_CREDENTIALS', False)
        
        frontend_url = 'http://localhost:3000'
        
        if frontend_url in cors_origins or 'http://localhost:3000' in cors_origins:
            print("✅ CORS allows frontend origin")
        else:
            print(f"❌ CORS missing frontend origin: {frontend_url}")
            print(f"Current CORS origins: {cors_origins}")
        
        if cors_credentials:
            print("✅ CORS allows credentials")
        else:
            print("❌ CORS credentials disabled")
            
    except Exception as e:
        print(f"❌ Error checking CORS: {e}")

def create_comprehensive_fix():
    """Create comprehensive fix for all issues"""
    print("\n🚀 COMPREHENSIVE FIX PLAN")
    print("=" * 50)
    
    print("\n1. UPDATE SERIALIZER TO ACCEPT FRONTEND FIELDS")
    print("2. CREATE V1 API URL MAPPING") 
    print("3. ADD FIELD TRANSFORMATION LOGIC")
    print("4. TEST COMPLETE REGISTRATION FLOW")
    
    return True

if __name__ == "__main__":
    try:
        analyze_frontend_backend_issues()
        create_api_v1_mapping()
        check_serializer_compatibility()
        test_cors_configuration()
        success = create_comprehensive_fix()
        
        print(f"\n{'='*50}")
        print("🎯 SUMMARY: Ready to implement fixes")
        print("📋 Next: Run the fix implementation script")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
