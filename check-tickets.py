"""
Check recent tickets in database
"""
import asyncio
import sys
sys.path.insert(0, 'production')

from production.api.main import get_db_pool

async def test():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT id, subject, status, created_at FROM tickets ORDER BY created_at DESC LIMIT 5')
        print('Recent Tickets:')
        for r in rows:
            print(f'  TKT-{str(r[0])[:8].upper()}: {r[1]} - {r[2]}')

asyncio.run(test())
