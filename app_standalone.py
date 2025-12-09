#!/usr/bin/env python3
"""Standalone FastAPI app for Render - imports app_minimal"""

from app_minimal import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
