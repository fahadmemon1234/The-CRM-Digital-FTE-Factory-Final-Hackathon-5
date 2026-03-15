"""
Simple Test API - No Database Required
For testing frontend connection
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="Test API", version="1.0.0")

# CORS - Allow ALL origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Pydantic model for request validation
class SupportFormSubmission(BaseModel):
    name: str
    email: str
    subject: str
    category: str
    message: str

@app.get("/")
def root():
    return JSONResponse(content={"name": "TechCorp Test API", "status": "running"})

@app.get("/health")
def health():
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected (mock)",
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    })

@app.post("/support/submit")
def submit_support_form(data: SupportFormSubmission):
    """Support form submission with validation"""
    ticket_id = f"TKT-{uuid.uuid4().hex[:9].upper()}"
    
    print("=" * 60)
    print("✅ Form submitted successfully!")
    print("=" * 60)
    print(f"   Ticket ID: {ticket_id}")
    print(f"   Name: {data.name}")
    print(f"   Email: {data.email}")
    print(f"   Subject: {data.subject}")
    print(f"   Category: {data.category}")
    print(f"   Message: {data.message[:50]}...")
    print("=" * 60)
    
    return JSONResponse(content={
        "ticket_id": ticket_id,
        "message": "Thank you for contacting us! Our AI assistant will respond shortly.",
        "estimated_response_time": "Usually within 5 minutes"
    })

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Simple Test API Server")
    print("=" * 60)
    print("📊 No database required (mock mode)")
    print("🌐 Server: http://0.0.0.0:8000")
    print("📚 Docs: http://0.0.0.0:8000/docs")
    print("✅ CORS: Enabled for all origins")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
