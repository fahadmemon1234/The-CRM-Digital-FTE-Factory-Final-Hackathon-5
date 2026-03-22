import asyncio
import asyncpg
import uuid
import json
from datetime import datetime

async def insert_test_notification():
    """Insert a test notification directly into Supabase database"""
    
    conn = await asyncpg.connect(
        "postgresql://postgres.hxsexqavhjzxihmwauoz:memonggc123Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
    )
    
    try:
        # Insert test notification
        notification_id = str(uuid.uuid4())
        ticket_id = f"TKT-{uuid.uuid4().hex[:9].upper()}"
        
        await conn.execute("""
            INSERT INTO notifications (
                id, notification_type, title, message, url,
                is_read, reference_id, reference_type, metadata, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
        """, 
            notification_id, 
            'NEW_TICKET',
            'New Ticket Received - LIVE TEST',
            f'Ticket {ticket_id} created: Testing notification from Supabase direct',
            f'/dashboard/tickets/{ticket_id}',
            False,  # is_read = FALSE (unread)
            ticket_id,  # reference_id
            'ticket',  # reference_type
            json.dumps({
                'ticket_id': ticket_id,
                'customer': 'Test User',
                'email': 'test@live.com',
                'category': 'general',
                'priority': 'MEDIUM',
                'icon': 'ticket',
                'color': 'blue',
                'test': True,
                'source': 'direct_database_insert'
            })
        )
        
        print(f"✅ Test notification inserted successfully!")
        print(f"   Notification ID: {notification_id}")
        print(f"   Ticket ID: {ticket_id}")
        
        # Verify insertion
        notif = await conn.fetchrow("""
            SELECT id, notification_type, title, message, is_read, reference_id, created_at
            FROM notifications
            WHERE id = $1
        """, notification_id)
        
        if notif:
            print(f"\n📊 Verification:")
            print(f"   Type: {notif['notification_type']}")
            print(f"   Title: {notif['title']}")
            print(f"   Message: {notif['message']}")
            print(f"   Is Read: {notif['is_read']}")
            print(f"   Reference ID: {notif['reference_id']}")
            print(f"   Created At: {notif['created_at']}")
        else:
            print("❌ Verification failed - notification not found!")
        
        # Get updated count
        unread_count = await conn.fetchval("""
            SELECT COUNT(*) FROM notifications WHERE is_read = FALSE
        """)
        
        print(f"\n📬 Total unread notifications in database: {unread_count}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(insert_test_notification())
