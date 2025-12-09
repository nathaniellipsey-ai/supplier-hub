#!/usr/bin/env python3
"""FastAPI Backend - Supplier Search Engine

A professional, production-ready API for supplier management.
Provides REST endpoints for supplier data, search, filtering, and statistics.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from .models import (
    SupplierResponse,
    SearchRequest,
    DashboardStats,
    SupplierList,
    CategoriesResponse
)
from .suppliers_generator import SupplierGenerator
from .user_service import user_service

# ============================================================================
# LOGGING & CONFIG
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
    title="Supplier Search Engine API",
    description="Professional API for supplier search and management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA INITIALIZATION
# ============================================================================

logger.info("Initializing Supplier Generator...")
generator = SupplierGenerator()
ALL_SUPPLIERS = generator.generate_suppliers()
logger.info(f"Generated {len(ALL_SUPPLIERS)} suppliers")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_statistics() -> dict:
    """Calculate dashboard statistics."""
    if not ALL_SUPPLIERS:
        return {
            "total_suppliers": 0,
            "walmart_verified": 0,
            "verified_percentage": 0,
            "average_rating": 0,
            "average_ai_score": 0
        }
    
    verified = sum(1 for s in ALL_SUPPLIERS if s['walmartVerified'])
    avg_rating = sum(s['rating'] for s in ALL_SUPPLIERS) / len(ALL_SUPPLIERS)
    avg_ai_score = sum(s['aiScore'] for s in ALL_SUPPLIERS) / len(ALL_SUPPLIERS)
    
    return {
        "total_suppliers": len(ALL_SUPPLIERS),
        "walmart_verified": verified,
        "verified_percentage": round((verified / len(ALL_SUPPLIERS) * 100), 1),
        "average_rating": round(avg_rating, 2),
        "average_ai_score": round(avg_ai_score, 1)
    }

def get_categories_breakdown() -> dict:
    """Get supplier count by category."""
    categories = {}
    for supplier in ALL_SUPPLIERS:
        cat = supplier['category']
        categories[cat] = categories.get(cat, 0) + 1
    return categories

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Supplier Search Engine API is running",
        "version": "2.0.0"
    }

@app.get("/api/health", tags=["Health"])
async def api_health():
    """Detailed health check with statistics."""
    stats = calculate_statistics()
    return {
        "status": "healthy",
        "database": "connected",
        "suppliers_loaded": stats["total_suppliers"],
        "version": "2.0.0"
    }

# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.get(
    "/api/dashboard/stats",
    response_model=DashboardStats,
    tags=["Dashboard"],
    summary="Get Dashboard Statistics",
    description="Returns aggregated statistics about suppliers"
)
async def get_dashboard_stats():
    """Get dashboard statistics including totals, averages, and breakdowns."""
    stats = calculate_statistics()
    categories = get_categories_breakdown()
    
    return DashboardStats(
        total_suppliers=stats["total_suppliers"],
        walmart_verified=stats["walmart_verified"],
        verified_percentage=stats["verified_percentage"],
        average_rating=stats["average_rating"],
        average_ai_score=stats["average_ai_score"],
        categories=categories,
        total_categories=len(categories)
    )

# ============================================================================
# SUPPLIER ENDPOINTS
# ============================================================================

@app.get(
    "/api/suppliers",
    response_model=SupplierList,
    tags=["Suppliers"],
    summary="Get All Suppliers (Paginated)",
    description="Returns a paginated list of suppliers"
)
async def get_suppliers(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return")
):
    """Get paginated list of suppliers."""
    total = len(ALL_SUPPLIERS)
    suppliers = ALL_SUPPLIERS[skip:skip + limit]
    
    return SupplierList(
        total=total,
        skip=skip,
        limit=limit,
        count=len(suppliers),
        suppliers=suppliers
    )

@app.get(
    "/api/suppliers/{supplier_id}",
    response_model=SupplierResponse,
    tags=["Suppliers"],
    summary="Get Supplier by ID",
    description="Returns detailed information about a specific supplier"
)
async def get_supplier(supplier_id: int):
    """Get a specific supplier by ID."""
    supplier = next((s for s in ALL_SUPPLIERS if s['id'] == supplier_id), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@app.get(
    "/api/suppliers/search/query",
    tags=["Search"],
    summary="Search Suppliers",
    description="Search suppliers by name, category, products, or location"
)
async def search_suppliers(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(100, ge=1, le=500, description="Max results to return")
):
    """Search suppliers across multiple fields."""
    q_lower = q.lower()
    results = [
        s for s in ALL_SUPPLIERS
        if (
            q_lower in s['name'].lower() or
            q_lower in s['category'].lower() or
            q_lower in s['location'].lower() or
            any(q_lower in p.lower() for p in s['products'])
        )
    ]
    
    return {
        "query": q,
        "count": len(results),
        "results": results[:limit]
    }

@app.post(
    "/api/suppliers/search",
    tags=["Search"],
    summary="Advanced Search",
    description="Advanced search with filters"
)
async def advanced_search(search: SearchRequest):
    """Advanced search with multiple filters."""
    results = ALL_SUPPLIERS
    
    # Filter by query
    if search.query:
        q = search.query.lower()
        results = [
            s for s in results
            if (
                q in s['name'].lower() or
                q in s['category'].lower() or
                any(q in p.lower() for p in s['products'])
            )
        ]
    
    # Filter by category
    if search.category:
        results = [s for s in results if s['category'] == search.category]
    
    # Filter by location
    if search.location:
        results = [s for s in results if s['location'] == search.location]
    
    # Filter by minimum rating
    if search.min_rating:
        results = [s for s in results if s['rating'] >= search.min_rating]
    
    # Filter by Walmart verification
    if search.walmart_verified is not None:
        results = [s for s in results if s['walmartVerified'] == search.walmart_verified]
    
    return {
        "query": search.query or "(all)",
        "filters_applied": search.dict(exclude_none=True),
        "count": len(results),
        "results": results[:search.limit]
    }

# ============================================================================
# CATEGORY ENDPOINTS
# ============================================================================

@app.get(
    "/api/categories",
    response_model=CategoriesResponse,
    tags=["Categories"],
    summary="Get All Categories",
    description="Returns all supplier categories with supplier counts"
)
async def get_categories():
    """Get all categories with supplier counts."""
    categories = get_categories_breakdown()
    return CategoriesResponse(
        categories=categories,
        total_categories=len(categories)
    )

@app.get(
    "/api/categories/{category}",
    tags=["Categories"],
    summary="Get Suppliers by Category",
    description="Returns all suppliers in a specific category"
)
async def get_suppliers_by_category(
    category: str,
    limit: int = Query(1000, ge=1, le=5000, description="Max results")
):
    """Get suppliers in a specific category."""
    suppliers = [s for s in ALL_SUPPLIERS if s['category'] == category]
    if not suppliers:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "category": category,
        "count": len(suppliers),
        "suppliers": suppliers[:limit]
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API root endpoint with information."""
    return {
        "name": "Supplier Search Engine API",
        "version": "2.0.0",
        "description": "Professional API for supplier search and management",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "stats": "/api/dashboard/stats",
            "suppliers": "/api/suppliers",
            "search": "/api/suppliers/search/query",
            "categories": "/api/categories"
        }
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )

# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on startup."""
    logger.info("API startup complete")
    logger.info(f"Loaded {len(ALL_SUPPLIERS)} suppliers")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown."""
    logger.info("API shutdown")

# ============================================================================
# AUTHENTICATION & SSO ENDPOINTS
# ============================================================================

@app.post("/api/auth/sso", tags=["Auth"], summary="Walmart SSO Login")
async def sso_login(walmart_id: str, email: str, name: str):
    """Handle Walmart SSO login.
    
    In production, this would validate against Azure AD.
    For now, we trust the SSO provider has already validated.
    """
    user, session_token = user_service.login_sso(walmart_id, email, name)
    
    return {
        "success": True,
        "user": user.to_dict(),
        "session_token": session_token,
        "message": f"Welcome {user.name}!"
    }

@app.post("/api/auth/guest-login", tags=["Auth"], summary="Guest Login")
async def guest_login(email: str, name: str):
    """Allow guest login (without SSO)."""
    user = user_service.register_user(email, name)
    
    # Create session
    import hashlib
    from datetime import datetime, timedelta
    session_token = hashlib.sha256(f"{email}-{datetime.now()}".encode()).hexdigest()
    user_service.sessions[session_token] = {
        "user_email": email,
        "expires": (datetime.now() + timedelta(days=1)).isoformat(),
        "sso": False
    }
    
    return {
        "success": True,
        "user": user.to_dict(),
        "session_token": session_token,
        "message": f"Welcome {user.name}!"
    }

@app.post("/api/auth/logout", tags=["Auth"], summary="Logout")
async def logout(session_token: str):
    """Logout user."""
    success = user_service.logout(session_token)
    return {
        "success": success,
        "message": "Logged out successfully" if success else "Invalid session"
    }

@app.get("/api/auth/validate", tags=["Auth"], summary="Validate Session")
async def validate_session(session_token: str):
    """Validate session token."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return {
        "valid": True,
        "user": user.to_dict()
    }

