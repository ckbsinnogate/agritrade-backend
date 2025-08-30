#!/usr/bin/env python
"""
AgriConnect Database Setup Script
Creates PostgreSQL database for the AgriConnect API using default postgres user
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_database():
    """Create PostgreSQL database for AgriConnect"""
    try:
        # Connect to PostgreSQL as superuser (postgres)
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",  # Default PostgreSQL superuser
            password="password",  # Change this to your PostgreSQL password
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Drop database if exists (for clean setup)
        print("Dropping existing database if it exists...")
        try:
            cursor.execute("DROP DATABASE IF EXISTS agriconnect_db;")
            print("✅ Existing database dropped")
        except Exception as e:
            print(f"ℹ️  No existing database to drop: {e}")
        
        # Create database
        print("Creating database 'agriconnect_db'...")
        cursor.execute("CREATE DATABASE agriconnect_db OWNER postgres;")
        print("✅ Database 'agriconnect_db' created successfully")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database to enable PostGIS
        print("Enabling PostGIS extension...")
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",
            database="agriconnect_db"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            print("✅ PostGIS extension enabled successfully")
        except Exception as e:
            print(f"⚠️  Could not enable PostGIS: {e}")
            print("   Geographic features may not work properly")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database setup completed successfully!")
        print("   Database: agriconnect_db")
        print("   User: postgres")
        print("   Host: localhost")
        print("   Port: 5432")
        
    except psycopg2.Error as e:
        print(f"❌ Database setup failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. You have superuser access (default user 'postgres')")
        print("3. Update the password in this script to match your PostgreSQL setup")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
