"""
Test Notifications API Directly
"""
import asyncio
import asyncpg

async def test_notifications():
    # Connect to database
    conn = await asyncpg.connect(
        'postgresql://fte_user:fte_password@localhost:5432/fte_db'
    )
    
    print("=== Testing Notifications Database ===")
    
    # Check current notifications
    notifications = await conn.fetch("""
        SELECT id, notification_type, title, is_read, created_at
        FROM notifications
        ORDER BY created_at DESC
    """)
    
    print(f"\nFound {len(notifications)} notifications in database:")
    for n in notifications:
        status = "READ" if n['is_read'] else "UNREAD"
        print(f"  [{status}] {n['notification_type']}: {n['title']}")
    
    # Count unread
    unread_count = await conn.fetchval("""
        SELECT COUNT(*) FROM notifications WHERE is_read = FALSE
    """)
    print(f"\nUnread count: {unread_count}")
    
    # Mark all as read
    print("\nMarking all as read...")
    result = await conn.execute("""
        UPDATE notifications
        SET is_read = TRUE, read_at = NOW()
        WHERE is_read = FALSE
    """)
    print(f"Update result: {result}")
    
    # Verify
    new_unread = await conn.fetchval("""
        SELECT COUNT(*) FROM notifications WHERE is_read = FALSE
    """)
    print(f"New unread count: {new_unread}")
    
    await conn.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_notifications())
