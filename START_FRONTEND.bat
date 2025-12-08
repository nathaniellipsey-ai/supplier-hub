@echo off
CLS
echo.
echo ============================================================================
echo        SUPPLIER SEARCH ENGINE - FRONTEND SERVER
echo ============================================================================
echo.
echo Starting frontend web server on port 8080...
echo.
echo Frontend URL: http://localhost:8080
echo Backend API: http://localhost:8000 (make sure it's running!)
echo.
echo ============================================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set FRONTEND_DIR=%SCRIPT_DIR%frontend

echo Script directory: %SCRIPT_DIR%
echo Frontend directory: %FRONTEND_DIR%
echo.

REM Check if index.html exists
if not exist "%FRONTEND_DIR%\index.html" (
    echo ERROR: index.html not found!
    echo Expected location: %FRONTEND_DIR%\index.html
    echo.
    echo Please make sure you are running this from:
    echo C:\Users\n0l08i7\Documents\supplier-search-engine\
    echo.
    pause
    exit /b 1
)

echo Found index.html - Server ready
echo.
echo Starting HTTP server...
echo.
echo To stop the server: Press Ctrl+C
echo.
echo ============================================================================
echo.

REM Change to frontend directory
cd /d "%FRONTEND_DIR%"

echo Current directory: %cd%
echo.

REM Start Python HTTP server on port 8080
python -m http.server 8080 --bind 127.0.0.1

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR: Could not start Python HTTP server
    echo ============================================================================
    echo.
    echo Troubleshooting:
    echo.
    echo 1. Make sure Python is installed:
    echo    - Download from https://www.python.org
    echo    - CHECK "Add Python to PATH" during install
    echo    - Restart after install
    echo.
    echo 2. Verify Python is in PATH:
    echo    - Open Command Prompt
    echo    - Type: python --version
    echo    - Should show Python 3.x.x
    echo.
    echo 3. Check if port 8080 is in use:
    echo    - Open Task Manager (Ctrl+Shift+Esc)
    echo    - Find "python" processes
    echo    - End any python tasks
    echo    - Or change port 8080 to 8081 below
    echo.
    echo 4. Try editing this file:
    echo    - Change: python -m http.server 8080
    echo    - To: python -m http.server 8081
    echo    - Then access: http://localhost:8081
    echo.
    pause
    exit /b 1
)
