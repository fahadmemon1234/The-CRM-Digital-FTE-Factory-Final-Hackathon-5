"""
Database Setup Script - Creates tables and inserts sample data
Run this to setup the database for the tickets page
"""

import asyncio
import asyncpg
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/luxeFlow_ai"
)

async def setup_database():
    """Create tables and insert sample data."""
    print("🔧 Connecting to database...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database!")
        
        # Enable UUID extension
        print("\n📦 Enabling extensions...")
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        print("✅ Extensions enabled")
        
        # Create customers table
        print("\n📋 Creating customers table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(50),
                name VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)")
        print("✅ Customers table created")
        
        # Create tickets table
        print("\n📋 Creating tickets table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                conversation_id UUID,
                customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
                source_channel VARCHAR(50) NOT NULL,
                category VARCHAR(100),
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(50) DEFAULT 'open',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                resolved_at TIMESTAMP WITH TIME ZONE,
                resolution_notes TEXT
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_channel ON tickets(source_channel)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(category)")
        print("✅ Tickets table created with indexes")
        
        # Insert sample customers
        print("\n👥 Inserting sample customers...")
        customers = [
            ('sarah.johnson@acmecorp.com', 'Sarah Johnson', '+14155551234'),
            ('mike.chen@techstart.io', 'Mike Chen', '+14155552345'),
            ('david.park@innovate.com', 'David Park', '+14155553456'),
            ('emma.wilson@startup.co', 'Emma Wilson', '+14155554567'),
            ('robert.thompson@enterprise.com', 'Robert Thompson', '+14155555678'),
            ('jennifer.martinez@corp.com', 'Jennifer Martinez', '+14155556789'),
            ('alex.rivera@digital.io', 'Alex Rivera', '+14155557890'),
            ('lisa.anderson@cloud.com', 'Lisa Anderson', '+14155558901'),
        ]
        
        for email, name, phone in customers:
            await conn.execute("""
                INSERT INTO customers (email, name, phone)
                VALUES ($1, $2, $3)
                ON CONFLICT (email) DO NOTHING
            """, email, name, phone)
        
        customer_count = await conn.fetchval("SELECT COUNT(*) FROM customers")
        print(f"✅ Inserted {customer_count} customers")
        
        # Insert sample tickets
        print("\n🎫 Inserting sample tickets...")
        tickets_data = [
            ('sarah.johnson@acmecorp.com', 'email', 'billing', 'medium', 'open', '15 minutes'),
            ('mike.chen@techstart.io', 'whatsapp', 'technical', 'high', 'in_progress', '32 minutes'),
            ('david.park@innovate.com', 'web_form', 'technical', 'medium', 'open', '1 hour'),
            ('emma.wilson@startup.co', 'whatsapp', 'billing', 'low', 'resolved', '3 hours'),
            ('robert.thompson@enterprise.com', 'web_form', 'feedback', 'low', 'open', '4 hours'),
            ('jennifer.martinez@corp.com', 'email', 'technical', 'medium', 'in_progress', '5 hours'),
            ('alex.rivera@digital.io', 'whatsapp', 'bug_report', 'high', 'open', '6 hours'),
            ('lisa.anderson@cloud.com', 'email', 'general', 'medium', 'resolved', '8 hours'),
            ('sarah.johnson@acmecorp.com', 'web_form', 'technical', 'high', 'in_progress', '1 day'),
            ('mike.chen@techstart.io', 'email', 'billing', 'critical', 'resolved', '1 day'),
            ('david.park@innovate.com', 'whatsapp', 'general', 'low', 'resolved', '2 days'),
            ('emma.wilson@startup.co', 'web_form', 'bug_report', 'medium', 'open', '3 days'),
            ('robert.thompson@enterprise.com', 'email', 'technical', 'high', 'in_progress', '5 days'),
            ('jennifer.martinez@corp.com', 'whatsapp', 'feedback', 'low', 'resolved', '1 week'),
        ]
        
        for email, channel, category, priority, status, time_ago in tickets_data:
            await conn.execute(f"""
                INSERT INTO tickets (customer_id, source_channel, category, priority, status, created_at)
                VALUES (
                    (SELECT id FROM customers WHERE email = $1),
                    $2, $3, $4, $5,
                    NOW() - INTERVAL '{time_ago}'
                )
            """, email, channel, category, priority, status)
        
        ticket_count = await conn.fetchval("SELECT COUNT(*) FROM tickets")
        print(f"✅ Inserted {ticket_count} tickets")
        
        # Show sample data
        print("\n📊 Sample Tickets:")
        print("-" * 100)
        rows = await conn.fetch("""
            SELECT 
                t.id,
                t.source_channel as channel,
                t.category,
                t.priority,
                t.status,
                c.name as customer_name,
                t.created_at
            FROM tickets t
            LEFT JOIN customers c ON t.customer_id = c.id
            ORDER BY t.created_at DESC
            LIMIT 5
        """)
        
        for row in rows:
            print(f"TKT-{str(row['id'])[:8].upper()} | {row['customer_name']:25} | {row['channel']:10} | {row['status']:15} | {row['created_at']}")
        
        print("\n" + "=" * 100)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 100)
        print("\n🎉 Ab frontend refresh karo: http://localhost:3000/dashboard/tickets")
        print("📊 Tickets show honge!")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure:")
        print("   1. PostgreSQL is running")
        print("   2. Database 'luxeFlow_ai' exists")
        print("   3. Password is correct in .env file")
        raise

if __name__ == "__main__":
    asyncio.run(setup_database())
