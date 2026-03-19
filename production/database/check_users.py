"""
Check users in database
"""

import asyncpg
import asyncio

async def check_users():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
    
    users = await conn.fetch('SELECT id, name, email, company, created_at FROM users ORDER BY created_at DESC LIMIT 10')
    
    print(f'Total users: {len(users)}\n')
    print('Users in database:')
    print('-' * 80)
    
    for u in users:
        print(f'  ID: {u["id"]}')
        print(f'  Name: {u["name"]}')
        print(f'  Email: {u["email"]}')
        print(f'  Company: {u["company"]}')
        print(f'  Created: {u["created_at"]}')
        print('-' * 80)
    
    await conn.close()

asyncio.run(check_users())
