"""
TechCorp Customer Success FTE - Database Connection & API
Complete working API with PostgreSQL integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import uuid
import asyncpg
import os
import json
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import tickets router
try:
    from production.api.tickets_api import router as tickets_router, set_db_pool as set_tickets_db_pool
except ImportError:
    from api.tickets_api import router as tickets_router, set_db_pool as set_tickets_db_pool

# Import auth router
try:
    from production.api.auth_api import router as auth_router, set_db_pool as set_auth_db_pool
except ImportError:
    from api.auth_api import router as auth_router, set_db_pool as set_auth_db_pool

# Import search router
try:
    from production.api.search_api import router as search_router, set_db_pool as set_search_db_pool
except ImportError:
    from api.search_api import router as search_router, set_db_pool as set_search_db_pool

# Initialize FastAPI app
app = FastAPI(
    title="Customer Success FTE API",
    description="24/7 AI-powered customer support across Email, WhatsApp, and Web",
    version="2.0.0"
)

# CORS Configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(search_router)

# ============================================================================
# SIMPLE TICKETS API - Direct endpoint for frontend
# ============================================================================

@app.get("/api/tickets")
async def get_tickets_simple(
    limit: int = 100,
    offset: int = 0
):
    """
    Simple tickets endpoint for frontend.
    Returns all tickets from database.
    """
    try:
        pool = await get_db_pool()

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
                try:
                    created_at = row['time']
                    
                    if created_at is None:
                        time_ago = "Unknown"
                    else:
                        # Convert timezone-aware to naive UTC for consistent comparison
                        if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                            # Convert to naive UTC by removing tzinfo
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
                except Exception as e:
                    print(f"Error processing ticket {row.get('id', 'unknown')}: {e}")
                    time_ago = "Unknown"

                tickets.append({
                    "id": f"TKT-{str(row['id'])[:8].upper()}",
                    "subject": f"Support Request #{str(row['id'])[:8]}",
                    "customer": row['customer_name'] or row['customer_email'] or "Unknown",
                    "channel": row['channel'] or "web_form",
                    "category": row['category'] or "general",
                    "status": (row['status'] or "open").lower(),
                    "priority": row['priority'] or "medium",
                    "sentiment": 0.5,
                    "time": time_ago
                })

            return {"tickets": tickets, "total": len(tickets)}

    except Exception as e:
        print(f"Error in get_tickets_simple: {e}")
        import traceback
        traceback.print_exc()
        return {"tickets": [], "total": 0, "error": str(e)}

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/luxeFlow_ai"
)

# ============================================================================
# DATABASE CONNECTION POOL
# ============================================================================

db_pool = None

async def get_db_pool():
    """Get or create database connection pool"""
    global db_pool
    if db_pool is None:
        try:
            db_pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            print("[INFO] Database pool created successfully")
            # Set db_pool for tickets_api module
            try:
                set_tickets_db_pool(db_pool)
                print("[INFO] Tickets API db_pool set successfully")
            except Exception as e:
                print(f"[WARNING] Failed to set tickets API db_pool: {e}")
            # Set db_pool for auth_api module
            try:
                set_auth_db_pool(db_pool)
                print("[INFO] Auth API db_pool set successfully")
            except Exception as e:
                print(f"[WARNING] Failed to set auth API db_pool: {e}")
            # Set db_pool for search_api module
            try:
                set_search_db_pool(db_pool)
                print("[INFO] Search API db_pool set successfully")
            except Exception as e:
                print(f"[WARNING] Failed to set search API db_pool: {e}")
        except Exception as e:
            print(f"[ERROR] Database pool creation failed: {e}")
            raise
    return db_pool


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SupportFormSubmission(BaseModel):
    """Support form submission model"""
    name: str
    email: EmailStr
    subject: str
    category: str
    message: str
    channel: str = "web_form"  # Optional channel field, defaults to web_form

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

    @validator('message')
    def message_must_have_content(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters')
        return v.strip()

    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = ['general', 'technical', 'billing', 'bug_report', 'feedback']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v

# Category mapping from API to database enum
CATEGORY_MAP = {
    'general': 'GENERAL_INQUIRY',
    'technical': 'TECHNICAL_SUPPORT',
    'billing': 'BILLING',
    'bug_report': 'BUG_REPORT',
    'feedback': 'FEATURE_REQUEST'
}

# Status and priority mappings
STATUS_MAP = {
    'open': 'OPEN',
    'in_progress': 'IN_PROGRESS',
    'resolved': 'RESOLVED'
}

PRIORITY_MAP = {
    'low': 'LOW',
    'medium': 'MEDIUM',
    'high': 'HIGH',
    'critical': 'CRITICAL'
}


class SupportFormResponse(BaseModel):
    """Response model for form submission"""
    ticket_id: str
    message: str
    estimated_response_time: str


class TicketStatus(BaseModel):
    """Ticket status response"""
    ticket_id: str
    status: str
    messages: List[Dict]
    created_at: str
    last_updated: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Customer Success FTE API",
        "version": "2.0.0",
        "status": "running",
        "database": "connected" if db_pool else "disconnected"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - Tests database connection"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }


@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    WhatsApp webhook endpoint - receives messages from Twilio and sends auto-reply.
    """
    import uuid as uuid_module
    from twilio.rest import Client

    try:
        # Parse form data from Twilio
        form_data = await request.form()

        from_number = form_data.get('From', '')
        body = form_data.get('Body', '')
        message_sid = form_data.get('MessageSid', '')
        to_number = form_data.get('To', '')

        print(f"[WhatsApp Webhook] From: {from_number}")
        print(f"[WhatsApp Webhook] Body: {body}")
        print(f"[WhatsApp Webhook] MessageSid: {message_sid}")

        if not body or not from_number:
            return {"status": "ignored", "reason": "No message body or from number"}

        # Create ticket from WhatsApp message
        pool = await get_db_pool()
        ticket_uuid = uuid_module.uuid4()
        ticket_id = f"TKT-{ticket_uuid.hex[:8].upper()}"
        customer_id = None

        async with pool.acquire() as conn:
            # Find or create customer
            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE phone = $1",
                from_number
            )

            if not customer:
                # Try finding by email first
                temp_email = f"whatsapp_{from_number[-4:]}@temp.local"
                customer = await conn.fetchrow(
                    "SELECT id FROM customers WHERE email = $1",
                    temp_email
                )

            if not customer:
                # Generate a UUID for customer ID
                customer_id = uuid_module.uuid4()
                await conn.execute("""
                    INSERT INTO customers (id, phone, email, name, created_at)
                    VALUES ($1, $2, $3, $4, NOW())
                """, str(customer_id), from_number, f"whatsapp_{from_number[-4:]}@temp.local", f"WhatsApp User {from_number[-4:]}")
            else:
                customer_id = str(customer['id'])  # Convert to string for VARCHAR(36)

            # Create ticket - use same pattern as /support/submit
            db_category = "GENERAL_INQUIRY"
            db_status = "OPEN"
            db_priority = "MEDIUM"

            await conn.execute("""
                INSERT INTO tickets (
                    id, customer_id, subject, source_channel, category,
                    status, priority, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            """, str(ticket_uuid), customer_id, f"Support Request from WhatsApp", "whatsapp",
                db_category, db_status, db_priority)

            print(f"[WhatsApp Webhook] Ticket created: {ticket_id}")

        # Send auto-reply using Twilio API
        background_tasks.add_task(send_whatsapp_reply, from_number, ticket_id, body)

        return {
            "status": "received",
            "ticket_id": ticket_id,
            "message_sid": message_sid
        }

    except Exception as e:
        print(f"[WhatsApp Webhook] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def send_whatsapp_reply(to_number: str, ticket_id: str, user_message: str):
    """
    Send WhatsApp reply using Twilio API.
    Runs in background to not block webhook response.
    """
    from twilio.rest import Client

    try:
        # Get Twilio credentials from environment
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

        if not all([account_sid, auth_token, whatsapp_number]):
            print("[WhatsApp Reply] Error: Twilio credentials not configured")
            return

        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        # Create personalized auto-reply message
        reply_message = (
            f"👋 Thank you for contacting TechCorp Support!\n\n"
            f"Your ticket ID is: *{ticket_id}*\n\n"
            f"We've received your message:\n\"{user_message[:100]}{'...' if len(user_message) > 100 else ''}\"\n\n"
            f"Our AI assistant is reviewing your request and will respond within 5-10 minutes.\n\n"
            f"Need immediate help? Visit: https://techcorp.com/support\n\n"
            f"Ticket ID: {ticket_id}"
        )

        # Send message
        message = client.messages.create(
            body=reply_message,
            from_=whatsapp_number,
            to=to_number
        )

        print(f"[WhatsApp Reply] Sent to {to_number}, SID: {message.sid}")

    except Exception as e:
        print(f"[WhatsApp Reply] Failed: {e}")
        import traceback
        traceback.print_exc()


@app.post("/webhooks/email")
async def email_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Email webhook endpoint - receives emails and sends auto-reply.
    
    For Gmail: Use Gmail API push notifications or forwarding rules
    For generic: Configure email server to POST to this endpoint
    """
    import uuid as uuid_module
    import base64
    from email.mime.text import MIMEText
    
    try:
        # Parse request body
        body_data = await request.json()
        
        # Extract email data (adjust based on your email service format)
        from_email = body_data.get('from', body_data.get('From', ''))
        subject = body_data.get('subject', body_data.get('Subject', 'No Subject'))
        email_body = body_data.get('body', body_data.get('Body', body_data.get('text', '')))
        message_id = body_data.get('message_id', body_data.get('MessageId', ''))
        
        # For Gmail API format
        if 'data' in body_data:
            # Decode Gmail base64 encoded message
            try:
                decoded_data = base64.urlsafe_b64decode(body_data['data']).decode('utf-8')
                # Parse if it's a full email
                if 'From:' in decoded_data:
                    for line in decoded_data.split('\n'):
                        if line.startswith('From:'):
                            from_email = line.replace('From:', '').strip()
                        elif line.startswith('Subject:'):
                            subject = line.replace('Subject:', '').strip()
                        elif line.strip() and email_body == '':
                            email_body = line.strip()
            except:
                pass
        
        print(f"[Email Webhook] From: {from_email}")
        print(f"[Email Webhook] Subject: {subject}")
        print(f"[Email Webhook] Body: {email_body[:100]}...")
        
        if not from_email or not email_body:
            return {"status": "ignored", "reason": "No email body or from address"}
        
        # Create ticket from email
        pool = await get_db_pool()
        ticket_uuid = uuid_module.uuid4()
        ticket_id = f"TKT-{ticket_uuid.hex[:8].upper()}"
        customer_id = None
        
        async with pool.acquire() as conn:
            # Find or create customer by email
            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE email = $1",
                from_email
            )

            if not customer:
                # Generate a UUID for customer ID
                customer_id = uuid_module.uuid4()
                await conn.execute("""
                    INSERT INTO customers (id, email, name, created_at)
                    VALUES ($1, $2, $3, NOW())
                """, str(customer_id), from_email, from_email.split('@')[0])
            else:
                customer_id = str(customer['id'])  # Convert to string for VARCHAR(36)

            # Create ticket
            db_category = "GENERAL_INQUIRY"
            db_status = "OPEN"
            db_priority = "MEDIUM"

            await conn.execute("""
                INSERT INTO tickets (
                    id, customer_id, subject, source_channel, category,
                    status, priority, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            """, str(ticket_uuid), customer_id, subject, "email",
                db_category, db_status, db_priority)
            
            print(f"[Email Webhook] Ticket created: {ticket_id}")
        
        # Send auto-reply via Gmail
        background_tasks.add_task(send_email_reply, from_email, ticket_id, subject, email_body)
        
        return {
            "status": "received",
            "ticket_id": ticket_id,
            "message_id": message_id
        }

    except Exception as e:
        # Encode error message to handle Unicode
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"[Email Webhook] Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}


async def send_email_reply(to_email: str, ticket_id: str, original_subject: str, user_message: str):
    """
    Send email reply using Gmail API.
    Runs in background to not block webhook response.
    """
    from google.oauth2 import credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import base64
    
    try:
        # Get Gmail credentials from environment
        client_id = os.getenv('GMAIL_CLIENT_ID')
        client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
        
        if not all([client_id, client_secret, refresh_token]):
            print("[Email Reply] Error: Gmail credentials not configured")
            return
        
        # Create credentials from refresh token
        creds = credentials.Credentials(
            None,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            refresh_token=refresh_token
        )
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Create auto-reply message
        reply_subject = f"Re: {original_subject}"
        reply_body = (
            f"Hello,\n\n"
            f"Thank you for contacting TechCorp Support!\n\n"
            f"Your ticket ID is: *{ticket_id}*\n\n"
            f"We've received your message regarding:\n\"{original_subject}\"\n\n"
            f"Original message:\n\"{user_message[:200]}{'...' if len(user_message) > 200 else ''}\"\n\n"
            f"Our AI assistant is reviewing your request and will respond within 5-10 minutes.\n\n"
            f"Need immediate help? Visit: https://techcorp.com/support\n\n"
            f"Best regards,\n"
            f"TechCorp Support Team\n"
            f"Ticket ID: {ticket_id}"
        )
        
        # Create MIME message
        message = MIMEText(reply_body)
        message['to'] = to_email
        message['from'] = 'TechCorp Support <support@techcorp.com>'
        message['subject'] = reply_subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message via Gmail API
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"[Email Reply] Sent to {to_email}, Message ID: {sent_message['id']}")
        
    except HttpError as error:
        print(f"[Email Reply] Gmail API error: {error}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"[Email Reply] Failed: {e}")
        import traceback
        traceback.print_exc()


@app.post("/support/submit", response_model=SupportFormResponse)
async def submit_support_form(
    submission: SupportFormSubmission,
    background_tasks: BackgroundTasks
):
    """
    Handle support form submission.
    
    This endpoint:
    1. Creates/gets customer from database
    2. Creates ticket in database
    3. Creates conversation and message
    4. Returns confirmation to user
    
    Tables updated:
    - customers
    - tickets
    - conversations
    - messages
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:9].upper()}"
    customer_id = None
    conversation_id = None
    
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            # Step 1: Create or get customer
            print(f"[INFO] Creating/getting customer: {submission.email}")

            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE email = $1",
                submission.email
            )

            if customer:
                customer_id = str(customer['id'])  # Convert to string for consistency
                print(f"[INFO] Customer found: {customer_id}")
            else:
                # Generate a UUID for customer ID (compatible with VARCHAR(36))
                import uuid as uuid_module
                customer_id = str(uuid_module.uuid4())
                customer_id = await conn.fetchval("""
                    INSERT INTO customers (id, email, name, created_at)
                    VALUES ($1, $2, $3, NOW())
                    RETURNING id
                """, customer_id, submission.email, submission.name)
                print(f"[INFO] Customer created: {customer_id}")

            # Step 2: Create ticket
            print(f"[INFO] Creating ticket: {ticket_id}")

            # Map category, status, and priority to database enum values
            db_category = CATEGORY_MAP.get(submission.category, 'GENERAL_INQUIRY')
            db_status = STATUS_MAP.get('open', 'OPEN')
            db_priority = PRIORITY_MAP.get('medium', 'MEDIUM')
            
            # Use channel from submission (defaults to 'web_form' if not provided)
            source_channel = submission.channel or 'web_form'

            await conn.execute("""
                INSERT INTO tickets (
                    id, customer_id, subject, source_channel, category,
                    status, priority, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
            """, ticket_id, customer_id, submission.subject, source_channel, db_category,
                db_status, db_priority)

            print(f"[INFO] Ticket created: {ticket_id}")

            # Step 3: Create conversation
            print(f"[INFO] Creating conversation")

            conversation_id = await conn.fetchval("""
                INSERT INTO conversations (
                    customer_id, initial_channel, status,
                    started_at, sentiment_score
                ) VALUES ($1, $2, $3, NOW(), $4)
                RETURNING id
            """, customer_id, 'web_form', 'active', 0.5)

            print(f"[INFO] Conversation created: {conversation_id}")

            # Step 4: Create customer message (using tickets table structure)
            print(f"[INFO] Creating message")

            # Generate message ID
            import uuid as uuid_module
            message_id = str(uuid_module.uuid4())

            # Map direction and role to sender enum
            sender = 'CUSTOMER'  # Messages table uses sender enum

            await conn.execute("""
                INSERT INTO messages (
                    id, ticket_id, sender, content, channel, timestamp
                ) VALUES ($1, $2, $3, $4, $5, NOW())
            """, message_id, ticket_id, sender, submission.message, 'WEB')

            print(f"[INFO] Message created: {message_id}")

            # Step 5: Update ticket with conversation_id
            await conn.execute("""
                UPDATE tickets SET conversation_id = $1 WHERE id = $2
            """, conversation_id, ticket_id)

            print(f"[INFO] Ticket updated with conversation link")

        print(f"[INFO] All operations completed successfully!")

        return SupportFormResponse(
            ticket_id=ticket_id,
            message="Thank you for contacting us! Our AI assistant will respond shortly.",
            estimated_response_time="Usually within 5 minutes"
        )

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/support/ticket/{ticket_id}", response_model=TicketStatus)
async def get_ticket_status(ticket_id: str):
    """Get ticket status and conversation history"""
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            # Get ticket info
            ticket = await conn.fetchrow("""
                SELECT id, status, created_at
                FROM tickets
                WHERE id = $1
            """, ticket_id)
            
            if not ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")
            
            # Get messages
            messages = await conn.fetch("""
                SELECT role, content, created_at, channel
                FROM messages
                WHERE conversation_id = (
                    SELECT conversation_id FROM tickets WHERE id = $1
                )
                ORDER BY created_at ASC
            """, ticket_id)
            
            return TicketStatus(
                ticket_id=str(ticket['id']),
                status=ticket['status'],
                messages=[dict(msg) for msg in messages],
                created_at=ticket['created_at'].isoformat(),
                last_updated=datetime.utcnow().isoformat()
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customers/lookup")
async def lookup_customer(email: Optional[str] = None, phone: Optional[str] = None):
    """Look up customer by email or phone"""
    if not email and not phone:
        raise HTTPException(status_code=400, detail="Provide email or phone")
    
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            if email:
                customer = await conn.fetchrow(
                    "SELECT id, email, name, created_at FROM customers WHERE email = $1",
                    email
                )
            else:
                customer = await conn.fetchrow(
                    "SELECT id, phone, name, created_at FROM customers WHERE phone = $1",
                    phone
                )
            
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            return dict(customer)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/channels")
async def get_channel_metrics():
    """Get performance metrics by channel"""
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            metrics = await conn.fetch("""
                SELECT
                    source_channel as channel,
                    COUNT(*) as total_tickets,
                    COUNT(*) FILTER (WHERE UPPER(status) = 'OPEN') as open,
                    COUNT(*) FILTER (WHERE UPPER(status) = 'RESOLVED') as resolved,
                    COUNT(*) FILTER (WHERE UPPER(status) = 'ESCALATED') as escalated
                FROM tickets
                WHERE created_at > NOW() - INTERVAL '24 hours'
                GROUP BY source_channel
            """)
            
            return {row['channel']: dict(row) for row in metrics}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        pool = await get_db_pool()

        async with pool.acquire() as conn:
            # Total tickets
            total = await conn.fetchval("SELECT COUNT(*) FROM tickets")

            # Resolved tickets
            resolved = await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE UPPER(status) = 'RESOLVED'"
            )

            # Pending tickets
            pending = await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE UPPER(status) IN ('OPEN', 'IN_PROGRESS')"
            )

            # Avg response time (mock)
            avg_response = "2.4m"

            return {
                "total_tickets": total,
                "resolved": resolved,
                "pending": pending,
                "avg_response_time": avg_response
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/channels")
async def get_channels():
    """Get all communication channels with stats from database"""
    try:
        if db_pool is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        async with db_pool.acquire() as conn:
            # Get channel statistics
            channels_data = await conn.fetch("""
                SELECT
                    source_channel as channel,
                    COUNT(*) as total_tickets,
                    COUNT(*) FILTER (WHERE status = 'OPEN' OR status = 'PENDING') as active_tickets,
                    COUNT(*) FILTER (WHERE status = 'RESOLVED') as resolved_tickets
                FROM tickets
                GROUP BY source_channel
            """)
            
            # Build channels response
            channels = []
            channel_map = {
                'email': {'name': 'Email', 'color': '#3b82f6'},
                'whatsapp': {'name': 'WhatsApp', 'color': '#22c55e'},
                'web_form': {'name': 'Web Form', 'color': '#8b5cf6'},
                'gmail': {'name': 'Email', 'color': '#3b82f6'}
            }
            
            # Aggregate email and gmail
            aggregated = {}
            for row in channels_data:
                channel = row['channel'] or 'web_form'
                if channel.lower() in ['email', 'gmail']:
                    key = 'email'
                else:
                    key = channel.lower()
                
                if key not in aggregated:
                    aggregated[key] = {
                        'total': 0,
                        'active': 0,
                        'resolved': 0
                    }
                aggregated[key]['total'] += row['total_tickets'] or 0
                aggregated[key]['active'] += row['active_tickets'] or 0
                aggregated[key]['resolved'] += row['resolved_tickets'] or 0
            
            # Build final response
            for key, data in aggregated.items():
                info = channel_map.get(key, {'name': key, 'color': '#8b5cf6'})
                channels.append({
                    'name': info['name'],
                    'status': 'active',
                    'color': info['color'],
                    'stats': {
                        'tickets': data['total'],
                        'active': data['active'],
                        'resolved': data['resolved']
                    }
                })
            
            # Ensure all 3 channels are present
            existing = {c['name'].lower() for c in channels}
            for default_key, default_info in channel_map.items():
                if default_info['name'].lower() not in existing and default_key in ['email', 'whatsapp', 'web_form']:
                    channels.append({
                        'name': default_info['name'],
                        'status': 'inactive',
                        'color': default_info['color'],
                        'stats': {
                            'tickets': 0,
                            'active': 0,
                            'resolved': 0
                        }
                    })
            
            return {"channels": channels}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET ALL TICKETS
# ============================================================================

@app.get("/tickets")
async def get_tickets(
    status: Optional[str] = None,
    channel: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get all tickets with optional filtering.
    """
    try:
        pool = await get_db_pool()
        
        # Simple query - just get tickets with basic info
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
            WHERE 1=1
            ORDER BY t.created_at DESC
            LIMIT $1 OFFSET $2
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, limit, offset)
            
            # Format tickets for frontend
            tickets = []
            for row in rows:
                # Calculate time ago - handle timezone-aware datetime
                created_at = row['time']
                # Convert timezone-aware to naive UTC for consistent comparison
                if created_at.tzinfo is not None:
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
                    "subject": f"Ticket #{str(row['id'])[:8]}",
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


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize database pool on startup"""
    print("[INFO] Starting API server...")
    print(f"[INFO] Database URL: {DATABASE_URL}")
    try:
        await get_db_pool()
        print("[INFO] Database connected successfully!")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        print("[WARNING] API will start but database operations will fail")


@app.on_event("shutdown")
async def shutdown():
    """Close database pool on shutdown"""
    global db_pool
    if db_pool:
        await db_pool.close()
        print("[INFO] Database pool closed")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("TechCorp Customer Success FTE API")
    print("=" * 60)
    print(f"Database: {DATABASE_URL}")
    print(f"Server: http://0.0.0.0:8000")
    print(f"Docs: http://0.0.0.0:8000/docs")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
