@echo off
REM Database Migration Runner for luxeflow_ai to fte_db

echo ======================================================================
echo Database Migration Runner
echo ======================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

echo Installing dependencies...
pip install asyncpg -q

echo.
echo Starting migration...
echo.

REM Run the migration script
python production/database/migrations/auto_migrate_luxeflow.py

echo.
pause
