# 🔧 TROUBLESHOOTING - "Failed to Fetch" Error

## ❌ PROBLEM
Frontend cannot connect to backend API. Error: "Failed to fetch"

---

## ✅ SOLUTIONS

### **Solution 1: Start API Server (MOST COMMON)**

**The API server is NOT running!**

**Steps to fix:**

1. **Open NEW Terminal/Command Prompt**

2. **Run the start script:**
   ```bash
   cd D:\GIAIC\Hackathon 5
   start-api.bat
   ```

3. **Wait for this message:**
   ```
   ✓ Database connected successfully!
   ✅ Application startup complete.
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

4. **Now test:** http://localhost:8000/health

5. **Then try form again:** http://localhost:3000/support

---

### **Solution 2: Check if API is Already Running**

**Check if port 8000 is in use:**

```bash
# Windows Command Prompt:
netstat -ano | findstr :8000
```

**If you see output:**
```
TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    12345
```

**Good! API is already running.** Just test:
```
http://localhost:8000/health
```

**If NO output:** API is NOT running. Use Solution 1.

---

### **Solution 3: Manual API Start**

If `start-api.bat` doesn't work:

```bash
# Navigate to production folder
cd D:\GIAIC\Hackathon 5\production

# Install packages manually
pip install fastapi uvicorn asyncpg pydantic python-dotenv email-validator

# Start API manually
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

### **Solution 4: Check Database Connection**

**API needs PostgreSQL!**

**Check Docker PostgreSQL:**
```bash
docker ps | grep postgres
```

**If nothing shows:**
```bash
# Start Docker PostgreSQL
cd D:\GIAIC\Hackathon 5\production
docker-compose up -d postgres

# Wait 10 seconds
timeout /t 10

# Check again
docker ps
```

**OR use local PostgreSQL:**

1. **Check if running:**
   ```bash
   netstat -ano | findstr :5432
   ```

2. **If not running:**
   ```bash
   net start postgresql-x64-16
   ```

---

### **Solution 5: Update API URL in Frontend**

**If using different port:**

Edit `frontend/src/app/support/page.tsx`:

```typescript
// Change this line:
const response = await fetch("http://localhost:8000/support/submit", {

// To your actual API URL:
const response = await fetch("http://YOUR-IP:YOUR-PORT/support/submit", {
```

---

## 🧪 TEST API CONNECTION

### **Test 1: Browser**

Open in browser:
```
http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**If error:** API is NOT running!

---

### **Test 2: Test Page**

Open test page:
```
http://localhost:3000/test-api
```

Click "Test Connection" button.

---

### **Test 3: cURL**

```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{"status":"healthy","database":"connected",...}
```

---

## 📊 COMMON SCENARIOS

### **Scenario A: Fresh Start**

```
1. Start PostgreSQL (Docker or local)
   ↓
2. Start API server (start-api.bat)
   ↓
3. Wait for "Application startup complete"
   ↓
4. Test: http://localhost:8000/health
   ↓
5. Start frontend: npm run dev
   ↓
6. Submit form: http://localhost:3000/support
```

---

### **Scenario B: API Already Running**

```
1. Check: netstat -ano | findstr :8000
   ↓
2. If running, just test health endpoint
   ↓
3. Submit form directly
```

---

### **Scenario C: Port Conflict**

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual number)
taskkill /F /PID 12345

# Restart API
```

---

## 🔍 DEBUGGING STEPS

### **Step 1: Check API Logs**

**Look for these in terminal:**

✅ **Good logs:**
```
✓ Database pool created successfully
✅ Database connected successfully!
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

❌ **Bad logs:**
```
✗ Database connection failed
ERROR: Connection refused
CRITICAL: Application startup failed
```

---

### **Step 2: Check Browser Console**

**Press F12 → Console tab**

**Look for:**

✅ **Good:**
```
📤 Submitting form...
📥 Response status: 200
✅ Submission successful
```

❌ **Bad:**
```
Failed to fetch
TypeError: Failed to fetch
Network request failed
```

---

### **Step 3: Check Network Tab**

**Press F12 → Network tab**

**Submit form and look for:**

✅ **Good:**
- Request to: `http://localhost:8000/support/submit`
- Status: `200 OK`
- Response: `{ticket_id: "..."}`

❌ **Bad:**
- Request: `(failed)`
- Status: `(failed)`
- Error: `Failed to fetch`

---

## 🎯 QUICK FIX CHECKLIST

Run through this checklist:

- [ ] PostgreSQL is running (Docker or local)
- [ ] API server started (`start-api.bat`)
- [ ] Terminal shows "Application startup complete"
- [ ] Can access http://localhost:8000/health
- [ ] Frontend is running (`npm run dev`)
- [ ] No firewall blocking port 8000
- [ ] No other service on port 8000
- [ ] Browser console shows no errors

---

## 🚀 COMPLETE WORKING FLOW

### **Terminal 1 - API Server:**
```bash
cd D:\GIAIC\Hackathon 5
start-api.bat

# Wait for:
# ✅ Application startup complete.
```

### **Terminal 2 - Frontend:**
```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run dev

# Wait for:
# ✓ Ready in XXXms
# ○ started server on 0.0.0.0:3000
```

### **Browser:**
1. **Test API:** http://localhost:8000/health
   - Should show: `{"status": "healthy", ...}`

2. **Submit Form:** http://localhost:3000/support
   - Fill form and submit
   - Should show success screen

3. **Check Database:** Open pgAdmin
   - Check tables for new data

---

## 📞 STILL NOT WORKING?

### **Try These:**

1. **Restart everything:**
   ```bash
   # Stop all
   Ctrl+C in all terminals
   
   # Restart API
   start-api.bat
   
   # Restart frontend
   npm run dev
   ```

2. **Check Python version:**
   ```bash
   python --version
   # Should be 3.11+
   ```

3. **Reinstall packages:**
   ```bash
   pip install --upgrade fastapi uvicorn asyncpg pydantic
   ```

4. **Check file exists:**
   ```bash
   # This file should exist:
   D:\GIAIC\Hackathon 5\production\api\main.py
   ```

5. **Test with different browser:**
   - Chrome
   - Firefox
   - Edge

---

## ✅ SUCCESS INDICATORS

You know it's working when:

1. ✅ Terminal shows: `Uvicorn running on http://0.0.0.0:8000`
2. ✅ http://localhost:8000/health returns JSON
3. ✅ Form submits without errors
4. ✅ Success screen shows ticket ID
5. ✅ pgAdmin shows new data in tables
6. ✅ No "Failed to fetch" errors

---

## 🎉 FINAL CHECK

**Everything working?**

Test this flow:
```
1. Open: http://localhost:3000/support
2. Fill form
3. Submit
4. See ticket ID
5. Check pgAdmin
6. See data in tables
```

**If YES → All good! 🚀**  
**If NO → Check logs and follow debugging steps above.**

---

**Last Updated:** 2026-03-15  
**Common Issue:** API server not running  
**Solution:** Run `start-api.bat`
