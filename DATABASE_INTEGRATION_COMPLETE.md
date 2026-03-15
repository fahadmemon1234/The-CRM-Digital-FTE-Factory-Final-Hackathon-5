# ✅ COMPLETE DATABASE INTEGRATION GUIDE

## 🎯 HOW DATA FLOWS FROM FRONTEND TO DATABASE

---

## 📊 COMPLETE FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    USER FILLS FORM                          │
│              http://localhost:3000/support                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ 1. User submits form
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND (Next.js)                         │
│  - Collects form data                                       │
│  - Validates fields                                         │
│  - Sends POST to API                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ 2. HTTP POST Request
                      │ JSON: {name, email, subject, category, message}
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                          │
│  - Receives request                                         │
│  - Validates data                                           │
│  - Connects to database                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ 3. SQL Queries
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL)                          │
│  - customers table ← New customer                           │
│  - tickets table ← New ticket                               │
│  - conversations table ← New conversation                   │
│  - messages table ← New message                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ TABLES UPDATED (4 Tables)

### **1. customers Table**
**Purpose:** Store customer information

**SQL:**
```sql
INSERT INTO customers (email, name, created_at)
VALUES ('test@example.com', 'Test User', NOW())
```

**Data:**
```
id: uuid-generated
email: test@example.com
name: Test User
created_at: 2026-03-15 12:00:00
```

---

### **2. tickets Table**
**Purpose:** Track support tickets

**SQL:**
```sql
INSERT INTO tickets (
    id, customer_id, source_channel, category, 
    status, priority, created_at
)
VALUES (
    'TKT-XXX', 'customer-uuid', 'web_form', 
    'technical', 'open', 'medium', NOW()
)
```

**Data:**
```
id: TKT-A1B2C3D4E
customer_id: uuid-from-customers-table
source_channel: web_form
category: technical
status: open
priority: medium
created_at: 2026-03-15 12:00:00
```

---

### **3. conversations Table**
**Purpose:** Track conversation sessions

**SQL:**
```sql
INSERT INTO conversations (
    customer_id, initial_channel, status, 
    started_at, sentiment_score
)
VALUES (
    'customer-uuid', 'web_form', 'active', 
    NOW(), 0.5
)
```

**Data:**
```
id: uuid-generated
customer_id: uuid-from-customers-table
initial_channel: web_form
status: active
sentiment_score: 0.5
started_at: 2026-03-15 12:00:00
```

---

### **4. messages Table**
**Purpose:** Store message content

**SQL:**
```sql
INSERT INTO messages (
    conversation_id, channel, direction, role,
    content, created_at, delivery_status
)
VALUES (
    'conversation-uuid', 'web_form', 'inbound', 
    'customer', 'Test message...', NOW(), 'delivered'
)
```

**Data:**
```
id: uuid-generated
conversation_id: uuid-from-conversations-table
channel: web_form
direction: inbound
role: customer
content: "This is a test message..."
created_at: 2026-03-15 12:00:00
delivery_status: delivered
```

---

## 🚀 HOW TO TEST

### **Option 1: Quick Test (Recommended)**

**Step 1: Start API**
```bash
# Double-click this file:
D:\GIAIC\Hackathon 5\test-api.bat

# Or manually:
cd D:\GIAIC\Hackathon 5\production
python -m uvicorn api.main:app --reload
```

**Step 2: Start Frontend**
```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

**Step 3: Open Support Form**
```
http://localhost:3000/support
```

**Step 4: Fill & Submit Form**
```
Name: Test User
Email: test@example.com
Subject: Database Test
Category: technical
Message: Testing database integration
```

**Step 5: Check Console (F12)**
```
📤 Submitting form... {name: "Test User", ...}
📥 Response status: 200
✅ Submission successful: {ticket_id: "TKT-XXX", ...}
```

**Step 6: Check pgAdmin**
```
1. Open pgAdmin 4
2. Navigate to: luxeFlow_ai → Tables
3. Right-click each table → View/Edit Data
4. See your new data!
```

---

### **Option 2: Direct API Test (cURL)**

**Test Submission:**
```bash
curl -X POST http://localhost:8000/support/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"John Doe\",
    \"email\": \"john@example.com\",
    \"subject\": \"API Test\",
    \"category\": \"technical\",
    \"message\": \"Testing via cURL\"
  }"
