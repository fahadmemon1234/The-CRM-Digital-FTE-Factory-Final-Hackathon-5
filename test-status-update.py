import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(
        'postgresql://postgres:postgres@localhost:5432/luxeFlow_ai'
    )
    
    print("=== Testing Status Update ===\n")
    
    # Get a ticket
    ticket = await conn.fetchrow("""
        SELECT id, subject, status 
        FROM tickets 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    
    print(f"Ticket ID: {ticket['id']}")
    print(f"Subject: {ticket['subject']}")
    print(f"Current Status: {ticket['status']}")
    
    # Update status
    print("\n📤 Updating to IN_PROGRESS...")
    await conn.execute("""
        UPDATE tickets SET status = 'IN_PROGRESS', updated_at = NOW()
        WHERE id = $1
    """, ticket['id'])
    
    # Verify
    updated = await conn.fetchrow("""
        SELECT id, status 
        FROM tickets 
        WHERE id = $1
    """, ticket['id'])
    
    print(f"✅ New Status: {updated['status']}")
    
    # Update to RESOLVED
    print("\n📤 Updating to RESOLVED...")
    await conn.execute("""
        UPDATE tickets SET status = 'RESOLVED', updated_at = NOW()
        WHERE id = $1
    """, ticket['id'])
    
    # Verify
    updated = await conn.fetchrow("""
        SELECT id, status 
        FROM tickets 
        WHERE id = $1
    """, ticket['id'])
    
    print(f"✅ New Status: {updated['status']}")
    
    await conn.close()
    print("\n✅ Database update test complete!")

if __name__ == "__main__":
    asyncio.run(main())
