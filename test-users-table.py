import asyncpg
import asyncio

async def check():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
        
        # Get users table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        print("Users table columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Get a user
        user = await conn.fetchrow("SELECT * FROM users WHERE email = 'admin@techcorp.com' LIMIT 1")
        print(f"\nAdmin user data:")
        for key, value in user.items():
            print(f"  {key}: {value}")
        
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(check())
