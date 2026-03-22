import asyncio
import asyncpg
import json

async def check_notifications():
    """Check notifications table in Supabase database"""
    
    # Database connection
    conn = await asyncpg.connect(
        "postgresql://postgres.hxsexqavhjzxihmwauoz:memonggc123Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
    )
    
    try:
        # Check if notifications table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'notifications'
            )
        """)
        
        print(f"Notifications table exists: {table_exists}")
        
        if table_exists:
            # Get all notifications
            notifications = await conn.fetch("""
                SELECT 
                    id, 
                    notification_type, 
                    title, 
                    message, 
                    url,
                    is_read, 
                    reference_id, 
                    reference_type, 
                    metadata,
                    created_at,
                    read_at
                FROM notifications 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            
            print(f"\n📊 Total notifications found: {len(notifications)}")
            
            # Count unread
            unread_count = await conn.fetchval("""
                SELECT COUNT(*) FROM notifications WHERE is_read = FALSE
            """)
            
            print(f"📬 Unread notifications: {unread_count}")
            
            print("\n" + "="*80)
            print("NOTIFICATIONS DATA:")
            print("="*80)
            
            for notif in notifications:
                print(f"\n🔔 ID: {notif['id']}")
                print(f"   Type: {notif['notification_type']}")
                print(f"   Title: {notif['title']}")
                print(f"   Message: {notif['message']}")
                print(f"   URL: {notif['url']}")
                print(f"   Is Read: {notif['is_read']}")
                print(f"   Reference ID: {notif['reference_id']}")
                print(f"   Reference Type: {notif['reference_type']}")
                print(f"   Created At: {notif['created_at']}")
                if notif['read_at']:
                    print(f"   Read At: {notif['read_at']}")
                if notif['metadata']:
                    print(f"   Metadata: {json.dumps(notif['metadata'], indent=2)}")
                print("-"*80)
            
            # Get notification stats by type
            print("\n" + "="*80)
            print("NOTIFICATIONS BY TYPE:")
            print("="*80)
            
            type_stats = await conn.fetch("""
                SELECT notification_type, COUNT(*) as count
                FROM notifications
                GROUP BY notification_type
                ORDER BY count DESC
            """)
            
            for stat in type_stats:
                print(f"  {stat['notification_type']}: {stat['count']}")
            
            # Get recent unread notifications
            print("\n" + "="*80)
            print("RECENT UNREAD NOTIFICATIONS:")
            print("="*80)
            
            unread = await conn.fetch("""
                SELECT id, notification_type, title, message, reference_id, created_at
                FROM notifications
                WHERE is_read = FALSE
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            if unread:
                for notif in unread:
                    print(f"\n  🔔 [{notif['notification_type']}] {notif['title']}")
                    print(f"      Message: {notif['message']}")
                    print(f"      Reference ID: {notif['reference_id']}")
                    print(f"      Created: {notif['created_at']}")
            else:
                print("\n  No unread notifications found")
        
        else:
            print("\n❌ Notifications table does not exist in the database!")
            print("   You need to run the migration script to create it.")
    
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_notifications())
