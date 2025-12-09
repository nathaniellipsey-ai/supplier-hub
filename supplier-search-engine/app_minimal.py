#!/usr/bin/env python3
"""FastAPI app with embedded supplier generation and traditional auth."""

import sys
import os
import random
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

print("[INFO] Starting Supplier Search Engine API...")

app = FastAPI(title="Supplier Search Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# EMBEDDED SUPPLIER GENERATION
# ============================================================================

print("[INFO] Generating suppliers with seeded RNG...")

class SeededRandom:
    """Seeded RNG using seed 1962 (Walmart founding year)"""
    def __init__(self, seed=1962):
        self.rng = random.Random(seed)
    def random(self):
        return self.rng.random()

def generate_suppliers():
    """Generate 5000 suppliers with seeded randomness"""
    seeded = SeededRandom(1962)
    
    product_categories = {
        "Lumber & Wood Products": ["2x4 Lumber", "Plywood", "Particle Board", "MDF", "Hardwood Flooring", "Cedar Shingles"],
        "Concrete & Masonry": ["Portland Cement", "Ready-Mix Concrete", "Cinder Blocks", "Bricks", "Gravel", "Sand"],
        "Steel & Metal": ["Steel Beams", "Rebar", "Steel Pipe", "Aluminum Siding", "Metal Roofing", "Wire Mesh"],
        "Electrical Supplies": ["Electrical Wire", "Outlets", "Light Fixtures", "Circuit Breakers", "Conduit", "Switches"],
        "Plumbing Supplies": ["PVC Pipe", "Copper Pipe", "Faucets", "Valves", "Toilets", "Sink Fixtures"],
        "HVAC Equipment": ["Air Conditioning Units", "Furnaces", "Heat Pumps", "Ductwork", "Thermostats", "Insulation"],
        "Roofing Materials": ["Asphalt Shingles", "Metal Roofing", "Tar & Gravel", "Underlayment", "Flashing", "Gutters"],
        "Windows & Doors": ["Vinyl Windows", "Wood Doors", "Sliding Glass Doors", "Storm Windows", "Hardware", "Weather Stripping"],
        "Paint & Finishes": ["Interior Paint", "Exterior Paint", "Primer", "Stain", "Polyurethane", "Caulk"],
        "Hardware & Fasteners": ["Nails", "Screws", "Bolts", "Hinges", "Locks", "Tools"]
    }
    
    adjectives = ['Premier', 'Elite', 'Pro', 'Superior', 'Quality', 'Reliable', 'National', 'Metro', 'Coastal', 'Summit', 'Precision', 'BuildRight', 'Apex', 'Pioneer', 'TruValue', 'First Choice', 'Top Tier', 'Allied', 'United', 'Global', 'Platinum', 'Diamond', 'Crown', 'Ace', 'Master', 'Prime', 'Advantage', 'American', 'Industrial', 'Commercial', 'Advanced', 'Dynamic', 'Innovative', 'Strategic', 'Certified', 'Professional', 'Executive', 'Specialist', 'Expert', 'Mega', 'Ultra', 'Super', 'Best', 'Direct', 'Express', 'Rapid', 'Swift', 'Instant', 'Quick']
    
    company_types = ['Inc.', 'LLC', 'Corp.', 'Co.', 'Supply Co.', 'Distributors', 'Materials', 'Solutions', 'Industries', 'Group', 'Enterprises', 'Services', 'Systems', 'Technologies']
    
    cities = [
        {'city': 'New York', 'state': 'NY', 'region': 'Northeast'},
        {'city': 'Los Angeles', 'state': 'CA', 'region': 'West'},
        {'city': 'Chicago', 'state': 'IL', 'region': 'Midwest'},
        {'city': 'Houston', 'state': 'TX', 'region': 'Southwest'},
        {'city': 'Phoenix', 'state': 'AZ', 'region': 'Southwest'},
        {'city': 'Philadelphia', 'state': 'PA', 'region': 'Northeast'},
        {'city': 'San Antonio', 'state': 'TX', 'region': 'Southwest'},
        {'city': 'San Diego', 'state': 'CA', 'region': 'West'},
        {'city': 'Dallas', 'state': 'TX', 'region': 'Southwest'},
        {'city': 'San Jose', 'state': 'CA', 'region': 'West'},
        {'city': 'Austin', 'state': 'TX', 'region': 'Southwest'},
        {'city': 'Jacksonville', 'state': 'FL', 'region': 'Southeast'},
        {'city': 'Fort Worth', 'state': 'TX', 'region': 'Southwest'},
        {'city': 'Columbus', 'state': 'OH', 'region': 'Midwest'},
        {'city': 'Charlotte', 'state': 'NC', 'region': 'Southeast'},
        {'city': 'Seattle', 'state': 'WA', 'region': 'West'},
        {'city': 'Denver', 'state': 'CO', 'region': 'West'},
        {'city': 'Boston', 'state': 'MA', 'region': 'Northeast'},
        {'city': 'Portland', 'state': 'OR', 'region': 'West'},
        {'city': 'Las Vegas', 'state': 'NV', 'region': 'West'},
        {'city': 'Detroit', 'state': 'MI', 'region': 'Midwest'},
        {'city': 'Memphis', 'state': 'TN', 'region': 'Southeast'},
        {'city': 'Baltimore', 'state': 'MD', 'region': 'Northeast'},
        {'city': 'Milwaukee', 'state': 'WI', 'region': 'Midwest'},
        {'city': 'Atlanta', 'state': 'GA', 'region': 'Southeast'},
        {'city': 'Miami', 'state': 'FL', 'region': 'Southeast'},
        {'city': 'Indianapolis', 'state': 'IN', 'region': 'Midwest'},
        {'city': 'Kansas City', 'state': 'MO', 'region': 'Midwest'},
        {'city': 'Minneapolis', 'state': 'MN', 'region': 'Midwest'},
        {'city': 'Raleigh', 'state': 'NC', 'region': 'Southeast'}
    ]
    
    certifications = ['ISO 9001', 'ISO 14001', 'OSHA Certified', 'EPA Certified', 'NSF Certified', 'UL Listed', 'ANSI Certified', 'Green Building', 'Walmart Supplier Standards', 'WBE Certified']
    
    suppliers = []
    used_names = set()
    supplier_id = 1
    
    for category, products in product_categories.items():
        suppliers_per_category = 5000 // len(product_categories)
        
        for i in range(suppliers_per_category):
            category_short = category.split()[0]
            
            # Generate unique name
            for attempt in range(20):
                adj = adjectives[int(seeded.random() * len(adjectives))]
                type_suffix = company_types[int(seeded.random() * len(company_types))]
                name = f"{adj} {category_short} {type_suffix}"
                
                if name not in used_names:
                    break
            
            used_names.add(name)
            city_data = cities[int(seeded.random() * len(cities))]
            
            # Products
            num_products = int(seeded.random() * 5) + 2
            supplier_products = []
            for _ in range(num_products):
                prod = products[int(seeded.random() * len(products))]
                if prod not in supplier_products:
                    supplier_products.append(prod)
            
            # Certifications
            num_certs = int(seeded.random() * 3) + 1
            supplier_certs = []
            for _ in range(num_certs):
                cert = certifications[int(seeded.random() * len(certifications))]
                if cert not in supplier_certs:
                    supplier_certs.append(cert)
            
            suppliers.append({
                'id': supplier_id,
                'name': name,
                'category': category,
                'location': f"{city_data['city']}, {city_data['state']}",
                'region': city_data['region'],
                'rating': round(seeded.random() * 1.5 + 3.5, 1),
                'aiScore': int(seeded.random() * 30 + 70),
                'products': supplier_products,
                'certifications': supplier_certs,
                'walmartVerified': seeded.random() > 0.4,
                'yearsInBusiness': int(seeded.random() * 40 + 5),
                'projectsCompleted': int(seeded.random() * 5000 + 100),
            })
            
            supplier_id += 1
    
    return suppliers

ALL_SUPPLIERS = generate_suppliers()
print(f"[SUCCESS] Generated {len(ALL_SUPPLIERS)} suppliers")

# ============================================================================
# HEALTH CHECKS
# ============================================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Server is running",
        "suppliers_count": len(ALL_SUPPLIERS)
    }

