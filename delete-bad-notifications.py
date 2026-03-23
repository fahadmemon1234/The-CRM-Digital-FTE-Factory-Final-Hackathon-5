"""
Delete all notifications with wrong ticket IDs
These are notifications where reference_id is a UUID instead of TKT-xxx
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv('production/.env')

async def delete_bad_notifications():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Delete notifications where reference_id looks like a UUID (not TKT-xxx format)
    result = await conn.execute("""
        DELETE FROM notifications 
        WHERE reference_id NOT LIKE 'TKT-%'
        AND reference_id IS NOT NULL
    """)
    
    print(f"✅ Deleted bad notifications: {result}")
    
    # Show remaining notifications
    notifs = await conn.fetch("""
        SELECT id, url, reference_id, created_at 
        FROM notifications 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    print(f"\nRemaining notifications ({len(notifs)}):")
    for n in notifs:
        print(f"  ✓ {n['reference_id']}: {n['url']}")
    
    await conn.close()

asyncio.run(delete_bad_notifications())
