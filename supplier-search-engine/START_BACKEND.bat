@echo off
CLS
echo.
echo ============================================================================
echo       SUPPLIER SEARCH ENGINE - BACKEND API SERVER (FastAPI)
echo ============================================================================
echo.
echo Starting backend API server on http://localhost:8000
echo.
echo Available endpoints:
echo   http://localhost:8000/health
echo   http://localhost:8000/docs (Swagger UI)
echo   http://localhost:8000/redoc (ReDoc)
echo.
echo   API Routes:
echo   POST   /api/dashboard/stats           - Dashboard statistics
echo   GET    /api/suppliers                 - All suppliers (paginated)
echo   GET    /api/suppliers/{id}            - Specific supplier
echo   GET    /api/suppliers/search/query    - Search
echo   POST   /api/suppliers/search          - Advanced search
echo   GET    /api/categories                - All categories
echo   GET    /api/categories/{category}     - Suppliers by category
echo.
echo Frontend will connect to this API at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.

cd /d "%~dp0"
python -m uvicorn backend.app:app --host localhost --port 8000 --reload

echo.
echo Server stopped.
pause
