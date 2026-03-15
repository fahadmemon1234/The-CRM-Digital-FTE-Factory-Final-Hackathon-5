@echo off
REM ============================================================================
REM TechCorp FTE - Test Database Integration
REM ============================================================================

echo ========================================================================
echo  Testing Database Integration
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

echo [1/4] Installing required packages...
pip install fastapi uvicorn asyncpg pydantic python-dotenv -q
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo ✓ Packages installed
echo.

echo [2/4] Starting API server...
echo.
echo ========================================================================
echo  API Server Starting...
echo  - API: http://localhost:8000
echo  - Docs: http://localhost:8000/docs
echo  - Health: http://localhost:8000/health
echo ========================================================================
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0production"
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
