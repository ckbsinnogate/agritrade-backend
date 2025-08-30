#!/usr/bin/env python
"""
Manually create weather tables
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db import connection
from django.core.management.color import no_style
from django.db import transaction

style = no_style()

print("Creating weather tables manually...")

sql_statements = [
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
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS weather_weatherlocation_name_region_idx 
    ON weather_weatherlocation (name, region);
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS weather_weatherforecast_location_date_idx 
    ON weather_weatherforecast (location_id, forecast_date);
    """
]

with transaction.atomic():
    cursor = connection.cursor()
    for sql in sql_statements:
        try:
            cursor.execute(sql)
            print(f"✅ Executed: {sql[:50]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

print("Weather tables creation completed!")

# Insert migration record
try:
    cursor.execute("""
        INSERT OR IGNORE INTO django_migrations (app, name, applied) 
        VALUES ('weather', '0001_initial', datetime('now'))
    """)
    print("✅ Migration record inserted")
except Exception as e:
    print(f"Migration record error: {e}")

print("Setup complete!")
