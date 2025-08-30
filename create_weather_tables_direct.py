#!/usr/bin/env python
"""
Manual Weather Tables Creation
Create weather tables directly in the database
"""

import os
import django
import sys
from django.db import connection

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def create_weather_tables():
    """Create weather tables manually"""
    print("🏗️ Creating Weather Tables Manually")
    print("=" * 50)
    
    cursor = connection.cursor()
    
    # SQL to create weather tables
    sql_commands = [
        # WeatherLocation table
        """
        CREATE TABLE IF NOT EXISTS "weather_weatherlocation" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "name" varchar(100) NOT NULL,
            "latitude" decimal NOT NULL,
            "longitude" decimal NOT NULL,
            "region" varchar(50) NOT NULL,
            "created_at" datetime NOT NULL
        );
        """,
        
        # CurrentWeather table
        """
        CREATE TABLE IF NOT EXISTS "weather_currentweather" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "temperature" decimal NOT NULL,
            "humidity" decimal NOT NULL,
            "weather_condition" varchar(100) NOT NULL,
            "rainfall_prediction" decimal NOT NULL,
            "wind_speed" decimal NOT NULL,
            "pressure" decimal NOT NULL,
            "visibility" decimal NOT NULL,
            "uv_index" integer NOT NULL,
            "last_updated" datetime NOT NULL,
            "location_id" bigint NOT NULL REFERENCES "weather_weatherlocation" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        """,
        
        # WeatherAlert table
        """
        CREATE TABLE IF NOT EXISTS "weather_weatheralert" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "alert_type" varchar(20) NOT NULL,
            "severity" varchar(10) NOT NULL,
            "title" varchar(200) NOT NULL,
            "message" text NOT NULL,
            "recommendations" text NOT NULL,
            "is_active" bool NOT NULL,
            "created_at" datetime NOT NULL,
            "expires_at" datetime NOT NULL,
            "location_id" bigint NOT NULL REFERENCES "weather_weatherlocation" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        """,
        
        # WeatherForecast table
        """
        CREATE TABLE IF NOT EXISTS "weather_weatherforecast" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "forecast_date" date NOT NULL,
            "temp_high" decimal NOT NULL,
            "temp_low" decimal NOT NULL,
            "condition" varchar(100) NOT NULL,
            "rainfall_probability" integer NOT NULL,
            "created_at" datetime NOT NULL,
            "location_id" bigint NOT NULL REFERENCES "weather_weatherlocation" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        """
    ]
    
    try:
        for i, sql in enumerate(sql_commands, 1):
            print(f"Creating table {i}/4...")
            cursor.execute(sql)
            
        # Create indexes
        index_commands = [
            'CREATE INDEX IF NOT EXISTS "weather_weatherlocation_name_region" ON "weather_weatherlocation" ("name", "region");',
            'CREATE INDEX IF NOT EXISTS "weather_currentweather_location_id" ON "weather_currentweather" ("location_id");',
            'CREATE INDEX IF NOT EXISTS "weather_weatheralert_location_id" ON "weather_weatheralert" ("location_id");',
            'CREATE INDEX IF NOT EXISTS "weather_weatherforecast_location_id" ON "weather_weatherforecast" ("location_id");',
        ]
        
        for idx_sql in index_commands:
            cursor.execute(idx_sql)
        
        # Insert sample data
        print("Adding sample weather data...")
        
        # Insert Accra location
        cursor.execute("""
            INSERT OR IGNORE INTO "weather_weatherlocation" 
            ("name", "latitude", "longitude", "region", "created_at")
            VALUES ('Accra', 5.6037, -0.1870, 'Greater Accra', datetime('now'))
        """)
        
        # Get the location ID
        cursor.execute("SELECT id FROM weather_weatherlocation WHERE name='Accra'")
        location_id = cursor.fetchone()[0]
        
        # Insert current weather
        cursor.execute("""
            INSERT OR REPLACE INTO "weather_currentweather"
            ("temperature", "humidity", "weather_condition", "rainfall_prediction", 
             "wind_speed", "pressure", "visibility", "uv_index", "last_updated", "location_id")
            VALUES (28.5, 75.0, 'Partly Cloudy', 15.0, 10.0, 1013.25, 10.0, 5, datetime('now'), ?)
        """, [location_id])
        
        connection.commit()
        
        print("✅ Weather tables created successfully!")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'weather_%'")
        tables = cursor.fetchall()
        print(f"📊 Created tables: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()

if __name__ == "__main__":
    success = create_weather_tables()
    sys.exit(0 if success else 1)