# ============================================================================
# FAVORITES ENDPOINTS
# ============================================================================

@app.post("/api/favorites/add", tags=["Favorites"], summary="Add Favorite")
async def add_favorite(session_token: str, supplier_id: int, supplier_name: str):
    """Add supplier to favorites."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    success = user_service.add_favorite(user.email, supplier_id, supplier_name)
    return {
        "success": success,
        "message": "Added to favorites" if success else "Already in favorites"
    }

@app.post("/api/favorites/remove", tags=["Favorites"], summary="Remove Favorite")
async def remove_favorite(session_token: str, supplier_id: int):
    """Remove supplier from favorites."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    success = user_service.remove_favorite(user.email, supplier_id)
    return {
        "success": success,
        "message": "Removed from favorites"
    }

@app.get("/api/favorites", tags=["Favorites"], summary="Get Favorites")
async def get_favorites(session_token: str):
    """Get user's favorite suppliers."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    favorites = user_service.get_favorites(user.email)
    return {
        "count": len(favorites),
        "favorites": favorites
    }

@app.get("/api/favorites/is-favorite", tags=["Favorites"], summary="Check if Favorite")
async def is_favorite(session_token: str, supplier_id: int):
    """Check if supplier is in favorites."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    is_fav = user_service.is_favorite(user.email, supplier_id)
    return {"is_favorite": is_fav}

# ============================================================================
# NOTES ENDPOINTS
# ============================================================================

@app.post("/api/notes/add", tags=["Notes"], summary="Add Note")
async def add_note(session_token: str, supplier_id: int, content: str):
    """Add note to supplier."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    note = user_service.add_note(user.email, supplier_id, content)
    return {
        "success": True,
        "note": note
    }

@app.post("/api/notes/update", tags=["Notes"], summary="Update Note")
async def update_note(session_token: str, note_id: str, content: str):
    """Update existing note."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    note = user_service.update_note(user.email, note_id, content)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"success": True, "note": note}

@app.post("/api/notes/delete", tags=["Notes"], summary="Delete Note")
async def delete_note(session_token: str, note_id: str):
    """Delete a note."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    success = user_service.delete_note(user.email, note_id)
    return {
        "success": success,
        "message": "Note deleted" if success else "Note not found"
    }

@app.get("/api/notes", tags=["Notes"], summary="Get Notes")
async def get_notes(session_token: str, supplier_id: Optional[int] = None):
    """Get user's notes, optionally filtered by supplier."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    notes = user_service.get_notes(user.email, supplier_id)
    return {
        "count": len(notes),
        "notes": notes
    }

# ============================================================================
# INBOX ENDPOINTS
# ============================================================================

@app.get("/api/inbox", tags=["Inbox"], summary="Get Inbox")
async def get_inbox(session_token: str, unread_only: bool = False):
    """Get user's inbox messages."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    messages = user_service.get_inbox(user.email, unread_only)
    unread_count = user_service.get_unread_count(user.email)
    
    return {
        "count": len(messages),
        "unread_count": unread_count,
        "messages": messages
    }

@app.post("/api/inbox/mark-read", tags=["Inbox"], summary="Mark Message as Read")
async def mark_as_read(session_token: str, message_id: str):
    """Mark message as read."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    success = user_service.mark_as_read(user.email, message_id)
    return {"success": success}

@app.post("/api/inbox/mark-all-read", tags=["Inbox"], summary="Mark All as Read")
async def mark_all_as_read(session_token: str):
    """Mark all messages as read."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    count = user_service.mark_all_as_read(user.email)
    return {"success": True, "marked_count": count}

@app.post("/api/inbox/delete", tags=["Inbox"], summary="Delete Message")
async def delete_message(session_token: str, message_id: str):
    """Delete message from inbox."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    success = user_service.delete_message(user.email, message_id)
    return {
        "success": success,
        "message": "Message deleted" if success else "Message not found"
    }

@app.get("/api/inbox/unread-count", tags=["Inbox"], summary="Get Unread Count")
async def get_unread_count(session_token: str):
    """Get count of unread messages."""
    user = user_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    count = user_service.get_unread_count(user.email)
    return {"unread_count": count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )
