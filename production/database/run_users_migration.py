"""
Run users migration on database
"""

import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Use 127.0.0.1 instead of localhost for Windows
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fte_user:fte_password@127.0.0.1:5432/fte_db")

async def run_migration():
    """Run users table migration"""
    print(f"Connecting to database: {DATABASE_URL.split('@')[1]}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected to database")
        
        # Read migration file
        with open("database/users_migration.sql", "r", encoding="utf-8") as f:
            migration_sql = f.read()
        
        # Execute migration
        await conn.execute(migration_sql)
        print("✓ Users table created successfully")
        
        # Verify users
        users = await conn.fetch("SELECT id, name, email, company FROM users")
        print(f"\n✓ Users in database ({len(users)}):")
        for user in users:
            print(f"  - {user['name']} ({user['email']}) - {user['company']}")
        
        await conn.close()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migration())
