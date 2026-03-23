"""
Fix wrong ticket ID in notification URL
Changes TKT-51AE8C4B2 to TKT-51AE8C4B
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv('production/.env')

async def fix_notification():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Fix the wrong ticket ID in notification URL
    await conn.execute("""
        UPDATE notifications 
        SET url = REPLACE(url, '/tickets/TKT-51AE8C4B2', '/dashboard/tickets/TKT-51AE8C4B'),
            reference_id = 'TKT-51AE8C4B',
            metadata = jsonb_set(metadata, '{ticket_id}', '"TKT-51AE8C4B"')
        WHERE url LIKE '%TKT-51AE8C4B2%'
    """)
    
    print("✅ Fixed notification URL from TKT-51AE8C4B2 to TKT-51AE8C4B")
    
    # Verify
    notifs = await conn.fetch("""
        SELECT url, reference_id 
        FROM notifications 
        WHERE url LIKE '%TKT-51AE8C4B%'
        ORDER BY created_at DESC
    """)
    
    print("Updated notifications:")
    for n in notifs:
        print(f"  {n['reference_id']}: {n['url']}")
    
    await conn.close()

asyncio.run(fix_notification())
