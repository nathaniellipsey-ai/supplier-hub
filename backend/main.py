"""FastAPI backend for Supplier Search Engine Dashboard.

Provides REST API endpoints for supplier management, product management,
and integration with live data sources.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import List, Optional
import logging

from models import (
    SupplierResponse, SupplierCreate, ProductResponse, ProductCreate,
    SearchResult, DashboardStats
)
from services import SupplierService, ProductService, SearchService, DataIngestionService
from database import SupplierDatabase
from suppliers_generator import SupplierGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
db = SupplierDatabase()
db.init_schema()  # Ensure schema exists
supplier_service = SupplierService(db)
product_service = ProductService(db)
search_service = SearchService(db)
ingestion_service = DataIngestionService(db)

# Initialize supplier generator for the dashboard
supplier_generator = SupplierGenerator()
all_suppliers = supplier_generator.generate_suppliers()
logger.info(f"Generated {len(all_suppliers)} suppliers from seeded random generator")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("[STARTUP] Supplier Search Engine API starting...")
    yield
    # Shutdown
    logger.info("[SHUTDOWN] Supplier Search Engine API shutting down...")


app = FastAPI(
    title="Supplier Search Engine API",
    description="REST API for supplier management and live data integration",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8080", "http://localhost:8080"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# FRONTEND - SIMPLE HTML DASHBOARD
# ==============================================================================

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serve HTML dashboard."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supplier Search Engine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .header { background: rgba(0,0,0,0.1); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 32px; font-weight: bold; margin: 10px 0; }
        h1 { color: #333; margin: 20px 0; }
        h2 { color: #667eea; margin: 20px 0 10px 0; }
        .category-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 20px 0; }
        .category-item { background: #f5f5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }
        .category-name { font-weight: bold; margin-bottom: 5px; color: #333; }
        .category-count { font-size: 24px; font-weight: bold; color: #667eea; }
        .loading { text-align: center; color: #666; padding: 40px; font-size: 18px; }
        .error { background: #fee; color: #c33; padding: 15px; border-radius: 4px; margin: 10px 0; border-left: 4px solid #c33; }
    </style>
</head>
<body>
    <div class="header"><h1>🏢 Supplier Search Engine Dashboard</h1></div>
    <div class="container">
        <div id="loading" class="loading">Loading...</div>
        <div id="content" style="display:none;">
            <h1>📊 Statistics</h1>
            <div class="stats-grid" id="statsGrid"></div>
            <h2>📁 Categories</h2>
            <div class="category-grid" id="categoryGrid"></div>
            <div style="margin-top: 30px; text-align: center; color: #666;">
                <p>Backend API is running at http://127.0.0.1:8000</p>
                <p>API Documentation: <a href="/docs" style="color: #667eea;">http://127.0.0.1:8000/docs</a></p>
            </div>
        </div>
    </div>
    <script>
        fetch('/api/dashboard/stats').then(r=>r.json()).then(s=>{
            document.getElementById('statsGrid').innerHTML=`
                <div class="stat-card"><div>Total Suppliers</div><div class="stat-value">${s.total_suppliers.toLocaleString()}</div></div>
                <div class="stat-card"><div>Walmart Verified</div><div class="stat-value">${s.walmart_verified}</div><div style="font-size:12px;margin-top:5px;">${s.verified_percentage}%</div></div>
                <div class="stat-card"><div>Avg Rating</div><div class="stat-value">⭐ ${s.average_rating}</div></div>
                <div class="stat-card"><div>Avg AI Score</div><div class="stat-value">${s.average_ai_score}</div></div>
            `;
            document.getElementById('categoryGrid').innerHTML=Object.entries(s.categories).sort((a,b)=>b[1]-a[1]).map(([n,c])=>`<div class="category-item"><div class="category-name">${n}</div><div class="category-count">${c}</div></div>`).join('');
            document.getElementById('loading').style.display='none';
            document.getElementById('content').style.display='block';
        }).catch(e=>{
            document.getElementById('loading').innerHTML='<div class="error">Error loading data</div>';
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html, media_type="text/html")


# ==============================================================================
# HEALTH CHECK ENDPOINTS
# ==============================================================================

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Check API health status."""
    return {
        "status": "healthy",
        "message": "Supplier Search Engine API is running",
        "version": "1.0.0"
    }


