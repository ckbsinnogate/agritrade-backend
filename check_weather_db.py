#!/usr/bin/env python
"""
Check weather tables in database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'weather_%';")
tables = cursor.fetchall()
print("Weather tables found:", tables)

# Check if django_migrations table shows weather migrations
cursor.execute("SELECT * FROM django_migrations WHERE app='weather';")
migrations = cursor.fetchall()
print("Weather migrations in database:", migrations)
