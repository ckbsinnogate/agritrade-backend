#!/usr/bin/env python
"""
🏆 RUN DIFFERENTIATORS COMPLETION
Execute the complete differentiators implementation step by step
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

print("🚀 STARTING DIFFERENTIATORS COMPLETION")
print("=" * 60)

# Import the implementation script
try:
    exec(open('complete_differentiators.py').read())
    print("\n✅ Script executed successfully!")
except Exception as e:
    print(f"❌ Error executing script: {e}")
    import traceback
    traceback.print_exc()
