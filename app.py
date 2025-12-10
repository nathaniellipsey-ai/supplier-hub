#!/usr/bin/env python3
"""Supplier Hub API - FastAPI Backend

Production-ready API for supplier search and management.
Serves both API endpoints and static frontend files.

Entry Point: app
Start: uvicorn app:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import os
import logging

from suppliers import SupplierGenerator

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Supplier Hub API",
    description="REST API for supplier search, filtering, and management",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
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
# INITIALIZATION
# ============================================================================

logger.info("[INIT] Initializing Supplier Hub API...")

# Generate suppliers once on startup (seeded)
supplier_gen = SupplierGenerator()
ALL_SUPPLIERS = supplier_gen.generate_suppliers(500)

logger.info(f"[INIT] Loaded {len(ALL_SUPPLIERS)} suppliers (seeded, seed=1962)")
logger.info(f"[INIT] Categories: {len(set(s['category'] for s in ALL_SUPPLIERS))}")
logger.info(f"[INIT] Regions: {len(set(s['region'] for s in ALL_SUPPLIERS))}")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "Supplier Hub API is running"}


@app.get("/api/suppliers")
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    verified_only: bool = Query(False),
    min_rating: float = Query(0, ge=0, le=5),
    min_ai_score: int = Query(0, ge=0, le=100),
) -> Dict[str, Any]:
    """Get suppliers with filtering and search."""
    
    # Apply filters
    filtered = ALL_SUPPLIERS.copy()
    
    if search:
        search_lower = search.lower()
        filtered = [
            s for s in filtered
            if search_lower in s['name'].lower()
            or any(search_lower in p.lower() for p in s['products'])
            or search_lower in s['category'].lower()
        ]
    
    if category:
        filtered = [s for s in filtered if s['category'] == category]
    
    if region:
        filtered = [s for s in filtered if s['region'] == region]
    
    if verified_only:
        filtered = [s for s in filtered if s['verified']]
    
    if min_rating > 0:
        filtered = [s for s in filtered if s['rating'] >= min_rating]
    
    if min_ai_score > 0:
        filtered = [s for s in filtered if s['aiScore'] >= min_ai_score]
    
    # Pagination
    total = len(filtered)
    suppliers = filtered[skip : skip + limit]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(suppliers),
        "suppliers": suppliers
    }


@app.get("/api/suppliers/{supplier_id}")
async def get_supplier(supplier_id: int) -> Dict[str, Any]:
    """Get a specific supplier by ID."""
    for supplier in ALL_SUPPLIERS:
        if supplier['id'] == supplier_id:
            return {"supplier": supplier}
    return {"error": "Supplier not found"}


@app.get("/api/categories")
async def get_categories() -> Dict[str, List[str]]:
    """Get all available categories."""
    categories = sorted(set(s['category'] for s in ALL_SUPPLIERS))
    return {"categories": categories}


@app.get("/api/regions")
async def get_regions() -> Dict[str, List[str]]:
    """Get all available regions."""
    regions = sorted(set(s['region'] for s in ALL_SUPPLIERS))
    return {"regions": regions}


@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """Get dashboard statistics."""
    verified_count = len([s for s in ALL_SUPPLIERS if s['verified']])
    avg_rating = sum(s['rating'] for s in ALL_SUPPLIERS) / len(ALL_SUPPLIERS)
    avg_ai_score = sum(s['aiScore'] for s in ALL_SUPPLIERS) // len(ALL_SUPPLIERS)
    
    return {
        "total_suppliers": len(ALL_SUPPLIERS),
        "verified_suppliers": verified_count,
        "average_rating": round(avg_rating, 2),
        "average_ai_score": avg_ai_score,
        "total_categories": len(set(s['category'] for s in ALL_SUPPLIERS)),
        "total_regions": len(set(s['region'] for s in ALL_SUPPLIERS))
    }


# ============================================================================
# STATIC FILE SERVING
# ============================================================================

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files (HTML, CSS, JS)
if os.path.exists(BASE_DIR):
    app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
    logger.info(f"[INIT] Mounted static files from: {BASE_DIR}")


# ============================================================================
# ROOT ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Serve the main dashboard."""
    dashboard_path = os.path.join(BASE_DIR, "dashboard_with_api.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "Dashboard not found", "path": dashboard_path}


@app.get("/{path:path}")
async def serve_static(path: str):
    """Serve static files (HTML, CSS, JS, etc.)."""
    file_path = os.path.join(BASE_DIR, path)
    
    # Security: prevent directory traversal
    file_path = os.path.normpath(file_path)
    if not file_path.startswith(os.path.normpath(BASE_DIR)):
        return {"error": "Access denied"}
    
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    return {"error": f"File not found: {path}"}


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("\n" + "="*80)
    logger.info("SUPPLIER HUB - STARTING SERVER")
    logger.info("="*80)
    logger.info("\nServer will be available at:")
    logger.info("  • Dashboard:  http://localhost:8000")
    logger.info("  • API Docs:   http://localhost:8000/api/docs")
    logger.info("  • ReDoc:      http://localhost:8000/api/redoc")
    logger.info("\nAPI Endpoints:")
    logger.info("  • GET  /api/suppliers")
    logger.info("  • GET  /api/suppliers/{id}")
    logger.info("  • GET  /api/categories")
    logger.info("  • GET  /api/regions")
    logger.info("  • GET  /api/stats")
    logger.info("\n" + "="*80 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
