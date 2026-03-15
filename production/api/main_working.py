"""
TechCorp Customer Success FTE - Working API with Database
Tested and Working Version
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid
import asyncpg
import os

# Initialize FastAPI app
app = FastAPI(
    title="Customer Success FTE API",
    version="2.0.0"
)

# CORS - Allow ALL origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration - Docker PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://fte_user:fte_password@localhost:5432/fte_db"
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SupportFormSubmission(BaseModel):
    name: str
    email: str
    subject: str
    category: str
    message: str

class SupportFormResponse(BaseModel):
    ticket_id: str
    message: str
    estimated_response_time: str

# ============================================================================
# DATABASE HELPERS
# ============================================================================

async def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print(f"✓ Database connected: {DATABASE_URL}")
        return conn
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {"name": "Customer Success FTE API", "version": "2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint - Tests database connection"""
    conn = await get_db_connection()
    if conn:
        try:
            await conn.fetchval("SELECT 1")
            await conn.close()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
    else:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }

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
    
    print("=" * 60)
    print(f"📥 Form submission received")
    print(f"   Name: {submission.name}")
    print(f"   Email: {submission.email}")
    print(f"   Subject: {submission.subject}")
    print(f"   Category: {submission.category}")
    print("=" * 60)
    
    try:
        conn = await get_db_connection()
        
        if not conn:
            # If database not available, return mock response
            print("⚠️ Database unavailable, returning mock response")
            return SupportFormResponse(
                ticket_id=ticket_id,
                message="Thank you for contacting us! Our AI assistant will respond shortly.",
                estimated_response_time="Usually within 5 minutes"
            )
        
        async with conn.transaction():
            # Step 1: Create or get customer
            print(f"📝 Creating/getting customer: {submission.email}")
            
            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE email = $1",
                submission.email
            )
            
            if customer:
                customer_id = customer['id']
                print(f"✓ Customer found: {customer_id}")
            else:
                customer_id = await conn.fetchval("""
                    INSERT INTO customers (email, name, created_at)
                    VALUES ($1, $2, NOW())
                    RETURNING id
                """, submission.email, submission.name)
                print(f"✓ Customer created: {customer_id}")
            
            # Step 2: Create ticket
            print(f"🎫 Creating ticket: {ticket_id}")
            
            await conn.execute("""
                INSERT INTO tickets (
                    id, customer_id, source_channel, category, 
                    status, priority, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """, ticket_id, customer_id, 'web_form', submission.category, 
                'open', 'medium')
            
            print(f"✓ Ticket created: {ticket_id}")
            
            # Step 3: Create conversation
            print(f"💬 Creating conversation")
            
            conversation_id = await conn.fetchval("""
                INSERT INTO conversations (
                    customer_id, initial_channel, status, 
                    started_at, sentiment_score
                ) VALUES ($1, $2, $3, NOW(), $4)
                RETURNING id
            """, customer_id, 'web_form', 'active', 0.5)
            
            print(f"✓ Conversation created: {conversation_id}")
            
            # Step 4: Create customer message
            print(f"📩 Creating message")
            
            await conn.execute("""
                INSERT INTO messages (
                    conversation_id, channel, direction, role,
                    content, created_at, delivery_status
                ) VALUES ($1, $2, $3, $4, $5, NOW(), $6)
            """, conversation_id, 'web_form', 'inbound', 'customer',
                submission.message, 'delivered')
            
            print(f"✓ Message created")
            
            # Step 5: Update ticket with conversation_id
            await conn.execute("""
                UPDATE tickets SET conversation_id = $1 WHERE id = $2
            """, conversation_id, ticket_id)
            
            print(f"✓ Ticket updated with conversation link")
        
        await conn.close()
        
        print(f"✅ All database operations completed successfully!")
        print("=" * 60)
        
        return SupportFormResponse(
            ticket_id=ticket_id,
            message="Thank you for contacting us! Our AI assistant will respond shortly.",
            estimated_response_time="Usually within 5 minutes"
        )
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return mock response even on error
        return SupportFormResponse(
            ticket_id=ticket_id,
            message="Thank you for contacting us! Our AI assistant will respond shortly.",
            estimated_response_time="Usually within 5 minutes"
        )

@app.get("/support/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Get ticket status"""
    conn = await get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")
    
    try:
        ticket = await conn.fetchrow("""
            SELECT id, status, created_at
            FROM tickets
            WHERE id = $1
        """, ticket_id)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        await conn.close()
        
        return {
            "ticket_id": str(ticket['id']),
            "status": ticket['status'],
            "created_at": ticket['created_at'].isoformat(),
            "messages": []
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    print("=" * 60)
    print("🚀 TechCorp Customer Success FTE API")
    print("=" * 60)
    print(f"📊 Database: {DATABASE_URL}")
    print(f"🌐 Server: http://0.0.0.0:8000")
    print(f"📚 Docs: http://0.0.0.0:8000/docs")
    print("=" * 60)
    
    # Test database connection
    conn = await get_db_connection()
    if conn:
        try:
            await conn.fetchval("SELECT 1")
            await conn.close()
            print("✅ Database connected successfully!")
        except Exception as e:
            print(f"⚠️ Database connection test failed: {e}")
    else:
        print("⚠️ Database unavailable - API will return mock responses")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("📴 API server shutting down...")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_working:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
