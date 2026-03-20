import asyncio
import asyncpg
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = 'your-super-secret-jwt-key-change-in-production-abc123xyz'

async def test():
    try:
        # Connect
        print("Connecting to database...")
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
        print("Connected!")
        
        # Get user
        print("Fetching user...")
        user = await conn.fetchrow('SELECT * FROM users WHERE email = $1', 'admin@techcorp.com')
        print(f'User: {user["name"]}, {user["email"]}, {user["role"]}')
        
        # Verify password
        print("Verifying password...")
        pw_valid = bcrypt.checkpw('admin123'.encode(), user['password_hash'].encode())
        print(f'Password valid: {pw_valid}')
        
        # Create token
        print("Creating token...")
        user_id = str(user['id'])
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        token = jwt.encode({'sub': user_id, 'exp': expire, 'iat': datetime.now(timezone.utc)}, JWT_SECRET, algorithm='HS256')
        print(f'Token: {token[:50]}...')
        
        # Response
        response = {
            'access_token': token,
            'token_type': 'bearer',
            'expires_in': 1800,
            'user': {
                'id': user_id,
                'name': user['name'],
                'email': user['email'],
                'company': user['company'],
                'role': user['role'],
                'created_at': user['created_at'].isoformat() if user['created_at'] else None
            }
        }
        print(f'\n✓ Login successful!')
        print(f'Response: {response}')
        
        await conn.close()
        
    except Exception as e:
        print(f'✗ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test())
