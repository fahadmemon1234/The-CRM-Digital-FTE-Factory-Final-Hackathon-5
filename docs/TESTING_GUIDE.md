# 🧪 API TESTING GUIDE

## Test Database Integration with Frontend

---

## 📋 STEP-BY-STEP TESTING

### **Step 1: Start Backend API**

```bash
cd D:\GIAIC\Hackathon 5\production

# Option A: Using Python directly
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Option B: Using Docker (if PostgreSQL in Docker)
docker-compose up -d postgres
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
============================================================
🚀 TechCorp Customer Success FTE API
============================================================
📊 Database: postgresql://postgres:postgres@localhost:5432/luxeFlow_ai
🌐 Server: http://0.0.0.0:8000
📚 Docs: http://0.0.0.0:8000/docs
============================================================
✓ Database pool created successfully
✅ Database connected successfully!
INFO:     Application startup complete.
```

---

### **Step 2: Start Frontend**

```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

**Expected Output:**
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

### **Step 3: Test API Health**

**Browser mein open karein:**
```
http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-15T12:00:00Z",
  "database": "connected",
  "channels": {
    "email": "active",
    "whatsapp": "active",
    "web_form": "active"
  }
}
```

---

### **Step 4: Submit Support Form (Frontend)**

1. **Open Support Form:**
   ```
   http://localhost:3000/support
   ```

2. **Fill Form:**
   ```
   Name: Test User
   Email: test@example.com
   Subject: API Testing
   Category: technical
   Message: This is a test message to verify database integration is working properly.
   ```

3. **Click "Submit Support Request"**

4. **Check Browser Console (F12):**
   ```
   📤 Submitting form... {name: "Test User", email: "test@example.com", ...}
   📥 Response status: 200
   ✅ Submission successful: {ticket_id: "TKT-XXX", message: "...", ...}
   ```

5. **Success Screen:**
   - Shows ticket ID
   - Shows confirmation message

---

### **Step 5: Verify in pgAdmin (Manual Check)**

**Open pgAdmin 4:**
```
http://localhost:5050
```

**Navigate to:**
```
Servers → PostgreSQL → Databases → luxeFlow_ai → Schemas → public → Tables
```

**Check These Tables:**

#### **1. customers Table**
```sql
SELECT * FROM customers ORDER BY created_at DESC LIMIT 5;
```

**Expected Data:**
```
id (UUID) | email | name | created_at
----------|-------|------|-----------
xxx-xxx-xxx | test@example.com | Test User | 2026-03-15 12:00:00
```

---

#### **2. tickets Table**
```sql
SELECT * FROM tickets ORDER BY created_at DESC LIMIT 5;
```

**Expected Data:**
```
id | customer_id | source_channel | category | status | priority
---|-------------|----------------|----------|--------|----------
TKT-XXX | xxx-xxx-xxx | web_form | technical | open | medium
```

---

#### **3. conversations Table**
```sql
SELECT * FROM conversations ORDER BY started_at DESC LIMIT 5;
```

**Expected Data:**
```
id | customer_id | initial_channel | status | sentiment_score
---|-------------|-----------------|--------|----------------
xxx-xxx-xxx | xxx-xxx-xxx | web_form | active | 0.5
```

---

#### **4. messages Table**
```sql
SELECT * FROM messages ORDER BY created_at DESC LIMIT 5;
```

**Expected Data:**
```
id | conversation_id | channel | direction | role | content
---|-----------------|---------|-----------|------|--------
xxx-xxx-xxx | xxx-xxx-xxx | web_form | inbound | customer | "This is a test..."
```

---

## 🔧 TESTING WITH cURL (Alternative)

### **Test 1: Health Check**
```bash
curl http://localhost:8000/health
```

### **Test 2: Submit Support Form**
```bash
curl -X POST http://localhost:8000/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Database Test",
    "category": "technical",
    "message": "Testing database insertion via API"
  }'