```

**Expected Response:**
```json
{
  "ticket_id": "TKT-A1B2C3D4E",
  "message": "Thank you for contacting us!",
  "estimated_response_time": "Usually within 5 minutes"
}
```

---

## 🔍 VERIFY IN pgAdmin

### **Quick Queries:**

#### **1. Check Customers:**
```sql
SELECT * FROM customers ORDER BY created_at DESC LIMIT 5;
```

#### **2. Check Tickets:**
```sql
SELECT * FROM tickets ORDER BY created_at DESC LIMIT 5;
```

#### **3. Check Complete Flow:**
```sql
SELECT 
  t.id as ticket_id,
  t.status,
  c.name as customer_name,
  c.email as customer_email,
  m.content as message,
  m.created_at
FROM tickets t
JOIN customers c ON t.customer_id = c.id
JOIN conversations conv ON t.conversation_id = conv.id
JOIN messages m ON conv.id = m.conversation_id
ORDER BY m.created_at DESC;
```

---

## 📊 WHAT TO CHECK IN EACH TABLE

### **customers Table:**
- [ ] New row created
- [ ] Email matches form input
- [ ] Name matches form input
- [ ] Timestamp is current

### **tickets Table:**
- [ ] New row created
- [ ] Ticket ID generated (TKT-XXX)
- [ ] customer_id links to customers table
- [ ] source_channel = 'web_form'
- [ ] category matches form selection
- [ ] status = 'open'
- [ ] priority = 'medium'

### **conversations Table:**
- [ ] New row created
- [ ] customer_id links to customers table
- [ ] initial_channel = 'web_form'
- [ ] status = 'active'
- [ ] sentiment_score = 0.5 (default)

### **messages Table:**
- [ ] New row created
- [ ] conversation_id links to conversations table
- [ ] channel = 'web_form'
- [ ] direction = 'inbound'
- [ ] role = 'customer'
- [ ] content matches form message
- [ ] delivery_status = 'delivered'

---

## 🎯 SUCCESS CRITERIA

After testing, you should see:

### **Frontend:**
- ✅ Form submits without errors
- ✅ Success screen appears
- ✅ Ticket ID is displayed
- ✅ No console errors

### **Backend:**
- ✅ API receives request
- ✅ No server errors
- ✅ Returns 200 status
- ✅ Logs show all operations completed

### **Database:**
- ✅ 1 row in customers
- ✅ 1 row in tickets
- ✅ 1 row in conversations
- ✅ 1 row in messages
- ✅ All relationships correct
- ✅ Timestamps accurate

---

## 🐛 COMMON ISSUES & SOLUTIONS

### **Issue 1: "Database connection failed"**

**Solution:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Or start local PostgreSQL
net start postgresql-x64-16
```

---

### **Issue 2: "Table doesn't exist"**

**Solution:**
```bash
# Run schema
cd D:\GIAIC\Hackathon 5\production
type database\schema.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db
```

---

### **Issue 3: "CORS error"**

**Solution:**
- API already has `allow_origins=["*"]`
- Restart API server
- Clear browser cache

---

### **Issue 4: "Frontend won't submit"**

**Check:**
1. API running on port 8000?
2. Browser console shows errors?
3. Network tab shows 200 status?

**Debug:**
```javascript
// Add to handleSubmit
console.log("Form data:", formData)
console.log("API Response:", response)
```

---

## 📋 TEST CHECKLIST

Use this checklist for each test:

### **Test Run #1:**
- [ ] API started successfully
- [ ] Frontend started successfully
- [ ] Form submitted
- [ ] Ticket ID received
- [ ] customers table updated
- [ ] tickets table updated
- [ ] conversations table updated
- [ ] messages table updated

### **Test Run #2:**
- [ ] Different email used
- [ ] Different category selected
- [ ] All tables updated correctly
- [ ] Relationships maintained

### **Test Run #3:**
- [ ] Same email used (should update existing customer)
- [ ] New ticket created
- [ ] Customer not duplicated

---

## 🎉 VERIFICATION COMPLETE!

When all checks pass:

```
✅ Frontend → Backend → Database flow working
✅ All 4 tables being updated
✅ Data relationships correct
✅ No errors in console
✅ No errors in server logs
✅ pgAdmin shows correct data
```

**Your complete stack is working perfectly!** 🚀

---

## 📞 QUICK COMMANDS

### **Start Everything:**
```bash
# Terminal 1 - API
cd D:\GIAIC\Hackathon 5\production
python -m uvicorn api.main:app --reload

# Terminal 2 - Frontend
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

### **Test Form:**
```
http://localhost:3000/support
```

### **Check API:**
```
http://localhost:8000/health
```

### **Check Database:**
```
Open pgAdmin 4 → luxeFlow_ai → Tables
```

---

**Last Updated:** 2026-03-15  
**Status:** ✅ Ready for Testing  
**Tables:** 4 tables auto-updated  
**Flow:** Frontend → API → Database ✅
