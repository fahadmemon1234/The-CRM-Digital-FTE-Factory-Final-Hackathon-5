"""
Update admin password in database
"""

import asyncpg
import asyncio
import bcrypt

async def update_password():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
    
    # Generate fresh hash for admin123
    password = 'admin123'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    
    print(f"Generated hash: {password_hash}")
    
    # Update admin user
    await conn.execute(
        "UPDATE users SET password_hash = $1 WHERE email = 'admin@techcorp.com'",
        password_hash
    )
    
    print('✓ Admin password updated to: admin123')
    
    # Also update demo user
    demo_hash = bcrypt.hashpw('demo123'.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    await conn.execute(
        "UPDATE users SET password_hash = $1 WHERE email = 'demo@techcorp.com'",
        demo_hash
    )
    
    print('✓ Demo password updated to: demo123')
    
    # Verify
    users = await conn.fetch("SELECT email, password_hash FROM users")
    print('\n✓ Users in database:')
    for user in users:
        print(f"  - {user['email']}: {user['password_hash'][:30]}...")
    
    await conn.close()
    print('\n✅ Password update completed!')

asyncio.run(update_password())
