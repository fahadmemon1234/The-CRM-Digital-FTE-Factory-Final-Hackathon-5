@echo off
echo ======================================================================
echo TechCorp AI FTE - Project Status Check
echo ======================================================================
echo.

echo Checking Frontend...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:3000
if %errorlevel% equ 0 (
    echo ✓ Frontend is RUNNING on http://localhost:3000
) else (
    echo ✗ Frontend is NOT running
)
echo.

echo Checking Backend API...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:8000/health
if %errorlevel% equ 0 (
    echo ✓ Backend API is RUNNING on http://localhost:8000
) else (
    echo ✗ Backend API is NOT running
    echo   To start backend: cd production ^&^& docker-compose up -d
)
echo.

echo Docker Containers:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo ======================================================================
echo Access URLs:
echo ======================================================================
echo Frontend:    http://localhost:3000
echo API Docs:    http://localhost:8000/docs
echo API Health:  http://localhost:8000/health
echo.

echo ======================================================================
echo Quick Commands:
echo ======================================================================
echo Start Backend:  cd production ^&^& docker-compose up -d
echo Stop Backend:   cd production ^&^& docker-compose down
echo View Logs:      cd production ^&^& docker-compose logs -f
echo Restart All:    docker-compose down ^&^& docker-compose up -d
echo.

pause
