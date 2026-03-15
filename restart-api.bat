@echo off
echo ========================================================================
echo  Restarting API Server
echo ========================================================================
echo.

echo [1/2] Stopping existing server...
taskkill /F /FI "WINDOWTITLE eq API Server*" /FI "IMAGENAME eq python.exe" >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✓ Server stopped
echo.

echo [2/2] Starting new server...
cd /d "%~dp0production"
start "API Server" python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

echo ✓ API Server restarted!
echo.
echo  API Docs:  http://localhost:8000/docs
echo  Health:    http://localhost:8000/health
echo  Webhook:   POST http://localhost:8000/webhooks/whatsapp
echo.
timeout /t 3 /nobreak >nul
