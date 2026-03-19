"""
Add role column to users table for role-based access
"""

import asyncpg
import asyncio

async def add_role_column():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
    
    # Add role column if not exists
    await conn.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user'
    """)
    print('✓ Role column added')
    
    # Update admin user
    await conn.execute("""
        UPDATE users SET role = 'admin' WHERE email = 'admin@techcorp.com'
    """)
    print('✓ Admin role assigned to admin@techcorp.com')
    
    # Update demo user
    await conn.execute("""
        UPDATE users SET role = 'user' WHERE email = 'demo@techcorp.com'
    """)
    print('✓ User role assigned to demo@techcorp.com')
    
    # Verify
    users = await conn.fetch('SELECT name, email, role FROM users')
    print('\nUsers with roles:')
    for u in users:
        print(f'  - {u["name"]} ({u["email"]}): {u["role"]}')
    
    await conn.close()
    print('\n✅ Role-based access setup complete!')

asyncio.run(add_role_column())
