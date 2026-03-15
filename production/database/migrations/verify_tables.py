"""Verify migrated tables in fte_db database."""

import asyncio
import asyncpg

async def verify_migration():
    """Verify the migration was successful."""
    
    # Connect to target database
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        database="fte_db",
        user="postgres",
        password="postgres"
    )
    
    print("="*70)
    print("Migration Verification Report")
    print("="*70)
    print()
    
    # Get all tables
    tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    
    tables = await conn.fetch(tables_query)
    
    print(f"📊 Total Tables Migrated: {len(tables)}")
    print()
    print("Tables:")
    print("-"*70)
    
    for table in tables:
        table_name = table['table_name']
        
        # Get column count
        col_query = """
            SELECT COUNT(*) as count
            FROM information_schema.columns
            WHERE table_name = $1;
        """
        col_count = await conn.fetchval(col_query, table_name)
        
        # Get row count
        try:
            row_query = f'SELECT COUNT(*) FROM "{table_name}"'
            row_count = await conn.fetchval(row_query)
        except Exception:
            row_count = 0
        
        print(f"  ✓ {table_name:30} | Columns: {col_count:2} | Rows: {row_count}")
    
    print("-"*70)
    print()
    
    # Check for primary keys
    print("Primary Keys:")
    print("-"*70)
    
    pk_query = """
        SELECT
            tc.table_name,
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = 'public'
        ORDER BY tc.table_name;
    """
    
    pks = await conn.fetch(pk_query)
    
    current_table = None
    for pk in pks:
        if pk['table_name'] != current_table:
            if current_table is not None:
                print()
            current_table = pk['table_name']
            print(f"  {current_table}:")
        print(f"    - {pk['column_name']}")
    
    print("-"*70)
    print()
    
    # Check foreign keys
    print("Foreign Keys:")
    print("-"*70)
    
    fk_query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
        ORDER BY tc.table_name;
    """
    
    fks = await conn.fetch(fk_query)
    
    if fks:
        current_table = None
        for fk in fks:
            if fk['table_name'] != current_table:
                if current_table is not None:
                    print()
                current_table = fk['table_name']
                print(f"  {current_table}:")
            print(f"    - {fk['column_name']} → {fk['foreign_table']}.{fk['foreign_column']}")
    else:
        print("  No foreign keys found")
    
    print("-"*70)
    print()
    
    await conn.close()
    
    print("✅ Verification Complete!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(verify_migration())