@app.get("/api/health")
def api_health():
    return {
        "status": "ok",
        "suppliers_count": len(ALL_SUPPLIERS)
    }

# ============================================================================
# SUPPLIER ENDPOINTS
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
# TRADITIONAL AUTHENTICATION
# ============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    name: str

class User(BaseModel):
    id: str
    username: str
    email: str
    name: str
    role: str = "user"

# In-memory user storage (in production, use a database)
USERS = {}
SESSIONS = {}

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_from_token(session_token: str = None) -> User:
    """Get user from session token."""
    if not session_token or session_token not in SESSIONS:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return SESSIONS[session_token]

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    """Register a new user with username and password."""
    if req.username in USERS:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = secrets.token_hex(8)
    user = {
        "id": user_id,
        "username": req.username,
        "email": req.email,
        "name": req.name,
        "password_hash": hash_password(req.password),
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
    USERS[req.username] = user
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": user_id,
            "username": req.username,
            "email": req.email,
            "name": req.name,
            "role": "user"
        }
    }

@app.post("/api/auth/login")
def login(req: LoginRequest):
    """Traditional username/password login."""
    if req.username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user = USERS[req.username]
    if user["password_hash"] != hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate session token
    session_token = secrets.token_hex(32)
    SESSIONS[session_token] = User(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        name=user["name"],
        role=user["role"]
    )
    
    return {
        "session_token": session_token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }

