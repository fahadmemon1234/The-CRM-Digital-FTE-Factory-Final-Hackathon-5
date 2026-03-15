# TechCorp Customer Success AI Agent - API Reference

**Version:** 2.0.0  
**Base URL:** `https://support-api.yourdomain.com`  
**Authentication:** Bearer token (where required)

---

## Authentication

Most endpoints are public. Protected endpoints require a Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
    https://support-api.yourdomain.com/protected-endpoint
```

---

## Endpoints

### GET /

**Description:** API information and available endpoints.

**Auth Required:** No

**Response Schema:**
```json
{
  "name": "string",
  "version": "string",
  "description": "string",
  "docs": "string",
  "health": "string",
  "channels": {
    "email": "string",
    "whatsapp": "string",
    "web_form": "string"
  }
}
```

**Example:**
```bash
curl https://support-api.yourdomain.com/
```

**Response:**
```json
{
  "name": "Customer Success FTE API",
  "version": "2.0.0",
  "description": "24/7 AI-powered customer support",
  "docs": "/docs",
  "health": "/health",
  "channels": {
    "email": "active",
    "whatsapp": "active",
    "web_form": "active"
  }
}
```

---

### GET /health

**Description:** Health check endpoint for monitoring.

**Auth Required:** No

**Response Schema:**
```json
{
  "status": "string",
  "timestamp": "string (ISO8601)",
  "channels": {
    "email": "string",
    "whatsapp": "string",
    "web_form": "string"
  }
}
```

**Example:**
```bash
curl https://support-api.yourdomain.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T12:00:00Z",
  "channels": {
    "email": "active",
    "whatsapp": "active",
    "web_form": "active"
  }
}
```

---

### GET /topics

**Description:** List all Kafka topics.

**Auth Required:** No

**Response Schema:**
```json
{
  "topics": {
    "key": "value"
  }
}
```

**Example:**
```bash
curl https://support-api.yourdomain.com/topics
```

---

### POST /support/submit

**Description:** Submit a support form.

**Auth Required:** No

**Request Body Schema:**
```json
{
  "name": "string (required, min 2 chars)",
  "email": "string (required, email format)",
  "subject": "string (required, min 5 chars)",
  "category": "string (required, one of: general, technical, billing, feedback, bug_report)",
  "message": "string (required, min 10 chars, max 10000)",
  "priority": "string (optional, default: medium, one of: low, medium, high)",
  "attachments": "array (optional, URLs)"
}
```

**Response Schema:**
```json
{
  "ticket_id": "string",
  "message": "string",
  "estimated_response_time": "string"
}
```

**Example:**
```bash
curl -X POST https://support-api.yourdomain.com/support/submit \
    -H "Content-Type: application/json" \
    -d '{
        "name": "John Doe",
        "email": "john@example.com",
        "subject": "API Authentication Issue",
        "category": "technical",
        "message": "I am unable to authenticate with the API. Getting 401 errors."
    }'
```

**Response:**
```json
{
  "ticket_id": "tkt_abc123",
  "message": "Thank you John! Your support request has been received.",
  "estimated_response_time": "Usually within 5 minutes"
}
```

**Error Responses:**
- `422`: Validation error
- `500`: Internal server error

---

### GET /support/ticket/{ticket_id}

**Description:** Get ticket status and messages.

**Auth Required:** No

**Path Parameters:**
- `ticket_id`: Ticket UUID

**Response Schema:**
```json
{
  "ticket_id": "string",
  "status": "string",
  "messages": [
    {
      "id": "string",
      "role": "string",
      "content": "string",
      "channel": "string",
      "created_at": "string"
    }
  ],
  "created_at": "string",
  "last_updated": "string"
}
```

**Example:**
```bash
curl https://support-api.yourdomain.com/support/ticket/tkt_abc123
```

**Response:**
```json
{
  "ticket_id": "tkt_abc123",
  "status": "open",
  "messages": [
    {
      "id": "msg_001",
      "role": "customer",
      "content": "I need help with...",
      "channel": "web_form",
      "created_at": "2025-01-20T12:00:00Z"
    }
  ],
  "created_at": "2025-01-20T12:00:00Z",
  "last_updated": "2025-01-20T12:00:00Z"
}
```

**Error Responses:**
- `404`: Ticket not found

---

### POST /webhooks/gmail

**Description:** Gmail Pub/Sub webhook for incoming emails.

**Auth Required:** Pub/Sub signature

**Request Body Schema:**
```json
{
  "message": {
    "data": "string (base64 encoded)",
    "messageId": "string"
  },
  "subscription": "string"
}
```

**Response Schema:**
```json
{
  "status": "string",
  "count": "integer"
}
```

**Example:**
```bash
curl -X POST https://support-api.yourdomain.com/webhooks/gmail \
    -H "Content-Type: application/json" \
    -d '{
        "message": {
            "data": "dGVzdCBub3RpZmljYXRpb24=",
            "messageId": "test-123"
        },
        "subscription": "projects/my-project/subscriptions/gmail-push"
    }'
