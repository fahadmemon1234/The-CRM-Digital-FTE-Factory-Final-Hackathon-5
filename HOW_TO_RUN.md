# Complete Project - How to Run

**TechCorp Customer Success AI Agent (Digital FTE)**

This guide shows you how to run the **complete project** with both Backend (FastAPI) and Frontend (Next.js).

---

## 📋 Project Structure

```
D:\GIAIC\Hackathon 5\
├── production/          # Backend (FastAPI + Kafka + PostgreSQL)
├── frontend/            # Frontend (Next.js)
├── context/             # Documentation & sample data
├── tests/               # Test files
└── docs/                # API documentation
```

---

## 🚀 Quick Start Options

### Option 1: **Frontend Only** (Demo Mode) ⚡
Best for: UI/UX demonstration, no backend needed

```bash
# Just run the frontend
cd frontend
npm run dev
```

Access: http://localhost:3000

---

### Option 2: **Complete Stack** (Full System) 🔥
Best for: Full functionality with AI, database, messaging

Requires: Docker, Python 3.11+, OpenAI API Key

---

## 📖 Complete Setup Guide

### **Step 1: Prerequisites Check**

Install these first:

| Software | Version | Download |
|----------|---------|----------|
| **Node.js** | 18+ | https://nodejs.org |
| **Python** | 3.11+ | https://python.org |
| **Docker Desktop** | 20.10+ | https://docker.com |
| **Git** | Latest | https://git-scm.com |

Verify installations:

```bash
node --version      # Should show v18+
npm --version       # Should show 9+
python --version    # Should show 3.11+
docker --version    # Should show 20.10+
docker-compose --version
```

---

### **Step 2: Backend Setup (FastAPI)**

#### 2.1 Navigate to production folder

```bash
cd D:\GIAIC\Hackathon 5\production
```

#### 2.2 Configure Environment Variables

```bash
# Copy example env file
copy .env.example .env

# Edit .env with your credentials
notepad .env
```

**Required:**
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

**Optional (for full features):**
```env
TWILIO_ACCOUNT_SID=AC-your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CREDENTIALS_PATH=./credentials/google.json
```

> **Get OpenAI API Key:** https://platform.openai.com/api-keys

#### 2.3 Start Backend with Docker Compose

```bash
# Start all backend services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

**Services Started:**
- ✅ Zookeeper (port 2181)
- ✅ Kafka (port 9092)
- ✅ PostgreSQL (port 5432)
- ✅ FastAPI API (port 8000)
- ✅ Worker (background processing)
- ✅ Metrics Worker (analytics)

#### 2.4 Verify Backend

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "channels": {...}}
```

**Access:**
- 🌐 API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

---

### **Step 3: Frontend Setup (Next.js)**

#### 3.1 Navigate to frontend folder

Open **new terminal**:

```bash
cd D:\GIAIC\Hackathon 5\frontend
```

#### 3.2 Install Dependencies (first time only)

```bash
npm install
```

#### 3.3 Configure API Connection

Create `.env.local`:

```bash
# Create env file
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
```

#### 3.4 Start Frontend

```bash
npm run dev
```

**Access:** http://localhost:3000

---

## 🎯 Running the Complete Project

### **Start Everything**

**Terminal 1 - Backend:**
```bash
cd D:\GIAIC\Hackathon 5\production
docker-compose up -d
```

**Terminal 2 - Frontend:**
```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

### **Access Points**

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend UI** | http://localhost:3000 | Main application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **ReDoc** | http://localhost:8000/redoc | API Documentation |

---

## 🔧 Development Workflow

### Daily Development

```bash
# 1. Start backend (Terminal 1)
cd production
docker-compose up -d

# 2. Start frontend (Terminal 2)
cd frontend
npm run dev

# 3. Make changes to code
# - Frontend: Auto-reloads on save
# - Backend: Auto-reloads on save (if configured)

# 4. View logs
docker-compose logs -f fte-api
docker-compose logs -f fte-worker
```

### Stopping Everything

```bash
# Stop backend
cd production
docker-compose down

# Stop frontend
# Press Ctrl+C in the terminal running npm run dev
```

### Reset Everything (Clean State)

```bash
# Stop and remove all containers + volumes
cd production
docker-compose down -v

# Remove node_modules (optional)
cd ../frontend
rm -rf node_modules
rm package-lock.json

# Reinstall
npm install

