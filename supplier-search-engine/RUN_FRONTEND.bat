@echo off
CLS
echo.
echo ============================================================================
echo   SUPPLIER SEARCH ENGINE - Frontend Web Server
echo ============================================================================
echo.
echo Starting web server on port 8888...
echo.
echo Open your browser to: http://127.0.0.1:8888/index.html
echo.
echo Backend API: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop
echo ============================================================================
echo.

cd /d "%~dp0"
python -m http.server 8888

pause
