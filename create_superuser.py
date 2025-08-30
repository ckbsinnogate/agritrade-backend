#!/usr/bin/env python
"""
Create Django superuser for AgriConnect
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@agriconnect.com',
        password='password123'
    )
    print("✅ Superuser 'admin' created successfully!")
    print("   Username: admin")
    print("   Email: admin@agriconnect.com")
    print("   Password: password123")
else:
    print("ℹ️  Superuser 'admin' already exists")
