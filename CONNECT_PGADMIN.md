# 🔗 Connect pgAdmin 4 to Your Project

## ✅ Quick Setup Guide

### Step 1: Start the Project

**Option A: Use the Runner Script (Recommended)**
```bash
# Double-click this file:
D:\GIAIC\Hackathon 5\run-complete-project.bat

# Or run manually:
cd D:\GIAIC\Hackathon 5
run-complete-project.bat
```

**Option B: Manual Start**
```bash
# Start PostgreSQL
cd D:\GIAIC\Hackathon 5\production
docker-compose up -d postgres

# Wait 10 seconds for PostgreSQL to initialize
timeout /t 10

# Start Frontend
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

---

### Step 2: Connect pgAdmin 4

#### 2.1 Open pgAdmin 4
1. Open your browser
2. Go to: http://localhost:5050 (or wherever pgAdmin is installed)
3. Login with your pgAdmin credentials

#### 2.2 Create New Server Connection
1. **Right-click** on "Servers" in the left panel
2. Select **"Create"** → **"Server..."**
3. Fill in the details:

**General Tab:**
```
Name: TechCorp FTE Database
```

**Connection Tab:**
```
Host name/address: localhost
Port: 5432
Maintenance database: fte_db
Username: fte_user
Password: fte_password
```

**OR use Superuser (postgres):**
```
Username: postgres
Password: postgres
```

4. Click **"Save"**

---

### Step 3: Verify Connection

#### In pgAdmin 4:
1. Expand **Servers** → **TechCorp FTE Database**
2. Expand **Databases** → **fte_db**
3. Expand **Schemas** → **public**
4. Expand **Tables**

You should see these tables:
```
✓ customers
✓ customer_identifiers
✓ conversations
✓ messages
✓ tickets
✓ knowledge_base
✓ channel_configs
✓ agent_metrics
✓ alembic_version
```

---

### Step 4: Run Queries

#### View All Tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

#### View Customers
```sql
SELECT email, name, phone, metadata->>'company' as company
FROM customers
ORDER BY created_at DESC
LIMIT 10;
```

#### View Tickets
```sql
SELECT t.id, t.status, t.category, t.priority, c.email
FROM tickets t
JOIN customers c ON t.customer_id = c.id
ORDER BY t.created_at DESC
LIMIT 10;
```

#### View Conversations with Messages
```sql
SELECT 
    c.id as conversation_id,
    c.initial_channel,
    c.status,
    c.sentiment_score,
    COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, c.initial_channel, c.status, c.sentiment_score
ORDER BY c.started_at DESC;
```

#### View Knowledge Base
```sql
SELECT title, category, created_at
FROM knowledge_base
ORDER BY created_at DESC;
```

---

## 🔧 Troubleshooting

### Issue: Cannot connect to database

**Solution 1: Check if PostgreSQL is running**
```bash
docker ps | findstr postgres
```

If not running:
```bash
cd D:\GIAIC\Hackathon 5\production
docker-compose up -d postgres
```

**Solution 2: Check port 5432**
```bash
netstat -ano | findstr :5432
```

**Solution 3: Verify credentials**
```bash
docker exec -it fte-postgres psql -U fte_user -d fte_db -c "\dt"
```

---

### Issue: No tables in database

**Solution: Run schema manually**
```bash
cd D:\GIAIC\Hackathon 5\production

# Method 1: Using docker exec
type database\schema.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db

# Method 2: Copy and paste SQL
docker exec -it fte-postgres psql -U fte_user -d fte_db
# Then paste the SQL from database/schema.sql
```

**Load seed data:**
```bash
type database\seed.sql\seed_data.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db
```

---

### Issue: Authentication failed

**Reset password:**
```bash
docker exec -it fte-postgres psql -U postgres -c "ALTER USER fte_user WITH PASSWORD 'fte_password';"
```

---

## 📊 Database Schema Overview

```
fte_db (Database)
│
├── customers              - Customer identity table
├── customer_identifiers   - Cross-channel identity resolution
├── conversations          - Conversation sessions
├── messages               - Message audit trail
├── tickets                - Support tickets
├── knowledge_base         - AI knowledge base (with pgvector)
├── channel_configs        - Channel configurations
├── agent_metrics          - Performance metrics
└── alembic_version        - Database version tracking
```

---

## 🎯 Quick Database Operations

### Insert Test Customer
```sql
INSERT INTO customers (email, name, phone, metadata)
VALUES (
    'test.user@company.com',
    'Test User',
    '+1-555-9999',
    '{"tier": "enterprise", "company": "Test Corp"}'::jsonb
);
```

### Insert Test Ticket
```sql
INSERT INTO tickets (customer_id, source_channel, category, priority, status)
VALUES (
    (SELECT id FROM customers WHERE email = 'test.user@company.com'),
    'web_form',
    'technical',
    'medium',
    'open'
);
```

### View Ticket Statistics
```sql
SELECT 
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
FROM tickets
GROUP BY status
ORDER BY count DESC;
```

### View Channel Distribution
```sql
SELECT 
    initial_channel as channel,
    COUNT(*) as conversations,
    AVG(sentiment_score)::numeric(3,2) as avg_sentiment
FROM conversations
GROUP BY initial_channel
ORDER BY conversations DESC;
```

---

## 🌐 Access URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:3000 | ✅ Should be running |
| **PostgreSQL** | localhost:5432 | ✅ Running in Docker |
| **pgAdmin 4** | http://localhost:5050 | ⚠️ Install if needed |

---

## 📝 Connection String

For applications, use this connection string:

```
postgresql://fte_user:fte_password@localhost:5432/fte_db
```

For `.env` file:
```env
DATABASE_URL=postgresql://fte_user:fte_password@localhost:5432/fte_db
```

---

## ✅ Verification Checklist

- [ ] PostgreSQL container is running
- [ ] Frontend is running on port 3000
- [ ] pgAdmin 4 connection created
- [ ] Can see all 9 tables
- [ ] Can run SELECT queries
- [ ] Can view seed data
- [ ] Dashboard shows data

---

## 🎉 You're Connected!

Once you see the tables in pgAdmin 4, you can:
1. Browse customer data
2. View tickets and conversations
3. Monitor message history
4. Check analytics
5. Run custom queries

**Your project is now fully dynamic and connected to PostgreSQL!** 🚀
