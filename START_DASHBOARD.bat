@echo off
REM Supplier Hub Dashboard - Quick Start Script
REM This script starts the dashboard locally for testing

cls
echo.
echo ====================================================================
echo SUPPLIER HUB DASHBOARD - LOCAL START
echo ====================================================================
echo.
echo Your dashboard will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first: https://www.python.org
    pause
    exit /b 1
)

echo [*] Python found
echo.

REM Check if requirements are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo [*] Starting FastAPI server...
echo.
echo    Dashboard: http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo    ReDoc:     http://localhost:8000/redoc
echo.
echo ====================================================================
echo.

uvicorn app:app --reload --port 8000