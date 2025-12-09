#!/usr/bin/env python3
"""Standalone FastAPI app for Render - All in one file"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

# ============================================================================
# FASTAPI SETUP
# ============================================================================

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

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Server is running"}

@app.get("/api/health")
def api_health():
    """API health check"""
    return {"status": "ok"}

# ============================================================================
# SERVE FRONTEND - MUST BE LAST
# ============================================================================

frontend_dir = Path(__file__).parent / "frontend"

if frontend_dir.exists():
    print(f"Frontend directory found at: {frontend_dir}")
    print(f"Frontend directory contents: {list(frontend_dir.glob('*'))}")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    
    # Serve index.html for root
    @app.get("/")
    async def serve_root():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file, media_type="text/html")
        return {"error": "index.html not found", "path": str(index_file)}
    
    # Serve HTML files
    @app.get("/{path:path}")
    async def serve_file(path: str):
        file_path = frontend_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Try with .html extension
        html_path = frontend_dir / f"{path}.html"
        if html_path.exists():
            return FileResponse(html_path, media_type="text/html")
        # Default to index.html for client-side routing
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file, media_type="text/html")
        return {"error": f"File not found: {path}"}
else:
    print(f"Frontend directory NOT found at: {frontend_dir}")
    @app.get("/")
    def root():
        return {"message": "Frontend not found", "frontend_path": str(frontend_dir), "exists": frontend_dir.exists()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
