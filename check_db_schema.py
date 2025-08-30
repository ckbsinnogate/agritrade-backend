#!/usr/bin/env python
"""
Check database schema for PaymentGateway table
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
django.setup()

from django.db import connection

def check_schema():
    cursor = connection.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name LIKE '%payment%'
    """)
    tables = cursor.fetchall()
    print('Payment-related tables:')
    for table in tables:
        print(f'  {table[0]}')
    
    print()
    
    # Check PaymentGateway table structure
    cursor.execute("""
        SELECT column_name, data_type, numeric_precision, numeric_scale, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'payments_paymentgateway'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    
    if columns:
        print('PaymentGateway table schema:')
        for col in columns:
            col_name, data_type, precision, scale, max_length = col
            if precision is not None:
                print(f'  {col_name}: {data_type}({precision},{scale})')
                if col_name == 'transaction_fee_percentage':
                    max_val = 10**(precision - scale) - 10**(-scale)
                    print(f'    --> Max value: {max_val}')
            elif max_length is not None:
                print(f'  {col_name}: {data_type}({max_length})')
            else:
                print(f'  {col_name}: {data_type}')
    else:
        print('PaymentGateway table not found')

if __name__ == '__main__':
    check_schema()