# Restart
docker-compose up -d
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│                     http://localhost:3000                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                          │
│  - Dashboard UI                                              │
│  - Ticket Management                                         │
│  - Analytics Charts                                          │
│  - AI Response Suggestions                                   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                           │
│                   http://localhost:8000                      │
│  - REST API Endpoints                                        │
│  - Web Form Handler                                          │
│  - Ticket Management                                         │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │   Kafka    │  │ PostgreSQL │  │  OpenAI    │
     │  Message   │  │  Database  │  │    API     │
     │   Broker   │  │  +pgvector │  │  (GPT-4o)  │
     └────────────┘  └────────────┘  └────────────┘
```

---

## 🧪 Testing

### Backend Tests

```bash
cd production

# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=production --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Run tests (when configured)
npm run test

# Build check
npm run build
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Submit support ticket
curl -X POST http://localhost:8000/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test Ticket",
    "category": "general",
    "message": "This is a test message"
  }'

# Get ticket status
curl http://localhost:8000/support/ticket/TKT-123
```

---

## 🔍 Troubleshooting

### Backend Issues

**Problem:** Docker containers won't start

```bash
# Check Docker is running
docker ps

# View container logs
docker-compose logs

# Restart services
docker-compose restart

# Full reset
docker-compose down -v
docker-compose up -d
```

**Problem:** Port already in use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /F /PID <PID>
```

**Problem:** Database connection failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Frontend Issues

**Problem:** npm install fails

```bash
# Clear cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules
rm package-lock.json

# Reinstall
npm install
```

**Problem:** Port 3000 already in use

```bash
# Find and kill process
netstat -ano | findstr :3000
taskkill /F /PID <PID>

# Or use different port
npm run dev -- -p 3001
```

**Problem:** API connection failed

```bash
# Check backend is running
curl http://localhost:8000/health

# Update .env.local
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local

# Restart frontend
# Ctrl+C, then npm run dev
```

---

## 📝 Environment Variables Reference

### Backend (.env)

```env
# Required
OPENAI_API_KEY=sk-...

# Optional - Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Optional - Google
GOOGLE_CLOUD_PROJECT=...
GOOGLE_CREDENTIALS_PATH=./credentials/google.json

# App Settings
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=INFO

# Database (Docker defaults)
DATABASE_URL=postgresql://fte_user:fte_password@postgres:5432/fte_db

# Kafka (Docker defaults)
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Feature Flags
ENABLE_EMAIL_CHANNEL=true
ENABLE_WHATSAPP_CHANNEL=true
ENABLE_WEB_FORM=true
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_ENABLE_AI_SUGGESTIONS=true
```

---

## 🎓 Learning Path

### Day 1: Frontend Demo
1. Run frontend only: `npm run dev`
2. Explore UI: Landing → Login → Dashboard
3. Check tickets and analytics pages

### Day 2: Backend Setup
1. Configure `.env` with OpenAI key
2. Start Docker Compose
3. Test API endpoints

### Day 3: Full Integration
1. Connect frontend to backend
2. Test ticket submission
3. Verify AI responses

### Day 4: Advanced Features
1. Configure WhatsApp (Twilio)
2. Configure Email (Gmail)
3. Test multi-channel support

---

## 📞 Quick Reference

### Commands Cheat Sheet

```bash
# ========== BACKEND ==========
cd production

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset everything
docker-compose down -v

# Check health
curl http://localhost:8000/health


# ========== FRONTEND ==========
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run linter
npm run lint
```

### Important URLs

```
Frontend:        http://localhost:3000
Backend API:     http://localhost:8000
API Docs:        http://localhost:8000/docs
ReDoc:           http://localhost:8000/redoc
PostgreSQL:      localhost:5432
Kafka:           localhost:9092
```

---

## ✅ Verification Checklist

Before going to production, verify:

- [ ] Backend containers running: `docker-compose ps`
- [ ] API health check passes: `curl localhost:8000/health`
- [ ] Frontend loads: http://localhost:3000
- [ ] Login page accessible
- [ ] Dashboard loads with data
- [ ] Tickets page shows tickets
- [ ] Analytics charts render
- [ ] API docs accessible
- [ ] Database connected
- [ ] Kafka messages flowing

---

## 🎉 Success!

If everything is running:

1. ✅ Open http://localhost:3000
2. ✅ See beautiful landing page
3. ✅ Navigate to login
4. ✅ Access dashboard
5. ✅ View tickets and analytics
6. ✅ Backend API responding
7. ✅ Database storing data
8. ✅ Kafka processing messages

**You're all set!** 🚀

---

## 📚 Additional Resources

- **Backend Docs:** `production/README.md`
- **Frontend Docs:** `frontend/README.md`
- **API Spec:** `docs/api-reference.md`
- **Sample Data:** `context/sample-tickets.json`

---

**Need Help?** Check individual README files or contact support.

**Happy Coding!** 💻✨
