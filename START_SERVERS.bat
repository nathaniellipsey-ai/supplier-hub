@echo off
CLS
echo.
echo ============================================================================
echo            SUPPLIER SEARCH ENGINE - Full Stack Startup
echo ============================================================================
echo.
echo [INFO] Starting both backend and frontend servers...
echo.

REM Backend is already running on port 8000
echo [OK] Backend API: http://127.0.0.1:8000
echo [OK] API Docs:    http://127.0.0.1:8000/docs
echo.

REM Start frontend web server
echo [STARTING] Frontend web server on port 3000...
echo.
cd /d "%~dp0"
python -m http.server 3000

pause
