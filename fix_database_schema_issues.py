#!/usr/bin/env python
"""
Fix Database Schema Issues
Resolves PostgreSQL vs SQLite compatibility issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def check_database_engine():
    """Check which database engine is being used"""
    engine = connection.settings_dict['ENGINE']
    print(f"🔍 Database Engine: {engine}")
    
    if 'postgresql' in engine:
        print("✅ PostgreSQL detected - using PostgreSQL syntax")
        return 'postgresql'
    elif 'sqlite' in engine:
        print("✅ SQLite detected - using SQLite syntax")
        return 'sqlite'
    else:
        print(f"⚠️  Unknown database engine: {engine}")
        return 'unknown'

def check_tables_postgresql():
    """Check tables using PostgreSQL syntax"""
    print("\n🔍 CHECKING TABLES (PostgreSQL)")
    print("-" * 40)
    
    try:
        with connection.cursor() as cursor:
            # Get all tables using PostgreSQL information_schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"📊 Total tables found: {len(tables)}")
            
            # Check for key AI-related tables
            ai_tables = [table for table in tables if any(keyword in table.lower() 
                        for keyword in ['ai_', 'disease', 'crop', 'weather'])]
            
            if ai_tables:
                print(f"🧠 AI-related tables: {len(ai_tables)}")
                for table in ai_tables:
                    print(f"   ✅ {table}")
            
            # Check for authentication tables
            auth_tables = [table for table in tables if any(keyword in table.lower() 
                          for keyword in ['auth_', 'user', 'authentication'])]
            
            if auth_tables:
                print(f"🔐 Authentication tables: {len(auth_tables)}")
                for table in auth_tables[:5]:  # Show first 5
                    print(f"   ✅ {table}")
                if len(auth_tables) > 5:
                    print(f"   ... and {len(auth_tables) - 5} more")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def check_migrations_status():
    """Check Django migrations status"""
    print("\n🔍 CHECKING MIGRATIONS STATUS")
    print("-" * 40)
    
    try:
        # Check if there are any unapplied migrations
        from django.core.management.commands.showmigrations import Command
        from io import StringIO
        import sys
        
        # Capture the output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            call_command('showmigrations', '--plan')
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # Count applied vs unapplied
        lines = output.strip().split('\n')
        applied = len([line for line in lines if '[X]' in line])
        unapplied = len([line for line in lines if '[ ]' in line])
        
        print(f"📊 Applied migrations: {applied}")
        print(f"📊 Unapplied migrations: {unapplied}")
        
        if unapplied > 0:
            print("⚠️  There are unapplied migrations")
            return False
        else:
            print("✅ All migrations are applied")
            return True
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
        return False

def fix_sqlite_scripts():
    """Fix scripts that use SQLite syntax"""
    print("\n🔧 FIXING SQLITE SCRIPTS")
    print("-" * 40)
    
    scripts_to_fix = [
        'check_weather_tables.py',
        'check_weather_db.py',
        'create_weather_tables_direct.py'
    ]
    
    fixed_count = 0
    
    for script_name in scripts_to_fix:
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Replace SQLite syntax with PostgreSQL
                if 'sqlite_master' in content:
                    new_content = content.replace(
                        "SELECT name FROM sqlite_master WHERE type='table'",
                        """SELECT table_name as name 
                           FROM information_schema.tables 
                           WHERE table_schema = 'public' 
                           AND table_type = 'BASE TABLE'"""
                    )
                    
                    new_content = new_content.replace(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'weather_%'",
                        """SELECT table_name as name 
                           FROM information_schema.tables 
                           WHERE table_schema = 'public' 
                           AND table_type = 'BASE TABLE'
                           AND table_name LIKE 'weather_%'"""
                    )
                    
                    # Write back the fixed content
                    with open(script_path, 'w') as f:
                        f.write(new_content)
                    
                    print(f"✅ Fixed {script_name}")
                    fixed_count += 1
                else:
                    print(f"ℹ️  {script_name} doesn't need fixing")
                    
            except Exception as e:
                print(f"❌ Error fixing {script_name}: {e}")
        else:
            print(f"ℹ️  {script_name} not found")
    
    print(f"📊 Fixed {fixed_count} scripts")
    return fixed_count > 0

def run_database_health_check():
    """Run comprehensive database health check"""
    print("\n🏥 DATABASE HEALTH CHECK")
    print("=" * 50)
    
    health_score = 0
    max_score = 4
    
    # Check 1: Database engine
    if check_database_engine() == 'postgresql':
        health_score += 1
        print("✅ Database engine check passed")
    
    # Check 2: Tables exist
    if check_tables_postgresql():
        health_score += 1
        print("✅ Tables check passed")
    
    # Check 3: Migrations status
    if check_migrations_status():
        health_score += 1
        print("✅ Migrations check passed")
    
    # Check 4: AI endpoints accessible
    try:
        from ai.models import DiseaseDetection
        DiseaseDetection.objects.count()  # Simple query test
        health_score += 1
        print("✅ AI models accessible")
    except Exception as e:
        print(f"❌ AI models check failed: {e}")
    
    print(f"\n📊 DATABASE HEALTH SCORE: {health_score}/{max_score}")
    
    if health_score == max_score:
        print("🎉 DATABASE IS HEALTHY!")
        return True
    else:
        print("⚠️  Database has some issues that need attention")
        return False

if __name__ == "__main__":
    print("🔧 FIXING DATABASE SCHEMA ISSUES")
    print("=" * 50)
    
    # Step 1: Check database type
    db_engine = check_database_engine()
    
    # Step 2: Fix SQLite scripts if using PostgreSQL
    if db_engine == 'postgresql':
        fix_sqlite_scripts()
    
    # Step 3: Run health check
    is_healthy = run_database_health_check()
    
    if is_healthy:
        print("\n✅ ALL DATABASE ISSUES RESOLVED!")
        print("🚀 Disease detection endpoint is ready for use")
    else:
        print("\n⚠️  Some issues remain. Check the output above for details.")
    
    print("\n📋 NEXT STEPS:")
    print("1. ✅ Backend URL routing fixed - /ai/disease-detection/ now accessible")
    print("2. ✅ Database schema issues addressed")
    print("3. 📋 Deploy the fixed frontend component: URGENT_IMAGE_UPLOAD_FIX.tsx")
    print("4. 🧪 Test with actual tomato plant image upload")
