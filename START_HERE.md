# 🚀 Quick Start - Run Complete Project

## ⚡ Fastest Way (3 Steps)

### Step 1: Start Everything

**Double-click:** `start-all.bat`

Or manually:

```bash
# Terminal 1 - Backend
cd production
docker-compose up -d

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

---

### Step 2: Access Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

---

### Step 3: Explore!

1. Open http://localhost:3000
2. See landing page
3. Click "Sign In" → Login page
4. Navigate to Dashboard
5. Explore Tickets & Analytics

---

## 📋 Prerequisites

Install these first:

- ✅ [Node.js 18+](https://nodejs.org)
- ✅ [Python 3.11+](https://python.org)
- ✅ [Docker Desktop](https://docker.com)

---

## 🛑 Stop Everything

**Double-click:** `stop-all.bat`

Or manually:

```bash
cd production
docker-compose down

# Frontend: Press Ctrl+C in terminal
```

---

## 📁 Project Structure

```
Hackathon 5/
├── start-all.bat         ← Run this to start everything
├── stop-all.bat          ← Run this to stop everything
├── HOW_TO_RUN.md         ← Detailed instructions
├── QUICK_START.md        ← Frontend guide
│
├── production/           ← Backend (FastAPI + Docker)
│   ├── docker-compose.yml
│   ├── .env
│   └── api/
│
└── frontend/             ← Frontend (Next.js)
    ├── src/app/
    └── package.json
```

---

## 🔧 Common Commands

### Backend

```bash
cd production

# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
```

### Frontend

```bash
cd frontend

# Start dev server
npm run dev

# Build production
npm run build

# Start production
npm run start

# Run linter
npm run lint
```

---

## 🎯 What Runs When You Start

### Backend Services (Docker)

| Service | Port | Purpose |
|---------|------|---------|
| **FastAPI API** | 8000 | REST API endpoints |
| **PostgreSQL** | 5432 | Database |
| **Kafka** | 9092 | Message broker |
| **Zookeeper** | 2181 | Kafka coordination |
| **Worker** | - | Message processor |
| **Metrics** | - | Analytics collector |

### Frontend (Node.js)

| Service | Port | Purpose |
|---------|------|---------|
| **Next.js** | 3000 | React application |

---

## ✅ Verification

Run these to verify everything is working:

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
# Open browser: http://localhost:3000

# API docs
# Open browser: http://localhost:8000/docs
```

**Expected Results:**
- ✅ Backend returns: `{"status": "healthy", ...}`
- ✅ Frontend loads landing page
- ✅ API docs show interactive Swagger UI

---

## 🐛 Troubleshooting

### Docker Issues

```bash
# Restart Docker Desktop
# Then run:
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill process
taskkill /F /PID <PID>
```

### Frontend Won't Start

```bash
cd frontend

# Clear and reinstall
rm -rf node_modules
rm package-lock.json
npm install
npm run dev
```

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| `HOW_TO_RUN.md` | Complete setup guide |
| `QUICK_START.md` | Frontend quick start |
| `frontend/README.md` | Frontend documentation |
| `README.md` | Main project docs |

---

## 🎉 You're Ready!

```
┌──────────────────────────────────────────┐
│  Backend:  http://localhost:8000         │
│  Frontend: http://localhost:3000         │
│                                          │
│  Open http://localhost:3000 and enjoy!  │
└──────────────────────────────────────────┘
```

**Happy Coding!** 💻✨

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| Docker won't start | Restart Docker Desktop |
| Port 8000 busy | Kill process or use different port |
| Port 3000 busy | `npm run dev -- -p 3001` |
| API not responding | Check `docker-compose ps` |
| Frontend errors | Clear cache & reinstall |

---

**Made with ❤️ for Hackathon 5**
