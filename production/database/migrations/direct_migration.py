"""
Direct Schema Migration - luxeflow_ai to fte_db

This script extracts schema from luxeflow_ai and creates it in fte_db.
Runs directly against local PostgreSQL (pgAdmin).

Usage:
    python direct_migration.py
"""

import subprocess
import sys
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

PG_USER = "postgres"
PG_PASSWORD = "postgres"
PG_HOST = "localhost"
PG_PORT = "5432"

SOURCE_DB = "luxeFlow_ai"
TARGET_DB = "fte_db"

# ============================================================================


def run_psql_command(database, sql_command):
    """Run a psql command."""
    os.environ['PGPASSWORD'] = PG_PASSWORD
    
    cmd = [
        'psql',
        '-U', PG_USER,
        '-h', PG_HOST,
        '-p', PG_PORT,
        '-d', database,
        '-c', sql_command
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        print("ERROR: psql not found. Please install PostgreSQL or add it to PATH.")
        return False, "", "psql not found"
    except Exception as e:
        return False, "", str(e)


def run_psql_file(database, sql_file):
    """Run a SQL file against database."""
    os.environ['PGPASSWORD'] = PG_PASSWORD
    
    cmd = [
        'psql',
        '-U', PG_USER,
        '-h', PG_HOST,
        '-p', PG_PORT,
        '-d', database,
        '-f', sql_file,
        '--echo-errors'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def export_schema_from_database(database, output_file):
    """Export schema from a database using pg_dump."""
    os.environ['PGPASSWORD'] = PG_PASSWORD
    
    cmd = [
        'pg_dump',
        '-U', PG_USER,
        '-h', PG_HOST,
        '-p', PG_PORT,
        '-s',  # Schema only
        '-f', output_file,
        database
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✓ Schema exported to {output_file}")
            return True
        else:
            print(f"✗ Export failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("ERROR: pg_dump not found. Please install PostgreSQL.")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def create_database_if_not_exists(database):
    """Create database if it doesn't exist."""
    os.environ['PGPASSWORD'] = PG_PASSWORD
    
    # First check if database exists
    check_cmd = [
        'psql',
        '-U', PG_USER,
        '-h', PG_HOST,
        '-p', PG_PORT,
        '-d', 'postgres',
        '-c',
        f"SELECT 1 FROM pg_database WHERE datname = '{database}'"
    ]
    
    try:
        result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
        if '1 row' in result.stdout:
            print(f"✓ Database {database} already exists")
            return True
        
        # Create database
        create_cmd = [
            'psql',
            '-U', PG_USER,
            '-h', PG_HOST,
            '-p', PG_PORT,
            '-d', 'postgres',
            '-c',
            f'CREATE DATABASE {database}'
        ]
        
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Database {database} created")
            return True
        else:
            print(f"✗ Failed to create database: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Main migration function."""
    print("="*70)
    print("Database Schema Migration")
    print(f"  Source: {SOURCE_DB}")
    print(f"  Target: {TARGET_DB}")
    print("="*70)
    print()
    
    # Step 1: Check psql is available
    print("Step 1: Checking PostgreSQL tools...")
    os.environ['PGPASSWORD'] = PG_PASSWORD
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✓ {result.stdout.strip()}")
        else:
            print("   ✗ psql not found")
            print("\n   Please ensure PostgreSQL is installed and in PATH.")
            print("   Typical path: C:\\Program Files\\PostgreSQL\\16\\bin")
            return 1
    except FileNotFoundError:
        print("   ✗ psql not found")
        print("\n   Please ensure PostgreSQL is installed and in PATH.")
        print("   Typical path: C:\\Program Files\\PostgreSQL\\16\\bin")
        return 1
    
    # Step 2: Create target database
    print("\nStep 2: Creating target database...")
    if not create_database_if_not_exists(TARGET_DB):
        print("\n   Trying to continue anyway...")
    
    # Step 3: Export schema from source
    print("\nStep 3: Exporting schema from source database...")
    schema_file = "luxeflow_schema_export.sql"
    
    if not export_schema_from_database(SOURCE_DB, schema_file):
        print("\n   ERROR: Could not export schema")
        print("   Make sure:")
        print(f"   - Database '{SOURCE_DB}' exists")
        print(f"   - PostgreSQL is running on {PG_HOST}:{PG_PORT}")
        print(f"   - Password is correct ({PG_PASSWORD})")
        return 1
    
    # Step 4: Import schema to target
    print("\nStep 4: Importing schema to target database...")
    success, stdout, stderr = run_psql_file(TARGET_DB, schema_file)
    
    if success:
        print("✓ Schema imported successfully!")
    else:
        print("⚠ Some errors occurred during import:")
        print(stderr[:500] if stderr else "Unknown error")
    
    # Step 5: Export data (optional)
    print("\nStep 5: Export data?")
    response = input("   Do you want to migrate data as well? (y/n): ").lower()
    
    if response == 'y':
        data_file = "luxeflow_data_export.sql"
        print("\n   Exporting data...")
        
        os.environ['PGPASSWORD'] = PG_PASSWORD
        cmd = [
            'pg_dump',
            '-U', PG_USER,
            '-h', PG_HOST,
            '-p', PG_PORT,
            '-a',  # Data only
            '-f', data_file,
            SOURCE_DB
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"✓ Data exported to {data_file}")
                
                # Import data
                print("\n   Importing data to target...")
                success, stdout, stderr = run_psql_file(TARGET_DB, data_file)
                
                if success:
                    print("✓ Data imported successfully!")
                else:
                    print(f"⚠ Data import had some errors: {stderr[:200]}")
            else:
                print(f"✗ Data export failed: {result.stderr}")
        except Exception as e:
            print(f"✗ Data migration failed: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("Migration Summary")
    print("="*70)
    print(f"  Schema file: {schema_file}")
    print(f"  Data file: {data_file if response == 'y' else 'Not exported'}")
    print(f"  Target database: {TARGET_DB}")
    print("\nYou can now connect to '{TARGET_DB}' using pgAdmin!")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
