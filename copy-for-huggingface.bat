@echo off
REM ============================================
REM Copy Files for Hugging Face Deployment
REM ============================================

echo.
echo ========================================
echo  Copying Files for Hugging Face Deploy
echo ========================================
echo.

SET SOURCE=D:\GIAIC\Hackathon 5
SET DEST=D:\GIAIC\AI-Powered-Customer-Success-FTE

echo [1/4] Copying production folder...
xcopy "%SOURCE%\production" "%DEST%\production" /E /I /Y /EXCLUDE:%SOURCE%\.gitignore

echo [2/4] Copying requirements.txt...
copy /Y "%SOURCE%\production\requirements.txt" "%DEST%\requirements.txt"

echo [3/4] Copying Dockerfile...
copy /Y "%SOURCE%\production\Dockerfile.huggingface" "%DEST%\Dockerfile"

echo [4/4] Copying .env.example...
copy /Y "%SOURCE%\production\.env.example" "%DEST%\.env.example"

echo.
echo ========================================
echo  Files Copied Successfully!
echo ========================================
echo.
echo Next Steps:
echo 1. Open: D:\GIAIC\AI-Powered-Customer-Success-FTE
echo 2. Check files are copied
echo 3. git add .
echo 4. git commit -m "Deploy backend"
echo 5. git push origin main
echo.
pause
