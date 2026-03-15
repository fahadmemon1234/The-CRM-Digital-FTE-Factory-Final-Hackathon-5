# ✅ FIX "Failed to Fetch" Error - COMPLETE GUIDE

## 🐛 PROBLEM
Support form submit karne par error: **"Failed to fetch"**

---

## ✅ SOLUTION - Step by Step

### **Step 1: API Server Chal Raha Hai Verify Karo**

**Browser mein open karo:**
```
http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "database": "connected (mock)",
  "channels": {...}
}
```

**Agar ye nahi aa raha:**
```bash
cd D:\GIAIC\Hackathon 5\production
python -m uvicorn api.test_api:app --reload
```

---

### **Step 2: Frontend Chal Raha Hai Verify Karo**

**Browser mein open karo:**
```
http://localhost:3000
```

**Expected:** Landing page dikhai de

**Agar nahi dikhai de raha:**
```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

---

### **Step 3: Test API Directly**

**Terminal/Command Prompt mein:**

```bash
curl -X POST http://localhost:8000/support/submit ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Test User\",\"email\":\"test@test.com\",\"subject\":\"Test\",\"category\":\"technical\",\"message\":\"Test message for API\"}"
```

**Expected Response:**
```json
{
  "ticket_id": "TKT-XXXXX",
  "message": "Thank you for contacting us!...",
  "estimated_response_time": "Usually within 5 minutes"
}
```

**Agar response aa raha hai → API working hai!** ✅

---

### **Step 4: Browser Console Check Karo**

**Support form page par jao:**
```
http://localhost:3000/support
```

**F12 press karo → Console tab**

**Form submit karo aur dekho:**

✅ **Good logs:**
```
📤 Submitting form... {name: "...", email: "..."}
📥 Response status: 200
✅ Submission successful: {ticket_id: "..."}
```

❌ **Bad logs:**
```
Failed to fetch
TypeError: NetworkError
Access to fetch blocked by CORS
```

---

### **Step 5: Network Tab Check Karo**

**F12 → Network tab**

**Form submit karo:**

✅ **Good:**
- Request: `http://localhost:8000/support/submit`
- Method: `POST`
- Status: `200`
- Response: `{ticket_id: "..."}`

❌ **Bad:**
- Request: `(failed)`
- Status: `(failed)`
- Error: `Failed to fetch`

---

## 🔧 FIXES

### **Fix 1: Restart API Server**

```bash
# Terminal 1:
cd D:\GIAIC\Hackathon 5\production
python -m uvicorn api.test_api:app --reload
```

**Wait for:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

### **Fix 2: Clear Browser Cache**

**Chrome/Edge:**
1. `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page (`Ctrl + R`)

---

### **Fix 3: Check CORS**

**API server mein CORS enabled hai:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Already enabled in `test_api.py`!** ✅

---

### **Fix 4: Use HTTP Instead of HTTPS**

**Make sure:**
```
✅ http://localhost:8000
❌ https://localhost:8000
```

**Frontend bhi HTTP par hai:**
```
✅ http://localhost:3000
❌ https://localhost:3000
```

---

### **Fix 5: Check Firewall**

**Windows Firewall:**
1. Control Panel → Windows Defender Firewall
2. Advanced settings
3. Inbound Rules
4. Allow Python through firewall

**Ya temporarily disable:**
```bash
# Not recommended for production!
netsh advfirewall set allprofiles state off
```

---

## 🧪 COMPLETE TEST FLOW

### **Terminal 1 - API Server:**
```bash
cd D:\GIAIC\Hackathon 5\production
python -m uvicorn api.test_api:app --reload

# Wait for:
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### **Terminal 2 - Frontend:**
```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run dev

# Wait for:
# ✓ Ready in XXXms
```

### **Browser:**

**1. Test API Health:**
```
http://localhost:8000/health
```
Should show: `{"status":"healthy",...}`

**2. Open Support Form:**
```
http://localhost:3000/support
```

**3. Fill Form:**
```
Name: Test User
Email: test@example.com
Subject: API Test
Category: technical
Message: Testing the support form submission
```

**4. Click Submit**

**5. Check Console (F12):**
```
📤 Submitting form...
📥 Response status: 200
✅ Submission successful
```

**6. Success Screen:**
```
✓ Thank You!
Your Ticket ID: TKT-XXXXX
```

---

## 📊 DEBUGGING CHECKLIST

Go through this checklist:

- [ ] API server running on port 8000?
- [ ] Frontend running on port 3000?
- [ ] Can access http://localhost:8000/health?
- [ ] Browser console shows no CORS errors?
- [ ] Network tab shows 200 status?
- [ ] Using HTTP (not HTTPS)?
- [ ] Browser cache cleared?
- [ ] Firewall not blocking?

---

## 🎯 QUICK FIX COMMANDS

### **Restart Everything:**

```bash
# Kill all Python processes
taskkill /F /IM python.exe

# Kill all Node processes
taskkill /F /IM node.exe

# Wait 5 seconds
timeout /t 5

# Start API
cd D:\GIAIC\Hackathon 5\production
start /B python -m uvicorn api.test_api:app --reload

# Wait 10 seconds
timeout /t 10

# Start Frontend
cd D:\GIAIC\Hackathon 5\frontend
start /B npm run dev
```

---

## ✅ SUCCESS INDICATORS

You know it's working when:

1. ✅ API health returns JSON
2. ✅ Form submits without errors
3. ✅ Console shows "✅ Submission successful"
4. ✅ Success screen with ticket ID
5. ✅ No "Failed to fetch" errors
6. ✅ Network tab shows 200 status

---

## 🐛 STILL NOT WORKING?

### **Try This:**

1. **Open Command Prompt as Administrator**

2. **Run these commands:**
```bash
# Check what's on port 8000
netstat -ano | findstr :8000

# If nothing, start API
cd D:\GIAIC\Hackathon 5\production
python api/test_api.py

# Check port 3000
netstat -ano | findstr :3000

# If nothing, start frontend
cd D:\GIAIC\Hackathon 5\frontend
npm run dev
```

3. **Test in this order:**
```
1. http://localhost:8000/health
2. http://localhost:3000
3. http://localhost:3000/support
4. Fill form → Submit
```

---

## 📝 API IS RUNNING - BUT FORM STILL FAILS?

**Possible reasons:**

1. **CORS not enabled** → Already enabled in test_api.py ✅
2. **Wrong URL** → Make sure it's `http://localhost:8000` ✅
3. **Browser extension blocking** → Try incognito mode
4. **Antivirus blocking** → Temporarily disable
5. **Port conflict** → Check `netstat -ano | findstr :8000`

---

## 🎉 FINAL VERIFICATION

**Everything working?**

Test this complete flow:

```
1. Open: http://localhost:8000/health
   ↓
   Shows: {"status":"healthy",...}
   
2. Open: http://localhost:3000/support
   ↓
   Form loads correctly
   
3. Fill form and submit
   ↓
   Console: 📤 Submitting form...
   
4. API receives request
   ↓
   Terminal: ✅ Form submitted successfully!
   
5. Frontend gets response
   ↓
   Console: ✅ Submission successful
   
6. Success screen shows
   ↓
   Ticket ID: TKT-XXXXX
   
7. Check pgAdmin (optional)
   ↓
   Data inserted in tables
```

**If this flow works → COMPLETE!** 🎉

---

**Last Updated:** 2026-03-15  
**Common Issue:** API server not running or CORS  
**Solution:** Run `python api/test_api.py` and check CORS
