"""
Automatic Migration Script - luxeflow_ai to fte_db

This script will:
1. Connect to luxeflow_ai database (pgAdmin)
2. Extract all tables schema
3. Migrate to fte_db (project database)

Usage:
    python auto_migrate_luxeflow.py
"""

import asyncio
import asyncpg
import sys
from typing import List, Dict, Any

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Source: luxeflow_ai database (pgAdmin)
SOURCE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "luxeFlow_ai",
    "user": "postgres",
    "password": "postgres",
}

# Target: Project database (fte_db)
# Using postgres user since Docker may not be running
TARGET_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "fte_db",
    "user": "postgres",
    "password": "postgres",
}

# ============================================================================


class DatabaseMigrator:
    """Handles database migration from luxeflow_ai to fte_db."""
    
    def __init__(self, source_config: Dict, target_config: Dict):
        self.source_config = source_config
        self.target_config = target_config
        self.source_conn: asyncpg.Connection = None
        self.target_conn: asyncpg.Connection = None
    
    async def connect(self):
        """Connect to both databases."""
        print("\n📡 Connecting to databases...")
        
        try:
            self.source_conn = await asyncpg.connect(**self.source_config)
            print(f"   ✓ Connected to source: {self.source_config['database']}")
        except Exception as e:
            print(f"   ✗ Failed to connect to source: {e}")
            raise
        
        try:
            self.target_conn = await asyncpg.connect(**self.target_config)
            print(f"   ✓ Connected to target: {self.target_config['database']}")
        except Exception as e:
            print(f"   ✗ Failed to connect to target: {e}")
            await self.source_conn.close()
            raise
    
    async def disconnect(self):
        """Close database connections."""
        if self.source_conn:
            await self.source_conn.close()
        if self.target_conn:
            await self.target_conn.close()
        print("\n   ✓ Connections closed")
    
    async def get_all_tables(self) -> List[str]:
        """Get list of all tables from source database."""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        rows = await self.source_conn.fetch(query)
        return [row['table_name'] for row in rows]
    
    async def get_table_columns(self, table_name: str) -> List[Dict]:
        """Get column information for a table."""
        query = """
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default,
                udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = $1
            ORDER BY ordinal_position;
        """
        rows = await self.source_conn.fetch(query, table_name)
        return [dict(row) for row in rows]
    
    async def get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns for a table."""
        query = """
            SELECT a.attname as column_name
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = $1::regclass 
            AND i.indisprimary;
        """
        try:
            rows = await self.source_conn.fetch(query, table_name)
            return [row['column_name'] for row in rows]
        except Exception:
            return []
    
    async def get_foreign_keys(self, table_name: str) -> List[Dict]:
        """Get foreign key information for a table."""
        query = """
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = $1;
        """
        try:
            rows = await self.source_conn.fetch(query, table_name)
            return [dict(row) for row in rows]
        except Exception:
            return []
    
    async def get_table_data(self, table_name: str) -> List[asyncpg.Record]:
        """Get all data from a table."""
        query = f'SELECT * FROM "{table_name}"'
        return await self.source_conn.fetch(query)
    
    def generate_create_table_sql(self, table_name: str, columns: List[Dict], 
                                   pk_columns: List[str], fks: List[Dict]) -> str:
        """Generate CREATE TABLE SQL statement."""
        column_defs = []
        
        type_mapping = {
            'integer': 'INTEGER',
            'bigint': 'BIGINT',
            'smallint': 'SMALLINT',
            'character varying': 'VARCHAR',
            'character': 'CHAR',
            'text': 'TEXT',
            'timestamp without time zone': 'TIMESTAMP',
            'timestamp with time zone': 'TIMESTAMPTZ',
            'double precision': 'DOUBLE PRECISION',
            'real': 'REAL',
            'boolean': 'BOOLEAN',
            'json': 'JSONB',
            'jsonb': 'JSONB',
            'uuid': 'UUID',
            'bytea': 'BYTEA',
            'numeric': 'NUMERIC',
            'decimal': 'DECIMAL',
            'date': 'DATE',
            'time without time zone': 'TIME',
        }
        
        for col in columns:
            col_name = col['column_name']
            data_type = col['data_type'].lower()
            udt_name = col['udt_name'].lower()
            
            # Determine PostgreSQL type
            if data_type == 'character varying':
                max_len = col['character_maximum_length']
                if max_len:
                    pg_type = f'VARCHAR({max_len})'
                else:
                    pg_type = 'VARCHAR(255)'
            elif data_type == 'numeric' or data_type == 'decimal':
                pg_type = 'DECIMAL'
            elif udt_name in type_mapping:
                pg_type = type_mapping[udt_name]
            elif data_type in type_mapping:
                pg_type = type_mapping[data_type]
            else:
                pg_type = data_type.upper()
            
            col_def = f'"{col_name}" {pg_type}'
            
            # Handle NOT NULL
            if col['is_nullable'] == 'NO':
                col_def += ' NOT NULL'
            
            # Handle DEFAULT
            if col['column_default']:
                default = col['column_default']
                if 'nextval' in default.lower():
                    # Auto-increment sequence
                    if 'integer' in data_type.lower() or 'bigint' in data_type.lower():
                        if 'bigint' in data_type.lower():
                            pg_type = 'BIGSERIAL'
                        else:
                            pg_type = 'SERIAL'
                        col_def = f'"{col_name}" {pg_type}'
                        if col['is_nullable'] == 'NO':
                            col_def += ' NOT NULL'
                else:
                    # Other defaults
                    if 'text' in data_type.lower() or 'char' in data_type.lower():
                        default = default.replace("''", "'")
                        col_def += f' DEFAULT {default}'
                    else:
                        col_def += f' DEFAULT {default}'
            
            column_defs.append(col_def)
        
        # Add primary key
        if pk_columns:
            pk_list = ', '.join([f'"{col}"' for col in pk_columns])
            column_defs.append(f'PRIMARY KEY ({pk_list})')
        
        # Add foreign keys
        for fk in fks:
            fk_col = fk['column_name']
            ref_table = fk['foreign_table_name']
            ref_col = fk['foreign_column_name']
            column_defs.append(
                f'FOREIGN KEY ("{fk_col}") REFERENCES "{ref_table}"("{ref_col}")'
            )
        
        sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    '
        sql += ',\n    '.join(column_defs)
        sql += '\n);'
        
        return sql
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if table exists in target database."""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = $1
            );
        """
        result = await self.target_conn.fetchval(query, table_name)
        return result
    
    async def drop_table(self, table_name: str):
        """Drop table if exists."""
        await self.target_conn.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
    
    async def create_table(self, table_name: str, columns: List[Dict], 
                           pk_columns: List[str], fks: List[Dict]):
        """Create table in target database."""
        sql = self.generate_create_table_sql(table_name, columns, pk_columns, fks)
        await self.target_conn.execute(sql)
    
    async def insert_data(self, table_name: str, columns: List[Dict], 
                          data: List[asyncpg.Record]):
        """Insert data into table."""
        if not data:
            return 0
        
        col_names = [col['column_name'] for col in columns]
        placeholders = ', '.join([f'${i+1}' for i in range(len(col_names))])
        col_list = ', '.join([f'"{col}"' for col in col_names])
        insert_sql = f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})'
        
        inserted = 0
        for row in data:
            try:
                values = [row[col] for col in col_names]
                await self.target_conn.execute(insert_sql, *values)
                inserted += 1
            except Exception as e:
                print(f"      ⚠ Error inserting row: {str(e)[:100]}")
        
        return inserted
    
    async def migrate_table(self, table_name: str, drop_existing: bool = False) -> bool:
        """Migrate a single table."""
        print(f"\n{'='*60}")
        print(f"📊 Migrating: {table_name}")
        print('='*60)
        
        try:
            # Get table info
            columns = await self.get_table_columns(table_name)
            pk_columns = await self.get_primary_keys(table_name)
            fks = await self.get_foreign_keys(table_name)
            
            print(f"   📋 Columns: {len(columns)}")
            print(f"   🔑 Primary Keys: {pk_columns if pk_columns else 'None'}")
            if fks:
                print(f"   🔗 Foreign Keys: {len(fks)}")
            
            # Check if table exists in target
            exists = await self.table_exists(table_name)
            if exists:
                if drop_existing:
                    print(f"   🗑️  Dropping existing table...")
                    await self.drop_table(table_name)
                else:
                    print(f"   ⚠️  Table already exists, skipping creation")
            else:
                # Create table
                print(f"   🏗️  Creating table...")
                await self.create_table(table_name, columns, pk_columns, fks)
                print(f"   ✓ Table created")
            
            # Migrate data
            print(f"   📥 Fetching data...")
            data = await self.get_table_data(table_name)
            print(f"   📦 Rows to migrate: {len(data)}")
            
            if data:
                print(f"   📤 Inserting data...")
                inserted = await self.insert_data(table_name, columns, data)
                print(f"   ✓ Inserted {inserted}/{len(data)} rows")
            
            return True
            
        except Exception as e:
            print(f"   ✗ Migration failed: {e}")
            return False
    
    async def migrate_all_tables(self, tables: List[str] = None, 
                                  drop_existing: bool = False):
        """Migrate all tables."""
        if not tables:
            tables = await self.get_all_tables()
        
        print(f"\n{'='*70}")
        print(f"🚀 Starting Migration - {len(tables)} tables")
        print('='*70)
        
        success = 0
        failed = 0
        
        for table in tables:
            result = await self.migrate_table(table, drop_existing)
            if result:
                success += 1
            else:
                failed += 1
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 Migration Summary")
        print('='*70)
        print(f"   ✅ Successful: {success}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📋 Total: {len(tables)}")
        
        if failed == 0:
            print(f"\n🎉 Migration completed successfully!")
        else:
            print(f"\n⚠️  Migration completed with {failed} error(s)")
        
        return success, failed
    
    async def verify_migration(self, tables: List[str]):
        """Verify migrated tables."""
        print(f"\n{'='*70}")
        print(f"🔍 Verifying Migration")
        print('='*70)
        
        for table in tables:
            source_count = await self.source_conn.fetchval(
                f'SELECT COUNT(*) FROM "{table}"'
            )
            target_count = await self.target_conn.fetchval(
                f'SELECT COUNT(*) FROM "{table}"'
            )
            
            status = "✓" if source_count == target_count else "⚠"
            print(f"   {status} {table}: Source={source_count}, Target={target_count}")


async def main():
    """Main migration function."""
    print("="*70)
    print("🔄 Database Migration Tool")
    print("   luxeflow_ai → fte_db")
    print("="*70)
    
    migrator = DatabaseMigrator(SOURCE_CONFIG, TARGET_CONFIG)
    
    try:
        # Connect
        await migrator.connect()
        
        # Get tables
        tables = await migrator.get_all_tables()
        
        if not tables:
            print("\n⚠️  No tables found in luxeflow_ai database")
            return
        
        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        
        # Confirm
        response = input(f"\n❓ Migrate all {len(tables)} tables to fte_db? (y/n): ")
        if response.lower() != 'y':
            print("Migration cancelled")
            return
        
        # Ask about dropping existing tables
        response = input(f"❓ Drop existing tables before migration? (y/n): ")
        drop_existing = response.lower() == 'y'
        
        # Run migration
        success, failed = await migrator.migrate_all_tables(tables, drop_existing)
        
        # Verify
        if success > 0:
            await migrator.verify_migration(tables)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await migrator.disconnect()


if __name__ == "__main__":
    # Check dependencies
    try:
        import asyncpg
    except ImportError:
        print("❌ Error: asyncpg not installed")
        print("   Install with: pip install asyncpg")
        sys.exit(1)
    
    # Run migration
    asyncio.run(main())
