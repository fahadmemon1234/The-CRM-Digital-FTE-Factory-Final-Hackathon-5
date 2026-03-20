import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
        
        # Get channel stats
        channels = await conn.fetch("""
            SELECT
                source_channel as channel,
                COUNT(*) as total_tickets,
                COUNT(*) FILTER (WHERE status = 'OPEN' OR status = 'PENDING') as active_tickets,
                COUNT(*) FILTER (WHERE status = 'RESOLVED') as resolved_tickets
            FROM tickets
            GROUP BY source_channel
        """)
        
        print("Channel Statistics from Database:")
        print("=" * 50)
        for row in channels:
            print(f"  {row['channel']}: {row['total_tickets']} total, {row['active_tickets']} active, {row['resolved_tickets']} resolved")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