@app.get("/api/health", tags=["Health"])
async def api_health() -> dict:
    """Check API and database health."""
    try:
        stats = supplier_service.get_statistics()
        return {
            "status": "healthy",
            "database": "connected",
            "suppliers": stats['total_active_suppliers'],
            "products": stats['total_products']
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


# ==============================================================================
# SUPPLIER ENDPOINTS
# ==============================================================================

@app.get("/api/suppliers", response_model=List[SupplierResponse], tags=["Suppliers"])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None
) -> List[SupplierResponse]:
    """List all suppliers with optional filtering."""
    try:
        suppliers = supplier_service.list_suppliers(skip, limit, category, status)
        return [SupplierResponse(**s) for s in suppliers]
    except Exception as e:
        logger.error(f"Error listing suppliers: {e}")
        raise HTTPException(status_code=500, detail="Failed to list suppliers")


@app.get("/api/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["Suppliers"])
async def get_supplier(supplier_id: int) -> SupplierResponse:
    """Get a specific supplier by ID."""
    try:
        supplier = supplier_service.get_supplier(supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return SupplierResponse(**supplier)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier {supplier_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supplier")


@app.post("/api/suppliers", response_model=dict, tags=["Suppliers"], status_code=201)
async def create_supplier(supplier: SupplierCreate) -> dict:
    """Create a new supplier."""
    try:
        supplier_id = supplier_service.create_supplier(supplier.dict())
        return {
            "id": supplier_id,
            "message": "Supplier created successfully",
            "supplier_id": supplier.supplier_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        raise HTTPException(status_code=500, detail="Failed to create supplier")


@app.get("/api/suppliers/search/{query}", response_model=SearchResult, tags=["Suppliers"])
async def search_suppliers(
    query: str,
    category: Optional[str] = None
) -> SearchResult:
    """Search for suppliers by name, ID, or keyword."""
    try:
        results = search_service.search_suppliers(query, category)
        return SearchResult(
            query=query,
            results_count=len(results),
            results=[SupplierResponse(**r) for r in results]
        )
    except Exception as e:
        logger.error(f"Error searching suppliers: {e}")
        raise HTTPException(status_code=500, detail="Failed to search suppliers")


# ==============================================================================
# PRODUCT ENDPOINTS
# ==============================================================================

@app.get("/api/suppliers/{supplier_id}/products", response_model=List[ProductResponse], tags=["Products"])
async def get_supplier_products(supplier_id: int) -> List[ProductResponse]:
    """Get all products from a specific supplier."""
    try:
        products = product_service.get_supplier_products(supplier_id)
        return [ProductResponse(**p) for p in products]
    except Exception as e:
        logger.error(f"Error getting products for supplier {supplier_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get products")


@app.post("/api/products", response_model=dict, tags=["Products"], status_code=201)
async def create_product(product: ProductCreate) -> dict:
    """Create a new product for a supplier."""
    try:
        product_id = product_service.create_product(product.dict())
        return {
            "id": product_id,
            "message": "Product created successfully",
            "product_code": product.product_code
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")


# ==============================================================================
# ANALYTICS & STATISTICS ENDPOINTS
# ==============================================================================

@app.get("/api/dashboard/stats", response_model=DashboardStats, tags=["Analytics"])
async def get_dashboard_stats() -> DashboardStats:
    """Get dashboard statistics."""
    try:
        stats = supplier_service.get_statistics()
        return DashboardStats(**stats)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# ==============================================================================
# DATA INGESTION ENDPOINTS
# ==============================================================================

@app.post("/api/data/ingest", response_model=dict, tags=["Data Ingestion"])
async def ingest_live_data(source: str = Query(..., description="Data source name")) -> dict:
    """Trigger live data ingestion from specified source."""
    try:
        result = await ingestion_service.ingest_from_source(source)
        return {
            "message": "Data ingestion completed",
            "source": source,
            "records_added": result.get('records_added', 0),
            "records_updated": result.get('records_updated', 0)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting data from {source}: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest data")


@app.get("/api/data/sources", response_model=dict, tags=["Data Ingestion"])
async def list_data_sources() -> dict:
    """List available data sources."""
    sources = ingestion_service.get_available_sources()
    return {
        "sources": sources,
        "count": len(sources)
    }


# ==============================================================================
# DASHBOARD SUPPLIER ENDPOINTS (for supplier-search-engine.html)
# ==============================================================================

@app.get("/api/dashboard/suppliers", tags=["Dashboard Suppliers"])
async def get_all_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
) -> dict:
    """Get all suppliers for the dashboard (seeded data)."""
    return {
        "total": len(all_suppliers),
        "skip": skip,
        "limit": limit,
        "suppliers": all_suppliers[skip:skip+limit]
    }


@app.get("/api/dashboard/suppliers/search", tags=["Dashboard Suppliers"])
async def search_dashboard_suppliers(q: str = Query("")) -> dict:
    """Search suppliers by name or category (seeded data)."""
    if not q:
        return {"results": []}
    
    q_lower = q.lower()
    results = [
        s for s in all_suppliers
        if q_lower in s['name'].lower() or q_lower in s['category'].lower()
    ]
    
    return {
        "query": q,
        "count": len(results),
        "results": results[:50]
    }


@app.get("/api/dashboard/suppliers/by-category", tags=["Dashboard Suppliers"])
async def get_suppliers_by_category(category: str = Query("")) -> dict:
    """Get suppliers filtered by category (seeded data)."""
    if not category:
        return {"results": [], "category": category, "count": 0}
    
    results = [s for s in all_suppliers if s['category'] == category]
    
    return {
        "category": category,
        "count": len(results),
        "results": results
    }


@app.get("/api/dashboard/suppliers/{supplier_id}", tags=["Dashboard Suppliers"])
async def get_dashboard_supplier(supplier_id: int) -> dict:
    """Get a specific supplier by ID (seeded data)."""
    supplier = next((s for s in all_suppliers if s['id'] == supplier_id), None)
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return supplier


@app.get("/api/dashboard/categories", tags=["Dashboard Suppliers"])
async def get_categories() -> dict:
    """Get all unique categories with supplier counts."""
    categories = {}
    for supplier in all_suppliers:
        cat = supplier['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "categories": categories,
        "total_categories": len(categories)
    }


@app.get("/api/dashboard/stats", tags=["Dashboard Suppliers"])
async def get_dashboard_supplier_stats() -> dict:
    """Get dashboard statistics for seeded suppliers."""
    verified_count = sum(1 for s in all_suppliers if s['walmartVerified'])
    avg_rating = sum(s['rating'] for s in all_suppliers) / len(all_suppliers) if all_suppliers else 0
    avg_ai_score = sum(s['aiScore'] for s in all_suppliers) / len(all_suppliers) if all_suppliers else 0
    
    categories = {}
    for supplier in all_suppliers:
        cat = supplier['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    regions = {}
    for supplier in all_suppliers:
        reg = supplier['region']
        regions[reg] = regions.get(reg, 0) + 1
    
    return {
        "total_suppliers": len(all_suppliers),
        "walmart_verified": verified_count,
        "verified_percentage": round((verified_count / len(all_suppliers) * 100) if all_suppliers else 0, 1),
        "average_rating": round(avg_rating, 2),
        "average_ai_score": round(avg_ai_score, 1),
        "categories": categories,
        "regions": regions,
        "total_categories": len(categories),
        "total_regions": len(regions)
    }


# ==============================================================================
# FRONTEND SERVING
# ==============================================================================

@app.get("/", tags=["Frontend"], include_in_schema=False)
async def serve_root():
    """Serve the root page (redirect to index.html)."""
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_path = os.path.join(parent_dir, "index.html")
    print(f"[DEBUG] Looking for frontend at: {frontend_path}")
    print(f"[DEBUG] File exists: {os.path.exists(frontend_path)}")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"message": "Frontend not found at " + frontend_path}


@app.get("/index.html", tags=["Frontend"], include_in_schema=False)
async def serve_index():
    """Serve the index.html file."""
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_path = os.path.join(parent_dir, "index.html")
    print(f"[DEBUG] Looking for frontend at: {frontend_path}")
    print(f"[DEBUG] File exists: {os.path.exists(frontend_path)}")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html", headers={"Cache-Control": "no-store"})
    raise HTTPException(status_code=404, detail=f"Frontend not found at {frontend_path}")


# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "Internal server error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
