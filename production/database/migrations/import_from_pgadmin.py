"""
Import database schema and data from pgAdmin/PostgreSQL.

This script helps migrate tables from an existing pgAdmin database
to the TechCorp Customer Success AI Agent database.

Usage:
    python import_from_pgadmin.py

Configuration:
    Edit the SOURCE_DB_* variables below with your pgAdmin database credentials.
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION - Edit these values with your pgAdmin database details
# ============================================================================

# Source Database (pgAdmin - your existing database)
SOURCE_DB_HOST = "localhost"
SOURCE_DB_PORT = 5432
SOURCE_DB_NAME = "your_database_name"  # Change this
SOURCE_DB_USER = "postgres"
SOURCE_DB_PASSWORD = "your_password"  # Change this

# Target Database (Project database from docker-compose)
TARGET_DB_HOST = "localhost"
TARGET_DB_PORT = 5432
TARGET_DB_NAME = "fte_db"
TARGET_DB_USER = "fte_user"
TARGET_DB_PASSWORD = "fte_password"

# Tables to migrate (leave empty for all tables)
TABLES_TO_MIGRATE = [
    # Add your table names here, e.g.:
    # "customers",
    # "products",
    # "orders",
]

# Migration mode
MIGRATE_SCHEMA_ONLY = False  # Set True to migrate only schema (no data)
MIGRATE_DATA_ONLY = False    # Set True to migrate only data (not schema)
DROP_EXISTING_TABLES = False # Set True to drop tables before migration

# ============================================================================


async def get_source_connection():
    """Get connection to source database (pgAdmin)."""
    return await asyncpg.connect(
        host=SOURCE_DB_HOST,
        port=SOURCE_DB_PORT,
        database=SOURCE_DB_NAME,
        user=SOURCE_DB_USER,
        password=SOURCE_DB_PASSWORD,
    )


async def get_target_connection():
    """Get connection to target database (project DB)."""
    return await asyncpg.connect(
        host=TARGET_DB_HOST,
        port=TARGET_DB_PORT,
        database=TARGET_DB_NAME,
        user=TARGET_DB_USER,
        password=TARGET_DB_PASSWORD,
    )


async def list_all_tables(source_conn):
    """List all tables in source database."""
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    tables = await source_conn.fetch(query)
    return [row['table_name'] for row in tables]


async def get_table_schema(source_conn, table_name):
    """Get CREATE TABLE statement for a table."""
    query = """
        SELECT pg_get_serial_sequence('public.' || $1, column_name) as sequence,
               column_name,
               data_type,
               is_nullable,
               column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = $1
        ORDER BY ordinal_position;
    """
    columns = await source_conn.fetch(query, table_name)
    
    # Get primary key info
    pk_query = """
        SELECT a.attname as column_name
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = $1::regclass AND i.indisprimary;
    """
    try:
        primary_keys = await source_conn.fetch(pk_query, table_name)
        pk_columns = [row['column_name'] for row in primary_keys]
    except Exception:
        pk_columns = []
    
    return columns, pk_columns


async def get_table_data(source_conn, table_name):
    """Get all data from a table."""
    query = f'SELECT * FROM "{table_name}"'
    return await source_conn.fetch(query)


async def create_table_sql(table_name, columns, pk_columns):
    """Generate CREATE TABLE SQL statement."""
    column_defs = []
    
    for col in columns:
        col_name = col['column_name']
        col_type = col['data_type'].upper()
        
        # Map common types to PostgreSQL
        type_mapping = {
            'INTEGER': 'INTEGER',
            'BIGINT': 'BIGINT',
            'SMALLINT': 'SMALLINT',
            'CHARACTER VARYING': 'VARCHAR',
            'CHARACTER': 'CHAR',
            'TEXT': 'TEXT',
            'TIMESTAMP WITHOUT TIME ZONE': 'TIMESTAMP',
            'TIMESTAMP WITH TIME ZONE': 'TIMESTAMPTZ',
            'DOUBLE PRECISION': 'DOUBLE PRECISION',
            'REAL': 'REAL',
            'BOOLEAN': 'BOOLEAN',
            'JSON': 'JSONB',
            'JSONB': 'JSONB',
            'UUID': 'UUID',
        }
        
        pg_type = type_mapping.get(col_type, col_type)
        
        # Handle VARCHAR length
        if col_type == 'CHARACTER VARYING':
            pg_type = 'VARCHAR(255)'  # Default length
        
        col_def = f'"{col_name}" {pg_type}'
        
        if col['is_nullable'] == 'NO':
            col_def += ' NOT NULL'
        
        if col['column_default']:
            default = col['column_default']
            if 'nextval' in default:
                # Auto-increment
                if 'integer' in col_type.lower():
                    col_def = f'"{col_name}" SERIAL'
            else:
                col_def += f' DEFAULT {default}'
        
        column_defs.append(col_def)
    
    # Add primary key constraint
    if pk_columns:
        pk_list = ', '.join([f'"{col}"' for col in pk_columns])
        column_defs.append(f'PRIMARY KEY ({pk_list})')
    
    sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    '
    sql += ',\n    '.join(column_defs)
    sql += '\n);'
    
    return sql


async def migrate_table(source_conn, target_conn, table_name, verbose=True):
    """Migrate a single table from source to target."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"Migrating table: {table_name}")
        print('='*60)
    
    try:
        # Get schema
        columns, pk_columns = await get_table_schema(source_conn, table_name)
        
        if verbose:
            print(f"Found {len(columns)} columns")
            if pk_columns:
                print(f"Primary Key: {', '.join(pk_columns)}")
        
        # Create table
        if not MIGRATE_DATA_ONLY:
            create_sql = await create_table_sql(table_name, columns, pk_columns)
            if verbose:
                print(f"\nCREATE TABLE statement:")
                print(create_sql)
            
            if DROP_EXISTING_TABLES:
                await target_conn.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
            
            await target_conn.execute(create_sql)
            if verbose:
                print("✓ Table created successfully")
        
        # Migrate data
        if not MIGRATE_SCHEMA_ONLY:
            data = await get_table_data(source_conn, table_name)
            if verbose:
                print(f"\nFound {len(data)} rows to migrate")
            
            if data:
                # Get column names
                col_names = [col['column_name'] for col in columns]
                
                # Insert data
                placeholders = ', '.join([f'${i+1}' for i in range(len(col_names))])
                col_list = ', '.join([f'"{col}"' for col in col_names])
                insert_sql = f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})'
                
                inserted = 0
                for row in data:
                    try:
                        values = [dict(row)[col] for col in col_names]
                        await target_conn.execute(insert_sql, *values)
                        inserted += 1
                    except Exception as e:
                        if verbose:
                            print(f"⚠ Error inserting row: {e}")
                
                if verbose:
                    print(f"✓ Inserted {inserted}/{len(data)} rows")
        
        return True
        
    except Exception as e:
        print(f"✗ Error migrating {table_name}: {e}")
        return False


