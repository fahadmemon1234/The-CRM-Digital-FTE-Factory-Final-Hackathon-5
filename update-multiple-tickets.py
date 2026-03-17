import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(
        'postgresql://postgres:postgres@localhost:5432/luxeFlow_ai'
    )
    
    print("=== Updating Multiple Tickets ===\n")
    
    # Update first 3 tickets to different statuses
    await conn.execute("""
        UPDATE tickets SET status = 'RESOLVED' 
        WHERE created_at = (SELECT MAX(created_at) FROM tickets)
    """)
    print("✅ Latest ticket → RESOLVED")
    
    await conn.execute("""
        UPDATE tickets SET status = 'IN_PROGRESS' 
        WHERE created_at = (SELECT MAX(created_at) FROM tickets WHERE status != 'RESOLVED')
    """)
    print("✅ Second latest → IN_PROGRESS")
    
    await conn.execute("""
        UPDATE tickets SET status = 'RESOLVED' 
        WHERE subject LIKE '%219a97a8%'
    """)
    print("✅ TKT-219A97A8 → RESOLVED")
    
    # Show updated tickets
    print("\n=== Updated Tickets ===")
    rows = await conn.fetch("""
        SELECT 
            LEFT(subject, 40) as subject,
            status,
            created_at
        FROM tickets 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    for row in rows:
        status_icon = "✅" if row['status'] == 'RESOLVED' else "🔄" if row['status'] == 'IN_PROGRESS' else "⏳"
        print(f"{status_icon} {row['subject']}: {row['status']}")
    
    await conn.close()
    print("\n✅ All updates complete!")

if __name__ == "__main__":
    asyncio.run(main())
