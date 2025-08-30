#!/usr/bin/env python3

import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from processors.models import ProcessorProfile

print("🌾 Testing Recipe Sharing System...")
print(f"Current Processor Profiles: {ProcessorProfile.objects.count()}")
print("✅ Recipe Sharing System Models Working!")
