# 📚 API DOCUMENTATION

## TechCorp Customer Success FTE API

**Version:** 2.0.0  
**Base URL:** `http://localhost:8000`

---

## 🔗 Quick Links

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📋 ENDPOINTS

### **1. Health Check**

Check API health status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-15T12:00:00Z",
  "channels": {
    "email": "active",
    "whatsapp": "active",
    "web_form": "active"
  }
}
```

---

### **2. Submit Support Form**

Submit a new support request via web form.

**Endpoint:** `POST /support/submit`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "API Integration Help",
  "category": "technical",
  "message": "I need help with API authentication..."
}
```

**Response:**
```json
{
  "ticket_id": "TKT-A1B2C3D4E",
  "message": "Thank you for contacting us! Our AI assistant will respond shortly.",
  "estimated_response_time": "Usually within 5 minutes"
}
```

**Status Codes:**
- `200` - Success
- `400` - Validation Error
- `500` - Server Error

---

### **3. Get Ticket Status**

Get status and conversation history for a ticket.

**Endpoint:** `GET /support/ticket/{ticket_id}`

**Response:**
```json
{
  "ticket_id": "TKT-A1B2C3D4E",
  "status": "open",
  "messages": [
    {
      "role": "customer",
      "content": "I need help...",
      "created_at": "2026-03-15T12:00:00Z",
      "channel": "web_form"
    },
    {
      "role": "agent",
      "content": "I'd be happy to help...",
      "created_at": "2026-03-15T12:05:00Z",
      "channel": "web_form"
    }
  ],
  "created_at": "2026-03-15T12:00:00Z",
  "last_updated": "2026-03-15T12:05:00Z"
}
```

---

### **4. Lookup Customer**

Look up customer by email or phone.

**Endpoint:** `GET /customers/lookup`

**Query Parameters:**
- `email` (optional) - Customer email
- `phone` (optional) - Customer phone

**Response:**
```json
{
  "id": "uuid-here",
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2026-03-15T12:00:00Z"
}
```

---

### **5. Channel Metrics**

Get performance metrics by channel.

**Endpoint:** `GET /metrics/channels`

**Response:**
```json
{
  "web_form": {
    "channel": "web_form",
    "total_tickets": 150,
    "open": 25,
    "resolved": 120,
    "escalated": 5
  },
  "email": {
    "channel": "email",
    "total_tickets": 300,
    "open": 50,
    "resolved": 240,
    "escalated": 10
  }
}
```

---

### **6. Gmail Webhook**

Receive Gmail push notifications.

**Endpoint:** `POST /webhooks/gmail`

**Request Body:**
```json
{
  "message": {
    "data": "base64_encoded_data",
    "messageId": "msg-123"
  },
  "subscription": "projects/xxx/subscriptions/gmail"
}
```

---

### **7. WhatsApp Webhook**

Receive WhatsApp messages via Twilio.

**Endpoint:** `POST /webhooks/whatsapp`

**Request Body (Form Data):**
```
MessageSid: SM123
From: whatsapp:+1234567890
Body: Hello, I need help
ProfileName: John Doe
```

---

## 🔧 REQUEST/RESPONSE MODELS

### **SupportFormSubmission**

```typescript
{
  name: string (min 2 characters)
  email: string (email format)
  subject: string
  category: "general" | "technical" | "billing" | "bug_report" | "feedback"
  message: string (min 10 characters)
}
```

### **SupportFormResponse**

```typescript
{
  ticket_id: string
  message: string
  estimated_response_time: string
}
```

### **TicketStatus**

```typescript
{
  ticket_id: string
  status: "open" | "in_progress" | "resolved" | "escalated" | "closed"
  messages: Message[]
  created_at: string (ISO 8601)
  last_updated: string (ISO 8601)
}
```

### **Message**

```typescript
{
  role: "customer" | "agent" | "system"
  content: string
  created_at: string (ISO 8601)
  channel: "email" | "whatsapp" | "web_form"
}
```

---

## 📊 ERROR RESPONSES

### **400 Bad Request**

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### **404 Not Found**

```json
{
  "detail": "Ticket not found"
}
```

### **500 Internal Server Error**

```json
{
  "detail": "Database unavailable"
}
```

---

## 🔐 AUTHENTICATION

Currently, the API does not require authentication for public endpoints.

For production deployment, add API key authentication:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
```

---

## 🚀 RATE LIMITING

For production, implement rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/support/submit")
@limiter.limit("10/minute")
async def submit_support_form(...):
    ...
```

---

## 📝 EXAMPLES

### **cURL Examples**

#### Submit Support Form:
```bash
curl -X POST http://localhost:8000/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "API Help",
    "category": "technical",
    "message": "I need help with authentication"
  }'
```

#### Get Ticket Status:
```bash
curl http://localhost:8000/support/ticket/TKT-A1B2C3D4E
```

#### Health Check:
```bash
curl http://localhost:8000/health
```

### **JavaScript/React Example**

```javascript
// Submit support form
const submitForm = async (formData) => {
  const response = await fetch('http://localhost:8000/support/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  })
  
  const data = await response.json()
  return data.ticket_id
}

// Get ticket status
const getTicketStatus = async (ticketId) => {
  const response = await fetch(`http://localhost:8000/support/ticket/${ticketId}`)
  return await response.json()
}
```

### **Python Example**

```python
import requests

# Submit support form
response = requests.post('http://localhost:8000/support/submit', json={
    'name': 'John Doe',
    'email': 'john@example.com',
    'subject': 'API Help',
    'category': 'technical',
    'message': 'I need help'
})

ticket_id = response.json()['ticket_id']

# Get ticket status
status = requests.get(f'http://localhost:8000/support/ticket/{ticket_id}')
print(status.json())
```

---

## 🎯 WORKFLOWS

### **Support Ticket Workflow**

```
1. User submits form → POST /support/submit
2. API creates ticket → Database
3. API publishes to Kafka → AI Agent
4. AI Agent processes → Generates response
5. Response sent → User email
6. User checks status → GET /support/ticket/{id}
```

### **Cross-Channel Workflow**

```
1. User submits via Web Form → Ticket created
2. User follows up via Email → Same ticket updated
3. User messages via WhatsApp → Same ticket updated
4. All messages linked → Single conversation view
```

---

## 📚 ADDITIONAL RESOURCES

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Spec:** http://localhost:8000/openapi.json

---

**Last Updated:** 2026-03-15  
**API Version:** 2.0.0
