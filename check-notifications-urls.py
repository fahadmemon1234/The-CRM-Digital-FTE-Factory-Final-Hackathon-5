"""
Check current notification URLs
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv('production/.env')

async def check_notifications():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    notifs = await conn.fetch("""
        SELECT id, url, reference_id, metadata 
        FROM notifications 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    print("Current notifications:")
    for n in notifs:
        print(f"  {n['reference_id']}: {n['url']}")
    
    await conn.close()

asyncio.run(check_notifications())
