#!/usr/bin/env python
"""
Check Weather Tables Script
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db import connection

def check_weather_tables():
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'weather_%'")
    tables = cursor.fetchall()
    print("Weather tables found:", tables)
    
    # Also check all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = cursor.fetchall()
    weather_related = [table for table in all_tables if 'weather' in table[0].lower()]
    print("All weather-related tables:", weather_related)

if __name__ == "__main__":
    check_weather_tables()
