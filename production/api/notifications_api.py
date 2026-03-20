"""
TechCorp Customer Success AI Agent - Notifications API

Real-time notifications for:
- New tickets
- Ticket status updates
- New messages
- Customer inquiries
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncpg

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

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

@router.get("")
async def get_notifications(
    limit: int = Query(20, ge=1, le=100, description="Max notifications to return"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    type_filter: Optional[str] = Query(None, description="Filter by notification type")
):
    """
    Get user notifications based on recent activity.
    
    This generates notifications from:
    - Recent tickets (last 24 hours)
    - Unread messages
    - Ticket status changes
    - Urgent/high priority items
    """
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        async with db_pool.acquire() as conn:
            notifications = []
            
            # Get recent tickets (last 24 hours)
            recent_tickets = await conn.fetch(f"""
                SELECT 
                    t.id, t.subject, t.status, t.priority, t.source_channel, t.created_at,
                    c.name as customer_name, c.email as customer_email
                FROM tickets t
                LEFT JOIN customers c ON t.customer_id = c.id
                WHERE t.created_at >= NOW() - INTERVAL '24 hours'
                ORDER BY t.created_at DESC
                LIMIT {int(limit)}
            """)
            
            for ticket in recent_tickets:
                ticket_id = str(ticket['id'])
                is_urgent = ticket['priority'] in ['CRITICAL', 'HIGH'] or 'urgent' in (ticket['subject'] or '').lower()
                
                notifications.append({
                    'id': f"notif_ticket_{ticket_id}",
                    'type': 'URGENT_TICKET' if is_urgent else 'NEW_TICKET',
                    'title': '🚨 Urgent Ticket' if is_urgent else '📬 New Ticket',
                    'message': f"{ticket['customer_name'] or ticket['customer_email']} created a ticket: {ticket['subject'] or 'Support Request'}",
                    'timestamp': ticket['created_at'].isoformat() if ticket['created_at'] else None,
                    'read': False,
                    'icon': 'alert' if is_urgent else 'ticket',
                    'color': 'red' if is_urgent else 'blue',
                    'url': f"/dashboard/tickets/{ticket_id}",
                    'data': {
                        'ticket_id': ticket_id,
                        'subject': ticket['subject'],
                        'customer': ticket['customer_name'] or ticket['customer_email'],
                        'channel': ticket['source_channel']
                    }
                })
            
            # Get tickets with recent status changes (updated in last 6 hours)
            updated_tickets = await conn.fetch(f"""
                SELECT 
                    t.id, t.subject, t.status, t.updated_at,
                    c.name as customer_name
                FROM tickets t
                LEFT JOIN customers c ON t.customer_id = c.id
                WHERE t.updated_at >= NOW() - INTERVAL '6 hours'
                    AND t.created_at < NOW() - INTERVAL '1 hour'
                ORDER BY t.updated_at DESC
                LIMIT {int(limit)}
            """)
            
            for ticket in updated_tickets[:5]:  # Limit to 5
                ticket_id = str(ticket['id'])
                notifications.append({
                    'id': f"notif_update_{ticket_id}",
                    'type': 'TICKET_UPDATED',
                    'title': '📝 Ticket Updated',
                    'message': f"Ticket '{ticket['subject'] or ticket_id}' status changed to {ticket['status']}",
                    'timestamp': ticket['updated_at'].isoformat() if ticket['updated_at'] else None,
                    'read': False,
                    'icon': 'refresh',
                    'color': 'purple',
                    'url': f"/dashboard/tickets/{ticket_id}",
                    'data': {
                        'ticket_id': ticket_id,
                        'status': ticket['status']
                    }
                })
            
            # Get recent messages (last 6 hours)
            messages_limit = int(min(limit, 10))
            recent_messages = await conn.fetch(f"""
                SELECT 
                    m.id, m.content, m.channel, m.timestamp, m.ticket_id,
                    t.subject as ticket_subject
                FROM messages m
                LEFT JOIN tickets t ON m.ticket_id = t.id
                WHERE m.timestamp >= NOW() - INTERVAL '6 hours'
                    AND m.sender = 'CUSTOMER'
                ORDER BY m.timestamp DESC
                LIMIT {messages_limit}
            """)
            
            for message in recent_messages:
                message_id = str(message['id'])
                ticket_id = str(message['ticket_id']) if message.get('ticket_id') else None
                
                # Truncate message content
                content = message['content'] or ''
                content_preview = content[:80] + '...' if len(content) > 80 else content
                
                notifications.append({
                    'id': f"notif_message_{message_id}",
                    'type': 'NEW_MESSAGE',
                    'title': '💬 New Message',
                    'message': f"New message: \"{content_preview}\"",
                    'timestamp': message['timestamp'].isoformat() if message['timestamp'] else None,
                    'read': False,
                    'icon': 'message',
                    'color': 'green',
                    'url': f"/dashboard/tickets/{ticket_id}" if ticket_id else "/dashboard/tickets",
                    'data': {
                        'message_id': message_id,
                        'ticket_id': ticket_id,
                        'channel': message['channel']
                    }
                })
            
            # Sort by timestamp (newest first)
            notifications.sort(
                key=lambda x: x['timestamp'] or '',
                reverse=True
            )
            
            # Limit results
            notifications = notifications[:limit]
            
            # Count unread
            unread_count = len([n for n in notifications if not n['read']])
            
            return {
                'notifications': notifications,
                'total': len(notifications),
                'unread': unread_count,
                'has_more': len(notifications) == limit
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")


@router.get("/unread-count")
async def get_unread_count():
    """Get count of unread notifications"""
    if db_pool is None:
        return {'unread': 0}
    
    try:
        async with db_pool.acquire() as conn:
            # Count recent tickets (last 24 hours)
            recent_tickets = await conn.fetchval("""
                SELECT COUNT(*) FROM tickets 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            
            # Count recent messages (last 6 hours from customers)
            recent_messages = await conn.fetchval("""
                SELECT COUNT(*) FROM messages 
                WHERE timestamp >= NOW() - INTERVAL '6 hours'
                AND sender = 'CUSTOMER'
            """)
            
            # Count updated tickets (last 6 hours)
            updated_tickets = await conn.fetchval("""
                SELECT COUNT(*) FROM tickets 
                WHERE updated_at >= NOW() - INTERVAL '6 hours'
                AND created_at < NOW() - INTERVAL '1 hour'
            """)
            
            # Total unread (cap at 99)
            unread = int(recent_tickets) + int(recent_messages) + int(updated_tickets)
            
            return {'unread': min(unread, 99)}
            
    except Exception as e:
        return {'unread': 0}


@router.post("/mark-read")
async def mark_notification_read(
    notification_id: str,
    user_id: Optional[str] = None
):
    """
    Mark a notification as read.
    
    In a full implementation, this would update a notifications table.
    For now, it's a no-op since we generate notifications dynamically.
    """
    return {
        'success': True,
        'message': 'Notification marked as read',
        'notification_id': notification_id
    }


@router.post("/mark-all-read")
async def mark_all_read(
    user_id: Optional[str] = None
):
    """Mark all notifications as read"""
    return {
        'success': True,
        'message': 'All notifications marked as read'
    }


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