@app.get("/api/auth/validate")
def validate_session(session_token: str = None):
    """Validate session token."""
    if not session_token or session_token not in SESSIONS:
        return {"valid": False}
    
    user = SESSIONS[session_token]
    return {
        "valid": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }

@app.post("/api/auth/logout")
def logout(session_token: str = None):
    """Logout user and invalidate session token."""
    if session_token and session_token in SESSIONS:
        del SESSIONS[session_token]
    
    return {"message": "Logged out successfully"}

# ============================================================================
# FAVORITES, NOTES, INBOX - STUBS
# ============================================================================

@app.get("/api/favorites")
def get_favorites(session_token: str = None):
    return {"count": 0, "favorites": []}

@app.post("/api/favorites/add")
def add_favorite(session_token: str = None, supplier_id: int = None, supplier_name: str = None):
    return {"message": "Added to favorites", "supplier_id": supplier_id}

@app.post("/api/favorites/remove")
def remove_favorite(session_token: str = None, supplier_id: int = None):
    return {"message": "Removed from favorites", "supplier_id": supplier_id}

@app.get("/api/favorites/is-favorite")
def is_favorite(session_token: str = None, supplier_id: int = None):
    return {"is_favorite": False}

@app.get("/api/notes")
def get_notes(session_token: str = None, supplier_id: int = None):
    return {"count": 0, "notes": []}

@app.post("/api/notes/add")
def add_note(session_token: str = None, supplier_id: int = None, content: str = None):
    import uuid
    return {"message": "Note added", "note_id": str(uuid.uuid4())}

@app.post("/api/notes/update")
def update_note(session_token: str = None, note_id: str = None, content: str = None):
    return {"message": "Note updated", "note_id": note_id}

@app.post("/api/notes/delete")
def delete_note(session_token: str = None, note_id: str = None):
    return {"message": "Note deleted", "note_id": note_id}

@app.get("/api/inbox")
def get_inbox(session_token: str = None, unread_only: bool = False):
    return {"count": 0, "unread_count": 0, "messages": []}

@app.post("/api/inbox/mark-read")
def mark_read(session_token: str = None, message_id: str = None):
    return {"message": "Marked as read"}

@app.post("/api/inbox/mark-all-read")
def mark_all_read(session_token: str = None):
    return {"message": "All marked as read"}

@app.post("/api/inbox/delete")
def delete_message(session_token: str = None, message_id: str = None):
    return {"message": "Message deleted"}

@app.get("/api/inbox/unread-count")
def unread_count(session_token: str = None):
    return {"unread_count": 0}

# ============================================================================
# SERVE FRONTEND
# ============================================================================

project_root = Path(__file__).parent
index_file = project_root / "index.html"

@app.get("/", include_in_schema=False)
async def serve_root():
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    return {"message": "Welcome to Supplier Search Engine", "docs_url": "/docs"}

@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    # Don't catch API routes
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Try to serve the file directly
    file_path = project_root / path
    if file_path.exists() and file_path.is_file():
        # Determine media type
        if path.endswith('.html'):
            return FileResponse(file_path, media_type="text/html")
        elif path.endswith('.css'):
            return FileResponse(file_path, media_type="text/css")
        elif path.endswith('.js'):
            return FileResponse(file_path, media_type="application/javascript")
        else:
            return FileResponse(file_path)
    
    # If file not found, try with .html extension
    if not path.endswith('.html'):
        html_path = project_root / f"{path}.html"
        if html_path.exists():
            return FileResponse(html_path, media_type="text/html")
    
    # Default to index.html for client-side routing
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    
    raise HTTPException(status_code=404, detail=f"File not found: {path}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
