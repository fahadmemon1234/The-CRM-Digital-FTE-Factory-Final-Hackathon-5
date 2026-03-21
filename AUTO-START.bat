@echo off
REM ============================================================================
REM TechCorp FTE - AUTO START (Fully Automatic - No Manual Steps!)
REM ============================================================================

echo ========================================================================
echo  TechCorp Customer Success AI Agent - AUTO START
echo  Fully Automatic Setup - No Manual Steps Required!
echo ========================================================================
echo.

REM Check if Docker is running
echo [CHECK] Verifying Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and run this script again.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Step 1: Start all backend services (Docker Compose)
echo [1/4] Starting Backend Services (Docker Compose)...
cd /d "%~dp0production"

if exist "docker-compose.yml" (
    echo Starting Docker containers...
    docker-compose up -d

    if errorlevel 1 (
        echo ERROR: Failed to start Docker containers
        pause
        exit /b 1
    )

    echo [OK] Backend services started!
    echo.
    echo Backend URLs:
    echo   - API: http://localhost:8000
    echo   - API Docs: http://localhost:8000/docs
    echo   - ReDoc: http://localhost:8000/redoc
    echo.
    
    REM Wait for backend to be ready
    echo Waiting for backend to be ready...
    timeout /t 10 /nobreak >nul
) else (
    echo [WARNING] docker-compose.yml not found in production folder
    echo.
)

REM Step 2: Go to frontend directory
echo [2/4] Setting up Frontend...
cd /d "%~dp0frontend"

REM Step 3: Check if node_modules exists
if not exist "node_modules" (
    echo [3/4] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
    echo.
) else (
    echo [OK] Dependencies already installed
    echo.
)

REM Step 4: Start Frontend
echo [4/4] Starting Next.js development server...
echo.
echo ========================================================================
echo  PROJECT IS RUNNING!
echo ========================================================================
echo.
echo Access URLs:
echo   Frontend:  http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo ========================================================================
echo  Press Ctrl+C to stop the frontend
echo  Docker containers will keep running in background
echo ========================================================================
echo.

REM Start frontend
call npm run dev