```

**Expected Response:**
```json
{
  "ticket_id": "TKT-A1B2C3D4E",
  "message": "Thank you for contacting us! Our AI assistant will respond shortly.",
  "estimated_response_time": "Usually within 5 minutes"
}
```

### **Test 3: Get Ticket Status**
```bash
curl http://localhost:8000/support/ticket/TKT-A1B2C3D4E
```

---

## 📊 DATABASE VERIFICATION QUERIES

### **Check All Tables Have Data:**
```sql
-- Count records in each table
SELECT 
  'customers' as table_name, COUNT(*) as count FROM customers
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'messages', COUNT(*) FROM messages;
```

**Expected Output:**
```
table_name    | count
--------------|-------
customers     | 1
tickets       | 1
conversations | 1
messages      | 1
```

---

### **View Complete Ticket Flow:**
```sql
SELECT 
  t.id as ticket_id,
  t.status,
  t.category,
  c.email as customer_email,
  c.name as customer_name,
  m.content as message,
  m.created_at
FROM tickets t
JOIN customers c ON t.customer_id = c.id
JOIN conversations conv ON t.conversation_id = conv.id
JOIN messages m ON conv.id = m.conversation_id
WHERE t.id = 'TKT-YOUR-TICKET-ID'
ORDER BY m.created_at;
```

---

## 🐛 TROUBLESHOOTING

### **Issue 1: Database Connection Failed**

**Error:**
```
❌ Database connection failed: connection refused
```

**Solution:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Or check local PostgreSQL
netstat -ano | findstr :5432

# Start PostgreSQL
cd production
docker-compose up -d postgres
```

---

### **Issue 2: Table Doesn't Exist**

**Error:**
```
relation "customers" does not exist
```

**Solution:**
```bash
# Run schema
cd D:\GIAIC\Hackathon 5\production
type database\schema.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db

# OR for local PostgreSQL
psql -U postgres -d luxeFlow_ai -f database/schema.sql
```

---

### **Issue 3: CORS Error**

**Error:**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
- Already fixed in API with `allow_origins=["*"]`
- Restart API server

---

### **Issue 4: Frontend Not Submitting**

**Check:**
1. API is running on port 8000
2. Browser console shows no errors
3. Network tab shows 200 status

**Debug:**
```javascript
// Add console.log in handleSubmit
console.log("Form data:", formData)
console.log("API Response:", await response.json())
```

---

## ✅ SUCCESS CHECKLIST

After testing, verify:

- [ ] API starts successfully
- [ ] Health check returns "connected"
- [ ] Frontend form submits without errors
- [ ] Ticket ID is generated
- [ ] Success screen shows
- [ ] **customers** table has new row
- [ ] **tickets** table has new row
- [ ] **conversations** table has new row
- [ ] **messages** table has new row
- [ ] All timestamps are correct
- [ ] Data relationships are correct

---

## 📋 SAMPLE TEST DATA

Use this data for testing:

### **Test Case 1: Technical Support**
```
Name: Alice Johnson
Email: alice@techcorp.com
Subject: API Integration Issue
Category: technical
Message: I'm having trouble integrating the API with our existing system. The authentication keeps failing.
```

### **Test Case 2: Billing Inquiry**
```
Name: Bob Smith
Email: bob@company.com
Subject: Invoice Question
Category: billing
Message: I was charged twice for this month's subscription. Can you please help?
```

### **Test Case 3: Bug Report**
```
Name: Carol White
Email: carol@example.com
Subject: App Crashes on Startup
Category: bug_report
Message: The mobile app crashes immediately after opening. Using iPhone 13, iOS 16.
```

---

## 🎯 EXPECTED FLOW

```
1. User fills form on http://localhost:3000/support
   ↓
2. Frontend sends POST to http://localhost:8000/support/submit
   ↓
3. API receives data and validates
   ↓
4. API creates customer (or finds existing)
   ↓
5. API creates ticket
   ↓
6. API creates conversation
   ↓
7. API creates message
   ↓
8. API returns ticket_id
   ↓
9. Frontend shows success screen
   ↓
10. You verify in pgAdmin
```

---

## 🎉 VERIFICATION COMPLETE!

Once all checks pass:
- ✅ Frontend is connected to backend
- ✅ Backend is connected to database
- ✅ Data is being inserted correctly
- ✅ All tables are updated
- ✅ Relationships are maintained

**Your complete stack is working!** 🚀

---

**Last Updated:** 2026-03-15  
**API Version:** 2.0.0  
**Status:** ✅ Ready for Testing
