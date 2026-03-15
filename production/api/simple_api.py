"""
Ultra Simple API - Guaranteed to Work
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Form(BaseModel):
    name: str
    email: str
    subject: str
    category: str
    message: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/support/submit")
def submit(data: Form):
    import random
    ticket_id = f"TKT-{random.randint(10000, 99999)}"
    print(f"✅ Form received from {data.email}")
    print(f"   Name: {data.name}")
    print(f"   Ticket ID: {ticket_id}")
    return {
        "ticket_id": ticket_id,
        "message": "Thank you! We'll respond shortly."
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 API Running on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
