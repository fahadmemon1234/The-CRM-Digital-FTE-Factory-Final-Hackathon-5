"""
TechCorp Customer Success AI Agent - Tickets API Extension

This file contains additional ticket endpoints for the frontend.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api", tags=["tickets"])

# Import db_pool from main module
import sys
sys.path.insert(0, '..')
from production.api.main import get_db_pool


@router.get("/tickets")
async def get_all_tickets(
    status: Optional[str] = None,
    channel: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get all tickets from database.
    
    Returns tickets in frontend-friendly format.
    """
    try:
        pool = await get_db_pool()
        
        # Simple query
        query = """
            SELECT 
                t.id,
                t.source_channel as channel,
                t.category,
                t.priority,
                t.status,
                t.created_at as time,
                c.name as customer_name,
                c.email as customer_email
            FROM tickets t
            LEFT JOIN customers c ON t.customer_id = c.id
            ORDER BY t.created_at DESC
            LIMIT $1 OFFSET $2
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, limit, offset)
            
            tickets = []
            for row in rows:
                # Calculate time ago - handle timezone-aware datetime
                created_at = row['time']
                
                if created_at is None:
                    time_ago = "Unknown"
                else:
                    # Convert timezone-aware to naive UTC for consistent comparison
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                        created_at = created_at.replace(tzinfo=None)
                    
                    # Now both datetimes are naive
                    now = datetime.utcnow()
                    diff = now - created_at

                    if diff.total_seconds() < 60:
                        time_ago = "Just now"
                    elif diff.total_seconds() < 3600:
                        time_ago = f"{int(diff.total_seconds() / 60)}m ago"
                    elif diff.total_seconds() < 86400:
                        time_ago = f"{int(diff.total_seconds() / 3600)}h ago"
                    else:
                        time_ago = f"{int(diff.total_seconds() / 86400)}d ago"

                tickets.append({
                    "id": f"TKT-{str(row['id'])[:8].upper()}",
                    "subject": f"Support Request #{str(row['id'])[:8]}",
                    "customer": row['customer_name'] or row['customer_email'] or "Unknown",
                    "channel": row['channel'] or "web_form",
                    "category": row['category'] or "general",
                    "status": row['status'] or "open",
                    "priority": row['priority'] or "medium",
                    "sentiment": 0.5,
                    "time": time_ago
                })

            return {"tickets": tickets, "total": len(tickets)}
            
    except Exception as e:
        # Return empty list on error
        return {"tickets": [], "total": 0, "error": str(e)}


@router.get("/tickets/stats")
async def get_tickets_stats():
    """Get tickets statistics for dashboard."""
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            # Get counts by status
            counts = await conn.fetchrow("""
                SELECT 
                    COUNT(*) FILTER (WHERE status IN ('open', 'pending')) as pending,
                    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                    COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
                    COUNT(*) as total
                FROM tickets
            """)
            
            return {
                "pending": counts['pending'] or 0,
                "in_progress": counts['in_progress'] or 0,
                "resolved": counts['resolved'] or 0,
                "total": counts['total'] or 0,
                "avg_response": "2.4m"
            }
            
    except Exception as e:
        return {
            "pending": 0,
            "in_progress": 0,
            "resolved": 0,
            "total": 0,
            "avg_response": "0m",
            "error": str(e)
        }
