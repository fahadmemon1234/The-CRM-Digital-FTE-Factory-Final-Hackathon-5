"""
Test role-based login
"""

import asyncpg
import asyncio
import bcrypt
import jwt
from datetime import datetime, timedelta

async def test_login():
    # Connect to database
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
    
    # Get admin user
    user = await conn.fetchrow(
        "SELECT * FROM users WHERE email = 'admin@techcorp.com'"
    )
    
    print(f"User found: {user['name']}")
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")
    print(f"Password hash: {user['password_hash'][:30]}...")
    
    # Test password verification
    password = 'admin123'
    is_valid = bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
    print(f"\nPassword valid: {is_valid}")
    
    # Create JWT token
    JWT_SECRET = 'your-super-secret-jwt-key-change-in-production-abc123xyz'
    token = jwt.encode({
        'sub': str(user['id']),
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'iat': datetime.utcnow(),
        'type': 'access'
    }, JWT_SECRET, algorithm='HS256')
    
    print(f"\nToken: {token[:50]}...")
    
    # User data
    user_data = {
        'id': str(user['id']),
        'name': user['name'],
        'email': user['email'],
        'company': user['company'],
        'role': user['role']
    }
    
    print(f"\nUser data with role:")
    print(user_data)
    
    await conn.close()

asyncio.run(test_login())
