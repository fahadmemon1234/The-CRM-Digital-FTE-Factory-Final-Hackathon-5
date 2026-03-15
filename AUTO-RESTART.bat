@echo off
REM ============================================================================
REM TechCorp FTE - AUTO RESTART (Fully Automatic)
REM ============================================================================

echo ========================================================================
echo  TechCorp FTE - AUTO RESTART
echo ========================================================================
echo.

REM Stop everything
echo [1/4] Stopping all services...
cd /d "%~dp0production"
docker-compose down >nul 2>&1
echo ✓ Stopped
echo.

REM Wait
echo [2/4] Waiting for services to stop...
timeout /t 5 /nobreak >nul
echo.

REM Start Docker
echo [3/4] Starting Docker services...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker
    pause
    exit /b 1
)
echo ✓ Docker started
echo.

REM Wait for PostgreSQL
echo [4/4] Waiting for PostgreSQL...
:wait_loop
timeout /t 3 /nobreak >nul
docker exec fte-postgres psql -U fte_user -d fte_db -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    goto wait_loop
)
echo ✓ PostgreSQL ready
echo.

echo ========================================================================
echo  RESTART COMPLETE!
echo ========================================================================
echo.
echo Services:
echo   ✓ PostgreSQL: Running
echo   ✓ Frontend:   Run AUTO-START.bat to start
echo.
echo Access:
echo   Database: localhost:5432 (fte_db)
echo   Frontend: Run AUTO-START.bat
echo.

pause
