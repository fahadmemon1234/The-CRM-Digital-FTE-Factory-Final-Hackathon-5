import asyncpg
import asyncio

async def check():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/luxeFlow_ai')
        
        # Check if users table exists
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        print("Tables:", [t['tablename'] for t in tables])
        
        # Check users
        try:
            users = await conn.fetch("SELECT id, name, email, role FROM users LIMIT 5;")
            print(f"\n✓ Users table has {len(users)} users:")
            for u in users:
                print(f"  - {u['name']} ({u['email']}) - Role: {u['role']}")
        except Exception as e:
            print(f"✗ Users table error: {e}")
            
            # Try to create users table
            print("\nCreating users table...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✓ Users table created")
            
            # Create test user
            import bcrypt
            hashed_pw = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            await conn.execute("""
                INSERT INTO users (name, email, password_hash, company, role)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (email) DO NOTHING;
            """, "Test User", "test@test.com", hashed_pw, "TechCorp", "admin")
            print("✓ Test user created: test@test.com / test123")
        
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check())
