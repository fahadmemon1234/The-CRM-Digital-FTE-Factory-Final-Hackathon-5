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
echo ✓ Docker is running
echo.

REM Step 1: Stop any existing containers
echo [1/6] Cleaning up existing containers...
cd /d "%~dp0production"
docker-compose down >nul 2>&1
echo ✓ Cleanup complete
echo.

REM Step 2: Start PostgreSQL
echo [2/6] Starting PostgreSQL Database...
docker-compose up -d postgres
if errorlevel 1 (
    echo ERROR: Failed to start PostgreSQL
    pause
    exit /b 1
)
echo ✓ PostgreSQL started
echo.

REM Step 3: Wait for PostgreSQL to be ready
echo [3/6] Waiting for PostgreSQL to initialize...
echo      This may take 30-60 seconds...
echo.

:wait_loop
timeout /t 5 /nobreak >nul
docker exec fte-postgres psql -U fte_user -d fte_db -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    echo      Still waiting for PostgreSQL...
    goto wait_loop
)
echo ✓ PostgreSQL is ready
echo.

REM Step 4: Load Database Schema
echo [4/6] Setting up database schema...
type database\schema.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db >nul 2>&1
if errorlevel 1 (
    echo Note: Schema may already exist
) else (
    echo ✓ Database schema created
)
echo.

REM Step 5: Load Seed Data
echo [5/6] Loading seed data...
if exist "database\seed.sql\seed_data.sql" (
    type database\seed.sql\seed_data.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db >nul 2>&1
    if errorlevel 1 (
        echo Note: Seed data may already exist
    ) else (
        echo ✓ Seed data loaded
    )
) else (
    echo Note: Seed data file not found
)
echo.

REM Step 6: Verify Database
echo [6/6] Verifying database setup...
for /f "tokens=*" %%i in ('docker exec fte-postgres psql -U fte_user -d fte_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2^>nul') do set TABLE_COUNT=%%i
echo ✓ Database has %TABLE_COUNT% tables
echo.

REM Show connection details
echo ========================================================================
echo  DATABASE CONNECTION DETAILS (for pgAdmin 4)
echo ========================================================================
echo.
echo Host:     localhost
echo Port:     5432
echo Database: fte_db
echo Username: fte_user
echo Password: fte_password
echo.
echo ========================================================================
echo  STARTING FRONTEND
echo ========================================================================
echo.

cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
    echo ✓ Dependencies installed
    echo.
)

REM Start Frontend
echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo ========================================================================
echo  PROJECT IS RUNNING!
echo ========================================================================
echo.
echo ✓ PostgreSQL: Running (port 5432)
echo ✓ Database:   fte_db (%TABLE_COUNT% tables)
echo ✓ Frontend:   Starting...
echo.
echo Access URLs:
echo   Frontend:  http://localhost:3000
echo   API Docs:  http://localhost:8000/docs (when backend starts)
echo.
echo pgAdmin 4 Connection:
echo   Host:     localhost
echo   Port:     5432
echo   Database: fte_db
echo   Username: fte_user
echo   Password: fte_password
echo.
echo ========================================================================
echo  Press Ctrl+C to stop the frontend
echo  Docker containers will keep running in background
echo ========================================================================
echo.

REM Start frontend
call npm run dev
