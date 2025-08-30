#!/usr/bin/env python3
"""
Check database tables
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db import connection

def check_tables():
    cursor = connection.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%financial%'")
    tables = cursor.fetchall()
    print('Financial tables:')
    for table in tables:
        print(f'  - {table[0]}')
    
    # Also check migration status
    cursor.execute("SELECT * FROM django_migrations WHERE app = 'financial'")
    migrations = cursor.fetchall()
    print('\nFinancial migrations:')
    for migration in migrations:
        print(f'  - {migration[1]}: {migration[2]}')

if __name__ == '__main__':
    check_tables()
