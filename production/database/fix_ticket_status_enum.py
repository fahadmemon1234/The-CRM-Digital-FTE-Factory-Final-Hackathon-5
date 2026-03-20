"""
Fix ticket status ENUM values in database
"""

import asyncpg
import asyncio

async def fix_enum():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
    
    print("Checking ENUM type...")
    
    # Check existing ENUM values
    enums = await conn.fetch("""
        SELECT e.enumlabel
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        WHERE t.typname = 'ticketstatus'
        ORDER BY e.enumsortorder
    """)
    
    print("\nCurrent ENUM values:")
    for e in enums:
        print(f"  - {e['enumlabel']}")
    
    # Add missing values if needed
    try:
        await conn.execute("ALTER TYPE ticketstatus ADD VALUE IF NOT EXISTS 'OPEN'")
        await conn.execute("ALTER TYPE ticketstatus ADD VALUE IF NOT EXISTS 'IN_PROGRESS'")
        await conn.execute("ALTER TYPE ticketstatus ADD VALUE IF NOT EXISTS 'RESOLVED'")
        await conn.execute("ALTER TYPE ticketstatus ADD VALUE IF NOT EXISTS 'PENDING'")
        print("\n✅ ENUM values added/verified")
    except Exception as e:
        print(f"\n⚠️ ENUM update: {e}")
    
    # Update any lowercase status values to uppercase
    await conn.execute("""
        UPDATE tickets 
        SET status = UPPER(status) 
        WHERE status IS NOT NULL 
        AND status != UPPER(status)
    """)
    
    print("✅ Status values converted to uppercase")
    
    await conn.close()
    print("\n✅ ENUM fix complete!")

asyncio.run(fix_enum())
