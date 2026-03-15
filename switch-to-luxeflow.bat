@echo off
REM ============================================================================
REM Switch to luxeFlow_ai Database (Your pgAdmin Database)
REM ============================================================================

echo ========================================================================
echo  Switching to luxeFlow_ai Database
echo ========================================================================
echo.

REM Step 1: Stop Docker PostgreSQL
echo [1/4] Stopping Docker PostgreSQL...
cd /d "%~dp0production"
docker-compose down
if errorlevel 1 (
    echo Note: Docker may not be running or containers already stopped
)
echo ✓ Docker PostgreSQL stopped
echo.

REM Step 2: Wait for port to be freed
echo [2/4] Waiting for port 5432 to be freed...
timeout /t 5 /nobreak >nul
echo.

REM Step 3: Check if local PostgreSQL is running
echo [3/4] Checking local PostgreSQL...
netstat -ano | findstr :5432 >nul 2>&1
if errorlevel 1 (
    echo Local PostgreSQL not running. Trying to start...
    net start postgresql-x64-16 2>nul
    if errorlevel 1 (
        net start postgresql 2>nul
        if errorlevel 1 (
            echo WARNING: Could not start PostgreSQL automatically.
            echo Please start PostgreSQL manually from Services.
        )
    )
) else (
    echo ✓ Local PostgreSQL is running on port 5432
)
echo.

REM Step 4: Test connection
echo [4/4] Testing connection to luxeFlow_ai...
set PGPASSWORD=postgres
psql -U postgres -h localhost -d luxeFlow_ai -c "SELECT 'Connection successful!' as status;" 2>&1 | findstr "status"
if errorlevel 1 (
    echo.
    echo WARNING: Could not connect to luxeFlow_ai database
    echo Please ensure:
    echo   1. PostgreSQL is running
    echo   2. Database 'luxeFlow_ai' exists
    echo   3. Username: postgres, Password: postgres
) else (
    echo ✓ Connected to luxeFlow_ai database
)
echo.

REM Show summary
echo ========================================================================
echo  SETUP COMPLETE!
echo ========================================================================
echo.
echo Database: luxeFlow_ai (Your pgAdmin database)
echo Host:     localhost
echo Port:     5432
echo Username: postgres
echo Password: postgres
echo.
echo ========================================================================
echo  NEXT STEPS
echo ========================================================================
echo.
echo 1. Start Frontend:
echo    cd D:\GIAIC\Hackathon 5\frontend
echo    npm run dev
echo.
echo 2. Access Frontend:
echo    http://localhost:3000
echo.
echo 3. Connect pgAdmin 4:
echo    - Host: localhost
echo    - Port: 5432
echo    - Database: luxeFlow_ai
echo    - Username: postgres
echo    - Password: postgres
echo.
echo ========================================================================
echo.

pause
