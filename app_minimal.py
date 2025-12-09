#!/usr/bin/env python3
"""FastAPI app that serves frontend and proxies/imports real backend API."""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

app = FastAPI(title="Supplier Search Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize suppliers
BACKEND_AVAILABLE = False
ALL_SUPPLIERS = []

try:
    print("[INFO] Attempting to import backend modules...")
    from backend.suppliers_generator import SupplierGenerator
    print("[INFO] Successfully imported SupplierGenerator")
    
    # Initialize real supplier data
    print("[INFO] Generating suppliers...")
    generator = SupplierGenerator()
    ALL_SUPPLIERS = generator.generate_suppliers()
    BACKEND_AVAILABLE = True
    print(f"[SUCCESS] Loaded {len(ALL_SUPPLIERS)} suppliers from backend")
except Exception as e:
    print(f"[ERROR] Could not load suppliers: {type(e).__name__}: {e}")
    print("[WARNING] Falling back to minimal data")
    BACKEND_AVAILABLE = False
    # Minimal fallback data
    ALL_SUPPLIERS = [
        {"id": 1, "name": "Premier Lumber Co.", "category": "Lumber & Wood Products", "location": "Portland, OR", "rating": 4.8, "products": ["2x4 Lumber", "Plywood"], "walmartVerified": True, "aiScore": 92},
        {"id": 2, "name": "Elite Concrete Distributors", "category": "Concrete & Masonry", "location": "Houston, TX", "rating": 4.6, "products": ["Ready-Mix Concrete", "Cinder Blocks"], "walmartVerified": True, "aiScore": 89},
        {"id": 3, "name": "Pro Steel & Metal", "category": "Steel & Metal", "location": "Pittsburgh, PA", "rating": 4.7, "products": ["Steel Beams", "Rebar"], "walmartVerified": True, "aiScore": 91},
    ]

print(f"[INFO] Total suppliers available: {len(ALL_SUPPLIERS)}")

# ============================================================================
# HEALTH CHECKS
# ============================================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Server is running",
        "backend_available": BACKEND_AVAILABLE
    }

@app.get("/api/health")
def api_health():
    return {
        "status": "ok",
        "suppliers_count": len(ALL_SUPPLIERS),
        "backend_available": BACKEND_AVAILABLE
    }

# ============================================================================
# SUPPLIER ENDPOINTS - SAME AS BACKEND
# ============================================================================

@app.get("/api/suppliers")
def get_suppliers(skip: int = 0, limit: int = 100):
    """Get suppliers with pagination."""
    total = len(ALL_SUPPLIERS)
    suppliers = ALL_SUPPLIERS[skip:skip + limit]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(suppliers),
        "suppliers": suppliers
    }

@app.get("/api/suppliers/{supplier_id}")
def get_supplier(supplier_id: int):
    """Get a specific supplier by ID."""
    supplier = next((s for s in ALL_SUPPLIERS if s['id'] == supplier_id), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@app.get("/api/suppliers/search/query")
def search(q: str = Query(..., min_length=1), limit: int = 100):
    """Search suppliers by name, category, location, or products."""
    q_lower = q.lower()
    results = [
        s for s in ALL_SUPPLIERS
        if (
            q_lower in s.get('name', '').lower() or
            q_lower in s.get('category', '').lower() or
            q_lower in s.get('location', '').lower() or
            any(q_lower in str(p).lower() for p in s.get('products', []))
        )
    ]
    return {
        "query": q,
        "count": len(results),
        "results": results[:limit]
    }

@app.post("/api/suppliers/search")
def advanced_search(category: str = None, min_rating: float = None, verified_only: bool = False):
    """Advanced search with filters."""
    results = ALL_SUPPLIERS
    
    if category:
        results = [s for s in results if s.get('category', '').lower() == category.lower()]
    
    if min_rating is not None:
        results = [s for s in results if s.get('rating', 0) >= min_rating]
    
    if verified_only:
        results = [s for s in results if s.get('walmartVerified', False)]
    
    return {
        "count": len(results),
        "suppliers": results
    }

# ============================================================================
# DASHBOARD STATS
# ============================================================================

@app.get("/api/dashboard/stats")
def get_stats():
    """Get dashboard statistics."""
    if not ALL_SUPPLIERS:
        return {
            "total_suppliers": 0,
            "walmart_verified": 0,
            "verified_percentage": 0,
            "average_rating": 0,
            "average_ai_score": 0,
            "categories": {}
        }
    
    verified = sum(1 for s in ALL_SUPPLIERS if s.get('walmartVerified', False))
    avg_rating = sum(s.get('rating', 0) for s in ALL_SUPPLIERS) / len(ALL_SUPPLIERS)
    avg_ai_score = sum(s.get('aiScore', 0) for s in ALL_SUPPLIERS) / len(ALL_SUPPLIERS)
    
    # Get categories breakdown
    categories = {}
    for supplier in ALL_SUPPLIERS:
        cat = supplier.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_suppliers": len(ALL_SUPPLIERS),
        "walmart_verified": verified,
        "verified_percentage": round((verified / len(ALL_SUPPLIERS) * 100), 1) if ALL_SUPPLIERS else 0,
        "average_rating": round(avg_rating, 2),
        "average_ai_score": round(avg_ai_score, 1),
        "categories": categories,
        "total_categories": len(categories)
    }

