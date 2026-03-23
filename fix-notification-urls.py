"""
Fix Notification URLs in Database
Updates all notification URLs from /tickets/ to /dashboard/tickets/
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Try loading from production/.env first, then root .env
load_dotenv('production/.env') or load_dotenv('.env')

async def fix_notification_urls():
    """Fix notification URLs in the database"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    print(f"🔧 Connecting to database...")
    conn = await asyncpg.connect(database_url)
    
    try:
        # Check current URLs
        print("\n📊 Current notification URLs:")
        notifications = await conn.fetch("""
            SELECT id, url, reference_id 
            FROM notifications 
            WHERE url LIKE '/tickets/%'
            ORDER BY created_at DESC
        """)
        
        print(f"   Found {len(notifications)} notifications with old URL format")
        
        if len(notifications) > 0:
            print("\n📝 Notifications to update:")
            for notif in notifications[:10]:  # Show first 10
                print(f"   - {notif['reference_id']}: {notif['url']}")
            if len(notifications) > 10:
                print(f"   ... and {len(notifications) - 10} more")
        
        # Fix URLs - update /tickets/ to /dashboard/tickets/
        print("\n🔧 Updating notification URLs...")
        updated = await conn.execute("""
            UPDATE notifications 
            SET url = REPLACE(url, '/tickets/', '/dashboard/tickets/')
            WHERE url LIKE '/tickets/%'
        """)
        
        print(f"   ✅ Updated {updated.split()[-1]} notifications")
        
        # Verify the fix
        print("\n✅ Verification - Updated notification URLs:")
        notifications = await conn.fetch("""
            SELECT id, url, reference_id 
            FROM notifications 
            WHERE url LIKE '/dashboard/tickets/%'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        for notif in notifications:
            print(f"   ✓ {notif['reference_id']}: {notif['url']}")
        
        # Check for any remaining old URLs
        remaining = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM notifications 
            WHERE url LIKE '/tickets/%'
        """)
        
        if remaining > 0:
            print(f"\n⚠️  Warning: {remaining} notifications still have old URLs")
        else:
            print(f"\n✅ All notification URLs have been fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()
        print("\n👋 Database connection closed")

if __name__ == "__main__":
    print("=" * 70)
    print("Fix Notification URLs Script")
    print("=" * 70)
    asyncio.run(fix_notification_urls())
