import asyncpg
import bcrypt
import asyncio

async def test_login():
    try:
        # Connect to database
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
        
        # Get user
        email = "admin@techcorp.com"
        user = await conn.fetchrow(
            "SELECT id, name, email, password_hash, company, role FROM users WHERE email = $1",
            email
        )
        
        if not user:
            print(f"✗ User {email} not found")
            await conn.close()
            return
        
        print(f"✓ User found: {user['name']} ({user['email']})")
        print(f"Password hash: {user['password_hash'][:50]}...")
        
        # Test password
        password = "admin123"
        password_hash = user['password_hash']
        
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"Password verification: {'✓ Valid' if is_valid else '✗ Invalid'}")
            
            if not is_valid:
                print("\nTrying to update password to 'admin123'...")
                new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                await conn.execute(
                    "UPDATE users SET password_hash = $1 WHERE email = $2",
                    new_hash, email
                )
                print("✓ Password updated successfully")
                
                # Verify again
                user2 = await conn.fetchrow(
                    "SELECT password_hash FROM users WHERE email = $1",
                    email
                )
                is_valid2 = bcrypt.checkpw(password.encode('utf-8'), user2['password_hash'].encode('utf-8'))
                print(f"New password verification: {'✓ Valid' if is_valid2 else '✗ Invalid'}")
                
        except Exception as e:
            print(f"Password verification error: {e}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_login())
