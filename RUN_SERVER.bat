@echo off
REM Start the Supplier Hub backend server
REM Use this instead of the direct uvicorn command

echo ========================================================================
echo                SUPPLIER HUB - BACKEND SERVER
echo ========================================================================
echo.
echo Starting FastAPI server...
echo.

cd /d "%~dp0"

REM Run WITHOUT reload flag to avoid import issues
REM If you want auto-reload, use: python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
python -m uvicorn app:app --host 0.0.0.0 --port 8000

echo.
echo Server stopped.
pause