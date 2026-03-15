@echo off
REM ============================================================================
REM Quick Start - API Server with Database Check
REM ============================================================================

echo ========================================================================
echo  Starting TechCorp FTE API Server
echo ========================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

echo [1/3] Installing required packages...
pip install fastapi uvicorn asyncpg pydantic python-dotenv email-validator -q
echo ✓ Packages installed
echo.

echo [2/3] Checking database connection...
set PGPASSWORD=postgres
docker exec fte-postgres psql -U fte_user -d fte_db -c "SELECT 1" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Docker PostgreSQL not accessible
    echo Trying local PostgreSQL...
    psql -U postgres -h localhost -d luxeFlow_ai -c "SELECT 1" >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Cannot connect to any PostgreSQL database!
        echo Please start PostgreSQL first.
        pause
        exit /b 1
    )
    echo ✓ Local PostgreSQL connected
    set DB_URL=postgresql://postgres:postgres@localhost:5432/luxeFlow_ai
) else (
    echo ✓ Docker PostgreSQL connected
    set DB_URL=postgresql://fte_user:fte_password@localhost:5432/fte_db
)
echo.

echo [3/3] Starting API server...
echo.
echo ========================================================================
echo  API Server is starting...
echo ========================================================================
echo.
echo  API Docs:  http://localhost:8000/docs
echo  Health:    http://localhost:8000/health
echo  Support:   POST http://localhost:8000/support/submit
echo.
echo  Database:  %DB_URL%
echo.
echo  Press Ctrl+C to stop the server
echo ========================================================================
echo.

REM Set environment variable
set DATABASE_URL=%DB_URL%

REM Start server
cd /d "%~dp0production"
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
