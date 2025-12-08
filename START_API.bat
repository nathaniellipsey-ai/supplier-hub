@echo off
CLS
echo.
echo ============================================================================
echo         SUPPLIER SEARCH ENGINE - API SERVER
echo ============================================================================
echo.
echo Starting API server on localhost:8000...
echo.
echo Available endpoints:
echo   http://localhost:8000/api/dashboard/stats
echo   http://localhost:8000/api/dashboard/suppliers
echo   http://localhost:8000/api/dashboard/suppliers/search?q=...
echo   http://localhost:8000/api/dashboard/categories
echo   http://localhost:8000/health
echo.
echo Press Ctrl+C to stop
echo.
echo ============================================================================
echo.

cd /d "%~dp0"
python -u api_server.py

pause
