# Hugging Face Spaces - TechCorp Backend Deployment

## 📁 Kaunsa Folder Upload Karein?

**Option 1: Pure Project (Recommended)**
- Complete project upload karein
- Size: ~50-100MB (without node_modules)
- Best for: Full functionality

**Option 2: Production Folder Only**
- `production/` folder
- Plus root level files
- Best for: API only deployment

## 🚀 Hugging Face Spaces Setup

### Step 1: Create Space
1. https://huggingface.co/spaces par jayein
2. "Create new Space" click karein
3. **Space type:** Docker
4. **License:** MIT

### Step 2: Required Files

Project root mein yeh files add karein:

#### 1. Dockerfile (Hugging Face optimized)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY production/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy production code
COPY production/ ./production/
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=7860

# Expose port
EXPOSE 7860

# Run the API
CMD ["uvicorn", "production.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

#### 2. requirements.txt (Simplified for HF)
```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
openai>=1.10.0
asyncpg>=0.29.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
httpx>=0.26.0
```

#### 3. .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.production

# Frontend (don't upload)
frontend/node_modules/
frontend/.next/
frontend/out/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Test
.pytest_cache/
.coverage
htmlcov/

# Docker
docker-compose.yml
*.pid
```

### Step 3: Upload to Hugging Face

#### Method A: Git Push (Recommended)
```bash
# Clone your HF Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy files
cp -r /path/to/your/project/* .

# Remove frontend (optional - reduces size)
rm -rf frontend/

# Commit and push
git add .
git commit -m "Initial commit - TechCorp Backend"
git push origin main
```

#### Method B: Web Upload
1. HF Space page par jayein
2. "Files" tab par click karein
3. "Add file" → "Upload files"
4. Yeh folders upload karein:
   - `production/` (complete folder)
   - `src/` (optional - agar MCP server chahiye)
   - `requirements.txt`
   - `Dockerfile`
   - `.env.example`

### Step 4: Environment Variables Configure Karein

HF Space Settings → "Repository secrets" mein add karein:

```bash
# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional (for full features)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
GOOGLE_CLOUD_PROJECT=...
```

### Step 5: Database Setup

**Option A: Hugging Face PostgreSQL (Recommended)**
- HF managed PostgreSQL use karein
- Connection string Secrets mein add karein

**Option B: External Database**
- Supabase (Free): https://supabase.com
- Neon (Free): https://neon.tech
- Railway (Free): https://railway.app

Connection string example:
```
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

## 📦 Folder Structure for HF

```
your-hf-space/
├── production/              # ✅ Required
│   ├── api/
│   ├── agent/
│   ├── channels/
│   ├── database/
│   ├── workers/
│   ├── utils/
│   ├── Dockerfile
│   └── requirements.txt
├── src/                     # ⚠️ Optional (MCP server)
│   └── mcp_server.py
├── Dockerfile               # ✅ Required
├── requirements.txt         # ✅ Required
├── .env.example             # ✅ Required
├── .gitignore               # ✅ Required
└── README.md                # ✅ Recommended
```

## ⚠️ Important Notes

### DON'T Upload:
- ❌ `frontend/node_modules/` (too large)
- ❌ `frontend/.next/` (build artifacts)
- ❌ `.env` file (contains secrets)
- ❌ `__pycache__/` folders
- ❌ `.git/` folder

### DO Upload:
- ✅ `production/` folder (complete)
- ✅ `requirements.txt`
- ✅ `Dockerfile`
- ✅ `.env.example` (without secrets)
- ✅ `README.md`

## 🔧 Minimal Deployment (API Only)

Agar sirf API deploy karna hai:

```
minimal-deployment/
├── production/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── auth_api.py
│   │   ├── tickets_api.py
│   │   ├── notifications_api.py
│   │   └── search_api.py
│   ├── database/
│   │   └── schema.sql
│   └── requirements.txt
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 Quick Deploy Commands

```bash
# 1. Create HF Space (via CLI)
pip install huggingface_hub
huggingface-cli login

# 2. Clone space
git clone https://huggingface.co/spaces/YOUR_USERNAME/techcorp-backend
cd techcorp-backend

# 3. Copy production files
cp -r /path/to/project/production .
cp /path/to/project/requirements.txt .
cp /path/to/project/Dockerfile .

# 4. Remove heavy folders
rm -rf frontend/
rm -rf node_modules/

# 5. Push to HF
git add .
git commit -m "Deploy TechCorp Backend"
git push origin main
```

## 📊 Deployment Size Comparison

| Deployment Type | Size | Upload Time | Features |
|----------------|------|-------------|----------|
| Full Project | ~200MB | 10-15 min | Everything |
| Production Only | ~50MB | 3-5 min | API + Workers |
| Minimal API | ~10MB | 1-2 min | API Only |

## ✅ Recommended: Production Folder Only

**Best balance of size and functionality:**

```bash
# Files to upload:
production/           # Complete folder
requirements.txt
Dockerfile
.env.example
README.md
.gitignore

# Total size: ~50MB
# Deploy time: ~5 minutes
```

## 🔗 Useful Links

- Hugging Face Spaces: https://huggingface.co/spaces
- Docker Spaces Docs: https://huggingface.co/docs/hub/spaces-sdks-docker
- PostgreSQL on HF: https://huggingface.co/docs/hub/spaces-postgresql
