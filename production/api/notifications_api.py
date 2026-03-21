"""
TechCorp Customer Success AI Agent - Notifications API
UPDATED: Database-backed notifications with mark-as-read support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncpg
import sys

print("[NOTIFICATIONS API] Loading notifications_api.py module...", file=sys.stderr)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

print("[NOTIFICATIONS API] Router created with prefix /api/notifications", file=sys.stderr)

# Database pool
db_pool = None

def set_db_pool(pool):
    """Set database pool from main module"""
    global db_pool
    db_pool = pool

async def get_db_pool():
    """Get database pool"""
    return db_pool

# ============================================================================
# Notification Types
# ============================================================================

NOTIFICATION_TYPES = {
    'NEW_TICKET': {
        'title': 'New Ticket Received',
        'icon': 'ticket',
        'color': 'blue',
        'priority': 'high'
    },
    'TICKET_UPDATED': {
        'title': 'Ticket Status Updated',
        'icon': 'refresh',
        'color': 'purple',
        'priority': 'medium'
    },
    'NEW_MESSAGE': {
        'title': 'New Message',
        'icon': 'message',
        'color': 'green',
        'priority': 'high'
    },
    'URGENT_TICKET': {
        'title': 'Urgent Ticket',
        'icon': 'alert',
        'color': 'red',
        'priority': 'urgent'
    },
    'CUSTOMER_FOLLOWUP': {
        'title': 'Customer Follow-up',
        'icon': 'user',
        'color': 'orange',
        'priority': 'medium'
    }
}

# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/debug")
async def debug_notifications():
    """Debug endpoint to check db_pool status"""
    return {
        'db_pool': 'connected' if db_pool is not None else 'NOT CONNECTED',
        'db_pool_type': type(db_pool).__name__ if db_pool else None
    }

@router.get("")
async def get_notifications(
    limit: int = Query(20, ge=1, le=100, description="Max notifications to return"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    type_filter: Optional[str] = Query(None, description="Filter by notification type")
):
    """
    Get user notifications from database.
    """
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database connection not available")

    try:
        async with db_pool.acquire() as conn:
            # Build query based on unread_only flag
            if unread_only:
                # Get only unread notifications from database
                notifications = await conn.fetch(f"""
                    SELECT
                        id, notification_type, title, message, url,
                        is_read, created_at, reference_id, reference_type, metadata
                    FROM notifications
                    WHERE is_read = FALSE
                    ORDER BY created_at DESC
                    LIMIT {int(limit)}
                """)
            else:
                # Get all notifications from database
                notifications = await conn.fetch(f"""
                    SELECT
                        id, notification_type, title, message, url,
                        is_read, created_at, reference_id, reference_type, metadata
                    FROM notifications
                    ORDER BY created_at DESC
                    LIMIT {int(limit)}
                """)

            # Convert to response format
            result = []
            for notif in notifications:
                metadata = notif['metadata'] or {}
                result.append({
                    'id': str(notif['id']),
                    'type': notif['notification_type'],
                    'title': notif['title'],
                    'message': notif['message'],
                    'timestamp': notif['created_at'].isoformat() if notif['created_at'] else None,
                    'read': notif['is_read'],
                    'icon': metadata.get('icon', 'bell'),
                    'color': metadata.get('color', 'blue'),
                    'url': notif['url'] or '/dashboard',
                    'data': {
                        'reference_id': notif['reference_id'],
                        'reference_type': notif['reference_type'],
                        **metadata
                    }
                })

            # Count unread
            unread_count = len([n for n in result if not n['read']])

            return {
                'notifications': result,
                'total': len(result),
                'unread': unread_count,
                'has_more': len(result) == limit
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")


@router.get("/unread-count")
async def get_unread_count():
    """Get count of unread notifications from database"""
    if db_pool is None:
        return {'unread': 0}

    try:
        async with db_pool.acquire() as conn:
            # Count unread notifications from database
            unread = await conn.fetchval("""
                SELECT COUNT(*) FROM notifications
                WHERE is_read = FALSE
            """)

            return {'unread': int(unread)}

    except Exception as e:
        return {'unread': 0}


@router.post("/mark-read")
async def mark_notification_read(
    notification_id: str,
    user_id: Optional[str] = None
):
    """
    Mark a notification as read in database.
    """
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database connection not available")

    try:
        async with db_pool.acquire() as conn:
            # Update notification to mark as read
            await conn.execute("""
                UPDATE notifications
                SET is_read = TRUE, read_at = NOW()
                WHERE id = $1
            """, notification_id)

            return {
                'success': True,
                'message': 'Notification marked as read',
                'notification_id': notification_id
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")


@router.post("/mark-all-read")
async def mark_all_read(
    user_id: Optional[str] = None
):
    """Mark all notifications as read in database"""
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database connection not available")

    try:
        async with db_pool.acquire() as conn:
            # First count unread notifications
            unread_count = await conn.fetchval("""
                SELECT COUNT(*) FROM notifications
                WHERE is_read = FALSE
            """)

            # Mark all notifications as read
            await conn.execute("""
                UPDATE notifications
                SET is_read = TRUE, read_at = NOW()
                WHERE is_read = FALSE
            """)

            print(f"[NOTIFICATIONS] Marked {unread_count} notifications as read")

            return {
                'success': True,
                'message': 'All notifications marked as read',
                'updated_count': int(unread_count)
            }

    except Exception as e:
        print(f"[NOTIFICATIONS ERROR] Failed to mark all as read: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to mark all notifications as read: {str(e)}")


@router.get("/stats")
async def get_notification_stats():
    """Get notification statistics"""
    if db_pool is None:
        return {
            'today': 0,
            'this_week': 0,
            'this_month': 0
        }
    
    try:
        async with db_pool.acquire() as conn:
            # Today's tickets
            today = await conn.fetchval("""
                SELECT COUNT(*) FROM tickets 
                WHERE created_at >= DATE_TRUNC('day', NOW())
            """)
            
            # This week's tickets
            this_week = await conn.fetchval("""
                SELECT COUNT(*) FROM tickets 
                WHERE created_at >= DATE_TRUNC('week', NOW())
            """)
            
            # This month's tickets
            this_month = await conn.fetchval("""
                SELECT COUNT(*) FROM tickets 
                WHERE created_at >= DATE_TRUNC('month', NOW())
            """)
            
            return {
                'today': int(today),
                'this_week': int(this_week),
                'this_month': int(this_month)
            }
            
    except Exception as e:
        return {
            'today': 0,
            'this_week': 0,
            'this_month': 0
        }
