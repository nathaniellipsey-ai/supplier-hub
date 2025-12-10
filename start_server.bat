@echo off
REM Supplier Hub - Server Startup Script
REM
REM This script:
REM 1. Checks for Python
REM 2. Installs dependencies if needed
REM 3. Starts the FastAPI server
REM
REM Usage: Double-click this file or run: start_server.bat

echo.
echo ====================================================================
echo SUPPLIER HUB - STARTUP SCRIPT
echo ====================================================================
echo.
echo Checking Python installation...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if dependencies are installed
python -c "import fastapi" > nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ====================================================================
echo STARTING SERVER
echo ====================================================================
echo.
echo Access your dashboard at: http://localhost:8000
echo.
echo API Documentation: http://localhost:8000/api/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ====================================================================
echo.

REM Start the server
python -m uvicorn app:app --reload --port 8000 --log-level info