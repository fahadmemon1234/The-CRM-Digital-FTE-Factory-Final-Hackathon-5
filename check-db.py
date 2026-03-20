import asyncpg
import asyncio

async def check():
    try:
        # Connect to postgres default database
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
        dbs = await conn.fetch('SELECT datname FROM pg_database WHERE datistemplate = false;')
        print("Available databases:", [d['datname'] for d in dbs])
        await conn.close()
        
        # Try connecting to luxeFlow_ai
        try:
            conn2 = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
            print("✓ luxeFlow_ai database exists and is accessible")
            await conn2.close()
        except Exception as e:
            print(f"✗ luxeFlow_ai database error: {e}")
    except Exception as e:
        print(f"Connection error: {e}")

asyncio.run(check())
