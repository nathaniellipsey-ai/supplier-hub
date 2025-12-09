@echo off
color 0A
echo.
echo ============================================================
echo    SUPPLIER HUB - FRESH START
echo ============================================================
echo.
echo This will kill any existing Python processes and start fresh.
echo.
pause

echo.
echo Stopping any previous servers...
taskkill /F /IM python.exe 2>nul

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak

echo.
echo Starting app_minimal.py...
echo.
python app_minimal.py

echo.
echo If you see "Uvicorn running on http://0.0.0.0:8000" above,
echo the server is working! Open your browser to http://localhost:8000
echo.
pause