async def run_migration():
    """Run the complete migration process."""
    print("="*70)
    print("PostgreSQL Migration Tool - pgAdmin to Project DB")
    print("="*70)
    print(f"\nSource: {SOURCE_DB_USER}@{SOURCE_DB_HOST}:{SOURCE_DB_PORT}/{SOURCE_DB_NAME}")
    print(f"Target: {TARGET_DB_USER}@{TARGET_DB_HOST}:{TARGET_DB_PORT}/{TARGET_DB_NAME}")
    print(f"\nMode: {'Schema Only' if MIGRATE_SCHEMA_ONLY else 'Data Only' if MIGRATE_DATA_ONLY else 'Schema + Data'}")
    
    try:
        # Connect to databases
        print("\nConnecting to databases...")
        source_conn = await get_source_connection()
        print(f"✓ Connected to source database")
        
        target_conn = await get_target_connection()
        print(f"✓ Connected to target database")
        
        # Get tables to migrate
        if TABLES_TO_MIGRATE:
            tables = TABLES_TO_MIGRATE
        else:
            tables = await list_all_tables(source_conn)
            print(f"\nFound {len(tables)} tables in source database:")
            for table in tables:
                print(f"  - {table}")
        
        # Confirm migration
        if not TABLES_TO_MIGRATE:
            response = input(f"\nMigrate all {len(tables)} tables? (y/n): ")
            if response.lower() != 'y':
                print("Migration cancelled")
                await source_conn.close()
                await target_conn.close()
                return
        
        # Migrate each table
        success_count = 0
        for table in tables:
            result = await migrate_table(source_conn, target_conn, table)
            if result:
                success_count += 1
        
        # Summary
        print("\n" + "="*70)
        print("Migration Summary")
        print("="*70)
        print(f"Tables migrated: {success_count}/{len(tables)}")
        print(f"Tables failed: {len(tables) - success_count}")
        
        if success_count == len(tables):
            print("\n✓ Migration completed successfully!")
        else:
            print("\n⚠ Migration completed with errors")
        
        # Close connections
        await source_conn.close()
        await target_conn.close()
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if asyncpg is installed
    try:
        import asyncpg
    except ImportError:
        print("Error: asyncpg not installed")
        print("Install with: pip install asyncpg")
        sys.exit(1)
    
    # Run migration
    asyncio.run(run_migration())