```

**Response:**
```json
{
  "status": "processed",
  "count": 1
}
```

---

### POST /webhooks/whatsapp

**Description:** WhatsApp (Twilio) webhook for incoming messages.

**Auth Required:** Twilio signature

**Request Body (Form Data):**
```
MessageSid=SM123
From=whatsapp:+1234567890
Body=Hello
ProfileName=Test User
```

**Response:** TwiML XML

**Example:**
```bash
curl -X POST https://support-api.yourdomain.com/webhooks/whatsapp \
    -d "MessageSid=SM123" \
    -d "From=whatsapp:+1234567890" \
    -d "Body=Hello"
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>
```

---

### POST /webhooks/whatsapp/status

**Description:** WhatsApp (Twilio) status webhook.

**Auth Required:** Twilio signature

**Request Body (Form Data):**
```
MessageSid=SM123
MessageStatus=delivered
```

**Response Schema:**
```json
{
  "status": "string"
}
```

**Example:**
```bash
curl -X POST https://support-api.yourdomain.com/webhooks/whatsapp/status \
    -d "MessageSid=SM123" \
    -d "MessageStatus=delivered"
```

**Response:**
```json
{
  "status": "received"
}
```

---

### GET /conversations/{conversation_id}

**Description:** Get conversation history.

**Auth Required:** Yes

**Path Parameters:**
- `conversation_id`: Conversation UUID

**Response Schema:**
```json
{
  "conversation_id": "string",
  "messages": [
    {
      "id": "string",
      "role": "string",
      "content": "string",
      "channel": "string",
      "timestamp": "string"
    }
  ],
  "count": "integer"
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
    https://support-api.yourdomain.com/conversations/conv_abc123
```

**Error Responses:**
- `404`: Conversation not found

---

### GET /customers/lookup

**Description:** Look up customer by email or phone.

**Auth Required:** Yes

**Query Parameters:**
- `email`: Customer email (optional, but at least one required)
- `phone`: Customer phone (optional, but at least one required)

**Response Schema:**
```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "phone": "string",
  "created_at": "string",
  "metadata": {}
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
    "https://support-api.yourdomain.com/customers/lookup?email=john@example.com"
```

**Error Responses:**
- `400`: Neither email nor phone provided
- `404`: Customer not found

---

### GET /metrics/channels

**Description:** Get channel performance metrics for last 24 hours.

**Auth Required:** Yes

**Response Schema:**
```json
{
  "period": "string",
  "channels": {
    "email": {
      "total_conversations": "integer",
      "avg_sentiment": "number",
      "escalations": "integer"
    },
    "whatsapp": {...},
    "web_form": {...}
  },
  "timestamp": "string"
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
    https://support-api.yourdomain.com/metrics/channels
```

**Response:**
```json
{
  "period": "24h",
  "channels": {
    "email": {
      "total_conversations": 150,
      "avg_sentiment": 0.75,
      "escalations": 5
    },
    "whatsapp": {
      "total_conversations": 200,
      "avg_sentiment": 0.80,
      "escalations": 3
    },
    "web_form": {
      "total_conversations": 100,
      "avg_sentiment": 0.70,
      "escalations": 2
    }
  },
  "timestamp": "2025-01-20T12:00:00Z"
}
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Invalid webhook signature |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/support/submit` | 100 | per minute per IP |
| `/health` | No limit | - |
| `/customers/lookup` | 60 | per minute per API key |
| `/metrics/channels` | 30 | per minute per API key |
| Webhooks | No limit | - |

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp for reset

---

## Web Form Embed

### HTML iframe

```html
<!-- Embed in any website -->
<iframe 
    src="https://support-api.yourdomain.com/support/form"
    width="100%"
    height="600"
    frameborder="0"
    style="border-radius: 8px;"
></iframe>
```

### React Component

```bash
# Install package
npm install @techcorp/support-form
```

```jsx
// Import and use
import SupportForm from '@techcorp/support-form';

function App() {
    return (
        <SupportForm 
            apiEndpoint="https://support-api.yourdomain.com/api/support/submit"
            onSuccess={(ticketId) => {
                console.log('Ticket created:', ticketId);
                alert('Thank you! Your ticket ID is: ' + ticketId);
            }}
            onError={(error) => {
                console.error('Error:', error);
                alert('Sorry, there was an error. Please try again.');
            }}
        />
    );
}
```

### Vanilla JavaScript

```html
<!-- Include script -->
<script src="https://support-api.yourdomain.com/static/support-form.js"></script>

<!-- Create container -->
<div id="support-form-container"></div>

<!-- Initialize -->
<script>
    TechCorpSupportForm.init({
        container: '#support-form-container',
        apiEndpoint: 'https://support-api.yourdomain.com/api/support/submit',
        onSuccess: function(ticketId) {
            console.log('Ticket:', ticketId);
        }
    });
</script>
```

---

**End of API Reference**
