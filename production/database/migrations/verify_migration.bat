@echo off
set PGPASSWORD=postgres
echo Listing tables in fte_db database...
psql -U postgres -h localhost -d fte_db -c "\dt"
echo.
echo Showing row counts...
psql -U postgres -h localhost -d fte_db -c "SELECT table_name, (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns FROM information_schema.tables t WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"
pause
