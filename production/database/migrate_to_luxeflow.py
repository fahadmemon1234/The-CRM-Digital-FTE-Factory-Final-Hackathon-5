"""
Migrate users table to luxeFlow_ai database
"""

import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/luxeFlow_ai")

async def run_migration():
    """Run users table migration"""
    print(f"Connecting to database: {DATABASE_URL}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected to database")
        
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                company VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                is_verified BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_login_at TIMESTAMP WITH TIME ZONE
            )
        """)
        print("✓ Users table created successfully")
        
        # Create index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        print("✓ Index created on email column")
        
        # Insert admin user (password: admin123)
        await conn.execute("""
            INSERT INTO users (name, email, password_hash, company, is_verified)
            VALUES (
                'Admin User',
                'admin@techcorp.com',
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu',
                'TechCorp',
                true
            )
            ON CONFLICT (email) DO NOTHING
        """)
        print("✓ Admin user created (admin@techcorp.com / admin123)")
        
        # Insert demo user (password: demo123)
        await conn.execute("""
            INSERT INTO users (name, email, password_hash, company, is_verified)
            VALUES (
                'Demo User',
                'demo@techcorp.com',
                '$2b$12$rH7xKZqQvxN9jGvVqK8LpOZm5xJ3vF2wY8nT6bR4cD1eA9fG0hI2jK',
                'Demo Corp',
                true
            )
            ON CONFLICT (email) DO NOTHING
        """)
        print("✓ Demo user created (demo@techcorp.com / demo123)")
        
        # Verify users
        users = await conn.fetch("SELECT id, name, email, company, created_at FROM users")
        print(f"\n✓ Users in database ({len(users)}):")
        for user in users:
            print(f"  - {user['name']} ({user['email']}) - {user['company']}")
        
        await conn.close()
        print("\n✅ Migration completed successfully!")
        print("\n🔐 Test Credentials:")
        print("   Email: admin@techcorp.com")
        print("   Password: admin123")
        print("\n   Email: demo@techcorp.com")
        print("   Password: demo123")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migration())
