#!/usr/bin/env python3
"""Standalone FastAPI app for Render - All in one file"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
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
# SERVE FRONTEND
# ============================================================================

frontend_dir = Path(__file__).parent / "frontend"

if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {"message": "Frontend not found. Please upload frontend folder."}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
