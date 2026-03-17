import asyncio
import asyncpg

async def main():
    # Connect to database
    conn = await asyncpg.connect(
        'postgresql://postgres:postgres@localhost:5432/luxeFlow_ai'
    )
    
    print("=== Current Ticket Statuses ===")
    rows = await conn.fetch("""
        SELECT id, subject, status 
        FROM tickets 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    for row in rows:
        print(f"{row['id']}: {row['status']}")
    
    # Update some tickets
    print("\n=== Updating Tickets ===")
    
    await conn.execute("""
        UPDATE tickets SET status = 'RESOLVED' 
        WHERE subject LIKE '%Database Test%'
    """)
    print("✅ Updated TKT-TKT-FE6D to RESOLVED")
    
    await conn.execute("""
        UPDATE tickets SET status = 'IN_PROGRESS' 
        WHERE id IN (
            SELECT id FROM tickets 
            WHERE subject LIKE '%TKT-FEA4%' 
            LIMIT 1
        )
    """)
    print("✅ Updated TKT-TKT-FEA4 to IN_PROGRESS")
    
    await conn.execute("""
        UPDATE tickets SET status = 'RESOLVED' 
        WHERE id IN (
            SELECT id FROM tickets 
            WHERE subject LIKE '%219a97a8%' 
            LIMIT 1
        )
    """)
    print("✅ Updated TKT-219A97A8 to RESOLVED")
    
    # Verify updates
    print("\n=== Updated Ticket Statuses ===")
    rows = await conn.fetch("""
        SELECT id, subject, status 
        FROM tickets 
        WHERE subject LIKE '%Database Test%' 
        OR subject LIKE '%TKT-FEA4%' 
        OR subject LIKE '%219a97a8%'
    """)
    
    for row in rows:
        print(f"{row['id']}: {row['status']}")
    
    await conn.close()
    print("\n✅ Database updates complete!")

if __name__ == "__main__":
    asyncio.run(main())
