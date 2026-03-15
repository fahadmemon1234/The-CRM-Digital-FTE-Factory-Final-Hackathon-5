@echo off
REM ============================================================================
REM WhatsApp Integration Test - Automated
REM ============================================================================

echo.
echo ============================================================================
echo   WhatsApp Integration Test
echo ============================================================================
echo.

echo [Test 1] Creating WhatsApp ticket via database...
echo.

python test_whatsapp.py

echo.
echo ============================================================================
echo [Test 2] Fetching tickets from API...
echo ============================================================================
echo.

curl -s http://localhost:8000/api/tickets | python -m json.tool --indent 2

echo.
echo ============================================================================
echo [Test 3] Filtering WhatsApp tickets only...
echo ============================================================================
echo.

curl -s http://localhost:8000/tickets | python -c "import sys, json; data=json.load(sys.stdin); whatsapp=[t for t in data['tickets'] if t['channel']=='whatsapp']; print(json.dumps({'whatsapp_tickets': whatsapp, 'total': len(whatsapp)}, indent=2))"

echo.
echo ============================================================================
echo   Test Complete!
echo ============================================================================
echo.
echo Next Steps:
echo 1. Open frontend: http://localhost:3000/dashboard/tickets
echo 2. Filter by Channel: WhatsApp
echo 3. You should see WhatsApp tickets!
echo.
echo For Real WhatsApp Integration:
echo 1. Install ngrok: choco install ngrok
echo 2. Run: ngrok http 8000
echo 3. Copy ngrok URL to Twilio Console
echo 4. URL: https://YOUR-NGROK-URL.ngrok.io/webhooks/whatsapp
echo.
pause
