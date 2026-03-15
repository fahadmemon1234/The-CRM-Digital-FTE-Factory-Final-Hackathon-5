@echo off
REM ============================================================================
REM TechCorp FTE - AUTO STOP (Fully Automatic)
REM ============================================================================

echo ========================================================================
echo  TechCorp FTE - AUTO STOP
echo ========================================================================
echo.

REM Stop Docker containers
echo [1/2] Stopping Docker containers...
cd /d "%~dp0production"
docker-compose down
if errorlevel 1 (
    echo Note: No containers to stop
) else (
    echo ✓ Docker containers stopped
)
echo.

REM Kill any node processes running frontend
echo [2/2] Stopping frontend server...
taskkill /F /FI "WINDOWTITLE eq npm run dev*" >nul 2>&1
if errorlevel 1 (
    echo Note: Frontend was not running
) else (
    echo ✓ Frontend stopped
)
echo.

echo ========================================================================
echo  ALL SERVICES STOPPED
echo ========================================================================
echo.
echo To start again, run: AUTO-START.bat
echo.

pause
