@echo off
REM ============================================================================
REM TechCorp Customer Success AI Agent - Start All Services
REM ============================================================================
REM This script starts both Backend (Docker) and Frontend (Next.js)
REM ============================================================================

echo.
echo ============================================================================
echo   TechCorp Customer Success AI Agent - Complete Startup
echo ============================================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running! Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Start Backend Services
echo ============================================================================
echo   Starting Backend Services (Docker Compose)...
echo ============================================================================
echo.

cd /d "%~dp0production"

if exist "docker-compose.yml" (
    echo Starting Docker containers...
    docker-compose up -d
    
    if errorlevel 1 (
        echo [ERROR] Failed to start Docker containers
        pause
        exit /b 1
    )
    
    echo.
    echo [OK] Backend services started!
    echo.
    echo Backend URLs:
    echo   - API: http://localhost:8000
    echo   - API Docs: http://localhost:8000/docs
    echo   - ReDoc: http://localhost:8000/redoc
    echo.
) else (
    echo [WARNING] docker-compose.yml not found in production folder
    echo.
)

cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo ============================================================================
    echo   Installing Frontend Dependencies...
    echo ============================================================================
    echo.
    call npm install
    
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start Frontend
echo ============================================================================
echo   Starting Frontend (Next.js)...
echo ============================================================================
echo.

echo Starting development server on http://localhost:3000
echo.
echo Press Ctrl+C to stop the frontend
echo.

call npm run dev

pause
