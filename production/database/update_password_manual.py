"""
Manual Password Update Script
Update user password in PostgreSQL database
"""

import asyncpg
import asyncio
import bcrypt

async def update_password():
    # Database connection
    conn = await asyncpg.connect(
        'postgresql://postgres:postgres@localhost:5432/luxeFlow_ai'
    )
    
    print("=" * 60)
    print("PASSWORD UPDATE TOOL")
    print("=" * 60)
    
    # Get user email
    email = input("\nEnter user email: ").strip()
    
    # Get new password
    password = input("Enter new password: ").strip()
    
    if len(password) < 6:
        print("\n❌ Error: Password must be at least 6 characters")
        await conn.close()
        return
    
    # Confirm password
    confirm_password = input("Confirm new password: ").strip()
    
    if password != confirm_password:
        print("\n❌ Error: Passwords do not match")
        await conn.close()
        return
    
    # Generate bcrypt hash
    print("\n🔐 Generating password hash...")
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')
    
    # Update in database
    try:
        await conn.execute(
            "UPDATE users SET password_hash = $1 WHERE email = $2",
            password_hash,
            email
        )
        
        print("\n✅ Password updated successfully!")
        print(f"\nUser: {email}")
        print(f"New Password: {password}")
        print(f"Hash: {password_hash[:50]}...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    await conn.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(update_password())
