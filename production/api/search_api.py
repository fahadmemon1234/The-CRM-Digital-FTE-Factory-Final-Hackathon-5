"""
TechCorp Customer Success AI Agent - Global Search API

Global search across tickets, customers, conversations, and messages.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import asyncpg

router = APIRouter(prefix="/api/search", tags=["search"])

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
# Search Result Models
# ============================================================================

class SearchTicket:
    def __init__(self, row):
        self.id = str(row['id'])
        self.subject = row['subject']
        self.status = row['status']
        self.channel = row['source_channel']
        self.created_at = row['created_at']
        self.customer_name = row.get('customer_name')
        self.customer_email = row.get('customer_email')
    
    def to_dict(self):
        return {
            "type": "ticket",
            "id": self.id,
            "subject": self.subject,
            "status": self.status,
            "channel": self.channel,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "customer": self.customer_name or self.customer_email,
            "url": f"/dashboard/tickets/{self.id}"
        }

class SearchCustomer:
    def __init__(self, row):
        self.id = str(row['id'])
        self.name = row['name']
        self.email = row['email']
        self.phone = row.get('phone')
        self.created_at = row.get('created_at')
    
    def to_dict(self):
        return {
            "type": "customer",
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "url": f"/dashboard/customers/{self.id}"
        }

class SearchConversation:
    def __init__(self, row):
        self.id = str(row['id'])
        self.status = row['status']
        self.channel = row['initial_channel']
        self.created_at = row['started_at']
        self.customer_name = row.get('customer_name')
        self.customer_email = row.get('customer_email')
    
    def to_dict(self):
        return {
            "type": "conversation",
            "id": self.id,
            "status": self.status,
            "channel": self.channel,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "customer": self.customer_name or self.customer_email,
            "url": f"/dashboard/conversations/{self.id}"
        }

class SearchMessage:
    def __init__(self, row):
        self.id = str(row['id'])
        self.content = row['content']
        self.channel = row['channel']
        self.created_at = row['timestamp']
        self.ticket_id = str(row['ticket_id']) if row.get('ticket_id') else None
    
    def to_dict(self):
        # Truncate content for preview
        content_preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return {
            "type": "message",
            "id": self.id,
            "content": content_preview,
            "channel": self.channel,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ticket_id": self.ticket_id,
            "url": f"/dashboard/tickets/{self.ticket_id}" if self.ticket_id else None
        }

# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/global")
async def global_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results per category"),
    types: Optional[str] = Query(None, description="Comma-separated types: ticket,customer,conversation,message")
):
    """
    Global search across tickets, customers, conversations, and messages.
    
    - **q**: Search query (minimum 2 characters)
    - **limit**: Maximum results per category (default: 20, max: 100)
    - **types**: Filter by types (optional): ticket, customer, conversation, message
    """
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Parse types filter
    type_filter = None
    if types:
        type_filter = [t.strip().lower() for t in types.split(',')]
    
    results = {
        "query": q,
        "total": 0,
        "tickets": [],
        "customers": [],
        "conversations": [],
        "messages": []
    }
    
    try:
        async with db_pool.acquire() as conn:
            # Search tickets
            if not type_filter or 'ticket' in type_filter:
                tickets = await conn.fetch("""
                    SELECT 
                        t.id, t.subject, t.status, t.source_channel, t.created_at,
                        c.name as customer_name, c.email as customer_email
                    FROM tickets t
                    LEFT JOIN customers c ON t.customer_id = c.id
                    WHERE 
                        t.subject ILIKE $1 OR
                        t.id::text ILIKE $1 OR
                        c.name ILIKE $1 OR
                        c.email ILIKE $1
                    ORDER BY t.created_at DESC
                    LIMIT $2
                """, f"%{q}%", limit)
                
                results["tickets"] = [SearchTicket(t).to_dict() for t in tickets]
            
            # Search customers
            if not type_filter or 'customer' in type_filter:
                customers = await conn.fetch("""
                    SELECT id, name, email, phone, created_at
                    FROM customers
                    WHERE 
                        name ILIKE $1 OR
                        email ILIKE $1 OR
                        phone ILIKE $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, f"%{q}%", limit)
                
                results["customers"] = [SearchCustomer(c).to_dict() for c in customers]
            
            # Search conversations
            if not type_filter or 'conversation' in type_filter:
                conversations = await conn.fetch("""
                    SELECT 
                        conv.id, conv.status, conv.initial_channel, conv.started_at,
                        c.name as customer_name, c.email as customer_email
                    FROM conversations conv
                    LEFT JOIN customers c ON conv.customer_id = c.id
                    WHERE 
                        conv.id::text ILIKE $1 OR
                        c.name ILIKE $1 OR
                        c.email ILIKE $1
                    ORDER BY conv.started_at DESC
                    LIMIT $2
                """, f"%{q}%", limit)
                
                results["conversations"] = [SearchConversation(c).to_dict() for c in conversations]
            
            # Search messages
            if not type_filter or 'message' in type_filter:
                messages = await conn.fetch("""
                    SELECT id, content, channel, timestamp, ticket_id
                    FROM messages
                    WHERE content ILIKE $1
                    ORDER BY timestamp DESC
                    LIMIT $2
                """, f"%{q}%", limit)
                
                results["messages"] = [SearchMessage(m).to_dict() for m in messages]
            
            # Calculate total
            results["total"] = (
                len(results["tickets"]) +
                len(results["customers"]) +
                len(results["conversations"]) +
                len(results["messages"])
            )
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/quick")
async def quick_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Max results")
):
    """
    Quick search for navbar autocomplete.
    Returns top results from all categories.
    """
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        async with db_pool.acquire() as conn:
            # Get top results from each category
            all_results = []
            
            # Tickets
            tickets = await conn.fetch("""
                SELECT 
                    t.id, t.subject, t.status, t.source_channel, t.created_at,
                    c.name as customer_name, c.email as customer_email
                FROM tickets t
                LEFT JOIN customers c ON t.customer_id = c.id
                WHERE 
                    t.subject ILIKE $1 OR
                    c.name ILIKE $1 OR
                    c.email ILIKE $1
                ORDER BY t.created_at DESC
                LIMIT $2
            """, f"%{q}%", limit)
            
            for t in tickets:
                all_results.append({
                    "type": "ticket",
                    "id": str(t['id']),
                    "title": t['subject'] or f"Ticket {t['id']}",
                    "subtitle": t['customer_name'] or t['customer_email'],
                    "icon": "ticket",
                    "url": f"/dashboard/tickets/{t['id']}"
                })
            
            # Customers
            customers = await conn.fetch("""
                SELECT id, name, email, phone, created_at
                FROM customers
                WHERE 
                    name ILIKE $1 OR
                    email ILIKE $1
                ORDER BY created_at DESC
                LIMIT $2
            """, f"%{q}%", limit)
            
            for c in customers:
                all_results.append({
                    "type": "customer",
                    "id": str(c['id']),
                    "title": c['name'],
                    "subtitle": c['email'],
                    "icon": "user",
                    "url": f"/dashboard/customers/{c['id']}"
                })
            
            # Return top results sorted by recency
            return {
                "query": q,
                "results": all_results[:limit],
                "total": len(all_results)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick search failed: {str(e)}")
