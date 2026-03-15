@echo off
REM ============================================================================
REM TechCorp FTE - AUTO STATUS (Check Everything)
REM ============================================================================

echo ========================================================================
echo  TechCorp FTE - PROJECT STATUS
echo ========================================================================
echo.

REM Check Docker
echo [DOCKER STATUS]
docker ps --filter "name=fte" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>nul
if errorlevel 1 (
    echo Docker is not running
)
echo.

REM Check Frontend
echo [FRONTEND STATUS]
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:3000 2>nul
if errorlevel 1 (
    echo Frontend is not running
)
echo.

REM Check Database
echo [DATABASE STATUS]
docker exec fte-postgres psql -U fte_user -d fte_db -t -c "SELECT COUNT(*) || ' tables' FROM information_schema.tables WHERE table_schema='public';" 2>nul
if errorlevel 1 (
    echo Database is not accessible
)
echo.

REM Show sample data
echo [SAMPLE DATA]
docker exec fte-postgres psql -U fte_user -d fte_db -c "SELECT 'customers' as table_name, COUNT(*) as rows FROM customers UNION ALL SELECT 'conversations', COUNT(*) FROM conversations;" 2>nul
echo.

REM Show connection details
echo ========================================================================
echo  CONNECTION DETAILS
echo ========================================================================
echo.
echo Database (Docker):
echo   Host:     localhost
echo   Port:     5432
echo   Database: fte_db
echo   Username: fte_user
echo   Password: fte_password
echo.
echo Frontend:
echo   URL: http://localhost:3000
echo.
echo ========================================================================
echo  QUICK COMMANDS
echo ========================================================================
echo.
echo Start:    AUTO-START.bat
echo Stop:     AUTO-STOP.bat
echo Restart:  AUTO-RESTART.bat
echo Status:   AUTO-STATUS.bat (this file)
echo.
echo ========================================================================

pause
