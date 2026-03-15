# 🚀 COMPLETE SETUP GUIDE

## TechCorp Customer Success FTE - Hackathon 5

**Version:** 2.0.0  
**Last Updated:** 2026-03-15

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Project](#running-the-project)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 PREREQUISITES

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend runtime |
| **Docker** | 20.10+ | Containerization |
| **Docker Compose** | 2.0+ | Local development |
| **PostgreSQL** | 16+ | Database |

### Required Accounts

| Service | Purpose | Setup Guide |
|---------|---------|-------------|
| **OpenAI** | AI Agent (GPT-4o) | https://platform.openai.com |
| **Google Cloud** | Gmail API (Optional) | See [Gmail Setup](#gmail-setup) |
| **Twilio** | WhatsApp API (Optional) | See [WhatsApp Setup](#whatsapp-setup) |

---

## 📦 INSTALLATION

### Step 1: Clone Repository

```bash
cd D:\GIAIC\Hackathon 5
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 3: Install Backend Dependencies

```bash
cd production
pip install -r requirements.txt
cd ..
```

### Step 4: Setup Database

**Option A: Using Docker (Recommended)**

```bash
cd production
docker-compose up -d postgres
```

**Option B: Using Local PostgreSQL**

```bash
# Create database
psql -U postgres -c "CREATE DATABASE luxeFlow_ai;"

# Run schema
psql -U postgres -d luxeFlow_ai -f production/database/schema.sql

# Load seed data
psql -U postgres -d luxeFlow_ai -f production/database/seed.sql/seed_data.sql
```

---

## ⚙️ CONFIGURATION

### Environment Variables

Create `.env` file in `production/` directory:

```env
# ============================================================================
# REQUIRED: OpenAI API Key
# ============================================================================
OPENAI_API_KEY=sk-your-api-key-here

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/luxeFlow_ai

# ============================================================================
# KAFKA CONFIGURATION
# ============================================================================
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# ============================================================================
# OPTIONAL: Twilio (WhatsApp Channel)
# ============================================================================
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# ============================================================================
# OPTIONAL: Google Cloud (Gmail Channel)
# ============================================================================
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CREDENTIALS_PATH=./credentials/google.json
```

---

## 🏃 RUNNING THE PROJECT

### Quick Start (Recommended)

**Use the auto-start script:**

```bash
# Double-click this file:
D:\GIAIC\Hackathon 5\AUTO-START.bat
```

### Manual Start

#### 1. Start Backend

```bash
cd D:\GIAIC\Hackathon 5\production
docker-compose up -d
```

Or run locally:

```bash
cd D:\GIAIC\Hackathon 5\production
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Start Frontend

```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

#### 3. Verify Services

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

---

## 🌐 ACCESS URLS

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:3000 | ✅ |
| **API Docs** | http://localhost:8000/docs | ✅ |
| **Health Check** | http://localhost:8000/health | ✅ |
| **Support Form** | http://localhost:3000/support | ✅ |
| **Dashboard** | http://localhost:3000/dashboard | ✅ |

---

## 🧪 TESTING

### Run Unit Tests

```bash
cd production
pytest tests/ -v
```

### Run E2E Tests

```bash
cd production
pytest tests/test_multichannel_e2e.py -v
```

### Run Load Tests

```bash
cd production
locust -f tests/load_test.py --host=http://localhost:8000
```

Then open: http://localhost:8080

---

## 📊 CHANNEL SETUP (OPTIONAL)

### Gmail Setup

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com

2. **Create New Project**

3. **Enable APIs:**
   - Gmail API
   - Cloud Pub/Sub API

4. **Create Service Account:**
   - IAM & Admin → Service Accounts
   - Create service account
   - Download JSON credentials

5. **Set Up Pub/Sub:**
   ```bash
   gcloud pubsub topics create fte-gmail-notifications
   gcloud pubsub subscriptions create fte-gmail-sub \
     --topic=fte-gmail-notifications
   ```

6. **Add to `.env`:**
   ```env
   GOOGLE_CREDENTIALS_PATH=./credentials/google.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   ```

### WhatsApp Setup

1. **Go to Twilio:**
   - https://www.twilio.com

2. **Sign Up / Login**

3. **Enable WhatsApp Sandbox:**
   - Messaging → Try it out → WhatsApp
   - Follow instructions to join sandbox

4. **Get Credentials:**
   - Account SID
   - Auth Token
   - WhatsApp Number

5. **Add to `.env`:**
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

### Web Form Setup

Web form is already built! Just access it:

```
http://localhost:3000/support
```

---

## 🚀 DEPLOYMENT

### Docker Deployment

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Kubernetes Deployment

```bash
# Apply namespace
kubectl apply -f production/k8s/namespace.yaml

# Apply config
kubectl apply -f production/k8s/configmap.yaml
kubectl apply -f production/k8s/secrets.yaml

# Deploy services
kubectl apply -f production/k8s/deployment-api.yaml
kubectl apply -f production/k8s/deployment-worker.yaml

# Apply service
kubectl apply -f production/k8s/service.yaml

# Apply ingress
kubectl apply -f production/k8s/ingress.yaml
```

---

## 🐛 TROUBLESHOOTING

### Frontend Issues

**Problem:** Frontend won't start

```bash
# Clear cache
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

**Problem:** Port 3000 already in use

```bash
# Use different port
npm run dev -- -p 3001
```

### Backend Issues

**Problem:** Database connection failed

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check connection
docker exec -it fte-postgres psql -U fte_user -d fte_db -c "SELECT 1"
```

**Problem:** Port 8000 already in use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /F /PID <PID>
```

### Docker Issues

**Problem:** Docker won't start

```bash
# Restart Docker Desktop
# Or on Linux:
sudo systemctl restart docker
```

**Problem:** Containers won't start

```bash
# Clean up
docker-compose down -v
docker-compose up -d
```

---

## 📁 PROJECT STRUCTURE

```
D:\GIAIC\Hackathon 5\
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App router pages
│   │   │   ├── dashboard/   # Dashboard pages
│   │   │   ├── support/     # Support form
│   │   │   └── login/       # Auth pages
│   │   └── components/      # UI components
│   └── package.json
│
├── production/               # Backend services
│   ├── api/                 # FastAPI endpoints
│   ├── agent/               # AI agent logic
│   ├── channels/            # Channel handlers
│   ├── database/            # Database schema
│   ├── workers/             # Kafka workers
│   └── docker-compose.yml
│
├── docs/                     # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── SETUP_GUIDE.md
│   └── RUNBOOK.md
│
└── context/                  # Company context
    ├── company-profile.md
    ├── product-docs.md
    └── sample-tickets.json
```

---

## ✅ VERIFICATION CHECKLIST

### Before Submission

- [ ] Frontend running on port 3000
- [ ] Backend running on port 8000
- [ ] Database connected
- [ ] Support form working
- [ ] Dashboard displaying data
- [ ] All pages accessible
- [ ] API documentation complete
- [ ] Tests passing

### Hackathon Deliverables

- [ ] Web Support Form (REQUIRED)
- [ ] Dashboard with stats
- [ ] PostgreSQL schema
- [ ] FastAPI endpoints
- [ ] Documentation complete
- [ ] README updated
- [ ] Architecture diagram

---

## 📞 QUICK COMMANDS

### Start Everything

```bash
# Auto-start
AUTO-START.bat

# Or manually:
cd production && docker-compose up -d
cd frontend && npm run dev
```

### Stop Everything

```bash
# Auto-stop
AUTO-STOP.bat

# Or manually:
cd production && docker-compose down
```

### Check Status

```bash
# Auto-status
AUTO-STATUS.bat

# Or manually:
docker ps
curl http://localhost:8000/health
```

---

## 🎯 HACKATHON DEMO FLOW

### 1. Show Landing Page
```
http://localhost:3000
```

### 2. Submit Support Ticket
```
http://localhost:3000/support
```

### 3. Show Dashboard
```
http://localhost:3000/dashboard
```

### 4. Show Channels Page
```
http://localhost:3000/dashboard/channels
```

### 5. Show API Documentation
```
http://localhost:8000/docs
```

---

## 📚 ADDITIONAL RESOURCES

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **GitHub Issues:** Report bugs here
- **Email:** support@techcorp.com

---

**Last Updated:** 2026-03-15  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