@app.get("/api/suppliers/categories")
def get_categories():
    """Get all supplier categories."""
    categories = set(s.get('category', 'Unknown') for s in ALL_SUPPLIERS)
    return {"categories": sorted(list(categories))}

# ============================================================================
# AUTH ENDPOINTS - STUB IMPLEMENTATIONS
# ============================================================================

@app.post("/api/auth/sso")
def sso_login(walmart_id: str = None, email: str = None, name: str = None):
    """Walmart SSO login."""
    import uuid
    session_token = str(uuid.uuid4())
    return {
        "session_token": session_token,
        "user": {
            "id": walmart_id or "guest",
            "email": email,
            "name": name,
            "role": "user"
        }
    }

@app.post("/api/auth/guest-login")
def guest_login(email: str = None, name: str = None):
    """Guest login."""
    import uuid
    session_token = str(uuid.uuid4())
    return {
        "session_token": session_token,
        "user": {
            "id": "guest",
            "email": email,
            "name": name,
            "role": "guest"
        }
    }

@app.get("/api/auth/validate")
def validate_session(session_token: str = None):
    """Validate session token."""
    return {
        "valid": True,
        "user": {
            "id": "guest",
            "role": "guest"
        }
    }

@app.post("/api/auth/logout")
def logout(session_token: str = None):
    """Logout user."""
    return {"message": "Logged out successfully"}

# ============================================================================
# FAVORITES ENDPOINTS - STUB
# ============================================================================

@app.get("/api/favorites")
def get_favorites(session_token: str = None):
    """Get user's favorite suppliers."""
    return {"count": 0, "favorites": []}

@app.post("/api/favorites/add")
def add_favorite(session_token: str = None, supplier_id: int = None, supplier_name: str = None):
    """Add favorite supplier."""
    return {"message": "Added to favorites", "supplier_id": supplier_id}

@app.post("/api/favorites/remove")
def remove_favorite(session_token: str = None, supplier_id: int = None):
    """Remove favorite supplier."""
    return {"message": "Removed from favorites", "supplier_id": supplier_id}

@app.get("/api/favorites/is-favorite")
def is_favorite(session_token: str = None, supplier_id: int = None):
    """Check if supplier is favorited."""
    return {"is_favorite": False, "supplier_id": supplier_id}

# ============================================================================
# NOTES ENDPOINTS - STUB
# ============================================================================

@app.get("/api/notes")
def get_notes(session_token: str = None, supplier_id: int = None):
    """Get user's notes."""
    return {"count": 0, "notes": []}

@app.post("/api/notes/add")
def add_note(session_token: str = None, supplier_id: int = None, content: str = None):
    """Add a note."""
    import uuid
    return {"message": "Note added", "note_id": str(uuid.uuid4())}

@app.post("/api/notes/update")
def update_note(session_token: str = None, note_id: str = None, content: str = None):
    """Update a note."""
    return {"message": "Note updated", "note_id": note_id}

@app.post("/api/notes/delete")
def delete_note(session_token: str = None, note_id: str = None):
    """Delete a note."""
    return {"message": "Note deleted", "note_id": note_id}

# ============================================================================
# INBOX ENDPOINTS - STUB
# ============================================================================

@app.get("/api/inbox")
def get_inbox(session_token: str = None, unread_only: bool = False):
    """Get user's inbox."""
    return {"count": 0, "unread_count": 0, "messages": []}

@app.post("/api/inbox/mark-read")
def mark_read(session_token: str = None, message_id: str = None):
    """Mark message as read."""
    return {"message": "Marked as read", "message_id": message_id}

@app.post("/api/inbox/mark-all-read")
def mark_all_read(session_token: str = None):
    """Mark all messages as read."""
    return {"message": "All marked as read"}

@app.post("/api/inbox/delete")
def delete_message(session_token: str = None, message_id: str = None):
    """Delete a message."""
    return {"message": "Message deleted", "message_id": message_id}

@app.get("/api/inbox/unread-count")
def unread_count(session_token: str = None):
    """Get unread message count."""
    return {"unread_count": 0}

# ============================================================================
# SERVE FRONTEND
# ============================================================================

index_file = project_root / "index.html"

@app.get("/", include_in_schema=False)
async def serve_root():
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    return {
        "message": "Welcome to Supplier Search Engine",
        "docs_url": "/docs",
        "suppliers_count": len(ALL_SUPPLIERS)
    }

# Catch-all for other paths
@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    # Don't catch API routes
    if path.startswith("api/"):
        return {"error": f"Endpoint not found: {path}"}
    # Serve other files from root
    file_path = project_root / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    # Default to index.html
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    return {"error": "Not found"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
