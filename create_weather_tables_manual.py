#!/usr/bin/env python
"""
Manual Weather Table Creation Script
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db import connection
from weather.models import WeatherLocation, CurrentWeather, WeatherAlert, WeatherForecast

def create_weather_tables():
    """Create weather tables manually"""
    print("🔨 Creating Weather Tables Manually...")
    
    try:
        # Force create tables using Django's schema editor
        from django.db import connection
        from django.core.management.color import no_style
        from django.core.management.sql import sql_create_index
        
        with connection.schema_editor() as schema_editor:
            # Create tables for each model
            schema_editor.create_model(WeatherLocation)
            print("✅ WeatherLocation table created")
            
            schema_editor.create_model(CurrentWeather) 
            print("✅ CurrentWeather table created")
            
            schema_editor.create_model(WeatherAlert)
            print("✅ WeatherAlert table created")
            
            schema_editor.create_model(WeatherForecast)
            print("✅ WeatherForecast table created")
        
        print("🎉 All weather tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def test_table_creation():
    """Test if tables were created by inserting sample data"""
    print("\n🧪 Testing Table Creation...")
    
    try:
        from decimal import Decimal
        
        # Create a test location
        location = WeatherLocation.objects.create(
            name="Test Location",
            latitude=Decimal('5.6037'),
            longitude=Decimal('-0.1870'),
            region="Test Region"
        )
        print("✅ Test location created successfully")
        
        # Create test weather data
        weather = CurrentWeather.objects.create(
            location=location,
            temperature=Decimal('28.5'),
            humidity=Decimal('75.0'),
            weather_condition='Sunny',
            rainfall_prediction=Decimal('15.0'),
            wind_speed=Decimal('10.0'),
            pressure=Decimal('1013.25'),
            visibility=Decimal('10.0'),
            uv_index=5
        )
        print("✅ Test weather data created successfully")
        
        # Clean up test data
        weather.delete()
        location.delete()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Table test failed: {e}")
        return False

if __name__ == "__main__":
    print("🌤️ WEATHER TABLE CREATION SCRIPT")
    print("=" * 40)
    
    # Create tables
    creation_success = create_weather_tables()
    
    if creation_success:
        # Test tables
        test_success = test_table_creation()
        
        if test_success:
            print("\n🎯 SUCCESS: Weather tables are ready!")
            print("The weather endpoint should now work correctly.")
        else:
            print("\n⚠️ Tables created but testing failed")
    else:
        print("\n❌ FAILED: Could not create weather tables")
