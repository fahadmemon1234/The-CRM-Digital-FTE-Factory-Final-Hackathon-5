"""
Test WhatsApp Integration - Direct Database Insert
"""
import asyncio
import asyncpg
import os
from datetime import datetime
import uuid

# Database URL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/luxeFlow_ai"

async def test_whatsapp_ticket():
    """Create a test WhatsApp ticket directly in database"""
    
    print("=" * 60)
    print("Testing WhatsApp Integration")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n[1/4] Connecting to database...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected!")
        
        # Create customer
        print("\n[2/4] Creating customer...")
        customer_id = str(uuid.uuid4())
        customer_email = "whatsapp_test@example.com"
        customer_name = "WhatsApp Test User"
        
        await conn.execute("""
            INSERT INTO customers (id, email, name, created_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (id) DO NOTHING
        """, customer_id, customer_email, customer_name)
        print(f"✓ Customer created: {customer_name} ({customer_email})")
        
        # Create ticket
        print("\n[3/4] Creating WhatsApp ticket...")
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        await conn.execute("""
            INSERT INTO tickets (
                id, customer_id, subject, source_channel, category,
                status, priority, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        """, ticket_id, customer_id, "Help with my order", "whatsapp", 
            "GENERAL_INQUIRY", "OPEN", "MEDIUM")
        print(f"✓ Ticket created: {ticket_id}")
        
        # Create message
        print("\n[4/4] Creating message...")
        message_id = str(uuid.uuid4())
        
        await conn.execute("""
            INSERT INTO messages (
                id, ticket_id, sender, content, channel, timestamp
            ) VALUES ($1, $2, $3, $4, $5, NOW())
        """, message_id, ticket_id, "CUSTOMER", 
            "Hello, I need help with my order", "WHATSAPP")
        print(f"✓ Message created!")
        
        # Verify
        print("\n" + "=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        
        ticket = await conn.fetchrow("""
            SELECT t.id, t.source_channel, t.status, c.name, c.email
            FROM tickets t
            LEFT JOIN customers c ON t.customer_id = c.id
            WHERE t.source_channel = 'whatsapp'
            ORDER BY t.created_at DESC
            LIMIT 1
        """)
        
        if ticket:
            print(f"\n✅ SUCCESS!")
            print(f"   Ticket ID: {ticket['id']}")
            print(f"   Channel: {ticket['source_channel']}")
            print(f"   Customer: {ticket['name']}")
            print(f"   Email: {ticket['email']}")
            print(f"   Status: {ticket['status']}")
            print("\n📱 WhatsApp message received and ticket created!")
        else:
            print("\n❌ Ticket not found!")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_whatsapp_ticket())
