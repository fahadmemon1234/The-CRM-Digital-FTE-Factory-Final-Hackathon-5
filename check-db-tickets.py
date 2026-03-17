"""
Check tickets in database
"""
import asyncio
import sys
sys.path.insert(0, 'production')

from production.api.main import get_db_pool

async def check_tickets():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT id, subject, source_channel, status, created_at FROM tickets ORDER BY created_at DESC LIMIT 10')
        print('Recent 10 Tickets in Database:')
        print('=' * 80)
        for r in rows:
            ticket_id = f"TKT-{str(r['id'])[:8].upper()}"
            subject = r['subject'][:40] if r['subject'] else 'N/A'
            channel = r['source_channel']
            status = r['status']
            created = r['created_at']
            print(f'{ticket_id} | {subject} | {channel} | {status} | {created}')
        print('=' * 80)
        print(f'Total tickets shown: {len(rows)}')

asyncio.run(check_tickets())
