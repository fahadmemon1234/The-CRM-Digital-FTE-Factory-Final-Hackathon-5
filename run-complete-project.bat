@echo off
REM ============================================================================
REM TechCorp FTE - Complete Project Runner with Database Setup
REM ============================================================================

echo ========================================================================
echo  TechCorp Customer Success AI Agent - Complete Setup
echo ========================================================================
echo.

REM Step 1: Start PostgreSQL
echo [1/5] Starting PostgreSQL Database...
cd /d "%~dp0production"
docker-compose up -d postgres
if errorlevel 1 (
    echo ERROR: Failed to start PostgreSQL
    pause
    exit /b 1
)
echo ✓ PostgreSQL started
echo.

REM Step 2: Wait for PostgreSQL to be ready
echo [2/5] Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul
echo.

REM Step 3: Initialize Database Schema
echo [3/5] Setting up database schema...
docker exec fte-postgres psql -U fte_user -d fte_db -c "\i /docker-entrypoint-initdb.d/01-schema.sql" 2>&1
if errorlevel 1 (
    echo Note: Schema may already exist or needs manual setup
    echo Running schema manually...
    type database\schema.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db
)
echo ✓ Database schema created
echo.

REM Step 4: Load Seed Data
echo [4/5] Loading seed data...
type database\seed.sql\seed_data.sql | docker exec -i fte-postgres psql -U fte_user -d fte_db 2>&1
if errorlevel 1 (
    echo Note: Seed data may already exist
)
echo ✓ Seed data loaded
echo.

REM Step 5: Verify Database
echo [5/5] Verifying database setup...
docker exec fte-postgres psql -U fte_user -d fte_db -c "SELECT COUNT(*) as tables FROM information_schema.tables WHERE table_schema = 'public';" 2>&1
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
echo OR (Superuser):
echo Username: postgres
echo Password: postgres
echo ========================================================================
echo.

REM Show status
echo ========================================================================
echo  SERVICE STATUS
echo ========================================================================
docker ps --filter "name=fte-postgres" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo ========================================================================
echo  ACCESS URLS
echo ========================================================================
echo Frontend:  http://localhost:3000
echo API Docs:  http://localhost:8000/docs (when backend starts)
echo.

echo ========================================================================
echo  NEXT STEPS
echo ========================================================================
echo 1. Open pgAdmin 4
echo 2. Right-click 'Servers' → 'Create' → 'Server...'
echo 3. Enter connection details shown above
echo 4. Test connection and save
echo 5. Navigate to: fte_db → Schemas → public → Tables
echo.
echo 6. Open browser: http://localhost:3000
echo 7. Login and explore the dashboard!
echo ========================================================================
echo.

pause
