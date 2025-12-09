#!/usr/bin/env python3
"""Standalone FastAPI app for Render - Serves both Frontend and API"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ============================================================================
# IMPORT BACKEND APP
# ============================================================================

try:
    print(f"[INFO] Python path: {sys.path}")
    print(f"[INFO] Project root: {project_root}")
    print(f"[INFO] Trying to import backend.app...")
    from backend.app import app as backend_app
    print(f"[INFO] Successfully imported backend.app")
    app = backend_app
except ImportError as e:
    print(f"[ERROR] Could not import backend.app: {e}")
    print(f"[ERROR] Creating minimal FastAPI app instead")
    
    # Create minimal app if backend import fails
    app = FastAPI(
        title="Supplier Search Engine API",
        description="Professional API for supplier search and management",
        version="2.0.0",
    )
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "message": "Server is running (minimal mode)"}
    
    @app.get("/api/health")
    def api_health():
        return {"status": "ok", "mode": "minimal"}

# ============================================================================
# SERVE FRONTEND
# ============================================================================

# Try to serve from frontend folder first, then fallback to root index.html
frontend_dir = project_root / "frontend"
root_index = project_root / "index.html"

if frontend_dir.exists():
    print(f"[INFO] Frontend directory found at: {frontend_dir}")
    # Serve index.html for root
    @app.get("/", include_in_schema=False)
    async def serve_root():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file, media_type="text/html")
        return {"error": "index.html not found in frontend directory"}
elif root_index.exists():
    print(f"[INFO] Using root index.html at: {root_index}")
    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(root_index, media_type="text/html")
else:
    print(f"[ERROR] No index.html found")
    @app.get("/", include_in_schema=False)
    def root():
        return {"error": "Frontend not found", "frontend_path": str(frontend_dir)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
