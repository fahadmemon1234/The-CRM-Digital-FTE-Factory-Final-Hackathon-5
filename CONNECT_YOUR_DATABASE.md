# 🔗 Connect Your luxeFlow_ai Database

## 📊 CURRENT SITUATION

### Two PostgreSQL Instances:

**1. Docker PostgreSQL (Running)**
```
Port:     5432 (occupied by Docker)
Database: fte_db (project database)
Status:   ✅ Running in Docker
```

**2. Local PostgreSQL (Your pgAdmin database)**
```
Port:     5432 (default)
Database: luxeFlow_ai (your existing database)
Status:   ⏸️  Need to stop Docker to access
```

---

## ✅ SOLUTION: Use Your luxeFlow_ai Database

### Option 1: Stop Docker & Use Local PostgreSQL (Recommended)

#### Step 1: Stop Docker PostgreSQL
```bash
cd D:\GIAIC\Hackathon 5\production
docker-compose down
```

#### Step 2: Verify Your Local PostgreSQL
```bash
# Check if PostgreSQL is running
netstat -ano | findstr :5432

# If not showing, start PostgreSQL service
net start postgresql-x64-16
# OR
net start postgresql
```

#### Step 3: Test Connection
```bash
set PGPASSWORD=postgres
psql -U postgres -h localhost -d luxeFlow_ai -c "\dt"
```

#### Step 4: Update .env (Already configured!)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/luxeFlow_ai
```

✅ **Already set in `production/.env`!**

---

### Option 2: Run Local PostgreSQL on Different Port

#### Step 1: Stop Docker
```bash
cd D:\GIAIC\Hackathon 5\production
docker-compose down
```

#### Step 2: Change Local PostgreSQL Port
1. Open pgAdmin 4
2. Right-click on PostgreSQL server
3. Properties → Connection
4. Change port to `5433`
5. Save

#### Step 3: Update .env
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/luxeFlow_ai
```

#### Step 4: Restart Docker
```bash
cd D:\GIAIC\Hackathon 5\production
docker-compose up -d postgres
```

---

## 🎯 QUICK START (Using Your Database)

### Method A: Stop Docker, Use Local PostgreSQL

```bash
# 1. Stop Docker
cd D:\GIAIC\Hackathon 5\production
docker-compose down

# 2. Start Frontend
cd D:\GIAIC\Hackathon 5\frontend
npm run dev

# 3. Access
# Frontend: http://localhost:3000
# Your DB: localhost:5432/luxeFlow_ai
```

### Method B: Keep Docker Running, Use fte_db

```bash
# Keep Docker running
# Frontend already configured for Docker

# Access
# Frontend: http://localhost:3000
# Docker DB: localhost:5432/fte_db
```

---

## 🔗 CONNECT pgAdmin 4

### For Your luxeFlow_ai Database:

**Connection Details:**
```
Host:     localhost
Port:     5432 (or 5433 if changed)
Database: luxeFlow_ai
Username: postgres
Password: postgres
```

### For Docker fte_db Database:

**Connection Details:**
```
Host:     localhost
Port:     5432
Database: fte_db
Username: fte_user
Password: fte_password
```

---

## 📊 YOUR DATABASE TABLES (luxeFlow_ai)

When you connect to `luxeFlow_ai`, you'll see:

```
✓ agents (3 rows)
✓ alembic_version (1 row)
✓ audit_log
✓ customers
✓ escalation_log
✓ event_logs
✓ knowledge_base
✓ messages
✓ tickets
```

---

## 🚀 RECOMMENDED SETUP

### For Development (Using luxeFlow_ai):

1. **Stop Docker:**
   ```bash
   cd D:\GIAIC\Hackathon 5\production
   docker-compose down
   ```

2. **Start Frontend:**
   ```bash
   cd D:\GIAIC\Hackathon 5\frontend
   npm run dev
   ```

3. **Connect pgAdmin:**
   - Host: localhost
   - Port: 5432
   - Database: luxeFlow_ai
   - Username: postgres
   - Password: postgres

4. **Access Frontend:**
   - http://localhost:3000

---

## 🔄 SWITCHING BETWEEN DATABASES

### Use luxeFlow_ai (Your Database):
```bash
# Stop Docker
docker-compose down

# Start Frontend
cd frontend
npm run dev
```

### Use fte_db (Docker Database):
```bash
# Start Docker
cd production
docker-compose up -d postgres

# Start Frontend
cd frontend
npm run dev
```

---

## 📝 CONFIGURATION FILES

### production/.env (Already configured):
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/luxeFlow_ai
```

### frontend/.env (if exists):
```env
NEXT_PUBLIC_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/luxeFlow_ai
```

---

## ✅ VERIFICATION

### Check Which PostgreSQL is Running:
```bash
# Check Docker
docker ps | findstr postgres

# Check Port
netstat -ano | findstr :5432
```

### Test Connection to luxeFlow_ai:
```bash
# Stop Docker first
docker-compose down

# Test connection
set PGPASSWORD=postgres
psql -U postgres -h localhost -d luxeFlow_ai -c "\dt"
```

---

## 🎯 CURRENT STATUS

| Component | Status | Database |
|-----------|--------|----------|
| **Docker PostgreSQL** | ✅ Running | fte_db |
| **Local PostgreSQL** | ⏸️ Stopped | luxeFlow_ai |
| **Frontend** | ✅ Running | Configured for luxeFlow_ai |
| **pgAdmin** | 🔗 Ready | Can connect to either |

---

## 🎉 RECOMMENDED NEXT STEPS

### To Use Your luxeFlow_ai Database:

1. **Stop Docker PostgreSQL:**
   ```bash
   cd D:\GIAIC\Hackathon 5\production
   docker-compose down
   ```

2. **Make sure local PostgreSQL is running:**
   - Check Services → PostgreSQL x64 16
   - Or run: `net start postgresql-x64-16`

3. **Test connection:**
   ```bash
   set PGPASSWORD=postgres
   psql -U postgres -h localhost -d luxeFlow_ai -c "\dt"
   ```

4. **Access Frontend:**
   - http://localhost:3000
   - It will use your luxeFlow_ai database!

---

## 📞 TROUBLESHOOTING

### Can't connect to luxeFlow_ai?
```bash
# Check if PostgreSQL is running
netstat -ano | findstr :5432

# If nothing on 5432, start PostgreSQL
net start postgresql-x64-16
```

### Port 5432 already in use?
```bash
# Find what's using it
netstat -ano | findstr :5432

# If Docker, stop it
docker-compose down
```

### PostgreSQL service not found?
```bash
# List all services
sc query | findstr postgres

# Start with correct name
net start <service-name-from-list>
```

---

**🚀 Aapka project configured hai aapke luxeFlow_ai database ke liye!**

**Bas Docker ko stop karna hoga aur local PostgreSQL start karna hoga!**
