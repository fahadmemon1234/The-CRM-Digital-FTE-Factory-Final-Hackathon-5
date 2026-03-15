@echo off
REM ============================================================================
REM TechCorp Customer Success AI Agent - Stop All Services
REM ============================================================================
REM This script stops both Backend (Docker) and Frontend
REM ============================================================================

echo.
echo ============================================================================
echo   Stopping All Services...
echo ============================================================================
echo.

REM Stop Backend Services
echo Stopping Docker containers...
echo.

cd /d "%~dp0production"

if exist "docker-compose.yml" (
    docker-compose down
    
    if errorlevel 1 (
        echo [ERROR] Failed to stop Docker containers
    ) else (
        echo [OK] Backend services stopped
    )
) else (
    echo [INFO] No docker-compose.yml found
)

echo.
echo ============================================================================
echo   Frontend Instructions
echo ============================================================================
echo.
echo To stop the Frontend (Next.js):
echo   1. Go to the terminal running 'npm run dev'
echo   2. Press Ctrl+C
echo.

echo All backend services stopped!
echo.

pause
