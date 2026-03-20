import asyncio
import asyncpg
import bcrypt
import jwt
from datetime import datetime, timedelta

JWT_SECRET = "your-super-secret-jwt-key-change-in-production-abc123xyz"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

async def test_login():
    try:
        # Connect to database
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
        
        email = "admin@techcorp.com"
        password = "admin123"
        
        # Get user
        user = await conn.fetchrow(
            "SELECT id, name, email, password_hash, company, role FROM users WHERE email = $1",
            email
        )
        
        if not user:
            print("✗ User not found")
            await conn.close()
            return
        
        print(f"✓ User found: {user['name']}")
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            print("✗ Invalid password")
            await conn.close()
            return
        
        print("✓ Password verified")
        
        # Create JWT token
        user_id = str(user['id'])
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        access_token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        print(f"✓ Token created: {access_token[:50]}...")
        
        # Response
        response = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user_id,
                "name": user['name'],
                "email": user['email'],
                "company": user['company'],
                "role": user['role']
            }
        }
        
        print("\n✓ Login successful!")
        print(f"Response: {response}")
        
        await conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_login())
