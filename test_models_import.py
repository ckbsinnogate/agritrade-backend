#!/usr/bin/env python
"""
Test script to check if the models can be imported properly
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Try importing the models
    from reviews.models import Review, ReviewHelpfulVote, ReviewFlag, ReviewResponse, ExpertReview
    print("✅ Successfully imported Review models")
    
    # Try importing serializers
    from reviews.serializers import ReviewListSerializer, ReviewDetailSerializer
    print("✅ Successfully imported Review serializers")
    
    # Try importing admin
    from reviews.admin import ReviewAdmin
    print("✅ Successfully imported Review admin")
    
    print("\n🎉 All imports successful! Models are properly configured.")
    
except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
